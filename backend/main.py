from fastapi import FastAPI, UploadFile, File
import shutil
import os
from ai_engine import ai_engine
from forensics import generate_ela_heatmap

app = FastAPI()
os.makedirs("temp", exist_ok=True)

@app.post("/verify-media/")
async def verify_media(file: UploadFile = File(...)):
    # 1. Save the uploaded file
    file_path = f"temp/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 2. Run the TensorFlow AI Brain
    ai_results = ai_engine.analyze_image(file_path)
    
    # 3. Run the Digital Forensics Engine
    heatmap_path = f"temp/heatmap_{file.filename}"
    generate_ela_heatmap(file_path, heatmap_path)
    
    # 4. Return all data to the frontend
    return {
        "filename": file.filename,
        "ai_analysis": ai_results,
        "heatmap_generated": True,
        "heatmap_path": heatmap_path
    }