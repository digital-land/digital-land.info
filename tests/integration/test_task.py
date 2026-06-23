from application.db.models import TaskOrm


def _make_task(**kwargs):
    defaults = {
        "reference": "task-001",
        "dataset": "brownfield-land",
        "organisation": "local-authority:TST",
        "endpoint": None,
        "resource": None,
        "details": {"issue_type": "missing value", "field": "name", "count": 3},
        "severity": "error",
        "responsibility": "supplier",
        "task_source": "issue",
        "entry_date": None,
    }
    defaults.update(kwargs)
    return TaskOrm(**defaults)


def test_task_json_returns_empty_when_no_data(client):
    response = client.get("/task.json")
    assert response.status_code == 200
    data = response.json()
    assert data["tasks"] == []
    assert data["count"] == 0
    assert "links" in data


def test_task_json_returns_inserted_task(client, db_session):
    db_session.add(_make_task())
    db_session.flush()

    response = client.get("/task.json")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    task = data["tasks"][0]
    assert task["reference"] == "task-001"
    assert task["dataset"] == "brownfield-land"
    assert task["details"] == {
        "issue_type": "missing value",
        "field": "name",
        "count": 3,
    }


def test_task_json_filters_by_organisation(client, db_session):
    db_session.add(_make_task(reference="task-001", organisation="local-authority:TST"))
    db_session.add(
        _make_task(reference="task-002", organisation="local-authority:OTHER")
    )
    db_session.flush()

    response = client.get("/task.json", params={"organisation": "local-authority:TST"})
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["tasks"][0]["reference"] == "task-001"


def test_task_json_filters_by_dataset(client, db_session):
    db_session.add(_make_task(reference="task-001", dataset="brownfield-land"))
    db_session.add(_make_task(reference="task-002", dataset="article-4-direction"))
    db_session.flush()

    response = client.get("/task.json", params={"dataset": "brownfield-land"})
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["tasks"][0]["dataset"] == "brownfield-land"


def test_task_json_filters_by_severity(client, db_session):
    db_session.add(_make_task(reference="task-001", severity="error"))
    db_session.add(_make_task(reference="task-002", severity="warning"))
    db_session.flush()

    response = client.get("/task.json", params={"severity": "error"})
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["tasks"][0]["severity"] == "error"


def test_task_json_filters_by_task_source(client, db_session):
    db_session.add(_make_task(reference="task-001", task_source="issue"))
    db_session.add(_make_task(reference="task-002", task_source="log"))
    db_session.flush()

    response = client.get("/task.json", params={"task_source": "issue"})
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["tasks"][0]["task-source"] == "issue"


def test_task_json_count_reflects_all_matches_not_page_size(client, db_session):
    for i in range(15):
        db_session.add(
            _make_task(reference=f"task-{i:03d}", organisation="local-authority:TST")
        )
    db_session.flush()

    response = client.get(
        "/task.json", params={"organisation": "local-authority:TST", "limit": 5}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 15
    assert len(data["tasks"]) == 5


def test_task_json_post_returns_405(client):
    response = client.post("/task.json")
    assert response.status_code == 405
