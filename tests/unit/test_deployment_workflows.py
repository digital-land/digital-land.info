from pathlib import Path

import pytest
import yaml

REPOSITORY_ROOT = Path(__file__).parents[2]
DEPLOYMENT_WORKFLOWS = (
    (".github/workflows/publish.yml", "publish"),
    (".github/workflows/deploy-smoke-test.yml", "publish-deploy"),
)


def load_workflow(relative_path):
    workflow_path = REPOSITORY_ROOT / relative_path
    return yaml.safe_load(workflow_path.read_text())


@pytest.mark.parametrize("workflow_path, job_name", DEPLOYMENT_WORKFLOWS)
def test_deployment_job_uses_oidc_role_credentials(workflow_path, job_name):
    workflow = load_workflow(workflow_path)
    job = workflow["jobs"][job_name]

    credential_steps = [
        step
        for step in job["steps"]
        if step.get("uses") == "aws-actions/configure-aws-credentials@v4"
    ]

    assert len(credential_steps) == 1
    assert credential_steps[0]["with"] == {
        "role-to-assume": "${{ secrets.DEPLOY_AWS_ROLE_ARN }}",
        "aws-region": "eu-west-2",
    }


@pytest.mark.parametrize("workflow_path, job_name", DEPLOYMENT_WORKFLOWS)
def test_deployment_job_grants_only_permissions_needed_for_oidc(
    workflow_path, job_name
):
    workflow = load_workflow(workflow_path)

    assert workflow["jobs"][job_name]["permissions"] == {
        "id-token": "write",
        "contents": "read",
    }


@pytest.mark.parametrize("workflow_path, deployment_job", DEPLOYMENT_WORKFLOWS)
def test_oidc_token_permission_is_not_granted_to_other_jobs(
    workflow_path, deployment_job
):
    workflow = load_workflow(workflow_path)

    assert "permissions" not in workflow
    for job_name, job in workflow["jobs"].items():
        if job_name != deployment_job:
            assert "id-token" not in job.get("permissions", {})


@pytest.mark.parametrize("workflow_path, _", DEPLOYMENT_WORKFLOWS)
def test_deployment_workflow_does_not_reference_long_lived_aws_keys(workflow_path, _):
    workflow_source = (REPOSITORY_ROOT / workflow_path).read_text()

    prohibited_references = (
        "aws-access-key-id",
        "aws-secret-access-key",
        "DEPLOY_AWS_ACCESS_KEY_ID",
        "DEPLOY_AWS_SECRET_ACCESS_KEY",
    )

    for reference in prohibited_references:
        assert reference not in workflow_source
