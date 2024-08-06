import json
from http import HTTPStatus

from httpx import AsyncClient

from internals.data_node import app


async def test_create_file(client: AsyncClient, file):
    obj = file.read()
    response = await client.post(
        app.url_path_for("create_file"),
        files={"obj": (file.name, file, "application/octet-stream")},
    )

    assert response.status_code == HTTPStatus.OK, response.json()
    offset, size = response.json()['offset'], response.json()['size']
    with open("test.txt", 'rb') as f:
        f.seek(offset - size)
        x = f.read(size).decode()
        assert json.loads(x)['file'] == obj.decode()


async def test_get_file(client: AsyncClient, file):
    response = await client.post(
        app.url_path_for("create_file"),
        files={"obj": (file.name, file, "application/octet-stream")},
    )
    file_id = response.json()['id']

    response = await client.get(app.url_path_for("read_file", file_id=file_id))

    assert response.status_code == HTTPStatus.OK


async def test_get_file_when_id_not_exists_then_raise_error(client, file):
    response = await client.get(app.url_path_for("read_file", file_id="invalid_id"))

    assert response.status_code == HTTPStatus.NOT_FOUND, response.json()
