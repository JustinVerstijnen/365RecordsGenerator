import json
import dns.resolver
import dns.exception
import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="/", methods=["GET"])
def main(req: func.HttpRequest) -> func.HttpResponse:
    html = """
    <!DOCTYPE html>
    <html lang="nl">
    <head>
        <meta charset="UTF-8">
        <title>M365 DNS Generator - justinverstijnen.nl</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.5.28/jspdf.plugin.autotable.min.js"></script>
        <style>
            body {
                font-family: 'Segoe UI', sans-serif;
                background: #f4f6f8;
                padding: 2em;
                max-width: 1000px;
                margin: auto;
            }
            h2 {
                color: #333;
                text-align: center;
            }
            input, select, button {
                padding: 0.6em;
                font-size: 1em;
                margin: 0.4em 0;
                border: 1px solid #ccc;
                border-radius: 4px;
                box-sizing: border-box;
            }
            button {
                background-color: #005A9E;
                color: white;
                cursor: pointer;
                border: none;
            }
            button:hover {
                background-color: #003f6d;
            }
            .export-btn {
                background-color: #4CAF50;
                margin-top: 1em;
            }
            .section {
                background: white;
                padding: 1.5em;
                border-radius: 8px;
                margin-top: 2em;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 1em;
            }
            table th, table td {
                padding: 0.6em;
                border: 1px solid #ddd;
                text-align: left;
                vertical-align: top;
            }
            .greyed {
                color: #888;
                font-style: italic;
            }
        </style>
    </head>
    <body>
        <h2>M365 DNS Generator</h2>
        <div class="section">
            <label>Step 1 :Domain</label>
            <input type="text" id="domain" placeholder="example.com">
            <label>Step 2: Microsoft 365 Tenant name:</label>
            <input type="text" id="tenant" placeholder="example.onmicrosoft.com">
            <button onclick="generateTable()"><i class="fas fa-cogs"></i> Generate DNS-records</button>
            <div id="output"></div>
            <button class="export-btn" onclick="downloadPDF()"><i class="fas fa-file-pdf"></i> Export to PDF</button>
        </div>

        <script>
            function generateTable() {
                const domain = document.getElementById("domain").value.trim();
                let tenant = document.getElementById("tenant").value.trim();
                if (!domain || !tenant) return alert("Fill in both field to get correct records.");
                const clean = domain.replace(/\\./g, "-");
                if (!tenant.endsWith(".onmicrosoft.com")) tenant += ".onmicrosoft.com";
                const dkim1 = `selector1-${clean}._domainkey.${tenant}`;
                const dkim2 = `selector2-${clean}._domainkey.${tenant}`;

                const table = `
                <table id="dns-table">
                    <thead>
                        <tr><th>Configuration</th><th>Type</th><th>Value</th><th>More options</th></tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>MX</td><td>MX</td>
                            <td><span id="mx">${clean}.mail.protection.outlook.com</span> <button onclick="copy('mx')">📋</button></td>
                            <td></td>
                        </tr>
                        <tr>
                            <td>SPF</td><td>TXT</td>
                            <td><span id="spf">v=spf1 include:spf.protection.outlook.com -all</span> <button onclick="copy('spf')">📋</button></td>
                            <td>
                                <select id="spf-policy" onchange="updateSPF()">
                                    <option value="-all" selected>Hardfail (-all)</option>
                                    <option value="~all">Softfail (~all)</option>
                                </select>
                            </td>
                        </tr>
                        <tr>
                            <td>DKIM</td><td>CNAME</td>
                            <td><span id="dkim1">${dkim1}</span> <button onclick="copy('dkim1')">📋</button></td>
                            <td></td>
                        </tr>
                        <tr>
                            <td>DKIM</td><td>CNAME</td>
                            <td><span id="dkim2">${dkim2}</span> <button onclick="copy('dkim2')">📋</button></td>
                            <td></td>
                        </tr>
                        <tr>
                            <td>DMARC</td><td>TXT</td>
                            <td><span id="dmarc">v=DMARC1; p=reject</span> <button onclick="copy('dmarc')">📋</button></td>
                            <td>
                                <select id="dmarc-policy" onchange="updateDMARC()">
                                    <option value="none">none</option>
                                    <option value="quarantine">quarantine</option>
                                    <option value="reject" selected>reject</option>
                                </select><br/>
                                RUA: <input id="rua" type="email" oninput="updateDMARC()" placeholder="rua@..."><br/>
                                RUF: <input id="ruf" type="email" oninput="updateDMARC()" placeholder="ruf@...">
                            </td>
                        </tr>
                        <tr>
                            <td>MTA-STS</td><td>TXT</td>
                            <td><span id="mta-sts">v=STS;</span> <button onclick="copy('mta-sts')">📋</button></td>
                            <td>
                                Datum-ID: <input type="date" id="mta-date" onchange="updateMTASTS()"><br/>
                                RUA: <input id="mta-rua" type="email" oninput="updateMTASTS()" placeholder="rua@...">
                            </td>
                        </tr>
                        <tr>
                            <td>SMTP DANE / DNSSEC</td><td>TLSA</td>
                            <td id="dnssec-status"><em>Bezig met controleren...</em></td>
                            <td class="greyed">Automatische controle op DNSSEC en DS-record</td>
                        </tr>
                    </tbody>
                </table>`;
                document.getElementById("output").innerHTML = table;
                updateDNSSEC(domain);
            }

            function updateSPF() {
                const pol = document.getElementById("spf-policy").value;
                document.getElementById("spf").innerText = `v=spf1 include:spf.protection.outlook.com ${pol}`;
            }

            function updateDMARC() {
                const p = document.getElementById("dmarc-policy").value;
                const rua = document.getElementById("rua").value;
                const ruf = document.getElementById("ruf").value;
                let r = `v=DMARC1; p=${p}`;
                if (rua) r += `; rua=mailto:${rua}`;
                if (ruf) r += `; ruf=mailto:${ruf}`;
                document.getElementById("dmarc").innerText = r;
            }

            function updateMTASTS() {
                const date = document.getElementById("mta-date").value;
                const rua = document.getElementById("mta-rua").value;
                let r = "v=STS;";
                if (date) r += ` id=${date.replace(/-/g,"")}000000Z`;
                if (rua) r += `; rua=mailto:${rua}`;
                document.getElementById("mta-sts").innerText = r;
            }

            function copy(id) {
                const val = document.getElementById(id).innerText;
                navigator.clipboard.writeText(val).then(() => alert("Gekopieerd: " + val));
            }

            function downloadPDF() {
                const { jsPDF } = window.jspdf;
                const doc = new jsPDF();
                doc.text("Microsoft 365 DNS Records", 14, 14);
                const table = document.getElementById("dns-table");
                if (!table) return alert("Genereer eerst een tabel.");
                doc.autoTable({ html: "#dns-table", startY: 20 });
                doc.save("M365-DNS-records.pdf");
            }

            function updateDNSSEC(domain) {
                fetch(`/api/dnssec-check?domain=${domain}`)
                    .then(response => response.json())
                    .then(data => {
                        const output = document.getElementById("dnssec-status");
                        if (data.dnssec && data.ds) {
                            output.innerHTML = "✅ DNSSEC actief + DS-record aanwezig";
                        } else if (data.dnssec) {
                            output.innerHTML = "⚠️ DNSSEC actief, maar geen DS-record";
                        } else {
                            output.innerHTML = "❌ Geen DNSSEC gedetecteerd";
                        }
                    })
                    .catch(error => {
                        document.getElementById("dnssec-status").innerHTML = "❌ Fout bij ophalen DNSSEC status";
                        console.error("DNSSEC check error:", error);
                    });
            }
        </script>
    </body>
    </html>
    """
    return func.HttpResponse(html, mimetype="text/html")

@app.route(route="/dnssec-check", methods=["GET"])
def dnssec_check(req: func.HttpRequest) -> func.HttpResponse:
    domain = req.params.get("domain")
    if not domain:
        return func.HttpResponse(json.dumps({"error": "Domein vereist"}), status_code=400, mimetype="application/json")

    try:
        dnskey_response = dns.resolver.resolve(domain, 'DNSKEY', raise_on_no_answer=False)
        has_dnskey = bool(dnskey_response.rrset)

        ds_response = dns.resolver.resolve(domain, 'DS', raise_on_no_answer=False)
        has_ds = bool(ds_response.rrset)

        result = {
            "dnssec": has_dnskey,
            "ds": has_ds
        }
        return func.HttpResponse(json.dumps(result), mimetype="application/json")
    except dns.resolver.NoNameservers:
        return func.HttpResponse(json.dumps({"error": "Geen geldige nameservers of fout bij resolutie"}), status_code=500, mimetype="application/json")
    except dns.resolver.NXDOMAIN:
        return func.HttpResponse(json.dumps({"error": "Domein bestaat niet"}), status_code=404, mimetype="application/json")
    except dns.exception.DNSException as e:
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500, mimetype="application/json")
