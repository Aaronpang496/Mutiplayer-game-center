import streamlit as st
import streamlit.components.v1 as components
import random, time, math, shutil
from streamlit_autorefresh import st_autorefresh

st.set_page_config(layout="wide", page_title="Game Center", page_icon="🎮")

# ============================================================
# GLOBAL STATE
# ============================================================
if "page" not in st.session_state:
    st.session_state.page = "home"
if "settings" not in st.session_state:
    st.session_state.settings = {}
if "sound_on" not in st.session_state:
    st.session_state.sound_on = True

# ============================================================
# SOUND + VIBRATION (injected once)
# ============================================================
def inject_fx():
    if not st.session_state.sound_on:
        return
    components.html("""
    <script>
    window.__sfx = function(type){
      try{
        const ctx = new (window.AudioContext||window.webkitAudioContext)();
        const o = ctx.createOscillator(), g = ctx.createGain();
        o.connect(g); g.connect(ctx.destination);
        const now = ctx.currentTime;
        if(type==='click'){ o.frequency.setValueAtTime(600,now); g.gain.setValueAtTime(0.08,now); g.gain.exponentialRampToValueAtTime(0.001,now+0.08); o.start(now); o.stop(now+0.08); }
        if(type==='win'){ o.frequency.setValueAtTime(880,now); o.frequency.linearRampToValueAtTime(1320,now+0.2); g.gain.setValueAtTime(0.1,now); g.gain.exponentialRampToValueAtTime(0.001,now+0.3); o.start(now); o.stop(now+0.3); }
        if(type==='lose'){ o.frequency.setValueAtTime(400,now); o.frequency.linearRampToValueAtTime(150,now+0.3); g.gain.setValueAtTime(0.1,now); g.gain.exponentialRampToValueAtTime(0.001,now+0.3); o.start(now); o.stop(now+0.3); }
        if(type==='hit'){ o.frequency.setValueAtTime(200,now); g.gain.setValueAtTime(0.12,now); g.gain.exponentialRampToValueAtTime(0.001,now+0.1); o.start(now); o.stop(now+0.1); }
        if(navigator.vibrate) navigator.vibrate(type==='hit'?20:10);
      }catch(e){}
    };
    </script>
    """, height=0, width=0)

def sfx(kind="click"):
    # Trigger JS sound via tiny iframe
    components.html(f"<script>parent.postMessage('x','*');try{{const c=new (window.AudioContext||window.webkitAudioContext)();const o=c.createOscillator(),g=c.createGain();o.connect(g);g.connect(c.destination);const n=c.currentTime;const f={{click:600,hit:200,win:880,lose:300}}['{kind}']||600;o.frequency.setValueAtTime(f,n);g.gain.setValueAtTime(0.08,n);g.gain.exponentialRampToValueAtTime(0.001,n+0.15);o.start(n);o.stop(n+0.15);if(navigator.vibrate)navigator.vibrate(15);}}catch(e){{}}</script>", height=0, width=0)

# ============================================================
# GAME REGISTRY
# ============================================================
GAMES = [
    # Board
    {"id":"ttt",     "cat":"Board", "name":"Tic-Tac-Toe",         "emoji":"❌⭕", "desc":"Classic 3x3"},
    {"id":"c4",      "cat":"Board", "name":"Connect Four",         "emoji":"🔴🟡", "desc":"Drop & connect four"},
    {"id":"reversi", "cat":"Board", "name":"Reversi / 黑白棋",      "emoji":"⚫⚪", "desc":"Flip discs, most discs wins"},
    {"id":"chess",   "cat":"Board", "name":"Chess",                "emoji":"♟️", "desc":"Full chess with clock"},
    {"id":"nim",     "cat":"Board", "name":"Nim",                  "emoji":"🪵",  "desc":"Take the last stick to win"},
    # Cards / Puzzle
    {"id":"memory",  "cat":"Puzzle","name":"Memory Match",         "emoji":"🃏",  "desc":"Flip & match pairs"},
    {"id":"hangman", "cat":"Puzzle","name":"Hangman",              "emoji":"🪢",  "desc":"Guess the word"},
    {"id":"2048",    "cat":"Puzzle","name":"2048",                 "emoji":"🔢",  "desc":"Merge tiles to 2048"},
    # Quick
    {"id":"rps",     "cat":"Quick", "name":"Rock Paper Scissors",  "emoji":"✊✋✌️","desc":"Best of three"},
    {"id":"guess",   "cat":"Quick", "name":"Number Guessing",      "emoji":"🔢",  "desc":"Higher or lower"},
    {"id":"dice",    "cat":"Quick", "name":"Dice Duel",            "emoji":"🎲",  "desc":"Roll higher to win"},
    {"id":"coin",    "cat":"Quick", "name":"Coin Flip Streak",     "emoji":"🪙",  "desc":"Call heads or tails"},
    # Action
    {"id":"reaction","cat":"Action","name":"Reaction Race",        "emoji":"⚡",  "desc":"Tap on green, fastest wins"},
    {"id":"whack",   "cat":"Action","name":"Whack-a-Mole",         "emoji":"🔨",  "desc":"Smash moles in 30s"},
    {"id":"target",  "cat":"Action","name":"Target Tap",           "emoji":"🎯",  "desc":"Hit moving targets"},
    {"id":"tug",     "cat":"Action","name":"Tug of War",           "emoji":"🪢",  "desc":"Mash to pull the rope"},
    {"id":"pong",    "cat":"Action","name":"Pong Duel",            "emoji":"🏓",  "desc":"Two paddles, one ball"},
    {"id":"snake",   "cat":"Action","name":"Snake Duel",           "emoji":"🐍",  "desc":"Two snakes, one grid"},
    {"id":"bey",     "cat":"Action","name":"Beyblade Arena",       "emoji":"🌀",  "desc":"Two joysticks, one arena"},
    # Reflex
    {"id":"simon",   "cat":"Reflex","name":"Simon Says",           "emoji":"🎵",  "desc":"Repeat the color pattern"},
]

