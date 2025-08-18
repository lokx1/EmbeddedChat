#!/usr/bin/env python3
"""
Script để migrate data từ local PostgreSQL sang Railway PostgreSQL
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

def run_command(command, description):
    """Chạy command và hiển thị output"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} thành công")
            return result.stdout
        else:
            print(f"❌ {description} thất bại:")
            print(result.stderr)
            return None
    except Exception as e:
        print(f"❌ Lỗi khi {description}: {e}")
        return None

def get_local_db_info():
    """Lấy thông tin database local từ user"""
    print("📋 Nhập thông tin PostgreSQL local:")
    
    host = input("Host (localhost): ").strip() or "localhost"
    port = input("Port (5432): ").strip() or "5432"
    database = input("Database name: ").strip()
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    
    return {
        'host': host,
        'port': port,
        'database': database,
        'username': username,
        'password': password
    }

def export_local_database(db_info):
    """Export database local"""
    # Tạo file backup tạm thời
    backup_file = tempfile.NamedTemporaryFile(suffix='.sql', delete=False)
    backup_file.close()
    
    # Tạo command pg_dump
    pg_dump_cmd = f"pg_dump -h {db_info['host']} -p {db_info['port']} -U {db_info['username']} -d {db_info['database']} -f {backup_file.name}"
    
    # Set password environment variable
    env = os.environ.copy()
    env['PGPASSWORD'] = db_info['password']
    
    print(f"🔄 Exporting database {db_info['database']}...")
    try:
        result = subprocess.run(pg_dump_cmd, shell=True, env=env, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Export thành công: {backup_file.name}")
            return backup_file.name
        else:
            print(f"❌ Export thất bại:")
            print(result.stderr)
            return None
    except Exception as e:
        print(f"❌ Lỗi khi export: {e}")
        return None

def check_railway_cli():
    """Kiểm tra Railway CLI"""
    result = run_command("railway --version", "Kiểm tra Railway CLI")
    return result is not None

def get_railway_db_url():
    """Lấy DATABASE_URL từ Railway"""
    result = run_command("railway variables", "Lấy Railway variables")
    if result:
        for line in result.split('\n'):
            if 'DATABASE_URL' in line:
                return line.split('=')[1].strip()
    return None

def import_to_railway(backup_file):
    """Import data vào Railway PostgreSQL"""
    print("🔄 Importing data vào Railway...")
    
    # SSH vào Railway và import
    import_cmd = f"railway shell -c 'psql $DATABASE_URL < {backup_file}'"
    
    try:
        result = subprocess.run(import_cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Import thành công")
            return True
        else:
            print(f"❌ Import thất bại:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Lỗi khi import: {e}")
        return False

def test_railway_connection():
    """Test kết nối Railway database"""
    test_script = """
import asyncio
import os
from src.models.database import engine

async def test_db():
    try:
        async with engine.begin() as conn:
            result = await conn.execute('SELECT 1')
            print('✅ Railway database connection successful!')
            return True
    except Exception as e:
        print(f'❌ Railway database connection failed: {e}')
        return False

asyncio.run(test_db())
"""
    
    # Tạo file test tạm thời
    test_file = tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w')
    test_file.write(test_script)
    test_file.close()
    
    # Chạy test
    result = run_command(f"python {test_file.name}", "Test Railway database connection")
    
    # Xóa file test
    os.unlink(test_file.name)
    
    return result is not None

def main():
    """Main function"""
    print("🚀 Migration từ Local PostgreSQL sang Railway")
    print("=" * 50)
    
    # Bước 1: Kiểm tra Railway CLI
    if not check_railway_cli():
        print("❌ Railway CLI chưa được cài đặt. Vui lòng cài đặt trước:")
        print("npm install -g @railway/cli")
        return
    
    # Bước 2: Lấy thông tin database local
    db_info = get_local_db_info()
    
    # Bước 3: Export database local
    backup_file = export_local_database(db_info)
    if not backup_file:
        print("❌ Không thể export database local")
        return
    
    # Bước 4: Kiểm tra Railway database URL
    railway_db_url = get_railway_db_url()
    if not railway_db_url:
        print("❌ Không tìm thấy DATABASE_URL trong Railway")
        print("Vui lòng cấu hình DATABASE_URL trước:")
        print("railway variables set DATABASE_URL='your-railway-db-url'")
        return
    
    print(f"📋 Railway DATABASE_URL: {railway_db_url}")
    
    # Bước 5: Import vào Railway
    if import_to_railway(backup_file):
        print("✅ Migration hoàn tất!")
        
        # Bước 6: Test kết nối
        if test_railway_connection():
            print("🎉 Migration thành công! Railway database đã sẵn sàng.")
        else:
            print("⚠️ Migration hoàn tất nhưng có vấn đề với kết nối database.")
    else:
        print("❌ Migration thất bại")
    
    # Xóa file backup
    try:
        os.unlink(backup_file)
        print(f"🗑️ Đã xóa file backup: {backup_file}")
    except:
        pass

if __name__ == "__main__":
    main()
