"""What is in the shared ``audio`` collection, as rows for the page. Reading only: every app that
brings music publishes it there (YouTube to MP3, Music Studio), and this plays it all."""

from __future__ import annotations

import dataclasses
from pathlib import Path
from urllib.parse import quote

from reflex_ddns_auth.collections import Collection, CollectionError

COLLECTION = "audio"
KIND = "audio.file"


def audio() -> Collection:
    return Collection(COLLECTION)


def _clock(seconds: float) -> str:
    m, s = divmod(int(round(seconds or 0)), 60)
    return f"{m}:{s:02d}"


def _number(value: object) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


@dataclasses.dataclass
class Track:
    ref: str
    title: str
    clock: str
    seconds: float
    group: str  # composed, remake, youtube or other
    who: str  # the channel, or the app that made it
    style: str
    mood: str
    tempo: str  # "120 BPM · A minor"
    rights: str  # own, or third-party when somebody else may hold them
    sound: str  # a path on the backend
    cover: str  # a path on the backend, "" without one
    loop_start: float
    loop_end: float


def group_of(owner: str, meta: dict) -> str:
    origin = str(meta.get("origin") or "")
    if origin in ("composed", "remake"):
        return origin
    return "youtube" if meta.get("youtube_id") or owner == "youtube-to-mp3" else "other"


def tracks() -> list[Track]:
    """Everything here, newest first."""
    try:
        items = audio().items(kind=KIND, remote=False)
    except CollectionError:
        return []
    items.sort(key=lambda i: i.created_at, reverse=True)
    rows = []
    for item in items:
        path = item.primary
        if path is None or not path.is_file():
            continue
        meta = item.meta
        seconds = _number(meta.get("duration"))
        group = group_of(item.owner, meta)
        bpm = _number(meta.get("bpm"))
        key = str(meta.get("key") or "")
        tempo = " · ".join(p for p in (f"{bpm:.0f} BPM" if bpm else "", key) if p)
        link = quote(item.ref, safe="")
        rows.append(
            Track(
                ref=item.ref,
                title=item.title or item.id,
                clock=_clock(seconds),
                seconds=seconds,
                group=group,
                who=str(meta.get("channel") or meta.get("artist") or item.owner),
                style=str(meta.get("style") or ""),
                mood=str(meta.get("mood") or ""),
                tempo=tempo,
                rights=str(meta.get("rights") or ("own" if group == "composed" else "third-party")),
                sound=f"/_box/sound?ref={link}",
                cover=f"/_box/cover?ref={link}" if item.thumbnail is not None else "",
                loop_start=_number(meta.get("loop_start")),
                loop_end=_number(meta.get("loop_end")),
            )
        )
    return rows


def file_of(ref: str) -> Path | None:
    try:
        item = audio().get(ref, remote=False)
    except CollectionError:
        return None
    if item is None or item.kind != KIND:
        return None
    path = item.primary
    return path if path is not None and path.is_file() else None


def cover_of(ref: str) -> Path | None:
    try:
        item = audio().get(ref, remote=False)
    except CollectionError:
        return None
    return item.thumbnail if item is not None else None
