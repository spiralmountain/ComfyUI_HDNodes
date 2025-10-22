import os
import requests
import folder_paths
import time
import tempfile

class FalAudioGeneration:
    """
    Generates audio/music using Fal.ai API
    Outputs audio file path for use with Combine Video + Audio node
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "upbeat background music, corporate, professional"
                }),
                "fal_api_key": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "model": ([
                    "beatoven/music-generation",
                    "beatoven/sound-effect-generation",
                    "fal-ai/stable-audio",
                    "fal-ai/musicgen"
                ], {"default": "beatoven/music-generation"}),
                "duration": ("INT", {
                    "default": 10,
                    "min": 1,
                    "max": 60
                }),
                "seed": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 0xffffffffffffffff
                }),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("audio_path",)
    FUNCTION = "generate_audio"
    CATEGORY = "hdelmont/audio"
    OUTPUT_NODE = True
    
    def download_audio(self, url, output_path):
        """Download audio from URL"""
        print(f"Downloading audio from: {url}")
        response = requests.get(url, stream=True, timeout=300)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        print(f"Audio downloaded to: {output_path}")
        return output_path
    
    def generate_audio(self, prompt, fal_api_key, model, duration, seed):
        
        if not fal_api_key:
            raise ValueError("Fal.ai API key is required. Get one at https://fal.ai/dashboard/keys")
        
        try:
            import fal_client as fal
        except ImportError:
            raise ImportError("fal_client not installed. Install with: pip install fal-client")
        
        # Set up Fal.ai credentials
        os.environ["FAL_KEY"] = fal_api_key
        
        # Generate random seed if -1
        if seed == -1:
            import random
            seed = random.randint(0, 0xffffffffffffffff)
        
        # Prepare payload based on model
        payload = {
            "prompt": prompt,
            "seed": seed
        }
        
        # Add duration if supported
        if "musicgen" in model or "stable-audio" in model:
            payload["duration_seconds"] = duration
        elif "beatoven" in model:
            payload["duration"] = duration
        
        try:
            print(f"Generating audio with {model}...")
            print(f"Prompt: {prompt}")
            print(f"Duration: {duration}s")
            
            # Submit the job
            result = fal.subscribe(
                model,
                arguments=payload,
                with_logs=True,
                on_queue_update=lambda update: print(f"Queue update: {update}")
            )
            
            # Extract audio URL from result
            audio_url = None
            
            if "audio" in result:
                audio_data = result["audio"]
                if isinstance(audio_data, dict) and "url" in audio_data:
                    audio_url = audio_data["url"]
                elif isinstance(audio_data, str):
                    audio_url = audio_data
            elif "audio_file" in result:
                audio_file = result["audio_file"]
                if isinstance(audio_file, dict) and "url" in audio_file:
                    audio_url = audio_file["url"]
                elif isinstance(audio_file, str):
                    audio_url = audio_file
            elif "url" in result:
                audio_url = result["url"]
            
            if not audio_url:
                raise ValueError(f"No audio URL in result: {result}")
            
            # Download audio to output folder
            output_dir = folder_paths.get_output_directory()
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            
            # Determine file extension from URL or default to mp3
            if audio_url.endswith(".wav"):
                ext = "wav"
            elif audio_url.endswith(".flac"):
                ext = "flac"
            else:
                ext = "mp3"
            
            output_filename = f"audio_{timestamp}.{ext}"
            output_path = os.path.join(output_dir, output_filename)
            
            # Download the audio
            self.download_audio(audio_url, output_path)
            
            print(f"Audio generated successfully: {output_path}")
            
            return (output_path,)
            
        except Exception as e:
            raise ValueError(f"Fal.ai API error: {str(e)}")

NODE_CLASS_MAPPINGS = {
    "FalAudioGeneration": FalAudioGeneration
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FalAudioGeneration": "Fal.ai Audio Generation"
}
