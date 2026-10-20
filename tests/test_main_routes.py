"""Tests for the main HTML page routes."""

import re

import pytest


@pytest.mark.parametrize("input_id", ["taskCode", "xctskFile"])
def test_index_inputs_have_labels(client, input_id):
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert f'<label for="{input_id}"' in html
    assert re.search(rf'<input[^>]*\bid="{input_id}"', html)
