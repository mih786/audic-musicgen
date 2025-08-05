#!/usr/bin/env python3
"""
Test script for Modal app
"""

import subprocess
import json
import sys

def test_modal_app():
    """Test the Modal app for issues"""
    print("🧪 Testing Modal App")
    print("=" * 30)
    
    # Test 1: Check if Modal CLI is available
    print("1. Checking Modal CLI...")
    try:
        result = subprocess.run(["modal", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Modal CLI available: {result.stdout.strip()}")
        else:
            print("❌ Modal CLI not available")
            return False
    except FileNotFoundError:
        print("❌ Modal CLI not found. Install with: pip install modal")
        return False
    
    # Test 2: Check app structure
    print("\n2. Checking app structure...")
    try:
        from modal_app import app, health_check, generate_fitness_ad, simple_test
        print("✅ App structure is valid")
    except Exception as e:
        print(f"❌ App structure error: {e}")
        return False
    
    # Test 3: Check environment variables
    print("\n3. Checking environment variables...")
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'S3_BUCKET_NAME']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("💡 Run 'python3 setup_aws.py' to configure")
    else:
        print("✅ Environment variables configured")
    
    # Test 4: Test simple function
    print("\n4. Testing simple function...")
    try:
        with app.run():
            result = simple_test.remote()
            print(f"✅ Simple test result: {result}")
    except Exception as e:
        print(f"❌ Simple test failed: {e}")
        print("💡 This might be due to image build issues. Check Modal logs.")
        return False
    
    # Test 5: Test health check function (optional)
    print("\n5. Testing health check...")
    try:
        with app.run():
            result = health_check.remote()
            print(f"✅ Health check result: {result}")
    except Exception as e:
        print(f"⚠️  Health check failed: {e}")
        print("💡 This is expected if environment variables are not set")
    
    print("\n🎉 Modal app test completed!")
    return True

if __name__ == "__main__":
    success = test_modal_app()
    sys.exit(0 if success else 1) 