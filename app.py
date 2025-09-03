import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime
import os
import google.generativeai as genai
import folium
from streamlit_folium import st_folium
import pickle
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import from your birds folder
import sys
sys.path.append('./birds')

try:
    from birds.helper_original import *
    BIRDS_MODULE_AVAILABLE = True
except ImportError:
    BIRDS_MODULE_AVAILABLE = False
    st.warning("Birds module not found. Using fallback visualization methods.")

# Try to import your core modules if they exist
try:
    from core.data import load_train_metadata
    from core.viz import bird_description, scientific_name, heatmap_folium, map_3d_deck
    CORE_MODULES_AVAILABLE = True
except ImportError:
    CORE_MODULES_AVAILABLE = False

# Configure the page
st.set_page_config(
    page_title="🕊️ Nest Risk Predictor",
    page_icon="🕊️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main background and theme */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    /* Custom header styling */
    .main-header {
        background: linear-gradient(90deg, #2E8B57, #3CB371);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }

    .main-title {
        color: white;
        font-size: 3.5rem;
        font-weight: 700;
        text-align: center;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }

    .main-subtitle {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.2rem;
        text-align: center;
        margin-top: 0.5rem;
        font-weight: 300;
    }

    /* Card styling */
    .feature-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        margin-bottom: 1rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }

    /* Navigation styling */
    .nav-container {
        background: rgba(255, 255, 255, 0.95);
        padding: 1rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        height: 10rem;
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }

    /* Success/Warning/Error messages */
    .success-box {
        background: linear-gradient(135deg, #4facfe, #00f2fe);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }

    .warning-box {
        background: linear-gradient(135deg, #f093fb, #f5576c);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }

    /* Form styling */
    .stSelectbox > div > div {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
    }

    .stSlider > div > div > div > div {
        background: linear-gradient(135deg, #667eea, #764ba2);
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    }

    /* Chat styling */
    .chat-container {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 5px 20px rgba(168, 237, 234, 0.3);
    }

    /* Risk prediction styling */
    .risk-card {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(255, 154, 158, 0.4);
    }

    /* Visualization styling */
    .viz-card {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(252, 182, 159, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'home'   # default page
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'total_messages' not in st.session_state:
    st.session_state.total_messages = 0

# Load ML Model for Risk Prediction
@st.cache_resource
def load_risk_model():
    """Load the trained risk prediction model"""
    try:
        with open('./model/risk_model.pkl', 'rb') as f:
            model = pickle.load(f)
        return model
    except FileNotFoundError:
        st.warning("⚠️ Risk model file not found. Using fallback prediction logic.")
        return None
    except Exception as e:
        st.error(f"❌ Error loading model: {str(e)}")
        return None

# Load Bird Data Functions
@st.cache_data
def load_bird_data():
    """Load actual bird data from your dataset"""
    try:
        if CORE_MODULES_AVAILABLE:
            # Use your actual data loading function
            df = load_train_metadata()
            return df
        else:
            # Try to load directly from CSV
            if os.path.exists('./birds/train_metadata.csv'):
                df = pd.read_csv('./birds/train_metadata.csv')
                return df
            else:
                st.warning("⚠️ Bird data file not found. Using sample data.")
                # Fallback sample data
                return pd.DataFrame({
                    'common_name': ['American Robin', 'Blue Jay', 'Cardinal', 'Sparrow', 'Owl'] * 20,
                    'latitude': np.random.uniform(30, 45, 100),
                    'longitude': np.random.uniform(-120, -70, 100),
                    'risk_level': np.random.choice(['Low', 'Medium', 'High'], 100)
                })
    except Exception as e:
        st.error(f"❌ Error loading bird data: {str(e)}")
        return pd.DataFrame()

def get_bird_species_list():
    """Get list of available bird species"""
    try:
        df = load_bird_data()
        if 'common_name' in df.columns:
            return sorted(df['common_name'].unique())
        else:
            # Fallback to image folder
            image_folder = './birds/bird_images/'
            if os.path.exists(image_folder):
                species = []
                for file in os.listdir(image_folder):
                    if file.endswith(('.webp', '.jpg', '.png')):
                        species.append(file.split('.')[0])
                return sorted(species)
            else:
                return ['American Robin', 'Blue Jay', 'Cardinal', 'Sparrow', 'Owl']
    except Exception as e:
        st.error(f" Error getting species list: {str(e)}")
        return ['American Robin', 'Blue Jay', 'Cardinal', 'Sparrow', 'Owl']

def get_bird_scientific_name(bird_name):
    """Get scientific name for a bird species"""
    try:
        if CORE_MODULES_AVAILABLE:
            return scientific_name(bird_name)
        else:
            # Fallback scientific names
            scientific_names = {
                'American Robin': 'Turdus migratorius',
                'Blue Jay': 'Cyanocitta cristata',
                'Cardinal': 'Cardinalis cardinalis',
                'Sparrow': 'Passer domesticus',
                'Owl': 'Strix varia'
            }
            return scientific_names.get(bird_name, 'Scientific name not available')
    except Exception as e:
        return 'Scientific name not available'

def get_bird_description(bird_name):
    """Get description for a bird species"""
    try:
        if CORE_MODULES_AVAILABLE:
            return bird_description(bird_name)
        else:
            return f"A beautiful bird species commonly found in various habitats. {bird_name} is an important part of the ecosystem."
    except Exception as e:
        return "Description not available"

# Gemini Client Functions
def get_gemini_client():
    """Initialize and return Gemini client"""
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            st.error("⚠️ Gemini API key not found in environment variables!")
            return None
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"❌ Error initializing Gemini: {str(e)}")
        return None

def generate_ai_response(prompt, chat_history):
    """Generate response using Gemini AI"""
    try:
        client = get_gemini_client()
        if not client:
            return " Cannot connect to Gemini. Please check your API key."

        system_context = """You are the AI assistant for a Bird Conservation web app used by volunteers, students, and researchers.  

Your goals:
- Explain bird species (common/scientific names, ID tips, behavior, habitat, migration, calls, conservation status).  
- Help interpret nest risk predictions and suggest safe, low-cost, legal mitigation steps.  
- Guide users on app features (Risk Prediction, Visualizations, Bird Chatbot, Nest Image Upload).  

Style:
- Be concise, clear, and field-ready.  
- Prefer simple, non-invasive actions (buffer zones, signage, noise reduction, minimal handling, timing fieldwork, removing attractants, simple deterrents).  
- Never suggest moving nests, handling eggs/chicks, or breaking wildlife laws.  
- If unsure about species ID, say so and suggest useful evidence (location, season, plumage, call, photo).  
- For medical/veterinary issues, direct users to licensed rehabilitators or authorities.  

Limits:
- Give answers only related to birds, nests, conservation, and app usage. 
- Politely decline unrelated requests. If asked to do anything harmful or illegal, refuse and suggest safer alternatives. 

Examples:  
- "How can I reduce risk for a wetland nest with disturbance?" → Explain buffer zones, signage, rerouting paths, quiet hours, monitoring.  
- "What does this heatmap show?" → Explain it's sighting density; guide how to read hotspots/outliers.  
- "Is it okay to move a nest?" → Explain legal/ethical concerns; suggest safe alternatives like barriers or reducing disturbance.  
"""

        conversation = f"{system_context}\n\nUser: {prompt}"

        response = client.generate_content(conversation)

        # Safe text extraction
        if hasattr(response, "text") and response.text:
            return response.text.strip()
        elif hasattr(response, "candidates") and response.candidates:
            return response.candidates[0].content.parts[0].text.strip()
        else:
            return "⚠️ No response received from Gemini."

    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"


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

def predict_nest_risk_fallback(params):
    risk_score = 0
    if params['human'] in ['Moderate', 'High']:
        risk_score += 1
    if params['predator'] in ['Moderate', 'High']:
        risk_score += 1
    if params['noise'] == 'Loud':
        risk_score += 1
    if params['habitat'] == 'Urban':
        risk_score += 1
    if params['egg_count'] > 5 or params['chick_count'] > 5:
        risk_score += 1
    if risk_score >= 3:
        return 'High'
    elif risk_score >= 1:
        return 'Medium'
    else:
        return 'Low'

# Sidebar Navigation
with st.sidebar:
    st.markdown("""
    <div class="nav-container">
        <h2 style="text-align: center; color: #2E8B57; margin-bottom: 1rem;">🕊️ Navigation</h2>
    </div>
    """, unsafe_allow_html=True)

    nav_options = {
        "🏠 Home": "home",
        "🪺 Risk Prediction": "risk",
        "🤖 Bird AI Chatbot": "chatbot",
        "📊 Data Visualizations": "viz",
    }

    for label, page in nav_options.items():
        if st.button(label, key=f"nav_{page}", use_container_width=True):
            st.session_state.page = page
            st.rerun()

# Main content based on selected page
if st.session_state.page == 'home':
    # Home Page
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🕊️ Nest Risk Predictor</h1>
        <p class="main-subtitle">Advanced Machine Learning Tools for Bird Conservation & Research</p>
    </div>
    """, unsafe_allow_html=True)

    # Feature overview
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #2E8B57; text-align: center;">🪺 Risk Assessment</h3>
            <p>Predict nesting site risks using advanced ML models to protect birds.</p>
            <ul>
                <li>Real-time risk scoring</li>
                <li>Mitigation recommendations</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #2E8B57; text-align: center;">🤖 AI Chatbot</h3>
            <p>Interactive AI assistant powered by advanced language models for bird information.</p>
            <ul>
                <li>Species identification</li>
                <li>Conservation guidance</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #2E8B57; text-align: center;">📊 Visualizations</h3>
            <p>Comprehensive data visualization tools for understanding bird distribution patterns and trends.</p>
            <ul>
                <li>Interactive Heatmaps</li>
                <li>Geographic Analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Quick stats
    st.markdown("### 📈 Platform Statistics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <h2>70+</h2>
            <p>Species Monitored</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
            <h2>95%</h2>
            <p>Model Accuracy</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3 style="font-size: 1.7rem;">Random-Forest</h3>
            <p>Prediction Model</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>Integrated with "Gemini"</h3>
            <p>AI Support</p>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.page == 'risk':
    risk_model = load_risk_model()
    all_cols = load_columns()

    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🪺 Nest Risk Assessment</h1>
        <p class="main-subtitle">Predict and mitigate nesting site risks using AI</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>📋 Environmental Assessment Form</h3>
        </div>
        """, unsafe_allow_html=True)
        with st.form("risk_assessment_form", clear_on_submit=False):
            col_a, col_b = st.columns(2)
            with col_a:
                habitat = st.selectbox(
                    "🌲 Habitat Type",
                    ['Trees', 'Wetland', 'Grassland', 'Urban', 'Coastal'],
                    help="Select the primary habitat type where the nest is located"
                )
                nest_stage = st.selectbox(
                    "🥚 Nest Stage",
                    ['Eggs', 'Chicks', 'Building', 'Failed', 'Empty'],
                    help="Current stage of the nesting cycle"
                )
                egg_count = st.slider("🥚 Egg Count", 0, 12, 3)
                chick_count = st.slider("🐣 Chick Count", 0, 10, 2)
            with col_b:
                human = st.selectbox(
                    "👥 Human Disturbance Level",
                    ['None', 'Low', 'Moderate', 'High'],
                    help="Level of human activity in the area"
                )
                predator = st.selectbox(
                    "🦊 Predator Signs",
                    ['None', 'Low', 'Moderate', 'High'],
                    help="Evidence of predator activity nearby"
                )
                noise = st.selectbox(
                    "🔊 Noise Level",
                    ['Quiet', 'Moderate', 'Loud'],
                    help="Ambient noise level in the environment"
                )
            submitted = st.form_submit_button("🔍 Assess Risk Level", use_container_width=True)

        if submitted:
            params = {
                'habitat': habitat,
                'nest_stage': nest_stage,
                'egg_count': egg_count,
                'chick_count': chick_count,
                'human': human,
                'predator': predator,
                'noise': noise
            }

            # Get both predictions
            ml_prediction_ok = True
            try:
                with st.spinner("🤖 Analyzing with ML model..."):
                    raw_risk = predict_risk_from_manual(
                        model=risk_model,
                        all_cols=all_cols,
                        egg_count=egg_count,
                        chick_count=chick_count,
                        habitat=habitat,
                        nest_stage=nest_stage,
                        human=human,
                        predator=predator,
                        noise=noise
                    )
                # Map raw prediction to risk level
                if isinstance(raw_risk, (int, float)):
                    if raw_risk >= 0.7:
                        risk_ml = 'High'
                    elif raw_risk >= 0.4:
                        risk_ml = 'Medium'
                    else:
                        risk_ml = 'Low'
                else:
                    risk_ml = raw_risk
            except Exception as e:
                st.error(f"❌ Error with ML prediction: {str(e)}")
                ml_prediction_ok = False

            # ALWAYS run fallback prediction
            risk_fallback = predict_nest_risk_fallback(params)

            # Decide final risk: ML if both are available, otherwise use fallback
            if ml_prediction_ok:
                # Priority order: High > Medium > Low
                risk_order = ['Low', 'Medium', 'High']
                ml_idx = risk_order.index(risk_ml)
                fb_idx = risk_order.index(risk_fallback)
                final_risk = risk_order[max(ml_idx, fb_idx)]
            else:
                final_risk = risk_fallback

            # Display results
            if final_risk == 'High':
                st.markdown("""
                <div class="warning-box">
                    <h3>⚠️ HIGH RISK DETECTED</h3>
                    <p>Immediate intervention recommended!</p>
                </div>
                """, unsafe_allow_html=True)
            elif final_risk == 'Medium':
                st.markdown("""
                <div style="background: linear-gradient(135deg, #f093fb, #f5576c); color: white; padding: 1rem; border-radius: 10px;">
                    <h3>⚡ MODERATE RISK</h3>
                    <p>Monitor closely and consider precautionary measures.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="success-box">
                    <h3>✅ LOW RISK</h3>
                    <p>Nest conditions appear favorable.</p>
                </div>
                """, unsafe_allow_html=True)


            # ==================
            # Risk-Level-Based Recommendations
            # ==================
            st.markdown("### 💡 AI Recommendations")
            recommendations = []

            # Human Disturbance
            if human in ['Moderate', 'High']:
                if final_risk in ['High', 'Medium']:
                    recommendations.append("🚧 Install protective barriers or signs to reduce human disturbance.")
                    if habitat == 'Urban':
                        recommendations.append("🏙️ For urban nests, consider temporary fencing and community outreach to keep people away.")
                elif final_risk == 'Low' and human in ['Moderate', 'High']:
                    recommendations.append("👀 Observe if human activity increases; mark the nest location for future monitoring.")
            
            # Predator Signs
            if predator in ['Moderate', 'High']:
                if final_risk in ['High', 'Medium']:
                    recommendations.append("🛡️ Deploy non-lethal predator deterrents (reflectors, motion devices, decoys) around the nest.")
                    if egg_count > 5 or chick_count > 5:
                        recommendations.append("🥚🐣 Large clutches—monitor closely for overcrowding and predator activity.")
                elif final_risk == 'Low' and predator in ['Moderate', 'High']:
                    recommendations.append("👀 Be alert for new signs of predators.")
            
            # Noise Level
            if noise == 'Loud':
                if final_risk in ['High', 'Medium']:
                    recommendations.append("🔇 Reduce noise during critical nesting times—coordinate with local authorities if possible.")
                elif final_risk == 'Low' and noise == 'Loud':
                    recommendations.append("👂 Monitor noise levels; document unusual changes for research.")

            # Habitat-Specific
            if habitat == 'Urban' and final_risk in ['High', 'Medium']:
                recommendations.append("🏙️ For urban nests, use signage and temporary barriers to protect the site.")
            elif habitat == 'Wetland' and final_risk in ['High', 'Medium']:
                recommendations.append("🌊 For wetland nests, monitor water levels—prepare for possible relocation if flooding is likely.")
            elif habitat == 'Coastal' and final_risk in ['High', 'Medium']:
                recommendations.append("🌊 For coastal nests, prepare for sudden storms—have relocation supplies on hand.")
            elif habitat == 'Grassland' and final_risk in ['High', 'Medium']:
                recommendations.append("🌾 For grassland nests, mark the area and minimize foot traffic.")
            elif habitat == 'Trees' and final_risk in ['High', 'Medium']:
                recommendations.append("🌳 For tree nests, communicate with landowners to prevent logging during nesting.")
            
            # Nest Stage
            if nest_stage == 'Eggs':
                if final_risk in ['High', 'Medium']:
                    recommendations.append("🥚 Minimize nest visits during incubation—stress can cause abandonment.")
                elif final_risk == 'Low' and nest_stage == 'Eggs':
                    recommendations.append("🥚 Schedule brief, discreet checks to monitor progress.")
            elif nest_stage == 'Chicks':
                if final_risk in ['High', 'Medium']:
                    recommendations.append("🐣 Limit handling and observation time to avoid stressing parents.")
                elif final_risk == 'Low' and nest_stage == 'Chicks':
                    recommendations.append("🐣 Enjoy observing chicks from a safe distance.")
            elif nest_stage == 'Building':
                if final_risk in ['High', 'Medium']:
                    recommendations.append("🪺 Avoid interfering with nest construction; observe from a distance.")
                elif final_risk == 'Low' and nest_stage == 'Building':
                    recommendations.append("🪺 Observe construction—your notes may help future nests.")
            elif nest_stage == 'Failed':
                if final_risk in ['High', 'Medium']:
                    recommendations.append("⚰️ Record probable causes of failure for future prevention.")
                elif final_risk == 'Low' and nest_stage == 'Failed':
                    recommendations.append("🪹 Document the event; valuable for research.")
            elif nest_stage == 'Empty':
                if final_risk in ['High', 'Medium']:
                    recommendations.append("🕊️ Record nest location and condition—inform conservationists if needed.")
                elif final_risk == 'Low' and nest_stage == 'Empty':
                    recommendations.append("🕊️ Log nest details—helpful for future monitoring.")

            # Risk Level Actions
            if final_risk == 'High':
                recommendations.append("📞 Contact local wildlife authorities for immediate assistance.")
                if egg_count > 5 or chick_count > 5:
                    recommendations.append("🆘 Extra vigilance: Large clutches increase the need for secure, safe monitoring.")
            elif final_risk == 'Medium':
                recommendations.append("📅 Schedule regular check-ins—monitor for changes in nest condition.")
                if egg_count > 5 or chick_count > 5:
                    recommendations.append("👁️ Watch for overloading and consider reinforcing nest support if unstable.")
            elif final_risk == 'Low':
                recommendations.append("✨ Continue regular monitoring and document nest progress.")
                if egg_count > 5 or chick_count > 5:
                    recommendations.append("🥚🐣 Large clutch noted—useful for research.")
        
            # Always suggest these basic monitoring practices (for all risk levels)
            recommendations.extend([
                "📸 Document progress with periodic photos.",
                "📊 Log environmental changes in your monitoring database."
            ])

            # Remove duplicates and display
            for i, rec in enumerate(sorted(set(recommendations)), 1):
                st.markdown(f"**{i}.** {rec}")
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>📊 Risk Factors Guide</h3>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        **🔴 High Risk Indicators:**
        - Multiple eggs/chicks with high predator activity
        - Significant human disturbance during nesting
        - Extreme weather conditions
        - Loud, persistent noise pollution
                    
        **🟡 Medium Risk Indicators:**
        - Moderate environmental stressors
        - Some predator signs present
        - Occasional human activity
                    
        **🟢 Low Risk Indicators:**
        - Stable environmental conditions
        - Minimal disturbance factors
        - Protected or remote location
        """)
        st.markdown("""
        <div style="background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); 
                    padding: 1rem; border-radius: 10px; margin: 1rem 0; color: white;">
            <strong>🤖 ML Model Active</strong><br>
            Using trained machine learning model and rule-based logic together
        </div>
        """, unsafe_allow_html=True)


elif st.session_state.page == 'chatbot':
    # AI Chatbot Page
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Bird Conservation AI Assistant</h1>
        <p>Expert knowledge about birds, conservation, and research</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick action buttons at the top
    st.markdown("### 🚀 Quick Questions")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🆔 Help identify a bird species", use_container_width=True):
            quick_prompt = "I need help identifying a bird species. What information should I provide for accurate identification?"
            st.session_state.chat_history.append({"role": "user", "content": quick_prompt})
            st.session_state.total_messages += 1
            
            # Generate AI response
            with st.spinner("🤔 Thinking..."):
                ai_response = generate_ai_response(quick_prompt, st.session_state.chat_history)
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
            st.rerun()

    with col2:
        if st.button("🏠 Ask about nesting behaviors", use_container_width=True):
            quick_prompt = "Tell me about bird nesting behaviors and what factors influence nesting site selection."
            st.session_state.chat_history.append({"role": "user", "content": quick_prompt})
            st.session_state.total_messages += 1
            
            # Generate AI response
            with st.spinner("🤔 Thinking..."):
                ai_response = generate_ai_response(quick_prompt, st.session_state.chat_history)
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
            st.rerun()

    with col3:
        if st.button("🌱 Conservation best practices", use_container_width=True):
            quick_prompt = "What are the most effective bird conservation strategies and best practices for field researchers?"
            st.session_state.chat_history.append({"role": "user", "content": quick_prompt})
            st.session_state.total_messages += 1
            
            # Generate AI response
            with st.spinner("🤔 Thinking..."):
                ai_response = generate_ai_response(quick_prompt, st.session_state.chat_history)
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
            st.rerun()

    # Chat interface
    st.markdown("""
    <div class="feature-card">
        <h3>💬 Ask me anything about birds, conservation, or field research!</h3>
        <p style="margin-bottom: 0;">I can help with species identification, behavior analysis, conservation strategies, and research methodologies.</p>
    </div>
    """, unsafe_allow_html=True)

    # Display chat statistics
    if st.session_state.total_messages > 0:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); 
                    padding: 1rem; border-radius: 15px; margin: 1rem 0; text-align: center; color: white;">
            <strong>💬 Chat Statistics: {st.session_state.total_messages} messages exchanged</strong>
        </div>
        """, unsafe_allow_html=True)

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.markdown(f"**You:** {message['content']}")
            else:
                st.markdown(message['content'])

    # Chat input
    if prompt := st.chat_input("Ask about birds, conservation, habitats, or research methods..."):
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.session_state.total_messages += 1

        with st.chat_message("user"):
            st.markdown(f"**You:** {prompt}")

        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                response = generate_ai_response(prompt, st.session_state.chat_history)
                st.markdown(response)
                
                # Add assistant response to history
                st.session_state.chat_history.append({"role": "assistant", "content": response})

elif st.session_state.page == 'viz':
    # Visualization Page - INTEGRATED WITH YOUR BIRDS FOLDER
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">📊 Data Visualizations</h1>
        <p class="main-subtitle">Explore bird distribution patterns and population dynamics</p>
    </div>
    """, unsafe_allow_html=True)

    # Load actual bird data
    df = load_bird_data()
    
    if df.empty:
        st.error("No bird data available. Please check your data files.")
        st.stop()

    # Get available species
    available_species = get_bird_species_list()
    
    col1, col2 = st.columns([4, 1])

    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>🎛️ Controls</h3>
        </div>
        """, unsafe_allow_html=True)

        bird_species = st.selectbox(
            "🐦 Select Species",
            [
    "Ashy Drongo",
    "Asian Brown Flycatcher",
    "Asian Koel",
    "Barn Swallow",
    "Black Drongo",
    "Black Kite",
    "Black-crowned Night-Heron",
    "Black-hooded Oriole",
    "Black-naped Monarch",
    "Black-winged Kite",
    "Black-winged Stilt",
    "Blyth's Reed Warbler",
    "Bronzed Drongo",
    "Brown Boobook",
    "Brown Shrike",
    "Cattle Egret",
    "Common Greenshank",
    "Common Iora",
    "Common Kingfisher",
    "Common Myna",
    "Common Rosefinch",
    "Common Sandpiper",
    "Common Tailorbird",
    "Coppersmith Barbet",
    "Crested Serpent-Eagle",
    "Eurasian Collared-Dove",
    "Eurasian Coot",
    "Eurasian Hoopoe",
    "Eurasian Marsh-Harrier",
    "Eurasian Moorhen",
    "Garganey",
    "Glossy Ibis",
    "Gray Heron",
    "Gray Wagtail",
    "Gray-breasted Prinia",
    "Gray-headed Canary-Flycatcher",
    "Great Egret",
    "Greater Coucal",
    "Greater Racket-tailed Drongo",
    "Green Sandpiper",
    "Green Warbler",
    "Greenish Warbler",
    "House Crow",
    "House Sparrow",
    "Kentish Plover",
    "Large-billed Crow",
    "Laughing Dove",
    "Little Egret",
    "Little Grebe",
    "Little Ringed Plover",
    "Pied Kingfisher",
    "Plain Prinia",
    "Puff-throated Babbler",
    "Purple Heron",
    "Purple Sunbird",
    "Red-rumped Swallow",
    "Red-wattled Lapwing",
    "Red-whiskered Bulbul",
    "Rock Pigeon",
    "Rose-ringed Parakeet",
    "Rufous Treepie",
    "Scaly-breasted Munia",
    "Spotted Dove",
    "Stork-billed Kingfisher",
    "Tickell's Blue Flycatcher",
    "Western Yellow Wagtail",
    "Whiskered Tern",
    "White-breasted Waterhen",
    "White-throated Kingfisher",
    "Wood Sandpiper",
    "Zitting Cisticola"
],
            help="Choose a bird species to analyze"
        )

        viz_type = st.selectbox(
            "📈 Visualization Type",
            ["Species Information", "Distribution Heatmap", "Geographic Analysis"],
            help="Select the type of visualization"
        )

        # Additional filters based on available data
        if 'latitude' in df.columns and 'longitude' in df.columns:
            show_markers = st.checkbox("📍 Show Individual Observations", value=True)
        
        # Date filter if date column exists
        date_columns = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        if date_columns:
            use_date_filter = st.checkbox("📅 Filter by Date Range")

    with col1:
        if viz_type == "Species Information":
            st.markdown("""
            <div class="feature-card">
                <h3>🐦 Species Profile</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Display species information
            col_a, col_b = st.columns([1, 2])
            
            with col_a:
                # Try to display bird image if available
                image_path = f"./birds/bird_images/{bird_species}.webp"
                if os.path.exists(image_path):
                    st.image(image_path, caption=bird_species, use_container_width=True)
                else:
                    # Try .jpg extension
                    image_path = f"./birds/bird_images/{bird_species}.jpg"
                    if os.path.exists(image_path):
                        st.image(image_path, caption=bird_species, use_container_width=True)
                    else:
                        st.info("📷 Image not available")
            
            with col_b:
                st.markdown(f"### {bird_species}")
                st.markdown(f"**Scientific Name:** *{scientific_n(bird_species, df)}*")
                st.markdown(f"**Description:** {get_bird_description(bird_species)}")

        elif viz_type == "Distribution Heatmap":
            st.markdown("""
            <div class="feature-card">
                <h3>🗺️ Geographic Distribution Heatmap</h3>
            </div>
            """, unsafe_allow_html=True)

            # Check if we have geographic data
            if 'latitude' in df.columns and 'longitude' in df.columns:
                # Filter data for selected species
                if 'common_name' in df.columns:
                    species_data = df[df['common_name'] == bird_species]
                else:
                    species_data = df
                
                if len(species_data) > 0:
                    # Use your existing heatmap function if available
                    if CORE_MODULES_AVAILABLE:
                        try:
                            heatmap_folium(bird_species, df, width=800)
                        except Exception as e:
                            st.error(f"Error creating heatmap: {e}")
                            # Fallback to simple map
                            center_lat = species_data['latitude'].mean()
                            center_lon = species_data['longitude'].mean()
                            
                            m = folium.Map(
                                location=[center_lat, center_lon],
                                zoom_start=6,
                                tiles='OpenStreetMap'
                            )
                            
                            # Add heatmap
                            from folium.plugins import HeatMap
                            heat_data = [[row['latitude'], row['longitude']] for idx, row in species_data.iterrows()]
                            HeatMap(heat_data, radius=15, blur=10, max_zoom=1).add_to(m)
                            
                            st_folium(m, width=800, height=500)
                    else:
                        # Create simple heatmap
                        center_lat = species_data['latitude'].mean()
                        center_lon = species_data['longitude'].mean()
                        
                        m = folium.Map(
                            location=[center_lat, center_lon],
                            zoom_start=6,
                            tiles='OpenStreetMap'
                        )
                        
                        # Add heatmap
                        from folium.plugins import HeatMap
                        heat_data = [[row['latitude'], row['longitude']] for idx, row in species_data.iterrows()]
                        HeatMap(heat_data, radius=15, blur=10, max_zoom=1).add_to(m)
                        
                        # Add markers if requested
                        if show_markers and len(species_data) <= 50:  # Limit for performance
                            for idx, row in species_data.iterrows():
                                folium.Marker(
                                    [row['latitude'], row['longitude']],
                                    popup=f"{bird_species}",
                                    icon=folium.Icon(color='blue', icon='info-sign')
                                ).add_to(m)
                        
                        st_folium(m, width=800, height=500)
                else:
                    st.warning(f"No geographic data available for {bird_species}")
            else:
                st.warning("No latitude/longitude columns found in the dataset")

        elif viz_type == "Geographic Analysis":
            st.markdown("""
            <div class="feature-card">
                <h3>📍 Geographic Distribution Analysis</h3>
            </div>
            """, unsafe_allow_html=True)

            # Check if we have geographic data
            if 'latitude' in df.columns and 'longitude' in df.columns:
                if 'common_name' in df.columns:
                    species_data = df[df['common_name'] == bird_species]
                else:
                    species_data = df
                
                if len(species_data) > 0:
                    # Use your existing 3D visualization if available
                    if CORE_MODULES_AVAILABLE:
                        try:
                            deck = map_3d_deck(bird_species, df)
                            if deck is not None:
                                st.pydeck_chart(deck)
                            else:
                                st.info("Not enough coordinate data for 3D visualization")
                        except Exception as e:
                            st.error(f"Error creating 3D map: {e}")
                    else:
                        # Create scatter plot as fallback
                        fig = px.scatter_mapbox(
                            species_data,
                            lat="latitude",
                            lon="longitude",
                            hover_name="common_name" if "common_name" in species_data.columns else None,
                            zoom=5,
                            height=500,
                            title=f"Distribution: {bird_species}"
                        )
                        fig.update_layout(mapbox_style="open-street-map")
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Show distribution statistics
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("Observation Points", len(species_data))
                        with col_b:
                            lat_range = species_data['latitude'].max() - species_data['latitude'].min()
                            st.metric("Latitude Range", f"{lat_range:.2f}°")
                        with col_c:
                            lon_range = species_data['longitude'].max() - species_data['longitude'].min()
                            st.metric("Longitude Range", f"{lon_range:.2f}°")
                else:
                    st.warning(f"No data available for {bird_species}")
            else:
                st.warning("No geographic coordinates available in the dataset")

        


# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🕊️ Birds Risk Predictor | Powered by Advanced Machine Learning</p>
    <p>Built for researchers, conservationists, and field volunteers worldwide</p>
</div>
""", unsafe_allow_html=True)