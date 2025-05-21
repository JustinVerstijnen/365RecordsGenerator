import azure.functions as func
import datetime
import json

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Microsoft 365 DNS Generator</title>
    <meta charset="utf-8" />
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f4f6f8;
            max-width: 900px;
            margin: auto;
            padding: 2em;
            color: #333;
        }}
        h1 {{
            text-align: center;
            margin-bottom: 0.2em;
        }}
        .logo {{
            text-align: center;
            margin-bottom: 1em;
        }}
        .logo img {{
            height: 50px;
        }}
        label {{
            font-weight: 600;
            display: block;
            margin-top: 1em;
            margin-bottom: 0.3em;
        }}
        input[type=text], select {{
            width: 100%;
            padding: 0.5em 0.7em;
            font-size: 1em;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
        }}
        .step {{
            font-weight: 700;
            margin-top: 2em;
            margin-bottom: 0.7em;
            font-size: 1.1em;
            color: #005A9E;
        }}
        button {{
            background-color: #0078D4;
            color: white;
            border: none;
            padding: 0.7em 1.2em;
            font-size: 1em;
            border-radius: 4px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 0.4em;
            margin-top: 1em;
        }}
        button:hover {{
            background-color: #005A9E;
        }}
        button#exportPdf {{
            background-color: #107C10;
            display: none;
        }}
        button#exportPdf:hover {{
            background-color: #0B6A0B;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 2em;
        }}
        thead {{
            background-color: #f0f0f0;
        }}
        thead th {{
            text-align: left;
            padding: 0.7em 0.5em;
            font-weight: 600;
            color: #333;
        }}
        tbody td {{
            padding: 0.6em 0.5em;
            vertical-align: middle;
            font-size: 0.95em;
        }}
        tbody tr:not(:last-child) {{
            border-bottom: 0px; /* no visible border */
        }}
        .copy-btn {{
            width: 25px;
            height: 25px;
            background-color: #0078D4;
            border: none;
            color: white;
            border-radius: 3px;
            cursor: pointer;
            display: inline-flex;
            justify-content: center;
            align-items: center;
            font-size: 14px;
            margin-right: 0.5em;
        }}
        .copy-btn:hover {{
            background-color: #005A9E;
        }}
        .greyed-out {{
            color: #888;
            font-style: italic;
            user-select: none;
        }}
        input[type="email"], input[type="date"] {{
            width: 100%;
            box-sizing: border-box;
            padding: 0.4em 0.6em;
            font-size: 0.9em;
            border-radius: 4px;
            border: 1px solid #ccc;
        }}
        .extra-options {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.7em;
            align-items: center;
        }}
        .extra-options > * {{
            flex: 1 1 150px;
        }}
    </style>
    <link
      href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
      rel="stylesheet"
    />
</head>
<body>
    <div class="logo">
        <a href="https://justinverstijnen.nl" target="_blank" rel="noopener">
            <img src="https://justinverstijnen.nl/wp-content/uploads/2025/04/cropped-Logo-2.0-Transparant.png" alt="Justin Verstijnen Logo" />
        </a>
    </div>
    <h1>Microsoft 365 DNS Record Generator</h1>

    <div class="step">Stap 1: Vul je domeinnaam in</div>
    <input type="text" id="domain" placeholder="voorbeeld.nl" autocomplete="off" spellcheck="false" />

    <div class="step">Stap 2: Vul je Microsoft 365 tenant in</div>
    <input type="text" id="tenant" placeholder="justinverstijnen of justinverstijnen.onmicrosoft.com" autocomplete="off" spellcheck="false" />

    <button id="generateBtn" onclick="generateRecords()">
        <i class="fas fa-magic"></i> Genereer DNS-records
    </button>

    <button id="exportPdf" onclick="exportPDF()">
        <i class="fas fa-file-pdf"></i> Exporteer als PDF
    </button>

    <table id="recordsTable" style="display:none;">
        <thead>
            <tr>
                <th>Techniek</th>
                <th>Type record</th>
                <th>Waarde</th>
                <th>Extra opties</th>
            </tr>
        </thead>
        <tbody id="recordsBody">
        </tbody>
    </table>

