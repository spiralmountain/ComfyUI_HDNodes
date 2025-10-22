import os
import folder_paths
import shutil

class PreviewVideo:
    """
    Preview video in ComfyUI interface
    Shows video in the output panel
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_path": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
            },
        }
    
    RETURN_TYPES = ()
    OUTPUT_NODE = True
    FUNCTION = "preview_video"
    CATEGORY = "hdelmont/video"
    
    def preview_video(self, video_path):
        
        if not video_path or not os.path.exists(video_path):
            raise ValueError(f"Video file not found: {video_path}")
        
        # Get the filename
        filename = os.path.basename(video_path)
        
        # ComfyUI looks for videos in the output folder
        # If it's already there, we just need to return it
        # If not, copy it there
        output_dir = folder_paths.get_output_directory()
        
        if not video_path.startswith(output_dir):
            # Copy to output folder if not already there
            dest_path = os.path.join(output_dir, filename)
            if video_path != dest_path:
                shutil.copy2(video_path, dest_path)
                video_path = dest_path
                filename = os.path.basename(dest_path)
        
        # Return video for preview in UI
        return {
            "ui": {
                "videos": [{
                    "filename": filename,
                    "subfolder": "",
                    "type": "output",
                    "format": "video/mp4"
                }]
            }
        }

NODE_CLASS_MAPPINGS = {
    "PreviewVideo": PreviewVideo
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PreviewVideo": "Preview Video"
}
