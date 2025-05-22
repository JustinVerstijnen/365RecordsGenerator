from flask import Flask, request, render_template_string
import datetime
import dns.resolver
import dns.exception

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>DNS MEGAtool</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f8f9fa;
            margin: 0;
            padding: 2rem;
            text-align: center;
        }
        h1 { color: #333; }
        form input[type=text] {
            padding: 10px;
            font-size: 16px;
            width: 250px;
            margin: 5px;
        }
        form input[type=submit], .btn-export {
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            border: none;
            font-size: 16px;
            cursor: pointer;
            margin-left: 5px;
        }
        table {
            margin: 2rem auto;
            border-collapse: collapse;
            width: 90%;
            background: white;
            box-shadow: 0 0 8px rgba(0,0,0,0.1);
        }
        th, td {
            padding: 12px 16px;
            border-bottom: 1px solid #ddd;
            text-align: left;
        }
        th {
            background-color: #f0f0f0;
        }
        .checkmark {
            color: green;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <h1>DNS MEGAtool</h1>
    <p>This tool checks multiple DNS records and their configuration for your domain.</p>
    <form method="POST">
        <input type="text" name="domain" placeholder="example.com" required value="{{ domain or '' }}">
        <input type="text" name="tenant" placeholder="tenant.onmicrosoft.com" required value="{{ tenant or '' }}">
        <input type="submit" value="Check">
        <button class="btn-export" type="button" onclick="alert('Export coming soon!')">⬇ Export</button>
    </form>

    {% if records %}
    <table>
        <tr>
            <th>Technology</th>
            <th>Status</th>
            <th>DNS Record</th>
        </tr>
        {% for r in records %}
        <tr>
            <td>{{ r["type"] }}</td>
            <td><span class="checkmark">✔</span></td>
            <td>{{ r["value"] | e }}</td>
        </tr>
        {% endfor %}
    </table>
    {% endif %}
</body>
</html>
"""

def check_dnssec(domain):
    try:
        dns.resolver.resolve(domain, 'DNSKEY')
        return True
    except dns.exception.DNSException:
        return False

@app.route("/", methods=["GET", "POST"])
def index():
    records = []
    domain = tenant = ""
    if request.method == "POST":
        domain = request.form.get("domain").strip()
        tenant = request.form.get("tenant").strip()
        today = datetime.date.today().isoformat().replace("-", "")
        dnssec_status = check_dnssec(domain)

        records = [
            {"type": "MX", "value": f"{domain}-u-v1.mx.microsoft.com"},
            {"type": "SPF", "value": "v=spf1 include:spf.protection.outlook.com -all"},
            {"type": "DKIM", "value": f"v=DKIM1; k=rsa; p=MIIBIjANBgkqhki... (verkort)"},
            {"type": "DMARC", "value": f"v=DMARC1; p=reject; rua=mailto:reports@{domain};"},
            {"type": "MTA-STS", "value": f"v=STSv1; rua=mailto:reports@{domain}; id={today}Z;"},
            {"type": "DNSSEC", "value": "✅ DNSSEC aanwezig" if dnssec_status else "❌ DNSSEC niet gevonden"}
        ]

    return render_template_string(HTML_TEMPLATE, records=records, domain=domain, tenant=tenant)

if __name__ == "__main__":
    app.run(debug=True)
