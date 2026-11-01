import streamlit as st
import requests
import time
import random
import re

st.set_page_config(page_title="AI SURVIVAL", page_icon="⚠️", layout="centered")

# --- ACTION GAME CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
    
    .stApp { background-color: #050505; color: #00ff00; font-family: 'Share Tech Mono', monospace; }
    h1, h2, h3 { color: #ff0040; text-transform: uppercase; text-align: center; text-shadow: 0 0 10px #ff0040; }
    
    .terminal-box {
        background-color: #0a0a0a;
        border: 1px solid #ff0040;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 0 15px rgba(255, 0, 64, 0.2);
        margin-bottom: 15px;
        font-size: 16px;
        line-height: 1.4;
    }
    
    .visual-display {
        text-align: center; font-size: 100px; margin: 20px 0;
        animation: glitch 1s linear infinite;
    }
    
    @keyframes glitch {
        2%, 64% { transform: translate(2px,0) skew(0deg); }
        4%, 60% { transform: translate(-2px,0) skew(0deg); }
        62% { transform: translate(0,0) skew(5deg); }
    }
    
    .timer-hud {
        background-color: #111; border: 2px solid #00ffcc; padding: 10px;
        text-align: center; font-size: 20px; font-weight: bold; color: #00ffcc;
        margin-bottom: 15px; box-shadow: 0 0 15px rgba(0, 255, 204, 0.3);
    }
    
    .status-bar { display: flex; justify-content: space-between; font-weight: bold; font-size: 18px; margin-bottom: 10px; color: #fff;}
    .inventory { color: #00ffff; font-size: 14px; margin-bottom: 10px; }
    
    .stButton>button {
        background-color: #111; color: #fff; border: 1px solid #444; font-family: 'Share Tech Mono', monospace; font-weight: bold; font-size: 16px; width: 100%; border-radius: 0; padding: 15px;
    }
    .stButton>button:hover { background-color: #ff0040; color: #fff; border-color: #ff0040; box-shadow: 0 0 15px #ff0040; }
    
    /* Win / Lose Screen Styles */
    .win-box { background-color: #003311; border: 2px solid #00ff00; padding: 20px; text-align: center; font-size: 22px; font-weight: bold; color: #00ff00; text-shadow: 0 0 10px #00ff00; }
    .lose-box { background-color: #330000; border: 2px solid #ff0000; padding: 20px; text-align: center; font-size: 22px; font-weight: bold; color: #ff0000; text-shadow: 0 0 10px #ff0000; }
    
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

VISUALS = ["👾", "🤖", "☠️", "🔥", "🌌", "🚨", "🌀", "👁️", "🧬", "⚡"]

# --- AI GENERATION ---
def generate_scene(action, current_story, turn, lives, inventory):
    if turn > 5:
        return "[TITLE]: ESCAPE\n[STATUS]: WON\n[STORY]: You override the final firewall. The simulation shatters. You are free."

    prompt = f"""
    You are a hostile, sarcastic AI Game Master. The player is trapped in your simulation.
    Story so far: {current_story}
    Player Action: {action}
    Turn: {turn}/5
    Player Inventory: {inventory}
    
    RULES:
    1. Write 1-2 short, punchy sentences describing what happens.
    2. If they succeed, give them an item for their inventory (e.g., "You find a [Keycard]").
    3. If they do something stupid, put "DEAD" in the status.
    4. If they survive, put "ALIVE".
    
    Reply in EXACTLY this format:
    [TITLE]: (1-2 word dramatic title)
    [STATUS]: (ALIVE or DEAD)
    [STORY]: (The outcome)
    """
    try:
        response = requests.get(f"https://text.pollinations.ai/{requests.utils.quote(prompt)}")
        return response.text.strip()
    except:
        return "[TITLE]: GLITCH\n[STATUS]: ALIVE\n[STORY]: The simulation freezes."

def parse_ai_response(result):
    title_match = re.search(r"\[TITLE\]:\s*(.*)", result, re.IGNORECASE)
    status_match = re.search(r"\[STATUS\]:\s*(.*)", result, re.IGNORECASE)
    story_match = re.search(r"\[STORY\]:\s*(.*)", result, re.IGNORECASE | re.DOTALL)
    
    return (
        title_match.group(1).strip() if title_match else "UNKNOWN",
        story_match.group(1).strip() if story_match else result,
        status_match.group(1).strip().upper() if status_match else "ALIVE"
    )

# --- STATE ---
if "lives" not in st.session_state: st.session_state.lives = 3
if "turn" not in st.session_state: st.session_state.turn = 1
if "score" not in st.session_state: st.session_state.score = 0
if "inventory" not in st.session_state: st.session_state.inventory = []
if "game_over" not in st.session_state: st.session_state.game_over = False
if "game_won" not in st.session_state: st.session_state.game_won = False
if "current_visual" not in st.session_state: st.session_state.current_visual = "⚠️"
if "story" not in st.session_state: st.session_state.story = "You wake up on a digital dissection table. A laser is moving toward your chest. You have 5 turns to escape before the simulation deletes you."
if "title" not in st.session_state: st.session_state.title = "THE AWAKENING"
if "last_action_time" not in st.session_state: st.session_state.last_action_time = time.time()

# --- MAIN UI ---
st.markdown("<h1>⚠️ AI SURVIVAL</h1>", unsafe_allow_html=True)

# ==========================================
# WIN SCREEN (CELEBRATION)
# ==========================================
if st.session_state.game_won:
    st.balloons() # Explodes balloons on the screen
    st.markdown(f"<div class='visual-display'>🏆</div>", unsafe_allow_html=True)
    
    inv_text = ", ".join(st.session_state.inventory) if st.session_state.inventory else "Nothing but your wits"
    
    st.markdown(f"""
    <div class="win-box">
        SYSTEM ESCAPED<br><br>
        You hacked the simulation using: <br>
        <span style="color:#fff;">{inv_text}</span><br><br>
        Final Score: {st.session_state.score}
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    if st.button("🔄 SYSTEM OVERRIDE (PLAY AGAIN)"):
        st.session_state.clear()
        st.rerun()

# ==========================================
# LOSE SCREEN (DESTRUCTION)
# ==========================================
elif st.session_state.game_over:
    st.markdown(f"<div class='visual-display'>☠️</div>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="lose-box">
        SYSTEM TERMINATED<br><br>
        Your digital remains have been deleted.<br>
        Final Score: {st.session_state.score}
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    if st.button("🔄 SYSTEM OVERRIDE (TRY AGAIN)"):
        st.session_state.clear()
        st.rerun()

# ==========================================
# GAMEPLAY SCREEN
# ==========================================
else:
    # TIMER CALCULATION
    time_passed = time.time() - st.session_state.last_action_time
    time_left = max(0, 15 - int(time_passed))
    
    if time_left == 0:
        st.session_state.lives -= 1
        st.session_state.story = "⚠️ HESITATION DETECTED. The system zapped you for being too slow."
        st.session_state.last_action_time = time.time()
        if st.session_state.lives <= 0:
            st.session_state.game_over = True
        st.rerun()

    # Status UI
    inv_text = ", ".join(st.session_state.inventory) if st.session_state.inventory else "Empty"
    st.markdown(f"""
    <div class="status-bar">
        <span>LIVES: {'❤️' * st.session_state.lives}</span>
        <span>TURN: {st.session_state.turn}/5</span>
    </div>
    <div class="inventory">🎒 INVENTORY: {inv_text}</div>
    """, unsafe_allow_html=True)
    
    # THE VISIBLE TIMER
    st.markdown(f'<div class="timer-hud">⏱️ ACT FAST: {time_left} SECONDS</div>', unsafe_allow_html=True)
    
    st.markdown(f"<h2 style='color:#fff; text-shadow: 0 0 10px #ff0040; font-size: 20px;'>{st.session_state.title}</h2>", unsafe_allow_html=True)
    st.markdown(f'<div class="visual-display">{st.session_state.current_visual}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="terminal-box">{st.session_state.story}</div>', unsafe_allow_html=True)
    
    # --- ACTION BUTTONS ---
    st.write("CHOOSE YOUR ACTION:")
    col1, col2, col3 = st.columns(3)
    
    action_taken = None
    if col1.button("⚔️ FIGHT"):
        action_taken = "I attack the threat with my bare hands."
    if col2.button("💻 HACK"):
        action_taken = "I try to hack into the nearest terminal."
    if col3.button("🏃 RUN"):
        action_taken = "I sprint away as fast as I can."
        
    with st.form(key="custom_action", clear_on_submit=True):
        custom = st.text_input("Or type a custom action:", placeholder="e.g., I look under the table...", label_visibility="collapsed")
        submit_custom = st.form_submit_button("EXECUTE")
        if submit_custom and custom:
            action_taken = custom

    # Process Action
    if action_taken:
        with st.spinner("Processing..."):
            result = generate_scene(action_taken, st.session_state.story, st.session_state.turn, st.session_state.lives, st.session_state.inventory)
            title, story, status = parse_ai_response(result)
            
            st.session_state.current_visual = random.choice(VISUALS)
            st.session_state.title = title
            st.session_state.story = f"> {action_taken}\n\n{story}"
            st.session_state.last_action_time = time.time() 
            
            items = re.findall(r"\[(.*?)\]", story)
            for item in items:
                if item.lower() not in ["alive", "dead", "won"] and item not in st.session_state.inventory:
                    st.session_state.inventory.append(item)
            
            if status == "WON":
                st.session_state.game_won = True
            elif status == "DEAD":
                st.session_state.lives -= 1
                if st.session_state.lives <= 0:
                    st.session_state.game_over = True
            else:
                st.session_state.score += 10
                st.session_state.turn += 1
                
            st.rerun()
