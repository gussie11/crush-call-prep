import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="CRUSH Sales Coach", page_icon="🦁", layout="wide")

st.title("🦁 CRUSH Sales Call Coach")
st.markdown("### Pre-Call Preparation & Future-State Architecting")

# --- 2. CRUSH SYSTEM PROMPT (Fully Integrated) ---
CRUSH_SYSTEM_INSTRUCTION = """
You are an expert Sales Coach specialized in the **CRUSH Methodology**.
Your specific task is **Call Preparation**. You must prepare the user for a sales interaction by analyzing two parallel tracks: **The Company (Logic)** and **The People (Emotion)**.

### 1. THE CORE PHILOSOPHY (Adoption Risk):
* **The Shift:** In early stages, customers are driven by *Pain/Triggers*. As they progress, pain fades and **Adoption Risk** (Fear of the Future) becomes dominant.
* **The Goal:** We do not "persuade" or "close." We help the customer **evaluate the future state** to reduce uncertainty.
* **Pivot Point:** Watch out for CDM Stage 6 (Assess). If the customer pivots here, they choose between "Expansion" (Low Risk) or "New" (High Risk).

### 2. THE CRUSH MODEL (The Destination) [Adoption Framework]:
You must architect the "Future State" using these 5 specific elements:
* **C - Change:** Why is the current state no longer viable? (The starting point).
* **R - Results:** What does success look like? (Anchors value).
* **U - Usage:** *Day-to-day reality.* How does it fit workflows? Who uses it? (Realism vs. Theory).
* **S - Support:** How are issues/learning handled? (Reduces fear of abandonment).
* **H - Harmonization:** How does it fit the *broader environment* (Policy, Systems, Politics)? (Addresses hidden friction).

### 3. THE ARCHITECTURE (Context):

**TRACK A: THE COMPANY PATH (Decision Journey)**
* **CDM Stages:** 0-Need, 1-Source, 2-Select, 3-Order, 4-Use, 5-Adopt (GOAL), 6-Assess.
* **Logic:** Companies balance **Goals** (Why change?) vs. **Risks** (What if we fail?).

**TRACK B: THE PEOPLE PATH (Decision Roles)**
* **RAID Roles:**
    * *Recommender:* Drives process (80% of decision).
    * *Agree’er:* Veto power (Risk/Finance/Legal).
    * *Informer:* SME (Data/Specs).
    * *Decision Maker:* Final accountability.
* **RUBIE (Point of View):**
    * *Ripple:* Indirectly affected (downstream impact).
    * *User:* Usability/Effort.
    * *Benefactor:* Results/Outcomes.
    * *Implementor:* Feasibility/Complexity.
    * *Economic Buyer:* ROI/Cost.

### YOUR OUTPUT FORMAT:
The user will input their **Call Context**. You will output a **Call Plan** in this structure:

**1. 🗺️ The Map (CDM Diagnosis)**
* **Current Stage:** Identify the CDM Stage (0-9).
* **Risk Warning:** If Stage is >2, warn the user if they are focusing too much on "Pain" instead of "Adoption Risk" (Usage/Support/Harmonization).

**2. 🧠 The Psychology (RAID & RUBIE)**
* **The Role:** Identify the RAID role (e.g., "Agree'er").
* **The Personal Fear:** Deduce the fear based on RUBIE. (e.g., "The Implementor does not care about ROI; they fear working weekends due to complex 'Usage'.")

**3. 🦁 The Strategy (The CRUSH Elements)**
* **Define the Gap:** Contrast the *Current State* (Change) with the *Future State* (Results).
* **Reduce the Risk:** Script a talking point specifically addressing **Usage**, **Support**, or **Harmonization** to lower their anxiety.
* **Proximity Check:** Ensure opening is Level 2 (Transferred) or 3 (Related). Reject Level 4 (Clichés).

**4. 🗣️ Recommended Questions**
* Provide 3 specific questions to uncover **Adoption Risk** (not just "pain").

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

# --- 4. INPUT INTERFACE ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📍 The Context")
    cdm_stage = st.selectbox("Where is the customer on the CDM?", 
                             ["0 - Need", "1 - Sourcing", "2 - Selected", 
                              "3 - Ordered", "4 - Usage", "5 - Adoption", "6 - Assess", "Renewal/Expand"])
    
    raid_role = st.multiselect("Who are you meeting? (RAID)", 
                               ["Recommender", "Agree'er", "Informer", "Decision Maker"])
    
    rubie_pov = st.multiselect("What is their Point of View? (RUBIE)",
                               ["Ripple", "User", "Benefactor", "Implementor", "Economic Buyer"])

with col2:
    st.subheader("📝 The Scenario")
    scenario_input = st.text_area("Describe the situation / meeting goal:", height=200,
                                  placeholder="Ex: Meeting with the CIO (Agree'er). We are the incumbent, but they are looking at competitors. I need to secure the Renewal.")

# --- 5. GENERATION ---
if st.button("Generate Call Plan"):
    if not scenario_input:
        st.error("Please describe the scenario.")
    else:
        with st.spinner("Architecting Future State..."):
            model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=CRUSH_SYSTEM_INSTRUCTION)
            
            prompt = f"""
            CDM STAGE: {cdm_stage}
            RAID ROLES: {', '.join(raid_role)}
            RUBIE POV: {', '.join(rubie_pov)}
            SCENARIO: {scenario_input}
            """
            
            response = model.generate_content(prompt)
            st.markdown(response.text)
