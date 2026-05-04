import streamlit as st
import google.generativeai as genai
import re

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Dark Files | Detective Agency", page_icon="🕯", layout="centered")

# ── STYLING ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=EB+Garamond&display=swap');
html, body, [class*="css"] { background-color: #0d0b08 !important; color: #d4c5a0 !important; font-family: 'EB Garamond', serif !important; }
.stApp { background-color: #0d0b08 !important; }
.game-title { font-family: 'Playfair Display', serif; font-size: 36px; color: #e8c96d; letter-spacing: 0.15em; text-transform: uppercase; text-shadow: 0 0 30px rgba(200,160,60,0.3); text-align:center; padding-top:30px; }
.game-subtitle { font-size: 12px; color: #7a6040; letter-spacing: 0.3em; text-transform: uppercase; text-align:center; margin-bottom:20px; }
.case-badge { display:inline-block; background:rgba(200,160,60,0.1); border:1px solid #3a2810; color:#c9a84c; padding:4px 14px; border-radius:20px; font-size:12px; letter-spacing:0.2em; }
.gm-label { font-size:10px; color:#5a4020; letter-spacing:0.25em; text-transform:uppercase; margin-bottom:6px; margin-top:16px; }
.gm-message { background:rgba(255,255,255,0.025); border:1px solid #1e1a12; border-radius:2px 12px 12px 12px; padding:16px 20px; font-size:15px; line-height:1.8; color:#d4c5a0; }
.user-message { background:linear-gradient(135deg,#2a1e0e,#1e1508); border:1px solid #3a2810; border-radius:12px 12px 2px 12px; padding:14px 18px; margin:12px 0 12px 60px; font-size:15px; line-height:1.8; color:#c8a878; }
.stButton > button { background:linear-gradient(135deg,#c9a84c,#8b6914) !important; color:#0d0b08 !important; border:none !important; font-family:'Playfair Display',serif !important; font-weight:700 !important; letter-spacing:0.15em !important; text-transform:uppercase !important; padding:12px 32px !important; border-radius:6px !important; font-size:13px !important; }
.stTextInput > div > div > input { background:rgba(255,255,255,0.02) !important; border:1px solid #2a2010 !important; border-radius:8px !important; color:#d4c5a0 !important; font-family:'EB Garamond',serif !important; font-size:15px !important; padding:12px 16px !important; }
#MainMenu, footer, header { visibility:hidden; }
.block-container { padding-top:0 !important; max-width:780px !important; }
hr { border-color:#2a2010 !important; }
</style>
""", unsafe_allow_html=True)

# ── SYSTEM PROMPT ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an intelligent detective game master AI running an interactive detective game.

GAME RULES:
- Each session, generate a completely new and unique case.
- Difficulty follows MIXED PROGRESSION (start easier, gradually increase complexity).
- Case style adapts naturally (realistic crime, thriller, psychological, mystery, etc.)

GAMEPLAY:
1. Start with a compelling case introduction (victim, setting, situation).
2. Do NOT reveal the solution upfront.
3. Present clues STEP-BY-STEP after each player response.
4. Allow: questions, requesting clues, interrogating suspects, making deductions.

INTERACTION:
- Respond like a game master, NOT like an AI.
- Only reveal info specifically asked for or logically discovered.
- Reward good questions with meaningful clues.
- Don't immediately correct wrong assumptions — let the player explore.

CASE ELEMENTS: Suspects with motives/alibis, red herrings, plot twists, evidence.

ENDING: When player gives final answer — evaluate correctness, explain full solution, highlight missed clues.

STYLE: Immersive, suspenseful, cinematic. Use **bold** for key clues/names. Keep responses concise but impactful."""

# ── SESSION STATE ─────────────────────────────────────────────────────────────
for key, default in {"conversation": [], "messages_display": [], "game_started": False, "case_number": 1, "api_key": ""}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── HELPERS ───────────────────────────────────────────────────────────────────
def fmt(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color:#e8c96d">\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em style="color:#b8a080">\1</em>', text)
    return text.replace('\n', '<br>')

def call_gemini(user_message):
    try:
        genai.configure(api_key=st.session_state.api_key)
        model = genai.GenerativeModel(model_name="gemini-2.0-flash", system_instruction=SYSTEM_PROMPT)
        history = [{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.conversation]
        chat = model.start_chat(history=history)
        response = chat.send_message(user_message)
        reply = response.text
        st.session_state.conversation.append({"role": "user", "content": user_message})
        st.session_state.conversation.append({"role": "model", "content": reply})
        return reply
    except Exception as e:
        err = str(e)
        if "API_KEY_INVALID" in err or "invalid" in err.lower():
            return "❌ Invalid API key. Please check and re-enter your Gemini API key."
        return f"*Connection lost… try again.*\n\nError: {err}"

def start_case():
    st.session_state.conversation = []
    st.session_state.messages_display = []
    st.session_state.game_started = True
    reply = call_gemini("Start a new detective case. Give me a compelling case introduction.")
    st.session_state.messages_display.append({"role": "assistant", "content": reply})

def new_case():
    st.session_state.case_number += 1
    st.session_state.conversation = []
    st.session_state.messages_display = []
    reply = call_gemini("Start a completely new detective case. Give me the case introduction.")
    st.session_state.messages_display.append({"role": "assistant", "content": reply})

def send_message(text):
    if not text.strip(): return
    st.session_state.messages_display.append({"role": "user", "content": text})
    reply = call_gemini(text)
    st.session_state.messages_display.append({"role": "assistant", "content": reply})

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown('<div class="game-title">🕯 Dark Files</div>', unsafe_allow_html=True)
st.markdown('<div class="game-subtitle">Detective Agency</div>', unsafe_allow_html=True)
st.markdown('<hr>', unsafe_allow_html=True)

# ── API KEY SCREEN ────────────────────────────────────────────────────────────
if not st.session_state.api_key:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p style="color:#8a7050;text-align:center;font-size:15px;">Enter your <strong style="color:#c9a84c;">FREE</strong> Gemini API key to begin</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        key_input = st.text_input("", placeholder="AIzaSy...", type="password", label_visibility="collapsed")
        if st.button("🔑  Unlock the Files", use_container_width=True):
            if key_input.strip():
                st.session_state.api_key = key_input.strip()
                st.rerun()
            else:
                st.error("Please enter your API key.")
    st.markdown("""
    <div style="text-align:center;margin-top:28px;padding:20px;background:rgba(200,160,60,0.05);border:1px solid #2a2010;border-radius:8px;">
        <p style="color:#c9a84c;font-size:14px;font-weight:bold;margin-bottom:12px;">🆓 How to get your FREE Gemini API Key</p>
        <p style="color:#7a6040;font-size:13px;line-height:2.2;margin:0;">
            1. Go to <strong style="color:#e8c96d;">aistudio.google.com</strong><br>
            2. Sign in with your Google account<br>
            3. Click <strong style="color:#e8c96d;">"Get API Key"</strong> on the left<br>
            4. Click <strong style="color:#e8c96d;">"Create API Key"</strong><br>
            5. Copy the key and paste it above
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── LANDING SCREEN ────────────────────────────────────────────────────────────
if not st.session_state.game_started:
    st.markdown("""
    <div style="text-align:center;padding:30px 0 20px;">
        <div style="font-size:64px;margin-bottom:20px;">🕵️</div>
        <p style="color:#8a7050;font-size:16px;max-width:420px;margin:0 auto;line-height:1.8;">
            An AI-powered detective investigation where every case is unique, every clue matters, and every answer must be earned.
        </p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div style="background:rgba(255,255,255,0.02);border:1px solid #1e1810;border-radius:6px;padding:12px 16px;color:#8a7050;font-size:13px;margin-bottom:8px;">🔍 Unique AI-generated cases</div>', unsafe_allow_html=True)
        st.markdown('<div style="background:rgba(255,255,255,0.02);border:1px solid #1e1810;border-radius:6px;padding:12px 16px;color:#8a7050;font-size:13px;">🎭 Cinematic storytelling</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div style="background:rgba(255,255,255,0.02);border:1px solid #1e1810;border-radius:6px;padding:12px 16px;color:#8a7050;font-size:13px;margin-bottom:8px;">🗂 Suspects, motives & red herrings</div>', unsafe_allow_html=True)
        st.markdown('<div style="background:rgba(255,255,255,0.02);border:1px solid #1e1810;border-radius:6px;padding:12px 16px;color:#8a7050;font-size:13px;">⚖️ Your reasoning is evaluated</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🕯  Open First Case", use_container_width=True):
            start_case()
            st.rerun()
    st.stop()

# ── GAME SCREEN ───────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f'<div class="case-badge">CASE #{str(st.session_state.case_number).zfill(3)}</div>', unsafe_allow_html=True)
with col2:
    if st.button("New Case →"):
        new_case()
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

for msg in st.session_state.messages_display:
    if msg["role"] == "assistant":
        st.markdown(f'<div class="gm-label">◈ Game Master</div><div class="gm-message">{fmt(msg["content"])}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="user-message">{fmt(msg["content"])}</div>', unsafe_allow_html=True)

if len(st.session_state.messages_display) <= 2:
    st.markdown("<br>", unsafe_allow_html=True)
    cols = st.columns(4)
    for i, s in enumerate(["Ask about suspects", "Examine crime scene", "Request more clues", "Final answer"]):
        with cols[i]:
            if st.button(s, key=f"sug_{i}"):
                send_message(s)
                st.rerun()

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<p style="color:#5a4020;font-size:12px;letter-spacing:0.1em;">YOUR MOVE, DETECTIVE</p>', unsafe_allow_html=True)
col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.text_input("", placeholder="Ask a question, interrogate a suspect, or make your deduction…", label_visibility="collapsed", key="input")
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Send →", use_container_width=True):
        if user_input:
            send_message(user_input)
            st.rerun()
