import streamlit as st
import math

st.set_page_config(page_title="PrecisionPK | Clinical Dosing", layout="wide", page_icon="🧬")

# --- Custom CSS for Styling ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .main .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1100px; }
    h1, h2, h3, h4 { font-family: 'Inter', sans-serif; color: var(--text-color); }
    
    /* Metrics */
    div[data-testid="stMetric"], .stMetric {
        background-color: var(--secondary-background-color) !important;
        padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
        border-top: 4px solid #0ea5e9;
    }
    div[data-testid="stMetric"]:hover, .stMetric:hover { transform: translateY(-2px); transition: transform 0.2s ease; }
    
    /* Alerts using semi-transparent backgrounds to work on both themes */
    .alert-box {
        padding: 20px; border-radius: 12px; margin-bottom: 24px;
        border-left: 6px solid; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }
    .alert-info { background-color: rgba(2, 132, 199, 0.1); border-color: #0284c7; color: var(--text-color); }
    .alert-success { background-color: rgba(22, 163, 74, 0.1); border-color: #16a34a; color: var(--text-color); }
    .alert-warning { background-color: rgba(217, 119, 6, 0.1); border-color: #d97706; color: var(--text-color); }
    .alert-danger { background-color: rgba(220, 38, 38, 0.1); border-color: #dc2626; color: var(--text-color); }
    
    /* Buttons */
    .stButton>button {
        font-weight: 600; border-radius: 8px; transition: all 0.2s;
        border: 1px solid var(--text-color); opacity: 0.8;
    }
    .stButton>button:hover {
        transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); opacity: 1;
    }
    
    /* Headers */
    .primary-header {
        background: linear-gradient(135deg, #0f172a 0%, #334155 100%);
        color: #f8fafc !important; padding: 40px 30px; border-radius: 16px;
        margin-bottom: 30px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }
    .primary-header h1 { color: #f8fafc !important; margin: 0; font-size: 2.8rem; letter-spacing: -0.02em; }
    .primary-header p { color: #cbd5e1; margin-top: 10px; font-size: 1.1rem; font-weight: 400; }
    
    div[data-testid="stSidebarNav"] { display: none; }
    
    /* Section Headers */
    .analysis-header {
        background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%);
        color: white !important; padding: 14px 20px; border-radius: 10px;
        margin: 20px 0 16px 0; text-align: center; font-weight: 700; font-size: 1.15rem;
        letter-spacing: 0.03em; box-shadow: 0 4px 12px rgba(14,165,233,0.3);
    }
    .crcl-header {
        background: linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%);
        color: white !important; padding: 14px 20px; border-radius: 10px;
        margin: 24px 0 16px 0; text-align: center; font-weight: 700; font-size: 1.15rem;
        letter-spacing: 0.03em; box-shadow: 0 4px 12px rgba(139,92,246,0.3);
    }
    .obese-header {
        background: linear-gradient(135deg, #ef4444 0%, #f97316 100%);
        color: white !important; padding: 14px 20px; border-radius: 10px;
        margin: 24px 0 16px 0; text-align: center; font-weight: 700; font-size: 1.15rem;
        letter-spacing: 0.03em; box-shadow: 0 4px 12px rgba(239,68,68,0.3);
    }
    
    /* Badges */
    .bmi-badge {
        display: inline-block; padding: 4px 14px; border-radius: 20px;
        font-weight: 600; font-size: 0.9rem; margin-left: 8px;
    }
    .bmi-underweight { background: rgba(30, 64, 175, 0.2); color: #60a5fa; }
    .bmi-normal { background: rgba(22, 101, 52, 0.2); color: #4ade80; }
    .bmi-overweight { background: rgba(133, 77, 14, 0.2); color: #facc15; }
    .bmi-obese { background: rgba(153, 27, 27, 0.2); color: #f87171; }
    
    /* Selected Equation Box */
    .selected-eq-box {
        background-color: var(--secondary-background-color) !important;
        border-left: 4px solid #0ea5e9 !important;
    }
    .selected-eq-box .eq-title { color: var(--text-color) !important; }
    .selected-eq-box .eq-name { color: #0ea5e9 !important; }
    .selected-eq-box .eq-reason { color: var(--text-color) !important; opacity: 0.8; }
    .selected-eq-box .eq-value { color: #0ea5e9 !important; }
</style>
""", unsafe_allow_html=True)

# --- Drug Database ---
DRUG_DB = {
    "Digoxin": {"category": "Cardiovascular", "class": "Cardiac Glycoside", "target_peak": 1.5, "target_trough": 0.8, "mic": 0, "thera_min": 0.5, "thera_max": 2.0},
    "Procainamide": {"category": "Cardiovascular", "class": "Antiarrhythmic", "target_peak": 6.0, "target_trough": 4.0, "mic": 0, "thera_min": 4.0, "thera_max": 10.0},
    "Lidocaine": {"category": "Cardiovascular", "class": "Antiarrhythmic", "target_peak": 3.0, "target_trough": 1.5, "mic": 0, "thera_min": 1.5, "thera_max": 5.0},
    "Amiodarone": {"category": "Cardiovascular", "class": "Antiarrhythmic", "target_peak": 1.5, "target_trough": 1.0, "mic": 0, "thera_min": 1.0, "thera_max": 2.5}
}

# --- Helper Functions ---
def calc_ibw(sex, height_cm):
    height_in = height_cm / 2.54
    return (50 + 2.3 * max(0, height_in - 60)) if sex == "Male" else (45.5 + 2.3 * max(0, height_in - 60))

def calc_bmi(weight_kg, height_cm):
    height_m = height_cm / 100.0
    return weight_kg / (height_m ** 2) if height_m > 0 else 0

def calc_bsa(height_cm, weight_kg):
    return math.sqrt((height_cm * weight_kg) / 3600.0)

def calc_lbw(sex, weight_kg, height_cm):
    if sex == "Male":
        return (0.32810 * weight_kg) + (0.33929 * height_cm) - 29.5336
    return (0.29569 * weight_kg) + (0.41813 * height_cm) - 43.2933

def calc_ajbw(ibw, abw):
    return ibw + 0.4 * (abw - ibw)

def bmi_classify(bmi):
    if bmi < 18.5: return "Underweight", "bmi-underweight"
    if bmi < 25: return "Normal", "bmi-normal"
    if bmi < 30: return "Overweight", "bmi-overweight"
    return "Obese", "bmi-obese"

def calc_crcl(age, weight, sex, scr):
    crcl = ((140 - age) * weight) / (72 * scr)
    if sex == "Female": crcl *= 0.85
    return crcl

def calc_crcl_jelliffe(age, sex, scr):
    crcl = (98 - 0.8 * (age - 20)) / scr
    if sex == "Female": crcl *= 0.9
    return crcl

def calc_mdrd(age, sex, scr, race="Non black"):
    egfr = 175 * (scr ** -1.154) * (age ** -0.203)
    if sex == "Female": egfr *= 0.742
    return egfr

def calc_salazar_corcoran(sex, age, weight_kg, height_cm, scr):
    height_m = height_cm / 100.0
    if sex == "Male":
        return ((137 - age) * ((0.285 * weight_kg) + (12.1 * (height_m ** 2)))) / (51 * scr)
    return ((146 - age) * ((0.287 * weight_kg) + (9.74 * (height_m ** 2)))) / (60 * scr)

def determine_dosing_weight(abw, ibw):
    if abw < ibw: return abw
    if abw > 1.2 * ibw: return ibw + 0.4 * (abw - ibw)
    return ibw

# --- Header ---
st.markdown("""
<div class='primary-header'>
    <h1>🧬 PrecisionPK</h1>
    <p>Advanced Clinical Pharmacokinetics & Decision Support System</p>
</div>
""", unsafe_allow_html=True)

# --- Main Tabs ---
tab_setup, tab_results, tab_docs = st.tabs(["1. Patient & Drug Setup", "2. Dosing & PK Results", "3. Clinical Documentation"])

with tab_setup:
    # ===== PATIENT DEMOGRAPHICS =====
    st.subheader("👤 Patient Demographics")
    with st.container(border=True):
        n1, n2 = st.columns(2)
        patient_name = n1.text_input("Patient Name")
        patient_location = n2.text_input("Location")

        c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
        age = c1.number_input("Age", min_value=18, max_value=120, value=65)
        scr = c2.number_input("Scr", min_value=0.1, max_value=15.0, value=1.0, step=0.1)
        scr_unit = c3.selectbox("Scr Unit", ["mg/dL"], label_visibility="hidden")
        sex = c4.selectbox("Sex", ["Male", "Female"])

        h1, h2 = st.columns(2)
        height_input = h1.number_input("Height", min_value=0.0, value=170.0)
        height_unit = h2.selectbox("Height Unit", ["Centimeters", "Inches"], label_visibility="hidden")

        w1, w2 = st.columns(2)
        weight_input = w1.number_input("Weight", min_value=0.0, value=80.0)
        weight_unit = w2.selectbox("Weight Unit", ["Kilograms", "Pounds"], label_visibility="hidden")

        height_cm = height_input * 2.54 if height_unit == "Inches" else height_input
        abw = weight_input * 0.453592 if weight_unit == "Pounds" else weight_input

        race = st.selectbox("For MDRD equation, specify race", ["Non black", "Black"])
        scr_stable = st.selectbox("Is the serum creatinine (Scr) currently stable?", ["Yes", "No"])
        scr_ref = st.selectbox("Select serum creatinine reference standard",
                               ["Conventional serum creatinine value reported - scr (DEFAULT)",
                                "IDMS-traceable serum creatinine - scr"])

        is_hf = st.checkbox("Patient has Congestive Heart Failure (CHF)")

    st.divider()

    # ===== THERAPY SELECTION (moved before drug-specific parameters) =====
    st.subheader("💊 Therapy Selection")
    with st.container(border=True):
        available_drugs = list(DRUG_DB.keys())
        selected_drug = st.selectbox("Select Drug", available_drugs)
        drug_info = DRUG_DB[selected_drug]
        st.markdown(f"**Drug Class:** `{drug_info['class']}`")
        
        calc_mode = st.radio("Calculation Type", ["Initial regimen", "Dose adjustment"], horizontal=True)
        initial_method = None
        route = None
        css = vd_input = cl_input = dose_input = conc_input = None
        dose_adjust_old = None
        child_pugh_score = None
        
        # Initialize Digoxin-specific variables
        indication = "Select Indication"
        hf_severity = None
        css_initial = None
        crcl_hf_adjustment = None
        route_of_admin = "Select Route"
        dosage_form = "IV"
        bioavailability = 1.0
        thyroid_status = "Select Status"
        calculation_type = "Initial dosing"
        
        # ===== DIGOXIN-SPECIFIC PARAMETERS =====
        if selected_drug == "Digoxin":
            st.markdown("---")
            st.subheader("🔧 Digoxin-Specific Parameters")
            with st.container(border=True):
                d_col1, d_col2 = st.columns(2)
                
                indication = d_col1.selectbox(
                    "Indication",
                    ["Select Indication", "Heart Failure", "Atrial Fibrillation"],
                    help="Select the clinical indication for Digoxin",
                    key="digoxin_indication"
                )
                
                if indication == "Heart Failure":
                    hf_severity = d_col2.selectbox(
                        "Heart Failure Severity",
                        ["Select Severity", "Mild", "Moderate", "Severe"],
                        help="Severity affects renal clearance adjustment",
                        key="hf_severity"
                    )
                    css_initial = 0.8
                    
                    # Logic for HF severity → CrCl adjustment
                    if hf_severity == "Mild":
                        crcl_hf_adjustment = 40
                    elif hf_severity == "Moderate":
                        crcl_hf_adjustment = 20
                    elif hf_severity == "Severe":
                        crcl_hf_adjustment = 20
                        
                elif indication == "Atrial Fibrillation":
                    d_col2.info("No severity selection needed for Atrial Fibrillation")
                    css_initial = 1.2
                
                # Route of Administration & Bioavailability
                d_col3, d_col4 = st.columns(2)
                
                route_of_admin = d_col3.selectbox(
                    "Route of Administration",
                    ["Select Route", "Oral", "IV"],
                    help="Choose Oral or IV administration",
                    key="route_of_admin"
                )
                
                if route_of_admin == "Oral":
                    dosage_form = d_col4.selectbox(
                        "Oral Dosage Form",
                        ["Select Form", "Tablet", "Elixir", "Capsule"],
                        help="Different oral forms have different bioavailability",
                        key="dosage_form"
                    )
                    
                    # Set bioavailability based on form
                    if dosage_form == "Tablet":
                        bioavailability = 0.7
                    elif dosage_form == "Elixir":
                        bioavailability = 0.8
                    elif dosage_form == "Capsule":
                        bioavailability = 0.9
                elif route_of_admin == "IV":
                    bioavailability = 1.0
                    d_col4.info("IV bioavailability = 1.0 (100% absorption)")
                
                # Thyroid Status
                d_col5, d_col6 = st.columns(2)
                thyroid_status = d_col5.selectbox(
                    "Thyroid Status",
                    ["Select Status", "Normal", "Hyperthyroidism"],
                    help="Thyroid status affects Digoxin metabolism",
                    key="thyroid_status"
                )
                
                calculation_type = d_col6.selectbox(
                    "Calculation Type",
                    ["Initial dosing", "Dose adjustment", "Toxicity assessment", "Dosage form switching"],
                    help="Type of pharmacokinetic calculation",
                    key="calculation_type"
                )
        else:
            # ===== PROCAINAMIDE-SPECIFIC PARAMETERS =====
            if selected_drug == "Procainamide":
                st.markdown("---")
                st.subheader("🔧 Procainamide-Specific Parameters")
                with st.container(border=True):
                    # Route of Administration
                    p_col1, p_col2 = st.columns(2)
                    
                    p_route = p_col1.radio(
                        "Route of Administration",
                        ["IV", "Oral", "IM"],
                        horizontal=True,
                        key="procainamide_route"
                    )
                    
                    # Set bioavailability based on route
                    p_bioavailability = 1.0
                    if p_route == "Oral":
                        p_bioavailability = 0.85
                    # IV and IM both have F=1
                    
                    p_col2.info(f"**Bioavailability (F):** {p_bioavailability}")
                    
                    # Indication
                    p_col3, p_col4 = st.columns(2)
                    
                    p_indication = p_col3.radio(
                        "Indication",
                        ["Atrial", "Ventricular"],
                        horizontal=True,
                        key="procainamide_indication"
                    )
                    
                    # Acetylator Status
                    p_acetylator = p_col4.radio(
                        "Acetylator Status",
                        ["Fast", "Slow", "Unknown"],
                        horizontal=True,
                        key="procainamide_acetylator"
                    )
                    
                    # Measured NAPA level (optional)
                    st.markdown("**Measured Levels (Optional)**")
                    n1, n2 = st.columns(2)
                    
                    measured_procainamide = n1.number_input(
                        "Measured Procainamide Level (mcg/mL)",
                        min_value=0.0,
                        value=0.0,
                        step=0.1,
                        help="Enter measured procainamide level, 0 to skip",
                        key="measured_procainamide"
                    )
                    
                    measured_napa = n2.number_input(
                        "Measured NAPA Level (mcg/mL)",
                        min_value=0.0,
                        value=0.0,
                        step=0.1,
                        help="Enter measured NAPA level, 0 to skip",
                        key="measured_napa"
                    )
            else:
                # Initialize Procainamide variables for non-Procainamide drugs
                p_route = None
                p_bioavailability = 1.0
                p_indication = None
                p_acetylator = None
                measured_procainamide = 0.0
                measured_napa = 0.0
            
            # Standard input for non-Digoxin, non-Procainamide drugs
            if calc_mode == "Initial regimen":
                initial_method = st.selectbox(
                    "Select Initial Input",
                    ["Pharmacokinetics parameter", "Literature"],
                    help="Choose whether to calculate from PK parameters or use published literature values."
                )
                if initial_method == "Pharmacokinetics parameter" or (selected_drug == "Amiodarone" and initial_method == "Literature"):
                    route = st.selectbox("Route of administration", ["Oral", "IV Continuous Infusion"])
                if initial_method == "Pharmacokinetics parameter":
                    st.markdown("**Pharmacokinetics parameter inputs**")
                    p1, p2, p3 = st.columns(3)
                    css = p1.number_input("Css (steady-state concentration)", value=1.0, format="%.2f")
                    vd_input = p2.number_input("Vd (L)", value=50.0, format="%.1f")
                    cl_input = p3.number_input("Cl (L/hr)", value=5.0, format="%.2f")
                    p4, p5 = st.columns(2)
                    dose_input = p4.number_input("Dose", value=100.0, format="%.1f")
                    conc_input = p5.number_input("Concentration for Vd formula", value=1.0, format="%.2f")
            else:
                dose_adjust_old = st.number_input("Dose old", min_value=0.0, value=100.0, step=0.1)
                child_pugh_score = st.number_input("Child Pugh score", min_value=1, max_value=15, value=6)

    st.divider()

    # ===== AUTO-ANALYSIS SECTION =====
    ibw = calc_ibw(sex, height_cm)
    bmi = calc_bmi(abw, height_cm)
    bsa = calc_bsa(height_cm, abw)
    lbw = calc_lbw(sex, abw, height_cm)
    ajbw = calc_ajbw(ibw, abw)
    bmi_label, bmi_css = bmi_classify(bmi)
    dosing_weight = determine_dosing_weight(abw, ibw)

    st.markdown('<div class="analysis-header">📊 Auto-Analysis</div>', unsafe_allow_html=True)
    with st.container(border=True):
        a1, a2 = st.columns(2)
        with a1:
            st.markdown(f"**BMI:** `{bmi:.2f}` kg/m² <span class='bmi-badge {bmi_css}'>{bmi_label}</span>", unsafe_allow_html=True)
            st.metric("Ideal Body Weight (IBW)", f"{ibw:.2f} kg")
            st.metric("BSA (Mosteller)", f"{bsa:.2f} m²")
        with a2:
            st.metric("Lean Body Weight (LBW)", f"{lbw:.2f} kg")
            st.metric("Adjusted Body Weight (AjBW)", f"{ajbw:.2f} kg")
            weight_note = "Actual Weight" if abw <= 1.2 * ibw else "Adjusted Weight (AjBW)"
            if abw < ibw: weight_note = "Actual Weight (below IBW)"
            st.info(f"💡 **Dosing Weight Used:** {dosing_weight:.2f} kg — _{weight_note}_")
            st.markdown(
                "**Weight selection rules**\n"
                "- BMI 18.5–25: use Ideal Body Weight (IBW)\n"
                "- BMI > 25: use Adjusted Body Weight (AdjBW)\n"
                "- BMI < 18.5: use Actual Body Weight\n"
            )

    # ===== CREATININE CLEARANCE SUMMARY =====
    crcl_abw = calc_crcl(age, abw, sex, scr)
    crcl_ibw = calc_crcl(age, ibw, sex, scr)
    crcl_jelliffe = calc_crcl_jelliffe(age, sex, scr)
    egfr_mdrd = calc_mdrd(age, sex, scr, race)
    crcl_ajbw = calc_crcl(age, ajbw, sex, scr)
    jelliffe_bsa = crcl_jelliffe * (bsa / 1.73)
    salazar = calc_salazar_corcoran(sex, age, abw, height_cm, scr)

    # ===== AUTOMATIC EQUATION SELECTION =====
    if bmi >= 30 or abw > 1.2 * ibw:
        equation_name = "Cockcroft-Gault (Adjusted BW)"
        reason = "Obesity → Adjusted BW corrects overestimation bias"
        selected_crcl = crcl_ajbw
    elif abw < ibw:
        equation_name = "Cockcroft-Gault (Actual BW)"
        reason = "Underweight → Actual BW prevents underestimation of clearance"
        selected_crcl = crcl_abw
    else:
        equation_name = "Cockcroft-Gault (Ideal BW)"
        reason = "Normal Weight → Ideal BW provides best estimate"
        selected_crcl = crcl_ibw

    st.markdown('<div class="crcl-header">🧪 Creatinine Clearance Summary</div>', unsafe_allow_html=True)
    with st.container(border=True):
        cg_abw_help = "**Cockcroft & Gault (Actual Body Weight)**\n\n*If Male:* CrCl = ((140 - Age) * Weight_Actual) / (72 * Creatinine)\n\n*If Female:* CrCl = [((140 - Age) * Weight_Actual) / (72 * Creatinine)] * 0.85"
        cg_ibw_help = "**Cockcroft & Gault (Ideal Body Weight)**\n\n*If Male:* CrCl = ((140 - Age) * Weight_Ideal) / (72 * Creatinine)\n\n*If Female:* CrCl = [((140 - Age) * Weight_Ideal) / (72 * Creatinine)] * 0.85"
        jelliffe_help = "**Jelliffe Equation**\n\n*If Male:* Jelliffe = (98 - [0.8 * (Age - 20)]) / Creatinine\n\n*If Female:* Jelliffe = ((98 - [0.8 * (Age - 20)]) / Creatinine) * 0.90"
        mdrd_help = "**Simplified 4-variable MDRD formula**\n\nMDRD = 175 * (Creatinine ^ -1.154) * (Age ^ -0.203)\n\n*If Female:* Multiply result by 0.742\n\n*If African American:* Multiply result by 1.212"

        r1, r2 = st.columns(2)
        with r1:
            st.metric("CG — Actual Body Weight", f"{crcl_abw:.1f} mL/min")
            with st.expander("View Equation"):
                st.markdown(cg_abw_help)
        with r2:
            st.metric("CG — Ideal Body Weight", f"{crcl_ibw:.1f} mL/min")
            with st.expander("View Equation"):
                st.markdown(cg_ibw_help)
                
        r3, r4 = st.columns(2)
        with r3:
            st.metric("Jelliffe", f"{crcl_jelliffe:.1f} mL/min")
            with st.expander("View Equation"):
                st.markdown(jelliffe_help)
        with r4:
            st.metric("MDRD (eGFR)", f"{egfr_mdrd:.1f} mL/min/1.73 m²")
            with st.expander("View Equation"):
                st.markdown(mdrd_help)
    # ===== OBESE PATIENTS SECTION =====
    if bmi >= 30:
        st.markdown('<div class="obese-header">⚠️ CONSIDER THESE RESULTS FOR OBESE PATIENTS (BMI ≥ 30)</div>', unsafe_allow_html=True)
        pct_over = ((abw - ibw) / ibw) * 100 if ibw > 0 else 0
        st.markdown(f"Currently **{pct_over:.2f}%** over IBW.")
        with st.container(border=True):
            o1, o2 = st.columns(2)
            o1.metric("CG — Adjusted BW (AdjBW)", f"{crcl_ajbw:.1f} mL/min")
            o2.metric("Salazar-Corcoran (Obese)", f"{salazar:.1f} mL/min")
            o3, o4 = st.columns(2)
            o3.metric("Jelliffe (adjusted for BSA)", f"{jelliffe_bsa:.1f} mL/min")
            o4.metric("MDRD (eGFR)", f"{egfr_mdrd:.1f} mL/min/1.73 m²")

    st.divider()

    st.markdown(f"""
    <div class='selected-eq-box' style='background-color: #f0f9ff; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #0ea5e9;'>
        <p class='eq-title' style='margin:0; font-weight:600; color:#0f172a;'>Selected Equation: <span class='eq-name' style='color:#0284c7;'>{equation_name}</span></p>
        <p class='eq-reason' style='margin:5px 0 0 0; font-size:0.9em; color:#475569;'>Reason: {reason}</p>
        <p class='eq-value' style='margin:5px 0 0 0; font-weight:700; color:#0369a1;'>CrCl: {selected_crcl:.1f} mL/min</p>
    </div>
    """, unsafe_allow_html=True)
    
    t1, t2 = st.columns(2)
    target_unit = "µg/mL"
    if selected_drug == "Digoxin": target_unit = "ng/mL"
    elif selected_drug == "Amiodarone": target_unit = "mg/L"
    
    target_peak = t1.number_input(f"Target Peak ({target_unit})", value=float(drug_info["target_peak"]))
    target_trough = t2.number_input(f"Target Trough ({target_unit})", value=float(drug_info["target_trough"])) if drug_info["target_trough"] > 0 else 0
    st.markdown("**Preferences & Monitoring**")
    m1, m2 = st.columns(2)
    interval = m1.number_input("Preferred Dosing Interval (hrs) [0 = Auto]", min_value=0, value=0, step=12)
    measured_level = m2.number_input(f"Measured Level ({target_unit}) [0 = Skip]", min_value=0.0, value=0.0, step=0.1)

    # Use automatically selected CrCl for downstream PK
    crcl = selected_crcl

with tab_results:
    if st.button("🚀 Process Pharmacokinetics", type="primary", use_container_width=True):
        # Validation for Digoxin-specific parameters
        if selected_drug == "Digoxin":
            validation_errors = []
            if indication == "Select Indication":
                validation_errors.append("❌ Please select an Indication (Heart Failure or Atrial Fibrillation)")
            if indication == "Heart Failure" and hf_severity == "Select Severity":
                validation_errors.append("❌ Please select Heart Failure Severity (Mild, Moderate, or Severe)")
            if route_of_admin == "Select Route":
                validation_errors.append("❌ Please select Route of Administration (Oral or IV)")
            if route_of_admin == "Oral" and dosage_form == "Select Form":
                validation_errors.append("❌ Please select Oral Dosage Form (Tablet, Elixir, or Capsule)")
            if thyroid_status == "Select Status":
                validation_errors.append("❌ Please select Thyroid Status (Normal or Hyperthyroidism)")
            if calculation_type == "Initial dosing":
                if initial_method is None:
                    validation_errors.append("❌ Please select Initial Input method (Pharmacokinetics parameter or Literature)")
            
            if validation_errors:
                st.error("⚠️ **Please complete all required Digoxin parameters:**")
                for error in validation_errors:
                    st.write(error)
                st.stop()
        
        st.divider()
        vd = cl = t_half = ld = md = ke = 0.0
        final_interval = interval
        warnings = []
        dose_adjustment_mode = calc_mode == "Dose adjustment"
        literature_mode = calc_mode == "Initial regimen" and initial_method == "Literature"
        pk_param_mode = calc_mode == "Initial regimen" and initial_method == "Pharmacokinetics parameter"
        literature_amiodarone = literature_mode and selected_drug == "Amiodarone"
        route = route or "Oral"

        if dose_adjustment_mode:
            if child_pugh_score in [8, 9]:
                new_dose = dose_adjust_old * 0.75
                adjustment_text = f"Dose new = {dose_adjust_old:.2f} × 0.75 = {new_dose:.2f}"
            elif child_pugh_score >= 10:
                new_dose = dose_adjust_old * 0.5
                adjustment_text = f"Dose new = {dose_adjust_old:.2f} × 0.5 = {new_dose:.2f}"
            else:
                new_dose = None
                adjustment_text = "No need to adjust the old dose."

            st.subheader("🧾 Dose Adjustment Recommendation")
            st.markdown(f"""
            <div class="alert-box alert-info">
                <p><strong>Old dose:</strong> {dose_adjust_old:.2f}</p>
                <p><strong>Child-Pugh score:</strong> {child_pugh_score}</p>
                <p><strong>Recommendation:</strong> {adjustment_text}</p>
            </div>
            """, unsafe_allow_html=True)

        if pk_param_mode:
            if route == "IV Continuous Infusion":
                ld_pk = css * vd_input if css and vd_input else 0
                md_pk = css * cl_input if css and cl_input else 0
                t_half_pk = 0.693 * vd_input / cl_input if cl_input else 0
                vd_calc = dose_input / conc_input if conc_input else 0
                st.subheader("⚙️ PK Parameter Derived Outputs")
                st.markdown(f"""
                <div class="alert-box alert-success">
                    <p><strong>LD = Css × Vd</strong> = {css:.2f} × {vd_input:.2f} = {ld_pk:.2f}</p>
                    <p><strong>MD = Css × Cl</strong> = {css:.2f} × {cl_input:.2f} = {md_pk:.2f}</p>
                    <p><strong>t½ = 0.693 × Vd / Cl</strong> = 0.693 × {vd_input:.2f} / {cl_input:.2f} = {t_half_pk:.2f}</p>
                    <p><strong>Vd = dose / Conc</strong> = {dose_input:.2f} / {conc_input:.2f} = {vd_calc:.2f}</p>
                    <p><strong>Cockcroft-Gault CrCl</strong> = ((140 − age) × weight) / (72 × Scr), multiply by 0.85 for females</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Oral route selected in PK parameter mode. Use drug-specific clinical references to convert PK parameters into appropriate oral dosing regimens.")

        if selected_drug == 'Digoxin':
            # Apply HF severity-based CrCl adjustment if applicable
            adjusted_crcl = crcl
            if indication == "Heart Failure" and crcl_hf_adjustment and hf_severity and hf_severity != "Select Severity":
                # For HF patients, use adjusted clearance
                adjusted_crcl = max(crcl_hf_adjustment, crcl)  # Use whichever is lower for conservative dosing
                st.info(f"💊 **Digoxin + {hf_severity} HF**: Using conservative CrCl adjustment to {adjusted_crcl:.1f} mL/min")
            
            # Use indication-based CSS if selected
            if indication == "Heart Failure" and css_initial:
                target_peak = css_initial  # 0.8 ng/mL for HF
                target_trough = 0  # Remove peak/trough for steady-state dosing
            elif indication == "Atrial Fibrillation" and css_initial:
                target_peak = css_initial  # 1.2 ng/mL for AFib
                target_trough = 0  # Remove peak/trough for steady-state dosing
            
            # Calculate VD and CL with bioavailability factor
            vd_factor = 7.3 if adjusted_crcl >= 30 else 4.5
            vd = vd_factor * ibw
            
            # Clearance adjusted for renal function
            cl = ((0.8 * ibw) + adjusted_crcl) * 60 / 1000
            
            # Apply bioavailability adjustment
            if route_of_admin == "Oral":
                cl = cl * bioavailability  # Effective clearance with bioavailability factor
            
            # Apply thyroid status adjustment (hyperthyroidism → increased metabolism)
            if thyroid_status == "Hyperthyroidism":
                cl = cl * 1.5  # Increased clearance due to increased metabolism
                st.warning("⚠️ **Hyperthyroidism detected**: Digoxin clearance increased by 50%. Higher maintenance doses may be needed.")
            
            if target_peak > 2.0: 
                warnings.append("Digoxin target > 2.0 ng/mL increases toxicity risk.")
            if interval == 0: 
                final_interval = 24 if adjusted_crcl >= 50 else (48 if adjusted_crcl >= 20 else 72)
        elif selected_drug == 'Procainamide':
            vd = 2.0 * abw
            cl = (180 + 3 * crcl) * 60 / 1000 if not is_hf else (90 + 1.5 * crcl) * 60 / 1000
            
            # Apply bioavailability factor
            p_bioavailability = 1.0 if p_route in ["IV", "IM"] else 0.85
            
            # Apply Procainamide formulas with bioavailability
            # LD = (Ctarget × Vd) ÷ F
            # MD = (CL × Css × dosing interval) ÷ F
            ld_calc = (target_peak * vd) / p_bioavailability
            md_calc = (cl * target_peak * final_interval) / p_bioavailability
            
            # Special rule: Oral loading not recommended
            if p_route == "Oral":
                ld = None  # Mark as unavailable for oral
                md = md_calc
                final_interval = 6  # Typical oral dosing interval (6 hours)
            else:
                ld = ld_calc
                md = md_calc
                final_interval = 1  # Force continuous IV infusion
            
            if target_peak > 10.0: warnings.append("Procainamide target > 10 µg/mL is associated with toxicity.")
        elif selected_drug == 'Lidocaine':
            vd = (0.9 if is_hf else 1.1) * abw
            cl = (6.0 if is_hf else 10.0) * abw * 60 / 1000
            final_interval = 1
        elif selected_drug == 'Amiodarone':
            vd = 60 * abw
            cl = 0.12 * abw
            if interval == 0: final_interval = 24
            
        if cl and vd:
            ke = cl / vd
            t_half = 0.693 / ke
            ld = vd * target_peak
            md = cl * target_peak * final_interval

        if md > 0: md = round(md / 50) * 50 if md > 100 else round(md, 2)
        if ld > 0: ld = round(ld / 50) * 50 if ld > 100 else round(ld, 2)

        validation_status = "✅ Within recommended dose limits"
        validation_title = "Approved"
        validation_color = "alert-success"

        # Formatting based on drug rules
        if selected_drug == "Digoxin":
            disp_vd = f"{(vd / ibw):.1f} L/kg"
            disp_cl = f"{(cl * 1000 / 60):.1f} mL/min"
            disp_thalf = f"{t_half:.1f} hours"
            md_daily = (md / final_interval) * 24 if final_interval > 0 else md
            
            # Dose limit check
            if md_daily > 250:
                md_daily = 250
                validation_status = "🔴 Calculated dose exceeded maximum limit<br>✔ Auto-adjusted to safe maximum"
                validation_title = "Auto-Adjusted"
                validation_color = "alert-danger"
            elif md_daily >= 200:
                validation_status = "🟡 High therapeutic dose<br>Monitor closely"
                validation_title = "Caution"
                validation_color = "alert-warning"
                
            maintenance_text = f"{md_daily:,.0f} µg PO q{final_interval}h" if final_interval in [24, 48, 72] else f"{md_daily:,.0f} µg/day"
            loading_text = f"{ld:,.0f} µg once" if ld > 0 else "None"
            rec_dose_str = f"{md_daily:,.0f} µg/day"
            admin_str = "PO or IV"
            interval_str = f"q{final_interval}h"
            
        elif selected_drug == "Lidocaine":
            disp_vd = f"{vd:.1f} L"
            disp_cl = f"{cl:.2f} L/hr"
            disp_thalf = f"{t_half:.1f} hours"
            
            # Dose limit check (Max ~ 240 mg/hr = 4 mg/min)
            if md > 240:
                md = 240
                validation_status = "🔴 Calculated dose exceeded maximum limit<br>✔ Auto-adjusted to safe maximum"
                validation_title = "Auto-Adjusted"
                validation_color = "alert-danger"
            elif md >= 180:
                validation_status = "🟡 High therapeutic dose<br>Monitor closely"
                validation_title = "Caution"
                validation_color = "alert-warning"

            maintenance_text = f"{md:.1f} mg/hr continuous infusion"
            loading_text = f"{ld:,.0f} mg once" if ld > 0 else "None"
            rec_dose_str = f"{md:.1f} mg/hr"
            admin_str = "Continuous IV Infusion"
            interval_str = "Continuous"
            
        elif selected_drug == "Procainamide":
            disp_vd = f"{vd:.1f} L"
            disp_cl = f"{cl:.2f} L/hr"
            disp_thalf = f"{t_half:.1f} hours"
            
            # Dose limit check (Max ~ 240 mg/hr)
            if md > 240:
                md = 240
                validation_status = "🔴 Calculated dose exceeded maximum limit<br>✔ Auto-adjusted to safe maximum"
                validation_title = "Auto-Adjusted"
                validation_color = "alert-danger"
            elif md >= 180:
                validation_status = "🟡 High therapeutic dose<br>Monitor closely"
                validation_title = "Caution"
                validation_color = "alert-warning"

            maintenance_text = f"{md:.1f} mg/hr (IV infusion)"
            # Handle oral loading N/A for Procainamide
            if isinstance(ld, str) or ld is None:
                loading_text = ld if isinstance(ld, str) else "None"
            else:
                loading_text = f"{ld:,.0f} mg once" if ld > 0 else "None"
            rec_dose_str = f"{md:.1f} mg/hr"
            admin_str = "IV Infusion"
            interval_str = "Continuous"
            
        elif selected_drug == "Amiodarone":
            disp_vd = f"{vd:,.0f} L"
            disp_cl = f"{cl:.2f} L/hr"
            disp_thalf = f"{(t_half/24):.1f} days"
            dose_unit = "g" if ld >= 1000 else "mg"
            ld_disp = ld / 1000 if ld >= 1000 else ld
            md_daily = (md / final_interval) * 24 if final_interval > 0 else md
            
            # Dose limit check (Max ~ 800 mg/day)
            if md_daily > 800:
                md_daily = 800
                validation_status = "🔴 Calculated dose exceeded maximum limit<br>✔ Auto-adjusted to safe maximum"
                validation_title = "Auto-Adjusted"
                validation_color = "alert-danger"
            elif md_daily >= 400:
                validation_status = "🟡 High therapeutic dose<br>Monitor closely"
                validation_title = "Caution"
                validation_color = "alert-warning"

            maintenance_text = f"{md_daily:,.0f} mg/day"
            loading_text = f"{ld_disp:,.1f} {dose_unit} once" if ld > 0 else "None"
            rec_dose_str = maintenance_text
            admin_str = "IV or PO"
            interval_str = f"q{final_interval}h"

            if literature_amiodarone:
                if route == "Oral":
                    maintenance_text = "MD = 200 - 400 mg/day"
                    loading_text = "LD = 800 - 1600 mg/day"
                    rec_dose_str = maintenance_text
                    admin_str = "Oral"
                    interval_str = "Daily"
                else:
                    maintenance_text = "MD = 0.5 mg/min"
                    loading_text = "LD = 15 mg/min for the first 10 minutes, then 1 mg/min for 6 hours, then 0.5 mg/min for the remaining 18 hours"
                    rec_dose_str = maintenance_text
                    admin_str = "IV Continuous Infusion"
                    interval_str = "Continuous"
                    disp_vd = "N/A"
                    disp_cl = "N/A"
                    disp_thalf = "N/A"

            if literature_amiodarone:
                if route == "Oral":
                    maintenance_text = "MD = 200 - 400 mg/day"
                    loading_text = "LD = 800 - 1600 mg/day"
                    rec_dose_str = maintenance_text
                    admin_str = "Oral"
                    interval_str = "Daily"
                else:
                    maintenance_text = "MD = 0.5 mg/min"
                    loading_text = "LD = 15 mg/min for the first 10 minutes, then 1 mg/min for 6 hours, then 0.5 mg/min for the remaining 18 hours"
                    rec_dose_str = maintenance_text
                    admin_str = "IV Continuous Infusion"
                    interval_str = "Continuous"
                    disp_vd = "N/A"
                    disp_cl = "N/A"
                    disp_thalf = "N/A"

        st.subheader("1. Core PK Parameters")
        rc1, rc2, rc3, rc4 = st.columns(4)
        rc1.metric("Creatinine Clearance", f"{crcl:.1f} mL/min")
        rc2.metric("Volume of Distribution", disp_vd)
        rc3.metric("Clearance", disp_cl)
        rc4.metric("Half-life (t½)", disp_thalf)

        # Determine status colors and logic for Therapeutic Level Evaluation
        level_status_text = "Not available"
        status_text = "N/A"
        status_color = ""
        range_str = ""
        
        thera_min = drug_info["thera_min"]
        thera_max = drug_info["thera_max"]
        
        if measured_level > 0:
            level_status_text = f"{measured_level:.1f} {target_unit}"
            if selected_drug == "Digoxin":
                range_str = "0.5 – 0.9 ng/mL"
                if measured_level < 0.5:
                    status_text = "Below therapeutic range (Sub-therapeutic)"
                    status_color = "#ef4444"
                elif measured_level <= 0.9:
                    status_text = "Within therapeutic range"
                    status_color = "#10b981"
                elif measured_level <= 2.0:
                    status_text = "Upper therapeutic range (Caution)"
                    status_color = "#f59e0b"
                else:
                    status_text = "Above therapeutic range (Toxic)"
                    status_color = "#ef4444"
            elif selected_drug == "Lidocaine":
                range_str = "1.5 – 5.0 µg/mL"
                if measured_level < 1.5:
                    status_text = "Below therapeutic range"
                    status_color = "#ef4444"
                elif measured_level <= 5.0:
                    status_text = "Within therapeutic range"
                    status_color = "#10b981"
                else:
                    status_text = "Above therapeutic range (CNS toxicity risk)"
                    status_color = "#ef4444"
            elif selected_drug == "Procainamide":
                range_str = "4.0 – 10.0 µg/mL"
                if measured_level < 4.0:
                    status_text = "Below therapeutic range"
                    status_color = "#ef4444"
                elif measured_level <= 10.0:
                    status_text = "Within therapeutic range"
                    status_color = "#10b981"
                else:
                    status_text = "Above therapeutic range"
                    status_color = "#ef4444"
            elif selected_drug == "Amiodarone":
                range_str = "1.0 – 2.5 mg/L"
                if measured_level < 1.0:
                    status_text = "Below therapeutic range"
                    status_color = "#ef4444"
                elif measured_level <= 2.5:
                    status_text = "Within therapeutic range"
                    status_color = "#10b981"
                else:
                    status_text = "Above therapeutic range (toxicity risk)"
                    status_color = "#ef4444"
        else:
            if selected_drug == "Digoxin": range_str = "0.5 – 0.9 ng/mL"
            elif selected_drug == "Lidocaine": range_str = "1.5 – 5.0 µg/mL"
            elif selected_drug == "Procainamide": range_str = "4.0 – 10.0 µg/mL"
            elif selected_drug == "Amiodarone": range_str = "1.0 – 2.5 mg/L"

        # Determine Overall Status
        overall_level = 0 # 0 = Safe, 1 = Caution, 2 = Toxic
        if "alert-danger" in validation_color:
            overall_level = 2
        elif "alert-warning" in validation_color:
            overall_level = max(overall_level, 1)
            
        if measured_level > 0:
            if status_color == "#ef4444":
                overall_level = 2
            elif status_color == "#f59e0b":
                overall_level = max(overall_level, 1)
                
        if overall_level == 2:
            card_color = "#ef4444"
            card_icon = "🔴"
            card_status = "High Risk – Immediate Review Required"
            action_step = "<li>Hold dose immediately.</li><li>Evaluate for toxicity symptoms.</li><li>Consider antidote or alternative therapy if severe.</li>"
            validation_status_plain = f"❌ {validation_status.replace('<br>', ' - ')}"
        elif overall_level == 1:
            card_color = "#f59e0b"
            card_icon = "🟡"
            card_status = "Caution – Upper Maintenance Range / Near Upper Limit"
            action_step = "<li>Maintain dose but increase monitoring frequency.</li><li>Consider dose reduction if renal function declines or symptoms develop.</li>"
            validation_status_plain = f"⚠ {validation_status.replace('<br>', ' - ')}"
        else:
            card_color = "#10b981"
            card_icon = "🟢"
            card_status = "Safe – Optimal Therapeutic Range"
            action_step = "<li>Continue current dose.</li><li>Routine clinical monitoring.</li><li>Recheck levels if clinical status changes.</li>"
            validation_status_plain = f"✔ {validation_status.replace('<br>', ' - ')}"
            
        # Toxicity Risk Engine & Monitoring
        risk_flags = []
        monitoring_points = []
        
        if measured_level == 0:
            risk_flags.append("⚠ No serum level available for evaluation")
            
        if selected_drug == "Digoxin":
            risk_flags.append("⚠ Narrow therapeutic index drug")
            if crcl < 60: risk_flags.append("⚠ Risk significantly increases with renal impairment (CrCl < 60)")
            monitoring_points = [
                f"Serum digoxin level (target 0.5–0.9 ng/mL)",
                "Serum creatinine / CrCl trend",
                "Electrolytes: K⁺, Mg²⁺, Ca²⁺",
                "ECG monitoring (if symptomatic)"
            ]
        elif selected_drug == "Lidocaine":
            risk_flags.append("⚠ CNS toxicity risk at high serum levels")
            risk_flags.append("⚠ Highly dependent on hepatic clearance")
            monitoring_points = [
                f"Serum lidocaine level (target 1.5–5.0 µg/mL)",
                "CNS toxicity (confusion, seizures)",
                "Neuro monitoring",
                "Continuous ECG monitoring"
            ]
        elif selected_drug == "Procainamide":
            risk_flags.append("⚠ Monitor for active NAPA metabolite")
            if crcl < 60: risk_flags.append("⚠ Renal clearance dependency (CrCl < 60)")
            monitoring_points = [
                f"Serum procainamide level (target 4.0–10.0 µg/mL)",
                "NAPA active metabolite level (10-20 µg/mL)",
                "QT interval monitoring",
                "Drug-induced lupus markers",
                "CBC (monitor for agranulocytosis)"
            ]
        elif selected_drug == "Amiodarone":
            risk_flags.append("⚠ Extremely long half-life and massive volume of distribution")
            risk_flags.append("⚠ Multi-organ toxicity risk")
            monitoring_points = [
                f"Serum amiodarone level (target 1.0–2.5 mg/L)",
                "TSH / T3 / T4",
                "Liver enzymes",
                "Lung toxicity (CXR/PFT)",
                "Routine ECGs",
                "Electrolytes (K⁺, Mg²⁺)"
            ]
            
        risk_engine_html = "".join([f"<li>{flag}</li>" for flag in risk_flags])
        monitoring_html = "".join([f"<li>{mon}</li>" for mon in monitoring_points])

        drug_card_html = f"""
        <div style="border: 2px solid {card_color}80; border-radius: 10px; overflow: hidden; margin-bottom: 30px; background-color: var(--background-color);">
            <div style="background-color: {card_color}15; padding: 20px; border-bottom: 2px solid {card_color}50;">
                <h2 style="margin-top: 0; margin-bottom: 10px; color: {card_color}; display: flex; align-items: center; gap: 10px;">🟦 {selected_drug}</h2>
                <h4 style="margin: 0; opacity: 0.9; color: var(--text-color);">🟨 1. Current Status</h4>
                <p style="margin: 5px 0 0 0; font-size: 1.3em; font-weight: bold; color: {card_color};">{card_icon} {card_status}</p>
            </div>
            <div style="padding: 20px;">
                <div style="display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 25px;">
                    <div style="flex: 1; min-width: 250px; background-color: var(--secondary-background-color); padding: 20px; border-radius: 8px; border-left: 4px solid #3b82f6;">
                        <h4 style="margin-top: 0; margin-bottom: 15px; font-size: 1.1em; color: var(--text-color);">📊 2. Therapeutic Assessment</h4>
                        <ul style="margin-bottom: 0; padding-left: 20px; line-height: 1.6; color: var(--text-color);">
                            <li><strong>Serum level status:</strong> {level_status_text}</li>
                            <li><strong>Therapeutic range:</strong> {range_str}</li>
                            <li><strong>Interpretation:</strong> <span style="color: {status_color if status_color else 'var(--text-color)'}; font-weight: 500;">{status_text}</span></li>
                        </ul>
                    </div>
                    <div style="flex: 1; min-width: 250px; background-color: var(--secondary-background-color); padding: 20px; border-radius: 8px; border-left: 4px solid #8b5cf6;">
                        <h4 style="margin-top: 0; margin-bottom: 15px; font-size: 1.1em; color: var(--text-color);">💉 3. Dose Evaluation</h4>
                        <ul style="margin-bottom: 0; padding-left: 20px; line-height: 1.6; color: var(--text-color);">
                            <li><strong>Maintenance dose:</strong> {maintenance_text}</li>
                            <li><strong>Loading dose:</strong> {loading_text}</li>
                            <li><strong>Dose status:</strong> <span style="font-weight: 500;">{validation_status_plain}</span></li>
                        </ul>
                    </div>
                </div>
                <div style="margin-bottom: 25px;">
                    <h4 style="margin-top: 0; margin-bottom: 10px; font-size: 1.1em; color: var(--text-color);">🧪 4. Toxicity Risk Engine</h4>
                    <ul style="padding-left: 20px; color: #ef4444; font-weight: 500; line-height: 1.6;">
                        {risk_engine_html}
                    </ul>
                </div>
                <div style="margin-bottom: 25px;">
                    <h4 style="margin-top: 0; margin-bottom: 10px; font-size: 1.1em; color: var(--text-color);">🧠 5. Clinical Monitoring Section</h4>
                    <ul style="padding-left: 20px; line-height: 1.6; color: var(--text-color);">
                        {monitoring_html}
                    </ul>
                </div>
                <hr style="opacity: 0.2; margin: 25px 0;">
                <div>
                    <h4 style="margin-top: 0; margin-bottom: 15px; font-size: 1.1em; color: var(--text-color);">📌 6. Action Recommendation</h4>
                    <div style="background-color: {card_color}10; padding: 15px; border-radius: 8px; border-left: 4px solid {card_color};">
                        <ul style="margin-bottom: 0; padding-left: 20px; line-height: 1.6; font-weight: 600; color: {card_color};">
                            {action_step}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        """

        st.subheader("2. Individualized Dosage Regimen")
        st.markdown(f"""
        <div class="alert-box {validation_color}" style="margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 15px;">
                <div style="flex: 1; min-width: 200px;">
                    <h4 style="margin-top:0; color: inherit; font-size: 1.1em; opacity: 0.9;">💉 Loading Dose</h4>
                    <p style="font-size: 1.3rem; margin-bottom:0; font-weight:bold;">{loading_text}</p>
                </div>
                <div style="flex: 1; min-width: 200px;">
                    <h4 style="margin-top:0; color: inherit; font-size: 1.1em; opacity: 0.9;">💊 Maintenance Dose</h4>
                    <p style="font-size: 1.3rem; margin-bottom:0; font-weight:bold;">{maintenance_text}</p>
                </div>
            </div>
            <hr style="margin: 20px 0; border-color: currentColor; opacity: 0.2;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
                <div>
                    <h4 style="margin: 0; color: inherit; font-size: 1.1em; opacity: 0.9;">🛡 Dose Validation</h4>
                    <p style="margin: 0; font-weight: bold; font-size: 1.2em;">{validation_title}</p>
                </div>
                <div style="text-align: right;">
                    <p style="margin: 0; font-size: 0.9em; opacity: 0.9;">Dose Check:</p>
                    <p style="margin: 0; font-weight: 500;">{validation_status}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ===== FINAL RENAL-ADJUSTED DOSE =====
        if crcl >= 60:
            renal_cat = "Normal (≥60 mL/min)"
        elif crcl >= 30:
            renal_cat = "Mild Impairment (30-59 mL/min)"
        elif crcl >= 15:
            renal_cat = "Moderate Impairment (15-29 mL/min)"
        else:
            renal_cat = "Severe Impairment (<15 mL/min)"

        st.markdown("### Final Renal-Adjusted Dose")
        st.markdown(f"""
        <div style='background-color: var(--secondary-background-color); padding: 20px; border-radius: 12px; border-left: 4px solid #8b5cf6; margin-bottom: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);'>
            <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 15px;'>
                <div>
                    <p style='margin:0; color: var(--text-color); opacity: 0.7; font-size: 0.9em;'>Drug:</p>
                    <p style='margin:0; font-weight:600; font-size: 1.1em;'>{selected_drug}</p>
                </div>
                <div>
                    <p style='margin:0; color: var(--text-color); opacity: 0.7; font-size: 0.9em;'>Renal Category:</p>
                    <p style='margin:0; font-weight:600; font-size: 1.1em;'>{renal_cat}</p>
                </div>
                <div>
                    <p style='margin:0; color: var(--text-color); opacity: 0.7; font-size: 0.9em;'>Recommended Dose:</p>
                    <p style='margin:0; font-weight:600; font-size: 1.1em;'>{rec_dose_str}</p>
                </div>
                <div>
                    <p style='margin:0; color: var(--text-color); opacity: 0.7; font-size: 0.9em;'>Dosing Interval:</p>
                    <p style='margin:0; font-weight:600; font-size: 1.1em;'>{interval_str}</p>
                </div>
                <div>
                    <p style='margin:0; color: var(--text-color); opacity: 0.7; font-size: 0.9em;'>Administration:</p>
                    <p style='margin:0; font-weight:600; font-size: 1.1em;'>{admin_str}</p>
                </div>
                <div>
                    <p style='margin:0; color: var(--text-color); opacity: 0.7; font-size: 0.9em;'>Next Review:</p>
                    <p style='margin:0; font-weight:600; font-size: 1.1em;'>Reassess renal function in 24 h</p>
                </div>
                <div>
                    <p style='margin:0; color: var(--text-color); opacity: 0.7; font-size: 0.9em;'>Confidence:</p>
                    <p style='margin:0; font-weight:600; font-size: 1.1em; color: #16a34a;'>High</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        for w in warnings:
            st.markdown(f"""<div class="alert-box alert-warning"><b>⚠️ Warning:</b> {w}</div>""", unsafe_allow_html=True)
        if crcl < 30:
            st.markdown("""<div class="alert-box alert-danger"><b>🚨 Severe Renal Impairment Detected.</b> Consider dose reductions and close monitoring.</div>""", unsafe_allow_html=True)

        # ===== THERAPEUTIC LEVEL EVALUATION =====
        if measured_level > 0:
            st.subheader("3. Therapeutic Level Evaluation")
            st.markdown(f"""
            <div style='background-color: var(--secondary-background-color); padding: 20px; border-radius: 12px; border-left: 4px solid {status_color}; margin-bottom: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);'>
                <p style='margin:0 0 5px 0; font-size:1.1em; color:var(--text-color);'><strong>Drug:</strong> {selected_drug}</p>
                <p style='margin:0 0 5px 0; font-size:1.1em; color:var(--text-color);'><strong>Level:</strong> {measured_level:.1f} {target_unit}</p>
                <p style='margin:0 0 10px 0; font-size:1.1em; color:var(--text-color);'><strong>Therapeutic Range:</strong> {range_str}</p>
                <p style='margin:0; font-size:1.2em; font-weight:600; color:{status_color};'>Status: {status_text}</p>
            </div>
            """, unsafe_allow_html=True)

        st.session_state['last_pk'] = {
            "drug": selected_drug, "age": age, "sex": sex, "abw": abw, "crcl": crcl,
            "vd": vd, "ke": ke, "t_half": t_half, "md": md, "interval": final_interval, "ld": ld,
            "mode": calc_mode, "ibw": ibw, "bmi": bmi, "bsa": bsa, "lbw": lbw, "ajbw": ajbw,
            "drug_card_html": drug_card_html,
            # Digoxin-specific parameters
            "indication": indication if selected_drug == "Digoxin" else None,
            "hf_severity": hf_severity if selected_drug == "Digoxin" else None,
            "route_of_admin": route_of_admin if selected_drug == "Digoxin" else None,
            "dosage_form": dosage_form if selected_drug == "Digoxin" else None,
            "bioavailability": bioavailability if selected_drug == "Digoxin" else None,
            "thyroid_status": thyroid_status if selected_drug == "Digoxin" else None,
            "calculation_type": calculation_type if selected_drug == "Digoxin" else None,
            # Procainamide-specific parameters
            "p_route": p_route if selected_drug == "Procainamide" else None,
            "p_bioavailability": p_bioavailability if selected_drug == "Procainamide" else None,
            "p_indication": p_indication if selected_drug == "Procainamide" else None,
            "p_acetylator": p_acetylator if selected_drug == "Procainamide" else None,
            "measured_procainamide": measured_procainamide if selected_drug == "Procainamide" else None,
            "measured_napa": measured_napa if selected_drug == "Procainamide" else None,
        }

with tab_docs:
    st.subheader("FINAL MONITORING OUTPUT (Clinical Documentation)")
    if 'last_pk' in st.session_state:
        pk = st.session_state['last_pk']
        st.markdown(pk['drug_card_html'], unsafe_allow_html=True)
        
        # Digoxin-specific documentation
        if pk['drug'] == "Digoxin" and pk['indication']:
            st.markdown("---")
            st.subheader("📋 Digoxin-Specific Clinical Parameters")
            
            with st.container(border=True):
                doc_col1, doc_col2 = st.columns(2)
                
                with doc_col1:
                    st.markdown("**Clinical Indication**")
                    if pk['indication'] == "Heart Failure":
                        severity_text = f"{pk['hf_severity']} Severity" if pk['hf_severity'] else "Not specified"
                        st.write(f"🫀 Heart Failure - {severity_text}")
                        st.markdown(f"- **Target Css**: 0.8 ng/mL")
                    else:
                        st.write(f"🫀 {pk['indication']}")
                        st.markdown(f"- **Target Css**: 1.2 ng/mL")
                
                with doc_col2:
                    st.markdown("**Route & Bioavailability**")
                    if pk['route_of_admin'] == "Oral":
                        st.write(f"💊 {pk['dosage_form']} (F = {pk['bioavailability']})")
                        bioavail_pct = pk['bioavailability'] * 100
                        st.markdown(f"- **Bioavailability**: {bioavail_pct:.0f}%")
                    else:
                        st.write(f"💉 IV (F = 1.0)")
                        st.markdown(f"- **Bioavailability**: 100%")
                
                doc_col3, doc_col4 = st.columns(2)
                
                with doc_col3:
                    st.markdown("**Thyroid Status**")
                    if pk['thyroid_status'] == "Hyperthyroidism":
                        st.write(f"⚠️ {pk['thyroid_status']}")
                        st.markdown(f"- **Clearance Adjustment**: ×1.5 (increased metabolism)")
                    else:
                        st.write(f"✅ {pk['thyroid_status']}")
                        st.markdown(f"- **Clearance Adjustment**: Normal")
                
                with doc_col4:
                    st.markdown("**Calculation Type**")
                    st.write(f"📊 {pk['calculation_type'].title()}")
            
            # Detailed recommendations based on parameters
            st.markdown("---")
            st.markdown("### 🎯 Personalized Recommendations")
            
            recommendations = []
            
            # Indication-based recommendations
            if pk['indication'] == "Heart Failure":
                recommendations.append(
                    f"**Heart Failure ({pk['hf_severity']})**: "
                    f"Target steady-state concentration = 0.8 ng/mL for symptom control"
                )
                if pk['hf_severity'] == "Severe":
                    recommendations.append(
                        "⚠️ **Severe HF**: Monitor closely for toxicity; consider more frequent serum level checks"
                    )
            else:
                recommendations.append(
                    "**Atrial Fibrillation**: "
                    "Target steady-state concentration = 1.2 ng/mL for rate control"
                )
            
            # Route and bioavailability recommendations
            if pk['route_of_admin'] == "Oral":
                if pk['bioavailability'] < 0.8:
                    recommendations.append(
                        f"**{pk['dosage_form']} (F={pk['bioavailability']})**: "
                        f"Lower bioavailability requires adjustment of oral doses; ensure consistent formulation"
                    )
                elif pk['bioavailability'] > 0.8:
                    recommendations.append(
                        f"**{pk['dosage_form']} (F={pk['bioavailability']})**: "
                        f"Higher bioavailability may require dose reduction compared to tablets"
                    )
            else:
                recommendations.append(
                    "**IV Administration**: 100% bioavailability; use for acute loading or when oral route unavailable"
                )
            
            # Thyroid status recommendations
            if pk['thyroid_status'] == "Hyperthyroidism":
                recommendations.append(
                    "⚠️ **Hyperthyroidism Alert**: Digoxin clearance is increased; higher maintenance doses required; "
                    "recheck levels 5-7 days after thyroid status normalization"
                )
            
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f"{i}. {rec}")
        
        # Procainamide-specific documentation
        elif pk['drug'] == "Procainamide" and pk['p_indication']:
            st.markdown("---")
            st.subheader("📋 Procainamide-Specific Clinical Parameters")
            
            with st.container(border=True):
                # Route & Bioavailability
                p_col1, p_col2 = st.columns(2)
                
                with p_col1:
                    st.markdown("**Route of Administration**")
                    st.write(f"💊 {pk['p_route']}")
                    st.markdown(f"- **Bioavailability (F)**: {pk['p_bioavailability']}")
                    if pk['p_route'] == "Oral":
                        st.markdown("- ⚠️ **Oral Loading**: N/A (not recommended)")
                
                with p_col2:
                    st.markdown("**Clinical Indication**")
                    if pk['p_indication'] == "Ventricular":
                        st.write(f"🫀 {pk['p_indication']} Arrhythmia")
                        st.markdown("- **Risk Level**: High")
                        st.markdown("- **Monitoring**: Continuous ECG (consider ICU)")
                        st.markdown("- **Dosing**: Upper therapeutic range (6-10 mcg/mL) with caution")
                        st.markdown("- **Alert Priority**: Focus on QRS widening (conduction risk)")
                    else:
                        st.write(f"🫀 {pk['p_indication']} Arrhythmia")
                        st.markdown("- **Risk Level**: Moderate")
                        st.markdown("- **Monitoring**: Standard ECG monitoring")
                        st.markdown("- **Dosing**: Lower therapeutic range (4-8 mcg/mL)")
                        st.markdown("- **Alert Priority**: Focus on QT prolongation (torsades risk)")
                
                # Acetylator Status
                p_col3, p_col4 = st.columns(2)
                
                with p_col3:
                    st.markdown("**Acetylator Status**")
                    if pk['p_acetylator'] == "Fast":
                        st.write(f"⚡ {pk['p_acetylator']} Acetylator")
                        st.markdown("- **Metabolism**: ↑ NAPA / ↓ Procainamide")
                    elif pk['p_acetylator'] == "Slow":
                        st.write(f"🐢 {pk['p_acetylator']} Acetylator")
                        st.markdown("- **Metabolism**: ↑ Procainamide / ↓ NAPA")
                    else:
                        st.write(f"❓ {pk['p_acetylator']} Acetylator Status")
                        st.markdown("- **Metabolism**: Uncertain — monitor both levels closely")
                
                # Measured Levels
                with p_col4:
                    st.markdown("**Measured Serum Levels**")
                    if pk['measured_procainamide'] > 0:
                        st.write(f"**Procainamide**: {pk['measured_procainamide']:.1f} mcg/mL")
                        if 4 <= pk['measured_procainamide'] <= 10:
                            st.success("✅ OK (4-10 range)")
                        else:
                            st.error("⚠️ Toxicity start (>10)")
                    
                    if pk['measured_napa'] > 0:
                        st.write(f"**NAPA**: {pk['measured_napa']:.1f} mcg/mL")
                        if 12 <= pk['measured_napa'] <= 18:
                            st.success("✅ OK (12-18 range)")
                        elif pk['measured_napa'] >= 40:
                            st.error("🔴 Toxic (≥40)")
                    
                    # Total calculation
                    if pk['measured_procainamide'] > 0 and pk['measured_napa'] > 0:
                        total_level = pk['measured_procainamide'] + pk['measured_napa']
                        st.write(f"**Total**: {total_level:.1f} mcg/mL")
                        if 5 <= total_level <= 30:
                            st.success("✅ Acceptable (5-30 range)")
                        else:
                            st.warning("⚠️ Outside acceptable range")
            
            # Detailed indication-based recommendations
            st.markdown("---")
            st.markdown("### 🎯 Personalized Clinical Guidance")
            
            if pk['p_indication'] == "Ventricular":
                st.markdown("""
                **🔴 High-Risk Ventricular Arrhythmia Protocol:**
                1. **Continuous cardiac monitoring** - ICU environment recommended
                2. **Target concentration**: Upper therapeutic range (6-10 mcg/mL) with caution
                3. **Primary concern**: QRS widening (proarrhythmic effect from conduction slowing)
                4. **Monitoring focus**: 
                   - Track QRS duration on every ECG
                   - If QRS > 50% of baseline or >120 ms → consider dose reduction
                   - Monitor for arrhythmia acceleration
                5. **Metabolite consideration**: Both procainamide and NAPA affect conduction
                """)
            else:
                st.markdown("""
                **🟡 Moderate-Risk Atrial Arrhythmia Protocol:**
                1. **Standard ECG monitoring** - daily for first 3-5 days, then weekly
                2. **Target concentration**: Lower therapeutic range (4-8 mcg/mL)
                3. **Primary concern**: QT prolongation (risk of torsades de pointes)
                4. **Monitoring focus**:
                   - Measure QTc interval baseline and at 2-3 days
                   - If QTc prolongs >60 ms from baseline → reconsider therapy
                   - Monitor electrolytes (K⁺, Mg²⁺, Ca²⁺) weekly
                5. **Metabolite consideration**: NAPA can also prolong QT
                """)
            
            # Acetylator-specific guidance
            st.markdown("---")
            st.markdown("### 💊 Acetylator Phenotype Guidance")
            
            if pk['p_acetylator'] == "Fast":
                st.markdown("""
                **Fast Acetylators:**
                - Rapidly convert procainamide → NAPA
                - May accumulate NAPA, which lacks antiarrhythmic properties but retains toxicity risk
                - **Action**: Monitor total (Proc + NAPA) levels; higher maintenance doses may be needed
                - **Dosing**: Consider higher target procainamide level (upper range 8-10) or increase frequency
                """)
            elif pk['p_acetylator'] == "Slow":
                st.markdown("""
                **Slow Acetylators:**
                - Accumulate procainamide; less NAPA formation
                - Higher risk of procainamide-related toxicity
                - **Action**: Lower maintenance doses; monitor for CNS toxicity (tremor, confusion)
                - **Dosing**: Consider lower target procainamide level (lower range 4-6)
                - **Risk**: Drug-induced lupus-like syndrome with prolonged therapy
                """)
            else:
                st.markdown("""
                **Unknown Acetylator Status:**
                - Monitor BOTH procainamide and NAPA levels closely
                - Initial dosing should be conservative (lower end of range)
                - Check metabolic phenotype if possible (genetic testing or acetaminophen challenge)
                - Adjust based on response and emerging side effects
                """)

    else:
        st.info("Process a calculation in the Dosing tab first to generate documentation.")
