import os
import requests
import json
import base64
import numpy as np
from PIL import Image
import io

class OllamaImageToMusicPrompt:
    """
    A ComfyUI node that uses Ollama's LLaVA model to analyze an image
    and generate a music prompt based on the visual content.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "prompt_style": (["descriptive", "mood_based", "genre_specific", "cinematic"],),
                "ollama_host": ("STRING", {
                    "default": "http://localhost:11434",
                    "multiline": False
                }),
                "model": ("STRING", {
                    "default": "llava:7b",
                    "multiline": False
                }),
            },
            "optional": {
                "custom_instruction": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "Additional instructions for music prompt generation..."
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("music_prompt",)
    FUNCTION = "generate_music_prompt"
    CATEGORY = "hdelmont/audio"

    def generate_music_prompt(self, image, prompt_style, ollama_host, model, custom_instruction=""):
        """
        Analyze the image using Ollama's LLaVA model and generate a music prompt.
        """

        # Convert ComfyUI image tensor to PIL Image
        image_np = (image[0].cpu().numpy() * 255).astype(np.uint8)
        pil_image = Image.fromarray(image_np)

        # Convert to base64 for Ollama API
        buffered = io.BytesIO()
        pil_image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        # Build the prompt based on style
        system_prompts = {
            "descriptive": (
                "Analyze this image and generate a one-sentence music prompt that describes "
                "what type of music would fit this scene. Focus on the visual elements, "
                "atmosphere, and mood. Be specific about instruments, tempo, and style."
            ),
            "mood_based": (
                "Analyze the mood and emotional tone of this image. Generate a one-sentence "
                "music prompt that captures the feeling and atmosphere. Focus on emotional "
                "qualities like peaceful, energetic, mysterious, uplifting, etc."
            ),
            "genre_specific": (
                "Analyze this image and suggest a specific music genre and style that would "
                "complement it. Generate a one-sentence prompt specifying the genre, tempo, "
                "and key characteristics."
            ),
            "cinematic": (
                "Analyze this image as if it were a scene from a film. Generate a one-sentence "
                "music prompt that describes the soundtrack that would accompany this scene. "
                "Think about drama, pacing, and cinematic elements."
            )
        }

        base_prompt = system_prompts.get(prompt_style, system_prompts["descriptive"])

        if custom_instruction:
            base_prompt += f"\n\nAdditional instructions: {custom_instruction}"

        # Call Ollama API
        try:
            api_url = f"{ollama_host}/api/generate"
            payload = {
                "model": model,
                "prompt": base_prompt,
                "images": [img_base64],
                "stream": False
            }

            response = requests.post(api_url, json=payload, timeout=120)
            response.raise_for_status()

            result = response.json()
            music_prompt = result.get("response", "").strip()

            if not music_prompt:
                music_prompt = "Ambient atmospheric music with gentle melodies"

            print(f"Generated music prompt: {music_prompt}")

            return (music_prompt,)

        except requests.exceptions.RequestException as e:
            error_msg = f"Ollama API error: {str(e)}"
            print(error_msg)
            # Return a fallback prompt instead of failing
            return ("Ambient background music with soft instrumentation",)
        except Exception as e:
            error_msg = f"Error generating music prompt: {str(e)}"
            print(error_msg)
            return ("Ambient background music with soft instrumentation",)

# Node registration
NODE_CLASS_MAPPINGS = {
    "OllamaImageToMusicPrompt": OllamaImageToMusicPrompt
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OllamaImageToMusicPrompt": "Ollama Image to Music Prompt"
}
