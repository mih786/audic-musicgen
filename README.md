# MusicGen - Modal Serverless App

This is a serverless Modal app that demonstrates AI-powered music generation using Facebook's MusicGen model from AudioCraft.

## 🎵 Features

- 🎵 **AI Music Generation**: Uses Facebook's MusicGen model for high-quality music generation
- 🚀 **Serverless Deployment**: Deployed on Modal for scalable, on-demand music generation
- ☁️ **S3 Integration**: Automatically uploads generated music to AWS S3
- 🎛️ **Multiple Model Sizes**: Support for small, medium, large, and melody models
- ⏱️ **Flexible Duration**: Generate music from 1-300 seconds
- 🔧 **Easy Configuration**: Simple setup with environment variables

## 🚀 Quick Start

### Prerequisites

- Modal account and CLI installed
- AWS account with S3 bucket
- Python 3.11+

### 1. Clone and Setup

```bash
git clone <repository-url>
cd audic-musicgen
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file:

```bash
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=audic-musicgen
HUGGING_FACE_TOKEN=your_hf_token  # Optional
```

### 3. Deploy to Modal

```bash
modal deploy musicgen_app.py
```

### 4. Generate Music

```bash
modal run musicgen_app.py::generate_music \
  --prompt "Energetic electronic dance music with heavy bass and synthesizers" \
  --duration 30 \
  --model-size large
```

## 📁 Project Structure

```
audic-musicgen/
├── musicgen_app.py           # Main Modal app with MusicGen
├── test_musicgen.py          # Test script for MusicGen
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── .gitignore               # Git ignore file
```

## 🔧 Configuration

### Environment Variables

- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
- `AWS_REGION`: AWS region (default: us-east-1)
- `S3_BUCKET_NAME`: S3 bucket for storing generated music
- `HUGGING_FACE_TOKEN`: Hugging Face token (optional, for private models)

### Modal Secrets Setup

```bash
modal secret create aws-credentials AWS_ACCESS_KEY_ID=your_key AWS_SECRET_ACCESS_KEY=your_secret AWS_REGION=us-east-1 S3_BUCKET_NAME=audic-musicgen
modal secret create huggingface-token HUGGING_FACE_TOKEN=your_token
```

## 🎵 Usage Examples

### Basic Music Generation

```python
import modal

# Get the app
app = modal.App.lookup("audic-musicgen")

# Generate music
result = app.generate_music.remote(
    prompt="Upbeat electronic music with synthesizers and drums",
    duration=30,
    model_size="large"
)
```

### Advanced Usage

```python
# Generate with melody model
result = app.generate_music_with_melody.remote(
    prompt="Jazz fusion with saxophone and piano",
    melody_prompt="Smooth jazz melody",
    duration=45,
    model_size="melody"
)
```

## 🎛️ Model Options

### Available Models

- **small**: Fast generation, good for prototyping
- **medium**: Balanced speed and quality
- **large**: Best quality, slower generation
- **melody**: Specialized for melody generation

### Model Specifications

- **Small**: 300M parameters, ~10s generation time
- **Medium**: 1.5B parameters, ~30s generation time  
- **Large**: 3.3B parameters, ~60s generation time
- **Melody**: 1.5B parameters, melody-focused

## 📊 Output Format

Generated music is saved as WAV files and uploaded to S3 with the following structure:

```
s3://your-bucket/musicgen/
├── {message_deduplication_id}/
│   ├── musicgen_{id}_{timestamp}.wav
│   └── musicgen_melody_{id}_{timestamp}.wav
```

## 🧪 Testing

Run the test script to verify functionality:

```bash
python3 test_musicgen.py
```

## 📚 Resources

- **MusicGen**: Check [AudioCraft documentation](https://github.com/facebookresearch/audiocraft)
- **Modal**: [Modal documentation](https://modal.com/docs)
- **AudioCraft**: [Facebook Research AudioCraft](https://github.com/facebookresearch/audiocraft) 