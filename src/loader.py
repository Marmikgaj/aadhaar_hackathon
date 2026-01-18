import pandas as pd
import streamlit as st
import os

# Define constants for file paths
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Data", "Combined_CSV")
ENROLMENT_PATH = os.path.join(DATA_DIR, "api_data_aadhar_enrolment_combined.csv")
DEMOGRAPHIC_PATH = os.path.join(DATA_DIR, "api_data_aadhar_demographic_combined.csv")
BIOMETRIC_PATH = os.path.join(DATA_DIR, "api_data_aadhar_biometric_combined.csv")

@st.cache_data
def load_data():
    """
    Loads and caches the Aadhaar datasets.
    Returns a dictionary containing the three dataframes.
    """
    try:
        enrolment_df = pd.read_csv(ENROLMENT_PATH)
        demographic_df = pd.read_csv(DEMOGRAPHIC_PATH)
        biometric_df = pd.read_csv(BIOMETRIC_PATH)

        # Basic preprocessing
        for df in [enrolment_df, demographic_df, biometric_df]:
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
            
            if 'state' in df.columns:
                df['state'] = df['state'].astype(str).str.strip().str.title()
        
        return {
            "enrolment": enrolment_df,
            "demographic": demographic_df,
            "biometric": biometric_df
        }
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def get_state_list(df):
    """Returns a sorted list of unique states from the dataframe."""
    """Returns a sorted list of unique states from the dataframe."""
    return sorted([s for s in df['state'].unique().tolist() if isinstance(s, str) and not any(char.isdigit() for char in s)])

def get_district_list(df, state):
    """Returns a sorted list of unique districts for a given state."""
    return sorted(df[df['state'] == state]['district'].unique().tolist())
