import os
import subprocess
import folder_paths
from datetime import datetime
import tempfile
import shutil

class StitchVideos:
    """
    A ComfyUI pass-through node that stitches multiple videos together using ffmpeg.
    If only one video is provided, it passes through without stitching.
    Accepts multiple video paths and concatenates them into a single video.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_path_1": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "Path or URL to first video"
                }),
                "filename_prefix": ("STRING", {
                    "default": "video",
                    "multiline": False
                }),
            },
            "optional": {
                "video_path_2": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "Path or URL to second video (optional)"
                }),
                "video_path_3": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "Path or URL to third video (optional)"
                }),
                "video_path_4": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "Path or URL to fourth video (optional)"
                }),
                "video_path_5": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "Path or URL to fifth video (optional)"
                }),
                "audio_path": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "Optional audio file path to add to final video"
                }),
                "audio_volume": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1,
                    "display": "number"
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("video_path",)
    OUTPUT_NODE = True
    FUNCTION = "stitch_videos"
    CATEGORY = "hdelmont/video"

    def download_video_if_url(self, video_path, temp_dir):
        """Download video if it's a URL, otherwise return the path as is"""
        if video_path.startswith(('http://', 'https://')):
            import requests
            print(f"Downloading video from URL: {video_path}")

            response = requests.get(video_path, stream=True, timeout=300)
            response.raise_for_status()

            # Create temp file
            temp_file = os.path.join(temp_dir, f"video_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.mp4")

            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Downloaded to: {temp_file}")
            return temp_file
        else:
            # It's a local path
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
            return video_path

    def copy_video_to_output(self, video_path, filename_prefix, audio_path="", audio_volume=1.0):
        """Copy a single video to output directory with new name, optionally adding audio"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{filename_prefix}_{timestamp}.mp4"
        output_dir = folder_paths.get_output_directory()
        output_path = os.path.join(output_dir, output_filename)

        # If it's a URL, download it
        if video_path.startswith(('http://', 'https://')):
            temp_dir = tempfile.mkdtemp()
            try:
                local_path = self.download_video_if_url(video_path, temp_dir)

                # If audio provided, combine them
                if audio_path and audio_path.strip():
                    self.add_audio_to_video(local_path, audio_path, output_path, audio_volume)
                else:
                    shutil.copy2(local_path, output_path)
            finally:
                shutil.rmtree(temp_dir)
        else:
            # If audio provided, combine them
            if audio_path and audio_path.strip():
                self.add_audio_to_video(video_path, audio_path, output_path, audio_volume)
            else:
                # Copy local file
                shutil.copy2(video_path, output_path)

        return output_path, output_filename

    def add_audio_to_video(self, video_path, audio_path, output_path, audio_volume):
        """Add audio to video using ffmpeg"""
        print(f"Adding audio to video: {audio_path} (volume: {audio_volume})")

        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-filter:a", f"volume={audio_volume}",
            "-shortest",  # End when shortest input ends
            output_path
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode != 0:
            error_msg = f"FFmpeg error adding audio: {result.stderr}"
            print(error_msg)
            raise RuntimeError(error_msg)

    def stitch_videos(self, video_path_1, filename_prefix,
                     video_path_2="", video_path_3="", video_path_4="", video_path_5="",
                     audio_path="", audio_volume=1.0):
        """
        Stitch multiple videos together using ffmpeg, or pass through if only one video.
        Optionally adds audio to the final video.
        """

        # Collect all non-empty video paths
        video_paths = [video_path_1] if video_path_1 and video_path_1.strip() else []
        for optional_path in [video_path_2, video_path_3, video_path_4, video_path_5]:
            if optional_path and optional_path.strip():
                video_paths.append(optional_path.strip())

        if len(video_paths) == 0:
            raise ValueError("At least one video path must be provided")

        # PASS-THROUGH: If only one video, just return it
        if len(video_paths) == 1:
            print(f"Pass-through mode: Only one video provided, copying to output...")
            output_path, output_filename = self.copy_video_to_output(video_paths[0], filename_prefix, audio_path, audio_volume)

            print(f"Passed through video: {output_path}")

            return {
                "ui": {
                    "videos": [{
                        "filename": output_filename,
                        "subfolder": "",
                        "type": "output",
                        "format": "video/mp4"
                    }]
                },
                "result": (output_path,)
            }

        # STITCHING: Multiple videos provided
        print(f"Stitching {len(video_paths)} videos together...")

        # Create temp directory for downloads
        temp_dir = tempfile.mkdtemp()

        try:
            # Download videos if they are URLs
            local_paths = []
            for i, video_path in enumerate(video_paths):
                print(f"Processing video {i+1}/{len(video_paths)}: {video_path}")
                local_path = self.download_video_if_url(video_path, temp_dir)
                local_paths.append(local_path)

            # Prepare output path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{filename_prefix}_{timestamp}.mp4"
            output_dir = folder_paths.get_output_directory()
            output_path = os.path.join(output_dir, output_filename)

            # Create concat file list for ffmpeg
            concat_file = os.path.join(temp_dir, 'concat_list.txt')
            with open(concat_file, 'w') as f:
                for local_path in local_paths:
                    # Escape single quotes in path for ffmpeg
                    escaped_path = local_path.replace("'", "'\\''")
                    f.write(f"file '{escaped_path}'\n")

            print(f"Created concat file: {concat_file}")

            # Simple concatenation
            print("Using simple concatenation...")

            # If audio is provided, we need a temp file for stitched video without audio first
            if audio_path and audio_path.strip():
                temp_video = os.path.join(temp_dir, 'stitched_temp.mp4')
                stitch_output = temp_video
            else:
                stitch_output = output_path

            cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_file,
                "-c", "copy",  # Copy codec for faster processing
                stitch_output
            ]

            print(f"Running ffmpeg command...")
            print(f"Output: {stitch_output}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )

            if result.returncode != 0:
                error_msg = f"FFmpeg error: {result.stderr}"
                print(error_msg)
                raise RuntimeError(error_msg)

            print(f"Successfully stitched videos: {stitch_output}")

            # Add audio if provided
            if audio_path and audio_path.strip():
                print(f"Adding audio to stitched video...")
                self.add_audio_to_video(stitch_output, audio_path, output_path, audio_volume)
                print(f"Audio added successfully: {output_path}")

            # Return UI format for queue display + video_path output
            return {
                "ui": {
                    "videos": [{
                        "filename": output_filename,
                        "subfolder": "",
                        "type": "output",
                        "format": "video/mp4"
                    }]
                },
                "result": (output_path,)
            }

        finally:
            # Clean up temp directory
            try:
                shutil.rmtree(temp_dir)
                print(f"Cleaned up temp directory: {temp_dir}")
            except Exception as e:
                print(f"Warning: Could not clean up temp directory: {e}")

# Node registration
NODE_CLASS_MAPPINGS = {
    "StitchVideos": StitchVideos
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "StitchVideos": "Stitch Videos"
}
