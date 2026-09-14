import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from clickdetect.api.datasource import router as datasource_router
from clickdetect.api.webhooks import router as webhooks_router
from clickdetect.api.plugins import router as plugins_router
from clickdetect.api.detector import router as detector_router
from clickdetect.api.rules import router as rules_router
from clickdetect.detector.runner import Runner, set_runner_instance

DATASOURCE = {"type": "duckdb", "database": ":memory:"}

WEBHOOK = {
    "name": "backend",
    "type": "generic",
    "url": "http://localhost:3000/alerts",
    "template": '{ "rule": {{ rule }}, "data": {{ data }} }',
}

DETECTOR = {
    "name": "api detector",
    "for": "5m",
    "description": "created through the api",
    "webhooks": ["backend"],
    "start": False,
}

RULE = {
    "id": "22000000-0000-0000-0000-000000000000",
    "name": "api rule",
    "level": 10,
    "size": ">0",
    "rule": "SELECT * FROM (VALUES (1), (2)) AS t(id);",
}


@pytest_asyncio.fixture
async def runner():
    r = await Runner({}).init_empty()
    set_runner_instance(r)
    yield r
    await r.manager.shutdown(wait=False)
    await r.close()


@pytest.fixture
def client(runner):
    app = FastAPI()
    for router in (
        datasource_router,
        webhooks_router,
        plugins_router,
        detector_router,
        rules_router,
    ):
        app.include_router(router)
    return TestClient(app)


@pytest.mark.asyncio
async def test_create_flow(client, runner):
    resp = client.post("/datasource", json=DATASOURCE)
    assert resp.status_code == 201
    assert resp.json()["type"] == "duckdb"

    resp = client.post("/webhooks", json=WEBHOOK)
    assert resp.status_code == 201
    assert resp.json() == {"name": "backend"}

    resp = client.post("/detector", json=DETECTOR)
    assert resp.status_code == 201
    detector_id = resp.json()["id"]

    resp = client.post(f"/rules/{detector_id}", json=RULE)
    assert resp.status_code == 201
    assert resp.json()["id"] == RULE["id"]

    detectors = client.get("/detector/list").json()
    assert [d["id"] for d in detectors] == [detector_id]
    assert detectors[0]["webhooks"] == ["backend"]
    assert detectors[0]["rules_count"] == 1

    rules = client.get(f"/rules/{detector_id}").json()
    assert [r["id"] for r in rules] == [RULE["id"]]

    detector = await runner.manager.get_detector_by_id(detector_id)
    assert [w.name for w in detector._webhooks] == ["backend"]


@pytest.mark.asyncio
async def test_errors(client, runner):
    assert client.post("/detector", json=DETECTOR).status_code == 409

    assert client.post("/datasource", json={"type": "nope"}).status_code == 404
    assert client.post("/datasource", json=DATASOURCE).status_code == 201
    assert client.post("/datasource", json=DATASOURCE).status_code == 409

    bad_template = {**WEBHOOK, "template": "{{ rule "}
    assert client.post("/webhooks", json=bad_template).status_code == 422
    assert client.post("/webhooks", json=WEBHOOK).status_code == 201
    assert client.post("/webhooks", json=WEBHOOK).status_code == 409

    assert client.post("/plugins", json={"id": "nope"}).status_code == 404

    bad_for = {**DETECTOR, "for": "xx"}
    assert client.post("/detector", json=bad_for).status_code == 422

    detector_id = client.post("/detector", json=DETECTOR).json()["id"]
    bad_size = {**RULE, "size": "abc"}
    assert client.post(f"/rules/{detector_id}", json=bad_size).status_code == 422
    assert client.post(f"/rules/{detector_id}", json=RULE).status_code == 201
    assert client.post(f"/rules/{detector_id}", json=RULE).status_code == 409
    assert client.post("/rules/nope", json=RULE).status_code == 404


@pytest.mark.asyncio
async def test_inactive_detector(client, runner):
    assert client.post("/datasource", json=DATASOURCE).status_code == 201

    resp = client.post("/detector", json={**DETECTOR, "active": False})
    assert resp.status_code == 201
    detector_id = resp.json()["id"]

    detectors = client.get("/detector/list").json()
    assert [(d["id"], d["active"]) for d in detectors] == [(detector_id, False)]
