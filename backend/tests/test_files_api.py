from typing import List  # noqa: F401

from app.models.error import Error  # noqa: F401
from app.models.file_profile import FileProfile  # noqa: F401
from app.models.file_stat import FileStat  # noqa: F401
from fastapi.testclient import TestClient
from pydantic import StrictStr  # noqa: F401


def test_get_file_stats(client: TestClient):
    """Test case for get_file_stats

    Detailed raw file stats & description
    """

    headers = {}
    # uncomment below to make a request
    # response = client.request(
    #    "GET",
    #    "/datasets/{dataset_id}/files/{file_id}/stats".format(dataset_id='dataset_id_example', file_id='file_id_example'),
    #    headers=headers,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_list_dataset_files(client: TestClient):
    """Test case for list_dataset_files

    List raw files with basic stats
    """

    headers = {}
    # uncomment below to make a request
    # response = client.request(
    #    "GET",
    #    "/datasets/{dataset_id}/files".format(dataset_id='dataset_id_example'),
    #    headers=headers,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200
