import os
import time
import json
from PIL import Image
import numpy as np
import torch
import folder_paths
import io
import base64
import tempfile

class SeedanceImageToVideo:
    """
    Seedance Image to Video Node (via Fal.ai)
    Converts images to videos using ByteDance's Seedance API through Fal.ai
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "high-end real-estate agency promo video, lock camera but add subtle motion and life, variations in lighting"
                }),
                "fal_api_key": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "model_version": (["pro", "lite"], {"default": "pro"}),
                "resolution": (["1080p", "720p", "480p"], {"default": "1080p"}),
                "aspect_ratio": (["auto", "21:9", "16:9", "4:3", "1:1", "3:4", "9:16"], {"default": "auto"}),
                "duration": ("INT", {"default": 5, "min": 3, "max": 12}),
                "seed": ("INT", {"default": -1, "min": -1, "max": 0xffffffffffffffff}),
                "camera_fixed": ("BOOLEAN", {"default": False}),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("video_url",)
    FUNCTION = "generate_video"
    CATEGORY = "hdelmont/video"
    
    def generate_video(self, image, prompt, fal_api_key, model_version, resolution, 
                       aspect_ratio, duration, seed, camera_fixed):
        
        if not fal_api_key:
            raise ValueError("Fal.ai API key is required. Get one at https://fal.ai/dashboard/keys")
        
        try:
            import fal_client as fal
        except ImportError:
            raise ImportError("fal_client not installed. Install with: pip install fal-client")
        
        # Set up Fal.ai credentials
        os.environ["FAL_KEY"] = fal_api_key
        
        # Convert ComfyUI image tensor to PIL Image
        image_np = (image[0].cpu().numpy() * 255).astype(np.uint8)
        pil_image = Image.fromarray(image_np)
        
        # Save image to temporary file and upload to Fal.ai
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
            pil_image.save(tmp_file, format='PNG')
            tmp_path = tmp_file.name
        
        try:
            # Upload image to Fal.ai
            print("Uploading image to Fal.ai...")
            image_url = fal.upload_file(tmp_path)
            print(f"Image uploaded: {image_url}")
            
            # Generate random seed if -1
            if seed == -1:
                import random
                seed = random.randint(0, 0xffffffffffffffff)
            
            # Prepare the request payload
            model_id = f"fal-ai/bytedance/seedance/v1/{model_version}/image-to-video"
            
            payload = {
                "image_url": image_url,
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "resolution": resolution,
                "duration": duration,
                "seed": seed,
                "camera_fixed": camera_fixed,
                "enable_safety_checker": True
            }
            
            print(f"Generating video with Seedance {model_version}...")
            print(f"Prompt: {prompt}")
            
            # Submit the job
            result = fal.subscribe(
                model_id,
                arguments=payload,
                with_logs=True,
                on_queue_update=lambda update: print(f"Queue update: {update}")
            )
            
            # Extract video URL from result
            if "video" in result:
                video_data = result["video"]
                if isinstance(video_data, dict) and "url" in video_data:
                    video_url = video_data["url"]
                elif isinstance(video_data, str):
                    video_url = video_data
                else:
                    video_url = str(video_data)
                    
                print(f"Video generated successfully: {video_url}")
                return (video_url,)
            else:
                print(f"Result: {result}")
                return (json.dumps(result),)
                
        except Exception as e:
            raise ValueError(f"Fal.ai API error: {str(e)}")
        finally:
            # Clean up temp file
            try:
                os.unlink(tmp_path)
            except:
                pass

NODE_CLASS_MAPPINGS = {
    "SeedanceImageToVideo": SeedanceImageToVideo
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SeedanceImageToVideo": "Seedance Image to Video (Fal.ai)"
}
