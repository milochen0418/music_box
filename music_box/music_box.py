"""Music Box (音樂盒): listen to everything in the shared ``audio`` collection.

``/`` is the box; ``/intent/audio-pick`` the same as a song picker in another app's dialog (DDNS
Intent ``audio.pick``; ``many`` lets several be chosen, ``q`` starts a search). The answer is
``{"refs": [...], "items": [{"ref", "title", "seconds", "loop_start", "loop_end", "rights"}]}``.
"""

import reflex as rx
from reflex_ddns_auth.intent import intent

from music_box.api import api
from music_box.state import Box
from music_box.views import dialog, index

app = rx.App(api_transformer=api)
app.add_page(index, route="/", title="音樂盒 · Music Box", on_load=Box.on_load)


@intent(app, action="audio.pick", title="Pick music", params={"many": bool, "q": str}, on_open=Box.open_intent)
def pick_intent() -> rx.Component:
    return dialog()
