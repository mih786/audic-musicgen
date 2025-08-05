#!/usr/bin/env python3
"""
Complete setup for AudioGen Modal app - AWS credentials and Modal secrets
"""

import subprocess
import os
from pathlib import Path
from dotenv import load_dotenv

def create_env_file():
    """Create a new .env file"""
    env_content = """# AWS Credentials
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key_here
AWS_REGION=us-east-1

# S3 Configuration
S3_BUCKET_NAME=audiogen-demo

# Hugging Face Token (optional)
HUGGING_FACE_TOKEN=your_hugging_face_token_here
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ Created .env file")

def setup_aws_credentials():
    """Setup AWS credentials in .env file"""
    print("🔧 AWS Credentials Setup")
    print("=" * 30)
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found. Creating one...")
        create_env_file()
    
    # Load existing values from .env
    existing_values = load_env_values()
    
    print("📝 Please provide your AWS credentials:")
    print("   You can get these from the AWS Console > IAM > Users > Security credentials")
    print("   Or use AWS CLI: aws configure")
    print()
    
    # Get AWS credentials from user with existing values as defaults
    access_key = input(f"AWS Access Key ID (current: {existing_values.get('AWS_ACCESS_KEY_ID', 'not set')}): ").strip()
    if not access_key and existing_values.get('AWS_ACCESS_KEY_ID'):
        access_key = existing_values['AWS_ACCESS_KEY_ID']
    
    secret_key = input(f"AWS Secret Access Key (current: {'*' * 8 if existing_values.get('AWS_SECRET_ACCESS_KEY') else 'not set'}): ").strip()
    if not secret_key and existing_values.get('AWS_SECRET_ACCESS_KEY'):
        secret_key = existing_values['AWS_SECRET_ACCESS_KEY']
    
    region = input(f"AWS Region (current: {existing_values.get('AWS_REGION', 'us-east-1')}): ").strip()
    if not region:
        region = existing_values.get('AWS_REGION', 'us-east-1')
    
    bucket_name = input(f"S3 Bucket Name (current: {existing_values.get('S3_BUCKET_NAME', 'audiogen-demo')}): ").strip()
    if not bucket_name:
        bucket_name = existing_values.get('S3_BUCKET_NAME', 'audiogen-demo')
    
    print("\n🔐 Hugging Face Token (Optional):")
    print("   The AudioGen model is public and doesn't require a token.")
    print("   However, if you have a Hugging Face token, you can provide it for:")
    print("   - Faster downloads")
    print("   - Access to private models in the future")
    print("   - Better rate limits")
    print()
    
    current_hf_token = existing_values.get('HUGGING_FACE_TOKEN', 'not set')
    hf_token = input(f"Hugging Face Token (current: {'*' * 8 if current_hf_token != 'not set' else 'not set'}, press Enter to keep current): ").strip()
    if not hf_token and current_hf_token != 'not set':
        hf_token = current_hf_token
    
    # Update .env file
    update_env_file(access_key, secret_key, region, bucket_name, hf_token)
    
    print("\n✅ Credentials updated in .env file!")

def load_env_values():
    """Load existing values from .env file"""
    values = {}
    if Path(".env").exists():
        with open(".env", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    values[key] = value
    return values

def update_env_file(access_key, secret_key, region, bucket_name, hf_token=None):
    """Update .env file with provided credentials"""
    # Read current .env file
    env_lines = []
    if Path(".env").exists():
        with open(".env", "r") as f:
            env_lines = f.readlines()
    
    # Update or add credentials
    updated = {
        "AWS_ACCESS_KEY_ID": access_key,
        "AWS_SECRET_ACCESS_KEY": secret_key,
        "AWS_REGION": region,
        "S3_BUCKET_NAME": bucket_name
    }
    
    # Add Hugging Face token if provided
    if hf_token:
        updated["HUGGING_FACE_TOKEN"] = hf_token
    
    # Process existing lines
    new_lines = []
    for line in env_lines:
        line = line.strip()
        if line and not line.startswith("#"):
            key, value = line.split("=", 1)
            if key in updated:
                new_lines.append(f"{key}={updated[key]}")
                del updated[key]
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    # Add any new keys
    for key, value in updated.items():
        new_lines.append(f"{key}={value}")
    
    # Write back to .env file
    with open(".env", "w") as f:
        f.write("\n".join(new_lines) + "\n")

def create_modal_secrets():
    """Create Modal secrets from .env file"""
    print("🔐 Setting up Modal Secrets")
    print("=" * 40)
    
    # Load .env file
    load_dotenv()
    
    # Check if .env exists
    if not Path(".env").exists():
        print("❌ .env file not found!")
        print("💡 Run setup first to create .env file")
        return False
    
    # Get AWS credentials from .env
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_REGION', 'us-east-1')
    s3_bucket = os.getenv('S3_BUCKET_NAME', 'audiogen-demo')
    hf_token = os.getenv('HUGGING_FACE_TOKEN')
    
    if not aws_access_key or not aws_secret_key:
        print("❌ AWS credentials not found in .env file!")
        print("💡 Run setup first to configure AWS credentials")
        return False
    
    print("📋 Creating Modal secrets...")
    
    # Create AWS credentials secret
    try:
        aws_secret_cmd = [
            "modal", "secret", "create", "aws-credentials",
            f"AWS_ACCESS_KEY_ID={aws_access_key}",
            f"AWS_SECRET_ACCESS_KEY={aws_secret_key}",
            f"AWS_REGION={aws_region}",
            f"S3_BUCKET_NAME={s3_bucket}"
        ]
        
        result = subprocess.run(aws_secret_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ AWS credentials secret created successfully!")
        else:
            print(f"⚠️  AWS secret creation failed: {result.stderr}")
            print("💡 Secret might already exist. Continuing...")
    
    except Exception as e:
        print(f"❌ Error creating AWS secret: {e}")
        return False
    
    # Create Hugging Face token secret (if available)
    if hf_token:
        try:
            hf_secret_cmd = [
                "modal", "secret", "create", "huggingface-token",
                f"HUGGING_FACE_TOKEN={hf_token}"
            ]
            
            result = subprocess.run(hf_secret_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Hugging Face token secret created successfully!")
            else:
                print(f"⚠️  HF token secret creation failed: {result.stderr}")
                print("💡 Secret might already exist. Continuing...")
        
        except Exception as e:
            print(f"❌ Error creating HF token secret: {e}")
    
    print("\n🎉 Modal secrets setup complete!")
    print("💡 Your app will now use Modal secrets instead of .env file")
    return True

def test_aws_credentials():
    """Test AWS credentials"""
    print("\n🧪 Testing AWS credentials...")
    
    try:
        import boto3
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # Test S3 access
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        
        bucket_name = os.getenv('S3_BUCKET_NAME', 'audiogen-demo')
        
        # Try to list buckets
        response = s3_client.list_buckets()
        print(f"✅ AWS credentials working! Found {len(response['Buckets'])} buckets")
        
        # Check if our bucket exists
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            print(f"✅ S3 bucket '{bucket_name}' exists and is accessible")
        except Exception as e:
            print(f"⚠️  S3 bucket '{bucket_name}' not found or not accessible: {e}")
            print("💡 You may need to create the bucket or check permissions")
        
    except Exception as e:
        print(f"❌ AWS credentials test failed: {e}")
        print("💡 Please check your credentials and try again")

def create_s3_bucket():
    """Create S3 bucket if it doesn't exist"""
    print("\n🪣 Creating S3 bucket...")
    
    try:
        import boto3
        from dotenv import load_dotenv
        
        load_dotenv()
        
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        
        bucket_name = os.getenv('S3_BUCKET_NAME', 'audiogen-demo')
        region = os.getenv('AWS_REGION', 'us-east-1')
        
        # Check if bucket already exists
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            print(f"✅ S3 bucket '{bucket_name}' already exists")
            return
        except:
            pass
        
        # Create bucket
        if region == 'us-east-1':
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        
        print(f"✅ S3 bucket '{bucket_name}' created successfully!")
        
    except Exception as e:
        print(f"❌ Failed to create S3 bucket: {e}")

