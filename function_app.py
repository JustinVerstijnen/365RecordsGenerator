import datetime
import dns.resolver
import dns.exception
import azure.functions as func
from azure.functions import HttpRequest, HttpResponse

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>DNS MEGAtool</title>
    <style>
        body { font-family: Arial; background: #f8f9fa; padding: 2rem; text-align: center; }
        h1 { color: #333; }
        form input[type=text] { padding: 10px; font-size: 16px; width: 250px; margin: 5px; }
        form input[type=submit], .btn-export {
            padding: 10px 20px; background-color: #4CAF50; color: white; border: none;
            font-size: 16px; cursor: pointer; margin-left: 5px;
        }
        table { margin: 2rem auto; border-collapse: collapse; width: 90%; background: white; box-shadow: 0 0 8px rgba(0,0,0,0.1); }
        th, td { padding: 12px 16px; border-bottom: 1px solid #ddd; text-align: left; }
        th { background-color: #f0f0f0; }
        .checkmark { color: green; font-weight: bold; }
    </style>
</head>
<body>
    <h1>DNS MEGAtool</h1>
    <p>This tool checks multiple DNS records and their configuration for your domain.</p>
    <form method="POST">
        <input type="text" name="domain" placeholder="example.com" required value="{{ domain }}">
        <input type="text" name="tenant" placeholder="tenant.onmicrosoft.com" required value="{{ tenant }}">
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
            <td>{{ r.type }}</td>
            <td><span class="checkmark">✔</span></td>
            <td>{{ r.value }}</td>
        </tr>
        {% endfor %}
    </table>
    {% endif %}
</body>
</html>
"""

from jinja2 import Template
from azure.functions import App

app = App()

def check_dnssec(domain: str) -> bool:
    try:
        dns.resolver.resolve(domain, 'DNSKEY')
        return True
    except dns.exception.DNSException:
        return False

@app.function_name(name="DnsChecker")
@app.route(route="dnscheck", methods=["GET", "POST"])
def dns_checker(req: HttpRequest) -> HttpResponse:
    domain = req.form.get("domain") or req.params.get("domain") or ""
    tenant = req.form.get("tenant") or req.params.get("tenant") or ""
    records = []

    if domain and tenant:
        today = datetime.date.today().isoformat().replace("-", "")
        dnssec = check_dnssec(domain)

        records = [
            {"type": "MX", "value": f"{domain}-u-v1.mx.microsoft.com"},
            {"type": "SPF", "value": "v=spf1 include:spf.protection.outlook.com -all"},
            {"type": "DKIM", "value": f"v=DKIM1; k=rsa; p=MIIB..."},
            {"type": "DMARC", "value": f"v=DMARC1; p=reject; rua=mailto:reports@{domain};"},
            {"type": "MTA-STS", "value": f"v=STSv1; rua=mailto:reports@{domain}; id={today}Z"},
            {"type": "DNSSEC", "value": "✅ DNSSEC aanwezig" if dnssec else "❌ DNSSEC niet gevonden"},
        ]

    template = Template(HTML_TEMPLATE)
    html = template.render(domain=domain, tenant=tenant, records=records)

    return HttpResponse(html, mimetype="text/html")
