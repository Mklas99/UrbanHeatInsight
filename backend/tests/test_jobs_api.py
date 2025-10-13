from typing import Any  # noqa: F401

from app.models.clustering_request import ClusteringRequest  # noqa: F401
from app.models.error import Error  # noqa: F401
from app.models.job import Job  # noqa: F401
from app.models.pipeline_request import PipelineRequest  # noqa: F401
from fastapi.testclient import TestClient
from pydantic import StrictStr  # noqa: F401


def test_cancel_job(client: TestClient):
    """Test case for cancel_job

    Cancel a running job
    """

    headers = {}
    # uncomment below to make a request
    # response = client.request(
    #    "DELETE",
    #    "/jobs/{job_id}".format(job_id='job_id_example'),
    #    headers=headers,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_get_job(client: TestClient):
    """Test case for get_job

    Get job status/result
    """

    headers = {}
    # uncomment below to make a request
    # response = client.request(
    #    "GET",
    #    "/jobs/{job_id}".format(job_id='job_id_example'),
    #    headers=headers,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_start_clustering(client: TestClient):
    """Test case for start_clustering

    Start a clustering job on selected data
    """
    clustering_request = {
        "output_name": "output_name",
        "features": ["features", "features"],
        "method": "kmeans",
        "webhook_url": "https://openapi-generator.tech",
        "dataset_id": "046b6c7f-0b8a-43b9-b35d-6489e6daee91",
        "input_layers": ["046b6c7f-0b8a-43b9-b35d-6489e6daee91", "046b6c7f-0b8a-43b9-b35d-6489e6daee91"],
        "params": {"key": ""},
    }

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    # response = client.request(
    #    "POST",
    #    "/jobs/clustering",
    #    headers=headers,
    #    json=clustering_request,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_start_pipeline(client: TestClient):
    """Test case for start_pipeline

    Execute the data pipeline on a dataset
    """
    pipeline_request = {
        "webhook_url": "https://openapi-generator.tech",
        "dataset_id": "046b6c7f-0b8a-43b9-b35d-6489e6daee91",
        "pipeline_id": "pipeline_id",
        "output_tags": ["output_tags", "output_tags"],
        "steps": [{"name": "name", "params": {"key": ""}}, {"name": "name", "params": {"key": ""}}],
    }

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    # response = client.request(
    #    "POST",
    #    "/jobs/pipeline",
    #    headers=headers,
    #    json=pipeline_request,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200
