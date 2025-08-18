#!/usr/bin/env python3
"""
Quick test script để verify compatibility của requirements.txt
"""

import subprocess
import sys
import tempfile
import os

def test_install():
    """Test install requirements trong temp environment"""
    print("🧪 Testing requirements.txt compatibility...")
    
    # Tạo temp directory
    with tempfile.TemporaryDirectory() as temp_dir:
        venv_path = os.path.join(temp_dir, "test_env")
        
        # Tạo virtual environment
        print("📦 Creating test virtual environment...")
        result = subprocess.run([sys.executable, "-m", "venv", venv_path], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Failed to create venv: {result.stderr}")
            return False
        
        # Get pip path
        if os.name == 'nt':  # Windows
            pip_path = os.path.join(venv_path, "Scripts", "pip.exe")
        else:  # Unix/Linux/Mac
            pip_path = os.path.join(venv_path, "bin", "pip")
        
        # Upgrade pip
        print("🔄 Upgrading pip...")
        result = subprocess.run([pip_path, "install", "--upgrade", "pip"], 
                              capture_output=True, text=True)
        
        # Install requirements
        print("📋 Installing requirements.txt...")
        result = subprocess.run([pip_path, "install", "-r", "requirements.txt"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Requirements.txt installed successfully!")
            print("🎉 All dependencies are compatible!")
            return True
        else:
            print("❌ Requirements installation failed:")
            print(result.stderr)
            return False

def main():
    """Main test function"""
    print("🔬 Python Requirements Compatibility Test")
    print("=" * 50)
    
    if test_install():
        print("\n🎉 SUCCESS: Requirements.txt is compatible!")
        print("🚀 Ready to deploy to Railway!")
        return True
    else:
        print("\n❌ FAILED: Requirements.txt has conflicts!")
        print("💡 Please fix the dependency conflicts before deploying")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
