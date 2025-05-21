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
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 1em;
            }
            th, td {
                border: 1px solid #ccc;
                padding: 0.6em;
                text-align: left;
            }
            th {
                background-color: #f0f0f0;
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
        <p style="text-align:center;">Vul hieronder je domeinnaam en M365 tenant in, en alle benodigde records worden weergegeven in een tabel.</p>

        <div class="section">
            <label>Domeinnaam (bijv. voorbeeld.nl):</label>
            <input type="text" id="domain" placeholder="example.nl" />

            <label>Microsoft 365 Tenant (bijv. justinverstijnen of justinverstijnen.onmicrosoft.com):</label>
            <input type="text" id="tenant" placeholder="justinverstijnen" />

            <button onclick="generate()">Genereer DNS-records</button>

            <div id="output"></div>
        </div>

        <script>
            function generate() {
                const domain = document.getElementById("domain").value.trim();
                let tenant = document.getElementById("tenant").value.trim();

                if (!domain || !tenant) {
                    alert("Vul zowel domeinnaam als tenantnaam in.");
                    return;
                }

                const domainClean = domain.replace(/\\./g, "-");
                if (!tenant.endsWith(".onmicrosoft.com")) {
                    tenant += ".onmicrosoft.com";
                }

                const records = [
                    { techniek: "Microsoft 365", record: "@ (MX)", extra: `${domainClean}.mail.protection.outlook.com` },
                    { techniek: "Microsoft 365", record: "@ (TXT - SPF)", extra: `v=spf1 include:spf.protection.outlook.com -all` },
                    { techniek: "Microsoft 365", record: "_dmarc (TXT)", extra: `v=DMARC1; p=quarantine;` },
                    { techniek: "Microsoft 365", record: "autodiscover (CNAME)", extra: `autodiscover.outlook.com` },
                    { techniek: "Microsoft 365", record: "selector1._domainkey (CNAME)", extra: `selector1-${domainClean}._domainkey.${tenant}` },
                    { techniek: "Microsoft 365", record: "selector2._domainkey (CNAME)", extra: `selector2-${domainClean}._domainkey.${tenant}` },
                ];

                let tableHTML = `
                    <table>
                        <thead>
                            <tr>
                                <th>Techniek</th>
                                <th>Aan te maken record</th>
                                <th>Extra opties</th>
                            </tr>
                        </thead>
                        <tbody>
                `;

                records.forEach(rec => {
                    tableHTML += `
                        <tr>
                            <td>${rec.techniek}</td>
                            <td>${rec.record}</td>
                            <td>${rec.extra}</td>
                        </tr>
                    `;
                });

                tableHTML += `
                        </tbody>
                    </table>
                    <p><strong>TTL:</strong> 3600 seconden (of gebruik provider-standaard).<br>
                    Controleer ook het Microsoft 365 admin center voor aanvullende verificatie-records.</p>
                `;

                document.getElementById("output").innerHTML = tableHTML;
            }
        </script>
    </body>
    </html>
    """
    return func.HttpResponse(html, mimetype="text/html")
