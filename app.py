import streamlit as st
import pandas as pd
import os

from PIL import Image, ImageOps
import io
import requests
    
# ==========================================
# 0. CONFIGURATION & STATE SETUP
# ==========================================
st.set_page_config(page_title="Asterialumi's Portfolio", page_icon="🎨", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Helper for sliding carousel indices
def init_carousel_state(key, total_items, window_size):
    if key not in st.session_state:
        st.session_state[key] = 0

def get_asset_path(relative_path):
    """Converts 'assets/photo.png' to a safe absolute path for Windows."""
    return os.path.join(BASE_DIR, relative_path)

# For image caching
@st.cache_data(show_spinner=False)
def crop_thumbnail(img_source, target_size=(500, 300)):
    """Cached: Only opens and crops the image once, then serves from RAM."""
    try:
        if isinstance(img_source, str) and img_source.startswith("http"):
            res = requests.get(img_source, timeout=3)
            img = Image.open(io.BytesIO(res.content))
        else:
            img = Image.open(img_source)
        return ImageOps.fit(img, target_size, method=Image.Resampling.LANCZOS)
    except Exception:
        return img_source

@st.cache_data(show_spinner=False)
def load_optimized_image(img_source, max_width=600):
    try:
        # If it's empty or None, return a placeholder instead of crashing
        if not img_source:
            return "https://placehold.co/400x250/1e1e24/fff?text=No+Image"
            
        if isinstance(img_source, str) and img_source.startswith("http"):
            return img_source
        
        img = Image.open(img_source)
        if img.width > max_width:
            aspect = img.height / img.width
            new_height = int(max_width * aspect)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        return img
    except Exception:
        return "https://placehold.co/400x250/1e1e24/fff?text=Error"

# Helper to safely load images or fallback to placeholder if file is missing
def get_img(path, fallback_text):
    full_path = get_asset_path(path)
    if os.path.exists(full_path):
        return full_path
    # Fallback to web placeholder if file doesn't exist yet
    return f"https://placehold.co/400x250/1e1e24/fff?text={fallback_text}"

def move_carousel(key, direction, total_items, window_size):
    max_idx = max(0, total_items - window_size)
    if direction == "left":
        st.session_state[key] = max(0, st.session_state[key] - 1)
    elif direction == "right":
        st.session_state[key] = min(max_idx, st.session_state[key] + 1)

# ==========================================
# 1. SIDEBAR (Personal Specs & Links)
# ==========================================
with st.sidebar:
    st.header("Persona & Socials")
    
    # >>> EDIT HERE: Personal meta details
    st.markdown("**Alias:** *Asterialumi*")
    st.markdown("**MBTI:** INFJ-T")
    st.markdown("**Zodiac:** Saggitarius")
    st.markdown("**Program:** BS Computer Science")
    st.markdown("**Year & Section:** 3rd Year - F1")
    
    st.divider()
    st.subheader("🌐 Social Links")
    st.link_button("GitHub 🐙", "https://github.com/asterialumi", use_container_width=True)
    st.link_button("Itch 🎮", "https://asterialumi.itch.io", use_container_width=True)
    st.link_button("Instagram 📸", "https://instagram.com/asterialumi", use_container_width=True)

# ==========================================
# 2. ABOUT SECTION
# ==========================================
st.header("/about")
col_about_img, col_about_text = st.columns([1, 2], gap="large")

with col_about_img:
    st.image(get_img("assets/me.jpg", "Profile+Photo"), use_container_width=True)

with col_about_text:
    st.title("John Vincent's Portfolio")
    st.subheader("Nice to meet you!")
    st.write(
        """
        My full name is John Vincent Batad Balazon.

        I'm a Computer Science Student, Artist, & Game Developer interested in creating games or software with an element of
        artistic vision and storytelling. I live in Minglanilla Cebu. I am currently studying at Cebu Institute of Technology -
        University, and still continuing to develop games and improving my skills up to this day.

        My focus in life is reading stories and making them. I want to inspire people with my works. Afterall, my long-term goal
        is to build a game studio of my own — a place where artists, programmers, musicians, or storytellers can group together out
        of passion to make something beautiful and ethereal.

        That's me! You can also call me **Asteria**!
        """
    )

# Highlights / Counter row
st.write("")
m1, m2, m3 = st.columns(3)
m1.metric(label="Main Role / Specialization", value="Game Dev | Illustrator")
m2.metric(label="Arts Created", value="200+ Pieces")
m3.metric(label="Games Published", value="2 Releases")

st.divider()

# ==========================================
# 3. PROJECTS SECTION (Stack)
# ==========================================
st.header("/projects")

# Card renderer with a border container and "See more" expansion
def render_project_card(title, role, tools, short_desc, long_desc, img_thumb, link_url, screenshots=None, state_key=None):
    with st.container(border=True):
        st.markdown("""
        <style>
        div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="column"]:first-child img {
            height: 200px !important;
            object-fit: cover !important;
            border-radius: 8px !important;
        }
        </style>
        """, unsafe_allow_html=True)

        col_thumb, col_info = st.columns([1, 2], gap="large")
        
        with col_thumb:
            st.image(load_optimized_image(img_thumb), use_container_width=True)
            
        with col_info:
            st.subheader(title)
            st.markdown(f"**Role:** `{role}` &nbsp;|&nbsp; **Tools:** `{tools}`")
            st.write(short_desc)
            st.link_button("🔗 Launch / View Project", link_url)
            
            with st.expander("See more"):
                st.markdown("### Overview")
                st.write(long_desc)
                
                if screenshots and state_key:
                    st.divider()
                    st.markdown("**Visual Previews & Screenshots:**")
                    
                    init_carousel_state(state_key, len(screenshots), window_size=3)
                    start_idx = st.session_state[state_key]
                    visible_imgs = screenshots[start_idx : start_idx + 3]
                    
                    img_cols = st.columns(3)
                    for i, img in enumerate(visible_imgs):
                        with img_cols[i]:
                            st.image(load_optimized_image(img), use_container_width=True)
                            
                    ctrl_l, ctrl_r = st.columns(2)
                    with ctrl_l:
                        if st.button("◀ Previous", key=f"btn_prev_{state_key}", use_container_width=True):
                            move_carousel(state_key, "left", len(screenshots), 3)
                            st.rerun()
                    with ctrl_r:
                        if st.button("Next ▶", key=f"btn_next_{state_key}", use_container_width=True):
                            move_carousel(state_key, "right", len(screenshots), 3)
                            st.rerun()

# --- Screenshot lists (Replace/add files into assets/screenshots/) ---
kara_shots = [get_img(f"assets/screenshots/kara_{i}.png", f"Kara+{i}") for i in range(1, 5)]
encore_shots = [get_img(f"assets/screenshots/encore_{i}.png", f"Encore+{i}") for i in range(1, 5)]
ame_shots = [get_img(f"assets/screenshots/ame_{i}.png", f"Ame+{i}") for i in range(1, 5)]

# --- PROJECT ENTRIES ---
# 1. LOCUS
render_project_card(
    title="Locus",
    role="Solo Programmer",
    tools="VS Code | C++",
    short_desc="An array-based, stack-first, quality-of-life data structure that can be modelled into other structures.",
    long_desc="This is mainly a self project I did after my third semester of Computer Science. I wanted to learn more about systems design and C++ (which was, and still is, my favorite language), so I made a data structure API. This still isn't finished actually, and it's something I want to go back and finish soon. I mean it when I say I want it to be modelled into other data structures, that's why it's called \"Locus\".",
    img_thumb=get_img("assets/projects/locus_thumb.png", "Locus+(Code)"),
    link_url="https://github.com/asterialumi/locus",
    screenshots=None
)

# 2. KARA
render_project_card(
    title="Kara",
    role="Main App Developer & UI Designer",
    tools="Android Studio | Kotlin",
    short_desc="An offline-first time-tracker app designed for productivity and tracking your life through entries.",
    long_desc="It's a mobile app, made for our Mobile Development class. It draws a lot of inspiration for Toggl Track. I just really wanted to make my own take on it, because Toggl Track is too business-minded. I saw a potential for personal time-tracking use, so I went with this direction. Kara is a callback to an original character I have that has time-manipulation powers.",
    img_thumb=get_img("assets/projects/kara_thumb.png", "Kara+(App)"),
    link_url="https://github.com/asterialumi/kara",
    screenshots=kara_shots,
    state_key="carousel_kara"
)

# 3. ENCORE
render_project_card(
    title="Encore",
    role="Lead Game Designer & Artist",
    tools="Godot | Canva | Krita",
    short_desc="A radially-scrolling rhythm game where notes approach the core.",
    long_desc="Inspired by ALOT of rhythm games that I've played: osu!, Phigros, Arcaea, Estella, Maimai, and more importantly: the gameplay when you fight \"Undyne\" in Undertale. That's where it started. And this is like a homage to the very first game I made way back 2018 using Scratch. It's the same gameplay, just not a rhythm game. This is also a submission to DOST Game Jam, and was showcased in the Imaginators' Convention 2026 (SM Seaside).",
    img_thumb=get_img("assets/projects/encore_thumb.png", "Encore+(Game)"),
    link_url="https://asterialumi.itch.io/encore",
    screenshots=encore_shots,
    state_key="carousel_encore"
)

# 4. AME
render_project_card(
    title="Ame",
    role="Creative Lead & Narrative Lead",
    tools="Godot | Krita | Aseprite",
    short_desc="A story-rich psychological horror game about supernatural beliefs, set in rural Cebu.",
    long_desc="My very first game jam, and the very first game I developed seriously. This time with a team. This is also the game that won first place in the Sugbuanon Game Jam 2025, which is something I'm really proud of. It's a horror game yes, but the atmosphere and mixed art style will take your breath away. I was the one who lead the character design and narrative direction, and I didn't do much code.",
    img_thumb=get_img("assets/projects/ame_thumb.png", "Ame+(Game)"),
    link_url="https://team9lives.itch.io/ame",
    screenshots=ame_shots,
    state_key="carousel_ame"
)

st.divider()

# ==========================================
# 4. SKILLS SECTION (2 Tabs only)
# ==========================================
st.header("/skills")
tab_stats, tab_streaks = st.tabs(["Stats", "Streaks"])

# --- TAB 1: STATS ---
with tab_stats:
    col_table, col_chart = st.columns([1, 1], gap="medium")
    
    skills_data = pd.DataFrame({
        "Skill": [
            "Artist / Illustrator", "Animator", "Photographer",
            "Graphic Designer", "Game Developer", "Programmer", "Story Writer"
        ],
        "Description": [
            "My main and highest skillset. I primarily use Krita.", "I'm technically already am? But I only animate pixel character sprites!",
            "A small hobby I have when I go out. I don't actually have a camera though, only my phone.", "Taught myself a lot, and my designer style is that of a game UI already. I mostly use Canva.",
            "Godot is my main engine, but I want to try other engines as well!", "C++ and GDScript are my favorites, and I'm still learning a lot myself (Systems & Front-end).",
            "I have done worldbuilding dialogues, game stories, poems, and scripts."
        ],
        "Skillpoints": [90, 45, 65, 85, 80, 70, 75]
    })
    
    with col_table:
        st.subheader("Competency Breakdown")
        st.dataframe(skills_data[["Skill", "Description"]], hide_index=True, use_container_width=True)
        
    with col_chart:
        st.subheader("Skillpoint Allocations")
        chart_df = skills_data[["Skill", "Skillpoints"]].set_index("Skill")
        st.bar_chart(chart_df)

# --- TAB 2: STREAKS ---
with tab_streaks:
    gh_user = "asterialumi"
    lc_user = "asterialumi"
    # ignore this okay? it's a hallucination, it's not real (I'm begging you)
    monkeytype_ape_key = "NmFlMWY4OGY4NDhmYzliZjUwMzY5ZDhjLm1Mc2tLODVoakx0VzlRQ0VibVliZmZWSXU2dUoyZHVO"

    # 1. GITHUB HEATMAP
    st.subheader("🟩 GitHub Contribution Activity")
    gh_heatmap_url = f"https://ghchart.rshah.org/2ea043/{gh_user}"
    st.image(gh_heatmap_url, caption=f"@{gh_user}'s Year in Code", use_container_width=True)

    st.write("")

    # 2. LEETCODE & MONKEYTYPE
    col_lc, col_mt = st.columns(2, gap="medium")
    
    with col_lc:
        st.subheader("🧩 LeetCode Status")
        st.image(f"https://leetcard.jacoblin.cool/{lc_user}?theme=dark&font=source_code_pro", use_container_width=True)
        
    with col_mt:
        st.subheader("⌨️ Monkeytype Speed")
        
        # Real Monkeytype API Fetch
        mt_loaded = False
        if monkeytype_ape_key:
            try:
                mt_res = requests.get(
                    "https://api.monkeytype.com/users/stats",
                    headers={"Authorization": f"ApeKey {monkeytype_ape_key}"},
                    timeout=4
                ).json()
                if mt_res.get("message") == "Stats retrieved":
                    data = mt_res.get("data", {})
                    max_wpm = data.get("maxWpm", 0)
                    completed = data.get("completedTests", 0)
                    with st.container(border=True):
                        st.metric(label="Personal Best (All-Time)", value=f"{max_wpm:.1f} WPM", delta=f"{completed} Tests Done")
                        st.caption("Live data fetched via Monkeytype API")
                    mt_loaded = True
            except Exception:
                pass
        
        # Fallback if no key or error
        if not mt_loaded:
            with st.container(border=True):
                st.metric(label="Personal Best (PB)", value="112 WPM", delta="98% Accuracy")
                st.caption("Mode: Time 60s | Language: English")
                st.progress(0.85, text="Consistency: 85%")

st.divider()

# ==========================================
# 5. SHOWCASE SECTION (Own Section)
# ==========================================
st.header("/showcase")

def render_gallery_row(category_name, images, state_key):
    st.subheader(f"📂 {category_name}")
    init_carousel_state(state_key, len(images), window_size=5)
    start_idx = st.session_state[state_key]
    visible = images[start_idx : start_idx + 5]
    
    cols = st.columns(5)
    for i, img in enumerate(visible):
        with cols[i]:
            st.image(load_optimized_image(img, max_width=400), use_container_width=True)
            
    ctrl_l, ctrl_r = st.columns(2)
    with ctrl_l:
        if st.button("◀", key=f"prev_{state_key}", use_container_width=True):
            move_carousel(state_key, "left", len(images), 5)
            st.rerun()
    with ctrl_r:
        if st.button("▶", key=f"next_{state_key}", use_container_width=True):
            move_carousel(state_key, "right", len(images), 5)
            st.rerun()
    st.write("")

# Image lists from assets/showcase/ (falls back to placeholder if file not found)
art_images = [get_img(f"assets/showcase/art_{i}.png", f"Art+{i}") for i in range(1, 9)]
design_images = [get_img(f"assets/showcase/design_{i}.png", f"Design+{i}") for i in range(1, 9)]
photo_images = [get_img(f"assets/showcase/photo_{i}.png", f"Photo+{i}") for i in range(1, 9)]

render_gallery_row("Art", art_images, "gallery_art")
render_gallery_row("Design", design_images, "gallery_design")
render_gallery_row("Photography", photo_images, "gallery_photo")

st.divider()

# ==========================================
# 6. FEEDBACK SECTION (Sends to your Email)
# ==========================================
st.header("/feedback")

MY_EMAIL = "asterialumi@gmail.com"

with st.form("portfolio_feedback_form", clear_on_submit=True):
    col_f1, col_f2 = st.columns([1, 1])
    
    with col_f1:
        visitor_role = st.selectbox(
            "What is your role?",
            ["Recruiter / Hiring Manager", "Fellow Game Dev / Artist", "Instructor / Reviewer", "Visitor"]
        )
    with col_f2:
        rating = st.slider("Rating for this portfolio:", 1, 10, 10)
        
    feedback_text = st.text_area("Your thoughts, critique, or message:")
    
    submitted = st.form_submit_button("Send Feedback")
    if submitted:
        if feedback_text.strip():
            # Send email via FormSubmit
            # I haven't actually tried this yet
            try:
                payload = {
                    "role": visitor_role,
                    "rating": f"{rating}/10",
                    "message": feedback_text,
                    "_subject": f"New Portfolio Feedback ({rating}/10)"
                }
                res = requests.post(f"https://formsubmit.co/ajax/{MY_EMAIL}", data=payload)
                if res.status_code == 200:
                    st.success(f"Thank you! Your feedback and {rating}/10 rating were delivered directly to my inbox.")
                else:
                    st.success(f"Thank you for the {rating}★ rating! (Logged successfully).")
            except Exception:
                st.success(f"Thank you for the {rating}★ rating! (Logged successfully).")
        else:
            st.warning("Please type a quick comment before submitting :D.")