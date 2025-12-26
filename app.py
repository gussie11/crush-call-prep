import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="CRUSH Call Architect", page_icon="🦁", layout="wide")

# --- 2. API SETUP & MODEL DISCOVERY ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = st.sidebar.text_input("Enter Google API Key", type="password")

if not api_key:
    st.warning("⚠️ Enter API Key to continue.")
    st.stop()

genai.configure(api_key=api_key)

# --- 3. DYNAMIC MODEL SELECTOR (The Fix) ---
# Instead of hardcoding names, we ask the API what is available.
@st.cache_resource
def get_available_models():
    try:
        # List all models that support 'generateContent'
        models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                models.append(m.name)
        
        # Sort so newer 1.5 models usually appear near top if available
        models.sort(reverse=True)
        return models
    except Exception as e:
        return []

# Get the list
available_models = get_available_models()

# Sidebar Selection
with st.sidebar:
    st.header("⚙️ AI Settings")
    if available_models:
        selected_model_name = st.selectbox("Select Model Version:", available_models, index=0)
    else:
        st.error("No models found. Check API Key permissions.")
        st.stop()

    st.info(f"Using: {selected_model_name}")

# --- 4. THE ARCHITECT BRAIN (System Prompt) ---
CRUSH_SYSTEM_INSTRUCTION = """
You are an expert Sales Coach specialized in the **CRUSH Methodology**.
**Your Mission:** Generate a progression call script that achieves TWO distinct goals:
1.  **The Move (CDM/RAID):** Advance the specific **Decision Role** to the next **CDM Stage**.
2.  **The Future (CRUSH/RUBIE):** De-risk the **Future State** by addressing specific Adoption Risks (C.R.U.S.H.).

### INPUTS:
* **Goal 1 (Mechanics):** CDM Stage {stage}, RAID Role {raid_role}.
* **Goal 2 (Future):** RUBIE POV {rubie_role}, Risk Factor {crush_element}.
* **Trust:** Proximity {proximity}.

### GENERATION RULES:

**1. THE OPENING (Visual & Trust):**
* Establish **Level 2/3 Proximity** immediately.
* State a "Collaborative Agenda" that explicitly links the *Decision* to the *Future Value*.

**2. THE FUTURE STATE (Addressing Goal 2):**
* You must script talking points that resolve the specific **CRUSH Risk Factor** selected.
* *Logic Check:* If the user selected "Usage Risk" for an "Implementor," talk about *workflows and feasibility*, not ROI.
* *Logic Check:* If the user selected "Support Risk," talk about *safety nets and recovery*.

**3. THE DECISION (Addressing Goal 1):**
* The Call to Action (CTA) must be a **Decision Boundary Cross**.
* Do not ask for "feedback." Ask for the specific commitment required to move from Stage {stage} to the next.

### OUTPUT STRUCTURE:
**1. 🦁 The "Safe" Opener**
(Verbatim script establishing Proximity and the Visual Agenda).

**2. 🔮 The Future State (De-Risking)**
(3 Bullet points specifically solving the **{crush_element}** risk for the **{rubie_role}**).

**3. 🚀 The Move (Decision Ask)**
(A specific closing question to get the **{raid_role}** to commit to the next CDM stage).

Tone: Strategic, "Orchestrator", High-Value.
"""

# --- 5. THE UI WIZARD ---
st.title("🦁 CRUSH Call Architect")
st.caption("Define the Move. De-risk the Future.")

col1, col2, col3 = st.columns(3)

# --- GOAL 1: THE MOVE (Mechanics) ---
with col1:
    st.header("1. The Move")
    st.info("Mechanics: CDM & RAID")
    
    cdm_stage = st.selectbox("Current CDM Stage", [
        "1 - Sourcing (Evaluating Options)", 
        "2 - Selected (Validating Fit)", 
        "3 - Ordered (Legal/Commercials)", 
        "4 - Usage (Implementation Prep)"
    ], help="Where are they now? We need to move them to the NEXT stage.")
    
    raid_role = st.selectbox("Decision Role (RAID)", [
        "Recommender (Needs to sell it internally)", 
        "Agree’er (Needs to feel safe to approve)", 
        "Informer (Needs technical details)", 
        "Decision Maker (Needs accountability protection)"
    ], help="Who are we asking to move?")

# --- GOAL 2: THE FUTURE (Content) ---
with col2:
    st.header("2. The Future")
    st.success("Adoption: CRUSH & RUBIE")
    
    rubie_role = st.selectbox("Adoption POV (RUBIE)", [
        "User (Cares about Usability)", 
        "Implementor (Cares about Feasibility)", 
        "Benefactor (Cares about Results)", 
        "Economic Buyer (Cares about ROI)"
    ], help="Whose view of the future matters most here?")

    crush_element = st.selectbox("Primary Future Risk (CRUSH)", [
        "C - Change Risk (Why do this now?)",
        "R - Results Risk (Will we get ROI?)",
        "U - Usage Risk (Is it too hard to use?)",
        "S - Support Risk (What if it breaks?)",
        "H - Harmonization Risk (Politics/Integration)"
    ], help="What specific part of the Future State are they afraid of?")

# --- CONTEXT: THE TRUST ---
with col3:
    st.header("3. The Trust")
    st.warning("Connection: Proximity")
    
    proximity = st.radio("Proximity Level", [
        "Level 2: Transferred (Referral)",
        "Level 3: Related (Context/Industry)",
    ], help="Level 4 (Cliché) is banned.")
    
    st.markdown("---")
    generate_btn = st.button("🦁 Architect the Call", type="primary", use_container_width=True)

# --- 6. EXECUTION ---
if generate_btn:
    with st.spinner(f"Architecting using {selected_model_name}..."):
        try:
            # Inputs
            inputs = f"""
            GOAL 1 (THE MOVE): Move {raid_role} from CDM Stage {cdm_stage} to Next Stage.
            GOAL 2 (THE FUTURE): De-risk {crush_element} for the {rubie_role}.
            TRUST: {proximity}
            """
            
            # Logic for models that support/don't support system instructions
            # Generally, '1.5' models support it. '1.0' or 'gemini-pro' might fail with it in some library versions.
            # We will use the Safer Append Method for everything to ensure compatibility.
            
            model = genai.GenerativeModel(selected_model_name)
            final_prompt = f"{CRUSH_SYSTEM_INSTRUCTION}\n\nTASK: Generate Script for:\n{inputs}"

            response = model.generate_content(final_prompt)
            
            st.markdown("---")
            st.markdown(response.text)
            
            st.info(f"💡 **CRUSH Logic:** You are solving **{crush_element.split('-')[1]}** for the **{rubie_role.split('(')[0]}**. If you solve this, the **{raid_role.split('(')[0]}** will feel safe enough to move.")

        except Exception as e:
            st.error(f"Error: {e}")
            st.error("Tip: Try selecting a different model from the Sidebar.")
