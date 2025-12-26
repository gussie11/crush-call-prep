import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="CRUSH Call Architect", page_icon="🦁", layout="wide")

# --- 2. API SETUP ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = st.sidebar.text_input("Enter Google API Key", type="password")

if not api_key:
    st.warning("⚠️ Enter API Key to continue.")
    st.stop()

genai.configure(api_key=api_key)

# --- 3. MODEL SELECTOR ---
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
2.  **The Future:** Address the specific **CRUSH Risk** (Usage/Support/Harmonization).

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

# --- 5. THE WIZARD UI ---
st.title("🦁 CRUSH Call Architect")
st.caption("Contextual Call Planner")

col1, col2, col3 = st.columns(3)

# --- COL 1: CONTEXT ---
with col1:
    st.header("1. The Context")
    cdm_stage = st.selectbox("CDM Stage", [
        "0 - Need (Latent Pain)",
        "1 - Sourcing (Evaluating Options)", 
        "2 - Selected (Validating Fit)"
    ])
    
    raid_role = st.selectbox("RAID Role", [
        "Recommender (Champion)", 
        "Agree’er (Veto Power)", 
        "Decision Maker (Signer)"
    ])
    
    rubie_role = st.selectbox("RUBIE POV", [
        "Benefactor (Cares about Results/Outcomes)", 
        "Economic Buyer (Cares about ROI)",
        "User (Cares about Usability)",
        "Implementor (Cares about Feasibility)"
    ])

# --- COL 2: THE GOAL ---
with col2:
    st.header("2. The Goal")
    st.info("What is the purpose of this call?")
    
    call_goal = st.selectbox("Call Objective", [
        "Discovery: Diagnose the 'Change' (Pain)",
        "Progression: De-Risk the Future (Adoption)"
    ], help="Select 'Discovery' if you don't know the pain yet.")

# --- COL 3: THE FOCUS ---
with col3:
    st.header("3. The Focus")
    if "Discovery" in call_goal:
        st.warning("Discovery Mode Active")
        crush_focus = "C - Change (Why is Status Quo failing?)"
        st.write(f"Focusing on uncovering **Change** for the **{rubie_role.split('(')[0]}**.")
    else:
        st.success("Progression Mode Active")
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
            inputs = f"""
            CONTEXT: CDM {cdm_stage}, RAID {raid_role}, RUBIE {rubie_role}
            GOAL: {call_goal}
            FOCUS: {crush_focus}
            """
            
            model = genai.GenerativeModel(selected_model)
            final_prompt = f"{CRUSH_SYSTEM_INSTRUCTION}\n\nTASK: Generate Script for:\n{inputs}"

            response = model.generate_content(final_prompt)
            
            st.markdown("---")
            st.markdown(response.text)
            
            if "Discovery" in call_goal:
                 st.info("💡 **CRUSH Logic:** You are probing the **Current State** to find the gap. [cite_start]Once they admit the gap, you have established **Change** [cite: 19-20].")
            else:
                 [cite_start]st.info(f"💡 **CRUSH Logic:** You are de-risking the **Future State** ({crush_focus.split('-')[1]}) so they feel safe to move[cite: 540].")

        except Exception as e:
            st.error(f"Error: {e}")
