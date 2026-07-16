import pytest_asyncio
import pytest
import logging
from clickdetect.detector.datasource.clickhouse import ClickhouseDataSource

logger = logging.getLogger(__name__)


@pytest_asyncio.fixture
async def datasource():
    source = ClickhouseDataSource()
    await source._parse(
        {
            "database": "default",
            "host": "play.clickhouse.com",
            "port": 443,
            "username": "play",
            "password": "",
            "verify": True
        }
    )
    yield source
    if source.client:
        await source.client.close()



@pytest.mark.asyncio
async def test_clickhouse_connect_except(datasource: ClickhouseDataSource):
    logger.debug("trying to connect to an invalid source")
    await datasource._parse(
        {
            "database": "default",
            "host": "localhost",
            "port": 555,
            "username": "notexist",
            "password": "",
        }
    )
    try:
        await datasource.connect()
        assert False
    except Exception as ex:
        logger.info("expected connection exception")
        assert True


@pytest.mark.asyncio
async def test_clickhouse_connect(datasource: ClickhouseDataSource):
    try:
        await datasource.connect()
        assert True
    except Exception as ex:
        logger.error(f'Connection error: {ex}')
        assert False


@pytest.mark.asyncio
async def test_clickhouse_list_database(datasource: ClickhouseDataSource):
    logger.debug("listing databases")
    await datasource.connect()
    assert datasource.client
    databases = (await datasource.client.query("show databases")).result_rows
    logging.info(f"databases {databases}")
    assert ("default",) in databases
