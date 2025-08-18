#!/usr/bin/env python3
"""
Script để solve dependencies conflicts một cách tự động
"""

import subprocess
import sys
import os
import tempfile
from pathlib import Path

def run_command(command, description, cwd=None):
    """Chạy command và return output"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            cwd=cwd
        )
        if result.returncode == 0:
            print(f"✅ {description} thành công")
            return result.stdout, True
        else:
            print(f"❌ {description} thất bại:")
            print(result.stderr)
            return result.stderr, False
    except Exception as e:
        print(f"❌ Lỗi khi {description}: {e}")
        return str(e), False

def install_pip_tools():
    """Install pip-tools if not available"""
    _, success = run_command("pip install pip-tools", "Installing pip-tools")
    return success

def compile_requirements():
    """Compile requirements.in to requirements.txt"""
    _, success = run_command("pip-compile requirements.in", "Compiling requirements.in")
    return success

def test_requirements(requirements_file):
    """Test requirements in isolated environment"""
    # Tạo temp directory
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📦 Testing {requirements_file} in isolated environment...")
        
        # Tạo virtual environment
        venv_path = os.path.join(temp_dir, "test_env")
        _, success = run_command(f"python -m venv {venv_path}", "Creating test venv")
        if not success:
            return False
        
        # Activate venv và test install
        if os.name == 'nt':  # Windows
            pip_path = os.path.join(venv_path, "Scripts", "pip")
        else:  # Unix/Linux/Mac
            pip_path = os.path.join(venv_path, "bin", "pip")
        
        _, success = run_command(f"{pip_path} install -r {requirements_file}", f"Installing {requirements_file}")
        return success

def create_minimal_working_version():
    """Tạo version minimal đảm bảo hoạt động"""
    minimal_requirements = """# Minimal working requirements
fastapi>=0.100.0,<0.115.0
uvicorn[standard]>=0.20.0,<0.26.0
sqlalchemy>=2.0.0,<2.1.0
alembic>=1.13.0,<1.14.0
asyncpg>=0.28.0,<0.30.0
pydantic>=2.5.0,<2.7.0
pydantic-settings>=2.1.0,<2.2.0
python-dotenv>=1.0.0,<2.0.0
python-jose[cryptography]>=3.3.0,<4.0.0
passlib[bcrypt]>=1.7.0,<2.0.0
python-multipart>=0.0.6,<0.1.0
aiofiles>=23.0.0,<24.0.0
httpx>=0.25.0,<0.27.0
email-validator>=2.0.0,<3.0.0
redis>=5.0.0,<6.0.0
pytest>=7.4.0,<8.0.0
pytest-asyncio>=0.23.0,<0.24.0
aiosqlite>=0.19.0,<0.20.0"""
    
    with open("requirements-minimal-working.txt", "w") as f:
        f.write(minimal_requirements)
    
    return test_requirements("requirements-minimal-working.txt")

def solve_ai_providers():
    """Solve AI providers dependencies separately"""
    ai_requirements = """# AI Providers only
openai>=1.0.0,<2.0.0
anthropic>=0.30.0,<1.0.0
httpx>=0.25.0,<0.28.0"""
    
    with open("requirements-ai.txt", "w") as f:
        f.write(ai_requirements)
    
    return test_requirements("requirements-ai.txt")

def main():
    """Main solving process"""
    print("🔬 Python Dependency Conflict Solver")
    print("=" * 50)
    
    # Step 1: Install pip-tools
    if not install_pip_tools():
        print("❌ Không thể install pip-tools")
        return False
    
    # Step 2: Try compiling requirements.in
    print("\n📋 Step 1: Compiling requirements.in với pip-tools...")
    if compile_requirements():
        print("✅ pip-tools compile thành công!")
        if test_requirements("requirements.txt"):
            print("🎉 Requirements.txt generated và test thành công!")
            return True
        else:
            print("⚠️ Requirements.txt generated nhưng test thất bại")
    
    # Step 3: Create minimal working version
    print("\n📋 Step 2: Tạo minimal working version...")
    if create_minimal_working_version():
        print("✅ Minimal working version thành công!")
        # Copy to main requirements.txt
        with open("requirements-minimal-working.txt", "r") as f:
            content = f.read()
        with open("requirements.txt", "w") as f:
            f.write(content)
        print("📄 Đã update requirements.txt với minimal working version")
        return True
    
    # Step 4: Solve AI providers separately
    print("\n📋 Step 3: Solving AI providers separately...")
    if solve_ai_providers():
        print("✅ AI providers dependencies solved!")
        print("💡 Cài đặt AI providers riêng sau khi deploy base app")
    
    return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Dependencies resolved successfully!")
        print("📝 File requirements.txt đã được update")
        print("🚀 Có thể deploy lên Railway ngay!")
    else:
        print("\n❌ Không thể resolve all dependencies")
        print("💡 Sử dụng requirements-core.txt để deploy minimal version")
