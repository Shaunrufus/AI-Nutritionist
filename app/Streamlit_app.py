import streamlit as st
import pandas as pd
import joblib
from groq import Groq

# Debug: Show if key is loaded
st.write("🔑 Loaded key:", st.secrets.get("GROQ_API_KEY", "NOT FOUND"))

# ===== 1. ENVIRONMENT CONFIGURATION =====
def get_api_key():
    """Get API key from Streamlit secrets (cloud) or local .env (dev)"""
    try:
        return st.secrets["GROQ_API_KEY"]
    except KeyError:
        try:
            from dotenv import load_dotenv
            import os
            load_dotenv()
            return os.getenv("GROQ_API_KEY")
        except:
            return None

# Initialize client
api_key = get_api_key()
if not api_key:
    st.error("""
    ❌ API Key not configured!
    For Cloud: Add to Streamlit Secrets as:
    [secrets]
    GROQ_API_KEY = "your_key_here"
    
    For Local: Create .env file with:
    GROQ_API_KEY=your_key_here
    """)
    st.stop()

# Connect Groq client
try:
    groq_client = Groq(api_key=api_key)
except Exception as e:
    st.error(f"❌ API Connection Failed: {str(e)}")
    st.stop()

# ===== 2. SIMPLIFIED MODEL LOADING =====
@st.cache_resource
def load_ml_model():
    try:
        return joblib.load("models/nutrition_regressor.pkl")
    except Exception as e:
        st.error(f"❌ Model Error: {str(e)}")
        st.stop()

ml_model = load_ml_model()

# ===== 3. YOUR EXISTING UI CODE =====
# [Keep ALL your existing UI and logic below]
# [All your inputs, calculations, and displays remain unchanged]

# ===== 4. YOUR EXISTING UI CODE =====
# [Keep ALL your existing UI code below exactly as is]
# [All your st.title(), inputs, calculations, etc. remain unchanged]

# ===== 3. KEEP ALL YOUR UI CODE BELOW =====
# [Your entire existing UI code remains UNCHANGED]
# [All your st.title(), columns, inputs, etc.]