<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<script>
    const copyIcon = '<i class="fas fa-copy" aria-hidden="true"></i>';

    function copyToClipboard(text) {{
        navigator.clipboard.writeText(text).catch(() => {{
            // fail silently
        }});
    }}

    function formatMtaStsId(date) {{
        // Format date like id=YYYYMMDDHHmmssZ;
        const y = date.getUTCFullYear();
        const mo = String(date.getUTCMonth()+1).padStart(2,'0');
        const d = String(date.getUTCDate()).padStart(2,'0');
        const h = String(date.getUTCHours()).padStart(2,'0');
        const mi = String(date.getUTCMinutes()).padStart(2,'0');
        const s = String(date.getUTCSeconds()).padStart(2,'0');
        return `id=${{y}}${{mo}}${{d}}${{h}}${{mi}}${{s}}Z;`;
    }}

    function generateRecords() {{
        const domain = document.getElementById('domain').value.trim().toLowerCase();
        let tenant = document.getElementById('tenant').value.trim().toLowerCase();

        if (!domain) {{
            alert('Vul je domeinnaam in.');
            return;
        }}
        if (!tenant) {{
            alert('Vul je Microsoft 365 tenant in.');
            return;
        }}

        if (!tenant.endsWith('.onmicrosoft.com')) {{
            tenant += '.onmicrosoft.com';
        }}

        const domainClean = domain.replace(/\./g, '-');

        // Clear old table
        const tbody = document.getElementById('recordsBody');
        tbody.innerHTML = '';

        // SPF soft/hard fail select
        const spfFailType = document.getElementById('spfFailType')?.value || '-all';

        // DMARC controls - Reject default
        const dmarcPolicy = document.getElementById('dmarcPolicy')?.value || 'reject';
        const dmarcRua = document.getElementById('dmarcRua')?.value.trim();
        const dmarcRuf = document.getElementById('dmarcRuf')?.value.trim();

        // MTA-STS controls
        let mtaStsDateInput = document.getElementById('mtaStsDate')?.value;
        let mtaStsDate = mtaStsDateInput ? new Date(mtaStsDateInput + 'T00:00:00Z') : new Date();
        if (isNaN(mtaStsDate.getTime())) {{
            mtaStsDate = new Date();
        }}
        const mtaStsRua = document.getElementById('mtaStsRua')?.value.trim();

        // DNSSEC check placeholder (fake, since real requires server-side DNS query)
        const dnssecSupported = domain.includes('.nl') || domain.includes('.com') || domain.includes('.net');

        // Define records array with objects
        const records = [
            // MX
            {{
                techniek: 'MX',
                type: 'MX',
                waarde: `@                       ${domainClean}.mail.protection.outlook.com`,
                extra: ''
            }},
            // SPF
            {{
                techniek: 'SPF',
                type: 'TXT',
                waarde: `@                       v=spf1 include:spf.protection.outlook.com ${spfFailType}`,
                extra: `
                    <label>SPF fail type:</label>
                    <select id="spfFailType" onchange="generateRecords()">
                        <option value="-all" selected>Hard fail (-all)</option>
                        <option value="~all">Soft fail (~all)</option>
                    </select>
                `
            }},
            // DKIM - 2 records
            {{
                techniek: 'DKIM',
                type: 'CNAME',
                waarde: `selector1._domainkey    selector1-${domainClean}._domainkey.${tenant}`,
                extra: ''
            }},
            {{
                techniek: 'DKIM',
                type: 'CNAME',
                waarde: `selector2._domainkey    selector2-${domainClean}._domainkey.${tenant}`,
                extra: ''
            }},
            // DMARC with options
            {{
                techniek: 'DMARC',
                type: 'TXT',
                waarde: (() => {{
                    let val = `_dmarc                  v=DMARC1; p=${{dmarcPolicy}};`;
                    if (dmarcRua) val += ` rua=mailto:${{dmarcRua}};`;
                    if (dmarcRuf) val += ` ruf=mailto:${{dmarcRuf}};`;
                    return val;
                }})(),
                extra: `
                    <div class="extra-options">
                    <label>Beleid (p):</label>
                    <select id="dmarcPolicy" onchange="generateRecords()">
                        <option value="reject" ${(dmarcPolicy==='reject'?'selected':'')}>Reject</option>
                        <option value="quarantine" ${(dmarcPolicy==='quarantine'?'selected':'')}>Quarantine</option>
                        <option value="none" ${(dmarcPolicy==='none'?'selected':'')}>None</option>
                    </select>

                    <label>RUA e-mail:</label>
                    <input type="email" id="dmarcRua" placeholder="rapport@example.nl" value="${{dmarcRua||''}}" onchange="generateRecords()" />

                    <label>RUF e-mail:</label>
                    <input type="email" id="dmarcRuf" placeholder="forensic@example.nl" value="${{dmarcRuf||''}}" onchange="generateRecords()" />
                    </div>
                `
            }},
            // MTA-STS with date and rua options
            {{
                techniek: 'MTA-STS',
                type: 'TXT',
                waarde: (() => {{
                    const idVal = formatMtaStsId(mtaStsDate);
                    let val = `mta-sts.${{domain}}    v=STSv1; id=${{idVal}}`;
                    if (mtaStsRua) val += `; rua=mailto:${{mtaStsRua}}`;
                    return val;
                }})(),
                extra: `
                    <div class="extra-options">
                    <label>ID datum:</label>
                    <input type="date" id="mtaStsDate" value="${{mtaStsDate.toISOString().slice(0,10)}}" onchange="generateRecords()" />
                    <label>RUA e-mail:</label>
                    <input type="email" id="mtaStsRua" placeholder="reports@example.nl" value="${{mtaStsRua||''}}" onchange="generateRecords()" />
                    </div>
                `
            }},
            // Autodiscover CNAME
            {{
                techniek: 'Autodiscover',
                type: 'CNAME',
                waarde: `autodiscover            autodiscover.outlook.com`,
                extra: ''
            }},
            // SMTP DANE
            {{
                techniek: 'SMTP DANE',
                type: 'TXT',
                waarde: dnssecSupported
                    ? "Activeer SMTP DANE nadat je DNSSEC hebt geverifieerd"
                    : "⚠ Domein ondersteunt geen DNSSEC, SMTP DANE niet toepassen",
                extra: `<span class="greyed-out">Deze info moet extern gecontroleerd worden</span>`
            }}
        ];

        // Append rows to table body
        for (const rec of records) {{
            // Build copy button + value HTML
            const valueEscaped = rec.waarde.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
            const copyBtnHtml = `<button class="copy-btn" title="Kopieer" onclick="copyToClipboard(\`${rec.waarde}\`)">${copyIcon}</button>`;
            const valueHtml = copyBtnHtml + `<span style="white-space: pre-wrap; font-family: monospace;">${valueEscaped}</span>`;

            const tr = document.createElement('tr');

            // techniek cell
            const tdTech = document.createElement('td');
            tdTech.textContent = rec.techniek;
            tr.appendChild(tdTech);

            // type record cell
            const tdType = document.createElement('td');
            tdType.textContent = rec.type;
            tr.appendChild(tdType);

            // waarde cell
            const tdValue = document.createElement('td');
            tdValue.innerHTML = valueHtml;
            tr.appendChild(tdValue);

            // extra opties cell
            const tdExtra = document.createElement('td');
            tdExtra.innerHTML = rec.extra || '';
            tr.appendChild(tdExtra);

            tbody.appendChild(tr);
        }}

        document.getElementById('recordsTable').style.display = 'table';
        document.getElementById('exportPdf').style.display = 'inline-flex';
    }}

    async function exportPDF() {{
        const {{ jsPDF }} = window.jspdf;
        const doc = new jsPDF();

        const domain = document.getElementById('domain').value.trim();
        const tenant = document.getElementById('tenant').value.trim();

        doc.setFontSize(16);
        doc.text("Microsoft 365 DNS Record Generator", 10, 15);
        doc.setFontSize(12);
        doc.text(`Domein: ${{domain}}`, 10, 25);
        doc.text(`Tenant: ${{tenant}}`, 10, 33);

        const table = document.getElementById('recordsTable');
        let y = 45;

        // Loop over rows and add text to PDF
        for (let i = 1; i < table.rows.length; i++) {{
            const row = table.rows[i];
            let techniek = row.cells[0].innerText;
            let typeRec = row.cells[1].innerText;
            let waarde = row.cells[2].innerText;
            let extra = row.cells[3].innerText;

            let line = `${{techniek}} | ${{typeRec}} | ${{waarde}}`;
            if (y > 270) {{
                doc.addPage();
                y = 20;
            }}
            doc.text(line, 10, y);
            y += 8;
            if (extra.trim() !== '') {{
                let extraLines = extra.split('\\n');
                for (const el of extraLines) {{
                    if (y > 270) {{
                        doc.addPage();
                        y = 20;
                    }}
                    doc.setFontSize(10);
                    doc.text('  Extra: ' + el.trim(), 10, y);
                    doc.setFontSize(12);
                    y += 6;
                }}
            }}
        }}

        doc.save(`DNS-records-${domain}.pdf`);
    }}
</script>
</body>
</html>
"""

@app.route(route="/", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def main(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(HTML_TEMPLATE, mimetype="text/html")
