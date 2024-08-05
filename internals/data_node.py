from io import BytesIO
from typing import Annotated

from fastapi import FastAPI, File, UploadFile
from starlette.responses import StreamingResponse

app = FastAPI()


@app.post("/files")
async def create_file(obj: Annotated[UploadFile, File(...)]):
    with open("test.txt", "ab") as file:
        # TODO: implement lock mechanism for file.tell() race condition possibility
        size = file.write((await obj.read()))
        return {"id": f"{file.tell()}:{size}:{obj.filename}"}


@app.get("/files/{file_id}")
async def read_file(file_id: str):
    params = file_id.split(":")
    offset, size = map(int, [params[:2]])
    with open("test.txt", 'rb') as f:
        f.seek(offset - size)
        return StreamingResponse(
            BytesIO(f.read(size)),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment;filename={params[2]}"},
        )
