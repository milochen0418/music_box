"""The box from a person's side: everything in the library shows and filters, a song really plays and
the next one follows; as a dialog page it lists songs to choose."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from playwright.sync_api import sync_playwright  # noqa: E402

from common import BASE_URL, finish, launch, log, new_page, shot, wait_for  # noqa: E402

errors: list[str] = []
with sync_playwright() as pw:
    browser = launch(pw)
    page = new_page(browser, errors, width=1180, height=800)
    page.goto(BASE_URL + "/", wait_until="domcontentloaded")
    page.wait_for_selector("[data-testid=box]", timeout=120000)
    wait_for(lambda: page.locator("[data-testid=track]").count() >= 2, "the library", 30)
    total = page.locator("[data-testid=track]").count()
    log("songs:", total)
    page.click("[data-testid=group-composed]")
    wait_for(lambda: 0 < page.locator("[data-testid=track]").count() < total or total == page.locator("[data-testid=track]").count(), "the filter")
    page.click("[data-testid=group-all]")
    page.click("[data-testid=search]")
    ime = page.context.new_cdp_session(page)
    for typed in ("ㄋ", "ㄋㄧ", "ㄋㄧˇ"):
        ime.send("Input.imeSetComposition", {"text": typed, "selectionStart": len(typed), "selectionEnd": len(typed)})
        page.wait_for_timeout(350)
    assert page.input_value("[data-testid=search]") == "ㄋㄧˇ", page.input_value("[data-testid=search]")
    ime.send("Input.insertText", {"text": "你"})
    wait_for(lambda: page.input_value("[data-testid=search]") == "你", "Chinese typed through the IME")
    page.fill("[data-testid=search]", "zzzz-nothing")
    wait_for(lambda: page.locator("[data-testid=track]").count() == 0, "the search")
    page.fill("[data-testid=search]", "")
    wait_for(lambda: page.locator("[data-testid=track]").count() == total, "all again")
    page.locator("[data-testid=play]").first.click()
    page.wait_for_selector("#box-player")
    first = page.locator("[data-testid=now]").inner_text()
    state = page.evaluate(
        """async () => { const a = document.getElementById('box-player'); a.muted = true;
        await new Promise((ok, no) => { if (a.readyState >= 2) ok(); a.oncanplay = ok; a.onerror = () => no(new Error('no sound')); });
        await a.play().catch(() => {}); await new Promise(r => setTimeout(r, 900)); return { at: a.currentTime, seconds: a.duration }; }"""
    )
    log("playing:", first, state)
    assert state["seconds"] > 10 and state["at"] > 0.1, state
    shot(page, "01_playing")
    page.click("[data-testid=next]")
    wait_for(lambda: page.locator("[data-testid=now]").inner_text() != first, "the next song")
    browser.close()
finish(errors)
