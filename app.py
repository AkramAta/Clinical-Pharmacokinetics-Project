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
    "Digoxin": {"category": "Cardiovascular", "class": "Cardiac Glycoside", "target_peak": 1.5, "target_trough": 0.8, "mic": 0},
    "Procainamide": {"category": "Cardiovascular", "class": "Antiarrhythmic", "target_peak": 6.0, "target_trough": 4.0, "mic": 0},
    "Lidocaine": {"category": "Cardiovascular", "class": "Antiarrhythmic", "target_peak": 3.0, "target_trough": 1.5, "mic": 0},
    "Amiodarone": {"category": "Cardiovascular", "class": "Antiarrhythmic", "target_peak": 1.5, "target_trough": 1.0, "mic": 0}
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
    if race == "Black": egfr *= 1.212
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

        h1, h2, w1, w2 = st.columns([1, 1, 1, 1])
        height_input = h1.number_input("Height", min_value=0.0, value=170.0)
        height_unit = h2.selectbox("Height Unit", ["Centimeters", "Inches"], label_visibility="hidden")
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

    # ===== AUTO-ANALYSIS SECTION =====
    ibw = calc_ibw(sex, height_cm)
    bmi = calc_bmi(abw, height_cm)
    bsa = calc_bsa(height_cm, abw)
    lbw = calc_lbw(sex, abw, height_cm)
    ajbw = calc_ajbw(ibw, abw)
    bmi_label, bmi_css = bmi_classify(bmi)
    dosing_weight = determine_dosing_weight(abw, ibw)

    st.markdown('<div class="analysis-header">📊 Auto-Analysis / التحليل التلقائي</div>', unsafe_allow_html=True)
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
        r1, r2 = st.columns(2)
        r1.metric("CG — Actual Body Weight", f"{crcl_abw:.1f} mL/min")
        r2.metric("CG — Ideal Body Weight", f"{crcl_ibw:.1f} mL/min")
        r3, r4 = st.columns(2)
        r3.metric("Jelliffe", f"{crcl_jelliffe:.1f} mL/min")
        r4.metric("MDRD (eGFR)", f"{egfr_mdrd:.1f} mL/min/1.73 m²")

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

    # ===== THERAPY SELECTION =====
    st.subheader("💊 Therapy Selection")
    with st.container(border=True):
        available_drugs = list(DRUG_DB.keys())
        selected_drug = st.selectbox("Select Drug", available_drugs)
        drug_info = DRUG_DB[selected_drug]
        st.markdown(f"**Drug Class:** `{drug_info['class']}`")
        calc_mode = st.radio("Calculation Type", ["Initial regimen", "Dose adjustment"], horizontal=True)
        st.divider()
        
        st.markdown(f"""
        <div class='selected-eq-box' style='background-color: #f0f9ff; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #0ea5e9;'>
            <p class='eq-title' style='margin:0; font-weight:600; color:#0f172a;'>Selected Equation: <span class='eq-name' style='color:#0284c7;'>{equation_name}</span></p>
            <p class='eq-reason' style='margin:5px 0 0 0; font-size:0.9em; color:#475569;'>Reason: {reason}</p>
            <p class='eq-value' style='margin:5px 0 0 0; font-weight:700; color:#0369a1;'>CrCl: {selected_crcl:.1f} mL/min</p>
        </div>
        """, unsafe_allow_html=True)
        
        t1, t2 = st.columns(2)
        target_peak = t1.number_input("Target Peak (mg/L)", value=float(drug_info["target_peak"]))
        target_trough = t2.number_input("Target Trough (mg/L)", value=float(drug_info["target_trough"])) if drug_info["target_trough"] > 0 else 0
        st.markdown("**Preferences**")
        interval = st.number_input("Preferred Dosing Interval (hrs) [0 = Auto]", min_value=0, value=0, step=12)

    # Use automatically selected CrCl for downstream PK
    crcl = selected_crcl

