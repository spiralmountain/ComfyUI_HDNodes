# ComfyUI-Seedance-Nodes

Custom nodes for [ComfyUI](https://github.com/comfyanonymous/ComfyUI) that enable video generation using ByteDance's Seedance model via [Fal.ai](https://fal.ai/).

## Features

### 🎬 Seedance Image to Video (Fal.ai)
Generate high-quality videos from images using ByteDance's Seedance model.

**Capabilities:**
- Image-to-video generation
- Pro (1080p) and Lite (720p) models
- Multiple aspect ratios (auto, 21:9, 16:9, 4:3, 1:1, 3:4, 9:16)
- Configurable duration (3-12 seconds)
- Camera control (fixed or dynamic)
- Seed-based reproducibility

### 📥 Download Video from URL
Automatically download generated videos to your ComfyUI output folder.

**Features:**
- Downloads video from URL
- Saves with timestamp
- Custom filename prefix
- Returns local file path

## Installation

1. Clone this repository into your ComfyUI custom_nodes folder:
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/YOUR_USERNAME/ComfyUI-Seedance-Nodes.git
```

2. Install dependencies:
```bash
cd ComfyUI-Seedance-Nodes
pip install -r requirements.txt
```

3. Restart ComfyUI

## Requirements

- Python 3.8+
- ComfyUI
- fal-client
- Fal.ai API key

## Getting Your Fal.ai API Key

1. Sign up at [Fal.ai](https://fal.ai/)
2. Go to [API Keys Dashboard](https://fal.ai/dashboard/keys)
3. Click Create Key
4. Copy your API key

## Usage

### Basic Workflow

1. **Load Image** → Connect to **Seedance Image to Video**
2. Add your Fal.ai API key to the node
3. Configure parameters (prompt, resolution, duration, etc.)
4. Connect **video_url output** → **Download Video from URL**
5. Run the workflow
6. Video saves to `ComfyUI/output/seedance_video_[timestamp].mp4`

### Example Workflow

```
Load Image 
    ↓
Seedance Image to Video (Fal.ai)
    - api_key: YOUR_FAL_API_KEY
    - prompt: high-end real-estate promo video, smooth camera motion
    - model_version: pro
    - resolution: 1080p
    - duration: 5
    ↓ (video_url)
Download Video from URL
    - filename_prefix: my_video
    ↓
Video saved: ComfyUI/output/my_video_20251022_120000.mp4
```

## Pricing

### Fal.ai Costs (approximate)
- **Pro (1080p)**: ~$0.62 per 5-second video
- **Lite (720p)**: Lower cost alternative
- Free tier available for testing

## Node Parameters

### Seedance Image to Video

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| image | IMAGE | - | Input image |
| prompt | STRING | - | Text description for motion |
| fal_api_key | STRING | - | Your Fal.ai API key |
| model_version | CHOICE | pro | pro (1080p) or lite (720p) |
| resolution | CHOICE | 1080p | 1080p, 720p, or 480p |
| aspect_ratio | CHOICE | auto | Video aspect ratio |
| duration | INT | 5 | Video duration (3-12 seconds) |
| seed | INT | -1 | Random seed (-1 for random) |
| camera_fixed | BOOLEAN | False | Lock camera position |

**Output:** `video_url` (STRING) - URL to generated video

### Download Video from URL

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| video_url | STRING | - | URL of video to download |
| filename_prefix | STRING | seedance_video | Prefix for saved file |

**Output:** `saved_path` (STRING) - Local path to saved video

## Troubleshooting

### API key is required error
- Make sure you've entered your Fal.ai API key in the node
- Get a key at https://fal.ai/dashboard/keys

### fal_client not installed error
- Run: `pip install fal-client`

### Video download fails
- Check your internet connection
- Verify the video URL is valid
- Ensure you have write permissions in the output folder

## Tips for Best Results

1. **Prompts**: Be specific about desired motion and camera movement
2. **Camera Fixed**: Enable for locked camera position (good for product shots)
3. **Duration**: Start with 5 seconds and adjust as needed
4. **Resolution**: Use Pro (1080p) for final outputs, Lite for testing

## Example Prompts

- high-end real-estate agency promo video, subtle camera motion, variations in lighting
- smooth dolly shot moving forward, cinematic, professional
- gentle pan from left to right, revealing the scene
- lock camera but add life and subtle motion to the image

## License

MIT License - See LICENSE file for details

## Credits

- Built for [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
- Uses [Fal.ai](https://fal.ai/) API
- ByteDance Seedance model

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

## Version

Current version: 1.0.0

## Changelog

### v1.0.0 (2025-10-22)
- Initial release
- Seedance Image to Video node
- Download Video from URL node
- Support for Pro and Lite models
- Configurable parameters
