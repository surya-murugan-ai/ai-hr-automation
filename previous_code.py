# _________________________________________________________________________________
# 03-july-2025

# import streamlit as st
# import requests
# from supabase import create_client
# from dotenv import load_dotenv
# import os

# # 🌱 Load environment
# load_dotenv()
# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# N8N_WEBHOOK = os.getenv("JD_GENERATOR_N8N_URL")

# # 🛠️ Supabase client
# supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# # 🧠 Init session state
# for key in ["user", "company", "access_token", "refresh_token", "chat", "show_profile"]:
#     if key not in st.session_state:
#         st.session_state[key] = [] if key == "chat" else False if key == "show_profile" else None

# # 🔁 Rehydrate user session from token
# if st.session_state.access_token and not st.session_state.user:
#     try:
#         session = {
#             "access_token": st.session_state.access_token,
#             "refresh_token": st.session_state.refresh_token
#         }
#         user = supabase.auth.set_session(session)
#         if user.user:
#             st.session_state.user = user
#             company = supabase.table("companies").select("*").eq("owner_id", user.user.id).single().execute()
#             st.session_state.company = company.data
#             load_chat_history(user.user.id)
#     except Exception:
#         st.warning("Session expired. Please log in again.")
#         for k in ["user", "company", "access_token", "refresh_token", "chat"]:
#             st.session_state.pop(k, None)

# # 🧠 Load Chat History
# def load_chat_history(user_id):
#     res = supabase.table("chat_logs").select("*").eq("user_id", user_id).order("created_at").execute()
#     st.session_state.chat = [
#         {"message": row["message"], "response": row["response"]["text"]} for row in res.data
#     ]

# # 🔐 Login Page
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

#                 # Get company
#                 company_resp = supabase.table("companies").select("*").eq("owner_id", user.user.id).single().execute()
#                 st.session_state.company = company_resp.data
#                 load_chat_history(user.user.id)
#                 st.rerun()
#             else:
#                 st.error("Login failed.")
#         except:
#             st.error("Invalid credentials. Try again.")

# # 🏢 Company Profile Setup
# def company_profile():
#     st.title("🏢 Create Company Profile")
#     with st.form("company_form"):
#         name = st.text_input("Company Name")
#         industry = st.text_input("Industry")
#         location = st.text_input("Location", value="Remote")
#         tone = st.selectbox("Tone", ["Professional", "Friendly", "Startup", "Corporate"])
#         size = st.number_input("Company Size", value=10, min_value=1)

#         if st.form_submit_button("Save Profile"):
#             user_id = st.session_state.user.user.id
#             res = supabase.table("companies").insert({
#                 "name": name,
#                 "industry": industry,
#                 "location": location,
#                 "tone": tone,
#                 "size": size,
#                 "owner_id": user_id
#             }).execute()

#             if res.data:
#                 st.session_state.company = res.data[0]
#                 st.success("Profile created. Redirecting...")
#                 st.rerun()
#             else:
#                 st.error("Error saving profile.")

# # 📋 Show Company Details
# def show_company_profile():
#     company = st.session_state.company
#     with st.expander("📋 Company Profile", expanded=True):
#         st.markdown(f"""
#         - **Name:** {company['name']}
#         - **Industry:** {company['industry']}
#         - **Location:** {company['location']}
#         - **Tone:** {company['tone']}
#         - **Size:** {company['size']} employees
#         """)

# # 💬 Chat UI
# def chat_ui():
#     st.set_page_config(page_title="JD Generator", layout="wide")
#     st.title("💬 JD Chat Assistant")

#     col1, col2 = st.columns([0.8, 0.2])
#     with col2:
#         if st.button("👤 View Profile"):
#             st.session_state.show_profile = not st.session_state.show_profile

#     if st.session_state.show_profile:
#         show_company_profile()

#     # 🔓 Logout
#     if st.sidebar.button("Logout 🔓"):
#         for key in ["user", "company", "access_token", "refresh_token", "chat"]:
#             st.session_state.pop(key, None)
#         st.rerun()

