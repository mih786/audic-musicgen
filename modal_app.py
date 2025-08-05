import modal
import requests
import json
import time
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

# Create Modal app
app = modal.App("audiogen-demo")

# Define the image with required dependencies
image = modal.Image.from_registry("python:3.11-slim").apt_install("git", "gcc", "ffmpeg").pip_install([
    "requests",
    "scipy",
    "boto3",
    "python-dotenv",
    "transformers",
    "git+https://github.com/facebookresearch/audiocraft.git"
])

def validate_environment():
    """Validate required environment variables"""
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'S3_BUCKET_NAME']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("💡 Run 'python3 setup_modal_secrets.py' to configure AWS credentials")
        print("💡 Or use Modal secrets: modal secret create aws-credentials AWS_ACCESS_KEY_ID=... AWS_SECRET_ACCESS_KEY=...")
        return False
    
    return True

# Define cache volume for model storage
model_cache = modal.Volume.from_name("model-cache", create_if_missing=True)

@app.function(image=image, gpu="A10G", timeout=600, volumes={"/cache_volume": model_cache}, secrets=[modal.Secret.from_name("aws-credentials"), modal.Secret.from_name("huggingface-token")])
def generate_sfx(prompt: str, duration: int = 60) -> Dict[str, Any]:
    """
    Generate audio using AudioGen model
    
    Args:
        prompt: Text description of the audio to generate
        duration: Duration in seconds (1-300)
    """
    try:
        # Validate environment variables
        if not validate_environment():
            return {"error": "Missing AWS credentials. Please run setup_modal_secrets.py or use Modal secrets"}
        
        from audiocraft.models import AudioGen
        from audiocraft.data.audio import audio_write
        import torch
        import base64
        import io
        import numpy as np
        from datetime import datetime
        
        # Get Hugging Face token if available
        hf_token = os.getenv('HUGGING_FACE_TOKEN')
        
        # Load AudioGen model with optional token and error handling
        try:
            print("🌐 Downloading public model from Hugging Face")
            model = AudioGen.get_pretrained('facebook/audiogen-medium')
        except Exception as model_error:
            print(f"❌ Failed to load AudioGen model: {model_error}")
            return {"error": f"Model loading failed: {str(model_error)}"}
        
        # Validate duration
        if duration < 1 or duration > 300:
            return {"error": "Duration must be between 1 and 300 seconds"}
        
        # Validate prompt
        if not prompt or not prompt.strip():
            return {"error": "Prompt cannot be empty"}
        
        model.set_generation_params(duration=duration)
        
        print(f"🎵 Generating {duration}-second audio...")
        print(f"📝 Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
        
        # Generate audio using AudioGen with error handling
        try:
            wav = model.generate([prompt])  # generates audio for the prompt
        except Exception as gen_error:
            print(f"❌ Audio generation failed: {gen_error}")
            return {"error": f"Audio generation failed: {str(gen_error)}"}
        
        # Get the first (and only) generated audio
        audio_values = wav[0]  # AudioGen returns a list of generated samples
        
        sampling_rate = model.sample_rate
        print(f"✅ Audio generated successfully! Sample rate: {sampling_rate}Hz")
        
        # Save the file using the recommended audio_write function
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_audio_{timestamp}"
        
        # Use audio_write as recommended in the documentation
        audio_write(filename, audio_values.cpu(), sampling_rate, strategy="loudness", loudness_compressor=True)
        
        # The file is saved with .wav extension by audio_write
        wav_filename = f"{filename}.wav"
        
        # Read the file back for base64 encoding
        with open(wav_filename, 'rb') as f:
            audio_bytes = f.read()
        
        # Convert to base64 for transmission
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        print(f"💾 Saved locally: {wav_filename}")
        
        # Upload to S3
        try:
            import boto3
            
            s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            
            bucket_name = os.getenv('S3_BUCKET_NAME', 'audiogen-demo')
            s3_key = f"audio/{wav_filename}"
            
            s3_client.upload_file(wav_filename, bucket_name, s3_key)
            
            # Generate S3 URI (internal path)
            s3_uri = f"s3://{bucket_name}/{s3_key}"
            
            print(f"✅ Audio uploaded to S3: {s3_uri}")
            
            return {
                "success": True,
                "audio_base64": audio_base64,
                "sampling_rate": sampling_rate,
                "duration": duration,
                "format": "wav",
                "filename": wav_filename,
                "file_size_bytes": len(audio_bytes),
                "s3_uri": s3_uri,
                "s3_bucket": bucket_name,
                "s3_key": s3_key,
                "prompt_used": prompt
            }
            
        except Exception as s3_error:
            print(f"⚠️  S3 upload failed: {s3_error}")
            # Return without S3 info if upload fails
            return {
                "success": True,
                "audio_base64": audio_base64,
                "sampling_rate": sampling_rate,
                "duration": duration,
                "format": "wav",
                "filename": wav_filename,
                "file_size_bytes": len(audio_bytes),
                "prompt_used": prompt
            }
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return {"error": str(e)}

@app.function(image=image)
def simple_test() -> Dict[str, Any]:
    """Simple test function to verify Modal app works"""
    return {
        "status": "success",
        "message": "Modal app is working!",
        "timestamp": "2024-01-01"
    }

@app.function(image=image)
def health_check() -> Dict[str, Any]:
    """Health check function to test Modal app configuration"""
    try:
        # Test environment variables
        env_status = validate_environment()
        
        # Test imports
        import_status = True
        missing_imports = []
        
        try:
            import torch
        except ImportError:
            missing_imports.append("torch")
            import_status = False
            
        try:
            import scipy
        except ImportError:
            missing_imports.append("scipy")
            import_status = False
            
        try:
            import boto3
        except ImportError:
            missing_imports.append("boto3")
            import_status = False
        
        return {
            "status": "healthy" if env_status and import_status else "unhealthy",
            "environment_valid": env_status,
            "imports_valid": import_status,
            "missing_imports": missing_imports,
            "gpu_available": True,  # Modal handles GPU allocation
            "modal_version": "1.1.0"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    # For local testing
    with app.run():
        result = simple_test.remote()
        print(f"Test result: {result}") 