import html
import sqlite3

import streamlit as st

import auth

# Which tool each saved action belongs to (key used by the tool -> tab name)
TOOL_NAMES = {
    "cowrite": "Co-Write",
    "rhythm": "Rhythm",
    "rhyme": "Rhyme",
    "cliche": "Cliché",
    "block": "Block Breaker",
    "memory": "Memory to Song",
}


def _db():
    con = sqlite3.connect(auth.DB_PATH)
    con.execute(
        "CREATE TABLE IF NOT EXISTS hooks ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, "
        "hook TEXT NOT NULL, note TEXT DEFAULT '', "
        "created TEXT DEFAULT CURRENT_TIMESTAMP)"
    )
    con.execute(
        "CREATE TABLE IF NOT EXISTS history ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, "
        "tool TEXT NOT NULL, state_key TEXT DEFAULT '', "
        "input_text TEXT DEFAULT '', output_text TEXT DEFAULT '', "
        "created TEXT DEFAULT CURRENT_TIMESTAMP)"
    )
    return con


# ---------- hooks ----------
def add_hook(username, hook, note=""):
    con = _db()
    con.execute(
        "INSERT INTO hooks (username, hook, note) VALUES (?, ?, ?)",
        (username, hook.strip(), note.strip()),
    )
    con.commit()
    con.close()


def list_hooks(username, search=""):
    like = "%" + search + "%"
    con = _db()
    rows = con.execute(
        "SELECT id, hook, note, created FROM hooks "
        "WHERE username = ? AND (hook LIKE ? OR note LIKE ?) "
        "ORDER BY id DESC LIMIT 100",
        (username, like, like),
    ).fetchall()
    con.close()
    return rows


def delete_hook(username, hook_id):
    con = _db()
    con.execute("DELETE FROM hooks WHERE id = ? AND username = ?", (hook_id, username))
    con.commit()
    con.close()


# ---------- activity history ----------
def log_action(username, state_key, input_text, output_text, tool=None):
    tool = tool or TOOL_NAMES.get(state_key, state_key)
    con = _db()
    con.execute(
        "INSERT INTO history (username, tool, state_key, input_text, output_text) "
        "VALUES (?, ?, ?, ?, ?)",
        (username, tool, state_key, input_text, output_text),
    )
    con.commit()
    con.close()


def list_history(username, search="", tool=""):
    like = "%" + search + "%"
    sql = (
        "SELECT id, tool, state_key, input_text, output_text, created FROM history "
        "WHERE username = ? AND (input_text LIKE ? OR output_text LIKE ?)"
    )
    args = [username, like, like]
    if tool:
        sql += " AND tool = ?"
        args.append(tool)
    sql += " ORDER BY id DESC LIMIT 50"
    con = _db()
    rows = con.execute(sql, args).fetchall()
    con.close()
    return rows


def delete_history(username, item_id):
    con = _db()
    con.execute("DELETE FROM history WHERE id = ? AND username = ?", (item_id, username))
    con.commit()
    con.close()


def _open(tool, state_key, input_text, output_text):
    """Runs when you click 'Open in tool': jumps to that tool and restores your work."""
    names = st.session_state.get("page_names", [])
    if tool in names:
        st.session_state["tool_idx"] = names.index(tool) + 1
        st.session_state["tb_open"] = False
    if state_key:
        st.session_state[state_key] = input_text
        st.session_state["restore_" + state_key] = output_text


# ---------- the page ----------
def render(user):
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown(
            '<div class="card"><h3>Hook Vault</h3>'
            "<p>Save catchy lines and hook ideas. Your vault is private to your account.</p></div>",
            unsafe_allow_html=True,
        )
        hook = st.text_area("Your hook or line", height=120, key="vault_hook")
        note = st.text_input("Note or tag (optional)", key="vault_note")
        if st.button("Save to vault", key="vault_save"):
            if hook.strip():
                add_hook(user, hook, note)
                st.success("Saved to your vault.")
            else:
                st.info("Write a hook first.")
    with right:
        st.markdown(
            '<div class="card glow"><h3>Your hooks</h3></div>',
            unsafe_allow_html=True,
        )
        search = st.text_input("Search your hooks", key="vault_search")
        rows = list_hooks(user, search.strip())
        if not rows:
            st.caption("Nothing saved yet." if not search.strip() else "No hooks match your search.")
        for hid, text, nt, created in rows:
            extra = ""
            if nt:
                extra = "<br><small>Tag: " + html.escape(nt) + "</small>"
            st.markdown(
                '<div class="paper">' + html.escape(text).replace("\n", "<br>") + extra
                + "<br><small>Saved " + html.escape(created[:16]) + " UTC</small></div>",
                unsafe_allow_html=True,
            )
            if st.button("Delete", key="vault_del_" + str(hid)):
                delete_hook(user, hid)
                st.rerun()

    st.markdown(
        '<div class="card glow"><h3>Activity history</h3>'
        "<p>Everything you ran in the tools. Click Open in tool to jump back with your text and result restored.</p></div>",
        unsafe_allow_html=True,
    )
    f1, f2 = st.columns([3, 2])
    hsearch = f1.text_input("Search history", key="hist_search")
    tool_list = ["All"] + sorted(set(TOOL_NAMES.values()))
    hfilter = f2.selectbox("Tool", tool_list, key="hist_filter")
    items = list_history(user, hsearch.strip(), "" if hfilter == "All" else hfilter)
    if not items:
        st.caption("No activity yet. Use any tool and it will appear here.")
    for hid, tool, skey, inp, out, created in items:
        preview = inp if len(inp) <= 140 else inp[:140] + "..."
        st.markdown(
            '<div class="paper"><b>' + html.escape(tool) + "</b>"
            + "<br>" + html.escape(preview).replace("\n", "<br>")
            + "<br><small>" + html.escape(created[:16]) + " UTC</small></div>",
            unsafe_allow_html=True,
        )
        b1, b2 = st.columns(2)
        b1.button("Open in tool", key="hist_open_" + str(hid), on_click=_open, args=(tool, skey, inp, out))
        if b2.button("Delete", key="hist_del_" + str(hid)):
            delete_history(user, hid)
            st.rerun()