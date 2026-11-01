import streamlit as st
import requests
import time
import random
import re

st.set_page_config(page_title="AI Survival", page_icon="💀", layout="centered")

# --- CYBERPUNK TERMINAL CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
    
    .stApp { background-color: #000000; color: #00ff00; font-family: 'Share Tech Mono', monospace; }
    
    h1, h2, h3 { color: #00ff00; text-transform: uppercase; text-align: center; text-shadow: 0 0 10px #00ff00; }
    
    .terminal-box {
        background-color: #050505;
        border: 2px solid #00ff00;
        padding: 20px;
        border-radius: 5px;
        box-shadow: 0 0 15px rgba(0, 255, 0, 0.2);
        margin-bottom: 20px;
        font-size: 18px;
        line-height: 1.6;
    }
    
    .ascii-art {
        text-align: center;
        color: #00ffff;
        font-family: monospace;
        white-space: pre;
        font-size: 14px;
        margin: 20px 0;
        text-shadow: 0 0 10px #00ffff;
    }
    
    .status-bar { display: flex; justify-content: space-between; font-weight: bold; font-size: 20px; margin-bottom: 10px; }
    .lives { color: #ff0000; text-shadow: 0 0 10px #ff0000; }
    .score { color: #00ffff; text-shadow: 0 0 10px #00ffff; }
    
    .stTextInput>div>div>input {
        background-color: #000000; color: #00ff00; border: 1px solid #00ff00; font-family: 'Share Tech Mono', monospace; font-size: 18px;
    }
    
    .stButton>button {
        background-color: #000000; color: #00ff00; border: 2px solid #00ff00; font-family: 'Share Tech Mono', monospace; font-weight: bold; font-size: 18px; width: 100%; transition: all 0.2s;
    }
    .stButton>button:hover { background-color: #00ff00; color: #000000; box-shadow: 0 0 20px #00ff00; }
    
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- ASCII VISUALS ---
ASCII_ART = [
    """\n      _____\n     /     \\\n    | () () |\n     \\  ^  /\n      |||||\n      |||||\n    [DEATH]\n""",
    """\n       [O]\n      /|_|\\\n      [___]\n      /   \\\n     /_____\\\n    [ROGUE AI]\n""",
    """\n      /\\\n     /  \\\n    /    \\\n   /______\\\n      ||\n      ||\n    [THE VOID]\n""",
    """\n    █▀▀ █░░ █ ▀█▀ █▀▀ █░█\n    █▄█ █▄▄ █ ░█░ █▄▄ █▀█\n    [SYSTEM CORRUPTED]\n""",
    """\n     .-\"\"\"-.\n    /       \\\n    \\       /\n     `-...-' \n    [ALIEN ENTITY]\n""",
    """\n      |\\\n      | \\\n      |  \\\n      |  /\n      | /\n      |/\n    [PORTAL]\n"""
]

# --- AI GENERATION FUNCTIONS ---
def get_starting_scene():
    prompt = """
    You are the Game Master of a deadly text adventure game. The player is trapped in a glitchy, chaotic sci-fi simulation.
    Generate a random, crazy starting scenario. 
    You must reply in EXACTLY this format:
    [TITLE]: (A short 1-3 word dramatic title, like "THE AWAKENING" or "GRAVITY FAILURE")
    [STATUS]: ALIVE
    [STORY]: (Write a short paragraph, max 3 sentences, describing where they are and the immediate danger.)
    """
    try:
        response = requests.get(f"https://text.pollinations.ai/{requests.utils.quote(prompt)}")
        return response.text.strip()
    except:
        return "[TITLE]: ERROR\n[STATUS]: ALIVE\n[STORY]: The simulation stutters."

def generate_next_scene(action, current_story):
    prompt = f"""
    You are the Game Master of a deadly text adventure game. The player is trapped in a glitchy sci-fi simulation.
    Current Story: {current_story}
    Player Action: {action}
    
    You must reply in EXACTLY this format:
    [TITLE]: (A short 1-3 word dramatic title for this new scene)
    [STATUS]: (Write strictly "ALIVE" if they survive, or "DEAD" if they fail/die)
    [STORY]: (Write a short paragraph, max 3 sentences, describing what happens next. Be dark, sarcastic, and fast-paced.)
    """
    try:
        response = requests.get(f"https://text.pollinations.ai/{requests.utils.quote(prompt)}")
        return response.text.strip()
    except:
        return "[TITLE]: ERROR\n[STATUS]: ALIVE\n[STORY]: The simulation stutters."

def parse_ai_response(result):
    title_match = re.search(r"\[TITLE\]:\s*(.*)", result, re.IGNORECASE)
    status_match = re.search(r"\[STATUS\]:\s*(.*)", result, re.IGNORECASE)
    story_match = re.search(r"\[STORY\]:\s*(.*)", result, re.IGNORECASE | re.DOTALL)
    
    title = title_match.group(1).strip() if title_match else "UNKNOWN SECTOR"
    is_dead = "DEAD" in status_match.group(1).upper() if status_match else False
    story = story_match.group(1).strip() if story_match else result
    
    return title, story, is_dead

# --- STATE MANAGEMENT ---
if "lives" not in st.session_state: st.session_state.lives = 3
if "score" not in st.session_state: st.session_state.score = 0
if "game_over" not in st.session_state: st.session_state.game_over = False
if "initialized" not in st.session_state: st.session_state.initialized = False

# Start game for the first time
if not st.session_state.initialized:
    with st.spinner("Booting simulation..."):
        raw = get_starting_scene()
        title, story, _ = parse_ai_response(raw)
        st.session_state.title = title
        st.session_state.story = story
        st.session_state.initialized = True

# --- MAIN UI ---
st.markdown("<h1>💀 AI SURVIVAL 💀</h1>", unsafe_allow_html=True)

if st.session_state.game_over:
    st.markdown(f"<h2 style='color:red; text-align:center;'>{st.session_state.title}</h2>", unsafe_allow_html=True)
    st.markdown(f'<div class="ascii-art" style="color:#ff0000; text-shadow: 0 0 10px #ff0000;">{ASCII_ART[0]}</div>', unsafe_allow_html=True)
    st.error("SYSTEM TERMINATED. YOU ARE DEAD.")
    st.metric("Final Score", st.session_state.score)
    if st.button("REBOOT SYSTEM"):
        with st.spinner("Rebooting..."):
            raw = get_starting_scene()
            title, story, _ = parse_ai_response(raw)
            st.session_state.title = title
            st.session_state.story = story
            st.session_state.lives = 3
            st.session_state.score = 0
            st.session_state.game_over = False
            st.rerun()
else:
    # Status Bar
    st.markdown(f"""
    <div class="status-bar">
        <span class="lives">LIVES: {'❤️' * st.session_state.lives}</span>
        <span class="score">SCORE: {st.session_state.score}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Dynamic Title
    st.markdown(f"<h2 style='color:#00ffff; text-shadow: 0 0 10px #00ffff;'>{st.session_state.title}</h2>", unsafe_allow_html=True)
    
    # Randomized Visuals (Picks a new graphic every rerun)
    if "current_visual" not in st.session_state:
        st.session_state.current_visual = random.choice(ASCII_ART)
        
    st.markdown(f'<div class="ascii-art">{st.session_state.current_visual}</div>', unsafe_allow_html=True)
    
    # Story Display
    st.markdown(f'<div class="terminal-box">{st.session_state.story}</div>', unsafe_allow_html=True)
    
    # Action Input
    with st.form(key="action_form", clear_on_submit=True):
        action = st.text_input("What do you do?", placeholder="e.g., I dodge to the left...", label_visibility="collapsed")
        submit = st.form_submit_button("EXECUTE ACTION")
        
    if submit and action:
        with st.spinner("Processing reality..."):
            # Get AI response
            result = generate_next_scene(action, st.session_state.story)
            title, story, is_dead = parse_ai_response(result)
            
            # Update state
            st.session_state.title = title
            st.session_state.story = f"> {action}\n\n{story}"
            st.session_state.current_visual = random.choice(ASCII_ART) # Randomize visual on every turn
            
            if is_dead:
                st.session_state.lives -= 1
                if st.session_state.lives <= 0:
                    st.session_state.game_over = True
            else:
                st.session_state.score += 10
                
            st.rerun()
