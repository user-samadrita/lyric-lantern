## • LYRIC LANTERN

**An AI songwriting companion that helps you write, polish, and perform your own lyrics, without writing the song for you.**

Built for **GeNarrative Clash 2026** 
            [**Domain** : *AI MUSIC & SOUND STUDIO*]

- **Demo video:** https://drive.google.com/file/d/1ayRK_fzfrPf82EMVpfs7xVxsDYkkgRTS/view?usp=drivesdk 
- **Team:** **Algo-rythm**: Adrija Adhikary, Samadrita Ghosh, Snehil Raj Singh, Shivam Jain
- **Live app :**  https://lyric-lantern-app.streamlit.app/ 

---

## • The Problem

Most AI lyric tools generate a whole song and take the creative work away from the writer. Songwriters actually get stuck on small things: a line that won't flow, a clichéd phrase, a word that won't rhyme, or a blank page. Lyric Lantern is a **co-writer, not a ghostwriter**. It nudges, critiques, and sparks ideas, while the song stays yours.

## • Features (what's built in this MVP)

| ◉ | FEATURE | What it does |
|---|---------|--------------|
| 1 | **Co-Write** | Give one line, get 3 directions to continue (emotional, imagery, twist) |
| 2 | **Rhythm** | Syllable count per line, flags where the flow breaks, suggests small fixes |
| 3 | **Rhyme** | Perfect and slant rhymes grouped by sound, with mood notes |
| 4 | **Cliché Detector** | Spots overused phrases and suggests fresher imagery |
| 5 | **Block Breaker** | Three playful creative constraints when you're stuck (never writes the verse for you) |
| 6 | **Voice Switch** | Rewrites a verse: sad↔hopeful, first↔second person |
| 7 | **Stage Mode** | Big-screen performance view with `[Am]`-style chords shown above lyrics and adjustable text size |
| 8 | **Photo to Mood** | Upload a photo and get moods, lyric imagery, and a song idea (multimodal) |
| 9 | **Chords + MIDI** | Mood and genre produce a chord progression, with downloadable chord and melody-sketch `.mid` files |
| 10 | **Hum to Melody** | Hum into the mic; pitch detection (autocorrelation, NumPy) turns it into notes and a MIDI file |
| 11 | **Collab** | Shared room code for co-writers, with a live-refreshing song view and feedback |
| 12 | **Memory to Song** | Describe a personal memory and get a song concept with a title, mood, lyric images, hook idea, and first-verse direction |
| 13 | **Genre Blender** | Combine two genres and get a style guide covering rhythm, instruments, lyric tone, chord ideas, and a song concept |
| 14 | **Multilingual Writing** | Work in English, Bengali, Hindi, or Hinglish, or let the app detect the language from your writing |
| 15 | **Hook Vault** | Save, search, and delete your catchy lines and hook ideas in a private, account-specific vault |
| 16 | **Activity History** | Review past writing-tool outputs, search your history, filter by tool, reopen work in its original tool, and delete entries |

Extras: a warm lantern-themed UI, ambient pad music toggle (Web Audio API), and sparkle sounds on button clicks.

## • Login and Accounts

- Create a free account from the login screen using a username and password, or log in with an existing account.
- Usernames must be 3 to 20 characters and may contain lowercase letters, numbers, and underscores. Passwords must be at least 6 characters long.
- Usernames are stored in lowercase. Passwords are not stored as plain text; the app stores a salted PBKDF2-SHA256 password hash.
- Google sign-in is also supported when Google authentication is configured in Streamlit secrets.
- Your Hook Vault and activity history are associated with your signed-in account.
- **There are no shared default login credentials.** On first use, select **Create account** and choose your own username and password.

## • Responsible-AI choices

- Every prompt tells the model **never to copy existing songs or imitate a living writer's lyrics**.
- Features are designed to **assist, not replace** the writer (e.g. Block Breaker explicitly does not write the verse).
- User text is HTML-escaped before being rendered back on the page.

## • Tech Stack