#     # �� Show chat history
#     for pair in st.session_state.chat:
#         with st.chat_message("user"):
#             st.markdown(pair["message"])
#         with st.chat_message("ai"):
#             st.markdown(pair["response"])

#     # ➕ JD Form Toggle
#     with st.expander("📋 Create JD via Form"):
#         with st.form("jd_form"):
#             role = st.text_input("Role / Title", placeholder="e.g. Full Stack Engineer")
#             hiring_count = st.number_input("Number of Hires", min_value=1, value=1)
#             exp_min = st.number_input("Min Years of Experience", min_value=0, value=0)
#             exp_max = st.number_input("Max Years of Experience", min_value=exp_min, value=3)
#             skills = st.text_area("Required Skills (comma-separated)", placeholder="e.g. Python, React, PostgreSQL")
#             location = st.text_input("Job Location", placeholder="Remote / Bangalore / etc.")

#             submit_jd = st.form_submit_button("Generate JD")

#             if submit_jd:
#                 message = f"""
#     Create a job description for the following:
#     - Role: {role}
#     - Number of Openings: {hiring_count}
#     - Experience: {exp_min} to {exp_max} years
#     - Skills: {skills if skills else 'Suggest suitable skills'}
#     - Location: {location or 'Remote'}
#     """
#                 # Show in chat
#                 with st.chat_message("user"):
#                     st.markdown(message)

#                 with st.spinner("Creating JD..."):
#                     payload = {
#                         "user_id": st.session_state.user.user.id,
#                         # "company_id": st.session_state.company["id"],
#                         "message": message
#                     }
#                     res = requests.post(N8N_WEBHOOK, json=payload)
#                     data = res.json()
#                     jd_text = data.get("text", str(data))

#                 with st.chat_message("ai"):
#                     st.markdown(jd_text)

#                 st.session_state.chat.append({
#                     "message": message,
#                     "response": jd_text
#                 })


#     # ➕ New Input
#     user_input = st.chat_input("Ask a question or type job role...")
#     if user_input:
#         with st.chat_message("user"):
#             st.markdown(user_input)

#         with st.spinner("Thinking..."):
#             payload = {
#                 "user_id": st.session_state.user.user.id,
#                 # "company_id": st.session_state.company["id"],
#                 "message": user_input
#             }
#             res = requests.post(N8N_WEBHOOK, json=payload)
#             data = res.json()
#             reply = data.get("text", str(data))

#         with st.chat_message("ai"):
#             st.markdown(reply)

#         st.session_state.chat.append({
#             "message": user_input,
#             "response": reply
#         })

# # 🔁 Page Router
# if not st.session_state.user:
#     login()
# elif not st.session_state.company:
#     company_profile()
# else:
#     chat_ui()



# import streamlit as st
# import requests
# from supabase import create_client
# from dotenv import load_dotenv
# import os

# # Load .env variables
# load_dotenv()

# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# # ---------------------------
# # Session State Init
# # ---------------------------
# if "user" not in st.session_state:
#     st.session_state.user = None
# if "access_token" not in st.session_state:
#     st.session_state.access_token = None
# if "refresh_token" not in st.session_state:
#     st.session_state.refresh_token = None
# if "company" not in st.session_state:
#     st.session_state.company = None
# if "page" not in st.session_state:
#     st.session_state.page = "login"

# # ---------------------------
# # Restore Session on Reload
# # ---------------------------
# if st.session_state.access_token and not st.session_state.user:
#     try:
#         session = {
#             "access_token": st.session_state.access_token,
#             "refresh_token": st.session_state.refresh_token
#         }
#         user = supabase.auth.set_session(session)
#         st.session_state.user = user

#         # Fetch company profile
#         company_resp = supabase.table("companies").select("*").eq("owner_id", user.user.id).execute()
#         if company_resp.data:
#             st.session_state.company = company_resp.data[0]
#             st.session_state.page = "chat"
#         else:
#             st.session_state.page = "company"

