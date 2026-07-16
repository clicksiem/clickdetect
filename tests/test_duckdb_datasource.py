import pytest_asyncio
import pytest
import logging
import duckdb
from clickdetect.detector.datasource.duckdb import DuckDBDataSource
from clickdetect.detector.runner import Runner
from clickdetect.detector import config

logger = logging.getLogger(__name__)


@pytest_asyncio.fixture
async def datasource(tmp_path):
    db_path = str(tmp_path / "test.duckdb")

    # pre-populate the database file (datasource opens it read-only)
    seed = duckdb.connect(db_path)
    seed.execute("CREATE TABLE events (id INTEGER, name VARCHAR)")
    seed.execute("INSERT INTO events VALUES (1, 'alice'), (2, 'bob')")
    seed.close()

    source = DuckDBDataSource()
    await source._parse({"database": db_path})
    yield source
    if source.connection:
        source.connection.close()


@pytest.fixture
def reset_running():
    # dry_run signals shutdown through these module globals; reset around each test
    config.running = True
    config.dry_run_code = 0
    yield
    config.running = True
    config.dry_run_code = 0


def _dry_run_data(rule_path: str) -> dict:
    return {
        "datasource": {"type": "duckdb", "database": ":memory:"},
        "detectors": {
            "d1": {
                "name": "dry run detector",
                "for": "5m",
                "description": "dry run test",
                "rules": [rule_path],
                "webhooks": [],
            }
        },
    }


def _write_rule(tmp_path, size: str) -> str:
    rule = tmp_path / "rule.yml"
    rule.write_text(
        f"""
id: "11000000-0000-0000-0000-000000000000"
name: "dry run rule"
level: 1
size: "{size}"
active: true
rule: |-
    SELECT * FROM (VALUES (1), (2), (3)) AS t(id);
"""
    )
    return str(rule)


@pytest.mark.asyncio
async def test_dry_run_not_triggered(tmp_path, reset_running):
    # 3 rows, condition ">5" is false -> rule does not trigger -> exit code 1
    data = _dry_run_data(_write_rule(tmp_path, ">5"))
    runner = await Runner(data, dry_run=True).init()
    detector = (await runner.get_detectors())[0]

    await detector.callback()

    assert config.running is False
    assert config.dry_run_code == 1
    await runner.close()


@pytest.mark.asyncio
async def test_dry_run_triggered(tmp_path, reset_running):
    # 3 rows, condition ">=3" is true -> rule triggers -> exit code 0
    data = _dry_run_data(_write_rule(tmp_path, ">=3"))
    runner = await Runner(data, dry_run=True).init()
    detector = (await runner.get_detectors())[0]

    await detector.callback()

    assert config.running is False
    assert config.dry_run_code == 0
    await runner.close()


@pytest.mark.asyncio
async def test_duckdb_connect_except():
    logger.debug("trying to connect to an invalid source")
    source = DuckDBDataSource()
    await source._parse({"database": "/nonexistent/path/to.duckdb"})
    await source.connect()
    assert source.connection is None


@pytest.mark.asyncio
async def test_duckdb_connect(datasource: DuckDBDataSource):
    await datasource.connect()
    assert datasource.connection


@pytest.mark.asyncio
async def test_duckdb_query(datasource: DuckDBDataSource):
    logger.debug("querying events table")
    await datasource.connect()
    assert datasource.connection

    result = await datasource.query("SELECT id, name FROM events ORDER BY id")
    assert result
    assert result.datasource == "duckdb"
    assert result.len == 2
    assert result.value == [
        {"id": 1, "name": "alice"},
        {"id": 2, "name": "bob"},
    ]
