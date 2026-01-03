(() => {
  const els = {
    // Stepper
    stepperSteps: Array.from(document.querySelectorAll('.stepper-step')),
    steps: Array.from(document.querySelectorAll('.step')),
    step1Next: document.getElementById('step1Next'),
    step2Back: document.getElementById('step2Back'),
    step2Next: document.getElementById('step2Next'),
    step3Back: document.getElementById('step3Back'),
    step3Next: document.getElementById('step3Next'),
    step4Back: document.getElementById('step4Back'),

    // Inputs
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

    generateBtn: document.getElementById('generateBtn'),
    exportBtn: document.getElementById('exportBtn'),
    results: document.getElementById('results'),
    footerYear: document.getElementById('footerYear')
  };

  const COPY_SVG = `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path fill="white" d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
    </svg>
  `;

  let currentStep = 0;
  let lastGenerated = null;

  // Footer year (same wording as dnsmegatool.justinverstijnen.nl)
  if (els.footerYear) {
    els.footerYear.textContent = String(new Date().getFullYear());
  }

  function normalizeTenantInput(input) {
    // Accept: tenantname OR tenantname.onmicrosoft.com OR tenantname.onmicrosoft.com.onmicrosoft.com
    let v = String(input || '').trim();
    if (!v) return '';

    // Remove ALL trailing .onmicrosoft.com occurrences, then add exactly one.
    v = v.replace(/(\.onmicrosoft\.com)+$/i, '');
    // If user pasted a full domain like tenant.onmicrosoft.com, keep only the left-most label(s)
    // (we don't over-validate here; domain validation happens elsewhere).
    return `${v}.onmicrosoft.com`;
  }

  function escapeHtml(text) {
    return String(text).replace(/[&<>"']/g, c => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;'
    })[c]);
  }

  function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  }

  function isValidDomain(domain) {
    const re = /^(?!-)(?:[a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,63}$/;
    return re.test(domain);
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
      await navigator.clipboard.writeText(text);
      if (button) {
        const prev = button.getAttribute('data-prev-title') || 'Copy';
        button.setAttribute('data-prev-title', prev);
        button.title = 'Copied!';
        button.classList.add('active');
        setTimeout(() => {
          button.title = prev;
          button.classList.remove('active');
        }, 700);
      }
    } catch {
      alert('Copy failed. Please copy manually.');
    }
  }

  function showStep(stepIndex) {
    currentStep = Math.max(0, Math.min(stepIndex, els.steps.length - 1));

    for (const stepEl of els.steps) {
      const i = Number(stepEl.getAttribute('data-step'));
      stepEl.hidden = i !== currentStep;
    }

    for (const btn of els.stepperSteps) {
      const i = Number(btn.getAttribute('data-step-jump'));
      if (i === currentStep) {
        btn.setAttribute('aria-current', 'step');
      } else {
        btn.removeAttribute('aria-current');
      }
    }

    // Accessibility: focus first input in step
    const activeStep = els.steps.find(s => Number(s.getAttribute('data-step')) === currentStep);
    const focusable = activeStep?.querySelector('input, select, button');
    focusable?.focus?.();
  }

  function setMtaFieldsEnabled(enabled) {
    if (!els.mtaStsFields) return;
    els.mtaStsFields.style.opacity = enabled ? '1' : '0.55';
    els.mtaStsFields.querySelectorAll('input').forEach(inp => {
      inp.disabled = !enabled;
    });
  }

  function validateStep1() {
    const defaultDomainInput = els.defaultDomainInput.value.trim();
    const customDomain = els.customDomain.value.trim();

    if (!defaultDomainInput) {
      alert('Please fill in the Default Microsoft 365 tenant domain.');
      els.defaultDomainInput.focus();
      return false;
    }

    if (!customDomain || !isValidDomain(customDomain)) {
      alert('Please enter a valid custom domain (e.g. example.com).');
      els.customDomain.focus();
      return false;
    }

    return true;
  }

  function validateStep2() {
    // SPF step: nothing to validate (choice is always available)
    return true;
  }

  function validateStep3() {
    // DMARC step: validate optional email inputs
    const dmarcRUA = els.dmarcRUA?.value.trim() || '';
    const dmarcRUF = els.dmarcRUF?.value.trim() || '';

    if (dmarcRUA && !isValidEmail(dmarcRUA)) {
      alert('Please enter a valid RUA email address.');
      els.dmarcRUA.focus();
      return false;
    }
    if (dmarcRUF && !isValidEmail(dmarcRUF)) {
      alert('Please enter a valid RUF email address.');
      els.dmarcRUF.focus();
      return false;
    }

    return true;
  }

  function validateStep4() {
    const enabled = !!els.mtaStsEnabled?.checked;
    const mtaStsEmail = els.mtaStsEmail?.value.trim() || '';

    if (enabled && mtaStsEmail && !isValidEmail(mtaStsEmail)) {
      alert('Please enter a valid MTA-STS report email address.');
      els.mtaStsEmail.focus();
      return false;
    }

    return true;
  }

  function buildRows(recordsBySection, recordOrder) {
    const rows = [];
    for (const section of recordOrder) {
      const recs = recordsBySection[section];
      if (!recs) continue;
      recs.forEach(rec => rows.push({
        section,
        type: rec.type,
        name: rec.name,
        value: rec.value
      }));
    }
    return rows;
  }

  function renderOverviewTable(rows) {
    // One clean table for everything.
    let html = '';
    html += `<div class="table-wrapper"><table><thead><tr>
      <th style="width: 22%;">Record</th>
      <th style="width: 12%;">Type</th>
      <th style="width: 18%;">Name</th>
      <th>Value</th>
      <th style="width: 60px;"></th>
    </tr></thead><tbody>`;

    rows.forEach((r, idx) => {
      html += `<tr>
        <td><strong>${escapeHtml(r.section)}</strong></td>
        <td>${escapeHtml(r.type)}</td>
        <td>${escapeHtml(r.name)}</td>
        <td class="value-cell"><code>${escapeHtml(r.value)}</code></td>
        <td style="text-align:center;">
          <button class="copy-btn" type="button" data-copy-index="${idx}" aria-label="Copy value" title="Copy">${COPY_SVG}</button>
        </td>
      </tr>`;
    });

    html += `</tbody></table></div>`;

    els.results.innerHTML = html;

    const buttons = els.results.querySelectorAll('button.copy-btn');
    buttons.forEach(btn => {
      const i = Number(btn.getAttribute('data-copy-index'));
      btn.addEventListener('click', () => copyToClipboard(rows[i].value, btn));
    });
  }

  function generateRecords() {
    // Always validate inputs before calling.
    const defaultDomainInput = els.defaultDomainInput.value.trim();
    const defaultDomain = normalizeTenantInput(defaultDomainInput);
    const customDomain = els.customDomain.value.trim();

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

    const dkimTenantPart = customDomain.replace(/\./g, '-');
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

    return { records, recordOrder, defaultDomain, customDomain, mtaEnabled };
  }

  function exportToHtml(out) {
    const rows = buildRows(out.records, out.recordOrder);

    const exportStyles = `
      body { font-family: 'Segoe UI', sans-serif; background-color:#f2f2f2; margin:0; padding:0; }
      .container { max-width:1300px; margin:40px auto; padding:20px; background:#fff; border-radius:8px; box-shadow:0 0 15px rgba(0,0,0,0.1); }
      .header { display:flex; flex-direction: column; align-items:center; justify-content:center; gap:10px; margin-bottom:14px; }
      .header img { width:50px; height:50px; object-fit:contain; }
      h1 { margin:0; font-size:1.8em; text-align:center; }
      p.desc { text-align:center; color:#555; margin: 10px 0 16px 0; line-height:1.45; }
      .table-wrapper { overflow-x:auto; margin-top:10px; border-radius:10px; box-shadow:0 0 10px rgba(0,0,0,0.08); background:#fff; }
      table { width:100%; border-collapse:separate; border-spacing:0; border-radius:10px; }
      thead { background:#f8f9fa; }
      th, td { padding:12px 10px; border-bottom:1px solid #ddd; text-align:left; vertical-align:top; word-break:break-word; }
      tbody tr:nth-child(even) { background:#f6f6f6; }
      button.copy-btn { background:#8EAFDA; color:#fff; border:1px solid transparent; border-radius:6px; cursor:pointer; width:34px; height:34px; display:inline-flex; align-items:center; justify-content:center; }
      button.copy-btn:hover { filter: brightness(0.95); }
      code { font-family:'Segoe UI', sans-serif; font-size:14px; }
      p.footer-text { margin-top:20px; font-size:0.95em; color:#555;text-align: center;text-decoration:none; }
      a { color: inherit; }
    `;

    let bodyHtml = `<div class="container">
      <div class="header">
        <a href="https://justinverstijnen.nl" target="_blank" rel="noopener noreferrer"><img src="https://justinverstijnen.nl/wp-content/uploads/2025/04/cropped-Logo-2.0-Transparant.png" alt="Justin Verstijnen Logo" /></a>
        <h1 style="color:black;">Microsoft 365 DNS Records Report</h1>
      </div>
      <p class="desc">Generated DNS records for <strong>${escapeHtml(out.customDomain)}</strong> (tenant: <strong>${escapeHtml(out.defaultDomain)}</strong>).</p>
    `;

    bodyHtml += `<div class="table-wrapper"><table><thead><tr>
      <th style="width: 22%;">Record</th>
      <th style="width: 12%;">Type</th>
      <th style="width: 18%;">Name</th>
      <th>Value</th>
      <th style="width: 60px;"></th>
    </tr></thead><tbody>`;

    rows.forEach(r => {
      const encoded = encodeURIComponent(r.value);
      bodyHtml += `<tr>
        <td><strong>${escapeHtml(r.section)}</strong></td>
        <td>${escapeHtml(r.type)}</td>
        <td>${escapeHtml(r.name)}</td>
        <td><code>${escapeHtml(r.value)}</code></td>
        <td style="text-align:center;">
          <button class="copy-btn" type="button" data-copy="${encoded}" title="Copy">${COPY_SVG}</button>
        </td>
      </tr>`;
    });

    bodyHtml += `</tbody></table></div>`;

    bodyHtml += `<p class="footer-text">This report was generated by the <a href="https://tools.justinverstijnen.nl/365recordsgenerator">Microsoft 365 DNS Record Generator</a> by Justin Verstijnen.</p>
    </div>`;

    const exportHtml = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>DNS Records Report - justinverstijnen.nl</title>
<style>${exportStyles}</style>
</head>
<body>
${bodyHtml}
<script>
  document.querySelectorAll('button[data-copy]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      try {
        const value = decodeURIComponent(btn.getAttribute('data-copy') || '');
        await navigator.clipboard.writeText(value);
        const prev = btn.title || 'Copy';
        btn.title = 'Copied!';
        setTimeout(() => { btn.title = prev; }, 700);
      } catch (e) {}
    });
  });
