import os
import pandas as pd
import streamlit as st

BIRDS_DIR = "birds"
TRAIN_CSV = os.path.join(BIRDS_DIR, "train_metadata.csv")

@st.cache_data
def load_train_metadata():
    df = pd.read_csv(TRAIN_CSV)
    df = df.dropna(subset=["latitude", "longitude", "common_name", "primary_label"])
    # Optional: Add audio file paths if you need them later
    # BASE_PATH should be adjusted if you actually have audio locally
    return df
