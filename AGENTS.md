# AGENTS.md

Read `README.md` first. Python 3.11 through Poetry; `poetry run` for everything; E2E through `./run_test_suite.sh <suite>` with a scratch `DDNS_COLLECTIONS_ROOT` holding some `audio` items.

This app reads the collection and never writes it. A dataclass field named `length` clashes with `ObjectVar.length()` in `rx.foreach`: rows use `clock`. `rx.el.audio` has no `on_ended`: `views.Player` adds it.
