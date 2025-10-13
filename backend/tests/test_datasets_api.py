from typing import (  # noqa: F401
    Annotated,  # noqa: F401
    List,
    Optional,
    Tuple,
    Union,
)

from app.models.dataset import Dataset  # noqa: F401
from app.models.error import Error  # noqa: F401
from app.models.list_datasets200_response import ListDatasets200Response  # noqa: F401
from fastapi.testclient import TestClient
from pydantic import Field, StrictBytes, StrictStr  # noqa: F401


def test_create_dataset(client: TestClient):
    """Test case for create_dataset

    Upload dataset (files + metadata)
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    data = {
        "name": "name_example",
        "description": "description_example",
        "tags": ["tags_example"],
        "metadata_json": "metadata_json_example",
        "files": ["/path/to/file"],
    }
    # uncomment below to make a request
    # response = client.request(
    #    "POST",
    #    "/datasets",
    #    headers=headers,
    #    data=data,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_get_dataset(client: TestClient):
    """Test case for get_dataset

    Get dataset details
    """

    headers = {}
    # uncomment below to make a request
    # response = client.request(
    #    "GET",
    #    "/datasets/{dataset_id}".format(dataset_id='dataset_id_example'),
    #    headers=headers,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_list_datasets(client: TestClient):
    """Test case for list_datasets

    List uploaded datasets
    """
    params = [("page", 1), ("page_size", 25), ("q", "q_example")]
    headers = {}
    # uncomment below to make a request
    # response = client.request(
    #    "GET",
    #    "/datasets",
    #    headers=headers,
    #    params=params,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200
