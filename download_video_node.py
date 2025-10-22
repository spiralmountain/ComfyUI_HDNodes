import requests
import os
import folder_paths
from pathlib import Path
import time

class DownloadVideo:
    """
    Downloads a video from a URL and saves it to ComfyUI output folder
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_url": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "filename_prefix": ("STRING", {
                    "default": "seedance_video",
                    "multiline": False
                }),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("saved_path",)
    FUNCTION = "download_video"
    CATEGORY = "hdelmont/video"
    OUTPUT_NODE = True
    
    def download_video(self, video_url, filename_prefix):
        
        if not video_url or video_url.startswith("Job ID:"):
            raise ValueError("Invalid video URL. Make sure video generation completed successfully.")
        
        # Get output directory
        output_dir = folder_paths.get_output_directory()
        
        # Generate filename with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.mp4"
        filepath = os.path.join(output_dir, filename)
        
        try:
            print(f"Downloading video from: {video_url}")
            
            # Download the video
            response = requests.get(video_url, stream=True, timeout=300)
            response.raise_for_status()
            
            # Save to file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"Video saved to: {filepath}")
            
            return (filepath,)
            
        except Exception as e:
            raise ValueError(f"Failed to download video: {str(e)}")

NODE_CLASS_MAPPINGS = {
    "DownloadVideo": DownloadVideo
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DownloadVideo": "Download Video from URL"
}
