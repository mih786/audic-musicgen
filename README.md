# AudioGen Demo - Modal Serverless App

This is a serverless Modal app that demonstrates AI-powered audio generation for fitness advertisements using AudioCraft/AudioGen models.

## Features

- 🎵 **Local Audio Generation**: Uses Facebook's AudioGen model for local audio generation
- 🌐 **S3 Integration**: Automatic upload to S3 for easy file management
- 🏃 **Fitness Ad Templates**: Pre-built prompts for fitness advertisement audio
- 🔧 **Custom Prompts**: Generate audio from any text prompt
- ⚡ **Serverless**: Runs on Modal's serverless infrastructure with GPU acceleration

## Quick Start

### 1. Install Dependencies

```bash
pip install modal python-dotenv boto3 requests
```

### 2. Setup AWS Credentials & Modal Secrets

```bash
python3 setup_modal_secrets.py
```

### 3. Deploy the App

```bash
modal deploy modal_app.py
```

### 4. Generate Audio

```bash
python3 generate_audio.py
```

## Usage

### Generate Audio (Main Function)

```bash
modal run modal_app.py::generate_sfx --prompt "your audio description" --duration 60
```

### Test the App

```bash
# Simple test
modal run modal_app.py::simple_test

# Health check
modal run modal_app.py::health_check
```

### Test Multiple Prompts

```bash
python3 test_prompts.py
```

This will test:
1. Simple function
2. Health check
3. Default fitness ad prompt
4. Electronic music
5. Nature sounds
6. Rock music
7. Ambient music

### Examples

```bash
# Fitness ad audio
modal run modal_app.py::generate_sfx --prompt "upbeat motivational fitness music" --duration 30

# Nature sounds
modal run modal_app.py::generate_sfx --prompt "peaceful nature sounds with birds and water" --duration 45

# Any custom audio
modal run modal_app.py::generate_sfx --prompt "your custom prompt here" --duration 60
```

## File Structure

```
audic-audiogen/
├── modal_app.py              # Main Modal app with AudioGen
├── test_modal.py            # Test script for Modal app
├── test_prompts.py          # Test different prompts
├── setup_modal_secrets.py   # Complete setup script
├── .env                     # AWS credentials (created by setup)
├── README.md                # This file
└── requirements.txt         # Python dependencies
```

## Environment Variables & Secrets

### Option 1: Local .env File (Development)
The `.env` file contains:

```env
# AWS Credentials
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key_here
AWS_REGION=us-east-1

# S3 Configuration
S3_BUCKET_NAME=audiogen-demo

# Hugging Face Token (optional)
HUGGING_FACE_TOKEN=your_hugging_face_token_here
```

### Option 2: Modal Secrets (Production - Recommended)
For production, use Modal secrets for better security:

```bash
# Create secrets from .env file
python3 setup_modal_secrets.py

# Or manually create secrets
modal secret create aws-credentials AWS_ACCESS_KEY_ID=your_key AWS_SECRET_ACCESS_KEY=your_secret AWS_REGION=us-east-1 S3_BUCKET_NAME=audiogen-demo
modal secret create huggingface-token HUGGING_FACE_TOKEN=your_token
```

The app automatically uses Modal secrets when available, falling back to .env file for local development.

### Option 3: Function Parameters
For dynamic values, pass them as function parameters:

```python
@app.function(image=image, gpu=gpu_config)
def generate_audio_local(
    prompt: str, 
    duration: int = 60,
    model_name: str = "facebook/audiogen-medium"
):
    # Use parameters directly
```

### Option 4: Modal Mounts
For configuration files:

```python
config_mount = modal.Mount.from_local_file("config.json", remote_path="/config.json")

@app.function(image=image, mounts=[config_mount])
def generate_audio_local(prompt: str, duration: int = 60):
    import json
    with open("/config.json", "r") as f:
        config = json.load(f)
```

## Model Details

- **Model**: `facebook/audiogen-medium` (1.5B parameters)
- **Library**: AudioCraft from Facebook Research
- **GPU**: A10G for acceleration
- **Output**: WAV format with configurable duration
- **Authentication**: Public model (no token required, but optional for better performance)

## Security Notes

- The `.env` file is automatically added to `.gitignore`
- Never commit your AWS credentials to version control
- Use IAM roles with minimal required permissions

## Troubleshooting

### CUDA Errors
The app uses GPU acceleration with A10G. If you encounter issues, check Modal's GPU availability.

### S3 Upload Failures
- Check your AWS credentials
- Ensure the S3 bucket exists and is accessible
- Verify your IAM user has S3 permissions

### Timeout Issues
- Try shorter audio durations (15-30 seconds)
- Check your internet connection
- Ensure Modal has enough resources

## Support

For issues with:
- **Modal**: Check [Modal documentation](https://modal.com/docs)
- **AWS**: Check [AWS documentation](https://docs.aws.amazon.com)
- **AudioGen**: Check [AudioCraft documentation](https://github.com/facebookresearch/audiocraft) 