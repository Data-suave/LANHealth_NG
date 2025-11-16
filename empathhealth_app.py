import streamlit as st
import re

# === NIGERIAN FLAG + MEDICAL THEME ===
st.set_page_config(page_title="The LANHealth NG", page_icon="NG", layout="wide")

# Custom CSS: Green & White (Nigeria Flag) + Medical Blue
st.markdown("""
<style>
    /* Set the whole app background to white */
    body, .block-container {
        background-color: white !important;
        color: #333333; /* Dark text for readability */
    }

    /* Header bar (Nigeria green) */
    header, .css-18e3th9 {
        background-color: #008751 !important;
        color: white !important;
    }

    /* Buttons (Nigeria green) */
    .stButton>button {
        background-color: #008751;
        color: white;
        font-weight: bold;
        border-radius: 6px;
        padding: 8px 16px;
    }

    /* Text inputs */
    .stTextInput>div>input {
        font-size: 1.1rem;
        padding: 12px;
        border: 1px solid #0066CC;
        border-radius: 6px;
    }

    /* Progress bar (medical blue) */
    .stProgress > div > div > div > div {
        background-color: #0066CC;
    }

    /* Urgency colors */
    .high-urgency {color: #CC0000; font-weight: bold;}
    .medium-urgency {color: #FF8800;}
    .low-urgency {color: #008751;}

    /* Info boxes (light medical blue background) */
    .stInfo {
        background-color: #E6F7FF;
        border-left: 5px solid #0066CC;
    }
</style>
""", unsafe_allow_html=True)


# === EXPANDED SYMPTOMS (40 TOTAL) ===
SYMPTOMS = {
    'headache': {'advice': 'Rest, hydrate. Common in malaria or stress.', 'urgency': 'low', 'causes': ['Malaria', 'Stress', 'Meningitis']},
    'fever': {'advice': 'Cool sponge bath. Monitor temp.', 'urgency': 'medium', 'causes': ['Malaria', 'Lassa', 'Typhoid']},
    'cough': {'advice': 'Honey + warm water. Avoid smoke.', 'urgency': 'medium', 'causes': ['TB', 'Diphtheria', 'COVID']},
    'diarrhea': {'advice': 'Sip ORS every 5 mins. Urgent if blood.', 'urgency': 'high', 'causes': ['Cholera', 'Typhoid']},
    'rash': {'advice': 'Don’t scratch. Note blisters.', 'urgency': 'high', 'causes': ['Mpox', 'Lassa', 'Measles']},
    'vomiting': {'advice': 'Small sips. Rest stomach.', 'urgency': 'medium', 'causes': ['Lassa', 'Cholera']},
    'stiff neck': {'advice': 'EMERGENCY! Go to hospital NOW.', 'urgency': 'high', 'causes': ['Meningitis', 'CSM']},
    'swollen neck': {'advice': 'Don’t press. Monitor breathing.', 'urgency': 'high', 'causes': ['Diphtheria']},
    'chills': {'advice': 'Layer up. Track fever cycles.', 'urgency': 'medium', 'causes': ['Malaria', 'Lassa']},
    'fatigue': {'advice': 'Rest, eat beans. Check anemia.', 'urgency': 'low', 'causes': ['Malaria', 'HIV']},
    'sore throat': {'advice': 'Salt water gargle. Rest voice.', 'urgency': 'medium', 'causes': ['Diphtheria', 'Strep', 'Dust']},
    'jaundice': {'advice': 'Avoid alcohol/oily food. Urgent yellow eyes!', 'urgency': 'high', 'causes': ['Hepatitis', 'Yellow Fever']},
    'weakness': {'advice': 'Rest, eat well. Check for paralysis.', 'urgency': 'medium', 'causes': ['Polio', 'Malnutrition']},
    'joint pain': {'advice': 'Rest affected area, Take NSAID such as diclofenac not more than 150 mg perday. Avoid mosquitoes.', 'urgency': 'medium', 'causes': ['Chikungunya', 'Dengue']},
    'chest pain': {'advice': 'Sit up, loosen clothes. Call 112 if severe.', 'urgency': 'high', 'causes': ['Heart attack', 'Pneumonia', 'TB']},
    'shortness of breath': {'advice': 'Sit upright. Open windows. Urgent!', 'urgency': 'high', 'causes': ['Asthma', 'Heart failure', 'Pneumonia']},
    'night sweats': {'advice': 'Change blanket. Test for TB/HIV.', 'urgency': 'medium', 'causes': ['TB', 'HIV', 'Malaria']},
    'weight loss': {'advice': 'Track diet. See doctor if >5kg.', 'urgency': 'medium', 'causes': ['Malnutrition','TB', 'HIV', 'Cancer', 'Hyperthyroidism']},
    'swollen legs': {'advice': 'Elevate legs. Reduce salt.', 'urgency': 'medium', 'causes': ['Heart failure', 'Kidney disease', 'Pregnancy']},
    'bleeding gums': {'advice': 'Rinse with salt water. Vitamin C.', 'urgency': 'medium', 'causes': ['Scurvy', 'Gingivitis', 'Lassa']},
    'convulsion': {'advice': 'Clear space. Do NOT insert spoon!', 'urgency': 'high', 'causes': ['Meningitis', 'Cerebral malaria', 'Epilepsy']},
    'snake bite': {'advice': 'Immobilize limb. DO NOT suck! Rush to hospital.', 'urgency': 'high', 'causes': ['Carpet viper (North)', 'Puff adder']},
    'body itching': {'advice': 'Avoid scratching. Use calamine lotion.', 'urgency': 'medium', 'causes': ['Scabies', 'Fungal infection', 'Allergy']},
    'yellow eyes': {'advice': 'Urgent! Avoid alcohol. See doctor.', 'urgency': 'high', 'causes': ['Hepatitis', 'Liver disease','Jaundice','Sickle Cell Disease']},
    'blood in stool': {'advice': 'Stop NSAIDs. Urgent if black!', 'urgency': 'high', 'causes': ['Ulcer', 'Hemorrhoids', 'Typhoid']},
    'frequent urination': {'advice': 'Reduce sugar. Test for diabetes.', 'urgency': 'medium', 'causes': ['Diabetes', 'Urinary Tract Infection', 'Pregnancy']},
    'dizziness': {'advice': 'Sit down. Hydrate. Check BP.', 'urgency': 'medium', 'causes': ['Low BP', 'Anemia', 'Dehydration','low blood sugar']},
    'palpitations': {'advice': 'Avoid caffeine. Rest. Monitor.', 'urgency': 'medium', 'causes': ['Anxiety', 'Arrhythmia', 'Thyroid']},
    'crisis pain': {'advice': 'Warm compress. Hydrate. Go to hospital!', 'urgency': 'high', 'causes': ['Sickle Cell Crisis']},
    'abdominal pain': {'advice': 'Note location. Avoid heavy food.', 'urgency': 'medium', 'causes': ['Typhoid', 'Ulcer', 'Appendicitis']}
}

