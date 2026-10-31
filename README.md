# Music Box 音樂盒

Everything in the shared `audio` collection in one place to listen to: what the AI wrote in Music Studio, what you changed, what you collected with YouTube to MP3. Filter by where it came from, search by title, style or mood, play through the list or repeat a song.

Other apps open it as their song picker: DDNS Intent `audio.pick` (params `many`, `q`) answers with `{"refs": [...], "items": [{"ref", "title", "seconds", "loop_start", "loop_end", "rights"}]}`.

It only reads. `rights` shows whether a song is free to use or for your own use.

```bash
poetry env use python3.11
poetry install
DDNS_COLLECTIONS_ROOT=/tmp/collections REFLEX_API_URL=http://localhost:8176 poetry run reflex run --frontend-port 3176 --backend-port 8176
poetry run pytest
DDNS_COLLECTIONS_ROOT=/tmp/collections FRONTEND_PORT=3176 BACKEND_PORT=8176 poetry run ./run_test_suite.sh box_flow
```
