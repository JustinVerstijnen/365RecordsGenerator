# 365RecordsGenerator

Generate complete DNS configuration records for Microsoft 365 (Office 365) based on your domain and tenant information.

## Overview

**365RecordsGenerator** is an open-source tool designed to help you automatically generate all necessary DNS records for Microsoft 365 services. It supports both basic and advanced configurations, including MX, SPF, Autodiscover, DKIM, DMARC, and MTA-STS.  
The tool can be used locally or deployed in serverless environments like Azure Functions.

## Features

- Generate all required DNS records for Microsoft 365 setup:
  - **MX** (Mail Exchange)
  - **SPF** (Sender Policy Framework)
  - **Autodiscover** (CNAME)
  - **DKIM** (DomainKeys Identified Mail)
  - **DMARC** (Domain-based Message Authentication, Reporting, and Conformance)
  - **MTA-STS** (Mail Transfer Agent Strict Transport Security)
- Simple CLI usage or deploy as an Azure Function
- Customizable output and record selection
- Export DNS configuration as a clean HTML report
- Open-source and easy to integrate in automation pipelines

Please note that records can be generated differently for some domains. Refer the domain settings in Microsoft 365 admin center to double check the values. For most domains, this tool will work properly.

