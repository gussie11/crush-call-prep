import streamlit as st
import google.generativeai as genai

# --- 1. APP CONFIGURATION ---
st.set_page_config(page_title="CRUSH Sales Coach", page_icon="🦁", layout="wide")

# --- 2. THE CRUSH BRAIN (System Prompt) ---
# This instruction embeds the canonical logic to detect "Traps" and enforce "Adoption Risk" thinking.
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
* **RAID:**
    * *Recommender:* Needs ammunition to sell internally.
    * *Agree’er:* Needs risk mitigation (Veto power).
    * *Informer:* Needs technical accuracy.
    * *Decision Maker:* Needs accountability protection.
* **RUBIE (The POV):**
    * *User:* Fears friction/difficulty.
    * *Implementor:* Fears complexity/failure.
    * *Economic Buyer:* Fears financial loss/ROI.
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
* Provide 3 distinct questions to ask this specific person (Role: {raid_role}, POV: {rubie_role}) to uncover their hidden Adoption Risk.

Tone: Direct, coaching, authoritative. No fluff.
"""

# --- 3. API SETUP ---
# Tries to find key in secrets first, otherwise asks in sidebar
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = st.sidebar.text_input("Enter Google API Key", type="password")

if not api_key:
    st.warning("⚠️ Please enter your Google API Key to activate the Coach.")
    st.stop()

genai.configure(api_key=api_key)

# --- 4. THE INTERFACE ---
st.title("🦁 CRUSH Sales Call Coach")
st.markdown("### Decision Architecture & Risk Analysis")
st.caption("Don't just 'check in'. Architect the decision.")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("1. The Context")
    st.info("Where are they in the decision?")
    
    # CDM Selector
    cdm_stage = st.selectbox(
        "CDM Stage (The Company Journey)",
        [
            "0 - Need (Latent Pain)",
            "1 - Sourcing (Evaluating Options)",
            "2 - Selected (Vendor Chosen)",
            "3 - Ordered (Commercials)",
            "4 - Usage (Implementation)",
            "5 - Adoption (Value Realized)",
            "6 - Assess (Renewal/Pivot)"
        ],
        help="Stage 0-1 = Pain Focus. Stage 2+ = Adoption Risk Focus."
    )
    
    st.info("Who are you meeting?")
    # RAID Selector
    raid_role = st.selectbox(
        "RAID Role (Decision Function)",
        ["Recommender (Driver)", "Agree’er (Veto Power)", "Informer (Expert)", "Decision Maker (Signer)"],
        help="Who is this person in the buying committee?"
    )
    
    # RUBIE Selector
    rubie_role = st.selectbox(
        "RUBIE POV (Adoption View)",
        ["User (Usability)", "Implementor (Feasibility)", "Benefactor (Outcomes)", "Economic Buyer (ROI)", "Ripple (Impacted)"],
        help="What creates value (or fear) for this specific person?"
    )

with col2:
    st.header("2. The Plan")
    st.success("Draft your approach")
    
    user_draft = st.text_area(
        "Paste your Script, Email, or Goal for the call:",
        height=250,
        placeholder="e.g. 'Hi Sarah, just checking in to see if you have signed the contract yet. We are excited to get started...'"
    )
    
    run_button = st.button("🦁 Coach Me", type="primary", use_container_width=True)

# --- 5. THE OUTPUT ---
if run_button:
    if not user_draft:
        st.error("Please enter a draft first.")
    else:
        with st.spinner("Analyzing Adoption Risk..."):
            try:
                # Initialize Model
                model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=CRUSH_SYSTEM_INSTRUCTION)
                
                # Construct Prompt
                prompt_content = f"""
                CONTEXT:
                - CDM Stage: {cdm_stage}
                - RAID Role: {raid_role}
                - RUBIE POV: {rubie_role}
                
                USER DRAFT:
                {user_draft}
                """
                
                # Generate
                response = model.generate_content(prompt_content)
                
                # Render
                st.markdown("---")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Error: {e}")

# --- 6. SIDEBAR REFERENCE ---
with st.sidebar:
    st.markdown("### CRUSH Reference")
    st.markdown("""
    **Proximity Rule:**
    * ❌ Level 4: "Hope you are well"
    * ✅ Level 2: "Reference to shared contact"
    
    **Focus Rule:**
    * 📉 Early Stage: Sell **Change/Results**
    * 📈 Late Stage: Sell **Usage/Support**
    """)
