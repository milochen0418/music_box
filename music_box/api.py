"""The songs' sound and covers, next to Reflex's routes (``backend-paths.txt`` sends ``/_box/`` here
behind re-ddns)."""

from __future__ import annotations

import asyncio
import mimetypes

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse, PlainTextResponse, Response
from starlette.routing import Route

from music_box import library

HEADERS = {"Access-Control-Allow-Origin": "*", "Cache-Control": "private, max-age=3600"}


async def sound(request: Request) -> Response:
    path = await asyncio.to_thread(library.file_of, request.query_params.get("ref", ""))
    if path is None:
        return PlainTextResponse("no such song", status_code=404, headers=HEADERS)
    return FileResponse(path, media_type=mimetypes.guess_type(path.name)[0] or "audio/mpeg", headers=HEADERS)


async def cover(request: Request) -> Response:
    path = await asyncio.to_thread(library.cover_of, request.query_params.get("ref", ""))
    if path is None:
        return PlainTextResponse("no cover", status_code=404, headers=HEADERS)
    return FileResponse(path, media_type=mimetypes.guess_type(path.name)[0] or "image/jpeg", headers=HEADERS)


api = Starlette(routes=[Route("/_box/sound", sound, methods=["GET"]), Route("/_box/cover", cover, methods=["GET"])])
