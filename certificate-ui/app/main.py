from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import json
import os

app = FastAPI(title="Certificate Automation UI")

CERT_FILE = os.getenv("CERT_FILE", "/app/certs.json")

def read_certs():
    if os.path.exists(CERT_FILE):
        with open(CERT_FILE) as f:
            return json.load(f)
    return []

def write_certs(data):
    with open(CERT_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Certificate Manager</title>
        <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
        <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body>
        <div id="root"></div>
        <script type="module">
            import { RefreshCw, CheckCircle, AlertCircle, Clock, Shield } from 'https://cdn.jsdelivr.net/npm/lucide-react@0.263.1/+esm';
            
            // React component kodu buraya gelecek
        </script>
    </body>
    </html>
    """

@app.get("/certificates")
def list_certificates():
    return read_certs()

@app.post("/renew/{cert_id}")
def renew_certificate(cert_id: str):
    certs = read_certs()
    for cert in certs:
        if cert["id"] == cert_id:
            cert["status"] = "renewed"
            write_certs(certs)
            return {"message": f"Certificate {cert_id} renewed"}
    raise HTTPException(status_code=404, detail="Certificate not found")
