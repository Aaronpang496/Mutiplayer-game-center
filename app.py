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
    
    .win-box { background-color: #003311; border: 2px solid #00ff00; padding: 20px; text-align: center; font-size: 22px; font-weight: bold; color: #00ff00; text-shadow: 0 0 10px #00ff00; }
    .lose-box { background-color: #330000; border: 2px solid #ff0000; padding: 20px; text-align: center; font-size: 22px; font-weight: bold; color: #ff0000; text-shadow: 0 0 10px #ff0000; }
    
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

VISUALS = ["👾", "🤖", "☠️", "🔥", "🌌", "🚨", "🌀", "👁️", "🧬", "⚡"]

# --- AI GENERATION ---
def generate_starting_scene(difficulty):
    prompt = f"""
    You are a sarcastic AI Game Master. Difficulty is {difficulty}.
    Generate a random starting scenario for a player trapped in your simulation.
    Format EXACTLY:
    [TITLE]: (1-3 words)
    [STATUS]: ALIVE
    [STORY]: (1-2 sentences of danger.)
    """
    for attempt in range(2):
        try:
            response = requests.get(f"https://text.pollinations.ai/{requests.utils.quote(prompt)}", timeout=10)
            if response.status_code == 200 and "[TITLE]" in response.text:
                return response.text.strip()
        except:
            pass
        time.sleep(1)
    return "[TITLE]: SYSTEM FAILURE\n[STATUS]: ALIVE\n[STORY]: A glitchy voice says: 'Survive.'"

def generate_scene(action, current_story, turn, max_turns, lives, inventory, difficulty):
    if turn > max_turns:
        return "[TITLE]: ESCAPE\n[STATUS]: WON\n[STORY]: You override the final firewall. The simulation shatters. You are free."

    ai_behavior = "You are fair but sarcastic." 
    if difficulty == "Easy": ai_behavior = "You are forgiving and give them lots of hints to survive."
    if difficulty == "Hard": ai_behavior = "You are ruthless. You actively try to kill the player unless their action is clever."

    prompt = f"""
    You are an AI Game Master. {ai_behavior}
    Story: {current_story}
    Action: {action}
    Turn: {turn}/{max_turns}
    Inventory: {inventory}
    
    1. Write 1-2 short sentences.
    2. If they succeed, give them an item (e.g., "[Keycard]").
    3. If they do something stupid, put "DEAD" in status.
    4. If they survive, put "ALIVE".
    
    Format EXACTLY:
    [TITLE]: (1-2 words)
    [STATUS]: (ALIVE or DEAD)
    [STORY]: (Outcome)
    """
    
    for attempt in range(2):
        try:
            response = requests.get(f"https://text.pollinations.ai/{requests.utils.quote(prompt)}", timeout=10)
            if response.status_code == 200:
                text = response.text.strip()
                if "[TITLE]" in text and "[STORY]" in text:
                    return text
        except:
            pass
        time.sleep(1)
        
    return "[TITLE]: GLITCH\n[STATUS]: ALIVE\n[STORY]: The system stutters. [Data Shard]"

def parse_ai_response(result):
    title_match = re.search(r"\[TITLE\]:\s*(.*)", result, re.IGNORECASE)
    status_match = re.search(r"\[STATUS\]:\s*(.*)", result, re.IGNORECASE)
    story_match = re.search(r"\[STORY\]:\s*(.*)", result, re.IGNORECASE | re.DOTALL)
    
    title = title_match.group(1).strip() if title_match else "UNKNOWN"
    status = status_match.group(1).strip().upper() if status_match else "ALIVE"
    story = story_match.group(1).strip() if story_match else result
    
    return title, story, status

# --- INITIAL STATE ---
if "game_started" not in st.session_state:
    st.session_state.game_started = False

# --- MAIN UI ---
st.markdown("<h1>⚠️ AI SURVIVAL</h1>", unsafe_allow_html=True)

# START SCREEN
if not st.session_state.game_started:
    st.markdown("<h3 style='text-align:center; color:#fff;'>SELECT DIFFICULTY</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    if col1.button("🟢 EASY\n5 Lives | 20s"):
        st.session_state.difficulty = "Easy"
        st.session_state.lives = 5
        st.session_state.max_turns = 15 
        st.session_state.time_limit = 20
        st.session_state.game_started = True
        st.rerun()
        
    if col2.button("🟡 NORMAL\n3 Lives | 15s"):
        st.session_state.difficulty = "Normal"
        st.session_state.lives = 3
        st.session_state.max_turns = 10
        st.session_state.time_limit = 15
        st.session_state.game_started = True
        st.rerun()
        
    if col3.button("🔴 HARD\n1 Life | 12s"):
        st.session_state.difficulty = "Hard"
        st.session_state.lives = 1
        st.session_state.max_turns = 8
        st.session_state.time_limit = 12
        st.session_state.game_started = True
        st.rerun()

# GAME LOGIC
else:
    if "turn" not in st.session_state:
        st.session_state.turn = 1
        st.session_state.score = 0
        st.session_state.inventory = []
        st.session_state.game_over = False
        st.session_state.game_won = False
        st.session_state.current_visual = random.choice(VISUALS)
        st.session_state.last_action_time = time.time()
        
        with st.spinner("Booting simulation..."):
            raw = generate_starting_scene(st.session_state.difficulty)
            title, story, _ = parse_ai_response(raw)
            st.session_state.title = title
            st.session_state.story = story
            st.session_state.last_action_time = time.time() 

    # WIN SCREEN
    if st.session_state.game_won:
        st.balloons()
        st.markdown(f"<div class='visual-display'>🏆</div>", unsafe_allow_html=True)
        inv_text = ", ".join(st.session_state.inventory) if st.session_state.inventory else "Nothing but your wits"
        st.markdown(f"""
        <div class="win-box">
            SYSTEM ESCAPED ({st.session_state.difficulty} MODE)<br><br>
            You hacked the simulation using: <br>
            <span style="color:#fff;">{inv_text}</span><br><br>
            Final Score: {st.session_state.score}
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        if st.button("🔄 SYSTEM OVERRIDE (PLAY AGAIN)"):
            st.session_state.clear()
            st.rerun()

    # LOSE SCREEN (FRIENDLY ARCADE EDITION)
    elif st.session_state.game_over:
        st.markdown(f"<div class='visual-display'>💥</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="lose-box">
            SYSTEM CRASHED<br><br>
            The AI got tired of your game and kicked you out.<br>
            You survived <b>{st.session_state.turn} turns</b>.<br><br>
            Final Score: {st.session_state.score}
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        if st.button("🔄 REBOOT SIMULATION"):
            st.session_state.clear()
            st.rerun()

    # GAMEPLAY SCREEN
    else:
        time_passed = time.time() - st.session_state.last_action_time
        time_left = max(0, st.session_state.time_limit - int(time_passed))
        
        if time_left == 0:
            st.session_state.lives -= 1
            st.session_state.story = "⚠️ HESITATION DETECTED. The system zapped you for being too slow."
            st.session_state.last_action_time = time.time()
            if st.session_state.lives <= 0:
                st.session_state.game_over = True
            st.rerun()

        inv_text = ", ".join(st.session_state.inventory) if st.session_state.inventory else "Empty"
        st.markdown(f"""
        <div class="status-bar">
            <span>LIVES: {'❤️' * st.session_state.lives}</span>
            <span>TURN: {st.session_state.turn}/{st.session_state.max_turns}</span>
        </div>
        <div class="inventory">🎒 INVENTORY: {inv_text}</div>
        """, unsafe_allow_html=True)
        
        st.markdown(f'<div class="timer-hud">⏱️ ACT FAST: {time_left} SECONDS</div>', unsafe_allow_html=True)
        st.markdown(f"<h2 style='color:#fff; text-shadow: 0 0 10px #ff0040; font-size: 20px;'>{st.session_state.title}</h2>", unsafe_allow_html=True)
        st.markdown(f'<div class="visual-display">{st.session_state.current_visual}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="terminal-box">{st.session_state.story}</div>', unsafe_allow_html=True)
        
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

        if action_taken:
            with st.spinner("Processing..."):
                result = generate_scene(
                    action_taken, 
                    st.session_state.story, 
                    st.session_state.turn, 
                    st.session_state.max_turns,
                    st.session_state.lives, 
                    st.session_state.inventory,
                    st.session_state.difficulty
                )
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
