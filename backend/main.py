from fastapi import FastAPI, UploadFile, File
import shutil
import os
from ai_engine import ai_engine
from forensics import generate_ela_heatmap, verify_metadata
from video_processor import video_processor

app = FastAPI()
os.makedirs("temp", exist_ok=True)

@app.post("/verify-media/")
async def verify_media(file: UploadFile = File(...)):
    # 1. Save the uploaded file to the temp directory
    file_path = f"temp/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Extract the file extension to determine the routing path
    file_ext = file.filename.split('.')[-1].lower()
    
    # ==========================================
    # ROUTE A: VIDEO PIPELINE
    # ==========================================
    if file_ext in ['mp4', 'mov', 'avi']:
        # Slices the video into frames (Max 5 for hackathon speed optimization)
        # Note: 'interval_sec' argument was replaced by 'max_frames' to satisfy speed requirements.
        frames = video_processor.extract_frames(file_path, max_frames=5)
        
        if not frames:
            return {"error": "Could not extract frames from video."}
            
        total_fake_score = 0.0
        
        # Run the upgraded FFT engine on every extracted frame
        for frame in frames:
            result = ai_engine.analyze_image(frame)
            total_fake_score += result['ml_confidence_fake']
            
        # Calculate the mathematical average for the entire video
        avg_fake = total_fake_score / len(frames)
        avg_real = 1.0 - avg_fake
        verdict = "AI-Generated" if avg_fake > 0.50 else "Authentic"
        
        ai_results = {
            "verdict": verdict,
            "ml_confidence_fake": float(avg_fake),
            "ml_confidence_real": float(avg_real)
        }
        
        # Scan the video's binary header for C2PA cryptographic credentials
        metadata_results = verify_metadata(file_path)
        
        # Generate an ELA heatmap on the first frame to detect external edits
        first_frame = frames[0]
        heatmap_path = f"temp/heatmap_video_{file.filename}.jpg"
        generate_ela_heatmap(first_frame, heatmap_path)
        
    # ==========================================
    # ROUTE B: STANDARD IMAGE PIPELINE
    # ==========================================
    else:
        # Run the upgraded FFT/Spectral analysis engine
        ai_results = ai_engine.analyze_image(file_path)
        metadata_results = verify_metadata(file_path)
        heatmap_path = f"temp/heatmap_{file.filename}"
        generate_ela_heatmap(file_path, heatmap_path)

    # 4. Return the unified JSON payload to the Streamlit frontend
    return {
        "filename": file.filename,
        "ai_analysis": ai_results,
        "metadata": metadata_results,
        "heatmap_generated": True,
        "heatmap_path": heatmap_path
    }