</script>
</body>
</html>`;

    const blob = new Blob([exportHtml], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'Microsoft365-DNS-Records.html';
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  function handleGenerate() {
    if (!validateStep1()) return;
    if (!validateStep2()) return;
    if (!validateStep3()) return;
    if (!validateStep4()) return;

    const out = generateRecords();
    lastGenerated = out;

    const rows = buildRows(out.records, out.recordOrder);
    renderOverviewTable(rows);

    els.exportBtn.style.display = 'block';
    document.getElementById('resultsNote').style.display = 'block';
    els.results.focus();
  }

  // --- Wire up events ---

  // Step navigation
  els.step1Next?.addEventListener('click', () => {
    if (!validateStep1()) return;
    showStep(1);
  });

  els.step2Back?.addEventListener('click', () => showStep(0));
  els.step2Next?.addEventListener('click', () => {
    if (!validateStep2()) return;
    showStep(2);
  });

  els.step3Back?.addEventListener('click', () => showStep(1));
  els.step3Next?.addEventListener('click', () => {
    if (!validateStep3()) return;
    showStep(3);
  });

  els.step4Back?.addEventListener('click', () => showStep(2));

  // Stepper click (only allow jumping backwards freely; forwards requires validation)
  els.stepperSteps.forEach(btn => {
    btn.addEventListener('click', () => {
      const target = Number(btn.getAttribute('data-step-jump'));
      if (Number.isNaN(target)) return;

      if (target <= currentStep) {
        showStep(target);
        return;
      }

      // forward jumps: validate progressively
      if (target >= 1 && !validateStep1()) return;
      if (target >= 2 && !validateStep2()) return;
      if (target >= 3 && !validateStep3()) return;
      showStep(target);
    });
  });

  // Auto-correct the tenant input so the suffix isn't duplicated visually
  els.defaultDomainInput?.addEventListener('blur', () => {
    const raw = (els.defaultDomainInput.value || '').trim();
    if (!raw) return;
    els.defaultDomainInput.value = raw.replace(/(\.onmicrosoft\.com)+$/i, '');
  });

  // MTA-STS toggle
  els.mtaStsEnabled?.addEventListener('change', () => {
    setMtaFieldsEnabled(!!els.mtaStsEnabled.checked);
  });

  // Generate / Export
  els.generateBtn?.addEventListener('click', handleGenerate);

  els.exportBtn?.addEventListener('click', () => {
    if (!lastGenerated) {
      // If user didn't generate yet, generate once.
      handleGenerate();
      if (!lastGenerated) return;
    }
    exportToHtml(lastGenerated);
  });

  // Enter-to-next / Enter-to-generate
  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Enter') return;
    const active = document.activeElement;
    if (!active) return;

    const tag = active.tagName;
    if (tag !== 'INPUT' && tag !== 'SELECT') return;

    event.preventDefault();

    if (currentStep === 0) {
      els.step1Next?.click();
      return;
    }
    if (currentStep === 1) {
      els.step2Next?.click();
      return;
    }
    if (currentStep === 2) {
      els.step3Next?.click();
      return;
    }
    if (currentStep === 3) {
      els.generateBtn?.click();
      return;
    }
  });

  // Default date: today (local)
  try {
    const now = new Date();
    const yyyy = now.getFullYear();
    const mm = String(now.getMonth() + 1).padStart(2, '0');
    const dd = String(now.getDate()).padStart(2, '0');
    if (els.mtaStsDate) els.mtaStsDate.value = `${yyyy}-${mm}-${dd}`;
  } catch {}

  // Initial state
  showStep(0);
  setMtaFieldsEnabled(false);
  if (els.exportBtn) els.exportBtn.style.display = 'none';
})();
