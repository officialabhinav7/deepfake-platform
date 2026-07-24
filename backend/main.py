from fastapi import FastAPI, UploadFile, File
import shutil
import os
from ai_engine import ai_engine

app = FastAPI()
os.makedirs("temp", exist_ok=True)

@app.post("/verify-media/")
async def verify_media(file: UploadFile = File(...)):
    file_path = f"temp/{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    ai_results = ai_engine.analyze_image(file_path)
    
    return {
        "filename": file.filename,
        "ai_analysis": ai_results
    }