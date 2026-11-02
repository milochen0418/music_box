"""The box's page, on its own and as the song picker in another app's dialog."""

from __future__ import annotations

import reflex as rx
from reflex.utils.imports import ImportVar
from reflex.vars import VarData

from music_box.library import Track
from music_box.state import Box

T = Box.t


class Player(rx.el.audio.__self__):
    """The page's <audio>, which also says when a song has run out."""

    on_ended: rx.EventHandler[lambda: []]


# The backend's origin: the /_box links are relative to it (two ports on a laptop, one here).
BACKEND = rx.Var(
    _js_expr="getBackendURL(env.UPLOAD).origin",
    _var_data=VarData(imports={"$/utils/state": "getBackendURL", "$/env.json": ImportVar(tag="env", is_default=True)}),
).to(str)
ROUND = "inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full transition-colors"


def _header() -> rx.Component:
    return rx.el.header(
        rx.el.div(rx.icon("disc-3", size=22, class_name="text-sky-300"), rx.el.span(T["app"], class_name="text-lg font-bold tracking-wide"), class_name="flex items-center gap-2"),
        rx.el.div(
            rx.cond(Box.studio != "", rx.el.a(rx.icon("sparkles", size=14), T["make"], href=Box.studio, target="_blank", class_name="hidden items-center gap-1 text-sm text-amber-300 hover:underline sm:inline-flex")),
            rx.el.button(rx.icon("languages", size=16), T["lang_other"], on_click=Box.switch_lang, data_testid="lang", class_name="flex items-center gap-1.5 rounded-full border border-slate-700 px-3 py-1 text-sm text-slate-300 hover:border-slate-500"),
            class_name="flex items-center gap-3",
        ),
        class_name="flex items-center justify-between py-4",
    )


def _filters() -> rx.Component:
    return rx.el.div(
        # The box keeps its own text: a value written back per key cuts Chinese input off.
        rx.el.input(id="search", default_value=Box.query, on_change=Box.set_query.debounce(200), placeholder=T["search"], data_testid="search", class_name="min-w-0 flex-1 rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:border-sky-400 focus:outline-none"),
        rx.el.div(
            rx.foreach(
                Box.groups,
                lambda g: rx.el.button(g[1], on_click=Box.set_group(g[0]), data_testid="group-" + g[0], class_name=rx.cond(Box.group == g[0], "rounded-full bg-sky-300 px-3 py-1 text-sm font-semibold text-slate-950", "rounded-full border border-slate-700 px-3 py-1 text-sm text-slate-300 hover:border-slate-500")),
            ),
            class_name="flex flex-wrap gap-2",
        ),
        class_name="flex flex-wrap items-center gap-3",
    )


def _cover(row: Track) -> rx.Component:
    return rx.cond(
        row.cover != "",
        rx.image(src=BACKEND + row.cover, alt="", class_name="h-12 w-12 shrink-0 rounded-lg object-cover"),
        rx.el.div(rx.icon("music-2", size=18, class_name="text-slate-500"), class_name="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-slate-800"),
    )


