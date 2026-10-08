import uvicorn
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

BACKEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print("=" * 65)
    print("       ChronoCTI Web API & Attack Flow Graph Server")
    print(f"       Web Dashboard : http://localhost:{port}/")
    print(f"      API Swagger UI: http://localhost:{port}/docs")
    print("=" * 65)
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True, app_dir=BACKEND_DIR)