# ============================================================
# HOME PAGE
# ============================================================
def home_page():
    st.title("🎮 Game Center")
    st.caption("Scroll to browse · pick a category to filter · every game has Human vs AI + difficulty")

    if st.button("🔊 Sound ON" if st.session_state.sound_on else "🔇 Sound OFF", key="sound_toggle"):
        st.session_state.sound_on = not st.session_state.sound_on
        st.rerun()

    cats = ["All"] + sorted({g["cat"] for g in GAMES})
    chosen = st.radio("Category", cats, horizontal=True, label_visibility="collapsed")
    visible = GAMES if chosen == "All" else [g for g in GAMES if g["cat"] == chosen]

    for game in visible:
        gid = game["id"]
        if gid not in st.session_state.settings:
            st.session_state.settings[gid] = {"mode":"Human", "difficulty":3}
        with st.container(border=True):
            head_l, head_r = st.columns([4,1])
            with head_l:
                st.markdown(f"## {game['emoji']} {game['name']}")
                st.caption(f"{game['cat']} · {game['desc']}")
            with head_r:
                play = st.button("▶ Play", key=f"play_{gid}", use_container_width=True)
            mode = st.radio("Mode", ["Human","AI"], horizontal=True,
                            index=0 if st.session_state.settings[gid]["mode"]=="Human" else 1,
                            key=f"mode_{gid}", label_visibility="collapsed")
            st.session_state.settings[gid]["mode"] = mode
            if mode == "AI":
                diff = st.slider("AI Difficulty", 1, 5,
                                 value=st.session_state.settings[gid]["difficulty"],
                                 key=f"diff_{gid}")
                st.session_state.settings[gid]["difficulty"] = diff
            if play:
                sfx("click")
                st.session_state.page = gid
                st.rerun()

# ============================================================
# HELPERS
# ============================================================
def result_banner(text, kind="win"):
    if kind == "win":
        st.success(text); sfx("win")
    elif kind == "lose":
        st.error(text); sfx("lose")
    else:
        st.info(text)

def fresh(key, init_fn):
    if key not in st.session_state:
        init_fn()

def fmt_clock(sec):
    m, s = divmod(int(max(0,sec)), 60)
    return f"{m}:{s:02d}"

# ============================================================
# TIC-TAC-TOE
# ============================================================
def game_ttt(mode, difficulty):
    st.subheader("❌⭕ Tic-Tac-Toe")
    def init():
        st.session_state.ttt_b = [[" "]*3 for _ in range(3)]
        st.session_state.ttt_t = "X"
        st.session_state.ttt_over = False
    fresh("ttt_b", init)
    b = st.session_state.ttt_b

    def win(b):
        lines = b + [list(c) for c in zip(*b)] + [[b[i][i] for i in range(3)], [b[i][2-i] for i in range(3)]]
        for l in lines:
            if l[0] != " " and len(set(l)) == 1: return l[0]
        return "D" if all(c != " " for r in b for c in r) else None

    def ai_move():
        empty = [(i,j) for i in range(3) for j in range(3) if b[i][j]==" "]
        if not empty: return
        if random.random() < (difficulty-1)/4:
            # try to win, then block
            for mark in ["O","X"]:
                for i,j in empty:
                    b[i][j] = mark
                    if win(b) == mark and mark=="O":
                        b[i][j]=" "; return (i,j)
                    b[i][j] = " "
            # else random
            return random.choice(empty)
        return random.choice(empty)

    if st.button("🔄 New Game", key="ttt_reset"):
        init(); st.rerun()

    w = win(b)
    if w and not st.session_state.ttt_over:
        st.session_state.ttt_over = True
    if w:
        if w == "D": result_banner("Draw!", "info")
        else: result_banner(f"{w} wins!", "win")

    if not w and mode=="AI" and st.session_state.ttt_t=="O":
        with st.spinner("AI thinking..."):
            mv = ai_move()
        if mv:
            b[mv[0]][mv[1]] = "O"
            st.session_state.ttt_t = "X"
            sfx("hit")
            st.rerun()

    for i in range(3):
        cols = st.columns(3)
        for j in range(3):
            label = b[i][j] if b[i][j] != " " else "·"
            if cols[j].button(label, key=f"ttt_{i}_{j}", use_container_width=True, disabled=bool(w) or b[i][j]!=" " or (mode=="AI" and st.session_state.ttt_t=="O")):
                b[i][j] = st.session_state.ttt_t
                st.session_state.ttt_t = "O" if st.session_state.ttt_t=="X" else "X"
                sfx("hit")
                st.rerun()

# ============================================================
# CONNECT FOUR
# ============================================================
def game_c4(mode, difficulty):
    st.subheader("🔴🟡 Connect Four")
    ROWS, COLS = 6, 7
    def init():
        st.session_state.c4_b = [[" "]*COLS for _ in range(ROWS)]
        st.session_state.c4_t = "R"
    fresh("c4_b", init)
    b = st.session_state.c4_b

    def drop(col, color):
        for r in range(ROWS-1, -1, -1):
            if b[r][col] == " ":
                b[r][col] = color; return r
        return None

    def check(r, c, color):
        for dr, dc in [(0,1),(1,0),(1,1),(1,-1)]:
            cnt = 1
            for s in (-1,1):
                rr, cc = r+dr*s, c+dc*s
                while 0<=rr<ROWS and 0<=cc<COLS and b[rr][cc]==color:
                    cnt += 1; rr += dr*s; cc += dc*s
            if cnt >= 4: return True
        return False

    def winner():
        for r in range(ROWS):
            for c in range(COLS):
                if b[r][c] != " " and check(r, c, b[r][c]): return b[r][c]
        return "D" if all(b[0][c] != " " for c in range(COLS)) else None

    if st.button("🔄 New Game", key="c4_reset"):
        init(); st.rerun()

    w = winner()
    if w:
        result_banner("Draw!" if w=="D" else ("🔴 Red wins!" if w=="R" else "🟡 Yellow wins!"), "win" if w!="D" else "info")

    if not w and mode=="AI" and st.session_state.c4_t=="Y":
        with st.spinner("AI thinking..."):
            cols = [c for c in range(COLS) if b[0][c]==" "]
            if cols:
                if random.random() < (difficulty-1)/4:
                    # try win / block
                    choice = random.choice(cols)
                    for color in ["Y","R"]:
                        for c in cols:
                            r = drop(c, color)
                            if r is not None and check(r, c, color):
                                b[r][c] = " "
                                if color == "Y": choice = c; break
                                else: choice = c
                            if r is not None: b[r][c] = " "
                        if color == "Y":
                            # re-check if found winning
                            r = drop(choice, "Y")
                            if r is not None and check(r, choice, "Y"):
                                b[r][choice] = " "
                                break
                            if r is not None: b[r][choice] = " "
                r = drop(choice, "Y")
                if r is not None and not winner():
                    st.session_state.c4_t = "R"
                sfx("hit")
        st.rerun()

    st.markdown("**Tap a column to drop:**")
    top = st.columns(COLS)
    for c in range(COLS):
        if top[c].button("⬇️", key=f"c4_drop_{c}", use_container_width=True, disabled=bool(w) or (mode=="AI" and st.session_state.c4_t=="Y") or b[0][c]!=" "):
            r = drop(c, st.session_state.c4_t)
            if r is not None:
                st.session_state.c4_t = "Y" if st.session_state.c4_t=="R" else "R"
                sfx("hit")
                st.rerun()

    for r in range(ROWS):
        cols = st.columns(COLS)
        for c in range(COLS):
            v = b[r][c]
            cols[c].markdown(f"<div style='text-align:center;font-size:28px'>{'🔴' if v=='R' else '🟡' if v=='Y' else '⚪'}</div>", unsafe_allow_html=True)

