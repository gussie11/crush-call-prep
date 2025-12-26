import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="CRUSH Call Architect", page_icon="🦁", layout="centered")

# --- 2. API SETUP ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = st.sidebar.text_input("Enter Google API Key", type="password")

if not api_key:
    st.warning("⚠️ Enter API Key to continue.")
    st.stop()

genai.configure(api_key=api_key)

# --- 3. DYNAMIC MODEL SELECTOR ---
@st.cache_resource
def get_working_models():
    try:
        model_list = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                model_list.append(m.name)
        return model_list
    except Exception as e:
        return []

my_models = get_working_models()

with st.sidebar:
    st.header("⚙️ System Settings")
    if my_models:
        my_models.sort(reverse=True)
        selected_model = st.selectbox("Select Your Model:", my_models, index=0)
    else:
        st.error("No models found. Check API Key.")
        st.stop()

# --- 4. THE BRAIN (System Prompt) ---
CRUSH_SYSTEM_INSTRUCTION = """
You are an expert Sales Coach specialized in the **CRUSH Methodology**.
**Your Mission:** Generate a Call Script based on the Simplified Operating Motion.

### MODE 1: MOVING (The Fast Lane)
**Trigger:** Deal Status = "Moving".
**Logic:** The deal is healthy. Do NOT over-analyze RAID/RUBIE.
**Focus:** Align to the **CDM Phase** and the **Next Decision Boundary** [cite: 1074-1075].
* **Early (CDM 0-2):** Script focuses on **Change** and **Results**.
* **Mid (CDM 2-5):** Script focuses on **Usage** and **Support**.

### MODE 2: STALLED (The Diagnostic)
**Trigger:** Deal Status = "Stalled/Blocked".
**Logic:** The decision has stopped. We must use **RAID/RUBIE** to find the blocker [cite: 1076-1078].
**Strategy:**
1.  **Identify the Blocker:** Is it a hidden *Informer* (RAID)? Or a fearful *User* (RUBIE)?
2.  **Script the Fix:** Address that specific fear directly.

### INPUTS:
* **Status:** {deal_status}.
* **Context:** CDM {stage}.
* **Deep Dive (Only if Stalled):** RAID {raid_role}, RUBIE {rubie_role}.

### OUTPUT STRUCTURE:
**1. 🦁 The Opener**
(A visual/collaborative agenda script appropriate for the stage).

**2. 🎯 The Strategy**
(If Moving: 3 Bullet points to advance to the next stage).
(If Stalled: 3 Bullet points to unblock the specific RAID/RUBIE fear).

**3. 🚀 The Call to Action**
(A specific closing question).

Tone: Strategic, Professional, Efficient.
"""

# --- 5. THE UI (Simplified Motion) ---
st.title("🦁 CRUSH Call Architect")
st.caption("Simplified Operating Motion | Sequence > Speed")

# STEP 1: THE STATUS CHECK (The Filter)
st.header("1. The Pulse")
deal_status = st.radio("How is the deal progressing?", 
                       ["✅ Moving (Standard Motion)", "❌ Stalled (Diagnostic Needed)"],
                       horizontal=True,
                       help="If moving, we keep it simple. If stalled, we dig deep [cite: 1074-1076].")

col1, col2 = st.columns(2)

# STEP 2: THE CONTEXT (Always needed)
with col1:
    st.header("2. The Stage")
    cdm_stage = st.selectbox("CDM Stage", [
        "0 - Need (Latent Pain)",
        "1 - Sourcing (Evaluating Options)", 
        "2 - Selected (Validating Fit)",
        "3 - Ordered (Commercials)",
        "4 - Usage (Implementation)"
    ])

# STEP 3: THE VARIABLE (Depends on Status)
with col2:
    st.header("3. The Details")
    
    # LOGIC: Only show RAID/RUBIE if Stalled
    if "Moving" in deal_status:
        st.success("🚀 **Fast Lane Active:** No deep mapping needed. We focus on the Next Step.")
        raid_role = "General Stakeholder"
        rubie_role = "General Alignment"
    else:
        st.error("🩺 **Diagnostic Mode Active:** We need to find the blocker.")
        raid_role = st.selectbox("Who is blocking? (RAID)", [
            "Recommender (Champion)", 
            "Agree’er (Veto Power)", 
            "Decision Maker (Signer)",
            "Informer (Expert)"
        ])
        rubie_role = st.selectbox("What is their Fear? (RUBIE)", [
            "Benefactor (Results Risk)", 
            "Economic Buyer (Financial Risk)",
            "User (Usability Risk)",
            "Implementor (Feasibility Risk)",
            "Ripple (Disruption Risk)"
        ])

st.markdown("---")
generate_btn = st.button("🦁 Architect the Call", type="primary", use_container_width=True)

# --- 6. EXECUTION ---
if generate_btn:
    with st.spinner(f"Architecting using {selected_model}..."):
        try:
            # Prepare inputs
            inputs = f"""
            STATUS: {deal_status}
            CONTEXT: CDM {cdm_stage}
            RAID: {raid_role}
            RUBIE: {rubie_role}
            """
            
            # Initialize Model
            model = genai.GenerativeModel(selected_model)
            
            # Construct Prompt
            final_prompt = f"{CRUSH_SYSTEM_INSTRUCTION}\n\nTASK: Generate Script for:\n{inputs}"

            # Generate
            response = model.generate_content(final_prompt)
            
            # Render Results
            st.markdown("---")
            st.markdown(response.text)
            
            # Contextual Footer
            if "Moving" in deal_status:
                 st.info("💡 **Simplified Motion:** Since the deal is moving, we skipped complex mapping to save your time[cite: 1075].")
            else:
                 st.info(f"💡 **Diagnostic Mode:** We are targeting the **{rubie_role.split('(')[0]}** to unblock the deal[cite: 1078].")

        except Exception as e:
            st.error(f"Error: {e}")