# === HOSPITAL & EMERGENCY DATA ===
STATE_PATTERNS = {
    r'\blagos\b': 'Lagos',
    r'\babuja\b': 'FCT (Abuja)',
    r'\bibadan\b': 'Oyo',
    r'\bkano\b': 'Kano',
    r'\benugu\b': 'Enugu',
    r'\bjos\b': 'Plateau',
    r'\bowerri\b': 'Imo',
    r'\bport harcourt\b': 'Rivers',
    r'\bcalabar\b': 'Cross River',
    r'\babeokuta\b': 'Ogun',
    r'\b zaria\b': 'Kaduna',
    r'\b uyo\b': 'Akwa Ibom'
}

HOSPITALS_BY_STATE = {
    'Lagos': ['Lagos University Teaching Hospital (LUTH), Ikeja', 'Lagos State University Teaching Hospital (LASUTH), Ikeja', 'General Hospital Lagos Island'],
    'FCT (Abuja)': ['National Hospital Abuja', 'University of Abuja Teaching Hospital (UATH), Gwagwalada', 'Asokoro District Hospital'],
    'Oyo': ['University College Hospital (UCH), Ibadan', 'Oyo State General Hospital, Ibadan', 'Adeoyo State Hospital, Ibadan'],
    'Kano': ['Aminu Kano Teaching Hospital (AKTH)', 'Murtala Muhammad Specialist Hospital, Kano', 'Hasiya Bayero Paediatric Hospital'],
    'Enugu': ['University of Nigeria Teaching Hospital (UNTH), Ituku Ozalla', 'Enugu State University of Science and Technology Teaching Hospital', 'General Hospital Enugu'],
    'Plateau': ['Jos University Teaching Hospital (JUTH)', 'Plateau State Specialist Hospital, Jos', 'Bingham University Teaching Hospital, Jos'],
    'Imo': ['Federal Medical Centre (FMC) Owerri', 'Imo State Specialist Hospital, Umuguma', 'Heritage Specialist Hospital, Owerri'],
    'Rivers': ['University of Port Harcourt Teaching Hospital (UPTH)', 'Rivers State University Teaching Hospital, Port Harcourt', 'Braithwaite Memorial Specialist Hospital'],
    'Cross River': ['University of Calabar Teaching Hospital (UCTH)', 'Asi Ukpo Diagnostic Center', 'Mary Slessor General Hospital, Calabar', 'St. Luke\'s Hospital, Anantigha'],
    'Ogun': ['Olabisi Onabanjo University Teaching Hospital, Sagamu', 'Federal Medical Centre, Abeokuta', 'General Hospital Ijaiye, Abeokuta'],
    'Kaduna': ['Ahmadu Bello University Teaching Hospital (ABUTH), Zaria', 'Barau Dikko Teaching Hospital, Kaduna', 'St. Gerard\'s Catholic Hospital, Kaduna'],
    'Akwa Ibom': ['University of Uyo Teaching Hospital (UUTH)', 'St. Luke\'s Hospital, Anua Obio', 'General Hospital Ikot Ekpene']
}