# ============================================================
# REVERSI
# ============================================================
def game_reversi(mode, difficulty):
    st.subheader("⚫⚪ Reversi / 黑白棋")
    DIRS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    def init():
        b = [["."]*8 for _ in range(8)]
        b[3][3] = b[4][4] = "W"; b[3][4] = b[4][3] = "B"
        st.session_state.rv_b = b
        st.session_state.rv_t = "B"
        st.session_state.rv_bt = 300.0; st.session_state.rv_wt = 300.0
        st.session_state.rv_last = time.time()
    fresh("rv_b", init)
    st_autorefresh(interval=1000, key="rv_tick")
    b = st.session_state.rv_b

    now = time.time()
    dt = now - st.session_state.rv_last
    st.session_state.rv_last = now
    if st.session_state.rv_t == "B": st.session_state.rv_bt = max(0, st.session_state.rv_bt - dt)
    else: st.session_state.rv_wt = max(0, st.session_state.rv_wt - dt)

    c1, c2 = st.columns(2)
    c1.metric("Black ⏱", fmt_clock(st.session_state.rv_bt))
    c2.metric("White ⏱", fmt_clock(st.session_state.rv_wt))

    if st.session_state.rv_bt <= 0: result_banner("⏰ Black timeout — White wins!", "lose"); return
    if st.session_state.rv_wt <= 0: result_banner("⏰ White timeout — Black wins!", "lose"); return
    if st.button("🔄 New Game", key="rv_reset"): init(); st.rerun()

    def flips(r, c, color):
        if b[r][c] != ".": return []
        opp = "W" if color=="B" else "B"; out = []
        for dr, dc in DIRS:
            line = []; rr, cc = r+dr, c+dc
            while 0<=rr<8 and 0<=cc<8 and b[rr][cc]==opp:
                line.append((rr,cc)); rr += dr; cc += dc
            if line and 0<=rr<8 and 0<=cc<8 and b[rr][cc]==color: out.extend(line)
        return out

    def legal(color):
        return [(r,c) for r in range(8) for c in range(8) if flips(r,c,color)]

    def apply(r, c, color):
        for rr, cc in flips(r,c,color): b[rr][cc] = color
        b[r][c] = color

    turn = st.session_state.rv_t
    moves = legal(turn)
    if not moves:
        st.warning(f"{turn} has no moves — passing.")
        st.session_state.rv_t = "W" if turn=="B" else "B"
        st.session_state.rv_last = time.time()
        st.rerun()

    bsc = sum(row.count("B") for row in b); wsc = sum(row.count("W") for row in b)
    st.caption(f"Black: {bsc} · White: {wsc} · Turn: {turn}")

    for r in range(8):
        cols = st.columns(8)
        for c in range(8):
            v = b[r][c]
            label = "·" if v=="." else ("⚫" if v=="B" else "⚪")
            if (r,c) in moves: label = f"·{label}" if v=="." else label
            if cols[c].button(label, key=f"rv_{r}_{c}", use_container_width=True, disabled=(mode=="AI" and turn=="W")):
                if (r,c) in moves:
                    apply(r,c,turn)
                    st.session_state.rv_t = "W" if turn=="B" else "B"
                    st.session_state.rv_last = time.time()
                    sfx("hit"); st.rerun()

    if mode=="AI" and st.session_state.rv_t=="W":
        with st.spinner("AI thinking..."):
            ms = legal("W")
            if ms:
                greedy = random.random() < (difficulty/5)
                mv = max(ms, key=lambda m: len(flips(m[0], m[1], "W"))) if greedy else random.choice(ms)
                apply(mv[0], mv[1], "W")
                st.session_state.rv_t = "B"
                st.session_state.rv_last = time.time()
                sfx("hit")
        st.rerun()

