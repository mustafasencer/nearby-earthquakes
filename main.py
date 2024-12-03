import asyncio
from collections import OrderedDict
from functools import wraps
from typing import Any, Callable, Dict, Final, List, Tuple
from typing import OrderedDict as OrderedDictType

import aiohttp
import numpy as np
import pandas as pd
import typer
from aiohttp import ClientTimeout

app = typer.Typer(help="KAYAK Maze CLI")

LATITUDE_PROMPT: Final[str] = "Please enter the latitude 🌍"
LONGITUDE_PROMPT: Final[str] = "Please enter the longitude 🌍"

EARTHQUAKES_LAST_30_DAYS_URL: Final[str] = (
    "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"
)

OUTPUT_SEPARATOR: Final[str] = " || "


def calculate_curve_distance_km(
    lon_1: pd.Series, lat_1: pd.Series, point: Tuple[float, float]
) -> pd.Series:
    """
    Calculates the curve distance and returns the results in kilometers
    :param lat_1:
    :param lon_1:
    :param point:
    :return:
    """
    lon2, lat2 = point
    lon_1, lat_1, lon2, lat2 = map(np.radians, [lon_1, lat_1, lon2, lat2])

    diff_lon = lon2 - lon_1
    diff_lat = lat2 - lat_1

    arc = (
        np.sin(diff_lat / 2.0) ** 2
        + np.cos(lat_1) * np.cos(lat2) * np.sin(diff_lon / 2.0) ** 2
    )

    c = 2 * np.arcsin(np.sqrt(arc))
    km = 6367 * c
    return km


async def fetch_earthquakes() -> Any:
    """
    fetch earthquakes from the API
    :return: The response from the API
    """
    async with aiohttp.ClientSession(timeout=ClientTimeout(total=30)) as session:
        try:
            async with session.get(EARTHQUAKES_LAST_30_DAYS_URL) as resp:
                if resp.status == 200:
                    response = await resp.json()
                else:
                    typer.echo(f"Site Error: {resp.status}")
                    typer.Abort()
                return response
        except aiohttp.ClientConnectorError as e:
            typer.echo(f"Connection Error: {str(e)}")
            typer.Abort()


def map_response_to_df(response: Dict[str, Any]) -> pd.DataFrame:
    """

    :param response:
    :return:
    """
    values = response
    earthquakes_list = [
        [
            val["id"],
            val["properties"]["title"],
            val["geometry"]["coordinates"][0],
            val["geometry"]["coordinates"][1],
        ]
        for val in values["features"]
    ]
    df = pd.DataFrame(
        earthquakes_list, columns=["id", "title", "longitude", "latitude"]
    )
    return df


def get_top_n_nearest_earthquakes(
    df: pd.DataFrame, coordinates: Tuple[float, float], top: int = 10
) -> Any:
    """
    Calculates the Haversine distance over the provided
    :param df:
    :param coordinates:
    :param top:
    :return:
    """

    df["distance"] = calculate_curve_distance_km(
        df["longitude"], df["latitude"], coordinates
    ).astype(int)
    df = df.drop_duplicates(subset="distance", keep="first").sort_values(by="distance")
    result = df.head(top)[["title", "distance"]].to_dict(
        into=OrderedDict, orient="records"
    )
    return result


def format_output(
    earthquakes: List[OrderedDictType[Any, Any]],
    output_separator: str = OUTPUT_SEPARATOR,
) -> str:
    """
    Format the output string as per the requirements
    :param earthquakes:
    :param output_separator:
    :return:
    """
    lines = []
    for earthquake in earthquakes:
        lines.append(f"{earthquake['title']}{output_separator}{earthquake['distance']}")
    return "\n".join(lines)


def coroutine(f: Callable[[], Any]) -> Any:
    @wraps(f)
    def wrapper() -> Any:
        return asyncio.run(f())

    return wrapper


@app.command()
@coroutine
async def main() -> None:
    """
    Main CLI driver function
    :return: None
    """

    latitude = typer.prompt(LATITUDE_PROMPT, type=float)
    longitude = typer.prompt(LONGITUDE_PROMPT, type=float)
    response = await fetch_earthquakes()
    df = map_response_to_df(response)
    earthquakes = get_top_n_nearest_earthquakes(df, (longitude, latitude))
    typer.echo(format_output(earthquakes))


if __name__ == "__main__":  # pragma: no cover
    typer.run(main)
