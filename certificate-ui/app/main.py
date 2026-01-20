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
    html_content = """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Certificate Manager</title>
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div id="root"></div>
    <script>
        const { createElement: h } = React;
        const { useState, useEffect } = React;

        function CertificateUI() {
            const [certificates, setCertificates] = useState([]);
            const [loading, setLoading] = useState(true);
            const [renewing, setRenewing] = useState(null);
            const [error, setError] = useState(null);

            const API_BASE = window.location.origin;

            const fetchCertificates = async () => {
                try {
                    setLoading(true);
                    setError(null);
                    const response = await fetch(`${API_BASE}/certificates`);
                    if (!response.ok) throw new Error('Failed to fetch certificates');
                    const data = await response.json();
                    setCertificates(data);
                } catch (err) {
                    setError(err.message);
                } finally {
                    setLoading(false);
                }
            };

            const renewCertificate = async (certId) => {
                try {
                    setRenewing(certId);
                    setError(null);
                    const response = await fetch(`${API_BASE}/renew/${certId}`, { method: 'POST' });
                    if (!response.ok) throw new Error('Failed to renew certificate');
                    await fetchCertificates();
                } catch (err) {
                    setError(err.message);
                } finally {
                    setRenewing(null);
                }
            };

            useEffect(() => { fetchCertificates(); }, []);

            const getStatusColor = (status) => {
                const s = status?.toLowerCase();
                if (s === 'active') return 'bg-green-100 text-green-800';
                if (s === 'renewed') return 'bg-blue-100 text-blue-800';
                if (s === 'expiring') return 'bg-yellow-100 text-yellow-800';
                if (s === 'expired') return 'bg-red-100 text-red-800';
                return 'bg-gray-100 text-gray-800';
            };

            const Icon = (name, props = {}) => {
                const icons = lucide;
                return h(icons[name], { ...props, size: props.size || 16 });
            };

            return h('div', { className: 'min-h-screen bg-gradient-to-br from-slate-50 to-slate-100' },
                h('div', { className: 'max-w-6xl mx-auto p-6' },
                    h('div', { className: 'mb-8' },
                        h('div', { className: 'flex items-center gap-3 mb-2' },
                            Icon('Shield', { className: 'w-8 h-8 text-blue-600', size: 32 }),
                            h('h1', { className: 'text-3xl font-bold text-slate-800' }, 'Certificate Manager')
                        ),
                        h('p', { className: 'text-slate-600' }, 'Manage and renew your SSL certificates')
                    ),
                    
                    error && h('div', { className: 'mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3' },
                        Icon('AlertCircle', { className: 'w-5 h-5 text-red-600 mt-0.5', size: 20 }),
                        h('div', null,
                            h('p', { className: 'font-semibold text-red-800' }, 'Error'),
                            h('p', { className: 'text-red-700 text-sm' }, error)
                        )
                    ),

                    h('div', { className: 'mb-6 flex justify-end' },
                        h('button', {
                            onClick: fetchCertificates,
                            disabled: loading,
                            className: 'flex items-center gap-2 px-4 py-2 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors disabled:opacity-50'
                        },
                            Icon('RefreshCw', { className: `w-4 h-4 ${loading ? 'animate-spin' : ''}` }),
                            'Refresh'
                        )
                    ),

                    loading && certificates.length === 0 ? h('div', { className: 'text-center py-12' },
                        Icon('RefreshCw', { className: 'w-8 h-8 animate-spin mx-auto text-blue-600 mb-3', size: 32 }),
                        h('p', { className: 'text-slate-600' }, 'Loading certificates...')
                    ) : certificates.length === 0 ? h('div', { className: 'text-center py-12 bg-white rounded-lg shadow-sm' },
                        Icon('Shield', { className: 'w-12 h-12 mx-auto text-slate-300 mb-3', size: 48 }),
                        h('p', { className: 'text-slate-600' }, 'No certificates found')
                    ) : h('div', { className: 'grid gap-4 md:grid-cols-2 lg:grid-cols-3' },
                        certificates.map(cert => h('div', {
                            key: cert.id,
                            className: 'bg-white rounded-lg shadow-sm border border-slate-200 p-5 hover:shadow-md transition-shadow'
                        },
                            h('div', { className: 'flex items-start justify-between mb-4' },
                                h('div', { className: 'flex-1' },
                                    h('h3', { className: 'font-semibold text-slate-800 mb-1' }, cert.domain || cert.name || cert.id),
                                    h('p', { className: 'text-xs text-slate-500 font-mono' }, cert.id)
                                ),
                                h('div', { className: `flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${getStatusColor(cert.status)}` },
                                    cert.status || 'Unknown'
                                )
                            ),
                            h('div', { className: 'space-y-2 mb-4 text-sm' },
                                cert.issuer && h('div', { className: 'flex justify-between' },
                                    h('span', { className: 'text-slate-600' }, 'Issuer:'),
                                    h('span', { className: 'text-slate-800 font-medium' }, cert.issuer)
                                ),
                                cert.expiry && h('div', { className: 'flex justify-between' },
                                    h('span', { className: 'text-slate-600' }, 'Expires:'),
                                    h('span', { className: 'text-slate-800 font-medium' }, cert.expiry)
                                ),
                                cert.created && h('div', { className: 'flex justify-between' },
                                    h('span', { className: 'text-slate-600' }, 'Created:'),
                                    h('span', { className: 'text-slate-800 font-medium' }, cert.created)
                                )
                            ),
                            h('button', {
                                onClick: () => renewCertificate(cert.id),
                                disabled: renewing === cert.id,
                                className: 'w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50'
                            },
                                Icon('RefreshCw', { className: `w-4 h-4 ${renewing === cert.id ? 'animate-spin' : ''}` }),
                                renewing === cert.id ? 'Renewing...' : 'Renew Certificate'
                            )
                        ))
                    )
                )
            );
        }

        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(h(CertificateUI));
    </script>
</body>
</html>"""
    return html_content

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
