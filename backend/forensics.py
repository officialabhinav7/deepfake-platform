import cv2
import numpy as np
import os
import c2pa
import json

def generate_ela_heatmap(image_path: str, output_path: str, quality: int = 90) -> str:
    original = cv2.imread(image_path)
    temp_compressed = "temp_compressed.jpg"
    cv2.imwrite(temp_compressed, original, [cv2.IMWRITE_JPEG_QUALITY, quality])
    compressed = cv2.imread(temp_compressed)
    
    diff = cv2.absdiff(original, compressed)
    max_diff = np.max(diff)
    if max_diff == 0:
        max_diff = 1
        
    scale = 255.0 / max_diff
    ela_image = cv2.convertScaleAbs(diff, alpha=scale)
    heatmap = cv2.applyColorMap(ela_image, cv2.COLORMAP_JET)
    cv2.imwrite(output_path, heatmap)
    os.remove(temp_compressed)
    return output_path

def verify_metadata(image_path: str) -> dict:
    try:
        json_report = c2pa.verify_from_file_json(image_path, None)
        data = json.loads(json_report)
        
        if "active_manifest" in data:
            return {"status": "Authentic Provenance Found", "tamper_evident": True}
        return {"status": "No Credentials Found", "tamper_evident": False}
        
    except Exception as e:
        return {"status": "No Credentials Found", "tamper_evident": False, "error": str(e)}