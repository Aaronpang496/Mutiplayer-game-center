import streamlit as st
from PIL import Image
import requests
import io
import time
import random
import json

st.set_page_config(page_title="Snap Hunt", page_icon="🎯", layout="centered")

# --- PROFESSIONAL GAME CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&display=swap');
    
    .stApp { background-color: #0a0a0a; color: #ffffff; font-family: 'Rajdhani', sans-serif; }
    h1, h2, h3 { font-family: 'Rajdhani', sans-serif; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; }
    .game-title { color: #00ffcc; text-align: center; font-size: 45px; text-shadow: 0px 0px 15px rgba(0, 255, 204, 0.6); margin-bottom: 0px; }
    .subtitle { color: #888; text-align: center; font-size: 16px; margin-bottom: 30px; letter-spacing: 1px; }
    
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
    
    .target-hud {
        background: linear-gradient(90deg, #001a1a, #000000, #001a1a);
        border-left: 6px solid #00ffcc; border-right: 6px solid #00ffcc;
        padding: 20px; text-align: center; margin-bottom: 20px;
        font-size: 24px; font-weight: 700; color: #ffffff;
        text-shadow: 0px 0px 10px rgba(0, 255, 204, 0.5);
    }
    .target-highlight { color: #00ffcc; font-size: 28px; text-decoration: underline; }
    
    .ai-commentator {
        background: rgba(0, 255, 204, 0.05);
        border: 1px solid #00ffcc; border-radius: 10px;
        padding: 20px; margin-top: 20px;
        font-size: 20px; line-height: 1.5; color: #00ffcc;
        box-shadow: inset 0px 0px 20px rgba(0, 255, 204, 0.1);
    }
    .roast-text { color: #ff0040; }
    .error-text { color: #ffaa00; }
    
    .stButton>button {
        width: 100%; border-radius: 8px; font-weight: 700; font-size: 20px;
        text-transform: uppercase; letter-spacing: 2px;
        background-color: #00ffcc; color: #000000; border: none;
        padding: 15px; transition: all 0.2s;
    }
    .stButton>button:hover { background-color: #ffffff; color: #000000; box-shadow: 0px 0px 20px rgba(255, 255, 255, 0.5); transform: scale(1.02); }
    
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- AI FUNCTIONS ---
def get_ai_comment(image_bytes, target):
    try:
        files = {'image': ('image.jpg', image_bytes, 'image/jpeg')}
        prompt = f"Does this image contain '{target}'? Answer strictly 'CORRECT!' followed by a sarcastic comment, or 'WRONG!' followed by a roast."
        data = {'prompt': prompt}
        response = requests.post("https://vision.pollinations.ai/analyze", files=files, data=data, timeout=25)
        
        if response.status_code == 200:
            result = response.json().get("response", "ERROR")
            if not result or result == "ERROR": return "ERROR"
            return result
        return "ERROR"
    except:
        return "ERROR"

def get_location_targets(location):
    try:
        prompt = f"The user is currently in: {location}. Generate exactly 5 short, funny, and specific scavenger hunt targets they can find in this location. Return ONLY a JSON list of strings. Example: [\"A dusty book\", \"A broken pen\"]."
        response = requests.get(f"https://text.pollinations.ai/{requests.utils.quote(prompt)}")
        if response.status_code == 200:
            raw = response.text.strip()
            if raw.startswith("```json"): raw = raw[7:-3]
            start = raw.find('[')
            end = raw.rfind(']')
            if start != -1 and end != -1: raw = raw[start:end+1]
            targets = json.loads(raw)
            return targets
        return []
    except:
        return []

# --- STATE ---
if "game_state" not in st.session_state: st.session_state.game_state = "location"
if "score" not in st.session_state: st.session_state.score = 0
if "streak" not in st.session_state: st.session_state.streak = 0
if "target" not in st.session_state: st.session_state.target = ""
if "start_time" not in st.session_state: st.session_state.start_time = 0
if "time_limit" not in st.session_state: st.session_state.time_limit = 30
if "judge_result" not in st.session_state: st.session_state.judge_result = ""
if "location_targets" not in st.session_state: st.session_state.location_targets = []
if "camera_key" not in st.session_state: st.session_state.camera_key = 0

# --- MAIN UI ---
st.markdown('<div class="game-title">SNAP HUNT</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI REFEREE // LOCATION MODE</div>', unsafe_allow_html=True)

# LOCATION SCREEN
if st.session_state.game_state == "location":
    st.info("Where are you right now? The AI will generate a custom hunt for your location.")
    location = st.text_input("Enter your location:", placeholder="e.g., My messy bedroom, School library, The kitchen")
    
    st.write("")
    if st.button("🌍 GENERATE HUNT"):
        if location.strip():
            with st.spinner("Scanning location data..."):
                targets = get_location_targets(location)
                if targets:
                    st.session_state.location_targets = targets
                    st.session_state.target = random.choice(targets)
                    st.session_state.time_limit = random.choice([20, 30, 45]) 
                    st.session_state.start_time = time.time()
                    st.session_state.game_state = "playing"
                    st.session_state.judge_result = ""
                    st.rerun()
                else:
                    st.error("AI failed to generate targets. Try again.")

# PLAYING SCREEN
elif st.session_state.game_state == "playing":
    elapsed = time.time() - st.session_state.start_time
    time_left = max(0, st.session_state.time_limit - int(elapsed))
    
    st.markdown(f'<div class="timer-container"><div class="timer-circle">{time_left}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="target-hud">TARGET:<br><span class="target-highlight">{st.session_state.target.upper()}</span></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    col1.metric("SCORE", st.session_state.score)
    col2.metric("STREAK", st.session_state.streak)
    
    if time_left <= 0:
        st.session_state.game_state = "game_over"
        st.rerun()
    
    # --- CAMERA & FLIP BUTTON ---
    st.write("---")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("📸 **CAMERA**")
    with col2:
        # THE FLIP CAMERA BUTTON
        if st.button("FLIP CAMERA"):
            st.session_state.camera_key += 1
            st.rerun()

    camera_image = st.camera_input("Snap target", key=f"cam_{st.session_state.camera_key}", label_visibility="collapsed")
    
    # Upload fallback
    with st.expander("📁 Or upload a photo instead"):
        uploaded_file = st.file_uploader("Upload photo", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            camera_image = uploaded_file
    
    if camera_image:
        with st.spinner("AI ANALYZING..."):
            img = Image.open(camera_image)
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            img_bytes = img_byte_arr.getvalue()
            
            result = get_ai_comment(img_bytes, st.session_state.target)
            st.session_state.judge_result = result
            
            if result == "ERROR":
                st.session_state.game_state = "error"
            elif result.upper().startswith("CORRECT"):
                st.session_state.score += 1
                st.session_state.streak += 1
                st.session_state.game_state = "win"
            else:
                st.session_state.streak = 0
                st.session_state.game_state = "lose"
            st.rerun()

    time.sleep(1)
    st.rerun()

# WIN SCREEN
elif st.session_state.game_state == "win":
    st.success("TARGET VERIFIED")
    st.markdown(f'<div class="ai-commentator">{st.session_state.judge_result}</div>', unsafe_allow_html=True)
    
    st.write("")
    if st.button("NEXT TARGET ➡️"):
        if st.session_state.location_targets:
            remaining = [t for t in st.session_state.location_targets if t != st.session_state.target]
            st.session_state.target = random.choice(remaining) if remaining else random.choice(st.session_state.location_targets)
        st.session_state.time_limit = random.choice([20, 30, 45])
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

# ERROR SCREEN
elif st.session_state.game_state == "error":
    st.warning("⚠️ CONNECTION FAILED")
    st.markdown('<div class="ai-commentator error-text">The AI server timed out. Your streak is safe. Try again!</div>', unsafe_allow_html=True)
    
    st.write("")
    if st.button("TRY PHOTO AGAIN"):
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
        st.session_state.game_state = "location"
        st.session_state.location_targets = []
        st.rerun()
