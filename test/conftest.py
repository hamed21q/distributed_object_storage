import os
from typing import AsyncGenerator

from faker import Faker
import pytest
import pytest_asyncio
from httpx import AsyncClient

from internals.data_node import app


@pytest_asyncio.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as c:
        c.headers.update({"Host": "localhost"})
        yield c


@pytest.fixture
def file():
    file_content = Faker().text()
    file_path = "./sample_file.txt"

    with open(file_path, "w") as file:
        file.write(file_content)

    with open(file_path, "rb") as file:
        yield file

    if os.path.exists(file_path):
        os.remove(file_path)
