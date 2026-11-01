import streamlit as st
from PIL import Image
import requests
import io
import time
import random

st.set_page_config(page_title="Snap Hunt", page_icon="🎯", layout="centered")

# --- PROFESSIONAL GAME CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&display=swap');
    
    /* Global Dark Theme */
    .stApp { background-color: #0a0a0a; color: #ffffff; font-family: 'Rajdhani', sans-serif; }
    
    /* Neon Glow Titles */
    h1, h2, h3 { font-family: 'Rajdhani', sans-serif; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; }
    .game-title { color: #00ffcc; text-align: center; font-size: 45px; text-shadow: 0px 0px 15px rgba(0, 255, 204, 0.6); margin-bottom: 0px; }
    .subtitle { color: #888; text-align: center; font-size: 16px; margin-bottom: 30px; letter-spacing: 1px; }
    
    /* The Timer HUD */
    .timer-container { display: flex; justify-content: center; margin-bottom: 20px; }
    .timer-circle {
        width: 120px; height: 120px; border-radius: 50%;
        background: #1a0000; border: 4px solid #ff0000;
        display: flex; align-items: center; justify-content: center;
        font-size: 50px; font-weight: 700; color: #ff0000;
        box-shadow: 0px 0px 30px rgba(255, 0, 0, 0.5);
        animation: pulse 1s infinite alternate;
    }
    @keyframes pulse { 0% { box-shadow: 0px 0px 10px rgba(255, 0, 0, 0.3); } 100% { box-shadow: 0px 0px 40px rgba(255, 0, 0, 0.8); } }
    
    /* Target Card */
    .target-hud {
        background: linear-gradient(90deg, #001a1a, #000000, #001a1a);
        border-left: 6px solid #00ffcc; border-right: 6px solid #00ffcc;
        padding: 20px; text-align: center; margin-bottom: 20px;
        font-size: 24px; font-weight: 700; color: #ffffff;
        text-shadow: 0px 0px 10px rgba(0, 255, 204, 0.5);
    }
    .target-highlight { color: #00ffcc; font-size: 28px; text-decoration: underline; }
    
    /* AI Commentator Box */
    .ai-commentator {
        background: rgba(0, 255, 204, 0.05);
        border: 1px solid #00ffcc; border-radius: 10px;
        padding: 20px; margin-top: 20px;
        font-size: 20px; line-height: 1.5; color: #00ffcc;
        box-shadow: inset 0px 0px 20px rgba(0, 255, 204, 0.1);
    }
    .roast-text { color: #ff0040; }
    
    /* Game Buttons */
    .stButton>button {
        width: 100%; border-radius: 8px; font-weight: 700; font-size: 20px;
        text-transform: uppercase; letter-spacing: 2px;
        background-color: #00ffcc; color: #000000; border: none;
        padding: 15px; transition: all 0.2s;
    }
    .stButton>button:hover { background-color: #ffffff; color: #000000; box-shadow: 0px 0px 20px rgba(255, 255, 255, 0.5); transform: scale(1.02); }
    
    /* Hide Streamlit Header */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- FAST AI VISION ---
def get_ai_comment(image_bytes, target):
    try:
        files = {'image': ('image.jpg', image_bytes, 'image/jpeg')}
        
        prompt = f"""
        You are an aggressive, hilarious AI referee. 
        The user was told to find: '{target}'.
        Look at the attached photo.
        
        If the photo contains the target, start your response with exactly: "CORRECT! "
        If the photo does NOT contain the target, start your response with exactly: "WRONG! "
        
        Follow the prefix with a single, highly dramatic, sarcastic sentence judging what you see.
        """
        
        data = {'prompt': prompt}
        response = requests.post("https://vision.pollinations.ai/analyze", files=files, data=data, timeout=15)
        
        if response.status_code == 200:
            return response.json().get("response", "WRONG! The AI judge is blind.")
        return "WRONG! The AI took a nap."
    except:
        return "WRONG! Connection lost."

# --- TARGET POOL ---
TARGETS = [
    "Something older than you", "Something that makes noise", 
    "Something with a face", "Something shiny", 
    "Something you can drink", "Something red", 
    "Something that fits in your pocket", "A shoe",
    "Something soft", "Something that smells weird"
]

# --- STATE ---
if "game_state" not in st.session_state: st.session_state.game_state = "start"
if "score" not in st.session_state: st.session_state.score = 0
if "streak" not in st.session_state: st.session_state.streak = 0
if "target" not in st.session_state: st.session_state.target = ""
if "start_time" not in st.session_state: st.session_state.start_time = 0
if "time_limit" not in st.session_state: st.session_state.time_limit = 30
if "judge_result" not in st.session_state: st.session_state.judge_result = ""

# --- MAIN UI ---
st.markdown('<div class="game-title">SNAP HUNT</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI REFEREE // 15 SECOND LIMIT</div>', unsafe_allow_html=True)

# START SCREEN
if st.session_state.game_state == "start":
    st.info("The AI will give you a target. You must find it and snap a photo before the timer hits zero. The AI will judge you.")
    st.write("")
    if st.button("🚀 INITIATE MISSION"):
        st.session_state.target = random.choice(TARGETS)
        st.session_state.time_limit = random.choice([15, 20, 30])
        st.session_state.start_time = time.time()
        st.session_state.game_state = "playing"
        st.session_state.judge_result = ""
        st.rerun()

# PLAYING SCREEN
elif st.session_state.game_state == "playing":
    elapsed = time.time() - st.session_state.start_time
    time_left = max(0, st.session_state.time_limit - int(elapsed))
    
    # Timer
    st.markdown(f'<div class="timer-container"><div class="timer-circle">{time_left}</div></div>', unsafe_allow_html=True)
    
    # Target
    st.markdown(f'<div class="target-hud">TARGET ACQUIRED:<br><span class="target-highlight">{st.session_state.target.upper()}</span></div>', unsafe_allow_html=True)
    
    # Stats
    col1, col2 = st.columns(2)
    col1.metric("SCORE", st.session_state.score)
    col2.metric("STREAK", st.session_state.streak)
    
    # Check if time ran out
    if time_left <= 0:
        st.session_state.game_state = "game_over"
        st.rerun()
    
    # Camera
    camera_image = st.camera_input("SNAP TARGET")
    
    if camera_image:
        with st.spinner("AI ANALYZING..."):
            img = Image.open(camera_image)
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            img_bytes = img_byte_arr.getvalue()
            
            result = get_ai_comment(img_bytes, st.session_state.target)
            st.session_state.judge_result = result
            
            if result.upper().startswith("CORRECT"):
                st.session_state.score += 1
                st.session_state.streak += 1
                st.session_state.game_state = "win"
            else:
                st.session_state.streak = 0
                st.session_state.game_state = "lose"
            st.rerun()

    # Force refresh to keep the timer ticking
    time.sleep(1)
    st.rerun()

# WIN SCREEN
elif st.session_state.game_state == "win":
    st.success("TARGET VERIFIED")
    st.markdown(f'<div class="ai-commentator">{st.session_state.judge_result}</div>', unsafe_allow_html=True)
    
    st.write("")
    if st.button("NEXT TARGET ➡️"):
        st.session_state.target = random.choice(TARGETS)
        st.session_state.time_limit = random.choice([15, 20, 30])
        st.session_state.start_time = time.time()
        st.session_state.game_state = "playing"
        st.rerun()

# LOSE SCREEN
elif st.session_state.game_state == "lose":
    st.error("TARGET REJECTED")
    st.markdown(f'<div class="ai-commentator roast-text">{st.session_state.judge_result}</div>', unsafe_allow_html=True)
    
    st.write("")
    if st.button("CONTINUE (TIME STILL RUNNING)"):
        st.session_state.game_state = "playing"
        st.rerun()

# GAME OVER SCREEN
elif st.session_state.game_state == "game_over":
    st.markdown(f'<div class="timer-container"><div class="timer-circle">0</div></div>', unsafe_allow_html=True)
    st.error("MISSION FAILED")
    
    col1, col2 = st.columns(2)
    col1.metric("FINAL SCORE", st.session_state.score)
    col2.metric("BEST STREAK", st.session_state.streak)
    
    st.write("")
    if st.button("RESTART SYSTEM"):
        st.session_state.score = 0
        st.session_state.streak = 0
        st.session_state.game_state = "start"
        st.rerun()