# ============================================================
# CHESS
# ============================================================
def game_chess(mode, difficulty):
    try:
        import chess, chess.engine
    except ImportError:
        st.error("Install python-chess: `pip install python-chess`"); return

    st.subheader("♟️ Chess")
    def init():
        st.session_state.ch_b = chess.Board()
        st.session_state.ch_wt = 300.0; st.session_state.ch_bt = 300.0
        st.session_state.ch_last = time.time()
        st.session_state.ch_sel = None
    fresh("ch_b", init)
    st_autorefresh(interval=1000, key="ch_tick")
    b = st.session_state.ch_b

    now = time.time()
    dt = now - st.session_state.ch_last
    st.session_state.ch_last = now
    if not b.is_game_over():
        if b.turn == chess.WHITE: st.session_state.ch_wt = max(0, st.session_state.ch_wt - dt)
        else: st.session_state.ch_bt = max(0, st.session_state.ch_bt - dt)

    c1, c2 = st.columns(2)
    c1.metric("White ⏱", fmt_clock(st.session_state.ch_wt))
    c2.metric("Black ⏱", fmt_clock(st.session_state.ch_bt))

    if st.session_state.ch_wt <= 0: result_banner("⏰ White timeout — Black wins!", "lose"); return
    if st.session_state.ch_bt <= 0: result_banner("⏰ Black timeout — White wins!", "lose"); return
    if st.button("🔄 New Game", key="ch_reset"): init(); st.rerun()

    if b.is_checkmate():
        result_banner(f"Checkmate! {'White' if b.turn==chess.BLACK else 'Black'} wins!", "win"); return
    if b.is_stalemate() or b.is_insufficient_material():
        result_banner("Draw.", "info"); return

    UNI = {"P":"♙","N":"♘","B":"♗","R":"♖","Q":"♕","K":"♔","p":"♟","n":"♞","b":"♝","r":"♜","q":"♛","k":"♚"}
    sel = st.session_state.ch_sel

    for rank in range(7, -1, -1):
        cols = st.columns(8)
        for file in range(8):
            sq = chess.square(file, rank)
            p = b.piece_at(sq)
            label = UNI.get(p.symbol(), "") if p else "·"
            if sel is not None:
                if sq == sel: label = f"【{label}】"
                elif chess.Move(sel, sq) in b.legal_moves: label = f"•{label}"
            if cols[file].button(label, key=f"ch_{sq}", use_container_width=True, disabled=(mode=="AI" and b.turn==chess.BLACK)):
                if sel is None:
                    pp = b.piece_at(sq)
                    if pp and pp.color == b.turn: st.session_state.ch_sel = sq
                else:
                    mv = chess.Move(sel, sq)
                    if b.piece_at(sel) and b.piece_at(sel).piece_type == chess.PAWN and chess.square_rank(sq) in (0,7):
                        mv = chess.Move(sel, sq, promotion=chess.QUEEN)
                    if mv in b.legal_moves:
                        b.push(mv); st.session_state.ch_sel = None
                        st.session_state.ch_last = time.time()
                        sfx("hit"); st.rerun()
                    else:
                        pp = b.piece_at(sq)
                        st.session_state.ch_sel = sq if (pp and pp.color == b.turn) else None
                        st.rerun()

    if mode=="AI" and b.turn==chess.BLACK and not b.is_game_over():
        with st.spinner("AI thinking..."):
            skill = {1:0,2:5,3:10,4:15,5:20}[difficulty]
            think = {1:0.05,2:0.1,3:0.3,4:0.6,5:1.0}[difficulty]
            mv = None
            path = shutil.which("stockfish") or "/usr/bin/stockfish"
            try:
                with chess.engine.SimpleEngine.popen_uci(path) as eng:
                    eng.configure({"Skill Level": skill})
                    mv = eng.play(b, chess.engine.Limit(time=think)).move
            except Exception:
                mv = random.choice(list(b.legal_moves))
            if mv:
                b.push(mv); st.session_state.ch_last = time.time(); sfx("hit")
        st.rerun()

# ============================================================
# NIM
# ============================================================
def game_nim(mode, difficulty):
    st.subheader("🪵 Nim — take the last stick to WIN")
    def init():
        st.session_state.nim_p = [3,5,7]
        st.session_state.nim_t = "You"
    fresh("nim_p", init)
    piles = st.session_state.nim_p
    if st.button("🔄 New Game", key="nim_reset"): init(); st.rerun()

    if sum(piles) == 0:
        result_banner(f"🏆 {st.session_state.nim_t} wins!", "win")
        return

    st.caption(f"Turn: **{st.session_state.nim_t}**")
    for i, p in enumerate(piles):
        st.markdown(f"Pile {i+1}: {'🪵'*p if p else '(empty)'}")
        if p > 0:
            take = st.slider(f"Take from pile {i+1}", 1, p, 1, key=f"nim_s_{i}")
            if st.button(f"Take {take} from pile {i+1}", key=f"nim_b_{i}"):
                piles[i] -= take
                st.session_state.nim_t = "AI" if mode=="AI" and st.session_state.nim_t=="You" else ("You" if st.session_state.nim_t=="AI" else "Player 2")
                sfx("hit"); st.rerun()

    if mode=="AI" and st.session_state.nim_t=="AI" and sum(piles) > 0:
        with st.spinner("AI thinking..."):
            if random.random() < (difficulty/5):
                xor = 0
                for p in piles: xor ^= p
                if xor != 0:
                    for i, p in enumerate(piles):
                        target = p ^ xor
                        if target < p:
                            piles[i] = target; break
                else:
                    for i, p in enumerate(piles):
                        if p > 0: piles[i] -= 1; break
            else:
                nonempty = [i for i,p in enumerate(piles) if p > 0]
                if nonempty:
                    i = random.choice(nonempty); piles[i] -= 1
            st.session_state.nim_t = "You"
            sfx("hit")
        st.rerun()

