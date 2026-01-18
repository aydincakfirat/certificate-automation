from fastapi import FastAPI, HTTPException
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
