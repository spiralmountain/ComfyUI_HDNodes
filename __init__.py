"""
ComfyUI-Seedance-Nodes
Custom nodes for Seedance video generation and audio via Fal.ai
"""

from .seedance_image_to_video_node import NODE_CLASS_MAPPINGS as Seedance_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as Seedance_DISPLAY
from .download_video_node import NODE_CLASS_MAPPINGS as Download_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as Download_DISPLAY
from .combine_video_audio_node import NODE_CLASS_MAPPINGS as Combine_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as Combine_DISPLAY
from .fal_audio_generation_node import NODE_CLASS_MAPPINGS as FalAudio_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as FalAudio_DISPLAY
from .preview_video_node import NODE_CLASS_MAPPINGS as PreviewVideo_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as PreviewVideo_DISPLAY
from .ollama_image_to_music_prompt_node import NODE_CLASS_MAPPINGS as OllamaImageToMusicPrompt_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as OllamaImageToMusicPrompt_DISPLAY
from .stitch_videos_node import NODE_CLASS_MAPPINGS as StitchVideos_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as StitchVideos_DISPLAY

NODE_CLASS_MAPPINGS = {}
NODE_CLASS_MAPPINGS.update(Seedance_MAPPINGS)
NODE_CLASS_MAPPINGS.update(Download_MAPPINGS)
NODE_CLASS_MAPPINGS.update(Combine_MAPPINGS)
NODE_CLASS_MAPPINGS.update(FalAudio_MAPPINGS)
NODE_CLASS_MAPPINGS.update(PreviewVideo_MAPPINGS)
NODE_CLASS_MAPPINGS.update(OllamaImageToMusicPrompt_MAPPINGS)
NODE_CLASS_MAPPINGS.update(StitchVideos_MAPPINGS)

NODE_DISPLAY_NAME_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS.update(Seedance_DISPLAY)
NODE_DISPLAY_NAME_MAPPINGS.update(Download_DISPLAY)
NODE_DISPLAY_NAME_MAPPINGS.update(Combine_DISPLAY)
NODE_DISPLAY_NAME_MAPPINGS.update(FalAudio_DISPLAY)
NODE_DISPLAY_NAME_MAPPINGS.update(PreviewVideo_DISPLAY)
NODE_DISPLAY_NAME_MAPPINGS.update(OllamaImageToMusicPrompt_DISPLAY)
NODE_DISPLAY_NAME_MAPPINGS.update(StitchVideos_DISPLAY)

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
__version__ = "1.4.0"
__author__ = "hdelmont"