# ============================================================
# MEMORY MATCH
# ============================================================
def game_memory(mode, difficulty):
    st.subheader("🃏 Memory Match")
    EMOJIS = ["🍎","🍌","🍇","🍓","🍒","🥝","🍑","🍍"]
    def init():
        n = 4 if difficulty <= 2 else (6 if difficulty <= 4 else 8)
        deck = EMOJIS[:n] * 2
        random.shuffle(deck)
        st.session_state.mem_d = deck
        st.session_state.mem_rev = []
        st.session_state.mem_done = set()
        st.session_state.mem_p = [0,0]
        st.session_state.mem_t = 0
    fresh("mem_d", init)
    d = st.session_state.mem_d

    if st.button("🔄 New Game", key="mem_reset"): init(); st.rerun()

    st.caption(f"P1: {st.session_state.mem_p[0]} · P2/AI: {st.session_state.mem_p[1]} · Turn: {'P1' if st.session_state.mem_t==0 else 'P2/AI'}")

    if len(st.session_state.mem_done) == len(d):
        p = st.session_state.mem_p
        if p[0] > p[1]: result_banner("🏆 P1 wins!", "win")
        elif p[1] > p[0]: result_banner("🏆 P2/AI wins!", "win")
        else: result_banner("Draw!", "info")
        return

    ncols = 4
    for r in range(0, len(d), ncols):
        cols = st.columns(ncols)
        for cidx in range(ncols):
            idx = r + cidx
            if idx >= len(d): break
            if idx in st.session_state.mem_done:
                cols[cidx].markdown(f"<div style='text-align:center;font-size:32px'>{d[idx]}</div>", unsafe_allow_html=True)
            elif idx in st.session_state.mem_rev:
                cols[cidx].markdown(f"<div style='text-align:center;font-size:32px'>{d[idx]}</div>", unsafe_allow_html=True)
            else:
                if cols[cidx].button("❓", key=f"mem_{idx}", use_container_width=True, disabled=(mode=="AI" and st.session_state.mem_t==1)):
                    st.session_state.mem_rev.append(idx)
                    sfx("hit")
                    if len(st.session_state.mem_rev) == 2:
                        a, bb = st.session_state.mem_rev
                        if d[a] == d[bb]:
                            st.session_state.mem_done.update([a,bb])
                            st.session_state.mem_p[st.session_state.mem_t] += 1
                            st.session_state.mem_rev = []
                            st.rerun()
                        else:
                            st.rerun()
                    else:
                        st.rerun()

    if len(st.session_state.mem_rev) == 2:
        a, bb = st.session_state.mem_rev
        if d[a] != d[bb]:
            st.warning("No match — switching turn")
            if st.button("OK, next turn"):
                st.session_state.mem_rev = []
                st.session_state.mem_t = 1 - st.session_state.mem_t
                st.rerun()

    if mode=="AI" and st.session_state.mem_t==1 and len(st.session_state.mem_rev) < 2:
        with st.spinner("AI thinking..."):
            unknown = [i for i in range(len(d)) if i not in st.session_state.mem_done and i not in st.session_state.mem_rev]
            if unknown:
                if random.random() < (difficulty/5):
                    # cheat-lite: peek a pair
                    seen = {}
                    for i in unknown:
                        if d[i] in seen:
                            st.session_state.mem_rev = [seen[d[i]], i]
                            break
                        seen[d[i]] = i
                    else:
                        pick = random.sample(unknown, min(2, len(unknown)))
                        st.session_state.mem_rev = pick
                else:
                    st.session_state.mem_rev = random.sample(unknown, min(2, len(unknown)))
                sfx("hit")
        st.rerun()

# ============================================================
# HANGMAN
# ============================================================
def game_hangman(mode, difficulty):
    st.subheader("🪢 Hangman")
    WORDS = ["APPLE","TIGER","PLANET","GUITAR","ROCKET","SILVER","GARDEN","WINTER","MONKEY","PUZZLE"]
    def init():
        st.session_state.hm_w = random.choice(WORDS)
        st.session_state.hm_g = set()
        st.session_state.hm_wrong = 0
    fresh("hm_w", init)
    w = st.session_state.hm_w
    max_wrong = 8 - difficulty

    if st.button("🔄 New Game", key="hm_reset"): init(); st.rerun()

    display = " ".join(c if c in st.session_state.hm_g else "_" for c in w)
    st.markdown(f"### {display}")
    st.caption(f"Wrong: {st.session_state.hm_wrong}/{max_wrong}")

    if "_" not in display:
        result_banner(f"🏆 You got it: {w}", "win"); return
    if st.session_state.hm_wrong >= max_wrong:
        result_banner(f"💀 Out of guesses. Word was {w}", "lose"); return

    for r in range(0, 26, 7):
        cols = st.columns(7)
        for i in range(7):
            idx = r + i
            if idx >= 26: break
            ch = chr(ord('A')+idx)
            if cols[i].button(ch, key=f"hm_{ch}", use_container_width=True, disabled=ch in st.session_state.hm_g):
                st.session_state.hm_g.add(ch)
                if ch not in w: st.session_state.hm_wrong += 1
                sfx("hit"); st.rerun()

    if mode=="AI":
        st.info("🤖 AI mode: play against the clock — try to finish in fewer than " + str(max(3, 9-difficulty)) + " wrong guesses.")

# ============================================================
# 2048
# ============================================================
def game
# ============================================================
# 2048
# ============================================================
def game_2048(mode, difficulty):
    st.subheader("🔢 2048")
    SIZE = 4

    def add_tile(b):
        empty = [(r, c) for r in range(SIZE) for c in range(SIZE) if b[r][c] == 0]
        if empty:
            r, c = random.choice(empty)
            b[r][c] = 4 if random.random() < 0.1 else 2

    def init():
        b = [[0]*SIZE for _ in range(SIZE)]
        add_tile(b); add_tile(b)
        st.session_state.g2048_b = b
        st.session_state.g2048_score = 0
        st.session_state.g2048_over = False
    fresh("g2048_b", init)
    b = st.session_state.g2048_b

    def slide(row):
        non_zero = [x for x in row if x != 0]
        out = []
        i = 0
        while i < len(non_zero):
            if i + 1 < len(non_zero) and non_zero[i] == non_zero[i+1]:
                out.append(non_zero[i]*2)
                st.session_state.g2048_score += non_zero[i]*2
                i += 2
            else:
                out.append(non_zero[i]); i += 1
        return out + [0]*(SIZE - len(out))

    def move(direction):
        grid = [row[:] for row in b]
        if direction in ("left", "right"):
            for r in range(SIZE):
                row = grid[r] if direction == "left" else grid[r][::-1]
                new = slide(row)
                grid[r] = new if direction == "left" else new[::-1]
        else:
            for c in range(SIZE):
                col = [grid[r][c] for r in range(SIZE)]
                if direction == "up":
                    new = slide(col)
                else:
                    new = slide(col[::-1])[::-1]
                for r in range(SIZE):
                    grid[r][c] = new[r]
        changed = grid != b
        if changed:
            for r in range(SIZE):
                for c in range(SIZE):
                    b[r][c] = grid[r][c]
            add_tile(b)
            if not any(can_move(r, c) for r in range(SIZE) for c in range(SIZE)):
                st.session_state.g2048_over = True
        return changed

    def can_move(r, c):
        if b[r][c] == 0: return True
        for dr, dc in [(0,1),(1,0)]:
            rr, cc = r+dr, c+dc
            if 0 <= rr < SIZE and 0 <= cc < SIZE and b[rr][cc] == b[r][c]:
                return True
        return False

    if st.button("🔄 New Game", key="g2048_reset"):
        init(); st.rerun()

    st.metric("Score", st.session_state.g2048_score)
    if any(b[r][c] == 2048 for r in range(SIZE) for c in range(SIZE)):
        result_banner("🏆 You reached 2048!", "win")
    elif st.session_state.g2048_over:
        result_banner("Game over — no more moves.", "lose")

    # Arrow-key handling
    components.html("""
    <script>
    window.addEventListener('keydown', (e) => {
        if(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.key)){
            window.parent.postMessage({type:'2048',key:e.key}, '*');
        }
    });
    </script>
    """, height=0)

    # Grid display
    for r in range(SIZE):
        cols = st.columns(SIZE)
        for c in range(SIZE):
            v = b[r][c]
            color = "#cdc1b4" if v == 0 else "#f2b179" if v < 8 else "#f67c5f" if v < 32 else "#f65e3b" if v < 128 else "#edcf72"
            text = "" if v == 0 else str(v)
            cols[c].markdown(
                f"<div style='background:{color};border-radius:6px;padding:18px;text-align:center;"
                f"font-size:22px;font-weight:bold;color:#776e65'>{text}</div>",
                unsafe_allow_html=True
            )

    # Buttons as fallback (since postMessage rerun needs extra wiring)
    b1, b2, b3 = st.columns([1,1,1])
    if b1.button("⬆️ Up", use_container_width=True) and move("up"): sfx("hit"); st.rerun()
    if b2.button("⬅️ Left", use_container_width=True) and move("left"): sfx("hit"); st.rerun()
    if b3.button("➡️ Right", use_container_width=True) and move("right"): sfx("hit"); st.rerun()
    if st.button("⬇️ Down", use_container_width=True) and move("down"): sfx("hit"); st.rerun()


