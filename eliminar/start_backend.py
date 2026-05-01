#!/usr/bin/env python3
import subprocess
import time
import sys
import requests

# Start backend
print("🚀 Starting backend server...")
process = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"],
    cwd=sys.path[0],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    universal_newlines=True
)

# Wait for server to be ready
max_retries = 20
for i in range(max_retries):
    try:
        response = requests.get("http://localhost:8000/docs", timeout=2)
        if response.status_code == 200:
            print("✅ Server is ready!")
            break
    except:
        print(f"  Waiting... ({i+1}/{max_retries})")
        time.sleep(1)
else:
    print("❌ Server failed to start")
    sys.exit(1)

# Keep the process running
print("\n✅ Backend running on http://127.0.0.1:8000")
print("Press Ctrl+C to stop...\n")
process.wait()
