from reflex_ddns_auth.collections import Collection

from music_box import library


def _publish(tmp_path, monkeypatch, owner, item_id, title, meta):
    monkeypatch.setenv("DDNS_COLLECTIONS_ROOT", str(tmp_path))
    monkeypatch.delenv("DDNS_COLLECTIONS_NODE_URL", raising=False)
    with Collection("audio", app_id=owner).publish(item_id, kind="audio.file", title=title, meta=meta, primary="a.mp3") as item:
        with item.open("a.mp3") as fh:
            fh.write(b"\xff\xfb" * 100)


def test_every_source_shows_with_what_is_known_of_it(tmp_path, monkeypatch):
    _publish(tmp_path, monkeypatch, "music-studio", "night-1", "夜行", {"duration": 125, "origin": "composed", "rights": "own", "bpm": 120, "key": "A minor", "style": "synthwave", "loop_start": 8.0, "loop_end": 72.0})
    _publish(tmp_path, monkeypatch, "youtube-to-mp3", "yt-abc", "A song", {"duration": 200, "youtube_id": "abc", "channel": "A channel"})
    _publish(tmp_path, monkeypatch, "music-studio", "changed-1", "改編", {"duration": 60, "origin": "remake", "rights": "third-party"})
    _publish(tmp_path, monkeypatch, "music-studio", "sung-1", "唱", {"duration": 60, "origin": "sung", "rights": "own"})
    _publish(tmp_path, monkeypatch, "music-studio", "cover-1", "重做", {"duration": 60, "origin": "cover", "rights": "third-party"})
    rows = {r.title: r for r in library.tracks()}
    assert rows["夜行"].group == "composed" and rows["夜行"].tempo == "120 BPM · A minor" and rows["夜行"].clock == "2:05"
    assert rows["夜行"].rights == "own" and rows["夜行"].loop_end == 72.0
    assert rows["A song"].group == "youtube" and rows["A song"].who == "A channel" and rows["A song"].rights == "third-party"
    assert rows["改編"].group == "remake" and rows["改編"].rights == "third-party"
    assert rows["唱"].group == "composed" and rows["重做"].group == "remake"


def test_only_real_songs_are_served(tmp_path, monkeypatch):
    _publish(tmp_path, monkeypatch, "music-studio", "a", "A", {"duration": 1})
    assert library.file_of("audio:music-studio/a").name == "a.mp3"
    assert library.file_of("audio:music-studio/none") is None
    assert library.file_of("../../etc/passwd") is None
    assert library.cover_of("nonsense") is None