# ===== 5. REST OF YOUR APP =====
# [Keep all your existing UI code below]
# [All your original UI/functionality remains the same]
# ===== 3. UI SETUP =====
st.set_page_config(
    page_title="AI Nutritionist Pro",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
        html, body, .stApp {
            background: linear-gradient(135deg, #0c1e3e 0%, #1a1a2e 100%);
            color: #e6f7ff;
            font-family: 'Segoe UI', 'Roboto', sans-serif;
        }
        .metric-box {
            background: rgba(20, 50, 80, 0.3);
            border-radius: 12px;
            padding: 1.5rem;
            border-left: 4px solid #5eead4;
            margin-bottom: 1rem;
        }
        .meal-card {
            background: rgba(30, 41, 59, 0.7);
            border-radius: 10px;
            padding: 1.2rem;
            margin: 0.5rem 0;
            border: 1px solid rgba(94, 234, 212, 0.3);
        }
    </style>
""", unsafe_allow_html=True)

# Header
with st.container():
    col1, col2 = st.columns([3,1])
    with col1:
        st.title("🥑 AI Nutritionist Pro")
        st.markdown("""
        <div style='border-radius:12px; padding:1rem; background:rgba(20,50,80,0.3)'>
            Get scientifically-optimized diet plans tailored to your biology.
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/2038/2038694.png", width=120)

# Sidebar with model selection
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Only show available models
    supported_models = ["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768"]
    available_models = [m for m in supported_models if m in st.session_state.get('available_models', [])]
    
    if not available_models:
        st.error("No supported models available")
        st.stop()
        
    model_choice = st.selectbox(
        "AI Model",
        available_models,
        help="70b for quality, 8b for speed"
    )
    
    st.markdown("---")
    st.header("📄 Upload Health Data (Optional)")
    uploaded_file = st.file_uploader("Upload health reports", type=["csv", "pdf"])

# ===== 4. USER INPUTS =====
with st.expander("🧑⚕️ Your Health Profile", expanded=True):
    cols = st.columns(3)
    with cols[0]:
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    with cols[1]:
        age = st.number_input("Age", 5, 100, 30)
    with cols[2]:
        goal = st.selectbox("Goal", ["Weight Loss", "Weight Gain", "Weight Maintenance"])
    
    cols = st.columns(2)
    with cols[0]:
        height_unit = st.radio("Height Unit", ["cm", "m", "ft"], index=0, horizontal=True)
        height = st.number_input(f"Height ({height_unit})", min_value=0.0, value=170.0)
    with cols[1]:
        weight_unit = st.radio("Weight Unit", ["kg", "lbs"], index=0, horizontal=True)
        weight = st.number_input(f"Weight ({weight_unit})", min_value=0.0, value=70.0)

# BMI Calculation
height_m = height / 100 if height_unit == "cm" else height * 0.3048 if height_unit == "ft" else height
weight_kg = weight * 0.453592 if weight_unit == "lbs" else weight
bmi = round(weight_kg / (height_m ** 2), 2) if height_m > 0 else 0

st.markdown(f"""
<div class='metric-box'>
    <h3 style='color:#5eead4;margin-top:0'>📊 Health Metrics</h3>
    <div style='font-size:1.2rem'>
        <b>BMI:</b> {bmi} • <b>Weight:</b> {weight_kg:.1f} kg • <b>Height:</b> {height_m:.2f} m
    </div>
</div>
""", unsafe_allow_html=True)

# ===== 5. DIET PLAN GENERATION =====
if st.button("✨ Generate Personalized Diet Plan", type="primary"):
    with st.spinner("Analyzing your profile..."):
        try:
            # Get expected features from model
            try:
                expected_features = ml_model.feature_names_in_
            except AttributeError:
                try:
                    expected_features = ml_model.get_booster().feature_names
                except AttributeError:
                    st.error("❌ Could not determine model's expected features")
                    st.stop()

            # Prepare input features
            input_dict = {
                'Age': age,
                'Height_cm': height_m * 100,
                'Weight_kg': weight_kg,
                'BMI': bmi,
                'Gender_Male': 1 if gender == "Male" else 0,
                'Gender_Female': 1 if gender == "Female" else 0,
                'Gender_Other': 1 if gender == "Other" else 0
            }
            
            # Add any missing features with default 0
            for feature in expected_features:
                if feature not in input_dict:
                    input_dict[feature] = 0
            
            input_df = pd.DataFrame([input_dict])[expected_features]
            
            # Make prediction
            prediction = ml_model.predict(input_df)
            if len(prediction[0]) != 4:
                st.error(f"❌ Unexpected prediction format. Expected 4 outputs, got {len(prediction[0])}")
                st.stop()
                
            calories, protein, carbs, fat = prediction[0]
            
            with st.spinner("Generating your meal plan..."):
                try:
                    response = groq_client.chat.completions.create(
                        model=model_choice,
                        messages=[
                            {
                                "role": "system",
                                "content": """You are an expert nutritionist creating detailed Indian meal plans with:
                                - Exact portion sizes in grams
                                - Preparation instructions
                                - Nutritional breakdown per meal
                                - Budget-friendly ingredients
                                - Easy-to-find items"""
                            },
                            {
                                "role": "user",
                                "content": f"""Create a {goal.lower()} meal plan for:
                                - {age}y/o {gender.lower()}
                                - BMI: {bmi}
                                - Daily needs: {calories:.0f} kcal
                                - Macros: {protein:.0f}g protein, {carbs:.0f}g carbs, {fat:.0f}g fat
                                
                                Structure:
                                1. Breakfast (protein focus)
                                2. Mid-morning snack
                                3. Lunch (balanced)
                                4. Evening snack
                                5. Dinner (light)
                                6. Hydration tips
                                
                                Format with Markdown headings and bullet points"""
                            }
                        ],
                        temperature=0.7,
                        max_tokens=3000
                    )
                    
                    # Display results
                    st.markdown("""
                    <div style='background:rgba(15,23,42,0.7);border-radius:12px;padding:1.5rem;margin-top:2rem'>
                        <h2 style='color:#5eead4'>🍽️ Your Personalized Diet Plan</h2>
                        <div class='meal-card'>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(response.choices[0].message.content)
                    
                    st.markdown("</div></div>", unsafe_allow_html=True)
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"""
                    🚨 Error generating meal plan:
                    {str(e)}
                    
                    Try:
                    1. Checking your Groq quota
                    2. Using a different model
                    3. Reducing max_tokens parameter
                    """)
                    
        except Exception as e:
            st.error(f"""
            ⚠️ Nutrition calculation failed:
            {str(e)}
            
            Possible fixes:
            1. Check your input values
            2. Verify model compatibility
            3. Check model file integrity
            """)