- **Frontend / App:** [Streamlit](https://streamlit.io) with custom CSS
- **AI:** Google Gemini (`gemini-3.5-flash-lite`) via the `google-genai` SDK (text and image input)
- **Audio / music:** NumPy (pitch detection), hand-built MIDI writer, Web Audio API (ambient sound)
- **Storage / accounts:** SQLite for user accounts, Hook Vault entries, and activity history; PBKDF2-SHA256 password hashing
- **Config:** `python-dotenv`

## • Project Structure

```
lyric-lantern/
├── app.py              # Main app: Gemini client, login gate, writing tools, language selection
├── auth.py             # Account creation, login, password hashing, optional Google sign-in
├── more_features.py    # Photo Mood, Chords/MIDI, Hum, and Collab
├── vault.py            # Hook Vault and per-user activity history
├── lantern_style.py    # Theme, CSS, sidebar "toolbox" navigation
├── requirements.txt
├── .env.example        # Template for your Gemini API key
└── .streamlit/config.toml
```

## •  Run Locally

**Requirements:** Python 3.10+ and a free [Gemini API key](https://aistudio.google.com/apikey).

```bash
git clone https://github.com/<your_username>/lyric-lantern.git
cd lyric-lantern

python -m venv venv
source venv/bin/activate        # Windows: venv\\Scripts\\activate

pip install -r requirements.txt

cp .env.example .env            # Windows: copy .env.example .env
# open .env and set GEMINI_API_KEY=your_real_key

streamlit run app.py
```

Then open http://localhost:8501. Create your account on the login screen to get started.

## • Deploy (Streamlit Community Cloud)

1. Push the repo to GitHub (public).
2. Go to [share.streamlit.io](https://share.streamlit.io), click **New app**, and select the repo with `app.py` as the entry file.
3. Under **Advanced settings → Secrets**, add: `GEMINI_API_KEY = "your_key"`.
4. If you want to enable Google sign-in, configure the Streamlit `[auth]` settings and the required Google OAuth credentials in the app's secrets.

**Important:** The app creates its SQLite database (`lantern_users.db`) locally when users register. On hosting platforms, local files may not be persistent across app rebuilds/redeployments unless persistent storage is configured. For durable accounts, hooks, and history, use a persistent database/storage setup.

## ∆ Known Limitations (MVP)

- **Collab** rooms live in server memory, so they reset on restart and work on a single instance only.
- **Hum to Melody** is a rough monophonic pitch tracker. Best in a quiet room, one note at a time.
- **SQLite data** is stored in the app's local filesystem; persistence depends on the hosting environment and its storage configuration.
- **AI replies** depend on Gemini API availability and free-tier rate limits.
- **Google sign-in** is available only after OAuth authentication has been configured in Streamlit secrets.

## • Roadmap: Beyond the Current Build

The original finale-build items for Memory to Song, Genre Blender, Bengali/Hindi/Hinglish support, and Hook Vault are now implemented in the app. The next improvements can focus on making the current experience more robust and persistent.

| ◉ | PLANNED FEATURE | Idea |
|---|-----------------|------|
| 1 | **Persistent Cloud Storage** | Move accounts, saved hooks, and activity history to a managed database so user data remains available across redeployments |
| 2 | **Real Multi-User Collaboration** | Replace in-memory collaboration rooms with persistent, synchronized rooms that support multiple users reliably |
| 3 | **Saved Songs** | Let writers save complete songs and organize drafts in their accounts |
| 4 | **PDF Export** | Export lyrics with chord annotations as clean, printable PDF sheets |

*Emotion Arc Map is not included in the current feature list or roadmap.*

## • Team Algo-rythm

| Name | Contribution |
|------|--------------|
| **Adrija Adhikary** (Team Lead) | Project idea, Devfolio registration, team host, demo video voice over|
| **Samadrita Ghosh** | Coding, project structure, Streamlit app development |
| **Snehil Raj Singh** | UI description and design direction, demo video editing |
| **Shivam Jain** | Feature suggestions, screen recording of the demo |
