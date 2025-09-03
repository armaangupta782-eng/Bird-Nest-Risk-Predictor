import streamlit as st
import joblib
import pandas as pd

@st.cache_resource
def load_risk_model():
    return joblib.load("model/risk_model.pkl")

@st.cache_data
def load_columns():
    return joblib.load("model/risk_model_columns.pkl")

def predict_risk_from_manual(
    model,
    all_cols,
    egg_count,
    chick_count,
    habitat,
    nest_stage,
    human,
    predator,
    noise,
):
    row = {
        "egg_count": egg_count,
        "chick_count": chick_count,
        f"habitat_type_{habitat}": 1,
        f"nest_stage_{nest_stage}": 1,
        f"human_disturbance_{human}": 1,
        f"predator_signs_{predator}": 1,
        f"noise_level_{noise}": 1,
    }
    df = pd.DataFrame([row])
    for col in all_cols:
        if col not in df.columns:
            df[col] = 0
    df = df[all_cols]
    pred = model.predict(df)[0]
    return pred

def recommend_mitigation(
    risk_level: str,
    habitat: str,
    nest_stage: str,
    egg_count: int,
    chick_count: int,
    human: str,
    predator: str,
    noise: str,
):
    """
    Returns a prioritized list of concise, practical actions based on inputs.
    Works fully offline; designed to be optionally refined by LLMs.
    """
    recs = []

    # Base on risk level
    if str(risk_level).lower() in {"high", "severe", "3", "4"}:
        recs.append("Initiate immediate protective measures and increase monitoring frequency to daily.")
        recs.append("Flag the site to local conservation/forest officials and record GPS with photos.")
    elif str(risk_level).lower() in {"moderate", "2"}:
        recs.append("Schedule regular monitoring (every 2–3 days) and log any changes in activity or threats.")
    else:
        recs.append("Maintain weekly checks and keep disturbance minimal around the nest site.")

    # Human disturbance
    if human in {"Moderate", "High"}:
        recs.append("Establish a 20–50 m buffer zone with temporary signage to reduce foot traffic.")
        recs.append("Reroute nearby paths and briefly halt noisy activities until chicks fledge.")

    # Predators
    if predator in {"Moderate", "High"}:
        recs.append("Install non-intrusive deterrents (e.g., reflective tape, visual decoys) outside the nest line-of-sight.")
        recs.append("Remove attractants (food scraps) and secure waste to discourage predators.")

    # Noise
    if noise in {"Moderate", "Loud"}:
        recs.append("Limit loud machinery and schedule unavoidable noise outside early morning/late evening peak activity.")
        recs.append("If near roads, consider temporary sound barriers or speed calming measures.")

    # Habitat specific
    if habitat == "Wetland":
        recs.append("Maintain stable water levels and avoid bank vegetation clearance during nesting.")
    elif habitat == "Trees":
        recs.append("Avoid pruning or tree work within a 50 m radius until the nesting period ends.")
    elif habitat == "Grassland":
        recs.append("Delay mowing and keep machinery at least 30 m from the nest area.")

    # Stage specific
    if nest_stage in {"Eggs", "Chicks"}:
        recs.append("Minimize visits to <10 minutes and keep observers concealed to prevent abandonment.")
        recs.append("Record temperature/weather changes that could impact incubation or chick thermoregulation.")

    # Clutch/brood size context
    if egg_count >= 5 or chick_count >= 3:
        recs.append("Prioritize continuous monitoring due to higher reproductive investment at this site.")

    # De-duplicate while preserving order
    deduped = []
    seen = set()
    for r in recs:
        if r not in seen:
            deduped.append(r)
            seen.add(r)

    # Limit to a practical number for field use
    return deduped[:8]
