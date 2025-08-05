#!/usr/bin/env python3
"""
Test different prompts with the AudioGen Modal app
"""

import subprocess
import json
import re
from datetime import datetime

def create_fitness_ad_prompt() -> str:
    #prompt = """Cozy coffee shop ambience, gentle coffee brewing sounds, soft espresso machine hissing, warm acoustic background music, morning café atmosphere, light jazz undertones, comfortable conversational setting, inviting coffee aroma soundscape, 30 seconds"""
    prompt = """Energetic, dynamic, high-energy music to be used as a background for a coffee ad, 30 seconds"""
    return prompt.strip()

def test_fitness_ad_prompt():
    """Test the default fitness ad prompt"""
    print("🏃 Testing Fitness Ad Prompt")
    print("=" * 40)
    
    # Get the fitness ad prompt
    prompt = create_fitness_ad_prompt()
    print(f"📝 Using fitness ad prompt: {prompt}")
    
    try:
        result = subprocess.run([
            "modal", "run", "modal_app.py::generate_sfx",
            "--prompt", prompt,
            "--duration", "30"
        ], capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print("✅ Fitness ad generation completed!")
            return extract_s3_uri(result.stdout + result.stderr)
        else:
            print(f"❌ Fitness ad generation failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_health_check():
    """Test the health check function"""
    print("🏥 Testing Health Check")
    print("=" * 30)
    
    try:
        result = subprocess.run([
            "modal", "run", "modal_app.py::health_check"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Health check completed!")
            return True
        else:
            print(f"❌ Health check failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def extract_s3_uri(output: str):
    """Extract S3 URI from Modal output"""
    s3_uri_pattern = r's3://[^\s]+'
    s3_matches = re.findall(s3_uri_pattern, output)
    
    if s3_matches:
        return s3_matches[0]
    
    # Try to find JSON with S3 URI
    json_pattern = r'\{[^{}]*"s3_uri"[^{}]*\}'
    matches = re.findall(json_pattern, output)
    
    for match in matches:
        try:
            data = json.loads(match)
            if "s3_uri" in data:
                return data["s3_uri"]
        except json.JSONDecodeError:
            continue
    
    return None

def main():
    """Main function to test different prompts"""
    print("🎵 AudioGen Modal App - Prompt Testing")
    print("=" * 50)
    
    
    # Test 1: Default fitness ad prompt
    print("\n3️⃣ Testing default fitness ad prompt...")
    s3_uri = test_fitness_ad_prompt()
    if s3_uri:
        print(f"✅ S3 URI: {s3_uri}")
    else:
        print("❌ No S3 URI found")
    

    print("\n🎉 Prompt testing completed!")
    print("💡 Check the S3 URIs above to download your generated audio files")

if __name__ == "__main__":
    main() 