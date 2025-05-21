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
                max-width: 1000px;
                margin: auto;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 2em;
            }
            th, td {
                border: 1px solid #ccc;
                padding: 0.6em;
                text-align: left;
            }
            th {
                background-color: #e0e0e0;
            }
            input, select {
                width: 100%;
                padding: 0.4em;
                box-sizing: border-box;
            }
            input[type="date"] {
                min-width: 150px;
            }
            .greyed {
                color: #999;
                font-style: italic;
            }
            .section {
                background: white;
                padding: 1.5em;
                border-radius: 8px;
                margin-top: 2em;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            button {
                padding: 0.6em;
                font-size: 1em;
                background-color: #88B0DC;
                border: none;
                color: white;
                border-radius: 4px;
                margin-top: 1em;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <h2>Microsoft 365 DNS Record Generator</h2>
        <div class="section">
            <label>Domeinnaam:</label>
            <input type="text" id="domain" placeholder="voorbeeld.nl">
            <label>Tenantnaam:</label>
            <input type="text" id="tenant" placeholder="exampletenant">

            <div id="output"></div>
        </div>

        <script>
            function generateTable() {
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

                const dkim1 = `selector1-${domainClean}._domainkey.${tenant}`;
                const dkim2 = `selector2-${domainClean}._domainkey.${tenant}`;

                const table = `
                <table>
                    <thead>
                        <tr>
                            <th>Techniek</th>
                            <th>Type record</th>
                            <th>Waarde</th>
                            <th>Extra opties</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>MX</td>
                            <td>MX</td>
                            <td>${domainClean}.mail.protection.outlook.com</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td>SPF</td>
                            <td>TXT</td>
                            <td>v=spf1 include:spf.protection.outlook.com -all</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td>DKIM</td>
                            <td>CNAME</td>
                            <td>${dkim1}</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td>DKIM</td>
                            <td>CNAME</td>
                            <td>${dkim2}</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td>DMARC</td>
                            <td>TXT</td>
                            <td id="dmarc-value">v=DMARC1; p=quarantine;</td>
                            <td>
                                Beleid:
                                <select id="dmarc-policy" onchange="updateDMARC()">
                                    <option value="none">none</option>
                                    <option value="quarantine" selected>quarantine</option>
                                    <option value="reject">reject</option>
                                </select><br/>
                                RUA e-mail: <input id="dmarc-rua" type="email" placeholder="rua@example.nl" oninput="updateDMARC()"><br/>
                                RUF e-mail: <input id="dmarc-ruf" type="email" placeholder="ruf@example.nl" oninput="updateDMARC()">
                            </td>
                        </tr>
                        <tr>
                            <td>MTA-STS</td>
                            <td>TXT</td>
                            <td id="mta-sts-value">v=STS; id=</td>
                            <td>
                                Datum-ID:
                                <input type="date" id="mta-date" onchange="updateMTASTS()"><br/>
                                RUA e-mail: <input id="mta-rua" type="email" placeholder="reports@example.nl" oninput="updateMTASTS()">
                            </td>
                        </tr>
                        <tr>
                            <td>SMTP DANE</td>
                            <td>TLSA</td>
                            <td class="greyed">Wordt handmatig opgehaald vanuit je mailservercertificaat</td>
                            <td class="greyed">Geen actie nodig hier</td>
                        </tr>
                    </tbody>
                </table>
                `;

                document.getElementById("output").innerHTML = table;
            }

            function updateDMARC() {
                const policy = document.getElementById("dmarc-policy").value;
                const rua = document.getElementById("dmarc-rua").value;
                const ruf = document.getElementById("dmarc-ruf").value;

                let record = `v=DMARC1; p=${policy}`;
                if (rua) record += `; rua=mailto:${rua}`;
                if (ruf) record += `; ruf=mailto:${ruf}`;
                document.getElementById("dmarc-value").innerText = record;
            }

            function updateMTASTS() {
                const date = document.getElementById("mta-date").value;
                const rua = document.getElementById("mta-rua").value;

                let record = `v=STS; id=${date}`;
                if (rua) record += `; rua=mailto:${rua}`;
                document.getElementById("mta-sts-value").innerText = record;
            }

            document.addEventListener("DOMContentLoaded", () => {
                const button = document.createElement("button");
                button.innerText = "Genereer DNS-records";
                button.onclick = generateTable;
                document.querySelector(".section").appendChild(button);
            });
        </script>
    </body>
    </html>
    """
    return func.HttpResponse(html, mimetype="text/html")
