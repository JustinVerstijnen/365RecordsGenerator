# 365RecordsGenerator

365RecordsGenerator is a lightweight and web-based DNS record generator for configuring Microsoft 365 domains created by Justin Verstijnen. This tool can be used to generate the most important DNS records for Microsoft 365, email security, monitoring, Windows 365 / Azure Virtual Desktop, and Intune enrollment.

The tool is designed as a single scrollable page with categories, quick navigation tabs, copy buttons for record names and values, and multiple export options for quick configuration or documentation.

However the tool is great and useful, the generated MX and DKIM records should still be checked in your own Microsoft 365 tenant. These records are highlighted in the results because they may differ per tenant or environment.

## Main features

The main features of this tool are:

- Generate DNS records for Microsoft 365 setup:
  - **MX** (Mail Exchange)
  - **SPF** (Sender Policy Framework)
  - **Autodiscover** (CNAME)
  - **DKIM** (DomainKeys Identified Mail)
  - **DMARC** (Domain-based Message Authentication, Reporting, and Conformance)
- Generate optional security and monitoring records:
  - **MTA-STS** (Mail Transfer Agent Strict Transport Security)
  - **SMTP-TLS / TLS-RPT** monitoring
- Generate the [PowerShell commands needed for SMTP DANE](https://justinverstijnen.nl/configure-dnssec-and-smtp-dane-with-exchange-online-microsoft-365/)
- Add optional Microsoft service records:
  - **Windows 365 / Azure Virtual Desktop feed discovery** (`_msradc`)
  - **Intune Enterprise Enrollment CNAMEs** (`enterpriseenrollment` and `enterpriseregistration`)
- Copy individual record names and values directly from the results table
- Highlight tenant-specific records that should be checked before publishing
- Export DNS configuration as:
  - **HTML** report
  - **Zone** file
  - **CSV** file

## Page categories

The tool is divided into the following categories:

1. **Domains**
2. **Security**
   - **2.1 SPF**
   - **2.2 DMARC**
   - **2.3 SMTP DANE**
   - **2.4 MTA-STS**
3. **Monitoring**
4. **Microsoft Services**
5. **Results**

Each category can be opened quickly using the tabs at the top of the page. The page automatically scrolls to the selected section.

## Documentation links

The tool includes documentation links for the main record types:

- [SPF, DKIM and DMARC](https://justinverstijnen.nl/enhance-email-security-with-spf-dkim-dmarc/)
- [SMTP DANE](https://justinverstijnen.nl/configure-dnssec-and-smtp-dane-with-exchange-online-microsoft-365)
- [MTA-STS](https://justinverstijnen.nl/what-is-mta-sts-and-how-to-protect-your-email-flow/)
- [TLS-RPT](https://justinverstijnen.nl/what-is-tls-rpt/)
- [AVD / W365 feed discovery](https://justinverstijnen.nl/automatic-avd-w365-feed-discovery-for-mobile-apps/)
- [Intune enrollment DNS records](https://justinverstijnen.nl/configuring-intune-enrollment-dns-records-nonsense-or-required/)

## Hosting

This tool is currently hosted on GitHub Pages. Configuration changes are pushed and built using the default deployment method.

## Technical Architecture

- **Languages** : HTML, CSS, Javascript
- **Platform** : GitHub Pages
- **Runtime model** : Serverless
- **Dependencies** : None

## Changelog/new features

New features to this tool are added when needed or if the tool is broken.

Feature request can be done by submitting issues into GitHub.

## Issues

Its possible to submit any issues using the GitHub issues system.

At this moment, this tool has no known issues.

## License

This project is licensed under the **MIT license**. This means that the software is open source and can be used to run the tool yourself.

Use at your own risk. No guarantees or official support are provided.
