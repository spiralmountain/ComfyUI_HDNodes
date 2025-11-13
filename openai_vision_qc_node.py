import os
import base64
import io
import json
import numpy as np
import torch
from PIL import Image
from openai import OpenAI

class OpenAIVisionQC:
    """
    ComfyUI node for OpenAI's Vision API - Quality Control with Article Context
    Only removes elements like utility infrastructure if they don't relate to the article
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "postTitle": ("STRING", {"multiline": False, "default": ""}),
                "postContent": ("STRING", {"multiline": True, "default": ""}),
                "brandProfile": ("STRING", {"multiline": True, "default": ""}),
                "prompt": ("STRING", {"multiline": True, "default": """You are an expert in luxury real estate image quality control.

Analyze the upscaled image and identify ONLY obvious flaws requiring correction. If no issues exist, output nothing.

ARTICLE TITLE: {postTitle}
ARTICLE CONTENT: {postContent}
BRAND TIER: {brandProfile}

SCAN FOR THREE TYPES OF ISSUES:

REMOVE (preserve structure, remove only these elements):
- Illegible text, words, letters on surfaces (keep blank blueprints/maps)
- Logos, watermarks, branding marks
- Visible people (whole, partial, distant)
- Utility infrastructure (power lines, poles, satellite dishes, exterior AC units) UNLESS the article is specifically about solar/utilities/infrastructure
- Clutter (trash, debris, tools, packaging, construction materials)
- Duplicate fixtures (two faucets, two ovens, etc.)

FIX (correct obvious defects only):
- Broken or irregular rooflines
- Crooked, floating, or impossible furniture
- Dirty, cracked, or damaged walls/surfaces
- Visible stains or wear marks
- Missing or misaligned fixtures
- Oversaturated or color-clipped areas

MINIMIZE:
- Harsh glare or heavy shadows obscuring architecture
- Blurry or defocused foreground elements

ARTICLE CONTEXT CONSIDERATION:
Read the article title and content above. If the article discusses solar panels, utility systems, infrastructure, or related topics, DO NOT flag these elements for removal as they are relevant to the content.

BRAND TIER consideration: {brandProfile} requires clean, pristine presentation. Remove only obvious flaws and defects, not stylistic elements.

OUTPUT FORMAT:
List only actual problems found. If category has no issues, skip it entirely.

Remove: [element + location]
Fix: [issue + location]
Minimize: [issue + area]

If no issues exist at all, output: "No corrections needed" """}),
                "model": (["GPT-4.1 ($2.00/$8.00 per 1M tokens)",
                          "GPT-4.1 mini ($0.40/$1.60 per 1M tokens)",
                          "GPT-4.1 nano ($0.10/$0.40 per 1M tokens)"],),
                "api_key": ("STRING", {"default": "", "multiline": False})
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("qc_analysis",)
    FUNCTION = "analyze_image_qc"
    CATEGORY = "spiralmountain/vision"

    def analyze_image_qc(self, image, postTitle, postContent, brandProfile, prompt, model, api_key=""):
        """Process the image with OpenAI's Vision API for QC with article context"""
        # Get API key from environment if not provided
        if not api_key:
            api_key = os.environ.get('OPENAI_API_KEY')
            if not api_key:
                return ("No OpenAI API key provided. Please enter your API key or set the OPENAI_API_KEY environment variable.",)

        # Replace placeholders in prompt with actual values
        formatted_prompt = prompt.replace("{postTitle}", postTitle)
        formatted_prompt = formatted_prompt.replace("{postContent}", postContent[:1000])  # Limit content length
        formatted_prompt = formatted_prompt.replace("{brandProfile}", brandProfile)

        # Map selected model to actual model identifier
        model_mapping = {
            "GPT-4.1 ($2.00/$8.00 per 1M tokens)": "gpt-4.1",
            "GPT-4.1 mini ($0.40/$1.60 per 1M tokens)": "gpt-4.1-mini",
            "GPT-4.1 nano ($0.10/$0.40 per 1M tokens)": "gpt-4.1-nano"
        }

        model_id = model_mapping[model]

        try:
            # ComfyUI images are in BCHW format with float values [0,1]
            # Extract the first image if we have a batch
            if len(image.shape) == 4:
                image_tensor = image[0]  # Get the first image from the batch
            else:
                image_tensor = image

            # Convert from BCHW/CHW to HWC format for PIL
            if image_tensor.shape[0] in [1, 3, 4]:  # If first dimension is channels
                image_tensor = image_tensor.permute(1, 2, 0)

            # Convert to numpy and scale to 0-255 range
            np_image = image_tensor.cpu().numpy()
            if np_image.max() <= 1.0:
                np_image = (np_image * 255).astype(np.uint8)

            # Handle different channel configurations
            if np_image.shape[2] == 1:  # Grayscale
                np_image = np.repeat(np_image, 3, axis=2)
            elif np_image.shape[2] == 4:  # RGBA
                np_image = np_image[:, :, :3]  # Remove alpha channel

            # Create PIL image from numpy array
            pil_image = Image.fromarray(np_image)

            # Encode the PIL image to base64
            image_bytes = io.BytesIO()
            pil_image.save(image_bytes, format='PNG')
            image_bytes.seek(0)
            base64_image = base64.b64encode(image_bytes.getvalue()).decode('utf-8')

            # Create OpenAI client
            client = OpenAI(api_key=api_key)

            # Create completion with the Vision API
            response = client.responses.create(
                model=model_id,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": formatted_prompt,
                            },
                            {
                                "type": "input_image",
                                "image_url": f"data:image/png;base64,{base64_image}",
                            },
                        ],
                    }
                ]
            )

            analysis = response.output_text.strip()
            return (analysis,)

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            return (f"Error processing image: {str(e)}\n\nDetails: {error_details}",)


# Node registration
NODE_CLASS_MAPPINGS = {
    "spiralmountain_openaivisionqc": OpenAIVisionQC
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "spiralmountain_openaivisionqc": "🔮 SpiralMountain OpenAI Vision QC"
}
