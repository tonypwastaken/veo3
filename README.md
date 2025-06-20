# AI Video Generator using Google's Veo Models

This Python script allows you to generate AI videos using Google's Veo models via the Vertex AI platform. It supports both text-to-video and image-to-video generation.

## Features

- **Text-to-Video**: Generate videos from descriptive text prompts
- **Image-to-Video**: Generate videos from an input image and text description
- **Interactive CLI**: Easy-to-use command-line interface
- **Local MP4 Files**: Automatically downloads and saves videos as MP4 files in current directory
- **Smart Filenames**: Generates descriptive filenames with timestamps
- **Configurable Parameters**: Control video duration, aspect ratio, and more
- **Google Cloud Integration**: Uses Google's powerful Veo 3 model

## Prerequisites

1. **Python 3.8+** installed on your system
2. **Google Cloud Project** with Vertex AI API enabled
3. **Google Cloud CLI** installed and authenticated
4. **Access to Veo models** (may require allowlist approval)

## Setup

### 1. Clone or Download this Repository

```bash
git clone <repository-url>
cd generate-veo3-videos-py
```

### 2. Run the Setup Script

```bash
python setup.py
```

This will:

- Install required Python dependencies
- Check your Google Cloud authentication
- Provide environment setup instructions

### 3. Set Environment Variables

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1
export GOOGLE_GENAI_USE_VERTEXAI=True
export GCS_BUCKET=your-bucket-name  # Optional: for storing output videos
```

### 4. Choose Your Authentication Method

#### Option A: Service Account Key (Recommended for Automation)

1. **Create a service account:**

```bash
# Create service account
gcloud iam service-accounts create veo-video-generator \
    --display-name="Veo Video Generator"

# Grant necessary permissions
gcloud projects add-iam-policy-binding your-project-id \
    --member="serviceAccount:veo-video-generator@your-project-id.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

# Create and download key file
gcloud iam service-accounts keys create ./veo-service-account.json \
    --iam-account=veo-video-generator@your-project-id.iam.gserviceaccount.com
```

2. **Set environment variable:**

```bash
export GOOGLE_APPLICATION_CREDENTIALS="./veo-service-account.json"
```

#### Option B: API Key (Limited Support)

1. **Create an API key:**

```bash
gcloud alpha services api-keys create --display-name="Veo Video Generator"
```

2. **Set environment variable:**

```bash
export GOOGLE_API_KEY="your-api-key-here"
```

#### Option C: gcloud CLI (Interactive)

```bash
gcloud auth login
gcloud config set project your-project-id
```

## Usage

### Run the Video Generator

```bash
python generate_video.py
```

### Follow the Interactive Prompts

1. **Choose Generation Type**:

   - Option 1: Text-to-Video
   - Option 2: Image-to-Video

2. **Configure Parameters**:

   - Video duration (5-8 seconds)
   - Aspect ratio (16:9 or 9:16)
   - Negative prompt (optional)
   - Enhanced prompts (recommended)

3. **Provide Input**:

   - For text-to-video: Enter a descriptive prompt
   - For image-to-video: Provide image path and text description

4. **Get Your Video**:
   - The script automatically saves the generated video as an MP4 file
   - Files are saved in the current directory with descriptive names
   - Example: `A_cat_reading_a_book_20250107_143052.mp4`

### Example Prompts

**Text-to-Video Examples:**

- "A cat reading a book in a cozy library"
- "Waves crashing on a beach at sunset"
- "A futuristic city with flying cars at night"

**Image-to-Video Examples:**

- Image: Photo of a person + Prompt: "The person waves hello"
- Image: Landscape photo + Prompt: "Clouds moving across the sky"

## Configuration

### Project Settings

Edit the configuration variables in `generate_video.py`:

```python
PROJECT_ID = "your-project-id"
LOCATION_ID = "us-central1"
MODEL_ID = "veo-3.0-generate-preview"
```

### Video Parameters

- **Duration**: 5-8 seconds (Veo 3 supports 8 seconds)
- **Aspect Ratio**: 16:9 (landscape) or 9:16 (portrait)
- **Resolution**: 720p
- **Frame Rate**: 24 FPS

## File Structure

```
generate-veo3-videos-py/
├── generate_video.py    # Main video generation script
├── requirements.txt     # Python dependencies
├── setup.py            # Setup and installation script
└── README.md           # This file
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed

   ```bash
   pip install -r requirements.txt
   ```

2. **Authentication Errors**: Ensure you're logged in to Google Cloud

   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

3. **API Access Errors**: Veo models may require allowlist approval

   - Check your project has access to Veo models
   - Contact Google Cloud support if needed

4. **Permission Errors**: Ensure your account has the necessary IAM roles
   - Vertex AI User
   - Storage Admin (if using GCS bucket)

### Getting Help

- Check the [Vertex AI documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/video/generate-videos)
- Review Google Cloud [authentication guide](https://cloud.google.com/docs/authentication)
- Submit issues to the project repository

## API Limits

- **Maximum API requests per minute**: 20
- **Maximum videos per request**: 4
- **Video length**: 5-8 seconds
- **Maximum image size**: 20 MB

## Costs

Video generation using Veo models incurs charges. Check the [Vertex AI pricing](https://cloud.google.com/vertex-ai/pricing) page for current rates.

## License

This project is provided as-is for educational and development purposes. Please review Google Cloud terms of service for usage guidelines.
