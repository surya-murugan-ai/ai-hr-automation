import streamlit as st
import requests
import json
from supabase import create_client
from dotenv import load_dotenv
import os

# 🌱 Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
N8N_WEBHOOK = os.getenv("JD_GENERATOR_N8N_URL")

# 🛠️ Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 🧠 Init session state
for key in ["user", "company", "access_token", "refresh_token", "chat", "show_profile"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key == "chat" else False if key == "show_profile" else None

# 🔁 Rehydrate session
if st.session_state.access_token and not st.session_state.user:
    try:
        session = {
            "access_token": st.session_state.access_token,
            "refresh_token": st.session_state.refresh_token
        }
        user = supabase.auth.set_session(session)
        if user.user:
            st.session_state.user = user
            company = supabase.table("companies").select("*").eq("owner_id", user.user.id).single().execute()
            st.session_state.company = company.data
    except Exception:
        for k in ["user", "company", "access_token", "refresh_token", "chat"]:
            st.session_state.pop(k, None)

# 📦 Load chat history
def load_chat_history(user_id):
    res = supabase.table("chat_logs").select("*").eq("user_id", user_id).order("created_at").execute()
    st.session_state.chat = [
        {"message": row["message"], "response": row["response"]["text"]} for row in res.data
    ]

# ✅ JD Renderer
def render_jd(jd):
    st.markdown(f"### 📄 **{jd['job_title']}** at **{jd['company_name']}**")
    st.markdown(f"📍 **Location:** {jd.get('location', 'Not specified')}")
    st.markdown(f"⏱️ **Employment Type:** {jd.get('employment_type', 'Full-time')}")
    st.markdown(f"🧠 **Experience Required:** {jd.get('experience_required', '0 years')}")
    st.markdown(f"📌 **Openings:** {jd.get('number_of_openings', '1')}")

    if jd.get("job_description"):
        st.markdown("#### 📃 Job Description")
        st.markdown(jd["job_description"])

    if jd.get("skills_required"):
        st.markdown("#### 🛠 Skills Required")
        st.markdown(", ".join(jd["skills_required"]))

    if jd.get("responsibilities"):
        st.markdown("#### 📌 Responsibilities")
        for r in jd["responsibilities"]:
            st.markdown(f"- {r}")

    if jd.get("qualifications"):
        st.markdown("#### 🎓 Qualifications")
        for q in jd["qualifications"]:
            st.markdown(f"- {q}")

    if jd.get("benefits"):
        st.markdown("#### 💼 Benefits")
        for b in jd["benefits"]:
            st.markdown(f"- {b}")

    if jd.get("pdf_url"):
        st.markdown("#### 📎 Download JD PDF")
        st.markdown(f"[🧾 View JD PDF]({jd['pdf_url']})", unsafe_allow_html=True)

# 🔐 Login Page
# def login():
#     st.title("🔐 Login")
#     email = st.text_input("Email")
#     password = st.text_input("Password", type="password")

#     if st.button("Login"):
#         try:
#             user = supabase.auth.sign_in_with_password({"email": email, "password": password})
#             if user.user:
#                 st.session_state.user = user
#                 st.session_state.access_token = user.session.access_token
#                 st.session_state.refresh_token = user.session.refresh_token

#                 # Load company
#                 company = supabase.table("companies").select("*").eq("owner_id", user.user.id).single().execute()
#                 st.session_state.company = company.data
#                 load_chat_history(user.user.id)
#                 st.rerun()
#             else:
#                 st.error("Login failed.")
#         except:
#             st.error("Invalid credentials.")

def login():
    st.title("🔐 Login")
    
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
    
        if submit:
            try:
                user = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })

                if user.user:
                    st.session_state.user = user
                    st.session_state.access_token = user.session.access_token
                    st.session_state.refresh_token = user.session.refresh_token

                    # Load company
                    company = supabase.table("companies").select("*").eq("owner_id", user.user.id).single().execute()
                    st.session_state.company = company.data
                    load_chat_history(user.user.id)
                    st.rerun()
                else:
                    st.error("Login failed. Please check credentials.")
            except Exception as e:
                st.error("Invalid credentials or server error.")


