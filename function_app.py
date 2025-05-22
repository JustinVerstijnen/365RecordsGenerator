import azure.functions as func
import dns.resolver
import dns.dnssec
import dns.name
import dns.message
import dns.query
import dns.rdatatype

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

def is_dnssec_enabled(domain):
    try:
        # Verkrijg DNSKEY van domein
        name = dns.name.from_text(domain)
        response = dns.resolver.resolve(domain, 'DNSKEY', raise_on_no_answer=False)
        return bool(response.rrset)
    except Exception:
        return False

@app.route(route="/", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def main(req: func.HttpRequest) -> func.HttpResponse:
    domain = req.params.get("checkdomain")
    dane_result = ""
    if domain:
        is_dnssec = is_dnssec_enabled(domain)
        dane_result = "DNSSEC is enabled ✅ — DANE can be configured" if is_dnssec else "DNSSEC not found ❌ — DANE not supported"

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>M365 DNS Generator - justinverstijnen.nl</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
        <style>
            body {{
                font-family: 'Segoe UI', sans-serif;
                background: #f4f6f8;
                padding: 2em;
                max-width: 1000px;
                margin: auto;
            }}
            h2 {{
                color: #333;
                text-align: center;
            }}
            input, select, button {{
                padding: 0.6em;
                font-size: 1em;
                margin: 0.4em 0;
                border: 1px solid #ccc;
                border-radius: 4px;
                box-sizing: border-box;
                width: 100%;
            }}
            button {{
                background-color: #003366;
                color: white;
                cursor: pointer;
                border: none;
            }}
            button:hover {{
                background-color: #002244;
            }}
            .export-btn {{
                background-color: #007B00;
                margin-top: 1em;
            }}
            .section {{
                background: white;
                padding: 1.5em;
                border-radius: 8px;
                margin-top: 2em;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 1em;
            }}
            table th, table td {{
                padding: 0.6em;
                border: 1px solid #ddd;
                text-align: left;
                vertical-align: top;
            }}
            table td:nth-child(4) {{
                width: 200px;
                font-size: 0.9em;
            }}
            .greyed {{
                color: #888;
                font-style: italic;
            }}
            .copy-btn {{
                width: 25px;
                height: 25px;
                font-size: 0.8em;
                margin-right: 0.5em;
            }}
        </style>
    </head>
    <body>
        <h2>M365 DNS Generator</h2>
        <div class="section">
            <label>Step 1: Domain name</label>
            <input type="text" id="domain" placeholder="example.com">
            <label>Step 2: Microsoft 365 Tenant name</label>
            <input type="text" id="tenant" placeholder="example.onmicrosoft.com">
            <button onclick="generateTable()"><i class="fas fa-cogs"></i> Generate DNS records</button>
            <div id="output"></div>
            <button class="export-btn" onclick="downloadPDF()"><i class="fas fa-file-pdf"></i> Export to PDF</button>
        </div>

        <script>
            function isValidDomain(domain) {{
                return /^[a-zA-Z0-9.-]+\\.[a-zA-Z]{{2,}}$/.test(domain);
            }}

            function generateTable() {{
                const domain = document.getElementById("domain").value.trim();
                let tenant = document.getElementById("tenant").value.trim();
                if (!domain || !tenant) return alert("Please fill in both fields.");
                if (!isValidDomain(domain) || !isValidDomain(tenant.replace(".onmicrosoft.com", ""))) {{
                    return alert("Please enter valid domain names.");
                }}

                const clean = domain.replace(/\\./g, "-");
                if (!tenant.endsWith(".onmicrosoft.com")) tenant += ".onmicrosoft.com";
                const dkim1 = `selector1-${{clean}}._domainkey.${{tenant}}`;
                const dkim2 = `selector2-${{clean}}._domainkey.${{tenant}}`;

                fetch(`/?checkdomain=${{domain}}`).then(resp => resp.text()).then(html => {{
                    const daneInfo = html.match(/<!--DANE_START-->(.*?)<!--DANE_END-->/s);
                    const daneStatus = daneInfo ? daneInfo[1] : "";

                    const table = `
                    <table id="dns-table">
                        <thead>
                            <tr><th>Configuration</th><th>Type</th><th>Value</th><th>More options</th></tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>MX</td><td>MX</td>
                                <td><button class="copy-btn" onclick="copy('mx')">📋</button><span id="mx">${{clean}}.mail.protection.outlook.com</span></td>
                                <td></td>
                            </tr>
                            <tr>
                                <td>SPF</td><td>TXT</td>
                                <td><button class="copy-btn" onclick="copy('spf')">📋</button><span id="spf">v=spf1 include:spf.protection.outlook.com -all</span></td>
                                <td>
                                    <select id="spf-policy" onchange="updateSPF()">
                                        <option value="-all" selected>Hardfail (-all)</option>
                                        <option value="~all">Softfail (~all)</option>
                                    </select>
                                </td>
                            </tr>
                            <tr>
                                <td>DKIM</td><td>CNAME</td>
                                <td><button class="copy-btn" onclick="copy('dkim1')">📋</button><span id="dkim1">${{dkim1}}</span></td>
                                <td></td>
                            </tr>
                            <tr>
                                <td>DKIM</td><td>CNAME</td>
                                <td><button class="copy-btn" onclick="copy('dkim2')">📋</button><span id="dkim2">${{dkim2}}</span></td>
                                <td></td>
                            </tr>
                            <tr>
                                <td>DMARC</td><td>TXT</td>
                                <td><button class="copy-btn" onclick="copy('dmarc')">📋</button><span id="dmarc">v=DMARC1; p=reject</span></td>
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
                                <td><button class="copy-btn" onclick="copy('mta-sts')">📋</button><span id="mta-sts">v=STS;</span></td>
                                <td>
                                    ID: <input type="date" id="mta-date" onchange="updateMTASTS()"><br/>
                                    RUA: <input id="mta-rua" type="email" oninput="updateMTASTS()" placeholder="rua@...">
                                </td>
                            </tr>
                            <tr>
                                <td>SMTP DANE</td><td>TLSA</td>
                                <td colspan="2">{dane_result}</td>
                            </tr>
                        </tbody>
                    </table>`;
                    document.getElementById("output").innerHTML = table;
                }});
            }}

            function updateSPF() {{
                const pol = document.getElementById("spf-policy").value;
                document.getElementById("spf").innerText = `v=spf1 include:spf.protection.outlook.com ${{pol}}`;
            }}

            function updateDMARC() {{
                const p = document.getElementById("dmarc-policy").value;
                const rua = document.getElementById("rua").value;
                const ruf = document.getElementById("ruf").value;
                let r = `v=DMARC1; p=${{p}}`;
                if (rua) r += `; rua=mailto:${{rua}}`;
                if (ruf) r += `; ruf=mailto:${{ruf}}`;
                document.getElementById("dmarc").innerText = r;
            }}

            function updateMTASTS() {{
                const date = document.getElementById("mta-date").value;
                const rua = document.getElementById("mta-rua").value;
                let r = "v=STS;";
                if (date) r += ` id=${{date.replace(/-/g,"")}}000000Z`;
                if (rua) r += `; rua=mailto:${{rua}}`;
                document.getElementById("mta-sts").innerText = r;
            }}

            function copy(id) {{
                const val = document.getElementById(id).innerText;
                navigator.clipboard.writeText(val).then(() => alert("Copied: " + val));
            }}

            function downloadPDF() {{
                const {{ jsPDF }} = window.jspdf;
                const doc = new jsPDF();
                const table = document.getElementById("dns-table");
                if (!table) return alert("Please generate the table first.");
                doc.text("Microsoft 365 DNS Records", 14, 14);
                doc.autoTable({ html: "#dns-table", startY: 20 });
                doc.save("M365-DNS-records.pdf");
            }}
        </script>
        <!--DANE_START-->{dane_result}<!--DANE_END-->
    </body>
    </html>
    """
    return func.HttpResponse(html, mimetype="text/html")