def _row(row: Track) -> rx.Component:
    return rx.el.div(
        rx.el.button(
            rx.cond(Box.playing == row.ref, rx.icon("pause", size=16), rx.icon("play", size=16)),
            on_click=Box.play(row.ref),
            data_testid="play",
            title=row.title,
            class_name=rx.cond(Box.playing == row.ref, f"{ROUND} bg-sky-300 text-slate-950", f"{ROUND} bg-slate-800 text-slate-200 hover:bg-slate-700"),
        ),
        _cover(row),
        rx.el.div(
            rx.el.div(row.title, class_name="truncate font-medium"),
            rx.el.div(
                rx.el.span(row.who, class_name="truncate"),
                rx.cond(row.tempo != "", rx.el.span("· ", row.tempo, class_name="hidden shrink-0 sm:inline")),
                rx.cond(row.loop_end > 0, rx.el.span(rx.icon("repeat", size=11), class_name="shrink-0 text-emerald-300", title=T["loops"])),
                class_name="flex items-center gap-1.5 text-xs text-slate-400",
            ),
            class_name="min-w-0 flex-1",
        ),
        rx.el.span(rx.cond(row.rights == "own", T["free"], T["personal"]), class_name=rx.cond(row.rights == "own", "hidden shrink-0 rounded-full bg-emerald-950 px-2 py-0.5 text-[11px] text-emerald-300 sm:inline", "hidden shrink-0 rounded-full bg-amber-950 px-2 py-0.5 text-[11px] text-amber-300 sm:inline")),
        rx.el.span(row.clock, class_name="shrink-0 font-mono text-xs text-slate-400"),
        rx.cond(
            Box.in_dialog,
            rx.el.button(
                rx.cond(Box.chosen.contains(row.ref), T["chosen"], T["choose"]),
                on_click=Box.choose(row.ref),
                data_testid="choose",
                class_name=rx.cond(Box.chosen.contains(row.ref), "shrink-0 rounded-lg bg-sky-300 px-3 py-1.5 text-sm font-semibold text-slate-950", "shrink-0 rounded-lg border border-slate-600 px-3 py-1.5 text-sm text-slate-100 hover:border-sky-300"),
            ),
        ),
        data_testid="track",
        class_name=rx.cond(Box.playing == row.ref, "flex items-center gap-3 rounded-xl bg-slate-800/70 p-2", "flex items-center gap-3 rounded-xl p-2 hover:bg-slate-900"),
    )


def _list() -> rx.Component:
    return rx.cond(
        Box.rows.length() > 0,
        rx.cond(
            Box.shown.length() > 0,
            rx.el.div(rx.foreach(Box.shown, _row), data_testid="tracks", class_name="mt-4 space-y-1"),
            rx.el.p(T["none_found"], class_name="mt-6 text-sm text-slate-400"),
        ),
        rx.el.p(T["empty"], data_testid="empty", class_name="mt-6 text-sm text-slate-400"),
    )


def _player() -> rx.Component:
    return rx.cond(
        Box.playing != "",
        rx.el.div(
            rx.el.button(rx.icon("skip-back", size=16), on_click=Box.back, class_name=f"{ROUND} text-slate-300 hover:bg-slate-800"),
            rx.el.button(rx.icon("skip-forward", size=16), on_click=Box.next, data_testid="next", class_name=f"{ROUND} text-slate-300 hover:bg-slate-800"),
            rx.el.div(rx.el.div(Box.now_title, data_testid="now", class_name="truncate text-sm font-medium"), rx.el.div(Box.now_who, class_name="truncate text-xs text-slate-400"), class_name="w-40 min-w-0 sm:w-56"),
            Player.create(id="box-player", src=BACKEND + Box.now_sound, auto_play=True, controls=True, on_ended=Box.ended, class_name="h-9 min-w-0 flex-1"),
            rx.el.button(rx.icon("repeat-1", size=16), on_click=Box.toggle_repeat, title=T["repeat"], data_testid="repeat", class_name=rx.cond(Box.repeat, f"{ROUND} bg-sky-300 text-slate-950", f"{ROUND} text-slate-300 hover:bg-slate-800")),
            class_name="fixed inset-x-0 bottom-0 z-20 flex items-center gap-2 border-t border-white/10 bg-slate-950/95 px-4 py-2 backdrop-blur",
        ),
    )


def index() -> rx.Component:
    return rx.el.div(
        rx.el.div(_header(), rx.el.p(T["tagline"], class_name="pb-4 text-slate-300"), _filters(), _list(), data_testid="box", class_name="mx-auto max-w-4xl px-4 pb-28"),
        _player(),
        class_name="min-h-screen bg-slate-950 text-slate-100",
    )


def dialog() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            _filters(),
            _list(),
            rx.cond(Box.many, rx.el.button(T["use"], on_click=Box.use_chosen, data_testid="use", class_name="mt-4 rounded-xl bg-sky-300 px-4 py-2 text-sm font-semibold text-slate-950")),
            data_testid="box",
            class_name="p-4 pb-20",
        ),
        _player(),
        class_name="min-h-[60vh] bg-slate-950 text-slate-100",
    )
