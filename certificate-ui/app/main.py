from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
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
async def index():
    html = """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Certificate Manager</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gradient-to-br from-slate-50 to-slate-100 min-h-screen">
    <div class="max-w-6xl mx-auto p-6">
        <div class="mb-8">
            <div class="flex items-center gap-3 mb-2">
                <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
                </svg>
                <h1 class="text-3xl font-bold text-slate-800">Certificate Manager</h1>
            </div>
            <p class="text-slate-600">Manage and renew your SSL certificates</p>
        </div>

        <div id="error-message" class="hidden mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p class="font-semibold text-red-800">Error</p>
            <p id="error-text" class="text-red-700 text-sm"></p>
        </div>

        <div class="mb-6 flex justify-end">
            <button onclick="loadCertificates()" class="flex items-center gap-2 px-4 py-2 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
                Refresh
            </button>
        </div>

        <div id="loading" class="text-center py-12">
            <svg class="w-8 h-8 animate-spin mx-auto text-blue-600 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            <p class="text-slate-600">Loading certificates...</p>
        </div>

        <div id="empty-state" class="hidden text-center py-12 bg-white rounded-lg shadow-sm">
            <svg class="w-12 h-12 mx-auto text-slate-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
            </svg>
            <p class="text-slate-600">No certificates found</p>
        </div>

        <div id="certificates-grid" class="hidden grid gap-4 md:grid-cols-2 lg:grid-cols-3"></div>
    </div>

    <script>
        const API_BASE = window.location.origin;

        function showError(message) {
            document.getElementById('error-message').classList.remove('hidden');
            document.getElementById('error-text').textContent = message;
        }

        function hideError() {
            document.getElementById('error-message').classList.add('hidden');
        }

        function getStatusColor(status) {
            const s = status?.toLowerCase();
            if (s === 'active') return 'bg-green-100 text-green-800';
            if (s === 'renewed') return 'bg-blue-100 text-blue-800';
            if (s === 'expiring') return 'bg-yellow-100 text-yellow-800';
            if (s === 'expired') return 'bg-red-100 text-red-800';
            return 'bg-gray-100 text-gray-800';
        }

        function createCertificateCard(cert) {
            return `
                <div class="bg-white rounded-lg shadow-sm border border-slate-200 p-5 hover:shadow-md transition-shadow">
                    <div class="flex items-start justify-between mb-4">
                        <div class="flex-1">
                            <h3 class="font-semibold text-slate-800 mb-1">${cert.domain || cert.name || cert.id}</h3>
                            <p class="text-xs text-slate-500 font-mono">${cert.id}</p>
                        </div>
                        <div class="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${getStatusColor(cert.status)}">
                            ${cert.status || 'Unknown'}
                        </div>
                    </div>
                    
                    <div class="space-y-2 mb-4 text-sm">
                        ${cert.issuer ? `
                            <div class="flex justify-between">
                                <span class="text-slate-600">Issuer:</span>
                                <span class="text-slate-800 font-medium">${cert.issuer}</span>
                            </div>
                        ` : ''}
                        ${cert.expiry ? `
                            <div class="flex justify-between">
                                <span class="text-slate-600">Expires:</span>
                                <span class="text-slate-800 font-medium">${cert.expiry}</span>
                            </div>
                        ` : ''}
                        ${cert.created ? `
                            <div class="flex justify-between">
                                <span class="text-slate-600">Created:</span>
                                <span class="text-slate-800 font-medium">${cert.created}</span>
                            </div>
                        ` : ''}
                    </div>
                    
                    <button 
                        onclick="renewCertificate('${cert.id}')" 
                        class="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                        </svg>
                        Renew Certificate
                    </button>
                </div>
            `;
        }

        async function loadCertificates() {
            try {
                hideError();
                document.getElementById('loading').classList.remove('hidden');
                document.getElementById('empty-state').classList.add('hidden');
                document.getElementById('certificates-grid').classList.add('hidden');

                const response = await fetch(`${API_BASE}/certificates`);
                if (!response.ok) throw new Error('Failed to fetch certificates');
                
                const certificates = await response.json();
                
                document.getElementById('loading').classList.add('hidden');

                if (certificates.length === 0) {
                    document.getElementById('empty-state').classList.remove('hidden');
                } else {
                    const grid = document.getElementById('certificates-grid');
                    grid.innerHTML = certificates.map(cert => createCertificateCard(cert)).join('');
                    grid.classList.remove('hidden');
                }
            } catch (error) {
                document.getElementById('loading').classList.add('hidden');
                showError(error.message);
            }
        }

        async function renewCertificate(certId) {
            try {
                hideError();
                const response = await fetch(`${API_BASE}/renew/${certId}`, {
                    method: 'POST'
                });
                
                if (!response.ok) throw new Error('Failed to renew certificate');
                
                await loadCertificates();
            } catch (error) {
                showError(error.message);
            }
        }

        loadCertificates();
    </script>
</body>
</html>"""
    return html

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
