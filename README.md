# 365RecordsGenerator

365RecordsGenerator is a lightweight and web-based DNS record generator for configuring Microsoft 365 domains created by Justin Verstijnen. This tool can be used to generate all needed records and export these records for quick configuration. It does it by take every neede DNS record into account for the highest domain and email security.

However the tool is great and worked perfectly till some time ago, the record-text generation for MX and DKIM is random from 2025 till now, so double check these records in your admin center.

## Main features

The main features of this tool are:

- Generate all required DNS records for Microsoft 365 setup:
  - **MX** (Mail Exchange)
  - **SPF** (Sender Policy Framework)
  - **Autodiscover** (CNAME)
  - **DKIM** (DomainKeys Identified Mail)
  - **DMARC** (Domain-based Message Authentication, Reporting, and Conformance)
  - **MTA-STS** (Mail Transfer Agent Strict Transport Security)
- Customizable output and record selection
- Export DNS configuration as a clean HTML report

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