# ============================================================
# ROCK PAPER SCISSORS
# ============================================================
def game_rps(mode, difficulty):
    st.subheader("✊✋✌️ Rock Paper Scissors")
    if "rps_you" not in st.session_state:
        st.session_state.rps_you = 0
        st.session_state.rps_opp = 0
        st.session_state.rps_log = []

    def play(move):
        if mode == "AI":
            if random.random() < difficulty/5:
                # best response to human's most frequent
                pass
            opp = random.choice(["rock","paper","scissors"])
        else:
            opp = random.choice(["rock","paper","scissors"])
        if move == opp: res = "draw"
        elif (move=="rock" and opp=="scissors") or (move=="paper" and opp=="rock") or (move=="scissors" and opp=="paper"):
            res = "win"; st.session_state.rps_you += 1
        else:
            res = "lose"; st.session_state.rps_opp += 1
        st.session_state.rps_log.append((move, opp, res))
        sfx("win" if res=="win" else "lose" if res=="lose" else "click")

    c1, c2, c3 = st.columns(3)
    if c1.button("✊ Rock", use_container_width=True): play("rock"); st.rerun()
    if c2.button("✋ Paper", use_container_width=True): play("paper"); st.rerun()
    if c3.button("✌️ Scissors", use_container_width=True): play("scissors"); st.rerun()

    st.caption(f"You: {st.session_state.rps_you} · Opponent: {st.session_state.rps_opp}")
    for m, o, r in st.session_state.rps_log[-5:]:
        emoji = {"win":"✅","lose":"❌","draw":"➖"}[r]
        st.write(f"{emoji} you: {m} vs {o}")

    if st.session_state.rps_you >= 2:
        result_banner("🏆 You win the match!", "win")
    elif st.session_state.rps_opp >= 2:
        result_banner("💀 Opponent wins the match.", "lose")


# ============================================================
# NUMBER GUESSING
# ============================================================
def game_guess(mode, difficulty):
    st.subheader("🔢 Number Guessing")
    if "guess_n" not in st.session_state:
        st.session_state.guess_n = random.randint(1, 100)
        st.session_state.guess_tries = 0
    n = st.session_state.guess_n
    g = st.number_input("Guess a number 1-100", 1, 100, 50, key="guess_input")
    if st.button("Guess!", key="guess_btn"):
        st.session_state.guess_tries += 1
        if g == n:
            result_banner(f"🏆 Got it in {st.session_state.guess_tries} tries!", "win")
        elif g < n:
            st.info("📈 Higher!"); sfx("click")
        else:
            st.info("📉 Lower!"); sfx("click")
    if st.button("🔄 New Number", key="guess_reset"):
        st.session_state.guess_n = random.randint(1, 100)
        st.session_state.guess_tries = 0
        st.rerun()


# ============================================================
# DICE DUEL
# ============================================================
def game_dice(mode, difficulty):
    st.subheader("🎲 Dice Duel")
    if "dice_rounds" not in st.session_state:
        st.session_state.dice_rounds = []
    if st.button("🎲 Roll!", key="dice_roll"):
        you = random.randint(1, 6)
        opp = random.randint(1, 6)
        st.session_state.dice_rounds.append((you, opp))
        sfx("hit")
    if st.session_state.dice_rounds:
        you, opp = st.session_state.dice_rounds[-1]
        st.write(f"You rolled: **{you}**")
        st.write(f"Opponent rolled: **{opp}**")
        if you > opp: result_banner("🏆 You win the round!", "win")
        elif you < opp: result_banner("💀 You lose the round.", "lose")
        else: result_banner("Draw.", "info")
    if st.button("🔄 Reset", key="dice_reset"):
        st.session_state.dice_rounds = []; st.rerun()


# ============================================================
# COIN FLIP STREAK
# ============================================================
def game_coin(mode, difficulty):
    st.subheader("🪙 Coin Flip Streak")
    if "coin_streak" not in st.session_state:
        st.session_state.coin_streak = 0
        st.session_state.coin_best = 0
    c1, c2 = st.columns(2)
    if c1.button("Heads", use_container_width=True):
        r = random.choice(["H","T"])
        if r == "H":
            st.session_state.coin_streak += 1
            st.session_state.coin_best = max(st.session_state.coin_best, st.session_state.coin_streak)
            sfx("win")
        else:
            st.session_state.coin_streak = 0; sfx("lose")
        st.rerun()
    if c2.button("Tails", use_container_width=True):
        r = random.choice(["H","T"])
        if r == "T":
            st.session_state.coin_streak += 1
            st.session_state.coin_best = max(st.session_state.coin_best, st.session_state.coin_streak)
            sfx("win")
        else:
            st.session_state.coin_streak = 0; sfx("lose")
        st.rerun()
    st.metric("Current Streak", st.session_state.coin_streak)
    st.metric("Best Streak", st.session_state.coin_best)


