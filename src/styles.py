
import streamlit as st

def apply_glass_style():
    """
    Applies a modern Glassmorphism style to the Streamlit app using custom CSS.
    """
    st.markdown("""
        <style>
        /* Import Google Font */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

        /* Global Defaults */
        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
        }

        /* App Background - Dark Gradient */
        .stApp {
            background: linear-gradient(135deg, #1e0533 0%, #11032b 50%, #000000 100%);
            background-attachment: fixed;
        }

        /* Sidebar Glass Effect */
        section[data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* Metric Cards */
        div[data-testid="stMetric"] {
            background-color: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 10px;
            color: white;
            transition: transform 0.2s ease-in-out;
            backdrop-filter: blur(10px);
        }
        div[data-testid="stMetric"]:hover {
            transform: scale(1.02);
            background-color: rgba(255, 255, 255, 0.1);
            border-color: rgba(255, 255, 255, 0.2);
        }
        div[data-testid="stMetricLabel"] {
            color: #d1d1d1 !important;
        }
        div[data-testid="stMetricValue"] {
            color: #ffffff !important;
        }

        /* Buttons (Glassy) */
        .stButton > button {
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            backdrop-filter: blur(4px);
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            background: rgba(255, 255, 255, 0.2);
            border-color: rgba(255, 255, 255, 0.4);
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }
        
        /* Inputs & Text Areas */
        .stTextInput > div > div > input, 
        .stSelectbox > div > div > div {
            background-color: rgba(255, 255, 255, 0.05) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 8px;
        }
        .stTextInput > div > div > input:focus {
            border-color: #9d4edd !important;
            box-shadow: 0 0 10px rgba(157, 78, 221, 0.3) !important;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #ffffff !important;
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        }
        
        /* Custom Container Glass */
        .glass-container {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 20px;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)
