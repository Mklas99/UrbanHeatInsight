from typing import List  # noqa: F401

from app.models.error import Error  # noqa: F401
from app.models.processed_artifact import ProcessedArtifact  # noqa: F401
from app.models.processed_profile import ProcessedProfile  # noqa: F401
from fastapi.testclient import TestClient
from pydantic import StrictStr  # noqa: F401


def test_get_processed_stats(client: TestClient):
    """Test case for get_processed_stats

    Stats/description of a processed artifact
    """

    headers = {}
    # uncomment below to make a request
    # response = client.request(
    #    "GET",
    #    "/datasets/{dataset_id}/processed/{artifact_id}/stats".format(dataset_id='dataset_id_example', artifact_id='artifact_id_example'),
    #    headers=headers,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_list_processed(client: TestClient):
    """Test case for list_processed

    List processed artifacts for a dataset
    """

    headers = {}
    # uncomment below to make a request
    # response = client.request(
    #    "GET",
    #    "/datasets/{dataset_id}/processed".format(dataset_id='dataset_id_example'),
    #    headers=headers,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200
