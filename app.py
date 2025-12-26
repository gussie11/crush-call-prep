import streamlit as st
import google.generativeai as genai
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="CRUSH Progression Coach", page_icon="🦁", layout="wide")

# --- 2. CRUSH LOGIC (Progression / Solution Building) ---
CRUSH_SYSTEM_INSTRUCTION = """
You are an expert Sales Coach specialized in the **CRUSH Methodology**.
**CONTEXT:** This is a **PROGRESSION CALL** (Discovery/Solution Building). The door is open. 
Your goal is to help the user architect a collaborative session that moves the customer from "Interested" to "Decided."

### THE LOGIC (Use this strictly):

**1. THE "NO VALUE" TRAP (The Opener)**
* **The Error:** "Just checking in" or "Touching base." This signals you have no value to add.
* **The Fix:** Progression calls require a **Visual Anchor** or **Recap**.
* **Rule:** If the draft lacks a clear "Purpose" or "Recap of previous value," REJECT it. Demand a "Collaborative Agenda" (e.g., "To ensure we are on track for your Q3 goals...").

**2. THE "FEATURE" TRAP (Solution Building)**
* **The Error:** Showing the product features (The "What").
* **The Fix:** Architecting the **Future State** (The "How").
* **Rule:** * If CDM Stage is 0-1: Focus on **Change** (Why Change?) and **Results** (Value).
    * If CDM Stage is 2-5: Focus on **Usage** (Workflow fit) and **Support** (Safety net).
    * *Critique:* If they are pitching features to an "Implementor" or "User," warn them to switch to "Usage" (Day-to-day reality).

**3. THE "ACTIVITY" TRAP (The Goal)**
* **The Error:** Ending with "Let me know what you think" or "Let's chat again soon."
* **The Fix:** Driving to the next **Decision Boundary**.
* **Rule:** The Call to Action (CTA) must target a *Decision*, not just an activity. (e.g., "Decide on the pilot scope" vs "Have another meeting").

### YOUR OUTPUT FORMAT:

**1. 🛡️ CRUSH Diagnosis**
* **Agenda Check:** Does the opener lower "Cognitive Load" or increase it with fluff?
* **Future-State Gap:** Are they selling the *Product* or the *Adoption* (Usage/Support)?
* **Empathy Check:** Does this specifically address the {rubie_role}'s fear? (e.g., "You are ignoring the User's fear of extra work.")

**2. 🦁 The CRUSH Rewrite**
* Rewrite the Opener/Talking Points to be:
    * **Collaborative:** Use "We" language.
    * **Visual/Structured:** "First we will cover X, then resolve Y."
    * **De-Risked:** Address **Adoption Risk** head-on.

**3. ❓ The Golden Questions (Discovery)**
* Provide 3 deep discovery questions to ask the {raid_role} to uncover hidden blockers (Harmonization/Politics).

Tone: Collaborative, strategic, "Orchestrator" vibe.
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

# --- 4. ROBUST MODEL FINDER (Safe Mode) ---
@st.cache_resource
def get_best_model():
    """
    Dynamically lists available models and picks the best one.
    Returns: (model_name, supports_system_instructions_boolean)
    """
    try:
        # Get all models that support generating content
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    except Exception as e:
        return 'gemini-pro', False

    # Priority: 1.5 Flash -> 1.5 Pro -> 1.0 Pro
    priorities = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']
    
    for priority in priorities:
        for available in available_models:
            if priority in available:
                supports_sys = '1.5' in available 
                return available, supports_sys
    
    return 'gemini-pro', False

# --- 5. UI LAYOUT ---
st.title("🦁 CRUSH Progression Coach")
st.caption("Discovery & Solution Building | Architecting the Future State")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("1. The Context")
    st.info("Goal: Collaboration/De-risking")
    
    cdm_stage = st.selectbox("CDM Stage", [
        "1 - Sourcing (Evaluating Options)", 
        "2 - Selected (Validating Fit)", 
        "3 - Ordered (Commercials/Legal)", 
        "4 - Usage (Implementation Planning)", 
        "5 - Adoption (Value Review)", 
        "6 - Assess (Expansion/Renewal)"
    ], help="Where is the company in the decision journey?")
    
    raid_role = st.selectbox("RAID Role", 
                             ["Recommender (The Champion)", "Agree’er (The Veto)", "Informer (The Expert)", "Decision Maker (The Signer)"],
                             help="Who are you collaborating with?")
    
    rubie_role = st.selectbox("RUBIE POV", 
                              ["User (Usability)", "Implementor (Feasibility)", "Benefactor (Outcomes)", "Economic Buyer (ROI)", "Ripple (Impacted)"],
                              help="What is their lens on the future?")

with col2:
    st.header("2. The Plan")
    st.success("Paste your Agenda / Talking Points")
    user_draft = st.text_area("Your Draft:", height=250, placeholder="e.g. 'Agenda: 1. Review requirements. 2. Show demo. 3. Discuss pricing.'")
    
    run_btn = st.button("🦁 Coach My Call", type="primary", use_container_width=True)

# --- 6. EXECUTION ---
if run_btn:
    if not user_draft:
        st.error("Please enter a draft first.")
    else:
        with st.spinner("Architecting the Decision..."):
            try:
                # 1. Get Model
                model_name, supports_sys = get_best_model()
                
                # 2. Build Prompt
                context_block = f"CONTEXT: PROGRESSION CALL. CDM {cdm_stage}, RAID {raid_role}, RUBIE {rubie_role}"
                
                if supports_sys:
                    model = genai.GenerativeModel(model_name, system_instruction=CRUSH_SYSTEM_INSTRUCTION)
                    final_prompt = f"{context_block}\n\nUSER DRAFT:\n{user_draft}"
                else:
                    model = genai.GenerativeModel(model_name)
                    final_prompt = f"{CRUSH_SYSTEM_INSTRUCTION}\n\nTASK: Analyze this.\n{context_block}\n\nUSER DRAFT:\n{user_draft}"

                # 3. Generate
                response = model.generate_content(final_prompt)
                
                # 4. Display
                st.success(f"Connected to: {model_name}")
                st.markdown("---")
                st.markdown(response.text)
            
            except Exception as e:
                st.error(f"Error: {e}")
                st.info("If this persists, check your API key.")
