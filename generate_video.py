#!/usr/bin/env python3
"""
Video Generation Script using Google's Veo Models
Supports both text-to-video and image-to-video generation
"""

import os
import sys
import time
import base64
import requests
from datetime import datetime
from typing import Optional
from google import genai
from google.genai.types import GenerateVideosConfig, Image
from google.cloud import storage
from google.oauth2.credentials import Credentials as AuthCredentials
from google.cloud import aiplatform  # For aiplatform.init()
import google.auth  # For exceptions

# Configuration
PROJECT_ID = "veo-testing"
LOCATION_ID = "us-central1"
MODEL_ID = "veo-3.0-generate-preview"
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")


def initialize_genai():
    """Initialize Google GenAI client with Vertex AI settings."""
    try:
        # Set environment variables for GenAI SDK to use Vertex AI
        os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
        os.environ["GOOGLE_CLOUD_LOCATION"] = LOCATION_ID
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

        access_token = os.environ.get("GOOGLE_ACCESS_TOKEN")

        if access_token:
            print("🔑 Using provided GOOGLE_ACCESS_TOKEN for authentication.")
            print(
                "💡 Note: Access tokens are short-lived. This method is not suitable for long-running processes without token refresh logic."
            )
            creds_from_token = AuthCredentials(token=access_token)
            # Initialize aiplatform with these explicit credentials.
            # genai.Client() will then use this initialized aiplatform session.
            aiplatform.init(
                project=PROJECT_ID, location=LOCATION_ID, credentials=creds_from_token
            )
        else:
            # If no access token, set up for ADC/Service Account for aiplatform.
            # genai.Client() will internally call aiplatform.init(),
            # which will discover credentials from the environment.
            os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
            os.environ["GOOGLE_CLOUD_LOCATION"] = LOCATION_ID
            print("🔑 No GOOGLE_ACCESS_TOKEN found. Attempting authentication using:")
            if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
                service_account_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
                # Check if the path actually exists
                if os.path.exists(service_account_path):
                    print(
                        f"   - Service account via GOOGLE_APPLICATION_CREDENTIALS: {service_account_path}"
                    )
                else:
                    print(
                        f"   - GOOGLE_APPLICATION_CREDENTIALS is set but file not found: {service_account_path}"
                    )
                    print(
                        "     Falling back to Application Default Credentials (ADC) or other means."
                    )
            elif os.path.exists("veo-service-account.json"):
                # This part of the original script sets the env var.
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
                    "veo-service-account.json"
                )
                print("   - Local service account key: veo-service-account.json")
            else:
                # API Key is not the primary auth for Vertex AI via genai SDK; ADC is.
                print(
                    "   - Application Default Credentials (ADC) (e.g., from 'gcloud auth application-default login')"
                )

        # Initialize the GenAI client.
        client = genai.Client()
        print(
            f"✅ Google GenAI client initialized for project: {PROJECT_ID}, location: {LOCATION_ID} using Vertex AI."
        )
        return client

    except google.auth.exceptions.DefaultCredentialsError as e:
        print(f"❌ Authentication Error: {e}")
        print(
            "💡 Please ensure your environment is authenticated correctly for Google Cloud and Vertex AI."
        )
        print("   Common methods include:")
        print("   - Setting GOOGLE_ACCESS_TOKEN (short-lived).")
        print(
            "   - Setting GOOGLE_APPLICATION_CREDENTIALS to a valid service account JSON key file."
        )
        print("   - Running 'gcloud auth application-default login'.")
        print(
            f"   - Ensure project '{PROJECT_ID}' and location '{LOCATION_ID}' are correctly configured and accessible."
        )
        return None
    except Exception as e:
        print(f"❌ Error initializing Google GenAI client: {e}")
        print("💡 Make sure you have proper authentication set up:")
        print("   - GOOGLE_ACCESS_TOKEN environment variable, or")
        print(
            "   - Service account key file (GOOGLE_APPLICATION_CREDENTIALS or veo-service-account.json), or"
        )
        print(
            "   - gcloud auth login, or"
        )  # Original line, might be better as 'gcloud auth application-default login'
        print(
            "   - GOOGLE_APPLICATION_CREDENTIALS environment variable"
        )  # This is redundant with the SA key file line.
        # Let's refine these general error messages.
        print(
            "   (e.g., 'gcloud auth application-default login' or service account key)."
        )
        return None


def generate_filename(prompt: str, extension: str = "mp4") -> str:
    """Generate a filename based on prompt and timestamp."""
    # Clean the prompt for filename
    clean_prompt = "".join(
        c for c in prompt if c.isalnum() or c in (" ", "-", "_")
    ).rstrip()
    clean_prompt = clean_prompt.replace(" ", "_")[:30]  # Limit length

    # Add timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{clean_prompt}_{timestamp}.{extension}"

    return filename


