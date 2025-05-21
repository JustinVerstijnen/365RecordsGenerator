import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="/", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def m365_dns_generator(req: func.HttpRequest) -> func.HttpResponse:
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Microsoft 365 DNS Generator</title>
        <style>
            body {
                font-family: 'Segoe UI', sans-serif;
                background: #f4f6f8;
                padding: 2em;
                max-width: 900px;
                margin: auto;
            }
            h2 {
                color: #333;
                text-align: center;
            }
            input, button {
                padding: 0.6em;
                font-size: 1em;
                margin: 0.5em 0;
                border: 1px solid #ccc;
                border-radius: 4px;
                width: 100%;
                box-sizing: border-box;
            }
            button {
                background-color: #88B0DC;
                color: white;
                cursor: pointer;
            }
            button:hover {
                background-color: #005A9E;
            }
            .section {
                background: white;
                padding: 1.5em;
                border-radius: 8px;
                margin-top: 2em;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            pre {
                background: #eef;
                padding: 1em;
                border-radius: 6px;
                white-space: pre-wrap;
            }
            .logo {
                text-align: center;
                margin-bottom: 1em;
            }
        </style>
    </head>
    <body>
        <div class="logo">
            <a href="https://justinverstijnen.nl" target="_blank">
                <img src="https://justinverstijnen.nl/wp-content/uploads/2025/04/cropped-Logo-2.0-Transparant.png" alt="Logo" style="height:50px;" />
            </a>
        </div>

        <h2>Microsoft 365 DNS Record Generator</h2>
        <p style="text-align:center;">Vul hieronder je domeinnaam en M365 tenant in, en alle benodigde records worden gegenereerd.</p>

        <div class="section">
            <label>Domeinnaam (bijv. voorbeeld.nl):</label>
            <input type="text" id="domain" placeholder="example.nl" />

            <label>Microsoft 365 Tenant (bijv. justinverstijnen of justinverstijnen.onmicrosoft.com):</label>
            <input type="text" id="tenant" placeholder="justinverstijnen" />

            <button onclick="generate()">Genereer DNS-records</button>

            <pre id="output"></pre>
        </div>

        <script>
            function generate() {
                const domainInput = document.getElementById("domain").value.trim();
                let tenantInput = document.getElementById("tenant").value.trim();

                if (!domainInput || !tenantInput) {
                    alert("Vul zowel domeinnaam als tenantnaam in.");
                    return;
                }

                const domainClean = domainInput.replace(/\\./g, "-");
                if (!tenantInput.endsWith(".onmicrosoft.com")) {
                    tenantInput += ".onmicrosoft.com";
                }

                const mx = `@                       ${domainClean}.mail.protection.outlook.com`;
                const spf = `@                       v=spf1 include:spf.protection.outlook.com -all`;
                const dmarc = `_dmarc                  v=DMARC1; p=quarantine;`;
                const cname1 = `autodiscover            autodiscover.outlook.com`;
                const dkim1 = `selector1._domainkey    selector1-${domainClean}._domainkey.${tenantInput}`;
                const dkim2 = `selector2._domainkey    selector2-${domainClean}._domainkey.${tenantInput}`;

                const output = `
De volgende DNS-records moeten worden aangemaakt:

----------------------------------------
MX-record
${mx}
----------------------------------------
TXT-records
${spf}
${dmarc}
----------------------------------------
CNAME-records
${cname1}
${dkim1}
${dkim2}
----------------------------------------
TTL: 3600 seconden (of gebruik de provider-standaard)
Controleer ook het Microsoft 365 admin center voor de verificatie-record.
✅ Succes!
                `.trim();

                document.getElementById("output").innerText = output;
            }
        </script>
    </body>
    </html>
    """
    return func.HttpResponse(html, mimetype="text/html")