EMERGENCY_NUMBERS = {
    'National': '112 (All emergencies)',
    'Lagos': '767 (LASEMA)',
    'NHIS': '0800 9700 4357 (NHIS)',
    'Calabar': '08134461293 (NNRH Emergency)',
    'Calabar 2':'08198120659 (UCTH Emergency)'
}
import random

# === EMPATHY MESSAGES ===
EMPATHY_MESSAGES = [
    "It’s okay and it is normal to be anxious.",
    "You are not alone, many people feel this way.",
    "It’s natural to worry when you don’t feel well.",
    "Your feelings are valid,take a deep breath, let’s take it step by step.",
    "Health concerns can be stressful, but you’re doing the right thing by checking."
]

# === FUNCTIONS ===
def detect_emotion(q): 
    return 'anxious' if any(w in q.lower() for w in ['scared', 'worry', 'afraid','petrified']) else 'neutral'

def get_state_from_address(addr):
    addr_lower = addr.lower()
    for pattern, state in STATE_PATTERNS.items():
        if re.search(pattern, addr_lower): return state
    return None

def search_advice(query):
    q = query.lower()
    matched = [s for s in SYMPTOMS if s in q]
    if not matched:
        return "Please describe your symptom clearly."
    
    data = SYMPTOMS[matched[0]]
    
    # Pick a random empathy message
    empathy = random.choice(EMPATHY_MESSAGES)
    
    # Add extra reassurance if anxious words are detected
    prefix = "It’s normal to feel worried, many do. " if detect_emotion(query) == 'anxious' else ""
    
    causes = ', '.join(data['causes'])
    urgency_class = f"<span class='{data['urgency']}-urgency'>"
    
    return f"{empathy}\n\n{prefix}{data['advice']}\n\n**Urgency:** {urgency_class}{data['urgency'].upper()}</span>\n**Possible causes:** {causes}"

# === STREAMLIT UI ===
st.title("TheLANHealth NG")
st.markdown("**Digital Health Guide for Nigerians |est: Nov 2025 | I am not the replacement of a doctor**")

col1, col2 = st.columns([3, 1])
with col2:
    st.info("**Current Outbreaks in Nigeria:** Lassa, Mpox, Diphtheria, Cholera, Measles")

with col1:
    query = st.text_input("**What are you feeling?**", placeholder="e.g., 'crisis pain in Lagos'")
    address = st.text_input("**Your location?** (e.g., 'Ikeja, Lagos')", placeholder="For nearby hospitals")

if st.button("Get Help", type="primary"):
    if not query.strip():
        st.warning("Please enter your symptom.")
    else:
        with st.spinner("Thinking..."):
            advice = search_advice(query)
        st.markdown(advice, unsafe_allow_html=True)
        
        # Urgency bar
        urgency = next((SYMPTOMS[s]['urgency'] for s in SYMPTOMS if s in query.lower()), 'low')
        st.progress({'low': 0.3, 'medium': 0.6, 'high': 1.0}[urgency])
        
        # Hospitals
        if address:
            state = get_state_from_address(address)
            if state and state in HOSPITALS_BY_STATE:
                st.subheader("Nearby Hospitals:")
                for h in HOSPITALS_BY_STATE[state]:
                    st.write(f"• {h}")
            else:
                st.info("Add city/state for hospital suggestions.")
        
        # Emergency
        st.subheader("Emergency Contacts")
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1: st.info(EMERGENCY_NUMBERS['National'])
        with c2: st.info(EMERGENCY_NUMBERS['Lagos'])
        with c3: st.info(EMERGENCY_NUMBERS['NHIS'])
        with c4: st.info(EMERGENCY_NUMBERS['Calabar'])
        with c5: st.info(EMERGENCY_NUMBERS['Calabar 2'])

st.caption("For TheLAN Network | Built with love for Nigerians NG")