from typing import (  # noqa: F401
    Annotated,  # noqa: F401
    Any,
    Dict,
    List,
    Optional,
)

from app.models.data_layer import DataLayer  # noqa: F401
from app.models.error import Error  # noqa: F401
from fastapi.testclient import TestClient
from pydantic import Field, StrictStr, field_validator  # noqa: F401


def test_get_layer(client: TestClient):
    """Test case for get_layer

    Get layer metadata
    """

    headers = {}
    # uncomment below to make a request
    # response = client.request(
    #    "GET",
    #    "/datasets/{dataset_id}/layers/{layer_id}".format(dataset_id='dataset_id_example', layer_id='layer_id_example'),
    #    headers=headers,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_get_layer_data(client: TestClient):
    """Test case for get_layer_data

    Retrieve layer data
    """
    params = [("format", geojson), ("bbox", "bbox_example"), ("time_range", "time_range_example")]
    headers = {}
    # uncomment below to make a request
    # response = client.request(
    #    "GET",
    #    "/datasets/{dataset_id}/layers/{layer_id}/data".format(dataset_id='dataset_id_example', layer_id='layer_id_example'),
    #    headers=headers,
    #    params=params,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_list_layers(client: TestClient):
    """Test case for list_layers

    List data layers for a dataset
    """

    headers = {}
    # uncomment below to make a request
    # response = client.request(
    #    "GET",
    #    "/datasets/{dataset_id}/layers".format(dataset_id='dataset_id_example'),
    #    headers=headers,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200
