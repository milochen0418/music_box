"""The box's page: the library, one song playing, and in a dialog the songs being chosen."""

from __future__ import annotations

from urllib.parse import urlsplit

import reflex as rx
from reflex_ddns_auth.intent import IntentPage

from music_box import library
from music_box.i18n import TEXT

GROUPS = ("all", "composed", "remake", "youtube", "other")


class Box(rx.State):
    lang: str = rx.LocalStorage("", name="music_box_lang")
    rows: list[library.Track] = []
    group: str = "all"
    query: str = ""
    playing: str = ""  # the ref
    repeat: bool = False
    in_dialog: bool = False
    many: bool = False
    chosen: list[str] = []

    @rx.var
    def t(self) -> dict[str, str]:
        return TEXT.get(self.lang, TEXT["zh"])

    @rx.var
    def shown(self) -> list[library.Track]:
        words = self.query.strip().lower()
        out = []
        for row in self.rows:
            if self.group != "all" and row.group != self.group:
                continue
            if words and words not in f"{row.title} {row.who} {row.style} {row.mood}".lower():
                continue
            out.append(row)
        return out

    @rx.var
    def groups(self) -> list[list[str]]:
        words = self.t
        return [[g, words[f"group_{g}"]] for g in GROUPS if g == "all" or any(r.group == g for r in self.rows)]

    @rx.var
    def now(self) -> library.Track | None:
        return next((r for r in self.rows if r.ref == self.playing), None)

    @rx.var
    def now_title(self) -> str:
        return self.now.title if self.now else ""

    @rx.var
    def now_who(self) -> str:
        return self.now.who if self.now else ""

    @rx.var
    def now_sound(self) -> str:
        return self.now.sound if self.now else ""

    @rx.var
    def studio(self) -> str:
        """Music Studio's page, next to this app on the same domain ("" when run on its own)."""
        parts = urlsplit(self.router.headers.origin or "")
        host = parts.hostname or ""
        if "." not in host or host.replace(".", "").isdigit():
            return ""
        return f"{parts.scheme}://music-studio.{host.split('.', 1)[1]}"

    def _detect_lang(self) -> None:
        if self.lang not in TEXT:
            self.lang = "zh" if "zh" in (self.router.headers.accept_language or "").lower() else "en"

    @rx.event
    def on_load(self):
        self._detect_lang()
        self.rows = library.tracks()

    @rx.event
    def open_intent(self, params: dict):
        """Asked by another app: ``many`` lets several be chosen, ``q`` starts a search."""
        self.in_dialog = True
        self.many = bool(params.get("many"))
        self.query = str(params.get("q") or "")
        self.chosen = []
        self.playing = ""
        self.on_load()

    @rx.event
    def switch_lang(self):
        self.lang = "en" if self.lang == "zh" else "zh"

    @rx.event
    def set_group(self, group: str):
        self.group = group

    @rx.event
    def set_query(self, value: str):
        self.query = value

    @rx.event
    def toggle_repeat(self):
        self.repeat = not self.repeat

    @rx.event
    def play(self, ref: str):
        self.playing = "" if self.playing == ref else ref

    @rx.event
    def stop(self):
        self.playing = ""

    def _step(self, by: int) -> None:
        order = [r.ref for r in self.shown]
        if not order:
            self.playing = ""
            return
        here = order.index(self.playing) if self.playing in order else -by
        self.playing = order[(here + by) % len(order)]

    @rx.event
    def next(self):
        self._step(1)

    @rx.event
    def back(self):
        self._step(-1)

    @rx.event
    def ended(self):
        """A song ran out: the next one, or the same again."""
        if self.repeat or self.in_dialog:
            return rx.call_script("document.getElementById('box-player')?.play()") if self.repeat else None
        self._step(1)
        return None

    @rx.event
    def choose(self, ref: str):
        if not self.many:
            return self._answer([ref])
        self.chosen = [r for r in self.chosen if r != ref] if ref in self.chosen else [*self.chosen, ref]
        return None

    @rx.event
    def use_chosen(self):
        return self._answer(self.chosen)

    def _answer(self, refs: list[str]):
        by_ref = {r.ref: r for r in self.rows}
        items = [
            {"ref": r, "title": by_ref[r].title, "seconds": by_ref[r].seconds, "loop_start": by_ref[r].loop_start, "loop_end": by_ref[r].loop_end, "rights": by_ref[r].rights}
            for r in refs
            if r in by_ref
        ]
        return IntentPage.finish({"refs": [i["ref"] for i in items], "items": items})
