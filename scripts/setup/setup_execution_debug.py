"""
Debug script để log chi tiết workflow execution từ frontend
"""
import json
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Log all execution requests to file
def log_execution_request(data):
    with open("d:/EmbeddedChat/frontend_execution_debug.log", "a", encoding="utf-8") as f:
        f.write(f"\n{'='*50}\n")
        f.write(f"EXECUTION REQUEST: {json.dumps(data, indent=2, ensure_ascii=False)}\n")
        f.write(f"{'='*50}\n")

if __name__ == "__main__":
    print("🔍 Tạo file log để debug execution từ frontend...")
    
    # Clear existing log
    with open("d:/EmbeddedChat/frontend_execution_debug.log", "w", encoding="utf-8") as f:
        f.write("FRONTEND EXECUTION DEBUG LOG\n")
        f.write("="*50 + "\n")
    
    print("✅ File log đã sẵn sàng tại: d:/EmbeddedChat/frontend_execution_debug.log")
    print("📝 Bây giờ hãy execute workflow từ frontend và kiểm tra log!")
