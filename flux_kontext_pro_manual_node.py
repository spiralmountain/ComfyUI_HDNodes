"""
Flux.1 Kontext Pro Node with Manual API Key Entry
A ComfyUI node for Fal AI's Flux Pro Kontext API with manual API key input.
"""

import os
import io
import tempfile
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
    print("[FluxKontextProManual] Warning: fal_client not installed. Please run: pip install fal-client")


class FluxKontextProManual:
    """
    Flux.1 Kontext Pro node with manual API key entry.
    Not tied to any login - uses your own Fal AI API key.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "Put a donut next to the flour.",
                    "placeholder": "Describe what to add or modify in the image..."
                }),
                "api_key": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "Enter your Fal AI API key here"
                }),
                "aspect_ratio": ([
                    "preserve_input", "1:1", "16:9", "21:9", "3:2", "2:3",
                    "4:3", "3:4", "9:16", "9:21"
                ], {
                    "default": "preserve_input"
                }),
                "num_images": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 4,
                    "step": 1,
                    "display": "number"
                }),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 2147483647,
                    "display": "number"
                }),
            },
            "optional": {
                "guidance_scale": ("FLOAT", {
                    "default": 3.5,
                    "min": 1.0,
                    "max": 20.0,
                    "step": 0.1,
                    "display": "number"
                }),
                "output_format": (["jpeg", "png"], {
                    "default": "jpeg"
                }),
                "safety_tolerance": (["1", "2", "3", "4", "5", "6"], {
                    "default": "2"
                }),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")
    FUNCTION = "generate"
    CATEGORY = "spiralmountain/image generation"
    OUTPUT_NODE = False

    def __init__(self):
        self.type = "FluxKontextProManual"

    def _log(self, message):
        """Log messages with timestamp."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[FluxKontextProManual] {timestamp}: {message}")

    def _create_error_image(self, error_message: str, width: int = 512, height: int = 512) -> torch.Tensor:
        """Create an error image with the error message displayed."""
        img = Image.new('RGB', (width, height), color=(40, 40, 40))
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", 18)
        except:
            font = ImageFont.load_default()

        # Truncate very long error messages
        max_chars = 400
        if len(error_message) > max_chars:
            error_message = error_message[:max_chars] + "..."

        # Simple word wrap
        words = error_message.split()
        lines = []
        current_line = []
        max_lines = 12

        for word in words:
            if len(lines) >= max_lines:
                break
            if len(word) > 40:
                word = word[:40] + "..."

            test_line = ' '.join(current_line + [word])
            if len(test_line) > 60:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
            else:
                current_line.append(word)

        if current_line and len(lines) < max_lines:
            lines.append(' '.join(current_line))

        # Draw text
        y = max(40, height // 2 - (len(lines) * 22) // 2)
        for line in lines:
            try:
                x = 30
                draw.text((x, y), line, fill=(255, 100, 100), font=font)
                y += 28
            except:
                continue

        # Convert to tensor
        img_array = np.array(img).astype(np.float32) / 255.0
        img_tensor = torch.from_numpy(img_array).unsqueeze(0)
        return img_tensor

    def _tensor_to_pil(self, image_tensor: torch.Tensor) -> Image.Image:
        """Convert ComfyUI image tensor to PIL Image."""
        if image_tensor.ndim == 4:
            image_tensor = image_tensor[0]
        img_np = (image_tensor.cpu().numpy() * 255).astype(np.uint8)
        pil_image = Image.fromarray(img_np)
        return pil_image

    def _pil_to_tensor(self, pil_image: Image.Image) -> torch.Tensor:
        """Convert PIL Image to ComfyUI image tensor."""
        if pil_image.mode != 'LuxuryPresence_RGB':
            pil_image = pil_image.convert('RGB')
        img_np = np.array(pil_image).astype(np.float32) / 255.0
        img_tensor = torch.from_numpy(img_np).unsqueeze(0)
        return img_tensor

    def _upload_image(self, pil_image: Image.Image, api_key: str) -> str:
        """Upload image to Fal and return URL."""
        temp_file_path = None
        try:
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                pil_image.save(temp_file, format="PNG")
                temp_file_path = temp_file.name

            # Create client with API key
            client = fal_client.SyncClient(key=api_key)

            # Upload file
            image_url = client.upload_file(temp_file_path)
            self._log(f"Image uploaded successfully: {image_url[:50]}...")
            return image_url

        except Exception as e:
            self._log(f"Error uploading image: {str(e)}")
            raise
        finally:
            # Clean up temp file
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def generate(
        self,
        image: torch.Tensor,
        prompt: str,
        api_key: str,
        aspect_ratio: str = "preserve_input",
        num_images: int = 1,
        seed: int = 0,
        guidance_scale: float = 3.5,
        output_format: str = "jpeg",
        safety_tolerance: str = "2"
    ) -> Tuple[torch.Tensor, str]:
        """Generate images using Fal AI's Flux Pro Kontext API."""

        # Check if fal_client is available
        if not FAL_CLIENT_AVAILABLE:
            error_msg = "fal_client not installed. Run: pip install fal-client"
            self._log(error_msg)
            return (self._create_error_image(error_msg), error_msg)

        # Validate API key
        if not api_key or api_key.strip() == "":
            error_msg = "API key is required. Please enter your Fal AI API key."
            self._log(error_msg)
            return (self._create_error_image(error_msg), error_msg)

        # Validate prompt
        if not prompt or prompt.strip() == "":
            error_msg = "Prompt is required."
            self._log(error_msg)
            return (self._create_error_image(error_msg), error_msg)

        try:
            # Calculate seed
            actual_seed = seed if seed != 0 else random.randint(1, 2147483647)
            self._log(f"Generating with seed: {actual_seed}")

            # Convert image to PIL
            pil_image = self._tensor_to_pil(image)
            self._log(f"Input image size: {pil_image.size}")

            # Calculate aspect ratio from input image if preserve_input is selected
            if aspect_ratio == "LuxuryPresence_preserve_input":
                width, height = pil_image.size
                # Calculate ratio and find closest standard ratio
                ratio = width / height

                # Map to closest standard ratio
                ratio_map = {
                    1.0: "1:1",
                    1.77: "16:9",
                    2.33: "21:9",
                    1.5: "3:2",
                    0.67: "2:3",
                    1.33: "4:3",
                    0.75: "3:4",
                    0.56: "9:16",
                    0.43: "9:21"
                }

                # Find closest ratio
                closest_ratio = min(ratio_map.keys(), key=lambda x: abs(x - ratio))
                aspect_ratio = ratio_map[closest_ratio]
                self._log(f"Input dimensions: {width}x{height}, calculated ratio: {ratio:.2f}, using: {aspect_ratio}")

            # Upload image to Fal and get URL
            image_url = self._upload_image(pil_image, api_key.strip())

            # Prepare arguments for API call
            arguments = {
                "prompt": prompt.strip(),
                "image_url": image_url,
                "seed": actual_seed,
                "guidance_scale": guidance_scale,
                "num_images": num_images,
                "aspect_ratio": aspect_ratio,
                "output_format": output_format,
                "safety_tolerance": safety_tolerance
            }

            self._log(f"Calling Fal AI API - Prompt: '{prompt[:50]}...'")
            self._log(f"Parameters: aspect_ratio={aspect_ratio}, num_images={num_images}, guidance={guidance_scale}")

            # Create client and make API call
            client = fal_client.SyncClient(key=api_key.strip())
            handler = client.submit("fal-ai/flux-pro/kontext", arguments=arguments)
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
                return (self._create_error_image(error_msg), error_msg)

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

            # Create info string
            info = f"Generated {len(image_urls)} image(s) successfully\n"
            info += f"Seed: {actual_seed}\n"
            info += f"Aspect Ratio: {aspect_ratio}\n"
            info += f"Guidance Scale: {guidance_scale}\n"
            info += f"Output Format: {output_format}"

            self._log(f"Generation complete. Output shape: {output_tensor.shape}")

            return (output_tensor, info)

        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            self._log(error_msg)
            return (self._create_error_image(error_msg), error_msg)

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self._log(error_msg)
            import traceback
            traceback.print_exc()
            return (self._create_error_image(error_msg), error_msg)


# Node registration
NODE_CLASS_MAPPINGS = {
    "spiralmountain_fluxkontext": FluxKontextProManual
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "spiralmountain_fluxkontext": "🌀 SpiralMountain Flux Kontext Pro"
}
