import streamlit as st
import google.generativeai as genai
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="CRUSH Sales Coach", page_icon="🦁", layout="wide")

# --- 2. CRUSH LOGIC (The Brain) ---
CRUSH_SYSTEM_INSTRUCTION = """
You are an expert Sales Coach specialized in the **CRUSH Methodology**.
Your goal is to coach a salesperson to prepare for a specific interaction. 
You must critique their plan based on **Adoption Risk** (Fear of the Future), not just "Pain" (The Past).

### THE LOGIC (Use this strictly):

**1. THE PROXIMITY TRAP (The Opener)**
* **Rule:** "Just checking in" or "Hope you are well" is **Level 4 Proximity (Cliché)**. It triggers a cortisol (threat) response.
* **Action:** If the user's draft includes clichés, REJECT it. Demand **Level 2 (Transferred)** or **Level 3 (Related)** context.

**2. THE PAIN TRAP (CDM Context)**
* **Rule:** In CDM Stages 0-1, "Pain" drives the look. But in **Stages 2-5**, "Adoption Risk" drives the stall.
* **Action:** If the CDM Stage is 2 (Selected) or higher, and the user is still talking about "Business Pain," WARN THEM. They should be talking about **Usage, Support, and Harmonization**.

**3. THE PERSON TRAP (RAID & RUBIE)**
* **Rule:** You cannot solve a "Person Fear" with a "Company Goal."
* **RAID:** Recommender (Driver), Agree’er (Veto), Informer (Expert), Decision Maker (Signer).
* **RUBIE:** User (Usability), Implementor (Feasibility), Economic Buyer (ROI).
* **Action:** Ensure the talking points match the specific **RUBIE** fear. (e.g., Don't sell ROI to an Implementor).

### YOUR OUTPUT FORMAT:

**1. 🛡️ Diagnosis & Trap Check**
* **Proximity Check:** (Pass/Fail) - Did they use a cliché?
* **Focus Check:** (Pain vs. Adoption Risk) - Are they solving the right problem for CDM Stage {stage}?
* **Empathy Check:** Are they addressing the {rubie_role}'s specific fear, or just pitching features?

**2. 🦁 The CRUSH Rewrite**
* Rewrite the Opening/Talking Points to be:
    * **Low Risk:** (Address Support/Harmonization).
    * **High Context:** (Level 2/3 Proximity).
    * **Decision-Oriented:** Move to the next Decision Boundary.

**3. ❓ The Golden Questions**
* Provide 3 distinct questions to ask this specific person to uncover their hidden Adoption Risk.

Tone: Direct, coaching, authoritative. No fluff.
"""

# --- 3. API SETUP ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = st.sidebar.text_input("Enter Google API Key", type="password")

if not api_key:
    st.warning("⚠️ Enter API Key to continue.")
    st.stop()

genai.configure(api_key=api_key)

# --- 4. ROBUST MODEL FINDER ---
@st.cache_resource
def get_best_model():
    """
    Dynamically lists available models and picks the best one.
    Returns: (model_name, supports_system_instructions_boolean)
    """
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    except Exception as e:
        # If list_models fails, default to a safe bet
        return 'gemini-pro', False

    # Priority list
    priorities = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']
    
    for priority in priorities:
        for available in available_models:
            if priority in available:
                # 1.5 models support system instructions natively
                supports_sys = '1.5' in available 
                return available, supports_sys
    
    # Fallback
    return 'gemini-pro', False

# --- 5. UI LAYOUT ---
st.title("🦁 CRUSH Sales Call Coach")
st.caption("Contextual Adoption Risk Analyzer")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("1. Context")
    cdm_stage = st.selectbox("CDM Stage", [
        "0 - Need", "1 - Sourcing", "2 - Selected", 
        "3 - Ordered", "4 - Usage", "5 - Adoption", "6 - Assess"
    ])
    raid_role = st.selectbox("RAID Role", ["Recommender", "Agree’er", "Informer", "Decision Maker"])
    rubie_role = st.selectbox("RUBIE POV", ["User", "Implementor", "Benefactor", "Economic Buyer", "Ripple"])

with col2:
    st.header("2. Draft")
    user_draft = st.text_area("Paste your script/email:", height=200)
    run_btn = st.button("Coach Me", type="primary", use_container_width=True)

# --- 6. EXECUTION ---
if run_btn and user_draft:
    with st.spinner("Analyzing..."):
        try:
            # 1. Get the best available model
            model_name, supports_sys = get_best_model()
            
            # 2. Build the Prompt
            if supports_sys:
                # Modern Method (1.5)
                model = genai.GenerativeModel(model_name, system_instruction=CRUSH_SYSTEM_INSTRUCTION)
                final_prompt = f"CONTEXT: CDM {cdm_stage}, RAID {raid_role}, RUBIE {rubie_role}\n\nDRAFT:\n{user_draft}"
            else:
                # Legacy Method (1.0) - Prepend instructions manually
                model = genai.GenerativeModel(model_name)
                final_prompt = f"{CRUSH_SYSTEM_INSTRUCTION}\n\nTASK:\nAnalyze this:\nCONTEXT: CDM {cdm_stage}, RAID {raid_role}, RUBIE {rubie_role}\n\nDRAFT:\n{user_draft}"

            # 3. Generate
            response = model.generate_content(final_prompt)
            
            # 4. Display
            st.success(f"Connected to: {model_name}")
            st.markdown("---")
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"Error: {e}")
            st.info("Try checking your API key permissions or updating the library locally with: pip install --upgrade google-generativeai")
