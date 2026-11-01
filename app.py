import streamlit as st
import requests
import time
import random

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
    
    /* Hide Streamlit elements */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- AI GENERATION FUNCTION ---
def generate_next_scene(action, current_story, lives):
    # Prompt the AI to act as a ruthless game master
    prompt = f"""
    You are the Game Master of a deadly text adventure game. The player is trapped in a glitchy sci-fi simulation.
    Current Story: {current_story}
    Player Action: {action}
    
    Write the next short paragraph (max 3 sentences) describing what happens. 
    If the player's action is stupid, dangerous, or fails, you MUST start your response with "[DEAD]" and describe their gruesome/funny demise.
    If the player's action is smart, you MUST start your response with "[ALIVE]" and describe their success.
    
    Keep the tone dark, sarcastic, and fast-paced. Do not break character.
    """
    
    try:
        response = requests.get(f"https://text.pollinations.ai/{requests.utils.quote(prompt)}")
        if response.status_code == 200:
            return response.text.strip()
        return "[ALIVE] The simulation stutters. Nothing happens."
    except:
        return "[ALIVE] Network lag. The matrix freezes for a second."

# --- STATE MANAGEMENT ---
if "story" not in st.session_state:
    st.session_state.story = "You wake up in a dark, digital void. A robotic voice echoes: 'PROVE YOUR WORTH OR BE DELETED.' A glowing red laser grid slowly advances toward you."
if "lives" not in st.session_state: st.session_state.lives = 3
if "score" not in st.session_state: st.session_state.score = 0
if "game_over" not in st.session_state: st.session_state.game_over = False

# --- MAIN UI ---
st.markdown("<h1>💀 AI SURVIVAL 💀</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#00ff00;'>ESCAPE THE SIMULATION</p>", unsafe_allow_html=True)

if st.session_state.game_over:
    st.error("SYSTEM TERMINATED. YOU ARE DEAD.")
    st.metric("Final Score", st.session_state.score)
    if st.button("REBOOT SYSTEM"):
        st.session_state.story = "You wake up in a dark, digital void. A robotic voice echoes: 'PROVE YOUR WORTH OR BE DELETED.' A glowing red laser grid slowly advances toward you."
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
    
    # Story Display
    st.markdown(f'<div class="terminal-box">{st.session_state.story}</div>', unsafe_allow_html=True)
    
    # Action Input
    with st.form(key="action_form", clear_on_submit=True):
        action = st.text_input("What do you do?", placeholder="e.g., I dodge to the left...", label_visibility="collapsed")
        submit = st.form_submit_button("EXECUTE ACTION")
        
    if submit and action:
        with st.spinner("Processing reality..."):
            # Get AI response
            result = generate_next_scene(action, st.session_state.story, st.session_state.lives)
            
            # Update Story (Remove the [DEAD]/[ALIVE] tags for display)
            clean_story = result.replace("[DEAD]", "").replace("[ALIVE]", "").strip()
            st.session_state.story = f"> {action}\n\n{clean_story}"
            
            # Check if they died
            if "[DEAD]" in result.upper():
                st.session_state.lives -= 1
                if st.session_state.lives <= 0:
                    st.session_state.game_over = True
            else:
                st.session_state.score += 10
                
            st.rerun()
