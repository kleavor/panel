from __future__ import absolute_import, division, unicode_literals

import sys
import pytest

from base64 import b64decode, b64encode

from panel.pane import GIF, JPG, PNG, SVG
from io import BytesIO, StringIO


def test_svg_pane(document, comm):
    rect = """
    <svg xmlns="http://www.w3.org/2000/svg">
      <rect x="10" y="10" height="100" width="100"/>
    </svg>
    """
    pane = SVG(rect)

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    assert model.text.startswith('<img')
    assert b64encode(rect.encode('utf-8')).decode('utf-8') in model.text

    # Replace Pane.object
    circle = """
    <svg xmlns="http://www.w3.org/2000/svg" height="100">
      <circle cx="50" cy="50" r="40" />
    </svg>
    """
    pane.object = circle
    assert pane._models[model.ref['id']][0] is model
    assert model.text.startswith('<img')
    assert b64encode(circle.encode('utf-8')).decode('utf-8') in model.text

    # Cleanup
    pane._cleanup(model)
    assert pane._models == {}


twopixel = dict(\
    gif = b'R0lGODlhAgABAPAAAEQ6Q2NYYCH5BAAAAAAAIf8LSW1hZ2VNYWdpY2sNZ2FtbWE' + \
          b'9MC40NTQ1NQAsAAAAAAIAAQAAAgIMCgA7',
    png = b'iVBORw0KGgoAAAANSUhEUgAAAAIAAAABCAYAAAD0In+KAAAAFElEQVQIHQEJAPb' + \
          b'/AWNYYP/h4uMAFL0EwlEn99gAAAAASUVORK5CYII=',
    jpg = b'/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQE' + \
          b'BAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQ' + \
          b'EBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBA' + \
          b'QEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAIDAREAAhEBAxEB/8QAFAABAAAAAAAA' + \
          b'AAAAAAAAAAAACf/EABoQAAEFAQAAAAAAAAAAAAAAAAYABAU2dbX/xAAVAQEBAAA' + \
          b'AAAAAAAAAAAAAAAAFBv/EABkRAAEFAAAAAAAAAAAAAAAAAAEAAjFxsf/aAAwDAQ' + \
          b'ACEQMRAD8AA0qs5HvTHQcJdsChioXSbOr/2Q==')

def test_imgshape():
    for t in [PNG, JPG, GIF]:
        w,h = t._imgshape(b64decode(twopixel[t.name.lower()]))
        assert w == 2
        assert h == 1

def test_load_from_byteio():
    """Testing a loading a image from a ByteIo"""
    memory = BytesIO()
    with open('panel/tests/test_data/logo.png', 'rb') as image_file:
        memory.write(image_file.read())
    memory.seek(0)
    image_pane = PNG(memory)
    image_data = image_pane._img()
    assert b'PNG' in image_data

@pytest.mark.skipif(sys.version_info.major <= 2, reason="Doesn't work with python 2")
def test_load_from_stringio():
    """Testing a loading a image from a StringIO"""
    memory = StringIO()
    with open('panel/tests/test_data/logo.png', 'rb') as image_file:
        memory.write(str(image_file.read()))
    memory.seek(0)
    image_pane = PNG(memory)
    image_data = image_pane._img()
    assert 'PNG' in image_data

def test_loading_a_image_from_url():
    """Tests the loading of a image from a url"""
    url = 'https://upload.wikimedia.org/wikipedia/commons/7/71/' \
          '1700_CE_world_map.PNG'

    image_pane = PNG(url)
    image_data = image_pane._img()
    assert b'PNG' in image_data
