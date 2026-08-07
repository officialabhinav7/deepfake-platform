import streamlit as st
import requests
import os

API_URL = "http://127.0.0.1:8000/verify-media/"

st.set_page_config(page_title="Deepfake Verification", layout="wide")
st.title("🛡️ Advanced Media Authenticity Platform")

# 1. UPDATE: Expand the uploader to accept video formats
uploaded_file = st.file_uploader("Upload Media (Image or Video)", type=["jpg", "jpeg", "png", "mp4", "mov", "avi"])

if uploaded_file is not None:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Original Media")
        # 2. UPDATE: Detect file type to display either an image or a video player
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension in ['mp4', 'mov', 'avi']:
            st.video(uploaded_file)
        else:
            # We display the original image natively to ensure the visual quality of your face is perfectly represented on screen
            st.image(uploaded_file, use_container_width=True)

    with col2:
        # 3. UPDATE: Add a warning that videos take slightly longer to process
        with st.spinner("Analyzing media pipelines (videos may take a moment to extract frames)..."):
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
                
                st.write("**Hybrid AI Confidence Scores (CV + ML)**")
                fake_score = data['ai_analysis']['ml_confidence_fake']
                real_score = data['ai_analysis']['ml_confidence_real']
                
                st.progress(fake_score, text=f"AI-Generated Probability: {fake_score * 100:.2f}%")
                st.progress(real_score, text=f"Authentic Probability: {real_score * 100:.2f}%")
                
                st.divider()
                
                # --- C2PA Cryptographic Section ---
                st.subheader("Cryptographic Provenance (C2PA)")
                meta_status = data['metadata']['status']
                if data['metadata'].get('tamper_evident', False):
                    st.success(f"✅ {meta_status} - Digital origin verified.")
                else:
                    st.warning(f"⚠️ {meta_status} - Origin cannot be mathematically proven.")
                
                st.divider()
                
                # --- Forensics Section ---
                st.subheader("Explainability: ELA Forensics")
                st.markdown("*Bright, glowing regions indicate mismatched compression, highlighting potential **external** manipulations.*")
                
                # The API returns the heatmap path for both images and the first extracted video frame
                heatmap_local_path = f"../backend/{data['heatmap_path']}"
                
                if os.path.exists(heatmap_local_path):
                    st.image(heatmap_local_path, caption="Error Level Analysis Heatmap", use_container_width=True)
                else:
                    st.warning("Heatmap could not be loaded.")
            else:
                st.error("Backend Error: Ensure the FastAPI server is running.")