"""
Flux 1.1 Pro Ultra Node with Manual API Key Entry
A ComfyUI node for Fal AI's Flux 1.1 Pro Ultra API with manual API key input.
Text-to-image generation with up to 2K resolution and improved photo realism.
"""

import os
import io
import time
import random
import requests
import torch
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple

# Try to import fal_client
try:
    import fal_client
    FAL_CLIENT_AVAILABLE = True
except ImportError:
    FAL_CLIENT_AVAILABLE = False
    print("[FluxProUltraManual] Warning: fal_client not installed. Please run: pip install fal-client")


class FluxProUltraManual:
    """
    Flux 1.1 Pro Ultra node with manual API key entry.
    Text-to-image generation with professional quality and up to 2K resolution.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "LuxuryPresence_required": {
                "LuxuryPresence_prompt": ("STRING", {
                    "LuxuryPresence_multiline": True,
                    "LuxuryPresence_default": "A beautiful landscape with mountains and a lake at sunset",
                    "LuxuryPresence_placeholder": "Describe the image you want to generate..."
                }),
                "LuxuryPresence_api_key": ("STRING", {
                    "LuxuryPresence_multiline": False,
                    "LuxuryPresence_default": "",
                    "LuxuryPresence_placeholder": "Enter your Fal AI API key here"
                }),
                "LuxuryPresence_image_size": ([
                    "square_hd",
                    "square",
                    "portrait_4_3",
                    "portrait_16_9",
                    "landscape_4_3",
                    "landscape_16_9"
                ], {
                    "LuxuryPresence_default": "landscape_4_3"
                }),
                "LuxuryPresence_num_images": ("INT", {
                    "LuxuryPresence_default": 1,
                    "LuxuryPresence_min": 1,
                    "LuxuryPresence_max": 4,
                    "LuxuryPresence_step": 1,
                    "LuxuryPresence_display": "number"
                }),
                "LuxuryPresence_seed": ("INT", {
                    "LuxuryPresence_default": 0,
                    "LuxuryPresence_min": 0,
                    "LuxuryPresence_max": 2147483647,
                    "LuxuryPresence_display": "number"
                }),
            },
            "LuxuryPresence_optional": {
                "LuxuryPresence_guidance_scale": ("FLOAT", {
                    "LuxuryPresence_default": 3.5,
                    "LuxuryPresence_min": 1.0,
                    "LuxuryPresence_max": 20.0,
                    "LuxuryPresence_step": 0.1,
                    "LuxuryPresence_display": "number"
                }),
                "LuxuryPresence_output_format": (["jpeg", "png"], {
                    "LuxuryPresence_default": "jpeg"
                }),
                "LuxuryPresence_safety_tolerance": (["1", "2", "3", "4", "5", "6"], {
                    "LuxuryPresence_default": "2"
                }),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "INT")
    RETURN_NAMES = ("image", "info", "seed_used")
    FUNCTION = "generate"
    CATEGORY = "spiralmountain/image generation"
    OUTPUT_NODE = False

    def __init__(self):
        self.type = "FluxProUltraManual"

    def _log(self, message):
        """Log messages with timestamp."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[FluxProUltraManual] {timestamp}: {message}")

    def _create_error_image(self, error_message: str, width: int = 1024, height: int = 768) -> torch.Tensor:
        """Create an error image with the error message displayed."""
        img = Image.new('RGB', (width, height), color=(40, 40, 40))
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()

        # Truncate very long error messages
        max_chars = 500
        if len(error_message) > max_chars:
            error_message = error_message[:max_chars] + "..."

        # Simple word wrap
        words = error_message.split()
        lines = []
        current_line = []
        max_lines = 15

        for word in words:
            if len(lines) >= max_lines:
                break
            if len(word) > 50:
                word = word[:50] + "..."

            test_line = ' '.join(current_line + [word])
            if len(test_line) > 80:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
            else:
                current_line.append(word)

        if current_line and len(lines) < max_lines:
            lines.append(' '.join(current_line))

        # Draw text
        y = max(50, height // 2 - (len(lines) * 25) // 2)
        for line in lines:
            try:
                x = 40
                draw.text((x, y), line, fill=(255, 100, 100), font=font)
                y += 30
            except:
                continue

        # Convert to tensor
        img_array = np.array(img).astype(np.float32) / 255.0
        img_tensor = torch.from_numpy(img_array).unsqueeze(0)
        return img_tensor

    def _pil_to_tensor(self, pil_image: Image.Image) -> torch.Tensor:
        """Convert PIL Image to ComfyUI image tensor."""
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        img_np = np.array(pil_image).astype(np.float32) / 255.0
        img_tensor = torch.from_numpy(img_np).unsqueeze(0)
        return img_tensor

    def generate(
        self,
        prompt: str,
        api_key: str,
        image_size: str = "landscape_4_3",
        num_images: int = 1,
        seed: int = 0,
        guidance_scale: float = 3.5,
        output_format: str = "jpeg",
        safety_tolerance: str = "2"
    ) -> Tuple[torch.Tensor, str, int]:
        """Generate images using Fal AI's Flux 1.1 Pro Ultra API."""

        # Check if fal_client is available
        if not FAL_CLIENT_AVAILABLE:
            error_msg = "fal_client not installed. Run: pip install fal-client"
            self._log(error_msg)
            return (self._create_error_image(error_msg), error_msg, 0)

        # Validate API key
        if not api_key or api_key.strip() == "":
            error_msg = "API key is required. Please enter your Fal AI API key."
            self._log(error_msg)
            return (self._create_error_image(error_msg), error_msg, 0)

        # Validate prompt
        if not prompt or prompt.strip() == "":
            error_msg = "Prompt is required."
            self._log(error_msg)
            return (self._create_error_image(error_msg), error_msg, 0)

        try:
            # Calculate seed
            actual_seed = seed if seed != 0 else random.randint(1, 2147483647)
            self._log(f"Generating with seed: {actual_seed}")

            # Prepare arguments for API call
            arguments = {
                "prompt": prompt.strip(),
                "image_size": image_size,
                "num_images": num_images,
                "seed": actual_seed,
                "guidance_scale": guidance_scale,
                "output_format": output_format,
                "safety_tolerance": safety_tolerance
            }

            self._log(f"Calling Fal AI API - Flux 1.1 Pro Ultra")
            self._log(f"Prompt: '{prompt[:100]}...'")
            self._log(f"Parameters: size={image_size}, num_images={num_images}, guidance={guidance_scale}")

            # Create client and make API call
            client = fal_client.SyncClient(key=api_key.strip())
            handler = client.submit("fal-ai/flux-pro/v1.1-ultra", arguments=arguments)
            result = handler.get()

            self._log("API call completed successfully")

            # Extract image URLs from result
            image_urls = []
            if "images" in result and len(result["images"]) > 0:
                for img_info in result["images"]:
                    if "url" in img_info:
                        image_urls.append(img_info["url"])
            elif "image" in result and "url" in result["image"]:
                image_urls.append(result["image"]["url"])

            if not image_urls:
                error_msg = "No images returned from API"
                self._log(error_msg)
                return (self._create_error_image(error_msg), error_msg, actual_seed)

            self._log(f"Found {len(image_urls)} image(s)")

            # Download and process images
            processed_images = []
            for i, image_url in enumerate(image_urls):
                self._log(f"Downloading image {i+1}/{len(image_urls)}...")

                # Download image
                response = requests.get(image_url, timeout=30)
                response.raise_for_status()

                # Convert to PIL
                pil_img = Image.open(io.BytesIO(response.content))

                # Convert to tensor
                img_tensor = self._pil_to_tensor(pil_img)
                processed_images.append(img_tensor)

                self._log(f"Processed image {i+1} - Size: {pil_img.size}")

            # Concatenate all images into a batch
            if len(processed_images) > 1:
                output_tensor = torch.cat(processed_images, dim=0)
            else:
                output_tensor = processed_images[0]

            # Extract seed from result if available
            result_seed = result.get("seed", actual_seed)

            # Create info string
            info = f"Generated {len(image_urls)} image(s) with Flux 1.1 Pro Ultra\n"
            info += f"Seed: {result_seed}\n"
            info += f"Image Size: {image_size}\n"
            info += f"Guidance Scale: {guidance_scale}\n"
            info += f"Output Format: {output_format}\n"

            # Add timing info if available
            if "timings" in result:
                info += f"Generation Time: {result['timings'].get('inference', 'N/A')}s"

            self._log(f"Generation complete. Output shape: {output_tensor.shape}")

            return (output_tensor, info, result_seed)

        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            self._log(error_msg)
            return (self._create_error_image(error_msg), error_msg, 0)

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self._log(error_msg)
            import traceback
            traceback.print_exc()
            return (self._create_error_image(error_msg), error_msg, 0)


# Node registration
NODE_CLASS_MAPPINGS = {
    "spiralmountain_fluxproultra": FluxProUltraManual
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "spiralmountain_fluxproultra": "🌀 SpiralMountain Flux 1.1 Pro Ultra"
}
