import streamlit as st
import requests
import time
import random
import re

st.set_page_config(page_title="AI SURVIVAL", page_icon="⚠️", layout="centered")

# --- CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
    
    .stApp { background-color: #050505; color: #00ff00; font-family: 'Share Tech Mono', monospace; }
    h1, h2, h3 { color: #ff0040; text-transform: uppercase; text-align: center; text-shadow: 0 0 10px #ff0040; }
    
    .terminal-box {
        background-color: #0a0a0a; border: 1px solid #ff0040; padding: 15px; border-radius: 5px;
        box-shadow: 0 0 15px rgba(255, 0, 64, 0.2); margin-bottom: 15px; font-size: 16px; line-height: 1.4;
    }
    
    .visual-display { text-align: center; font-size: 100px; margin: 20px 0; animation: glitch 1s linear infinite; }
    @keyframes glitch {
        2%, 64% { transform: translate(2px,0) skew(0deg); }
        4%, 60% { transform: translate(-2px,0) skew(0deg); }
        62% { transform: translate(0,0) skew(5deg); }
    }
    
    .timer-hud {
        background-color: #111; border: 2px solid #00ffcc; padding: 10px; text-align: center; 
        font-size: 20px; font-weight: bold; color: #00ffcc; margin-bottom: 15px; box-shadow: 0 0 15px rgba(0, 255, 204, 0.3);
    }
    
    .status-bar { display: flex; justify-content: space-between; font-weight: bold; font-size: 18px; margin-bottom: 10px; color: #fff;}
    .inventory { color: #00ffff; font-size: 14px; margin-bottom: 10px; }
    
    .stButton>button {
        background-color: #111; color: #fff; border: 1px solid #444; font-family: 'Share Tech Mono', monospace; 
        font-weight: bold; font-size: 16px; width: 100%; border-radius: 0; padding: 15px; margin-bottom: 10px;
    }
    .stButton>button:hover { background-color: #ff0040; color: #fff; border-color: #ff0040; box-shadow: 0 0 15px #ff0040; }
    
    .win-certificate {
        background: linear-gradient(135deg, #001a00, #003311, #001a00); border: 4px solid #00ff00;
        padding: 40px 20px; text-align: center; border-radius: 10px;
        box-shadow: 0 0 40px rgba(0, 255, 0, 0.6), inset 0 0 20px rgba(0, 255, 0, 0.2);
        animation: pulse-win 2s infinite alternate;
    }
    @keyframes pulse-win { 0% { box-shadow: 0 0 20px rgba(0, 255, 0, 0.4); } 100% { box-shadow: 0 0 60px rgba(0, 255, 0, 0.8); } }
    .win-title { font-size: 40px; color: #00ff00; text-shadow: 0 0 20px #00ff00; margin-bottom: 10px; font-weight: 900; }
    .win-stats { font-size: 24px; color: #00ffff; font-weight: bold; margin: 15px 0; }

    .lose-box { background-color: #330000; border: 2px solid #ff0000; padding: 20px; text-align: center; font-size: 22px; font-weight: bold; color: #ff0000; text-shadow: 0 0 10px #ff0000; }
    
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

WIN_AUDIO = """<audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2013/2013-preview.mp3" type="audio/mpeg"></audio>"""
VISUALS = ["👾", "🤖", "☠️", "🔥", "🌌", "🚨", "🌀", "👁️", "🧬", "⚡"]

# --- LOCAL FALLBACK ENGINE ---
SCENARIOS = {
    "start": [
        ("THE AWAKENING", "You wake up on a digital dissection table. A laser is moving toward your chest."),
        ("GRAVITY FAILURE", "The simulation glitches. Gravity turns sideways. You are sliding toward a pit."),
        ("ROGUE TOASTER", "You are trapped in a kitchen, but the toaster is armed with a plasma cannon.")
    ],
    "FIGHT": [
        ("COMBAT", "You swing your fist. You find a [Brass Knuckles]."),
        ("COMBAT", "You attack the threat. It shatters, revealing a [Keycard]."),
        ("DANGER", "You punch the air. The simulation laughs. The floor starts to crumble."),
        ("DEAD", "You try to fight a laser beam. You are instantly vaporized.")
    ],
    "HACK": [
        ("HACKED", "You type furiously. The system opens a door. You grab a [Data Chip]."),
        ("HACKED", "You bypass the firewall. A [Medkit] appears."),
        ("DANGER", "Your hack fails. An alarm blares. Security drones are converging."),
        ("DEAD", "The system reverse-hacks your brain and deletes your consciousness.")
    ],
    "RUN": [
        ("ESCAPE", "You sprint away. You find a [Running Shoes]."),
        ("ESCAPE", "You run into a dark corridor. You trip over a [Metal Pipe] but hide."),
        ("DANGER", "You run, but the corridor loops back. You are trapped."),
        ("DEAD", "You run blindly off a cliff.")
    ],
    "CUSTOM": [
        ("MYSTERY", "You do something unexpected. A hidden panel opens, revealing a [Strange Coin]."),
        ("MYSTERY", "The system is confused. It glitches, and you slip through a crack."),
        ("DANGER", "You try to be clever. The temperature drops rapidly."),
        ("DEAD", "You do something incredibly stupid. The simulation deletes you.")
    ]
}

def get_local_scenario(action_type, turn, max_turns):
    if turn > max_turns:
        return "ESCAPE", "You override the final firewall. You are free."
    title, story = random.choice(SCENARIOS[action_type])
    if title == "DEAD" and random.random() > 0.15: 
        title, story = random.choice(SCENARIOS["RUN"]) 
    return title, story

# --- HYBRID AI ENGINE (API + LOCAL) ---
def generate_scene_hybrid(action_type, action_text, current_story, turn, max_turns, inventory, difficulty):
    if turn > max_turns:
        return "ESCAPE", "You override the final firewall. You are free.", "WON"
        
    ai_behavior = "Fair but sarcastic."
    if difficulty == "Easy": ai_behavior = "Forgiving, gives hints."
    if difficulty == "Hard": ai_behavior = "Ruthless. Tries to kill."
    
    prompt = f"AI Game Master. {ai_behavior}\nStory: {current_story}\nAction: {action_text}\nTurn: {turn}/{max_turns}\nInv: {inventory}\n1. 1-2 sentences.\n2. Give item if succeed (e.g., \"[Keycard]\").\n3. If stupid action, put \"DEAD\".\n4. Else \"ALIVE\".\nFormat EXACTLY:\n[TITLE]: (1-2 words)\n[STATUS]: ALIVE/DEAD\n[STORY]: (Outcome)"

    try:
        response = requests.get(f"https://text.pollinations.ai/{requests.utils.quote(prompt)}", timeout=8)
        if response.status_code == 200 and "[TITLE]" in response.text:
            text = response.text.strip()
            t = re.search(r"\[TITLE\]:\s*(.*)", text, re.IGNORECASE)
            s = re.search(r"\[STATUS\]:\s*(.*)", text, re.IGNORECASE)
            st_match = re.search(r"\[STORY\]:\s*(.*)", text, re.IGNORECASE | re.DOTALL)
            if t and s and st_match:
                return t.group(1).strip(), st_match.group(1).strip(), s.group(1).strip().upper()
    except:
        pass 
        
    title, story = get_local_scenario(action_type, turn, max_turns)
    status = "DEAD" if title == "DEAD" else ("WON" if title == "ESCAPE" else "ALIVE")
    return title, story, status

# --- INITIAL STATE ---
if "credits" not in st.session_state: st.session_state.credits = 0
if "upgrades" not in st.session_state: st.session_state.upgrades = []
if "screen" not in st.session_state: st.session_state.screen = "menu" # menu, shop, game

# --- MAIN UI ---
st.markdown("<h1>⚠️ AI SURVIVAL</h1>", unsafe_allow_html=True)

# ==========================================
# MAIN MENU
# ==========================================
if st.session_state.screen == "menu":
    st.markdown(f"<h3 style='text-align:center; color:#ffd700;'>💰 CREDITS: {st.session_state.credits}</h3>", unsafe_allow_html=True)
    st.write(f"**Owned Upgrades:** {', '.join(st.session_state.upgrades) if st.session_state.upgrades else 'None'}")
    
    if st.button("🛒 ENTER BLACK MARKET"):
        st.session_state.screen = "shop"
        st.rerun()
        
    st.divider()
    st.markdown("<h3 style='text-align:center; color:#fff;'>SELECT DIFFICULTY</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    if col1.button("🟢 EASY\n5 Lives | 20s"):
        st.session_state.difficulty = "Easy"
        st.session_state.base_lives = 5
        st.session_state.max_turns = 15 
        st.session_state.base_time = 20
        st.session_state.screen = "game"
        st.rerun()
    if col2.button("🟡 NORMAL\n3 Lives | 15s"):
        st.session_state.difficulty = "Normal"
        st.session_state.base_lives = 3
        st.session_state.max_turns = 10
        st.session_state.base_time = 15
        st.session_state.screen = "game"
        st.rerun()
    if col3.button("🔴 HARD\n1 Life | 12s"):
        st.session_state.difficulty = "Hard"
        st.session_state.base_lives = 1
        st.session_state.max_turns = 8
        st.session_state.base_time = 12
        st.session_state.screen = "game"
        st.rerun()

# ==========================================
# SHOP SCREEN
# ==========================================
elif st.session_state.screen == "shop":
    st.markdown(f"<h2 style='text-align:center; color:#00ffff;'>🛒 BLACK MARKET</h2>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align:center; color:#ffd700;'>💰 CREDITS: {st.session_state.credits}</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💣 EMP Grenade (80 💰)\nSave from 1 death"):
            if st.session_state.credits >= 80 and "EMP" not in st.session_state.upgrades:
                st.session_state.credits -= 80
                st.session_state.upgrades.append("EMP")
                st.rerun()
        if st.button("🥽 X-Ray Goggles (60 💰)\nReveals a safe hint"):
            if st.session_state.credits >= 60 and "Goggles" not in st.session_state.upgrades:
                st.session_state.credits -= 60
                st.session_state.upgrades.append("Goggles")
                st.rerun()
    with col2:
        if st.button("🔫 Plasma Pistol (120 💰)\nGuarantees survival on FIGHT"):
            if st.session_state.credits >= 120 and "Plasma" not in st.session_state.upgrades:
                st.session_state.credits -= 120
                st.session_state.upgrades.append("Plasma")
                st.rerun()
        if st.button("☕ Overclock (100 💰)\nEarn 2x Credits"):
            if st.session_state.credits >= 100 and "Overclock" not in st.session_state.upgrades:
                st.session_state.credits -= 100
                st.session_state.upgrades.append("Overclock")
                st.rerun()
                
    st.info(f"**Owned Upgrades:** {', '.join(st.session_state.upgrades) if st.session_state.upgrades else 'None'}")
    
    if st.button("🔙 BACK TO MAIN MENU", type="primary"):
        st.session_state.screen = "menu"
        st.rerun()

# ==========================================
# GAME LOGIC
# ==========================================
elif st.session_state.screen == "game":
    if "turn" not in st.session_state:
        st.session_state.lives = st.session_state.base_lives
        st.session_state.time_limit = st.session_state.base_time
        st.session_state.turn = 1
        st.session_state.score = 0
        st.session_state.inventory = []
        st.session_state.used_emp = False
        st.session_state.current_visual = random.choice(VISUALS)
        st.session_state.last_action_time = time.time()
        
        title, story = get_local_scenario("start", 1, st.session_state.max_turns)
        st.session_state.title = title
        st.session_state.story = story
        st.session_state.last_action_time = time.time() 

    if st.session_state.get("game_won"):
        st.balloons()
        st.markdown(WIN_AUDIO, unsafe_allow_html=True)
        st.markdown(f"<div class='visual-display'>👑</div>", unsafe_allow_html=True)
        
        multiplier = 2 if "Overclock" in st.session_state.upgrades else 1
        earned_credits = (st.session_state.score // 2) * multiplier
        st.session_state.credits += earned_credits
        
        st.markdown(f"""
        <div class="win-certificate">
            <div class="win-title">SYSTEM ESCAPED</div>
            <div class="win-stats">
                DIFFICULTY: {st.session_state.difficulty.upper()}<br>
                SCORE: {st.session_state.score}<br>
                <span style="color:#ffd700;">EARNED: 💰 {earned_credits} Credits</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        if st.button("🛒 GO TO SHOP"):
            keys_to_keep = ["credits", "upgrades", "screen"]
            for key in list(st.session_state.keys()):
                if key not in keys_to_keep: del st.session_state[key]
            st.session_state.screen = "menu"
            st.rerun()

    elif st.session_state.get("game_over"):
        st.markdown(f"<div class='visual-display'>💥</div>", unsafe_allow_html=True)
        multiplier = 2 if "Overclock" in st.session_state.upgrades else 1
        earned_credits = (st.session_state.score // 2) * multiplier
        st.session_state.credits += earned_credits
        
        st.markdown(f"""
        <div class="lose-box">
            SYSTEM CRASHED<br><br>
            You survived {st.session_state.turn} turns.<br>
            <span style="color:#ffd700;">EARNED: 💰 {earned_credits} Credits</span>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        if st.button("🛒 GO TO SHOP"):
            keys_to_keep = ["credits", "upgrades", "screen"]
            for key in list(st.session_state.keys()):
                if key not in keys_to_keep: del st.session_state[key]
            st.session_state.screen = "menu"
            st.rerun()

    else:
        time_passed = time.time() - st.session_state.last_action_time
        time_left = max(0, st.session_state.time_limit - int(time_passed))
        
        if time_left == 0:
            st.session_state.lives -= 1
            st.session_state.story = "⚠️ HESITATION DETECTED. The system zapped you."
            st.session_state.last_action_time = time.time()
            if st.session_state.lives <= 0: st.session_state.game_over = True
            st.rerun()

        if "Goggles" in st.session_state.upgrades:
            st.markdown("<div style='text-align:center; color:#ffd700; font-weight:bold;'>🥽 X-RAY SCAN: Threat Level is HIGH. Try running or hacking.</div>", unsafe_allow_html=True)

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
        
        action_taken, action_type = None, None
        if col1.button("⚔️ FIGHT"): action_taken, action_type = "I attack with my bare hands.", "FIGHT"
        if col2.button("💻 HACK"): action_taken, action_type = "I try to hack the terminal.", "HACK"
        if col3.button("🏃 RUN"): action_taken, action_type = "I sprint away.", "RUN"
            
        with st.form(key="custom_action", clear_on_submit=True):
            custom = st.text_input("Or type a custom action:", placeholder="e.g., I look under the table...", label_visibility="collapsed")
            submit_custom = st.form_submit_button("EXECUTE")
            if submit_custom and custom: 
                action_taken, action_type = custom, "CUSTOM"

        if action_taken:
            with st.spinner("Processing..."):
                if action_type == "FIGHT" and "Plasma" in st.session_state.upgrades:
                    title, story, status = "OBLITERATED", "You pull out the Plasma Pistol and vaporize the threat. [Plasma Cell]", "ALIVE"
                else:
                    title, story, status = generate_scene_hybrid(action_type, action_taken, st.session_state.story, st.session_state.turn, st.session_state.max_turns, st.session_state.inventory, st.session_state.difficulty)
                
                st.session_state.current_visual = random.choice(VISUALS)
                st.session_state.title = title
                st.session_state.story = f"> {action_taken}\n\n{story}"
                st.session_state.last_action_time = time.time() 
                
                items = re.findall(r"\[(.*?)\]", story)
                for item in items:
                    if item.lower() not in ["alive", "dead", "won"] and item not in st.session_state.inventory:
                        st.session_state.inventory.append(item)
                
                if status == "WON" or title == "ESCAPE":
                    st.session_state.game_won = True
                elif status == "DEAD" or title == "DEAD":
                    if "EMP" in st.session_state.upgrades and not st.session_state.used_emp:
                        st.session_state.used_emp = True
                        st.session_state.story = "💣 EMP GRENADE ACTIVATED! The threat is destroyed, but you survive."
                        st.session_state.turn += 1
                    else:
                        st.session_state.lives -= 1
                        if st.session_state.lives <= 0: st.session_state.game_over = True
                else:
                    st.session_state.score += 10
                    st.session_state.turn += 1
                    
                st.rerun()
