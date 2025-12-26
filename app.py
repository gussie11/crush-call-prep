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
        # Sort so newer 1.5 models appear at the top
        my_models.sort(reverse=True)
        selected_model = st.selectbox("Select Your Model:", my_models, index=0)
    else:
        st.error("No models found. Check API Key.")
        st.stop()

# --- 4. THE BRAIN (System Prompt) ---
CRUSH_SYSTEM_INSTRUCTION = """
You are an expert Sales Coach specialized in the **CRUSH Methodology**.
**Your Mission:** Generate a specific Call Script based on the User's Goal.

### MODE A: DISCOVERY (Diagnose the "Change")
**Trigger:** If Goal is "Discovery: Diagnose the Change".
**Logic:** The user does NOT know the pain yet. Do not assume it.
**Strategy:** Use the "Anchor -> Impact -> Future Gap" sequence.
1.  **Anchor Question:** Probe the limitations of the *Current State* (Status Quo).
2.  **Impact Question:** Tie those limitations to **Results** (if Benefactor) or **Effort** (if User).
3.  **Future Gap:** Ask what the Ideal Future looks like.
* **Constraint:** Do NOT ask "What keeps you up at night?". Ask "How is the current process limiting X?".

### MODE B: PROGRESSION (De-Risk the Future)
**Trigger:** If Goal is "Progression: De-Risk the Future".
**Logic:** The pain is known. Now we must sell the *Adoption*.
**Strategy:**
1.  **The Move:** Ask for the commitment to the next CDM Stage.
2.  **The Future:** Address the specific **CRUSH Risk** (Usage/Support/Harmonization) selected by the user.

### INPUTS:
* **Context:** CDM {stage}, RAID {raid_role}, RUBIE {rubie_role}.
* **Goal:** {call_goal}.
* **Risk/Focus:** {crush_focus}.

### OUTPUT STRUCTURE:
**1. 🦁 The Opener**
(A visual/collaborative agenda script).

**2. 🎯 Strategic Questions (The Core)**
(3 Bullet points following the Mode A or Mode B strategy above).

**3. 🚀 The Next Step**
(A specific closing question).

Tone: Strategic, Professional, "Orchestrator".
"""

# --- 5. THE WIZARD UI (Tabs) ---
st.title("🦁 CRUSH Call Architect")
st.caption("Step-by-Step Call Planner")

# Create Tabs for sequential thinking
tab1, tab2, tab3 = st.tabs(["1. The Company 🏢", "2. The Person 👤", "3. The Strategy 🚀"])

# --- TAB 1: COMPANY LOGIC ---
with tab1:
    st.header("Step 1: The Business Logic")
    st.info("Focus only on the **Company** right now. Where are they in the decision journey?")
    
    cdm_stage = st.selectbox("CDM Stage (Decision Journey)", [
        "0 - Need (Latent Pain)",
        "1 - Sourcing (Evaluating Options)", 
        "2 - Selected (Validating Fit)",
        "3 - Ordered (Commercials)",
        "4 - Usage (Implementation)"
    ], help="This determines if we focus on Pain (Stage 0-1) or Adoption Risk (Stage 2+).")
    
    st.markdown("👉 **Done? Click the next tab above.**")

# --- TAB 2: HUMAN EMOTION ---
with tab2:
    st.header("Step 2: The Human Element")
    st.info("Now switch gears. Focus on the **Person** across the table.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        raid_role = st.selectbox("RAID Role (Function)", [
            "Recommender (Champion)", 
            "Agree’er (Veto Power)", 
            "Decision Maker (Signer)",
            "Informer (Expert)"
        ], help="What is their job in the decision team?")
    
    with col_b:
        rubie_role = st.selectbox("RUBIE POV (Motivation)", [
            "Benefactor (Cares about Results/Outcomes)", 
            "Economic Buyer (Cares about ROI)",
            "User (Cares about Usability)",
            "Implementor (Cares about Feasibility)",
            "Ripple (Impacted)"
        ], help="What creates value (or fear) for them personally?")

# --- TAB 3: STRATEGY & EXECUTION ---
with tab3:
    st.header("Step 3: The Objective")
    st.success("Finally, what do we want to achieve?")
    
    call_goal = st.selectbox("Call Objective", [
        "Discovery: Diagnose the 'Change' (Pain)",
        "Progression: De-Risk the Future (Adoption)"
    ], help="Choose 'Discovery' if you don't know the pain yet.")

    # Dynamic Focus based on Goal
    if "Discovery" in call_goal:
        st.warning("🔎 **Discovery Mode:** We will probe the Status Quo.")
        crush_focus = "C - Change (Why is Status Quo failing?)"
    else:
        st.success("🏗️ **Progression Mode:** We will de-risk the Adoption.")
        crush_focus = st.selectbox("Primary Risk to Resolve", [
            "R - Results Risk (ROI confidence)",
            "U - Usage Risk (Usability/Workflow)",
            "S - Support Risk (Safety Net)",
            "H - Harmonization Risk (Politics)"
        ])
    
    st.markdown("---")
    generate_btn = st.button("🦁 Architect the Call", type="primary", use_container_width=True)

# --- 6. EXECUTION ---
if generate_btn:
    with st.spinner(f"Architecting using {selected_model}..."):
        try:
            # Inputs
            inputs = f"""
            CONTEXT: CDM {cdm_stage}, RAID {raid_role}, RUBIE {rubie_role}
            GOAL: {call_goal}
            FOCUS: {crush_focus}
            """
            
            # Model & Generation
            model = genai.GenerativeModel(selected_model)
            final_prompt = f"{CRUSH_SYSTEM_INSTRUCTION}\n\nTASK: Generate Script for:\n{inputs}"
            response = model.generate_content(final_prompt)
            
            # Display Results below the tabs
            st.markdown("---")
            st.markdown(response.text)
            
            # Contextual Footer
            if "Discovery" in call_goal:
                 st.info("💡 **CRUSH Logic:** You are probing the **Current State** to find the gap. Once they admit the gap, you have established **Change**.")
            else:
                 # Clean string splitting to avoid errors
                 focus_name = crush_focus.split('-')[1] if '-' in crush_focus else crush_focus
                 st.info(f"💡 **CRUSH Logic:** You are de-risking the **Future State** ({focus_name}) so they feel safe to move.")

        except Exception as e:
            st.error(f"Error: {e}")
