from aqt import mw, gui_hooks
from aqt.utils import tooltip

CSS = "Custom Study Session"
CARD_LIMIT = 9999

def insert_review_button(overview, content):
    # If we're in the "Custom Study Session" deck page then we don't insert the
    # review button.
    current = overview.mw.col.decks.current()
    cur_name = current.get("name") if isinstance(current, dict) else ""
    if cur_name == CSS:
        return

    review_button = f"""
    <button id="start_review" class="but"
            style="margin-left: 4px;"
            onclick="pycmd('start_review');return false;"
            title="Shortcut key: Shift+R">
      Review
    </button>
    """
    content.table = content.table.replace("</button>", "</button>" + review_button, 1)

def on_js_message(handled, message, context):
    if message == "start_review":
        do_start_review()
        return (True, None)
    return handled

def do_start_review():
    current = mw.col.decks.current()
    deck_name = current.get("name") if isinstance(current, dict) else None
    if not deck_name:
        tooltip("⚠️ Could not determine current deck.", 3000)
        return

    # Remove an old session with the same name (if any).
    existing = mw.col.decks.by_name(CSS)
    if existing:
        try:
            mw.col.decks.remove([existing["id"]])
        except Exception:
            pass

    # Creating the Custom Study Session:
    deck = mw.col.decks.id(CSS)
    conf = mw.col.decks.get(deck)
    conf["dyn"] = True
    deck_esc = deck_name.replace('"', '\\"')
    search_str = f'deck:"{deck_esc}" (is:due OR is:learn)'
    conf["terms"] = [[search_str, CARD_LIMIT, 1]]
    conf["resched"] = True

    try:
        mw.col.decks.save(conf)
        mw.col.sched.rebuild_filtered_deck(deck)
        mw.col.decks.select(deck)
        mw.moveToState("review")
    except Exception as e:
        tooltip(f"⚠️ Custom session failed: {e}", 4000)

def add_shortcut(state, shortcuts):
    if state != "overview":
        return
    shortcuts[:] = [(k, fn) for (k, fn) in shortcuts if str(k).lower() != "shift+r"]
    shortcuts.append(("Shift+R", do_start_review))

gui_hooks.overview_will_render_content.append(insert_review_button)
gui_hooks.webview_did_receive_js_message.append(on_js_message)
gui_hooks.state_shortcuts_will_change.append(add_shortcut)