def list_modal_secrets():
    """List existing Modal secrets"""
    print("📋 Listing Modal secrets...")
    
    try:
        result = subprocess.run(["modal", "secret", "list"], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"❌ Failed to list secrets: {result.stderr}")
    
    except Exception as e:
        print(f"❌ Error listing secrets: {e}")

def delete_modal_secrets():
    """Delete Modal secrets"""
    print("🗑️  Deleting Modal secrets...")
    
    secrets_to_delete = ["aws-credentials", "huggingface-token"]
    
    for secret_name in secrets_to_delete:
        try:
            result = subprocess.run(["modal", "secret", "delete", secret_name], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Deleted secret: {secret_name}")
            else:
                print(f"⚠️  Failed to delete {secret_name}: {result.stderr}")
        
        except Exception as e:
            print(f"❌ Error deleting {secret_name}: {e}")

def main():
    """Main function"""
    print("🎵 AudioGen Modal App - Complete Setup")
    print("=" * 50)
    
    choice = input("What would you like to do?\n1. Setup AWS credentials\n2. Create Modal secrets\n3. Test AWS credentials\n4. Create S3 bucket\n5. List Modal secrets\n6. Delete Modal secrets\n7. Exit\nChoice (1-7): ").strip()
    
    if choice == "1":
        setup_aws_credentials()
    elif choice == "2":
        create_modal_secrets()
    elif choice == "3":
        test_aws_credentials()
    elif choice == "4":
        create_s3_bucket()
    elif choice == "5":
        list_modal_secrets()
    elif choice == "6":
        delete_modal_secrets()
    elif choice == "7":
        print("👋 Goodbye!")
        return
    else:
        print("❌ Invalid choice")
        return
    
    print("\n🎉 Setup complete!")
    print("💡 You can now run: python3 test_modal.py")

if __name__ == "__main__":
    main() 