# 🏢 Company Profile Setup
def company_profile():
    st.title("🏢 Create Company Profile")
    with st.form("company_form"):
        name = st.text_input("Company Name")
        industry = st.text_input("Industry")
        location = st.text_input("Location", value="Remote")
        tone = st.selectbox("Tone", ["Professional", "Friendly", "Startup", "Corporate"])
        size = st.number_input("Company Size", value=10, min_value=1)

        if st.form_submit_button("Save Profile"):
            user_id = st.session_state.user.user.id
            res = supabase.table("companies").insert({
                "name": name,
                "industry": industry,
                "location": location,
                "tone": tone,
                "size": size,
                "owner_id": user_id
            }).execute()
            if res.data:
                st.session_state.company = res.data[0]
                st.success("Profile created.")
                st.rerun()
            else:
                st.error("Error saving profile.")

# 📋 Company Profile View
def show_company_profile():
    company = st.session_state.company
    with st.expander("📋 Company Profile", expanded=True):
        st.markdown(f"""
        - **Name:** {company['name']}
        - **Industry:** {company['industry']}
        - **Location:** {company['location']}
        - **Tone:** {company['tone']}
        - **Size:** {company['size']} employees
        """)

# 💬 Main Chat UI
def chat_ui():
    st.set_page_config(page_title="JD Generator", layout="wide")
    st.title("💬 JD Generator")

    col1, col2 = st.columns([0.8, 0.2])
    with col2:
        if st.button("👤 View Profile"):
            st.session_state.show_profile = not st.session_state.show_profile

    if st.session_state.show_profile:
        show_company_profile()

    if st.sidebar.button("Logout 🔓"):
        for key in ["user", "company", "access_token", "refresh_token", "chat"]:
            st.session_state.pop(key, None)
        st.rerun()

    for pair in st.session_state.chat:
        with st.chat_message("user"):
            st.markdown(pair["message"])
        with st.chat_message("ai"):
            try:
                jd = json.loads(pair["response"]) if isinstance(pair["response"], str) else pair["response"]
                render_jd(jd)
            except Exception:
                st.markdown(pair["response"])

    # 📋 JD via Form
    with st.expander("📋 Create JD via Form"):
        with st.form("jd_form"):
            role = st.text_input("Role / Title", placeholder="e.g. Full Stack Engineer")
            hiring_count = st.number_input("Number of Hires", min_value=1, value=1)
            exp_min = st.number_input("Min Years of Experience", min_value=0, value=0)
            exp_max = st.number_input("Max Years of Experience", min_value=exp_min, value=3)
            skills = st.text_area("Required Skills (comma-separated)", placeholder="e.g. Python, React")
            location = st.text_input("Job Location", placeholder="Remote / Onsite")

            if st.form_submit_button("Generate JD"):
                message = f"""
We are hiring {hiring_count} {role}(s)
- Experience: {exp_min} to {exp_max} years
- Skills: {skills if skills else 'Suggest suitable skills'}
- Location: {location or 'Remote'}
"""
                with st.chat_message("user"):
                    st.markdown(message)

                with st.spinner("Creating JD..."):
                    try:
                        payload = {
                            "user_id": st.session_state.user.user.id,
                            "message": message
                        }
                        res = requests.post(N8N_WEBHOOK, json=payload)
                        data = res.json()
                        jd_data = data.get("output") or data.get("text") or data
                        jd = json.loads(jd_data) if isinstance(jd_data, str) else jd_data
                        reply = jd
                    except Exception as e:
                        reply = f"Error generating JD: {e}"

                with st.chat_message("ai"):
                    try:
                        render_jd(reply)
                    except:
                        st.markdown(reply)

                st.session_state.chat.append({
                    "message": message,
                    "response": reply
                })

    # 💬 Direct Chat Input
    user_input = st.chat_input("Describe the JD or ask a question...")
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.spinner("Thinking..."):
            try:
                payload = {
                    "user_id": st.session_state.user.user.id,
                    "message": user_input
                }
                res = requests.post(N8N_WEBHOOK, json=payload)
                data = res.json()
                jd_data = data.get("output") or data.get("text") or data
                jd = json.loads(jd_data) if isinstance(jd_data, str) else jd_data
                reply = jd
            except Exception as e:
                reply = f"❌ Failed to fetch JD: {e}"

        with st.chat_message("ai"):
            try:
                render_jd(reply)
            except:
                st.markdown(reply)

        st.session_state.chat.append({
            "message": user_input,
            "response": reply
        })

# 🌐 Page Routing
if not st.session_state.user:
    login()
elif not st.session_state.company:
    company_profile()
else:
    chat_ui()
