(() => {
  const els = {
    tabs: Array.from(document.querySelectorAll('.stepper-step')),
    sections: Array.from(document.querySelectorAll('.tool-section')),
    scrollNextButtons: Array.from(document.querySelectorAll('[data-scroll-next]')),

    defaultDomainInput: document.getElementById('defaultDomainInput'),
    customDomain: document.getElementById('customDomain'),

    dmarcPolicy: document.getElementById('dmarcPolicy'),
    dmarcRUA: document.getElementById('dmarcRUA'),
    dmarcRUF: document.getElementById('dmarcRUF'),
    dmarcPct: document.getElementById('dmarcPct'),
    dmarcAdkim: document.getElementById('dmarcAdkim'),
    dmarcAspf: document.getElementById('dmarcAspf'),
    dmarcFo: document.getElementById('dmarcFo'),
    dmarcRf: document.getElementById('dmarcRf'),
    dmarcRi: document.getElementById('dmarcRi'),

    spfFailRadios: document.querySelectorAll('input[name="spfFail"]'),

    mtaStsEnabled: document.getElementById('mtaStsEnabled'),
    mtaStsFields: document.getElementById('mtaStsFields'),
    mtaStsDate: document.getElementById('mtaStsDate'),
    mtaStsEmail: document.getElementById('mtaStsEmail'),

    tlsRptEnabled: document.getElementById('tlsRptEnabled'),
    tlsRptFields: document.getElementById('tlsRptFields'),
    tlsRptEmail: document.getElementById('tlsRptEmail'),

    includeW365Avd: document.getElementById('includeW365Avd'),
    includeIntune: document.getElementById('includeIntune'),

    smtpDaneCmdDnssec: document.getElementById('smtpDaneCmdDnssec'),
    smtpDaneCmdInbound: document.getElementById('smtpDaneCmdInbound'),
    copySmtpDaneCmdDnssec: document.getElementById('copySmtpDaneCmdDnssec'),
    copySmtpDaneCmdInbound: document.getElementById('copySmtpDaneCmdInbound'),

    generateBtn: document.getElementById('generateBtn'),
    exportBtn: document.getElementById('exportBtn'),
    results: document.getElementById('results'),
    resultsEmpty: document.getElementById('resultsEmpty'),
    resultsNote: document.getElementById('resultsNote'),
    footerYear: document.getElementById('footerYear')
  };

  const DEFAULT_TTL = 3600;
  const COPY_ICON = `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
    <path fill="currentColor" d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
  </svg><span class="sr-only">Copy</span>`;
  let lastGenerated = null;
  let renderTimer = null;

  if (els.footerYear) {
    els.footerYear.textContent = String(new Date().getFullYear());
  }

  function normalizeTenantInput(input) {
    let value = String(input || '').trim();
    if (!value) return '';
    value = value.replace(/(\.onmicrosoft\.com)+$/i, '');
    return `${value}.onmicrosoft.com`;
  }

  function escapeHtml(text) {
    return String(text).replace(/[&<>"']/g, char => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;'
    })[char]);
  }

  function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  function isValidDomain(domain) {
    return /^(?!-)(?:[a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,63}$/.test(domain);
  }

  function delay(ms) {
    return new Promise(resolve => {
      renderTimer = window.setTimeout(resolve, ms);
    });
  }

  function scrollToSection(sectionId) {
    const target = document.getElementById(sectionId);
    if (!target) return;
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function setActiveTab(sectionId) {
    els.tabs.forEach(tab => {
      if (tab.dataset.sectionTarget === sectionId) {
        tab.setAttribute('aria-current', 'step');
      } else {
        tab.removeAttribute('aria-current');
      }
    });
  }

  function getSelectedSPFFail() {
    for (const radio of els.spfFailRadios) {
      if (radio.checked) return radio.value;
    }
    return 'hard';
  }

  function formatDate(date) {
    if (!date) return '';
    const d = new Date(date);
    return d.getUTCFullYear().toString().padStart(4, '0') +
      (d.getUTCMonth() + 1).toString().padStart(2, '0') +
      d.getUTCDate().toString().padStart(2, '0') + 'T000000Z';
  }

  async function copyToClipboard(text, button) {
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(text);
      } else {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.setAttribute('readonly', '');
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        textarea.remove();
      }

      if (button) {
        const previousTitle = button.getAttribute('data-prev-title') || button.title || 'Copy';
        button.setAttribute('data-prev-title', previousTitle);
        button.title = 'Copied!';
        button.classList.add('active');
        setTimeout(() => {
          button.title = previousTitle;
          button.classList.remove('active');
        }, 850);
      }
    } catch {
      alert('Copy failed. Please copy manually.');
    }
  }

  function setMtaFieldsEnabled(enabled) {
    if (!els.mtaStsFields) return;
    els.mtaStsFields.classList.toggle('is-disabled', !enabled);
    els.mtaStsFields.querySelectorAll('input').forEach(input => {
      input.disabled = !enabled;
    });
  }

  function setTlsRptFieldsEnabled(enabled) {
    if (!els.tlsRptFields) return;
    els.tlsRptFields.classList.toggle('is-disabled', !enabled);
    els.tlsRptFields.querySelectorAll('input').forEach(input => {
      input.disabled = !enabled;
    });
  }

  function validateDomains() {
    const tenant = els.defaultDomainInput.value.trim();
    const customDomain = els.customDomain.value.trim();

    if (!tenant) {
      alert('Please fill in the Default Microsoft 365 tenant domain.');
      els.defaultDomainInput.focus();
      scrollToSection('domains');
      return false;
    }

    if (!customDomain || !isValidDomain(customDomain)) {
      alert('Please enter a valid custom domain (e.g. example.com).');
      els.customDomain.focus();
      scrollToSection('domains');
      return false;
    }

    return true;
  }

  function validateDmarc() {
    const rua = els.dmarcRUA?.value.trim() || '';
    const ruf = els.dmarcRUF?.value.trim() || '';

    if (rua && !isValidEmail(rua)) {
      alert('Please enter a valid RUA email address.');
      els.dmarcRUA.focus();
      scrollToSection('security');
      return false;
    }

    if (ruf && !isValidEmail(ruf)) {
      alert('Please enter a valid RUF email address.');
      els.dmarcRUF.focus();
      scrollToSection('security');
      return false;
    }

    return true;
  }

  function validateOptionalRecords() {
    const mtaEnabled = !!els.mtaStsEnabled?.checked;
    const mtaEmail = els.mtaStsEmail?.value.trim() || '';
    const tlsEnabled = !!els.tlsRptEnabled?.checked;
    const tlsEmail = els.tlsRptEmail?.value.trim() || '';

    if (mtaEnabled && mtaEmail && !isValidEmail(mtaEmail)) {
      alert('Please enter a valid MTA-STS report email address.');
      els.mtaStsEmail.focus();
      scrollToSection('security');
      return false;
    }

    if (tlsEnabled && !tlsEmail) {
      alert('Please enter a TLS-RPT report email address.');
      els.tlsRptEmail.focus();
      scrollToSection('monitoring');
      return false;
    }

    if (tlsEnabled && !isValidEmail(tlsEmail)) {
      alert('Please enter a valid TLS-RPT report email address.');
      els.tlsRptEmail.focus();
      scrollToSection('monitoring');
      return false;
    }

    return true;
  }

  function validateAll() {
    return validateDomains() && validateDmarc() && validateOptionalRecords();
  }

  function buildSmtpDaneCommands(customDomain) {
    const domain = String(customDomain || '').trim() || '<yourdomain.com>';
    return {
      dnssec: `Enable-DnssecForVerifiedDomain -DomainName ${domain}`,
      inbound: `Enable-SmtpDaneInbound -DomainName ${domain}`
    };
  }

  function updateSmtpDaneCommands() {
    const commands = buildSmtpDaneCommands(els.customDomain?.value || '');
    if (els.smtpDaneCmdDnssec) els.smtpDaneCmdDnssec.value = commands.dnssec;
    if (els.smtpDaneCmdInbound) els.smtpDaneCmdInbound.value = commands.inbound;
  }

  function buildRows(recordsBySection, recordOrder) {
    const rows = [];
    recordOrder.forEach(section => {
      const records = recordsBySection[section];
      if (!records) return;
      records.forEach(record => {
        rows.push({
          section,
          ttl: record.ttl || DEFAULT_TTL,
          type: record.type,
          name: record.name,
          value: record.value
        });
      });
    });
    return rows;
  }

  function recordRowHtml(record, index) {
    return `<tr class="record-row" style="--row-delay:${index * 55}ms">
      <td><strong>${escapeHtml(record.section)}</strong></td>
      <td>${escapeHtml(record.type)}</td>
      <td>${escapeHtml(record.ttl)}</td>
      <td class="copy-cell">
        <div class="copy-cell-content">
          <code>${escapeHtml(record.name)}</code>
          <button class="copy-btn table-copy" type="button" data-copy-index="${index}" data-copy-field="name" aria-label="Copy ${escapeHtml(record.name)} name" title="Copy name">${COPY_ICON}</button>
        </div>
      </td>
      <td class="copy-cell value-cell">
        <div class="copy-cell-content">
          <code>${escapeHtml(record.value)}</code>
          <button class="copy-btn table-copy" type="button" data-copy-index="${index}" data-copy-field="value" aria-label="Copy ${escapeHtml(record.name)} value" title="Copy value">${COPY_ICON}</button>
        </div>
      </td>
    </tr>`;
  }

  function bindResultCopyButtons(rows) {
    els.results.querySelectorAll('button.table-copy').forEach(button => {
      button.addEventListener('click', () => {
        const index = Number(button.dataset.copyIndex);
        const field = button.dataset.copyField;
        if (!rows[index] || !field) return;
        copyToClipboard(rows[index][field], button);
      });
    });
  }

  async function renderOverviewTable(rows) {
    if (renderTimer) {
      clearTimeout(renderTimer);
      renderTimer = null;
    }

    els.resultsEmpty.hidden = true;
    els.results.innerHTML = `<div class="generate-animation" role="status">
      <div class="pulse-stack" aria-hidden="true">
        <span></span><span></span><span></span>
      </div>
      <div>
        <strong>Generating DNS records</strong>
        <p>Preparing the report and adding records to the table...</p>
      </div>
    </div>`;

    scrollToSection('results-section');
    await delay(650);

    els.results.innerHTML = `<div class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Record</th>
            <th>Type</th>
            <th>TTL</th>
            <th>Name</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody id="recordsBody"></tbody>
      </table>
    </div>`;

    const tbody = document.getElementById('recordsBody');
    for (let i = 0; i < rows.length; i += 1) {
      tbody.insertAdjacentHTML('beforeend', recordRowHtml(rows[i], i));
      await delay(70);
    }

    bindResultCopyButtons(rows);
  }

  function generateRecords() {
    const defaultDomain = normalizeTenantInput(els.defaultDomainInput.value.trim());
    const customDomain = els.customDomain.value.trim();
    const dkimTenantPart = customDomain.replace(/\./g, '-');
    const spfFailType = getSelectedSPFFail();

    const dmarcPolicy = els.dmarcPolicy?.value || 'reject';
    const dmarcRUA = els.dmarcRUA?.value.trim() || '';
    const dmarcRUF = els.dmarcRUF?.value.trim() || '';
    const dmarcPct = els.dmarcPct?.value;
    const dmarcAdkim = els.dmarcAdkim?.value;
    const dmarcAspf = els.dmarcAspf?.value;
    const dmarcFo = els.dmarcFo?.value.trim();
    const dmarcRf = els.dmarcRf?.value.trim();
    const dmarcRi = els.dmarcRi?.value;

    const mtaEnabled = !!els.mtaStsEnabled?.checked;
    const mtaStsDateInput = els.mtaStsDate?.value || '';
    const mtaStsEmail = els.mtaStsEmail?.value.trim() || '';
    const tlsRptEnabled = !!els.tlsRptEnabled?.checked;
    const tlsRptEmail = els.tlsRptEmail?.value.trim() || '';
    const includeW365Avd = !!els.includeW365Avd?.checked;
    const includeIntune = !!els.includeIntune?.checked;

    const dkim1 = `selector1-${dkimTenantPart}._domainkey.${defaultDomain}`;
    const dkim2 = `selector2-${dkimTenantPart}._domainkey.${defaultDomain}`;
    const mxValue = `0 ${dkimTenantPart}.mail.protection.outlook.com`;
    const spfValue = `v=spf1 include:spf.protection.outlook.com ${spfFailType === 'hard' ? '-all' : '~all'}`;

    let dmarcValue = `v=DMARC1; p=${dmarcPolicy};`;
    if (dmarcPct && dmarcPct !== '') dmarcValue += ` pct=${dmarcPct};`;
    if (dmarcAdkim) dmarcValue += ` adkim=${dmarcAdkim};`;
    if (dmarcAspf) dmarcValue += ` aspf=${dmarcAspf};`;
    if (dmarcFo) dmarcValue += ` fo=${dmarcFo};`;
    if (dmarcRf) dmarcValue += ` rf=${dmarcRf};`;
    if (dmarcRi && dmarcRi !== '') dmarcValue += ` ri=${dmarcRi};`;
    if (dmarcRUA) dmarcValue += ` rua=mailto:${dmarcRUA};`;
    if (dmarcRUF) dmarcValue += ` ruf=mailto:${dmarcRUF};`;

    let mtaStsValue = '';
    if (mtaEnabled) {
      const mtaStsIdDate = formatDate(mtaStsDateInput || new Date());
      mtaStsValue = `v=STSv1; id=${mtaStsIdDate}`;
      if (mtaStsEmail) mtaStsValue += `; rua=mailto:${mtaStsEmail}`;
    }

    const records = {
      'MX Record*': [
        { type: 'MX', name: '@', value: mxValue }
      ],
      'Autodiscover Record': [
        { type: 'CNAME', name: 'autodiscover', value: 'autodiscover.outlook.com' }
      ],
      'SPF Record': [
        { type: 'TXT', name: '@', value: spfValue }
      ],
      'DKIM Records*': [
        { type: 'CNAME', name: 'selector1._domainkey', value: dkim1 },
        { type: 'CNAME', name: 'selector2._domainkey', value: dkim2 }
      ],
      'DMARC Record': [
        { type: 'TXT', name: '_dmarc', value: dmarcValue }
      ]
    };

    const recordOrder = [
      'MX Record*',
      'Autodiscover Record',
      'SPF Record',
      'DKIM Records*',
      'DMARC Record'
    ];

    if (mtaEnabled) {
      records['MTA-STS Record'] = [
        { type: 'TXT', name: '_mta-sts', value: mtaStsValue }
      ];
      recordOrder.push('MTA-STS Record');
    }

    if (tlsRptEnabled) {
      records['TLS-RPT Record'] = [
        { type: 'TXT', name: '_smtp._tls', value: `v=TLSRPTv1; rua=mailto:${tlsRptEmail};` }
      ];
      recordOrder.push('TLS-RPT Record');
    }

    if (includeW365Avd) {
      records['Windows 365 / AVD Record'] = [
        { type: 'TXT', name: '_msradc', value: 'https://rdweb.wvd.microsoft.com/api/arm/feeddiscovery' }
      ];
      recordOrder.push('Windows 365 / AVD Record');
    }

    if (includeIntune) {
      records['Intune Enterprise Enrollment Records'] = [
        { type: 'CNAME', name: 'enterpriseenrollment', value: 'EnterpriseEnrollment-s.manage.microsoft.com.' },
        { type: 'CNAME', name: 'enterpriseregistration', value: 'EnterpriseRegistration.windows.net.' }
      ];
      recordOrder.push('Intune Enterprise Enrollment Records');
    }

    return {
      records,
      recordOrder,
      defaultDomain,
      customDomain,
      includeW365Avd,
      includeIntune
    };
  }

  function exportToHtml(out) {
    const rows = buildRows(out.records, out.recordOrder);
    const rowsHtml = rows.map((row, index) => {
      const encodedName = encodeURIComponent(row.name);
      const encodedValue = encodeURIComponent(row.value);
      return `<tr>
        <td><strong>${escapeHtml(row.section)}</strong></td>
        <td>${escapeHtml(row.type)}</td>
        <td>${escapeHtml(row.ttl)}</td>
        <td class="copy-cell"><div class="copy-cell-content"><code>${escapeHtml(row.name)}</code><button class="copy-btn" type="button" data-copy="${encodedName}" title="Copy name">${COPY_ICON}</button></div></td>
        <td class="copy-cell"><div class="copy-cell-content"><code>${escapeHtml(row.value)}</code><button class="copy-btn" type="button" data-copy="${encodedValue}" title="Copy value">${COPY_ICON}</button></div></td>
      </tr>`;
    }).join('');

    const exportStyles = `
      body { font-family:'Segoe UI', sans-serif; background-color:#eef2f7; margin:0; padding:0; color:#111827; }
      .container { max-width:1300px; margin:40px auto; padding:22px; background:#fff; border-radius:8px; box-shadow:0 12px 30px rgba(17,24,39,0.12); }
      .header { display:flex; flex-direction:column; align-items:center; gap:10px; margin-bottom:18px; }
      .header img { width:50px; height:50px; object-fit:contain; }
      h1 { margin:0; font-size:1.8em; text-align:center; }
      p.desc { text-align:center; color:#52606f; margin:10px 0 18px; line-height:1.45; }
      .table-wrapper { overflow-x:auto; margin-top:14px; border:1px solid #d9dde6; border-radius:8px; background:#fff; }
      table { width:100%; border-collapse:separate; border-spacing:0; }
      thead { background:#f8fafc; }
      th, td { padding:12px 10px; border-bottom:1px solid #e5e7eb; text-align:left; vertical-align:middle; word-break:break-word; }
      tbody tr:nth-child(even) { background:#f8fafc; }
      code { font-family:'Segoe UI', sans-serif; font-size:14px; }
      .copy-cell { min-width:170px; }
      .copy-cell-content { min-height:34px; display:flex; align-items:center; gap:8px; justify-content:space-between; }
      .copy-cell-content code { min-width:0; }
      button.copy-btn { background:#77B0DE; color:#fff; border:1px solid transparent; border-radius:6px; cursor:pointer; min-width:34px; height:34px; display:inline-flex; align-items:center; justify-content:center; }
      button.copy-btn:hover { filter:brightness(0.95); }
      button.copy-btn svg { width:16px; height:16px; }
      .sr-only { position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0; }
      p.footer-text { margin-top:20px; font-size:0.95em; color:#52606f; text-align:center; }
      a { color:inherit; }
    `;

    const exportHtml = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>DNS Records Report - justinverstijnen.nl</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>${exportStyles}</style>
</head>
<body>
  <div class="container">
    <div class="header">
      <a href="https://justinverstijnen.nl" target="_blank" rel="noopener noreferrer"><img src="https://justinverstijnen.nl/wp-content/uploads/2025/04/cropped-Logo-2.0-Transparant.png" alt="Justin Verstijnen Logo" /></a>
      <h1>Microsoft 365 DNS Records Report</h1>
    </div>
    <p class="desc">Generated DNS records for <strong>${escapeHtml(out.customDomain)}</strong> (tenant: <strong>${escapeHtml(out.defaultDomain)}</strong>).</p>
    <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Record</th>
            <th>Type</th>
            <th>TTL</th>
            <th>Name</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody>${rowsHtml}</tbody>
      </table>
    </div>
    <p class="footer-text">This report was generated by the <a href="https://tools.justinverstijnen.nl/365recordsgenerator">Microsoft 365 DNS Record Generator</a> by Justin Verstijnen.</p>
  </div>
  <script>
    document.querySelectorAll('button[data-copy]').forEach((btn) => {
      btn.addEventListener('click', async () => {
        try {
          const value = decodeURIComponent(btn.getAttribute('data-copy') || '');
          await navigator.clipboard.writeText(value);
          const previousTitle = btn.title || 'Copy';
          btn.title = 'Copied!';
          setTimeout(() => { btn.title = previousTitle; }, 800);
        } catch (e) {}
      });
    });
  </script>
</body>
</html>`;

    const blob = new Blob([exportHtml], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = 'Microsoft365-DNS-Records.html';
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
  }

  async function handleGenerate() {
    if (!validateAll()) return;

    const out = generateRecords();
    lastGenerated = out;
    const rows = buildRows(out.records, out.recordOrder);

    els.generateBtn.disabled = true;
    els.exportBtn.hidden = true;
    els.resultsNote.hidden = true;
    els.generateBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i>Generating...';

    await renderOverviewTable(rows);

    els.exportBtn.hidden = false;
    els.resultsNote.hidden = false;
    els.generateBtn.disabled = false;
    els.generateBtn.innerHTML = '<i class="fas fa-check-circle"></i>Generate records';
    els.results.focus();
  }

  els.tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const sectionId = tab.dataset.sectionTarget;
      if (sectionId) scrollToSection(sectionId);
    });
  });

  els.scrollNextButtons.forEach(button => {
    button.addEventListener('click', () => {
      const sectionId = button.dataset.scrollNext;
      if (sectionId) scrollToSection(sectionId);
    });
  });

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      const visible = entries
        .filter(entry => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

      if (visible?.target?.dataset.section) {
        setActiveTab(visible.target.dataset.section);
      }
    }, {
      rootMargin: '-35% 0px -55% 0px',
      threshold: [0.1, 0.25, 0.5]
    });

    els.sections.forEach(section => observer.observe(section));
  }

  els.customDomain?.addEventListener('input', updateSmtpDaneCommands);
  els.customDomain?.addEventListener('blur', updateSmtpDaneCommands);

  els.defaultDomainInput?.addEventListener('blur', () => {
    const raw = (els.defaultDomainInput.value || '').trim();
    if (!raw) return;
    els.defaultDomainInput.value = raw.replace(/(\.onmicrosoft\.com)+$/i, '');
  });

  els.mtaStsEnabled?.addEventListener('change', () => setMtaFieldsEnabled(!!els.mtaStsEnabled.checked));
  els.tlsRptEnabled?.addEventListener('change', () => setTlsRptFieldsEnabled(!!els.tlsRptEnabled.checked));

  els.copySmtpDaneCmdDnssec?.addEventListener('click', () => {
    copyToClipboard(els.smtpDaneCmdDnssec?.value || '', els.copySmtpDaneCmdDnssec);
  });

  els.copySmtpDaneCmdInbound?.addEventListener('click', () => {
    copyToClipboard(els.smtpDaneCmdInbound?.value || '', els.copySmtpDaneCmdInbound);
  });

  els.generateBtn?.addEventListener('click', handleGenerate);

  els.exportBtn?.addEventListener('click', () => {
    if (!lastGenerated) {
      handleGenerate();
      return;
    }
    exportToHtml(lastGenerated);
  });

  try {
    const now = new Date();
    const yyyy = now.getFullYear();
    const mm = String(now.getMonth() + 1).padStart(2, '0');
    const dd = String(now.getDate()).padStart(2, '0');
    if (els.mtaStsDate) els.mtaStsDate.value = `${yyyy}-${mm}-${dd}`;
  } catch {}

  setMtaFieldsEnabled(false);
  setTlsRptFieldsEnabled(false);
  updateSmtpDaneCommands();
})();