def download_video_from_gcs(gcs_uri: str, local_filename: str) -> bool:
    """Download video from Google Cloud Storage URI to local file."""
    try:
        print(f"📥 Downloading video from: {gcs_uri}")

        # Check if gcs_uri is None or empty
        if not gcs_uri:
            print(f"❌ GCS URI is None or empty: {gcs_uri}")
            return False

        # Parse GCS URI
        if not gcs_uri.startswith("gs://"):
            print(f"❌ Invalid GCS URI: {gcs_uri}")
            return False

        # Remove gs:// prefix and split bucket/path
        path_without_prefix = gcs_uri[5:]  # Remove 'gs://'
        bucket_name, blob_name = path_without_prefix.split("/", 1)

        # Initialize storage client
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        # Download to local file
        blob.download_to_filename(local_filename)
        print(f"✅ Video saved to: {local_filename}")
        return True

    except Exception as e:
        print(f"❌ Error downloading video: {e}")
        return False


def save_video_data(video_data: bytes, local_filename: str) -> bool:
    """Save video data (bytes) to local MP4 file."""
    try:
        print(f"💾 Saving video data to: {local_filename}")

        with open(local_filename, "wb") as f:
            f.write(video_data)

        print(f"✅ Video saved to: {local_filename}")
        return True

    except Exception as e:
        print(f"❌ Error saving video: {e}")
        return False


def get_user_choice():
    """Get user's choice for video generation method."""
    print("\n🎬 Welcome to AI Video Generator!")
    print("Choose your video generation method:")
    print("1. Text-to-Video (Generate video from text prompt)")
    print("2. Image-to-Video (Generate video from image + text)")

    while True:
        choice = input("\nEnter your choice (1 or 2): ").strip()
        if choice in ["1", "2"]:
            return choice
        print("Invalid choice. Please enter 1 or 2.")


def get_text_prompt():
    """Get text prompt from user."""
    print("\n📝 Enter your video description:")
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as file:
            prompt = file.read()
        print(f"Prompt: {prompt}")
    else:
        prompt = input("Prompt: ").strip()
    while not prompt:
        print("Please enter a valid prompt.")
        prompt = input("Prompt: ").strip()
    return prompt


def get_image_path():
    """Get image path from user."""
    print("\n🖼️  Enter the path to your image file:")
    image_path = input("Image path: ").strip()

    while not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        image_path = input("Please enter a valid image path: ").strip()
        if not image_path:
            return None

    return image_path


def get_generation_parameters():
    """Get optional parameters for video generation."""
    print("\n⚙️  Optional Parameters (press Enter to use defaults):")

    # Duration
    duration = input("Video duration in seconds (5-8, default: 5): ").strip()
    if not duration:
        duration = 5
    else:
        try:
            duration = int(duration)
            if duration < 5 or duration > 8:
                print("Duration must be between 5-8 seconds. Using default: 5")
                duration = 5
        except ValueError:
            print("Invalid duration. Using default: 5")
            duration = 5

    # Aspect ratio
    aspect_ratio = input("Aspect ratio (16:9 or 9:16, default: 16:9): ").strip()
    if aspect_ratio not in ["16:9", "9:16"]:
        aspect_ratio = "16:9"

    # Negative prompt
    negative_prompt = input("Negative prompt (what to avoid): ").strip()

    # Enhanced prompt
    enhance_prompt = input("Use enhanced prompts? (y/n, default: y): ").strip().lower()
    enhance_prompt = enhance_prompt != "n"

    return {
        "duration": duration,
        "aspect_ratio": aspect_ratio,
        "negative_prompt": negative_prompt if negative_prompt else None,
        "enhance_prompt": enhance_prompt,
    }


