import hashlib
import hmac
import os
import re
import sqlite3

import streamlit as st

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lantern_users.db")

LOGIN_CSS = """
<style>
.st-key-login_card {
  width: min(460px, 94vw);
  aspect-ratio: 3 / 4;
  margin: 1.5rem auto 3rem auto;
  padding: 2rem 1.8rem;
  box-sizing: border-box;
  background: rgba(251, 241, 220, 0.92);
  border: 2px solid #3b2a20;
  border-radius: 20px;
  box-shadow: 6px 6px 0 rgba(59, 42, 32, 0.35);
}
.st-key-login_card [data-testid="stVerticalBlock"] { gap: 0.6rem; }
.st-key-login_card [data-testid="stForm"] { border: none; padding: 0; }
.login-title { font-size: 1.8rem; line-height: 1.2; margin: 0; }
.login-sub { margin: 0.3rem 0 0.6rem 0; opacity: 0.85; }
.login-or { text-align: center; opacity: 0.7; }
.login-hint {
  max-height: 0; opacity: 0; overflow: hidden;
  transition: max-height 0.25s ease, opacity 0.25s ease;
  font-size: 0.85rem; line-height: 1.35; color: #b5502f;
}
.st-key-login_user:focus-within ~ div .login-hint { max-height: 5rem; opacity: 1; }
</style>
"""

USERNAME_HINT = (
    "Choose a username: 3 to 20 letters, numbers or underscores. "
    "No spaces. Example: lantern_writer"
)


def _db():
    con = sqlite3.connect(DB_PATH)
    con.execute(
        "CREATE TABLE IF NOT EXISTS users ("
        "username TEXT PRIMARY KEY, salt BLOB NOT NULL, pw_hash BLOB NOT NULL, "
        "created TEXT DEFAULT CURRENT_TIMESTAMP)"
    )
    return con


def _hash(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200000)


def create_user(username, password):
    username = username.strip().lower()
    if not re.fullmatch(r"[a-z0-9_]{3,20}", username):
        return False, "Username must be 3 to 20 letters, numbers or underscores."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    salt = os.urandom(16)
    con = _db()
    try:
        con.execute(
            "INSERT INTO users (username, salt, pw_hash) VALUES (?, ?, ?)",
            (username, salt, _hash(password, salt)),
        )
        con.commit()
    except sqlite3.IntegrityError:
        return False, "That username is already taken."
    finally:
        con.close()
    return True, "Account created."


def check_login(username, password):
    username = username.strip().lower()
    con = _db()
    row = con.execute(
        "SELECT salt, pw_hash FROM users WHERE username = ?", (username,)
    ).fetchone()
    con.close()
    if row is None:
        return False
    return hmac.compare_digest(_hash(password, row[0]), row[1])


def _google_ready():
    """True only when Google login has been set up in secrets."""
    try:
        return "auth" in st.secrets
    except Exception:
        return False


def _google_email():
    if not _google_ready():
        return None
    try:
        if st.user.is_logged_in:
            email = getattr(st.user, "email", None) or ""
            return email.strip().lower() or None
    except Exception:
        pass
    return None


def logout():
    via_google = st.session_state.pop("via_google", False)
    st.session_state.pop("user", None)
    if via_google:
        st.logout()
    else:
        st.rerun()


def gate():
    """Shows the login page until someone is signed in. Returns the username."""
    if st.session_state.get("user"):
        return st.session_state["user"]

    g_email = _google_email()
    if g_email:
        st.session_state["user"] = g_email
        st.session_state["via_google"] = True
        return g_email

    st.markdown(LOGIN_CSS, unsafe_allow_html=True)
    with st.container(key="login_card"):
        st.markdown(
            '<div class="login-title">Welcome to Lyric Lantern</div>'
            '<div class="login-sub">Log in, or create a free account to start writing.</div>',
            unsafe_allow_html=True,
        )
        with st.form("login_form"):
            username = st.text_input("Username", key="login_user")
            st.markdown(
                '<div class="login-hint">' + USERNAME_HINT + "</div>",
                unsafe_allow_html=True,
            )
            password = st.text_input("Password", type="password", key="login_pass")
            c1, c2 = st.columns(2)
            login_clicked = c1.form_submit_button("Log in")
            signup_clicked = c2.form_submit_button("Create account")
        message = st.empty()

        if _google_ready():
            st.markdown('<div class="login-or">or</div>', unsafe_allow_html=True)
            st.button("Continue with Google", key="google_btn", on_click=st.login)

        if login_clicked:
            if check_login(username, password):
                st.session_state["user"] = username.strip().lower()
                st.rerun()
            else:
                message.error("Wrong username or password.")
        elif signup_clicked:
            ok, msg = create_user(username, password)
            if ok:
                st.session_state["user"] = username.strip().lower()
                st.rerun()
            else:
                message.error(msg)
    st.stop()