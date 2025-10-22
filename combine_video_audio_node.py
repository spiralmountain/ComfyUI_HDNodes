import os
import subprocess
import requests
import folder_paths
import time
import tempfile
from pathlib import Path

class CombineVideoAudio:
    """
    Combines video (from URL or file) with audio file using ffmpeg
    Downloads video from Seedance URL automatically
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_url_or_path": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "audio_path": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "filename_prefix": ("STRING", {
                    "default": "video_with_audio",
                    "multiline": False
                }),
                "audio_volume": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1
                }),
            },
            "optional": {
                "trim_audio_to_video": ("BOOLEAN", {"default": True}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("output_path",)
    FUNCTION = "combine_video_audio"
    CATEGORY = "hdelmont/video"
    OUTPUT_NODE = True
    
    def download_video(self, url, output_path):
        """Download video from URL"""
        print(f"Downloading video from: {url}")
        response = requests.get(url, stream=True, timeout=300)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        print(f"Video downloaded to: {output_path}")
        return output_path
    
    def combine_video_audio(self, video_url_or_path, audio_path, filename_prefix, 
                           audio_volume, trim_audio_to_video=True):
        
        if not video_url_or_path:
            raise ValueError("Video URL or path is required")
        
        if not audio_path or not os.path.exists(audio_path):
            raise ValueError(f"Audio file not found: {audio_path}")
        
        # Determine if input is URL or local path
        is_url = video_url_or_path.startswith(('http://', 'https://'))
        
        # Get output directory
        output_dir = folder_paths.get_output_directory()
        
        # Handle video input
        temp_video = None
        try:
            if is_url:
                # Download video to temp file
                temp_video = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
                video_path = temp_video.name
                temp_video.close()
                self.download_video(video_url_or_path, video_path)
            else:
                # Use local file
                video_path = video_url_or_path
                if not os.path.exists(video_path):
                    raise ValueError(f"Video file not found: {video_path}")
            
            # Generate output filename with timestamp
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_filename = f"{filename_prefix}_{timestamp}.mp4"
            output_path = os.path.join(output_dir, output_filename)
            
            # Build ffmpeg command
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-i", audio_path,
                "-c:v", "copy",  # Copy video stream without re-encoding
                "-c:a", "aac",   # Encode audio to AAC
                "-b:a", "192k",  # Audio bitrate
            ]
            
            # Audio volume adjustment
            if audio_volume != 1.0:
                cmd.extend(["-filter:a", f"volume={audio_volume}"])
            
            # Handle audio length vs video length
            if trim_audio_to_video:
                cmd.extend(["-shortest"])  # Stop at shortest stream (usually video)
            
            cmd.extend([
                "-y",  # Overwrite output file
                output_path
            ])
            
            print(f"Combining video and audio...")
            print(f"Video: {video_path}")
            print(f"Audio: {audio_path}")
            
            # Run ffmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                raise ValueError(f"ffmpeg error: {result.stderr}")
            
            print(f"Video with audio saved to: {output_path}")
            
            return (output_path,)
            
        except subprocess.TimeoutExpired:
            raise ValueError("Video processing timed out (>5 minutes)")
        except FileNotFoundError:
            raise ValueError("ffmpeg not found. Please install ffmpeg: sudo yum install ffmpeg -y")
        except Exception as e:
            raise ValueError(f"Failed to combine video and audio: {str(e)}")
        finally:
            # Clean up temp video file
            if temp_video and os.path.exists(temp_video.name):
                try:
                    os.unlink(temp_video.name)
                except:
                    pass

NODE_CLASS_MAPPINGS = {
    "CombineVideoAudio": CombineVideoAudio
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CombineVideoAudio": "Combine Video + Audio"
}
