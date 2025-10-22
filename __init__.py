"""
ComfyUI-Seedance-Nodes
Custom nodes for Seedance video generation via Fal.ai
"""

from .seedance_image_to_video_node import NODE_CLASS_MAPPINGS as Seedance_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as Seedance_DISPLAY
from .download_video_node import NODE_CLASS_MAPPINGS as Download_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as Download_DISPLAY
from .combine_video_audio_node import NODE_CLASS_MAPPINGS as Combine_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as Combine_DISPLAY

NODE_CLASS_MAPPINGS = {}
NODE_CLASS_MAPPINGS.update(Seedance_MAPPINGS)
NODE_CLASS_MAPPINGS.update(Download_MAPPINGS)
NODE_CLASS_MAPPINGS.update(Combine_MAPPINGS)

NODE_DISPLAY_NAME_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS.update(Seedance_DISPLAY)
NODE_DISPLAY_NAME_MAPPINGS.update(Download_DISPLAY)
NODE_DISPLAY_NAME_MAPPINGS.update(Combine_DISPLAY)

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
__version__ = '1.1.0'
__author__ = 'hdelmont'
