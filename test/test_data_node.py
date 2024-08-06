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
    params = response.json()['id'].split(":")
    offset, size = map(int, params[:2])
    with open("test.txt", 'rb') as f:
        f.seek(offset - size)
        assert f.read(size) == obj
