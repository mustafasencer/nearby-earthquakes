import json
from collections import OrderedDict
from typing import Dict, List, Tuple, Union, Any

import pandas as pd
import pytest
from typer.testing import CliRunner

from main import app, fetch_earthquakes, format_output, get_top_n_nearest_earthquakes, map_response_to_df, \
    calculate_curve_distance_km

# runner = CliRunner()
#
#
# def test_app():
#     test_table: List[Dict[str, Union[Tuple[int, int], str]]] = [
#         {
#             "coordinates": (32, 32),
#             "expected": "M 5.0 - 15 km S of Xylofágou, Cyprus  ||  359",
#         },
#         {"coordinates": (12, -23), "expected": ""},
#         {"coordinates": (56, -100), "expected": ""},
#         {"coordinates": (-12, 34), "expected": ""},
#     ]
#     for test_case in test_table:
#         latitude, longitude = test_case["coordinates"]
#         result = runner.invoke(app, input=f"{latitude}\n{longitude}\n")
#         assert result.exit_code == 0
#         assert test_case["expected"] in result.stdout




# @pytest.mark.asyncio
# def test_fetch_earthquakes():
#     resp = await fetch_earthquakes()
#     assert resp.status == 200
#
#
# @pytest.mark.asyncio
# def test_fetch_earthquakes_with_connection_error():
#     resp = await fetch_earthquakes()
#     assert resp.status == 500
#
#
# @pytest.mark.asyncio
# def test_fetch_earthquakes_with_site_error():
#     resp = await fetch_earthquakes()
#     assert resp.status == 400


def test_format_output():
    expected = "M 0.6 - 13 km NE of Badger, Alaska || 6474\nM 1.4 - 34 km SSE of Cantwell, Alaska || 6684"
    earthquakes = [
        OrderedDict([('title', "M 0.6 - 13 km NE of Badger, Alaska"), ("distance", 6474)]),
        OrderedDict([('title', "M 1.4 - 34 km SSE of Cantwell, Alaska"), ("distance", 6684)])
    ]
    std_output = format_output(earthquakes)
    assert std_output == expected


def test_get_top_n_nearest_earthquakes():
    df = pd.read_csv("tests/test_data/test_data.csv")

    test_table: List[Dict[str, Any]] = [
        {
            "name": "Working case with 10 outputs",
            "point": (32, 32),
            "top": 10,
            "expected_no_1": ("M 4.3 - 37 km SE of Parapat, Indonesia", 7715),
        },
        {
            "name": "Working case with 5 outputs",
            "point": (-10, 23),
            "top": 5,
            "expected_no_1": ("M 3.1 - 74 km NNW of Charlotte Amalie, U.S. Virgin Islands", 5706),
        }
    ]

    for test_case in test_table:
        result = get_top_n_nearest_earthquakes(df, test_case["point"], top=test_case["top"])
        assert len(result) == test_case["top"]
        assert result[0]["title"] == test_case["expected_no_1"][0]
        assert result[0]["distance"] == test_case["expected_no_1"][1]


def test_map_response_to_df():
    with open("tests/test_data/test_response.json") as f:
        response = json.load(f)
    result = map_response_to_df(response)
    assert result.shape[0] == 100
    assert isinstance(result, pd.DataFrame)
    assert result.iloc[0,-1] == response["features"][0]["geometry"]["coordinates"][1]


def test_calculate_curve_distance_km():
    df = pd.read_csv("tests/test_data/test_data.csv")

    x = calculate_curve_distance_km(df["longitude"], df["latitude"], (55,5))
    assert x.iloc[0].round() == 15628.0
