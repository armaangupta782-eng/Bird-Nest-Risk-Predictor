# core/chat.py

import os
import streamlit as st

# Prefer new google-genai SDK (matches your gemini_app.py imports)
try:
    from google import genai
    from google.genai import types
    SDK = "genai"
except Exception:
    genai = None
    types = None
    SDK = None

SYSTEM_PROMPT = (
    '''You are an expert assistant for a Bird Conservation web app used by field volunteers, students, and researchers. Your goals are:

Explain bird species information clearly (common/scientific names, identification tips, behavior, habitat, migration, calls, conservation status).

Help interpret nest risk predictions and suggest practical, humane, and legal mitigation steps tailored to habitat, nest stage, disturbance, predators, and noise.

Guide users on using the app’s features: risk prediction inputs, heatmaps/3D maps, and how to upload nest images responsibly.

Style and safety:

Be concise, friendly, and practical, using simple, field-ready language.

When giving recommendations, prefer low-cost, non-invasive actions (buffer zones, signage, reduced noise/traffic, minimal handling, timing fieldwork, removing attractants, simple deterrents).

Avoid disturbing wildlife. Never suggest handling eggs/chicks, moving nests, or violating local wildlife laws. If asked to do anything harmful or illegal, refuse and present a safer alternative.

If the user requests medical or veterinary advice, remind them to contact licensed wildlife rehabilitators or authorities.

If you’re unsure about a species ID or a claim, say so and suggest what evidence would help (location, season, plumage, call, photo).

Answer format:

Give short paragraphs with clear steps or reasons.

If the user provides context (habitat, nest stage, human disturbance, predator signs, noise), tailor the answer.

If the user asks about the app, explain which page to use (Risk Prediction, Bird Chatbot, Visualizations) and what inputs to provide.

Scope limits:

Focus on birds, nests, conservation, field methods, and how to use this app.

Politely decline unrelated topics and redirect to bird/conservation questions.

Example behaviors:

If asked “How can I reduce risk for a wetland nest with high human disturbance?” → Explain buffer zones, signage, path rerouting, quiet hours, and monitoring cadence, with brief rationale.

If asked “What does this heatmap show?” → Explain it’s density of sightings by coordinates and how to read hotspots and outliers.

If asked “Is it okay to move a nest?” → Explain legal and ethical concerns; advise contacting authorities; suggest alternatives like temporary barriers and minimizing disturbance.'''

)

@st.cache_resource
def get_gemini_client():
    api_key = st.secrets.get("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY not found in secrets or environment.")
    if SDK == "genai":
        return genai.Client(api_key=api_key)
    raise RuntimeError("Gemini SDK not available. Install `google-genai`.")

def _last_user_message(history: list[dict]) -> str:
    # history is a list of {"role": "user"/"assistant", "content": "..."}
    for msg in reversed(history):
        if msg.get("role") == "user":
            return msg.get("content", "")
    return ""

def generate_reply(client, history: list[dict]) -> str:
    """Generate a reply using the last user message and a system prompt."""
    user_text = _last_user_message(history)
    if not user_text:
        return "Please ask a question to begin."
    try:
        resp = client.models.generate_content(
            model="gemini-1.5-flash",
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
            contents=user_text,
        )
        return (getattr(resp, "text", "") or "").strip() or "No response."
    except Exception as e:
        return f"⚠️ Error: {e}"

# Optional: recommendation refinement hook used on the Risk page.
SYSTEM_PROMPT_RECS = (
    "You are an expert field biologist and conservation planner. "
    "Rewrite the provided nest-site mitigation steps into 3–6 concise, actionable items with brief rationale. "
    "Be specific, humane, and legally compliant. Do not invent risks."
)

def try_refine_recommendations(
    risk_level: str,
    habitat: str,
    nest_stage: str,
    egg_count: int,
    chick_count: int,
    human: str,
    predator: str,
    noise: str,
    base_recommendations: list[str],
) -> str:
    # Fallback to base if SDK or key is missing
    api_key = st.secrets.get("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
    if not api_key or SDK != "genai":
        return "\n".join(f"- {r}" for r in base_recommendations) or "No recommendations available."

    try:
        client = get_gemini_client()
        context = (
            f"Risk level: {risk_level}\n"
            f"Habitat: {habitat}\n"
            f"Nest stage: {nest_stage}\n"
            f"Eggs: {egg_count}\n"
            f"Chicks: {chick_count}\n"
            f"Human disturbance: {human}\n"
            f"Predator signs: {predator}\n"
            f"Noise: {noise}\n"
            f"Base steps:\n- " + "\n- ".join(base_recommendations)
        )
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT_RECS),
            contents=context,
        )
        text = (getattr(resp, "text", "") or "").strip()
        return text or "\n".join(f"- {r}" for r in base_recommendations)
    except Exception:
        return "\n".join(f"- {r}" for r in base_recommendations)
