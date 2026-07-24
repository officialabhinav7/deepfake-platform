import streamlit as st
import requests
import os

API_URL = "http://127.0.0.1:8000/verify-media/"

st.set_page_config(page_title="Deepfake Verification", layout="wide")
st.title("🛡️ Advanced Media Authenticity Platform")

uploaded_file = st.file_uploader("Upload Media (Image)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Original File")
        st.image(uploaded_file, use_container_width=True)

    with col2:
        with st.spinner("Analyzing image pipelines..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            response = requests.post(API_URL, files=files)
            
            if response.status_code == 200:
                data = response.json()
                
                # --- AI Verdict Section ---
                st.subheader("System Verdict")
                verdict = data['ai_analysis']['verdict']
                
                if verdict == "Authentic":
                    st.success(f"Final Verdict: {verdict}")
                else:
                    st.error(f"Final Verdict: {verdict}")
                
                st.write("**AI Confidence Scores**")
                fake_score = data['ai_analysis']['ml_confidence_fake']
                real_score = data['ai_analysis']['ml_confidence_real']
                
                st.progress(fake_score, text=f"AI-Generated Probability: {fake_score * 100:.2f}%")
                st.progress(real_score, text=f"Authentic Probability: {real_score * 100:.2f}%")
                
                st.divider()
                
                # --- Forensics Section ---
                st.subheader("Explainability: ELA Forensics")
                st.markdown("*Bright, glowing regions indicate mismatched compression, highlighting potential **external** manipulations.*")
                
                # Because the backend and frontend are on the same machine, 
                # we can tell Streamlit to just open the heatmap file directly.
                heatmap_local_path = f"../backend/{data['heatmap_path']}"
                
                if os.path.exists(heatmap_local_path):
                    st.image(heatmap_local_path, caption="Error Level Analysis Heatmap", use_container_width=True)
                else:
                    st.warning("Heatmap could not be loaded.")
            else:
                st.error("Backend Error: Ensure the FastAPI server is running.")