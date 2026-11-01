import streamlit as st
from PIL import Image
import requests
import io
import time
import random

st.set_page_config(page_title="Project: Bounty", page_icon="🎯", layout="centered")

# --- HIGH-ACTION CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Black+Ops+One&family=Nunito:wght@400;700;900&display=swap');
    
    h1, h2, h3 { font-family: 'Black Ops One', cursive; letter-spacing: 1px; text-transform: uppercase; }
    html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }
    
    @keyframes flash { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    .timer-box { background: #ff0000; color: white; padding: 20px; text-align: center; border-radius: 15px; font-size: 60px; font-weight: 900; animation: flash 1s infinite; margin-bottom: 20px;}
    
    .target-card { background: #111; color: #00ffcc; padding: 30px; text-align: center; border-radius: 15px; border: 4px dashed #00ffcc; font-size: 30px; font-weight: 900; margin-bottom: 20px; }
    
    .commentator-box { background: #222; border-left: 10px solid #ff0040; padding: 20px; font-size: 22px; font-style: italic; color: #fff; margin-top: 20px; border-radius: 5px; }
    
    .stButton>button { border-radius: 10px; font-weight: 900; font-size: 20px; border: 3px solid #000; box-shadow: 4px 4px 0 #000; transition: all 0.1s; }
    .stButton>button:hover { transform: translate(2px, 2px); box-shadow: 2px 2px 0 #000; background-color: #00ffcc; color: black; }
</style>
""", unsafe_allow_html=True)

# --- AI COMMENTATOR ---
def get_ai_comment(image_bytes, target):
    try:
        files = {'image': ('image.jpg', image_bytes, 'image/jpeg')}
        
        # The prompt tells the AI to act like an aggressive, funny commentator
        prompt = f"""
        You are an aggressive, hilarious sports commentator and AI referee. 
        The user was told to find: '{target}'.
        Look at the attached photo.
        
        If the photo actually contains the target, start your response with: "CORRECT! "
        If the photo does NOT contain the target, start your response with: "WRONG! "
        
        Follow the prefix with a single, highly dramatic, sarcastic, or funny sentence roasting the user or hyping them up based on what you see in the photo.
        """
        
        data = {'prompt': prompt}
        response = requests.post("https://vision.pollinations.ai/analyze", files=files, data=data, timeout=15)
        
        if response.status_code == 200:
            return response.json().get("response", "WRONG! The AI judge is blind. You fail.")
        return "WRONG! The AI took a nap. You fail by default."
    except:
        return "WRONG! The referee fell asleep at the wheel."

# --- TARGET POOL (Made harder and funnier) ---
TARGETS = [
    "Something older than you", "Something that makes noise", 
    "Something with a face", "Something shiny", 
    "Something you can drink", "Something red", 
    "Something that fits in your pocket", "A shoe",
    "Something soft", "Something that smells weird",
    "Something you would use as a weapon in a zombie apocalypse"
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
st.markdown('<h1 style="text-align:center; color:#ff0040;">🎯 PROJECT: BOUNTY</h1>', unsafe_allow_html=True)

# START SCREEN
if st.session_state.game_state == "start":
    st.write("You have a randomly generated time limit to find the target and snap a photo. The AI is your judge and commentator. Don't embarrass yourself.")
    if st.button("🚀 START MISSION", type="primary", use_container_width=True):
        st.session_state.target = random.choice(TARGETS)
        st.session_state.time_limit = random.choice([15, 20, 30]) # Random difficulty!
        st.session_state.start_time = time.time()
        st.session_state.game_state = "playing"
        st.session_state.judge_result = ""
        st.rerun()

# PLAYING SCREEN
elif st.session_state.game_state == "playing":
    elapsed = time.time() - st.session_state.start_time
    time_left = max(0, st.session_state.time_limit - int(elapsed))
    
    # Display Timer and Target
    st.markdown(f'<div class="timer-box">{time_left}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="target-card">FIND: {st.session_state.target}</div>', unsafe_allow_html=True)
    st.write(f"🔥 **Current Streak:** {st.session_state.streak}")
    
    # Check if time ran out
    if time_left <= 0:
        st.session_state.game_state = "game_over"
        st.rerun()
    
    # Camera
    camera_image = st.camera_input("Snap the target NOW!")
    
    if camera_image:
        with st.spinner("AI Commentator is looking at your evidence..."):
            img = Image.open(camera_image)
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            img_bytes = img_byte_arr.getvalue()
            
            # Get AI Commentator response
            result = get_ai_comment(img_bytes, st.session_state.target)
            st.session_state.judge_result = result
            
            # Check the result
            if result.upper().startswith("CORRECT"):
                st.session_state.score += 1
                st.session_state.streak += 1
                st.session_state.game_state = "win"
            else:
                st.session_state.streak = 0 # Reset streak on wrong answer
                st.session_state.game_state = "lose"
            st.rerun()

    # Force refresh to keep the timer ticking
    time.sleep(1)
    st.rerun()

# WIN SCREEN
elif st.session_state.game_state == "win":
    st.success("✅ TARGET ACQUIRED")
    
    # Show the AI's hilarious comment
    st.markdown(f'<div class="commentator-box">{st.session_state.judge_result}</div>', unsafe_allow_html=True)
    
    st.metric("Score", st.session_state.score, delta=f"Streak: {st.session_state.streak}")
    
    if st.button("Next Target ➡️", type="primary"):
        st.session_state.target = random.choice(TARGETS)
        st.session_state.time_limit = random.choice([15, 20, 30])
        st.session_state.start_time = time.time()
        st.session_state.game_state = "playing"
        st.rerun()

# LOSE SCREEN (Wrong Object or Fail)
elif st.session_state.game_state == "lose":
    st.error("❌ TARGET NOT FOUND")
    
    # Show the AI's roast
    st.markdown(f'<div class="commentator-box">{st.session_state.judge_result}</div>', unsafe_allow_html=True)
    
    if st.button("Try Again (Timer continues!)", type="primary"):
        # Note: We do NOT reset start_time, so the timer keeps ticking!
        st.session_state.game_state = "playing"
        st.rerun()

# GAME OVER SCREEN (Time ran out)
elif st.session_state.game_state == "game_over":
    st.markdown('<div class="timer-box">0</div>', unsafe_allow_html=True)
    st.error("💀 TIME'S UP. MISSION FAILED.")
    st.metric("Final Score", st.session_state.score)
    
    if st.button("Restart Game", type="primary"):
        st.session_state.score = 0
        st.session_state.streak = 0
        st.session_state.game_state = "start"
        st.rerun()