# ============================================================
# REACTION RACE
# ============================================================
def game_reaction(mode, difficulty):
    st.subheader("⚡ Reaction Race")
    if "react_start" not in st.session_state:
        st.session_state.react_start = None
        st.session_state.react_ready = False
        st.session_state.react_result = None
    if st.button("Start Timer", key="react_start_btn"):
        st.session_state.react_start = time.time()
        st.session_state.react_ready = True
        st.session_state.react_result = None
    if st.session_state.react_ready and st.button("🟢 TAP!", key="react_tap"):
        rt = time.time() - st.session_state.react_start
        st.session_state.react_result = rt
        st.session_state.react_ready = False
        sfx("hit")
    if st.session_state.react_result:
        st.metric("Your reaction", f"{st.session_state.react_result*1000:.0f} ms")
        if st.session_state.react_result < 0.3:
            result_banner("⚡ Insane reflexes!", "win")
        elif st.session_state.react_result < 0.5:
            result_banner("Great!", "win")
        else:
            result_banner("Keep practicing.", "info")


# ============================================================
# WHACK-A-MOLE
# ============================================================
def game_whack(mode, difficulty):
    st.subheader("🔨 Whack-a-Mole")
    GRID = 9
    if "whack_mole" not in st.session_state:
        st.session_state.whack_mole = random.randint(0, GRID-1)
        st.session_state.whack_score = 0
        st.session_state.whack_start = time.time()
    elapsed = time.time() - st.session_state.whack_start
    if elapsed > 30:
        result_banner(f"⏰ Time! Score: {st.session_state.whack_score}", "info")
        if st.button("🔄 Play again", key="whack_reset"):
            for k in ["whack_mole","whack_score","whack_start"]:
                del st.session_state[k]
            st.rerun()
        return
    st.caption(f"Score: {st.session_state.whack_score} · Time left: {30 - elapsed:.1f}s")
    for r in range(3):
        cols = st.columns(3)
        for c in range(3):
            idx = r*3 + c
            is_mole = idx == st.session_state.whack_mole
            label = "🐹" if is_mole else "·"
            if cols[c].button(label, key=f"whack_{idx}", use_container_width=True):
                if is_mole:
                    st.session_state.whack_score += 1
                    st.session_state.whack_mole = random.randint(0, GRID-1)
                    sfx("hit")
                st.rerun()


# ============================================================
# TARGET TAP
# ============================================================
def game_target(mode, difficulty):
    st.subheader("🎯 Target Tap")
    if "target_pos" not in st.session_state:
        st.session_state.target_pos = random.randint(0, 8)
        st.session_state.target_score = 0
        st.session_state.target_start = time.time()
    elapsed = time.time() - st.session_state.target_start
    if elapsed > 20:
        result_banner(f"⏰ Score: {st.session_state.target_score}", "info")
        if st.button("🔄 Again", key="target_reset"):
            for k in ["target_pos","target_score","target_start"]:
                del st.session_state[k]
            st.rerun()
        return
    st.caption(f"Score: {st.session_state.target_score} · Time left: {20 - elapsed:.1f}s")
    for r in range(3):
        cols = st.columns(3)
        for c in range(3):
            idx = r*3 + c
            label = "🎯" if idx == st.session_state.target_pos else "·"
            if cols[c].button(label, key=f"target_{idx}", use_container_width=True):
                if idx == st.session_state.target_pos:
                    st.session_state.target_score += 1
                    st.session_state.target_pos = random.randint(0, 8)
                    sfx("hit")
                st.rerun()


# ============================================================
# TUG OF WAR
# ============================================================
def game_tug(mode, difficulty):
    st.subheader("🪢 Tug of War")
    if "tug_pos" not in st.session_state:
        st.session_state.tug_pos = 0.0
    pos = st.session_state.tug_pos
    st.progress(min(max((pos + 10) / 20, 0), 1))
    st.caption(f"Rope: {pos:.1f} (-10 you lose · +10 you win)")
    c1, c2 = st.columns(2)
    if c1.button("💪 Pull!", use_container_width=True):
        st.session_state.tug_pos += 1
        if random.random() < 0.5: st.session_state.tug_pos -= 0.7
        sfx("hit"); st.rerun()
    if c2.button("🧘 Rest", use_container_width=True):
        if random.random() < 0.6: st.session_state.tug_pos -= 0.8
        st.rerun()
    if st.session_state.tug_pos >= 10:
        result_banner("🏆 You win!", "win")
    elif st.session_state.tug_pos <= -10:
        result_banner("💀 You lose.", "lose")


# ============================================================
# PONG (simplified turn-based-ish demo)
# ============================================================
def game_pong(mode, difficulty):
    st.subheader("🏓 Pong Duel")
    st.info("Use the sliders below to move paddles. First to 5 wins the exchange.")
    if "pong_you" not in st.session_state:
        st.session_state.pong_you = 0
        st.session_state.pong_opp = 0
        st.session_state.pong_bally = 50
        st.session_state.pong_ballx = 50
    ypaddle = st.slider("Your paddle", 0, 100, 50, key="pong_yp")
    opp_paddle = 50 if mode == "Human" else random.randint(30, 70)
    ball_y = st.session_state.pong_bally
    ball_x = st.session_state.pong_ballx

    if st.button("🏓 Hit!", key="pong_hit"):
        if abs(ball_y - ypaddle) < 20:
            st.session_state.pong_you += 1; sfx("win")
        else:
            st.session_state.pong_opp += 1; sfx("lose")
        st.session_state.pong_bally = random.randint(0, 100)
        st.session_state.pong_ballx = random.randint(0, 100)
        st.rerun()

    st.caption(f"Ball at (x={ball_x}, y={ball_y}) · You {st.session_state.pong_you} - {st.session_state.pong_opp} Opp")
    if st.session_state.pong_you >= 5:
        result_banner("🏆 You win Pong!", "win")
    elif st.session_state.pong_opp >= 5:
        result_banner("💀 Opponent wins Pong.", "lose")