def generate_text_to_video(client, prompt: str, parameters: dict):
    """Generate video from text prompt using Veo model."""
    try:
        print(f"\n🎯 Generating video from text prompt...")
        print(f"Prompt: {prompt}")

        # Create storage URI or set to None for response data
        output_gcs_uri = None
        if os.environ.get("GCS_BUCKET"):
            output_gcs_uri = f"gs://{os.environ.get('GCS_BUCKET')}/videos/"

        print("🔄 Starting video generation... This may take several minutes.")

        # Create the video generation operation
        operation = client.models.generate_videos(
            model=MODEL_ID,
            prompt=prompt,
            config=GenerateVideosConfig(
                aspect_ratio=parameters["aspect_ratio"],
                output_gcs_uri=output_gcs_uri,
            ),
        )

        # Poll for completion
        while not operation.done:
            time.sleep(15)
            operation = client.operations.get(operation)
            print("⏳ Still generating video...")

        if operation.response:
            print("✅ Video generation completed!")

            # DEBUG: Print the full response structure
            print("\n🔍 DEBUG - Response structure:")
            print(f"operation.response: {operation.response}")
            if hasattr(operation, "result"):
                print(f"operation.result: {operation.result}")
                print(f"operation.result type: {type(operation.result)}")
                if hasattr(operation.result, "__dict__"):
                    print(f"operation.result attributes: {operation.result.__dict__}")

            # Generate local filename
            local_filename = generate_filename(prompt)

            # Handle the response
            if (
                hasattr(operation.result, "generated_videos")
                and operation.result.generated_videos
            ):
                print(
                    f"🔍 DEBUG - Found generated_videos: {len(operation.result.generated_videos)} videos"
                )
                video_info = operation.result.generated_videos[0]
                print(f"🔍 DEBUG - Video info: {video_info}")
                print(f"🔍 DEBUG - Video info type: {type(video_info)}")
                if hasattr(video_info, "__dict__"):
                    print(f"🔍 DEBUG - Video info attributes: {video_info.__dict__}")

                if hasattr(video_info, "video") and video_info.video is not None:
                    # Check if video has direct bytes data first
                    if (
                        hasattr(video_info.video, "video_bytes")
                        and video_info.video.video_bytes
                    ):
                        print("📹 Video data received directly (video_bytes)")
                        video_bytes = video_info.video.video_bytes
                        if save_video_data(video_bytes, local_filename):
                            return True
                        else:
                            print(
                                "⚠️ Failed to save video data, but generation was successful"
                            )
                            return True

                    # Check if video has GCS URI
                    elif hasattr(video_info.video, "uri") and video_info.video.uri:
                        video_uri = video_info.video.uri
                        print(f"📹 Video stored at: {video_uri}")
                        if download_video_from_gcs(video_uri, local_filename):
                            return True
                        else:
                            print(
                                "⚠️ Failed to download video, but generation was successful"
                            )
                            return True

                    else:
                        print("⚠️ Video object found but no video_bytes or valid uri")
                        print(
                            f"🔍 Video object attributes: {video_info.video.__dict__ if hasattr(video_info.video, '__dict__') else 'No __dict__'}"
                        )
                        return True

                elif hasattr(video_info, "video_data"):
                    # Video data returned directly
                    video_data = video_info.video_data
                    if isinstance(video_data, str):
                        # Base64 encoded data
                        video_bytes = base64.b64decode(video_data)
                    else:
                        # Raw bytes
                        video_bytes = video_data

                    return save_video_data(video_bytes, local_filename)

            # Check if video data is in the response directly
            elif hasattr(operation.result, "video_data"):
                print("🔍 DEBUG - Found video_data directly in result")
                video_data = operation.result.video_data
                if isinstance(video_data, str):
                    video_bytes = base64.b64decode(video_data)
                else:
                    video_bytes = video_data
                return save_video_data(video_bytes, local_filename)

            # Try alternative response structures
            elif hasattr(operation.result, "videos") and operation.result.videos:
                print("🔍 DEBUG - Found videos array in result")
                video_info = operation.result.videos[0]
                print(f"🔍 DEBUG - Video from videos array: {video_info}")
                if hasattr(video_info, "gcsUri"):
                    video_uri = video_info.gcsUri
                    print(f"📹 Video stored at (gcsUri): {video_uri}")
                    if video_uri and download_video_from_gcs(video_uri, local_filename):
                        return True
                elif hasattr(video_info, "uri"):
                    video_uri = video_info.uri
                    print(f"📹 Video stored at (uri): {video_uri}")
                    if video_uri and download_video_from_gcs(video_uri, local_filename):
                        return True

            else:
                print(
                    "✅ Video generated successfully, but unable to retrieve video data"
                )
                print("💡 Check your GCS bucket or response format")
                print("🔍 DEBUG - Available result attributes:")
                if hasattr(operation.result, "__dict__"):
                    for attr, value in operation.result.__dict__.items():
                        print(f"  - {attr}: {type(value)} = {value}")
                return True

        else:
            print("❌ No response received from video generation")
            return False

    except Exception as e:
        print(f"❌ Error generating video: {e}")
        return False


