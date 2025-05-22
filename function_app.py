from flask import Flask, request, render_template_string
import datetime
import dns.resolver
import dns.dnssec
import dns.name
import dns.query
import dns.exception

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>M365 DNS Generator</title>
    <style>
        table, th, td { border: 1px solid black; border-collapse: collapse; padding: 8px; }
        th { background-color: #eee; }
    </style>
</head>
<body>
    <h1>M365 DNS Record Generator</h1>
    <form method="post">
        Domein: <input type="text" name="domain" required>
        Tenant naam (onmicrosoft): <input type="text" name="tenant" required>
        <input type="submit" value="Genereer">
    </form>
    {% if records %}
    <h2>DNS Records voor {{ domain }}</h2>
    <table>
        <tr><th></th><th>Type</th><th>Value</th><th>More Options</th></tr>
        {% for r in records %}
        <tr>
            <td></td>
            <td>{{ r['type'] }}</td>
            <td>{{ r['value'] }}</td>
            <td>
                {% for k,v in r['moreOptions'].items() %}
                    <b>{{ k }}</b>: {{ v }}<br>
                {% endfor %}
            </td>
        </tr>
        {% endfor %}
    </table>
    {% endif %}
</body>
</html>
"""

def check_dnssec(domain):
    try:
        name = dns.name.from_text(domain)
        response = dns.resolver.resolve(domain, 'DNSKEY', raise_on_no_answer=False)
        return "✅" if response.rrset else "❌"
    except dns.exception.DNSException:
        return "❌"

@app.route("/", methods=["GET", "POST"])
def index():
    records = []
    domain = ""
    if request.method == "POST":
        domain = request.form.get("domain").strip()
        tenant = request.form.get("tenant").strip()
        today = datetime.date.today().isoformat().replace("-", "")
        dnssec_status = check_dnssec(domain)

        records = [
            {"type": "MX", "value": f"0 {tenant}.mail.protection.outlook.com.", "moreOptions": {"ttl": 3600}},
            {"type": "TXT", "value": "v=spf1 include:spf.protection.outlook.com -all", "moreOptions": {"SPF policy": "-all / ~all"}},
            {"type": "CNAME", "value": "autodiscover -> autodiscover.outlook.com", "moreOptions": {"ttl": 3600}},
            {"type": "CNAME", "value": f"selector1._domainkey -> selector1-{tenant}._domainkey.{tenant}", "moreOptions": {"DKIM": "selector1"}},
            {"type": "CNAME", "value": f"selector2._domainkey -> selector2-{tenant}._domainkey.{tenant}", "moreOptions": {"DKIM": "selector2"}},
            {"type": "TXT", "value": f"v=DMARC1; p=reject; rua=mailto:dmarc@{domain}; ruf=mailto:dmarc@{domain};",
             "moreOptions": {"Policy": "none/quarantine/reject", "rua": f"dmarc@{domain}", "ruf": f"dmarc@{domain}"}},
            {"type": "TXT", "value": f"v=STSv1; id={today}", "moreOptions": {"ID datum": today}},
            {"type": "TLSA", "value": "TLSA record (vereist DNSSEC)", "moreOptions": {"DNSSEC status": dnssec_status}},
        ]

    return render_template_string(HTML_TEMPLATE, records=records, domain=domain)

if __name__ == "__main__":
    app.run(debug=True)