#     except Exception:
#         st.warning("Session expired. Please log in again.")
#         for key in ["user", "access_token", "refresh_token", "company"]:
#             st.session_state.pop(key, None)
#         st.session_state.page = "login"

# # ---------------------------
# # 🔐 Login Page
# # ---------------------------
# def login_page():
#     st.title("Login")
#     email = st.text_input("Email")
#     password = st.text_input("Password", type="password")

#     if st.button("Login"):
#         try:
#             user = supabase.auth.sign_in_with_password({"email": email, "password": password})
#             st.session_state.user = user
#             st.session_state.access_token = user.session.access_token
#             st.session_state.refresh_token = user.session.refresh_token

#             # Check for existing company
#             company_resp = supabase.table("companies").select("*").eq("owner_id", user.user.id).execute()
#             if company_resp.data:
#                 st.session_state.company = company_resp.data[0]
#                 st.session_state.page = "chat"
#             else:
#                 st.session_state.page = "company"

#             st.rerun()

#         except Exception as e:
#             st.error("Login failed. Please check your credentials.")

# # ---------------------------
# # 🏢 Company Profile Page
# # ---------------------------
# def company_page():
#     st.title("Create Company Profile")

#     with st.form("company_form"):
#         name = st.text_input("Company Name", max_chars=100)
#         industry = st.text_input("Industry", placeholder="e.g. Software, Healthcare, Fintech")
#         location = st.text_input("Location", value="Remote")
#         tone = st.selectbox("Tone", ["Professional", "Friendly", "Startup", "Corporate"])
#         size = st.number_input("Company Size", min_value=1, value=10)

#         submitted = st.form_submit_button("Save Company Profile")

#         if submitted:
#             user_id = st.session_state.user.user.id
#             insert_data = {
#                 "name": name,
#                 "industry": industry,
#                 "location": location,
#                 "tone": tone,
#                 "size": size,
#                 "owner_id": user_id
#             }
#             res = supabase.table("companies").insert(insert_data).execute()
#             if res.data:
#                 st.success("Company profile created successfully.")
#                 st.session_state.company = res.data[0]
#                 st.session_state.page = "chat"
#                 st.rerun()
#             else:
#                 st.error("Failed to create company profile.")

# # ---------------------------
# # 💬 JD Generator Page
# # ---------------------------
# def jd_generator_page():
#     st.title("JD Generator")

#     company = st.session_state.company
#     st.markdown(f"""
#     **{company['name']}**  
#     📍 {company['location']} | 🏢 {company['industry']} | 👥 {company['size']}  
#     _Tone: {company['tone']}_  
#     """)

#     prompt = st.text_input("Who are you hiring?", placeholder="e.g. Hiring a backend engineer")

#     if st.button("Generate JD"):
#         with st.spinner("Generating JD..."):
#             res = requests.post(os.getenv("JD_GENERATOR_N8N_URL"), json={
#                 "user_id": st.session_state.user.user.id,
#                 "company_id": company["id"],
#                 "message": prompt
#             })

#             if res.status_code == 200:
#                 st.success("JD Generated:")
#                 st.json(res.json())
#             else:
#                 st.error("JD generation failed. Check n8n webhook.")

# # ---------------------------
# # 🔒 Logout Button
# # ---------------------------
# def logout_button():
#     if st.sidebar.button("🔓 Logout"):
#         for key in ["user", "access_token", "refresh_token", "company", "page"]:
#             st.session_state.pop(key, None)
#         st.success("Logged out successfully.")
#         st.rerun()

# # ---------------------------
# # Route Pages
# # ---------------------------
# if st.session_state.user:
#     logout_button()

# if st.session_state.page == "login":
#     login_page()
# elif st.session_state.page == "company":
#     company_page()
# elif st.session_state.page == "chat":
#     jd_generator_page()