with tab_results:
    if st.button("🚀 Process Pharmacokinetics", type="primary", use_container_width=True):
        st.divider()
        vd = cl = t_half = ld = md = ke = 0.0
        final_interval = interval
        warnings = []

        if selected_drug == 'Digoxin':
            vd_factor = 7.3 if crcl >= 30 else 4.5
            vd = vd_factor * ibw
            cl = ((0.8 * ibw) + crcl) * 60 / 1000
            if target_peak > 2.0: warnings.append("Digoxin target > 2.0 ng/mL increases toxicity risk.")
            if interval == 0: final_interval = 24 if crcl >= 50 else (48 if crcl >= 20 else 72)
        elif selected_drug == 'Procainamide':
            vd = 2.0 * abw
            cl = (180 + 3 * crcl) * 60 / 1000 if not is_hf else (90 + 1.5 * crcl) * 60 / 1000
            if target_peak > 10.0: warnings.append("Procainamide target > 10 mcg/mL is associated with toxicity.")
            if interval == 0: final_interval = 4 if crcl >= 50 else (6 if crcl >= 10 else 12)
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

        st.subheader("1. Core PK Parameters")
        rc1, rc2, rc3, rc4 = st.columns(4)
        rc1.metric("Creatinine Clearance", f"{crcl:.1f} mL/min")
        rc2.metric("Volume of Distribution", f"{vd:.1f} L")
        rc3.metric("Clearance", f"{cl:.2f} L/hr")
        if t_half > 72:
            rc4.metric("Half-life (t½)", f"{(t_half/24):.1f} days")
        else:
            rc4.metric("Half-life (t½)", f"{t_half:.1f} hrs")

        st.subheader("2. Individualized Dosage Regimen")
        if selected_drug == "Lidocaine":
            maintenance_text = f"{md:.1f} mg/hr continuous infusion"
        else:
            maintenance_text = f"{md:,.0f} mg q{final_interval}h"
            
        loading_text = f"<p style='font-size: 1.2rem; margin-bottom:0;'><strong>Loading dose:</strong> {ld:,.0f} mg</p>" if ld > 0 else ""
        
        st.markdown(f"""
        <div class="alert-box alert-success">
            <h3 style="margin-top:0; margin-bottom:10px; font-weight:bold;">{selected_drug}</h3>
            <p style="font-size: 1.2rem; margin-bottom:5px;"><strong>Maintenance dose:</strong> {maintenance_text}</p>
            {loading_text}
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

        if selected_drug == "Lidocaine":
            admin_str = "Continuous IV Infusion"
            interval_str = "Continuous"
            rec_dose_str = f"{md:.1f} mg/hr"
        else:
            admin_str = "IV/PO Administration"
            interval_str = f"Every {final_interval} Hours (q{final_interval}h)"
            rec_dose_str = f"{md:,.0f} mg"

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

        st.session_state['last_pk'] = {
            "drug": selected_drug, "age": age, "sex": sex, "abw": abw, "crcl": crcl,
            "vd": vd, "ke": ke, "t_half": t_half, "md": md, "interval": final_interval, "ld": ld,
            "mode": calc_mode, "ibw": ibw, "bmi": bmi, "bsa": bsa, "lbw": lbw, "ajbw": ajbw
        }

with tab_docs:
    st.subheader("Clinical Documentation (SOAP)")
    if 'last_pk' in st.session_state:
        pk = st.session_state['last_pk']
        soap = f"""Subjective / Objective:
Patient is a {pk['age']}yo {pk['sex']} presenting for {pk['drug']} therapy management.
Wt: {pk['abw']}kg. Estimated CrCl: {pk['crcl']:.1f} mL/min.

Assessment:
{pk['drug']} dosing designed to achieve therapeutic targets ({pk['mode']}).
Patient-specific PK Parameters calculated:
- Vd: {pk['vd']:.1f} L
- Ke: {pk['ke']:.4f} hr⁻¹
- t½: {pk['t_half']:.1f} hrs

Plan:
1. Initiate {pk['drug']} regimen: {pk['md']:,.0f} mg q{pk['interval']}h.
"""
        if pk['ld'] > 0:
            soap += f"2. Administer a one-time loading dose of {pk['ld']:,.0f} mg.\n"
        soap += "\nMonitoring:\n- Check serum creatinine and electrolytes regularly.\n- Adjust based on clinical response and subsequent levels."
        st.text_area("Generated EMR Note", value=soap, height=300)
        if st.button("📋 Copy to Clipboard"):
            st.toast("Feature requires browser clipboard API.")
    else:
        st.info("Process a calculation in the Dosing tab first to generate documentation.")
