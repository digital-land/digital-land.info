from pathlib import Path

import pytest
import yaml


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
AWS_CREDENTIALS_ACTION = "aws-actions/configure-aws-credentials@"
DEPLOYMENT_JOBS = (
    ("deploy-smoke-test.yml", "publish-deploy"),
    ("publish.yml", "publish"),
)
LONG_LIVED_CREDENTIAL_REFERENCES = (
    "aws-access-key-id",
    "aws-secret-access-key",
    "DEPLOY_AWS_ACCESS_KEY_ID",
    "DEPLOY_AWS_SECRET_ACCESS_KEY",
)


def load_workflow(filename):
    workflow_path = REPOSITORY_ROOT / ".github" / "workflows" / filename
    return yaml.safe_load(workflow_path.read_text())


def aws_credentials_steps(job):
    return [
        step
        for step in job["steps"]
        if step.get("uses", "").startswith(AWS_CREDENTIALS_ACTION)
    ]


@pytest.mark.parametrize("filename, job_name", DEPLOYMENT_JOBS)
def test_deployment_job_has_least_privilege_oidc_permissions(filename, job_name):
    job = load_workflow(filename)["jobs"][job_name]

    assert job["permissions"] == {"id-token": "write", "contents": "read"}


@pytest.mark.parametrize("filename, job_name", DEPLOYMENT_JOBS)
def test_deployment_job_assumes_the_configured_role(filename, job_name):
    job = load_workflow(filename)["jobs"][job_name]
    credentials_steps = aws_credentials_steps(job)

    assert len(credentials_steps) == 1
    assert credentials_steps[0]["with"]["role-to-assume"] == (
        "${{ secrets.DEPLOY_AWS_ROLE_ARN }}"
    )
    assert credentials_steps[0]["with"]["aws-region"] == "eu-west-2"


@pytest.mark.parametrize("filename, job_name", DEPLOYMENT_JOBS)
def test_only_deployment_job_can_request_an_oidc_token(filename, job_name):
    jobs = load_workflow(filename)["jobs"]

    jobs_with_oidc_write = {
        name
        for name, job in jobs.items()
        if job.get("permissions", {}).get("id-token") == "write"
    }

    assert jobs_with_oidc_write == {job_name}


@pytest.mark.parametrize("filename, _job_name", DEPLOYMENT_JOBS)
def test_workflow_does_not_reference_long_lived_aws_credentials(filename, _job_name):
    workflow_path = REPOSITORY_ROOT / ".github" / "workflows" / filename
    workflow_source = workflow_path.read_text()

    for credential_reference in LONG_LIVED_CREDENTIAL_REFERENCES:
        assert credential_reference not in workflow_source
