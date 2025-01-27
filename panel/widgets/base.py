"""
Defines the Widget base class which provides bi-directional
communication between the rendered dashboard and the Widget
parameters.
"""
from __future__ import absolute_import, division, unicode_literals

from functools import partial

import param

from ..io import push, state
from ..viewable import Reactive, Layoutable



class Widget(Reactive):
    """
    Widgets allow syncing changes in bokeh widget models with the
    parameters on the Widget instance.
    """

    disabled = param.Boolean(default=False, doc="""
       Whether the widget is disabled.""")

    name = param.String(default='')

    height = param.Integer(default=None, bounds=(0, None))

    width = param.Integer(default=None, bounds=(0, None))

    margin = param.Parameter(default=(5, 10), doc="""
        Allows to create additional space around the component. May
        be specified as a two-tuple of the form (vertical, horizontal)
        or a four-tuple (top, right, bottom, left).""")

    __abstract = True

    _widget_type = None

    # Whether the widget supports embedding
    _supports_embed = False

    # Any parameters that require manual updates handling for the models
    # e.g. parameters which affect some sub-model
    _manual_params = []

    _rename = {'name': 'title'}

    def __init__(self, **params):
        if 'name' not in params:
            params['name'] = ''
        if '_supports_embed' in params:
            self._supports_embed = params.pop('_supports_embed')
        super(Widget, self).__init__(**params)
        self.param.watch(self._update_widget, self._manual_params)

    def _manual_update(self, event, model, doc, root, parent, comm):
        """
        Method for handling any manual update events, i.e. events triggered
        by changes in the manual params.
        """

    def _update_widget(self, event):
        for ref, (model, parent) in self._models.items():
            viewable, root, doc, comm = state._views[ref]
            if comm or state._unblocked(doc):
                self._manual_update(event, model, doc, root, parent, comm)
                if comm and 'embedded' not in root.tags:
                    push(doc, comm)
            else:
                cb = partial(self._manual_update, event, model, doc, root, parent, comm)
                doc.add_next_tick_callback(cb)

    def _get_model(self, doc, root=None, parent=None, comm=None):
        model = self._widget_type(**self._process_param_change(self._init_properties()))
        if root is None:
            root = model
        # Link parameters and bokeh model
        values = dict(self.get_param_values())
        properties = self._filter_properties(list(self._process_param_change(values)))
        self._models[root.ref['id']] = (model, parent)
        self._link_props(model, properties, doc, root, comm)
        return model

    def _synced_params(self):
        return [p for p in self.param if p not in self._manual_params]

    def _filter_properties(self, properties):
        return [p for p in properties if p not in Layoutable.param]

    def _get_embed_state(self, root, max_opts=3):
        """
        Returns the bokeh model and a discrete set of value states
        for the widget.

        Arguments
        ---------
        root: bokeh.model.Model
          The root model of the widget
        max_opts: int
          The maximum number of states the widget should return

        Returns
        -------
        widget: panel.widget.Widget
          The Panel widget instance to modify to effect state changes
        model: bokeh.model.Model
          The bokeh model to record the current value state on
        values: list
          A list of value states to explore.
        getter: callable
          A function that returns the state value given the model
        on_change: string
          The name of the widget property to attach a callback on
        js_getter: string
          JS snippet that returns the state value given the model
        """


class CompositeWidget(Widget):
    """
    A baseclass for widgets which are made up of two or more other
    widgets
    """

    __abstract = True

    def select(self, selector=None):
        """
        Iterates over the Viewable and any potential children in the
        applying the Selector.

        Arguments
        ---------
        selector: type or callable or None
          The selector allows selecting a subset of Viewables by
          declaring a type or callable function to filter by.

        Returns
        -------
        viewables: list(Viewable)
        """
        objects = super(CompositeWidget, self).select(selector)
        for obj in self._composite.objects:
            objects += obj.select(selector)
        return objects

    def _get_model(self, doc, root=None, parent=None, comm=None):
        return self._composite._get_model(doc, root, parent, comm)

    def __contains__(self, object):
        return object in self._composite.objects