# ============================================================
# SNAKE DUEL (simplified grid demo)
# ============================================================
def game_snake(mode, difficulty):
    st.subheader("🐍 Snake Duel")
    st.info("Classic snake mechanics — simplified demo version.")
    if "snake_body" not in st.session_state:
        st.session_state.snake_body = [(5, 5)]
        st.session_state.snake_food = (2, 7)
        st.session_state.snake_score = 0
        st.session_state.snake_dir = "R"
    head = st.session_state.snake_body[0]
    food = st.session_state.snake_food
    cols = st.columns(4)
    for c, d in zip(cols, ["⬆️","⬇️","⬅️","➡️"]):
        if c.button(d, key=f"snake_{d}", use_container_width=True):
            st.session_state.snake_dir = d[0]
            st.rerun()
    d = st.session_state.snake_dir
    dr, dc = {"⬆️":(-1,0),"⬇️":(1,0),"⬅️":(0,-1),"➡️":(0,1)}[d]
    new_head = (head[0]+dr, head[1]+dc)
    if new_head == food:
        st.session_state.snake_score += 1
        st.session_state.snake_body.insert(0, new_head)
        st.session_state.snake_food = (random.randint(0,9), random.randint(0,9))
        sfx("win")
    else:
        st.session_state.snake_body = [new_head] + st.session_state.snake_body[:-1]
    if not (0 <= new_head[0] < 10 and 0 <= new_head[1] < 10) or new_head in st.session_state.snake_body[1:]:
        result_banner("💀 Crashed! Game over.", "lose")
        if st.button("🔄 New Snake", key="snake_reset"):
            for k in ["snake_body","snake_food","snake_score","snake_dir"]:
                if k in st.session_state: del st.session_state[k]
            st.rerun()
        return
    st.caption(f"Score: {st.session_state.snake_score} · Head at {head}")
    grid_rows = []
    for r in range(10):
        row = ""
        for c in range(10):
            if (r, c) == new_head: row += "🟢"
            elif (r, c) == food: row += "🍎"
            elif (r, c) in st.session_state.snake_body: row += "🟩"
            else: row += "⬛"
        grid_rows.append(row)
    st.markdown("\n".join(grid_rows))


# ============================================================
# BEYBLADE ARENA
# ============================================================
def game_bey(mode, difficulty):
    st.subheader("🌀 Beyblade Arena")
    st.info("Spin up your blade — highest momentum wins the clash.")
    if "bey_score" not in st.session_state:
        st.session_state.bey_score = 0
        st.session_state.bey_opp = 0
    c1, c2 = st.columns(2)
    if c1.button("🌀 Spin!", use_container_width=True):
        you = random.randint(50, 100) + difficulty * 2
        opp = random.randint(50, 100)
        if you > opp: st.session_state.bey_score += 1; sfx("win")
        else: st.session_state.bey_opp += 1; sfx("lose")
        st.caption(f"Your spin: {you} · Opp: {opp}")
    st.caption(f"You {st.session_state.bey_score} - {st.session_state.bey_opp} Opp")
    if st.session_state.bey_score >= 3:
        result_banner("🏆 You win the clash!", "win")
    elif st.session_state.bey_opp >= 3:
        result_banner("💀 Opponent wins.", "lose")


# ============================================================
# SIMON SAYS
# ============================================================
def game_simon(mode, difficulty):
    st.subheader("🎵 Simon Says")
    COLORS = ["🔴","🟢","🔵","🟡"]
    if "simon_seq" not in st.session_state:
        st.session_state.simon_seq = [random.choice(COLORS)]
        st.session_state.simon_input = []
        st.session_state.simon_score = 0
        st.session_state.simon_show = True
    if st.session_state.simon_show:
        st.markdown(f"Watch: {' '.join(st.session_state.simon_seq)}")
        if st.button("I'm ready"):
            st.session_state.simon_show = False; st.rerun()
        return
    st.caption(f"Your input: {len(st.session_state.simon_input)}/{len(st.session_state.simon_seq)} · Score {st.session_state.simon_score}")
    cols = st.columns(4)
    for i, c in enumerate(COLORS):
        if cols[i].button(c, key=f"simon_{i}", use_container_width=True):
            st.session_state.simon_input.append(c)
            pos = len(st.session_state.simon_input) - 1
            if st.session_state.simon_seq[pos] != c:
                result_banner("💀 Wrong — sequence reset.", "lose")
                st.session_state.simon_seq = [random.choice(COLORS)]
                st.session_state.simon_input = []
                st.session_state.simon_show = True
                sfx("lose"); st.rerun()
            sfx("click")
            if len(st.session_state.simon_input) == len(st.session_state.simon_seq):
                st.session_state.simon_score += 1
                st.session_state.simon_seq.append(random.choice(COLORS))
                st.session_state.simon_input = []
                st.session_state.simon_show = True
                sfx("win"); st.rerun()


# ============================================================
# ROUTER / ENTRY POINT
# ============================================================
def game_router(gid, mode, difficulty):
    """Dispatch to the game by id, and show a Back button."""
    if st.button("⬅️ Back to Home", key="back_btn"):
        st.session_state.page = "home"
        st.rerun()
    st.divider()
    mapping = {
        "ttt": game_ttt, "c4": game_c4, "reversi": game_reversi,
        "chess": game_chess, "nim": game_nim, "memory": game_memory,
        "hangman": game_hangman, "2048": game_2048, "rps": game_rps,
        "guess": game_guess, "dice": game_dice, "coin": game_coin,
        "reaction": game_reaction, "whack": game_whack, "target": game_target,
        "tug": game_tug, "pong": game_pong, "snake": game_snake,
        "bey": game_bey, "simon": game_simon,
    }
    fn = mapping.get(gid)
    if fn:
        fn(mode, difficulty)
    else:
        st.warning(f"Game '{gid}' is not implemented yet.")


def main():
    inject_fx()
    page = st.session_state.page
    if page == "home":
        home_page()
    else:
        settings = st.session_state.settings.get(page, {"mode": "Human", "difficulty": 3})
        game_router(page, settings["mode"], settings["difficulty"])


if __name__ == "__main__":
    main()