def generate_image_to_video(client, image_path: str, prompt: str, parameters: dict):
    """Generate video from image and text prompt using Veo model."""
    try:
        print(f"\n🎯 Generating video from image and text...")
        print(f"Image: {image_path}")
        print(f"Prompt: {prompt}")

        # Create storage URI or set to None for response data
        output_gcs_uri = None
        if os.environ.get("GCS_BUCKET"):
            output_gcs_uri = f"gs://{os.environ.get('GCS_BUCKET')}/videos/"

        print("🔄 Starting video generation... This may take several minutes.")

        # Create image object from file
        mime_type = "image/png" if image_path.lower().endswith(".png") else "image/jpeg"

        # Create the video generation operation
        operation = client.models.generate_videos(
            model=MODEL_ID,
            prompt=prompt,
            image=Image(
                gcs_uri=None,  # We'll use local file path for now
                mime_type=mime_type,
            ),
            config=GenerateVideosConfig(
                aspect_ratio=parameters["aspect_ratio"],
                output_gcs_uri=output_gcs_uri,
            ),
        )

        # Poll for completion
        while not operation.done:
            time.sleep(15)
            operation = client.operations.get(operation)
            print("⏳ Still generating video...")

        if operation.response:
            print("✅ Video generation completed!")

            # DEBUG: Print the full response structure
            print("\n🔍 DEBUG - Response structure:")
            print(f"operation.response: {operation.response}")
            if hasattr(operation, "result"):
                print(f"operation.result: {operation.result}")
                print(f"operation.result type: {type(operation.result)}")
                if hasattr(operation.result, "__dict__"):
                    print(f"operation.result attributes: {operation.result.__dict__}")

            # Generate local filename
            local_filename = generate_filename(f"image_to_video_{prompt}")

            # Handle the response
            if (
                hasattr(operation.result, "generated_videos")
                and operation.result.generated_videos
            ):
                print(
                    f"🔍 DEBUG - Found generated_videos: {len(operation.result.generated_videos)} videos"
                )
                video_info = operation.result.generated_videos[0]
                print(f"🔍 DEBUG - Video info: {video_info}")
                print(f"🔍 DEBUG - Video info type: {type(video_info)}")
                if hasattr(video_info, "__dict__"):
                    print(f"🔍 DEBUG - Video info attributes: {video_info.__dict__}")

                if hasattr(video_info, "video") and video_info.video is not None:
                    # Check if video has direct bytes data first
                    if (
                        hasattr(video_info.video, "video_bytes")
                        and video_info.video.video_bytes
                    ):
                        print("📹 Video data received directly (video_bytes)")
                        video_bytes = video_info.video.video_bytes
                        if save_video_data(video_bytes, local_filename):
                            return True
                        else:
                            print(
                                "⚠️ Failed to save video data, but generation was successful"
                            )
                            return True

                    # Check if video has GCS URI
                    elif hasattr(video_info.video, "uri") and video_info.video.uri:
                        video_uri = video_info.video.uri
                        print(f"📹 Video stored at: {video_uri}")
                        if download_video_from_gcs(video_uri, local_filename):
                            return True
                        else:
                            print(
                                "⚠️ Failed to download video, but generation was successful"
                            )
                            return True

                    else:
                        print("⚠️ Video object found but no video_bytes or valid uri")
                        print(
                            f"🔍 Video object attributes: {video_info.video.__dict__ if hasattr(video_info.video, '__dict__') else 'No __dict__'}"
                        )
                        return True

                elif hasattr(video_info, "video_data"):
                    # Video data returned directly
                    video_data = video_info.video_data
                    if isinstance(video_data, str):
                        # Base64 encoded data
                        video_bytes = base64.b64decode(video_data)
                    else:
                        # Raw bytes
                        video_bytes = video_data

                    return save_video_data(video_bytes, local_filename)

            # Check if video data is in the response directly
            elif hasattr(operation.result, "video_data"):
                video_data = operation.result.video_data
                if isinstance(video_data, str):
                    video_bytes = base64.b64decode(video_data)
                else:
                    video_bytes = video_data
                return save_video_data(video_bytes, local_filename)

            else:
                print(
                    "✅ Video generated successfully, but unable to retrieve video data"
                )
                print("💡 Check your GCS bucket or response format")
                return True

        else:
            print("❌ No response received from video generation")
            return False

    except Exception as e:
        print(f"❌ Error generating video: {e}")
        return False


def main():
    """Main function to orchestrate the video generation process."""
    print("🚀 AI Video Generator using Google's Veo Models")

    # Initialize GenAI client
    client = initialize_genai()
    if not client:
        sys.exit(1)

    try:
        # Get user choice
        choice = get_user_choice()

        # Get generation parameters
        parameters = get_generation_parameters()

        if choice == "1":
            # Text-to-Video
            prompt = get_text_prompt()
            success = generate_text_to_video(client, prompt, parameters)
        else:
            # Image-to-Video
            image_path = get_image_path()
            if not image_path:
                print("❌ No image provided. Exiting.")
                sys.exit(1)

            prompt = get_text_prompt()
            success = generate_image_to_video(client, image_path, prompt, parameters)

        if success:
            print("\n🎉 Video generation process completed successfully!")
            print("📁 Check the current directory for your generated MP4 file!")
            print(
                "💡 The video file is saved with a timestamp for easy identification."
            )
        else:
            print(
                "\n❌ Video generation failed. Please check your inputs and try again."
            )

    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
