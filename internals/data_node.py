from datetime import datetime
from http import HTTPStatus
from io import BytesIO
from typing import Annotated, Optional

from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from pydantic import BaseModel, computed_field
from redis import Redis
from snowflake import SnowflakeGenerator
from starlette.responses import StreamingResponse

from internals.conn import get_redis

app = FastAPI()
snow_flake_generator = SnowflakeGenerator(42)


class ObjectModel(BaseModel):
    file: Optional[bytes] = None
    deleted: Optional[bool] = False

    @computed_field
    @property
    def id(self) -> int:
        return next(snow_flake_generator)


@app.post("/files")
async def create_file(
        obj: Annotated[UploadFile, File(...)], redis: Annotated[Redis, Depends(get_redis)]
):
    with open("test.txt", "a") as file:
        # TODO: implement lock mechanism for file.tell() race condition possibility
        model = ObjectModel(file=(await obj.read()))
        size = file.write(model.model_dump_json())
        meta = {
            "offset": file.tell(),
            "size": size,
            "id": model.id,
            "timestamp": datetime.utcnow().timestamp(),
            "file_name": obj.filename,
        }
    redis.hset(meta["id"], mapping=meta)
    return meta


def get_params(file_id: str, redis: Annotated[Redis, Depends(get_redis)]):
    params = redis.hgetall(file_id)
    if not params:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
    d = {}
    for key, value in params.items():
        try:
            d[key.decode()] = int(value.decode())
        except ValueError:
            d[key.decode()] = value.decode()
    return d


@app.get("/files/{file_id}")
async def read_file(params: Annotated[dict, Depends(get_params)]):
    with open("test.txt", "rb") as f:
        f.seek(params['offset'] - params['size'])
        return StreamingResponse(
            BytesIO(f.read(params['size'])),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment;filename={params['file_name']}"},
        )
