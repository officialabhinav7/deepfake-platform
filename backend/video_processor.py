import cv2
import os

class VideoProcessor:
    def __init__(self, output_dir="temp_frames"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def extract_frames(self, video_path: str, max_frames: int = 5) -> list:
        vidcap = cv2.VideoCapture(video_path)
        total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if total_frames <= 0:
            vidcap.release()
            return []

        # Calculate step size to pick up to 5 evenly spaced frames
        step = max(1, total_frames // max_frames)
        extracted_paths = []
        frame_id = 0

        for i in range(0, total_frames, step):
            if len(extracted_paths) >= max_frames:
                break
            vidcap.set(cv2.CAP_PROP_POS_FRAMES, i)
            success, image = vidcap.read()
            if success:
                frame_path = f"{self.output_dir}/frame_{frame_id}.jpg"
                # Save at 100% quality to avoid degrading facial detail for ELA analysis
                cv2.imwrite(frame_path, image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
                extracted_paths.append(frame_path)
                frame_id += 1

        vidcap.release()
        return extracted_paths

video_processor = VideoProcessor()