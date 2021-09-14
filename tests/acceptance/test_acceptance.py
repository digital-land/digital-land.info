import pytest
import os
import time
import subprocess
import requests

image = "955696714113.dkr.ecr.eu-west-2.amazonaws.com/dl-web"


@pytest.fixture()
def running_instance():
    proc = subprocess.run(
        ["docker", "run", "-d", "-p", "80:80", image],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid,
    )
    assert proc.stderr == b""
    container_id = proc.stdout.decode("utf-8").strip()
    time.sleep(30)  # wait for container to start fully

    yield container_id

    # kill the instance once tests are done
    subprocess.run(["docker", "kill", container_id])


def test_acceptance(running_instance):
    # in case you want to assert the container output...
    #
    # logs_proc = subprocess.run(
    #     ["docker", "logs", running_instance], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    # )

    resp = requests.get("http://127.0.0.1/health")

    assert resp.status_code == 200
    assert resp.text == "OK"
