# =========================================================
# APEX PULSE - SMART ATHLETE MONITORING (RULE-BASED EXPERT SYSTEM)
# =========================================================
# FILE MAP (read the file in this order):
#   PART 1  (top)        : Page look + styling (CSS). You can SKIP this in your viva.
#   PART 2  (sidebar)    : Athlete profile inputs (name, age, weight, sport).
#   PART 3  (4 tabs)     : The 50 RULES (C-01 to C-50)  <-- THIS IS THE EXPERT SYSTEM
#   PART 4  (bottom)     : Dashboard that shows the final result.
#
# HOW ONE RULE WORKS:
#   if <CONDITION>:       -> if the athlete's answers match this condition...
#       fire(...)         -> ...save the reason + advice, change the score, raise the risk.
import re
import base64
from pathlib import Path
from PIL import Image
import streamlit as st

# ---------------------------------------------------------
# PART 1. PAGE CONFIGURATION & CUSTOM CSS (look only, skip in viva)
# ---------------------------------------------------------
LOGO_DIR = Path(__file__).parent / "logo"
LOGO_DARK = LOGO_DIR / "transparentlogo-black-theme-cropped.png"  # light logo for dark UI

@st.cache_data(show_spinner=False)
def _b64(path):
    return base64.b64encode(Path(path).read_bytes()).decode()

# --- Glass icon set (inline SVG, replaces emojis) ---
ICONS = {
    "alert":    '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><path d="M12 9v4M12 17h.01"/>',
    "down":     '<path d="M23 18l-9.5-9.5-5 5L1 6"/><path d="M17 18h6v-6"/>',
    "up":       '<path d="M23 6l-9.5 9.5-5-5L1 18"/><path d="M17 6h6v6"/>',
    "check":    '<path d="M20 6L9 17l-5-5"/>',
    "bolt":     '<path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>',
    "moon":     '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>',
    "drop":     '<path d="M12 2.7l5.66 5.65a8 8 0 1 1-11.31 0z"/>',
    "food":     '<path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2M7 2v20M21 15V2a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3zm0 0v7"/>',
    "pulse":    '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
    "dumbbell": '<path d="M6.5 6.5l11 11M21 21l-1-1M3 3l1 1M18 22l4-4M2 6l4-4M3 10l7-7M14 21l7-7"/>',
    "info":     '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>',
}

# leading emoji used in recommendation text -> icon name
EMOJI_TO_ICON = {
    "🚨": "alert", "🛑": "alert", "⚠️": "alert", "📉": "down", "📈": "up", "✅": "check",
    "⚡": "bolt", "🚀": "bolt", "🛌": "moon", "💧": "drop", "🥤": "drop", "🍝": "food",
    "🥩": "food", "🏋️": "dumbbell", "👟": "pulse", "🩹": "pulse", "🧊": "pulse",
}

