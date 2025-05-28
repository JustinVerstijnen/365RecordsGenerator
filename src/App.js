import React, { useState } from 'react';

function App() {
  const [defaultDomain, setDefaultDomain] = useState('');
  const [customDomain, setCustomDomain] = useState('');
  const [records, setRecords] = useState(null);

  const generateRecords = () => {
    if (!defaultDomain || !customDomain) {
      alert('Vul beide domeinen in');
      return;
    }

    const dkim1 = `selector1-${customDomain.replace(/\./g, '-')}._domainkey.${defaultDomain}`;
    const dkim2 = `selector2-${customDomain.replace(/\./g, '-')}._domainkey.${defaultDomain}`;

    const mxRecord = {
      name: '@',
      type: 'MX',
      priority: 0,
      value: `${defaultDomain.replace('onmicrosoft.com', 'mail.protection.outlook.com')}`
    };

    const autodiscover = {
      name: 'autodiscover',
      type: 'CNAME',
      value: 'autodiscover.outlook.com'
    };

    const spf = {
      name: '@',
      type: 'TXT',
      value: 'v=spf1 include:spf.protection.outlook.com -all'
    };

    const dmarc = {
      name: '_dmarc',
      type: 'TXT',
      value: `v=DMARC1; p=none; rua=mailto:admin@${customDomain}`
    };

    const mtaSts = {
      name: '_mta-sts',
      type: 'TXT',
      value: 'v=STSv1; id=20250527T0000Z'
    };

    setRecords({
      dkim: [
        { name: 'selector1._domainkey', ttl: 3600, record: dkim1 },
        { name: 'selector2._domainkey', ttl: 3600, record: dkim2 }
      ],
      mx: [mxRecord],
      autodiscover: [autodiscover],
      spf: [spf],
      dmarc: [dmarc],
      mtaSts: [mtaSts]
    });
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert('Gekopieerd naar klembord!');
  };

  return (
    <div style={{ maxWidth: '600px', margin: '2rem auto', fontFamily: 'Arial, sans-serif' }}>
      <h1>DNS Record Generator voor Microsoft 365</h1>

      <label>
        Default domain (bv. jouwnaam.onmicrosoft.com):
        <input
          type="text"
          value={defaultDomain}
          onChange={(e) => setDefaultDomain(e.target.value)}
          style={{ width: '100%', margin: '0.5rem 0' }}
          placeholder="voorbeeld.onmicrosoft.com"
        />
      </label>

      <label>
        Custom domain (bv. jouwnaam.nl):
        <input
          type="text"
          value={customDomain}
          onChange={(e) => setCustomDomain(e.target.value)}
          style={{ width: '100%', margin: '0.5rem 0' }}
          placeholder="voorbeeld.nl"
        />
      </label>

      <button onClick={generateRecords} style={{ padding: '0.5rem 1rem', margin: '1rem 0' }}>
        Genereer records
      </button>

      {records && (
        <div>
          <h2>DKIM Records</h2>
          <table border="1" cellPadding="8" style={{ width: '100%', marginBottom: '1rem' }}>
            <thead>
              <tr>
                <th>Name</th>
                <th>TTL</th>
                <th>Record</th>
                <th>Copy</th>
              </tr>
            </thead>
            <tbody>
              {records.dkim.map((r, i) => (
                <tr key={i}>
                  <td>{r.name}</td>
                  <td>{r.ttl}</td>
                  <td><code>{r.record}</code></td>
                  <td><button onClick={() => copyToClipboard(r.record)}>Copy</button></td>
                </tr>
              ))}
            </tbody>
          </table>

          <h2>MX Record</h2>
          <table border="1" cellPadding="8" style={{ width: '100%', marginBottom: '1rem' }}>
            <thead>
              <tr><th>Name</th><th>Type</th><th>Priority</th><th>Value</th><th>Copy</th></tr>
            </thead>
            <tbody>
              {records.mx.map((r, i) => (
                <tr key={i}>
                  <td>{r.name}</td>
                  <td>{r.type}</td>
                  <td>{r.priority}</td>
                  <td><code>{r.value}</code></td>
                  <td><button onClick={() => copyToClipboard(r.value)}>Copy</button></td>
                </tr>
              ))}
            </tbody>
          </table>

          <h2>Autodiscover Record</h2>
          <table border="1" cellPadding="8" style={{ width: '100%', marginBottom: '1rem' }}>
            <thead><tr><th>Name</th><th>Type</th><th>Value</th><th>Copy</th></tr></thead>
            <tbody>
              {records.autodiscover.map((r, i) => (
                <tr key={i}>
                  <td>{r.name}</td>
                  <td>{r.type}</td>
                  <td><code>{r.value}</code></td>
                  <td><button onClick={() => copyToClipboard(r.value)}>Copy</button></td>
                </tr>
              ))}
            </tbody>
          </table>

          <h2>SPF Record</h2>
          <table border="1" cellPadding="8" style={{ width: '100%', marginBottom: '1rem' }}>
            <thead><tr><th>Name</th><th>Type</th><th>Value</th><th>Copy</th></tr></thead>
            <tbody>
              {records.spf.map((r, i) => (
                <tr key={i}>
                  <td>{r.name}</td>
                  <td>{r.type}</td>
                  <td><code>{r.value}</code></td>
                  <td><button onClick={() => copyToClipboard(r.value)}>Copy</button></td>
                </tr>
              ))}
            </tbody>
          </table>

          <h2>DMARC Record</h2>
          <table border="1" cellPadding="8" style={{ width: '100%', marginBottom: '1rem' }}>
            <thead><tr><th>Name</th><th>Type</th><th>Value</th><th>Copy</th></tr></thead>
            <tbody>
              {records.dmarc.map((r, i) => (
                <tr key={i}>
                  <td>{r.name}</td>
                  <td>{r.type}</td>
                  <td><code>{r.value}</code></td>
                  <td><button onClick={() => copyToClipboard(r.value)}>Copy</button></td>
                </tr>
              ))}
            </tbody>
          </table>

          <h2>MTA-STS Record</h2>
          <table border="1" cellPadding="8" style={{ width: '100%', marginBottom: '1rem' }}>
            <thead><tr><th>Name</th><th>Type</th><th>Value</th><th>Copy</th></tr></thead>
            <tbody>
              {records.mtaSts.map((r, i) => (
                <tr key={i}>
                  <td>{r.name}</td>
                  <td>{r.type}</td>
                  <td><code>{r.value}</code></td>
                  <td><button onClick={() => copyToClipboard(r.value)}>Copy</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default App;
