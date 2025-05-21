import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="/", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def generate_dns_records(req: func.HttpRequest) -> func.HttpResponse:
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DNS Record Generator - justinverstijnen.nl</title>
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
            input, select, textarea, button {
                padding: 0.6em;
                font-size: 1em;
                margin: 0.4em 0;
                border: 1px solid #ccc;
                border-radius: 4px;
                width: 100%;
                box-sizing: border-box;
            }
            textarea {
                resize: vertical;
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
                margin-bottom: 2em;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            pre {
                background: #eef;
                padding: 1em;
                border-radius: 6px;
                overflow-x: auto;
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

        <h2>DNS Record Generator</h2>
        <p style="text-align:center;">Generate SPF, DKIM, and DMARC records for your domain below.</p>

        <div class="section">
            <h3>SPF Record</h3>
            <label>Allowed sources (e.g. ip4:192.0.2.0/24 include:_spf.google.com):</label>
            <input type="text" id="spfSources" placeholder="e.g. ip4:192.0.2.0/24 include:_spf.google.com" />
            <button onclick="generateSPF()">Generate SPF</button>
            <pre id="spfResult"></pre>
        </div>

        <div class="section">
            <h3>DMARC Record</h3>
            <label>Policy (p=):</label>
            <select id="dmarcPolicy">
                <option value="none">none</option>
                <option value="quarantine">quarantine</option>
                <option value="reject" selected>reject</option>
            </select>
            <label>Aggregate Report Email (rua):</label>
            <input type="email" id="dmarcRua" placeholder="mailto:postmaster@example.com" />
            <button onclick="generateDMARC()">Generate DMARC</button>
            <pre id="dmarcResult"></pre>
        </div>

        <div class="section">
            <h3>DKIM Record</h3>
            <label>Selector:</label>
            <input type="text" id="dkimSelector" placeholder="e.g. default" />
            <label>Public Key:</label>
            <textarea id="dkimKey" rows="5" placeholder="Paste your DKIM public key here..."></textarea>
            <button onclick="generateDKIM()">Generate DKIM</button>
            <pre id="dkimResult"></pre>
        </div>

        <script>
            function generateSPF() {
                const sources = document.getElementById("spfSources").value.trim();
                if (!sources) return alert("Please enter SPF sources.");
                const result = `v=spf1 ${sources} -all`;
                document.getElementById("spfResult").innerText = result;
            }

            function generateDMARC() {
                const policy = document.getElementById("dmarcPolicy").value;
                const rua = document.getElementById("dmarcRua").value.trim();
                if (!rua.startsWith("mailto:")) return alert("DMARC rua must start with 'mailto:'");
                const result = `v=DMARC1; p=${policy}; rua=${rua}; sp=${policy}; adkim=s; aspf=s`;
                document.getElementById("dmarcResult").innerText = result;
            }

            function generateDKIM() {
                const selector = document.getElementById("dkimSelector").value.trim();
                const key = document.getElementById("dkimKey").value.trim().replace(/\\n/g, "").replace(/\\r/g, "");
                if (!selector || !key) return alert("Please fill in both selector and public key.");
                const recordName = `${selector}._domainkey`;
                const recordValue = `v=DKIM1; k=rsa; p=${key}`;
                document.getElementById("dkimResult").innerText = `Record Name: ${recordName}\nRecord Value: ${recordValue}`;
            }
        </script>
    </body>
    </html>
    """
    return func.HttpResponse(html, mimetype="text/html")