def gicon(name, size=38):
    """Frosted-glass rounded icon chip."""
    return (f'<span class="gicon" style="width:{size}px;height:{size}px"><svg width="{int(size*0.5)}" height="{int(size*0.5)}" '
            f'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            f'stroke-linejoin="round">{ICONS.get(name, ICONS["info"])}</svg></span>')

def section_head(icon, title, sub):
    st.markdown(f'<div class="sec-head">{gicon(icon)}<div><h3>{title}</h3><p>{sub}</p></div></div>', unsafe_allow_html=True)

def nav_html(risk=None, score=None):
    """Navbar markup. Called once empty (reserves the space, no layout jump) and again with live values."""
    status = ""
    if risk is not None:
        dot = {"Low": "", "Moderate": "amber", "High": "red", "Critical": "red"}.get(risk, "")
        status = f'<span class="pill"><i class="dot {dot}"></i>Risk: {risk}</span><span class="pill">Readiness {score}%</span>'
    logo_img = f'<img src="data:image/png;base64,{_b64(TAB_LOGO)}">' if TAB_LOGO.exists() else gicon("pulse", 30)
    return (f'<div class="navbar"><div class="nav-brand">{logo_img}Apex <span>Pulse</span></div>'
            f'<div class="nav-links"><a href="#modules">Inputs</a><a href="#dashboard">Results</a></div>'
            f'<div class="nav-status">{status}</div></div>')

TAB_LOGO = LOGO_DIR / "main-tabbar-logo.png"

@st.cache_resource(show_spinner=False)
def _cropped(path):
    """Trim transparent padding so the browser-tab icon fills the favicon."""
    if not Path(path).exists():
        return "⚡"
    im = Image.open(path).convert("RGBA")
    box = im.split()[3].getbbox()
    return im.crop(box) if box else im

st.set_page_config(
    page_title="Apex Pulse | Smart Athlete Monitoring",
    page_icon=_cropped(TAB_LOGO),
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --glass: rgba(255,255,255,0.05);
        --glass-strong: rgba(255,255,255,0.08);
        --border: rgba(255,255,255,0.12);
        --text: #e8ecf4;
        --muted: #8b95a9;
        --accent: #34d399;
        --accent2: #60a5fa;
    }

    html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif !important; color: var(--text); }

    /* Background with soft glowing orbs */
    .stApp {
        background:
            radial-gradient(600px circle at 8% 10%, rgba(52,211,153,0.18), transparent 60%),
            radial-gradient(700px circle at 92% 18%, rgba(96,165,250,0.18), transparent 60%),
            radial-gradient(800px circle at 50% 100%, rgba(167,139,250,0.14), transparent 60%),
            #090d16;
        background-attachment: fixed;
    }
    /* Keep Streamlit's running-athlete status icon (top right); only hide deploy button, menu & footer */
    header[data-testid="stHeader"] { background: transparent !important; }
    .stAppDeployButton, #MainMenu, footer { display: none !important; }
    .block-container { padding-top: 4rem; max-width: 1280px; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(255,255,255,0.03);
        backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
        border-right: 1px solid var(--border);
    }
    section[data-testid="stSidebar"] h2 { font-size: 1.05rem; font-weight: 600; letter-spacing: .02em; color: #fff !important; }

    /* Typography */
    h1, h2, h3 { font-weight: 600 !important; letter-spacing: -0.01em; }
    h3 { font-size: 1.1rem !important; color: var(--text); }
    label, .stMarkdown p, [data-testid="stWidgetLabel"] p { color: var(--muted) !important; font-size: .85rem !important; font-weight: 500; }
    hr { border-color: var(--border) !important; }

    /* Inputs (force dark glass background & high-contrast light text) */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    div[data-baseweb="base-input"],
    div[data-testid="stNumberInput"] input,
    div[data-testid="stTextInput"] input {
        background: #131b2e !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        color: var(--text) !important;
        -webkit-text-fill-color: var(--text) !important;
    }
    div[data-baseweb="select"] > div:hover, div[data-baseweb="input"] > div:hover { border-color: rgba(52,211,153,.5) !important; }
    div[data-baseweb="slider"] div[role="slider"] { background: var(--accent) !important; box-shadow: 0 0 0 4px rgba(52,211,153,.2); }

    /* Tabs as glass pills */
    div[data-baseweb="tab-list"] {
        gap: 6px; background: var(--glass); border: 1px solid var(--border);
        padding: 6px; border-radius: 16px; backdrop-filter: blur(20px);
    }
    button[data-baseweb="tab"] {
        border-radius: 11px !important; padding: 8px 18px !important;
        color: var(--muted) !important; font-weight: 500; transition: all .25s ease;
    }
    button[data-baseweb="tab"]:hover { color: var(--text) !important; background: var(--glass); }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, rgba(52,211,153,.22), rgba(96,165,250,.22)) !important;
        color: #fff !important; border: 1px solid var(--border) !important;
    }
    div[data-baseweb="tab-highlight"], div[data-baseweb="tab-border"] { display: none; }

    /* Hero */
    .hero {
        display: flex; align-items: center; gap: 18px;
        background: var(--glass); border: 1px solid var(--border);
        backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
        border-radius: 24px; padding: 22px 28px; margin-bottom: 18px;
        box-shadow: 0 10px 40px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.08);
    }
    .hero h1 { margin: 0; font-size: 1.55rem; color: #fff; }
    .hero h1 span { background: linear-gradient(90deg,#34d399,#60a5fa); -webkit-background-clip: text; background-clip: text; color: transparent; }
    .hero p { margin: 4px 0 0; color: var(--muted); font-size: .9rem; }
    .chips { margin-left: auto; display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }
    .chip {
        padding: 6px 12px; border-radius: 999px; font-size: .75rem; color: var(--text);
        background: var(--glass-strong); border: 1px solid var(--border);
    }

    /* Metrics */
    div[data-testid="stMetric"] {
        background: var(--glass); border: 1px solid var(--border);
        backdrop-filter: blur(20px); border-radius: 18px; padding: 18px 20px;
        box-shadow: 0 6px 24px rgba(0,0,0,.25); transition: transform .25s ease, border-color .25s ease;
    }
    div[data-testid="stMetric"]:hover { transform: translateY(-3px); border-color: rgba(52,211,153,.45); }
    div[data-testid="stMetricValue"] { font-weight: 700; color: #fff; }
    div[data-testid="stMetricLabel"] p { text-transform: uppercase; letter-spacing: .08em; font-size: .7rem !important; }

    /* Progress */
    div[data-testid="stProgress"] > div > div { background: var(--glass-strong) !important; border-radius: 99px; }
    div[data-testid="stProgress"] > div > div > div { background: linear-gradient(90deg,#34d399,#60a5fa) !important; border-radius: 99px; }

    /* Section label */
    .section-title { font-size: .72rem; text-transform: uppercase; letter-spacing: .14em; color: var(--muted); margin: 18px 0 12px; font-weight: 600; }

    /* Recommendation cards */
    .rec-card {
        background: var(--glass); border: 1px solid var(--border);
        backdrop-filter: blur(18px); border-radius: 16px;
        padding: 14px 18px; margin-bottom: 12px; font-size: .92rem; line-height: 1.55;
        border-left: 3px solid var(--accent2); transition: transform .2s ease, background .2s ease;
    }
    .rec-card:hover { transform: translateX(4px); background: var(--glass-strong); }
    .rec-card b { color: #fff; }
    .rec-red   { border-left-color: #f87171; }
    .rec-amber { border-left-color: #fbbf24; }
    .rec-green { border-left-color: #34d399; }

    /* Rule trace cards */
    .rule-card {
        background: var(--glass); border: 1px solid var(--border);
        backdrop-filter: blur(18px); border-radius: 14px;
        padding: 12px 16px; margin-bottom: 10px; font-size: .85rem; color: var(--text);
    }
    .rule-badge {
        background: linear-gradient(135deg, rgba(52,211,153,.25), rgba(96,165,250,.25));
        border: 1px solid var(--border); color: #fff;
        padding: 2px 9px; border-radius: 8px; font-size: .72rem; font-weight: 600; margin-right: 8px;
    }

    /* Navbar */
    .navbar {
        display: flex; align-items: center; gap: 14px;
        background: var(--glass); border: 1px solid var(--border);
        backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
        border-radius: 18px; padding: 10px 18px; margin-bottom: 16px;
        box-shadow: 0 8px 30px rgba(0,0,0,.3), inset 0 1px 0 rgba(255,255,255,.08);
    }
    .nav-brand { display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 1.05rem; color: #fff; letter-spacing: -.01em; }
    .nav-brand img { height: 34px; width: auto; }
    .nav-brand span { color: #2bff00; }
    .nav-links { display: flex; gap: 4px; margin-left: 28px; }
    .nav-links a {
        color: var(--muted) !important; text-decoration: none !important; font-size: .85rem; font-weight: 500;
        padding: 7px 14px; border-radius: 10px; transition: all .2s ease;
    }
    .nav-links a:hover { color: #fff !important; background: var(--glass-strong); }
    .nav-status { margin-left: auto; display: flex; gap: 8px; }
    .pill {
        display: inline-flex; align-items: center; gap: 7px; padding: 6px 13px; border-radius: 999px;
        font-size: .75rem; font-weight: 500; color: var(--text);
        background: var(--glass-strong); border: 1px solid var(--border);
    }
    .dot { width: 8px; height: 8px; border-radius: 50%; background: #34d399; box-shadow: 0 0 10px currentColor; color: #34d399; }
    .dot.amber { background: #fbbf24; color: #fbbf24; }
    .dot.red { background: #f87171; color: #f87171; }
    html { scroll-behavior: smooth; }

    /* Glass icon chip (replaces emojis) */
    .gicon {
        display: inline-grid; place-items: center; flex-shrink: 0; border-radius: 12px; color: #2bff00;
        background: linear-gradient(135deg, rgba(255,255,255,.14), rgba(255,255,255,.04));
        border: 1px solid var(--border); box-shadow: inset 0 1px 0 rgba(255,255,255,.18), 0 4px 14px rgba(0,0,0,.25);
    }
    .sec-head { display: flex; align-items: center; gap: 14px; margin: 18px 0 14px; }
    .sec-head h3 { margin: 0; font-size: 1.05rem !important; color: #fff; }
    .sec-head p { margin: 2px 0 0; color: var(--muted); font-size: .82rem; }

    /* Recommendation card with icon; lighter blur = smoother reruns */
    .rec-card { display: flex; gap: 14px; align-items: flex-start; backdrop-filter: none !important; background: rgba(255,255,255,.06) !important; }
    .rec-card .gicon { margin-top: 1px; }
    .rec-red .gicon { color: #f87171; } .rec-amber .gicon { color: #fbbf24; } .rec-green .gicon { color: #34d399; }
    .rule-card { backdrop-filter: none !important; background: rgba(255,255,255,.06) !important; }
    .legend { display: flex; gap: 14px; flex-wrap: wrap; color: var(--muted); font-size: .78rem; margin: 4px 0 18px; }
    .legend i { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
    .steps { color: var(--muted); font-size: .82rem; line-height: 1.9; }
    .steps b { color: #fff; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# PART 2. SIDEBAR: ATHLETE PROFILE INPUTS
# ---------------------------------------------------------
with st.sidebar:
    if LOGO_DARK.exists():
        st.markdown(f'<img src="data:image/png;base64,{_b64(LOGO_DARK)}" style="width:100%;max-width:240px;display:block;margin:-10px auto 6px;">', unsafe_allow_html=True)
    st.markdown("## Athlete Profile")
    athlete_name = st.text_input("Athlete Name", value="Ali Khan")
    age = st.slider("Age", 15, 45, 22)
    weight = st.number_input("Weight (kg)", 40.0, 130.0, 72.0, step=0.5)
    sport_type = st.selectbox(
        "Primary Sport Category",
        ["Sprint / Power (100m, Jumping)", "Team Sport (Football, Cricket, Basketball)", "Endurance (Marathon, Cycling)"]
    )
    st.divider()
    st.markdown('<div class="steps"><b>How to use:</b><br><b>1.</b> Fill your profile here<br><b>2.</b> Answer the 4 checks in the tabs<br><b>3.</b> Read your advice below</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# NAVBAR (filled after the rules run) + HEADER BANNER
# ---------------------------------------------------------
navbar_slot = st.empty()
navbar_slot.markdown(nav_html(), unsafe_allow_html=True)
st.markdown(f"""<div class="hero">
<div><h1>Hi, <span>{athlete_name}</span></h1>
<p>Answer the four quick checks below and get your personal training advice.</p></div>
<div class="chips"><span class="chip">{age} yrs</span><span class="chip">{weight} kg</span><span class="chip">{sport_type.split(' (')[0]}</span></div>
</div>""", unsafe_allow_html=True)

# =========================================================
# PART 3. EXPERT SYSTEM CORE: MEMORY + HELPERS
# =========================================================
# Working memory: these are filled in by the rules below
triggered_rules = []      # which rules matched (shown in "Why you got this advice")
recommendations = []      # advice for the athlete (shown in "What to do")
risk_level = "Low"        # starts Low, rules can only push it UP
readiness_score = 85      # starts at 85%, rules push it up or down

RISK_ORDER = {"Low": 0, "Moderate": 1, "High": 2, "Critical": 3}

def escalate_risk(current_risk, new_risk):
    """Risk can only go UP (Low -> Moderate -> High -> Critical), never down."""
    return new_risk if RISK_ORDER[new_risk] > RISK_ORDER[current_risk] else current_risk

def fire(rule_id, reason, advice, score_change=0, risk=None):
    """Called when a rule matches: save the reason, save the advice, change the score, raise the risk."""
    global readiness_score, risk_level
    triggered_rules.append((rule_id, reason))
    recommendations.append(advice)
    readiness_score += score_change
    if risk:
        risk_level = escalate_risk(risk_level, risk)

# ---------------------------------------------------------
# 4 TABS = 4 EXPERT MODULES
# ---------------------------------------------------------
st.markdown('<div id="modules"></div>', unsafe_allow_html=True)
tab1, tab2, tab3, tab4 = st.tabs([
    ":material/personal_injury: Injury Check",
    ":material/bedtime: Recovery",
    ":material/water_drop: Nutrition",
    ":material/directions_run: Performance"
])

# =========================================================
# TAB 1: INJURY CHECK  ->  Rules C-01 to C-15
# =========================================================
with tab1:
    section_head("pulse", "Injury Check", "Tell us where it hurts and how it feels.")
    col1, col2 = st.columns(2)

    with col1:
        pain_site = st.selectbox("Pain Location", ["None", "Knee", "Ankle", "Hamstring", "Shoulder", "Lower Back"])
        pain_severity = st.slider("Pain Score (0 = No Pain, 10 = Extreme)", 0, 10, 0)
        heard_pop = st.checkbox("Heard a 'Pop' or 'Snap' when injured?")
        headache_dizzy = st.checkbox("Headache or dizziness after a hit?")

    with col2:
        swelling = st.selectbox("Swelling Timing", ["No Swelling", "Immediate (< 2 hours)", "Delayed (Next day)"])
        weight_bearing = st.radio("Can Bear Weight / Move Joint Freely?", ["Yes, Fully", "Partial / Limping", "No, Unable"])
        feeling_sick = st.checkbox("Fever or feeling sick today?")

    # True as soon as the user selects anything in Tab 1 (Injury Check)
    tab1_used = (
        pain_site != "None"
        or pain_severity > 0
        or heard_pop
        or headache_dizzy
        or swelling != "No Swelling"
        or weight_bearing != "Yes, Fully"
        or feeling_sick
    )

    # ===== KNEE RULES (C-01 to C-04): covers ALL Knee combinations (Mild -> Moderate -> High -> Critical) =====

    # C-01 (Critical): Knee + (Pop with swelling/limping, OR Immediate swelling + cannot bear weight, OR extreme pain >= 8)
    if pain_site == "Knee" and (
        (heard_pop and (swelling != "No Swelling" or weight_bearing != "Yes, Fully"))
        or (swelling == "Immediate (< 2 hours)" and weight_bearing == "No, Unable")
        or pain_severity >= 8
    ):   # CONDITION (if this is true)
        fire(
            "C-01",                                                                                   # Rule ID
            f"You said: Knee pain ({pain_severity}/10) + {swelling} + Bear weight: {weight_bearing}{' + Pop sound' if heard_pop else ''}. This may be a serious knee ligament injury (ACL).",  # Why (shown to user)
            "🚨 **See a doctor today:** Get an MRI scan. Wear a knee brace and do NOT stand or walk on it.",  # Advice (shown to user)
            -60,                                                                                      # Readiness change (-60 = lower by 60)
            "Critical"                                                                                # Risk level
        )

    # C-02 (High): Knee + (Cannot bear weight, OR Immediate swelling, OR Pop sound, OR high pain >= 6)
    elif pain_site == "Knee" and (
        weight_bearing == "No, Unable"
        or swelling == "Immediate (< 2 hours)"
        or heard_pop
        or pain_severity >= 6
    ):   # CONDITION
        fire(
            "C-02",                                                                                   # Rule ID
            f"You said: Knee pain ({pain_severity}/10) + {swelling} + Bear weight: {weight_bearing}. This is a serious knee injury.", # Why
            "🛑 **Stop training:** Rest the knee and see a physio or doctor before you exercise again.",  # Advice
            -40,                                                                                      # Readiness change
            "High"                                                                                    # Risk level
        )

    # C-03 (Moderate - Overload): Knee + (Delayed swelling, OR Partial/Limping, OR moderate pain >= 4)
    elif pain_site == "Knee" and (
        swelling == "Delayed (Next day)"
        or weight_bearing == "Partial / Limping"
        or pain_severity >= 4
    ):   # CONDITION
        fire(
            "C-03",                                                                                   # Rule ID
            f"You said: Knee pain ({pain_severity}/10) + {swelling} + Bear weight: {weight_bearing}. Your knee joint is overloaded.",  # Why
            "⚠️ **Go easy on the knee:** No deep squats or jumping for 7 days. Do simple thigh (quad) holds instead.",  # Advice
            -25,                                                                                      # Readiness change
            "Moderate"                                                                                # Risk level
        )

    # C-04 (Mild): Any remaining Knee case (No swelling + Full weight bearing + mild pain 0-3)
    elif pain_site == "Knee":   # CONDITION
        fire(
            "C-04",                                                                                   # Rule ID
            f"You said: Knee selected with mild pain ({pain_severity}/10), no swelling, and full movement. This is a mild knee strain.",  # Why
            "⚠️ **Reduce knee load:** Do half of your normal running and jumping. Rest if the pain increases.",  # Advice
            -15,                                                                                      # Readiness change
            "Moderate"                                                                                # Risk level
        )

    # ===== ANKLE RULES (C-05 to C-07): covers ALL Ankle combinations =====

    # C-05 (Critical): Ankle + (Cannot bear weight, OR Immediate swelling + high pain, OR Pop sound, OR pain >= 7)
    if pain_site == "Ankle" and (
        weight_bearing == "No, Unable"
        or (swelling == "Immediate (< 2 hours)" and pain_severity >= 5)
        or heard_pop
        or pain_severity >= 7
    ):   # CONDITION
        fire(
            "C-05",                                                                                   # Rule ID
            f"You said: Ankle pain ({pain_severity}/10) + {swelling} + Bear weight: {weight_bearing}. The bone may be broken or severely sprained.",  # Why
            "🚨 **Get an X-ray:** Rest, ice and keep the ankle raised. A doctor must check for a fracture.",  # Advice
            -55,                                                                                      # Readiness change
            "Critical"                                                                                # Risk level
        )

    # C-06 (Moderate - Sprain): Ankle + (Limping, OR any swelling, OR pain >= 4)
    elif pain_site == "Ankle" and (
        weight_bearing == "Partial / Limping"
        or swelling != "No Swelling"
        or pain_severity >= 4
    ):   # CONDITION
        fire(
            "C-06",                                                                                   # Rule ID
            f"You said: Ankle pain ({pain_severity}/10) + {swelling} + Bear weight: {weight_bearing}. This looks like an ankle sprain.",  # Why
            "🩹 **Ankle care:** Use a compression wrap and do balance exercises before you run again.",  # Advice
            -30,                                                                                      # Readiness change
            "Moderate"                                                                                # Risk level
        )

    # C-07 (Mild): Any remaining Ankle case (No swelling + Full weight bearing + mild pain 0-3)
    elif pain_site == "Ankle":   # CONDITION
        fire(
            "C-07",                                                                                   # Rule ID
            f"You said: Ankle selected with mild pain ({pain_severity}/10). This is a mild ankle strain.",  # Why
            "⚠️ **Protect the ankle:** Use tape or a brace and avoid sharp turns today.",             # Advice
            -15,                                                                                      # Readiness change
            "Moderate"                                                                                # Risk level
        )

    # ===== HAMSTRING RULES (C-08, C-09): covers ALL Hamstring combinations =====

    # C-08 (High): Hamstring + ('pop' sound, OR cannot bear weight, OR swelling, OR pain >= 6)
    if pain_site == "Hamstring" and (
        heard_pop
        or weight_bearing == "No, Unable"
        or swelling != "No Swelling"
        or pain_severity >= 6
    ):   # CONDITION
        fire(
            "C-08",                                                                                   # Rule ID
            f"You said: Hamstring pain ({pain_severity}/10) + {swelling} + Bear weight: {weight_bearing}{' + Pop sound' if heard_pop else ''}. The muscle may be torn.",  # Why
            "🛑 **No sprinting:** Do not run fast for 3-4 weeks. Start gentle bridge exercises after 3 days.",  # Advice
            -45,                                                                                      # Readiness change
            "High"                                                                                    # Risk level
        )

    # C-09 (Moderate): Any remaining Hamstring case
    elif pain_site == "Hamstring":   # CONDITION
        fire(
            "C-09",                                                                                   # Rule ID
            f"You said: Hamstring pain ({pain_severity}/10) + Bear weight: {weight_bearing}. This is a mild muscle strain.",  # Why
            "⚠️ **Light work only:** No sprints for a week. Do easy stretching and hamstring bridges.",  # Advice
            -20,                                                                                      # Readiness change
            "Moderate"                                                                                # Risk level
        )

    # ===== SHOULDER and LOWER BACK RULES (C-10, C-11): covers ALL Shoulder & Back combinations =====

    # C-10: Shoulder selected
    if pain_site == "Shoulder":   # CONDITION
        severe_shoulder = (pain_severity >= 6 or weight_bearing != "Yes, Fully" or swelling != "No Swelling" or heard_pop)
        fire(
            "C-10",                                                                                   # Rule ID
            f"You said: Shoulder pain ({pain_severity}/10) + {swelling} + Move freely: {weight_bearing}. Your shoulder is strained.",  # Why
            "⚠️ **Rest the shoulder:** No lifting overhead and no throwing. See a physio if the pain stays.",  # Advice
            -35 if severe_shoulder else -20,                                                          # Readiness change
            "High" if severe_shoulder else "Moderate"                                                 # Risk level
        )

    # C-11: Lower Back selected
    if pain_site == "Lower Back":   # CONDITION
        severe_back = (pain_severity >= 6 or weight_bearing != "Yes, Fully" or swelling != "No Swelling" or heard_pop)
        fire(
            "C-11",                                                                                   # Rule ID
            f"You said: Lower back pain ({pain_severity}/10) + {swelling} + Move freely: {weight_bearing}. Your back is strained.",  # Why
            "⚠️ **Protect the back:** No heavy squats or deadlifts. Do gentle core and stretching work.",  # Advice
            -35 if severe_back else -20,                                                              # Readiness change
            "High" if severe_back else "Moderate"                                                     # Risk level
        )

    # ===== GENERAL HEALTH RULES (C-12 to C-15) =====

    # C-12: Headache or dizziness after a hit
    if headache_dizzy:   # CONDITION
        fire(
            "C-12",                                                                                   # Rule ID
            "You said: headache or dizziness after a hit. This could be a concussion (head injury).", # Why
            "🚨 **Stop playing now:** Do not play again until a doctor says it is safe.",             # Advice
            -50,                                                                                      # Readiness change
            "Critical"                                                                                # Risk level
        )

    # C-13: Fever or feeling sick
    if feeling_sick:   # CONDITION
        fire(
            "C-13",                                                                                   # Rule ID
            "You said: you have a fever or feel sick. Your body is fighting an illness.",             # Why
            "🛑 **Rest today:** Skip hard training and drink plenty of fluids until you feel normal.",  # Advice
            -25,                                                                                      # Readiness change
            "High"                                                                                    # Risk level
        )

    # C-14: Pain, swelling, pop, or limping selected, but Pain Location is still "None"
    if pain_site == "None" and (pain_severity >= 3 or swelling != "No Swelling" or weight_bearing != "Yes, Fully" or heard_pop):   # CONDITION
        fire(
            "C-14",                                                                                   # Rule ID
            "You said: you have pain, swelling, or trouble moving, but Pain Location is still set to 'None'.",  # Why
            "⚠️ **Pick the Pain Location:** Choose where it hurts above, or train lightly until the pain settles.",  # Advice
            -15,                                                                                      # Readiness change
            "Moderate"                                                                                # Risk level
        )

    # C-15: No pain, no swelling, moves freely = no injury
    if (pain_site == "None" and pain_severity <= 2 and swelling == "No Swelling"
            and weight_bearing == "Yes, Fully" and not heard_pop and not headache_dizzy and not feeling_sick):   # CONDITION
        fire(
            "C-15",                                                                                   # Rule ID
            "You said: no pain, no swelling and you can move freely. No injury found.",               # Why
            "✅ **No injury found:** You can train normally.",                                         # Advice
            0,                                                                                        # Readiness change (no change)
            None                                                                                      # Risk level (no change)
        )

    # Track whether the athlete has any injury/illness so Tab 2 does not give contradictory "train hard" advice
    has_injury = not (
        pain_site == "None" and pain_severity <= 2 and swelling == "No Swelling"
        and weight_bearing == "Yes, Fully" and not heard_pop and not headache_dizzy and not feeling_sick
    )

# =========================================================
# TAB 2: RECOVERY  ->  Rules C-16 to C-30
# =========================================================
with tab2:
    section_head("moon", "Recovery", "Sleep, heart rate and training load show how tired you are.")
    c1, c2 = st.columns(2)

    with c1:
        sleep_hours = st.slider("Average Sleep Last 3 Nights (Hours)", 3.0, 10.0, 7.5, 0.5)
        rhr_delta = st.slider("Resting Heart Rate Elevation above Baseline (bpm)", 0, 20, 3)

    with c2:
        weekly_load_spike = st.slider("Weekly Training Load Increase (%)", 0, 60, 10)
        doms_level = st.select_slider("Muscle Soreness / DOMS", options=["Low", "Moderate", "Severe"])

    # Only run Recovery rules when the user actually changes an input in this tab
    tab2_used = (sleep_hours != 7.5 or rhr_delta != 3 or weekly_load_spike != 10 or doms_level != "Low")
    if tab2_used:
        # ===== SLEEP RULES (C-16 to C-19) =====

        # C-16: Sleep under 6 hours + heart rate 7 or more above normal
        if sleep_hours < 6.0 and rhr_delta >= 7:   # CONDITION
            fire(
                "C-16",                                                                                   # Rule ID
                "You said: sleep under 6 hours + heart rate 7 or more above normal. Your body is very tired.",  # Why
                "🛌 **Take a rest day:** Skip hard training. Do 20 minutes of light stretching and sleep 9 hours.",  # Advice
                -20,                                                                                      # Readiness change
                "High"                                                                                    # Risk level
            )

        # C-17: Sleep 8 hours or more + normal heart rate (only when not injured)
        if not has_injury and sleep_hours >= 8.0 and rhr_delta <= 3:   # CONDITION
            fire(
                "C-17",                                                                                   # Rule ID
                "You said: sleep 8 hours or more + normal heart rate. You are fully rested.",             # Why
                "⚡ **You are fully rested:** Your body is ready for fast running or heavy lifting today.",  # Advice
                10,                                                                                       # Readiness change (+10 = raise by 10)
                None                                                                                      # Risk level (no change)
            )

        # C-18: Sleep under 5 hours
        if sleep_hours < 5.0:   # CONDITION
            fire(
                "C-18",                                                                                   # Rule ID
                "You said: sleep under 5 hours. Very low sleep makes you slow and more likely to make mistakes.",  # Why
                "⚠️ **Avoid tricky drills:** Skip contact and skill drills today. You are more likely to make mistakes.",  # Advice
                -15,                                                                                      # Readiness change
                "High"                                                                                    # Risk level
            )

        # C-19: Sleep between 5 and 7 hours
        elif sleep_hours < 7.0:   # CONDITION
            fire(
                "C-19",                                                                                   # Rule ID
                f"You said: sleep is {sleep_hours} hours (under 7 hours). This is below the 7-8 hours athletes need.",  # Why
                "⚠️ **Sleep more tonight:** Try for 8 hours and keep today's training light.",            # Advice
                -10,                                                                                      # Readiness change
                "Moderate"                                                                                # Risk level
            )

        # ===== HEART RATE RULES (C-20, C-21) =====

        # C-20: Heart rate 10 or more above normal
        if rhr_delta >= 10:   # CONDITION
            fire(
                "C-20",                                                                                   # Rule ID
                "You said: heart rate 10 or more above normal. Your body is under stress.",               # Why
                "🛑 **Take it easy:** A very high resting heart rate means you need rest, or you may be getting sick.",  # Advice
                -15,                                                                                      # Readiness change
                "High"                                                                                    # Risk level
            )

        # C-21: Heart rate 4 to 9 above normal
        elif rhr_delta >= 4:   # CONDITION
            fire(
                "C-21",                                                                                   # Rule ID
                f"You said: heart rate is +{rhr_delta} bpm above normal. You are a little tired.",        # Why
                "⚠️ **Keep training light:** Do an easy session and drink more water.",                   # Advice
                -10,                                                                                      # Readiness change
                "Moderate"                                                                                # Risk level
            )

        # ===== TRAINING LOAD RULES (C-22 to C-25): only ONE of these can match =====

        # C-22: Training up more than 20% + very sore muscles
        if weekly_load_spike > 20 and doms_level == "Severe":   # CONDITION
            fire(
                "C-22",                                                                                   # Rule ID
                "You said: training up more than 20% this week + very sore muscles. High chance of injury.",  # Why
                "📉 **Cut training by 40%:** You increased training too fast and your muscles are very sore.",  # Advice
                -25,                                                                                      # Readiness change
                "High"                                                                                    # Risk level
            )

        # C-23: Training up more than 35%
        elif weekly_load_spike > 35:   # CONDITION
            fire(
                "C-23",                                                                                   # Rule ID
                "You said: training up more than 35% this week. That is too much, too fast.",             # Why
                "📉 **Reduce your training:** Such a big jump in one week is risky. Do fewer or shorter sessions.",  # Advice
                -25,                                                                                      # Readiness change
                "High"                                                                                    # Risk level
            )

        # C-24: Training up between 11% and 35%
        elif weekly_load_spike > 10:   # CONDITION
            fire(
                "C-24",                                                                                   # Rule ID
                f"You said: training up {weekly_load_spike}% this week (above the safe 10% limit).",      # Why
                "⚠️ **Slow down:** Increase your training by only 10% per week.",                         # Advice
                -15,                                                                                      # Readiness change
                "Moderate"                                                                                # Risk level
            )

        # C-25: Training up 10% or less + low soreness (only when not injured and rested)
        elif not has_injury and sleep_hours >= 7.0 and rhr_delta <= 3 and weekly_load_spike <= 10 and doms_level == "Low":   # CONDITION
            fire(
                "C-25",                                                                                   # Rule ID
                "You said: training up 10% or less + low soreness. Your training is steady and safe.",    # Why
                "📈 **Safe to progress:** You can add 5-10% more training this week.",                    # Advice
                0,                                                                                        # Readiness change (no change)
                None                                                                                      # Risk level (no change)
            )

        # ===== SORENESS, AGE and OVERALL RECOVERY RULES (C-26 to C-30) =====

        # C-26: Moderate or Severe muscle soreness
        if doms_level in ["Moderate", "Severe"]:   # CONDITION
            fire(
                "C-26",                                                                                   # Rule ID
                f"You said: muscle soreness is {doms_level}. Your muscles need time to repair.",          # Why
                "🧊 **Recover well:** Do light walking and stretching, drink water and avoid heavy lifting.",  # Advice
                -15 if doms_level == "Severe" else -10,                                                   # Readiness change
                "Moderate"                                                                                # Risk level
            )

        # C-27: Age over 32 + sore muscles
        if age > 32 and doms_level in ["Moderate", "Severe"]:   # CONDITION
            fire(
                "C-27",                                                                                   # Rule ID
                "You said: age over 32 + sore muscles. Older athletes recover more slowly.",              # Why
                "🧊 **Take extra recovery:** Keep 2 days between hard sessions. A warm or cold shower can help.",  # Advice
                -10,                                                                                      # Readiness change
                "Moderate"                                                                                # Risk level
            )

        # C-28: Age 18 or under + training up more than 15%
        if age <= 18 and weekly_load_spike > 15:   # CONDITION
            fire(
                "C-28",                                                                                   # Rule ID
                "You said: age 18 or under + training up more than 15%. Young bodies get injured easily.",  # Why
                "⚠️ **Increase slowly:** Add training slowly to protect your growing body.",              # Advice
                -10,                                                                                      # Readiness change
                "Moderate"                                                                                # Risk level
            )

        # C-29: Low sleep + sore muscles
        if sleep_hours < 6.5 and doms_level in ["Moderate", "Severe"]:   # CONDITION
            fire(
                "C-29",                                                                                   # Rule ID
                "You said: low sleep + sore muscles. Your body is not recovering well.",                  # Why
                "⚠️ **Fix your sleep first:** Low sleep with sore muscles raises injury risk. Rest more.",  # Advice
                -10,                                                                                      # Readiness change
                "Moderate"                                                                                # Risk level
            )

        # C-30: Good sleep + normal heart rate + low soreness + steady training (only when not injured)
        if not has_injury and sleep_hours >= 7.5 and rhr_delta <= 3 and doms_level == "Low" and weekly_load_spike <= 10:   # CONDITION
            fire(
                "C-30",                                                                                   # Rule ID
                "You said: good sleep + normal heart rate + low soreness + steady training. You are fully recovered.",  # Why
                "✅ **Recovery looks great:** Your body is ready for a good session.",                    # Advice
                5,                                                                                        # Readiness change (+5)
                None                                                                                      # Risk level (no change)
            )

# =========================================================
# TAB 3: NUTRITION  ->  Rules C-31 to C-40
# =========================================================
with tab3:
    section_head("drop", "Nutrition & Water", "Check if you are drinking and eating enough for your session.")
    n1, n2 = st.columns(2)

    with n1:
        session_mins = st.slider("Training Session Duration (Minutes)", 30, 180, 75, 15)
        temp_c = st.slider("Ambient Temperature (°C)", 10, 45, 32)

    with n2:
        sweat_loss_kg = st.number_input("Weight Lost After Session (kg)", 0.0, 5.0, 0.5, step=0.1)
        urine_color = st.selectbox("Urine Hydration Scale (1-8)", ["1-2 (Pale/Optimal)", "3-4 (Light Yellow/Mild Dehydration)", "5-8 (Dark/Severe Dehydration)"])

    sweat_pct = (sweat_loss_kg / weight) * 100                # % of body weight lost as sweat
    water_to_drink = max(1.0, sweat_loss_kg * 1.5)            # liters to drink back

    # Only run Nutrition rules when the user actually changes an input in this tab
    tab3_used = (session_mins != 75 or temp_c != 32 or sweat_loss_kg != 0.5 or urine_color != "1-2 (Pale/Optimal)")
    if tab3_used:
        # ===== WATER RULES (C-31 to C-34): only ONE of these can match =====

        # C-31: Lost 3% or more of body weight
        if sweat_pct >= 3.0:   # CONDITION
            fire(
                "C-31",                                                                                   # Rule ID
                f"You said: you lost {sweat_pct:.1f}% of your body weight as sweat (3% or more). You are very dehydrated.",  # Why
                f"💧 **Drink a lot now:** Drink {water_to_drink:.2f} Liters of water with a little salt over the next 3 hours.",  # Advice
                -20,                                                                                      # Readiness change
                "High"                                                                                    # Risk level
            )

        # C-32: Lost 2% or more of body weight, or very dark urine
        elif sweat_pct >= 2.0 or urine_color == "5-8 (Dark/Severe Dehydration)":   # CONDITION
            fire(
                "C-32",                                                                                   # Rule ID
                f"You said: you lost {sweat_pct:.1f}% of your body weight (2% or more) or your urine is dark. You are dehydrated.",  # Why
                f"💧 **Drink more water:** Drink {water_to_drink:.2f} Liters of fluid with a little salt over the next 3 hours.",  # Advice
                -15,                                                                                      # Readiness change
                "Moderate"                                                                                # Risk level
            )

        # C-33: Lost 1% or more of body weight, or light-yellow urine
        elif sweat_pct >= 1.0 or urine_color == "3-4 (Light Yellow/Mild Dehydration)":   # CONDITION
            fire(
                "C-33",                                                                                   # Rule ID
                f"You said: you lost {sweat_pct:.1f}% of your body weight (1% or more) or your urine is light yellow. You are slightly dehydrated.",  # Why
                "🥤 **Drink a bit more:** Have 500 ml of water after your session.",                      # Advice
                -5,                                                                                       # Readiness change
                None                                                                                      # Risk level (no change)
            )

        # C-34: Little sweat loss + pale urine
        else:   # CONDITION (none of the above matched)
            fire(
                "C-34",                                                                                   # Rule ID
                "You said: little sweat loss + pale urine. You are well hydrated.",                       # Why
                "🥤 **Water is fine:** Keep drinking your normal water every day (about 35-45 ml per kg of body weight).",  # Advice
                0,                                                                                        # Readiness change (no change)
                None                                                                                      # Risk level (no change)
            )

        # ===== HEAT and COLD RULES (C-35, C-36) =====

        # C-35: Hot weather + session of 60 minutes or more
        if temp_c >= 35 and session_mins >= 60:   # CONDITION
            fire(
                "C-35",                                                                                   # Rule ID
                f"You said: temperature {temp_c}°C (35°C or more) + session of 60 minutes or more. Hot weather is dangerous.",  # Why
                "⚠️ **Beware of the heat:** Train in shade, take water breaks every 15 minutes and stop if you feel dizzy.",  # Advice
                -10,                                                                                      # Readiness change
                "Moderate"                                                                                # Risk level
            )

        # C-36: Cold weather
        if temp_c <= 15:   # CONDITION
            fire(
                "C-36",                                                                                   # Rule ID
                f"You said: temperature {temp_c}°C (15 or less). It is cold weather.",                    # Why
                "🩹 **Warm up longer:** Cold muscles get injured easily. Warm up for 15 extra minutes.",  # Advice
                0,                                                                                        # Readiness change (no change)
                None                                                                                      # Risk level (no change)
            )

        # ===== FOOD RULES BY SPORT (C-37 to C-40) =====

        # C-37: Endurance sport + session of 90 minutes or more
        if session_mins >= 90 and sport_type == "Endurance (Marathon, Cycling)":   # CONDITION
            fire(
                "C-37",                                                                                   # Rule ID
                "You said: endurance sport + session of 90 minutes or more. You use up a lot of energy.", # Why
                f"🍝 **Eat more carbs:** Aim for {int(weight * 8)}g of carbs per day (8g per kg of body weight) and take 60g of carbs every hour while training.",  # Advice
                0,                                                                                        # Readiness change (no change)
                None                                                                                      # Risk level (no change)
            )

        # C-38: Sprint / Power sport
        if sport_type == "Sprint / Power (100m, Jumping)":   # CONDITION
            fire(
                "C-38",                                                                                   # Rule ID
                "You said: your sport is Sprint / Power. Your muscles need extra protein to repair.",     # Why
                f"🥩 **Eat more protein:** Aim for {int(weight * 2.0)}g of protein per day (2g per kg of body weight) and 5g of creatine daily.",  # Advice
                0,                                                                                        # Readiness change (no change)
                None                                                                                      # Risk level (no change)
            )

        # C-39: Team sport
        if sport_type == "Team Sport (Football, Cricket, Basketball)":   # CONDITION
            fire(
                "C-39",                                                                                   # Rule ID
                "You said: your sport is a Team Sport. You need a mix of carbs and protein.",             # Why
                f"🍝 **Eat a balanced diet:** Aim for {int(weight * 6)}g of carbs and {int(weight * 1.6)}g of protein per day.",  # Advice
                0,                                                                                        # Readiness change (no change)
                None                                                                                      # Risk level (no change)
            )

        # C-40: Very long session (120 minutes or more)
        if session_mins >= 120:   # CONDITION
            fire(
                "C-40",                                                                                   # Rule ID
                "You said: session of 120 minutes or more. Long sessions use up your energy.",            # Why
                "🥤 **Eat while training:** Have a banana or an energy snack every hour.",                # Advice
                -5,                                                                                       # Readiness change
                None                                                                                      # Risk level (no change)
            )

# =========================================================
# TAB 4: PERFORMANCE  ->  Rules C-41 to C-50
# =========================================================
with tab4:
    section_head("bolt", "Performance", "Enter your test results to see your athletic strengths.")
    p1, p2 = st.columns(2)

    with p1:
        sprint_40m = st.slider("40m Sprint Time (Seconds)", 4.3, 6.5, 5.0, 0.05)
        vert_jump = st.slider("Vertical Jump (cm)", 30, 90, 58)

    with p2:
        agility_ttest = st.slider("T-Test Agility Time (Seconds)", 8.5, 13.0, 9.8, 0.1)
        vo2_max = st.slider("Estimated VO2 Max (ml/kg/min)", 35, 80, 54)

    # Only run Performance rules when the user actually changes an input in this tab
    tab4_used = (sprint_40m != 5.0 or vert_jump != 58 or agility_ttest != 9.8 or vo2_max != 54)
    if tab4_used:
        # ===== SPEED and JUMP RULES (C-41 to C-44): only ONE of these can match =====

        # C-41: Fast sprint + high jump
        if sprint_40m <= 4.85 and vert_jump >= 62:   # CONDITION
            fire(
                "C-41",                                                                                   # Rule ID
                f"You said: 40m sprint {sprint_40m}s (4.85s or faster) + jump {vert_jump}cm (62cm or more). You are fast and explosive.",  # Why
                "🚀 **Best sports for you:** Winger, Striker, Fast Bowler or 100m Sprinter.",             # Advice
                0,                                                                                        # Readiness change (no change)
                None                                                                                      # Risk level (no change)
            )

        # C-42: Slow sprint + low jump
        elif sprint_40m > 5.3 and vert_jump < 45:   # CONDITION
            fire(
                "C-42",                                                                                   # Rule ID
                f"You said: 40m sprint {sprint_40m}s (slower than 5.3s) + jump {vert_jump}cm (under 45cm). Your leg power is low.",  # Why
                "🏋️ **Build leg power:** Do heavy deadlifts and box jumps 2 times a week.",               # Advice
                0,                                                                                        # Readiness change (no change)
                None                                                                                      # Risk level (no change)
            )

        # C-43: Slow sprint
        elif sprint_40m > 5.3:   # CONDITION
            fire(
                "C-43",                                                                                   # Rule ID
                f"You said: 40m sprint {sprint_40m}s (slower than 5.3s). Your running speed is slow.",    # Why
                "👟 **Work on speed:** Add short sprints and running drills 2 times a week.",             # Advice
                0,                                                                                        # Readiness change (no change)
                None                                                                                      # Risk level (no change)
            )

        # C-44: Low jump
        elif vert_jump < 45:   # CONDITION
            fire(
                "C-44",                                                                                   # Rule ID
                f"You said: vertical jump {vert_jump}cm (under 45cm). Your jumping power is low.",        # Why
                "🏋️ **Work on jumping:** Add squats, calf raises and box jumps.",                         # Advice
                0,                                                                                        # Readiness change (no change)
                None                                                                                      # Risk level (no change)
            )

        # ===== STAMINA and AGILITY RULES (C-45 to C-48) =====

        # C-45: High stamina + quick turns
        if vo2_max >= 58 and agility_ttest <= 9.6:   # CONDITION
            fire(
                "C-45",                                                                                   # Rule ID
                f"You said: VO2 Max {vo2_max} (58 or more) + agility {agility_ttest}s (9.6s or faster). You have great stamina and quick turns.",  # Why
                "⚡ **Best sports for you:** Midfielder or all-rounder who runs the whole game.",          # Advice
                0,                                                                                        # Readiness change (no change)
                None                                                                                      # Risk level (no change)
            )

        # C-46: Low stamina
        elif vo2_max < 45:   # CONDITION
            fire(
                "C-46",                                                                                   # Rule ID
                f"You said: VO2 Max {vo2_max} (under 45). Your stamina is low.",                          # Why
                "👟 **Build stamina:** Do 30 minutes of easy running or cycling 3 times a week.",         # Advice
                -10,                                                                                      # Readiness change
                "Moderate"                                                                                # Risk level
            )

        # C-47: Slow agility
        if agility_ttest > 10.8:   # CONDITION
            fire(
                "C-47",                                                                                   # Rule ID
                f"You said: agility time {agility_ttest}s (slower than 10.8s). You are slow at turning and stopping.",  # Why
                "👟 **Work on agility:** Practice cone drills and quick side-to-side cuts.",              # Advice
                -10,                                                                                      # Readiness change
                "Moderate"                                                                                # Risk level
            )

        # C-48: Strong speed, jump, stamina, or agility
        if vo2_max >= 58 or sprint_40m <= 4.85 or vert_jump >= 62 or agility_ttest <= 9.5:   # CONDITION
            fire(
                "C-48",                                                                                   # Rule ID
                f"You said: Sprint {sprint_40m}s, Jump {vert_jump}cm, Agility {agility_ttest}s, VO2 Max {vo2_max}. You have above-average athletic fitness.",  # Why
                "⚡ **Strong all-round fitness:** Good for sports with lots of running and sprinting.",    # Advice
                0,                                                                                        # Readiness change (no change)
                None                                                                                      # Risk level (no change)
            )

        # ===== BODY and OVERALL RULES (C-49, C-50) =====

        # C-49: Heavy body + low jump
        if weight > 90 and vert_jump < 45:   # CONDITION
            fire(
                "C-49",                                                                                   # Rule ID
                f"You said: weight {weight}kg (over 90kg) + jump {vert_jump}cm (under 45cm). A heavy body puts stress on your joints.",  # Why
                "⚠️ **Protect your joints:** Mix in swimming or cycling instead of only running and jumping.",  # Advice
                -5,                                                                                       # Readiness change
                None                                                                                      # Risk level (no change)
            )

        # C-50: All test results are average
        if 4.85 < sprint_40m <= 5.3 and 45 <= vert_jump < 62 and 45 <= vo2_max < 58 and 9.5 < agility_ttest <= 10.8:   # CONDITION
            fire(
                "C-50",                                                                                   # Rule ID
                f"You said: Sprint {sprint_40m}s, Jump {vert_jump}cm, Agility {agility_ttest}s, VO2 Max {vo2_max}. All your test results are balanced.",  # Why
                "✅ **Balanced athlete:** Keep a steady training plan and improve one weak area at a time.",  # Advice
                0,                                                                                        # Readiness change (no change)
                None                                                                                      # Risk level (no change)
            )

# If the user only changed Recovery, Nutrition, or Performance and left Injury Check untouched, hide default C-15
if (tab2_used or tab3_used or tab4_used) and not tab1_used:
    triggered_rules = [(rid, desc) for rid, desc in triggered_rules if rid != "C-15"]
    recommendations = [r for r in recommendations if not r.startswith("✅ **No injury found:**")]

# Keep readiness score between 0 and 100
readiness_score = max(0, min(100, readiness_score))

# If the score is very low, the risk level must be high too
if readiness_score < 35:
    risk_level = escalate_risk(risk_level, "Critical")
elif readiness_score < 55:
    risk_level = escalate_risk(risk_level, "High")
elif readiness_score < 75:
    risk_level = escalate_risk(risk_level, "Moderate")

# ---------------------------------------------------------
# PART 4. LIVE DASHBOARD SUMMARY
# ---------------------------------------------------------
navbar_slot.markdown(nav_html(risk_level, readiness_score), unsafe_allow_html=True)

st.markdown('<div id="dashboard" class="section-title">Your Results</div>', unsafe_allow_html=True)
st.markdown('<div class="legend"><span><i style="background:#34d399"></i>Safe</span><span><i style="background:#fbbf24"></i>Be careful</span><span><i style="background:#f87171"></i>Urgent</span></div>', unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Readiness", f"{readiness_score}%")
m2.metric("Risk Level", risk_level)
m3.metric("Rules Matched", f"{len(triggered_rules)}")
m4.metric("Daily Water", f"{round(weight * 0.04, 1)} L")

st.progress(readiness_score / 100)

col_rec, col_trace = st.columns([1.2, 1], gap="large")

def _rec_class(text):
    if text.startswith(("🚨", "🛑")): return "rec-red"
    if text.startswith(("⚠️", "📉", "🩹", "🧊")): return "rec-amber"
    if text.startswith(("✅", "⚡", "🚀", "📈")): return "rec-green"
    return ""

def _split_emoji(text):
    """Split the leading emoji from the text so it can be shown as a glass icon."""
    head, _, rest = text.partition(" ")
    return (head, rest) if head and not head.isascii() else ("", text)

with col_rec:
    st.markdown('<div class="section-title">What to do</div>', unsafe_allow_html=True)
    for rec in recommendations:
        emoji, body = _split_emoji(rec)
        html_rec = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", body)
        icon_html = gicon(EMOJI_TO_ICON.get(emoji, "info"), 36)
        st.markdown(f'<div class="rec-card {_rec_class(rec)}">{icon_html}<div>{html_rec}</div></div>', unsafe_allow_html=True)

with col_trace:
    st.markdown('<div class="section-title">Why you got this advice</div>', unsafe_allow_html=True)
    for rule_id, desc in triggered_rules:
        st.markdown(f'<div class="rule-card"><span class="rule-badge">{rule_id}</span>{desc}</div>', unsafe_allow_html=True)
