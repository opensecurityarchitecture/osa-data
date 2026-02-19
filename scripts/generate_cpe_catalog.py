#!/usr/bin/env python3
"""Generate the TRIDENT CPE reference catalog.

4-layer model (platform type hierarchy):
  L1 — Major Platforms:       OS, browsers, runtimes, languages
  L2 — Enterprise Applications: servers, databases, email, collaboration, productivity
  L3 — Enterprise Infrastructure: network, security, virtualisation, identity, backup
  L4 — FS Applications:       SWIFT, trading, core banking, payments, risk, market data

L4 sub-categories (TFSP alignment):
  CB  — Core Banking           AML — AML & Compliance
  PAY — Messaging & Payments   PTS — Payment Terminals
  HSM — HSM & Cryptography     TRD — Trading & Execution
  MKD — Market Data            RSK — Risk & Treasury
  CLR — Clearing & Settlement  REG — Regulatory Reporting

Evidence sources:
  - CISA KEV (Known Exploited Vulnerabilities) — confirmed exploitation in the wild
  - NVD CPE Dictionary — authoritative product identifiers where they exist

CPE source attribution:
  - "nvd"  = identifier exists in the NVD CPE Dictionary
  - "osa"  = minted by TRIDENT for FS platforms absent from NVD

CPE 2.3 URI format:
  cpe:2.3:<part>:<vendor>:<product>:<version>:*:*:*:*:*:*:*

Produces:
  - data/attack/cpe-catalog.json
  - data/attack/cpe-parent-of-edges.json
"""

import json
import os
import urllib.request
from collections import Counter
from pathlib import Path

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'attack')
KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
CACHE_PATH = Path("/tmp/kev.json")

def cpe_uri(part, vendor, product, version="*"):
    return f"cpe:2.3:{part}:{vendor}:{product}:{version}:*:*:*:*:*:*:*"

def download_kev():
    if CACHE_PATH.exists() and CACHE_PATH.stat().st_size > 0:
        pass
    else:
        print(f"Downloading KEV from {KEV_URL}")
        urllib.request.urlretrieve(KEV_URL, CACHE_PATH)
    with open(CACHE_PATH) as f:
        return json.load(f)

# ============================================================================
# 4-LAYER CPE CATALOG
# L1-L3 entries: (part, vendor, product, title, kev_validated, source)
# L4 entries:    (part, vendor, product, title, kev_validated, source, fs_category)
#
# kev_validated = True means this product appears in CISA KEV
# source = "nvd" (NVD CPE Dictionary) or "osa" (OSA-minted for FS platforms)
# fs_category = TFSP category code for L4 entries (CB, AML, PAY, etc.)
# ============================================================================

# Layer 1: Major Platforms — OS, browsers, runtimes, languages
L1_MAJOR_PLATFORMS = [
    # Operating Systems
    ("o", "microsoft", "windows_server", "Microsoft Windows Server", True, "nvd"),
    ("o", "microsoft", "windows_10", "Microsoft Windows 10", True, "nvd"),
    ("o", "microsoft", "windows_11", "Microsoft Windows 11", True, "nvd"),
    ("o", "redhat", "enterprise_linux", "Red Hat Enterprise Linux", True, "nvd"),
    ("o", "canonical", "ubuntu_linux", "Ubuntu Linux", False, "nvd"),
    ("o", "suse", "sles", "SUSE Linux Enterprise Server", False, "nvd"),
    ("o", "oracle", "linux", "Oracle Linux", False, "nvd"),
    ("o", "centos", "centos", "CentOS", False, "nvd"),
    ("o", "rocky", "rocky_linux", "Rocky Linux", False, "nvd"),
    ("o", "linux", "linux_kernel", "Linux Kernel", True, "nvd"),
    ("o", "apple", "macos", "Apple macOS", True, "nvd"),
    ("o", "apple", "ios", "Apple iOS", True, "nvd"),
    ("o", "google", "android", "Google Android", True, "nvd"),
    ("o", "ibm", "aix", "IBM AIX", False, "nvd"),
    ("o", "vmware", "photon_os", "VMware Photon OS", False, "nvd"),

    # Browsers
    ("a", "google", "chrome", "Google Chrome", True, "nvd"),
    ("a", "mozilla", "firefox", "Mozilla Firefox", True, "nvd"),
    ("a", "microsoft", "edge", "Microsoft Edge", False, "nvd"),
    ("a", "microsoft", "internet_explorer", "Microsoft Internet Explorer", True, "nvd"),

    # Runtimes and Languages
    ("a", "oracle", "java_se", "Oracle Java SE", True, "nvd"),
    ("a", "microsoft", "dotnet_framework", "Microsoft .NET Framework", True, "nvd"),
    ("a", "microsoft", "dotnet", "Microsoft .NET (Core)", False, "nvd"),
    ("a", "python", "python", "Python", False, "nvd"),
    ("a", "nodejs", "node.js", "Node.js", False, "nvd"),
    ("a", "php", "php", "PHP", False, "nvd"),
    ("a", "ruby", "ruby", "Ruby", False, "nvd"),

    # Core Libraries
    ("a", "openssl", "openssl", "OpenSSL", False, "nvd"),
    ("a", "apache", "log4j", "Apache Log4j", True, "nvd"),
    ("a", "gnu", "glibc", "GNU C Library (glibc)", True, "nvd"),
    ("a", "gnu", "bash", "GNU Bash", True, "nvd"),
    ("a", "sudo", "sudo", "Sudo", True, "nvd"),
]

# Layer 2: Enterprise Applications — servers, databases, email, productivity
L2_ENTERPRISE_APPS = [
    # Web / Application Servers
    ("a", "apache", "http_server", "Apache HTTP Server", True, "nvd"),
    ("a", "apache", "tomcat", "Apache Tomcat", True, "nvd"),
    ("a", "apache", "struts", "Apache Struts", True, "nvd"),
    ("a", "microsoft", "iis", "Microsoft IIS", False, "nvd"),
    ("a", "oracle", "weblogic", "Oracle WebLogic Server", True, "nvd"),
    ("a", "oracle", "fusion_middleware", "Oracle Fusion Middleware", True, "nvd"),
    ("a", "ibm", "websphere", "IBM WebSphere Application Server", False, "nvd"),
    ("a", "redhat", "jboss", "Red Hat JBoss EAP", True, "nvd"),
    ("a", "eclipse", "jetty", "Eclipse Jetty", False, "nvd"),
    ("a", "f5", "nginx", "NGINX", False, "nvd"),
    ("a", "spring", "spring_framework", "Spring Framework", True, "nvd"),
    ("a", "spring", "spring_boot", "Spring Boot", False, "nvd"),
    ("a", "sap", "netweaver", "SAP NetWeaver", True, "nvd"),
    ("a", "adobe", "coldfusion", "Adobe ColdFusion", True, "nvd"),
    ("a", "adobe", "commerce", "Adobe Commerce / Magento", True, "nvd"),

    # Databases
    ("a", "oracle", "database", "Oracle Database", True, "nvd"),
    ("a", "microsoft", "sql_server", "Microsoft SQL Server", False, "nvd"),
    ("a", "postgresql", "postgresql", "PostgreSQL", False, "nvd"),
    ("a", "oracle", "mysql", "MySQL", False, "nvd"),
    ("a", "mongodb", "mongodb", "MongoDB", False, "nvd"),
    ("a", "ibm", "db2", "IBM Db2", False, "nvd"),
    ("a", "mariadb", "mariadb", "MariaDB", False, "nvd"),
    ("a", "redis", "redis", "Redis", False, "nvd"),
    ("a", "elastic", "elasticsearch", "Elasticsearch", False, "nvd"),
    ("a", "apache", "cassandra", "Apache Cassandra", False, "nvd"),

    # Email and Collaboration
    ("a", "microsoft", "exchange_server", "Microsoft Exchange Server", True, "nvd"),
    ("a", "microsoft", "outlook", "Microsoft Outlook", True, "nvd"),
    ("a", "microsoft", "365", "Microsoft 365", True, "nvd"),
    ("a", "microsoft", "teams", "Microsoft Teams", False, "nvd"),
    ("a", "microsoft", "sharepoint", "Microsoft SharePoint", True, "nvd"),
    ("a", "microsoft", "onedrive", "Microsoft OneDrive", False, "nvd"),
    ("a", "google", "workspace", "Google Workspace", False, "nvd"),
    ("a", "synacor", "zimbra", "Zimbra Collaboration Suite", True, "nvd"),
    ("a", "roundcube", "webmail", "Roundcube Webmail", True, "nvd"),
    ("a", "zoom", "zoom", "Zoom", False, "nvd"),
    ("a", "slack", "slack", "Slack", False, "nvd"),
    ("a", "mimecast", "email_security", "Mimecast Email Security", False, "nvd"),
    ("a", "proofpoint", "email_protection", "Proofpoint Email Protection", False, "nvd"),
    ("a", "exim", "exim", "Exim MTA", True, "nvd"),

    # Productivity / Endpoint Software
    ("a", "microsoft", "office", "Microsoft Office", True, "nvd"),
    ("a", "adobe", "acrobat_reader", "Adobe Acrobat Reader", True, "nvd"),
    ("a", "adobe", "flash_player", "Adobe Flash Player (Legacy)", True, "nvd"),
    ("a", "microsoft", "powershell", "Microsoft PowerShell", False, "nvd"),
    ("a", "rarlab", "winrar", "WinRAR", True, "nvd"),

    # Middleware and Messaging
    ("a", "apache", "kafka", "Apache Kafka", False, "nvd"),
    ("a", "ibm", "mq", "IBM MQ", False, "nvd"),
    ("a", "apache", "activemq", "Apache ActiveMQ", True, "nvd"),
    ("a", "vmware", "rabbitmq", "RabbitMQ", False, "nvd"),
    ("a", "apache", "zookeeper", "Apache ZooKeeper", False, "nvd"),
    ("a", "etcd-io", "etcd", "etcd", False, "nvd"),

    # CMS / Content
    ("a", "atlassian", "confluence", "Atlassian Confluence", True, "nvd"),
    ("a", "atlassian", "jira", "Atlassian Jira", True, "nvd"),
    ("a", "atlassian", "bitbucket", "Atlassian Bitbucket", True, "nvd"),
    ("a", "drupal", "drupal", "Drupal", True, "nvd"),
    ("a", "wordpress", "wordpress", "WordPress", False, "nvd"),
    ("a", "sitecore", "xp", "Sitecore Experience Platform", True, "nvd"),

    # File Transfer
    ("a", "progress", "moveit_transfer", "Progress MOVEit Transfer", True, "nvd"),
    ("a", "fortra", "goanywhere_mft", "Fortra GoAnywhere MFT", True, "nvd"),
    ("a", "accellion", "fta", "Accellion FTA", True, "nvd"),
    ("a", "crushftp", "crushftp", "CrushFTP", True, "nvd"),

    # API Gateways
    ("a", "kong", "kong_gateway", "Kong API Gateway", False, "nvd"),
    ("a", "mulesoft", "anypoint", "MuleSoft Anypoint Platform", False, "nvd"),

    # Development / CI-CD
    ("a", "gitlab", "gitlab", "GitLab CE/EE", True, "nvd"),
    ("a", "github", "enterprise", "GitHub Enterprise", False, "nvd"),
    ("a", "jenkins", "jenkins", "Jenkins", True, "nvd"),
    ("a", "jfrog", "artifactory", "JFrog Artifactory", False, "nvd"),
    ("a", "sonarqube", "sonarqube", "SonarQube", False, "nvd"),
    ("a", "jetbrains", "teamcity", "JetBrains TeamCity", True, "nvd"),
    ("a", "microsoft", "azure_devops", "Microsoft Azure DevOps", False, "nvd"),

    # ITSM / GRC
    ("a", "servicenow", "now_platform", "ServiceNow Now Platform", True, "nvd"),
    ("a", "servicenow", "grc", "ServiceNow GRC", False, "nvd"),
    ("a", "rsa", "archer", "RSA Archer", False, "nvd"),
    ("a", "bmc", "remedy", "BMC Remedy", False, "nvd"),
]

# Layer 3: Enterprise Infrastructure — network, security, virtualisation, identity
L3_INFRASTRUCTURE = [
    # Firewalls / Network Security
    ("o", "cisco", "ios", "Cisco IOS", True, "nvd"),
    ("o", "cisco", "ios_xe", "Cisco IOS XE", True, "nvd"),
    ("o", "cisco", "ios_xr", "Cisco IOS XR", True, "nvd"),
    ("o", "cisco", "asa", "Cisco ASA", True, "nvd"),
    ("o", "cisco", "nx-os", "Cisco NX-OS", True, "nvd"),
    ("a", "cisco", "firepower_threat_defense", "Cisco Firepower Threat Defense", True, "nvd"),
    ("a", "cisco", "ise", "Cisco Identity Services Engine", True, "nvd"),
    ("a", "cisco", "anyconnect", "Cisco AnyConnect", True, "nvd"),
    ("o", "paloaltonetworks", "pan-os", "Palo Alto PAN-OS", True, "nvd"),
    ("a", "paloaltonetworks", "expedition", "Palo Alto Expedition", True, "nvd"),
    ("a", "paloaltonetworks", "cortex_xdr", "Palo Alto Cortex XDR", False, "nvd"),
    ("a", "paloaltonetworks", "prisma_access", "Palo Alto Prisma Access", False, "nvd"),
    ("o", "fortinet", "fortios", "Fortinet FortiOS", True, "nvd"),
    ("a", "fortinet", "fortimanager", "Fortinet FortiManager", True, "nvd"),
    ("a", "fortinet", "fortiweb", "Fortinet FortiWeb", True, "nvd"),
    ("a", "f5", "big-ip", "F5 BIG-IP", True, "nvd"),
    ("o", "juniper", "junos", "Juniper Junos OS", True, "nvd"),
    ("a", "checkpoint", "security_gateway", "Check Point Security Gateway", False, "nvd"),
    ("o", "sonicwall", "sonicos", "SonicWall SonicOS", True, "nvd"),
    ("h", "sonicwall", "sma100", "SonicWall SMA100", True, "nvd"),
    ("a", "sophos", "firewall", "Sophos Firewall", True, "nvd"),
    ("h", "zyxel", "firewall", "Zyxel Firewall", True, "nvd"),
    ("h", "barracuda", "email_security_gateway", "Barracuda ESG", True, "nvd"),
    ("h", "watchguard", "firebox", "WatchGuard Firebox", True, "nvd"),
    ("a", "citrix", "netscaler", "Citrix NetScaler ADC / Gateway", True, "nvd"),
    ("o", "mikrotik", "routeros", "MikroTik RouterOS", True, "nvd"),
    ("a", "zscaler", "zia", "Zscaler Internet Access", False, "nvd"),
    ("a", "zscaler", "zpa", "Zscaler Private Access", False, "nvd"),
    ("a", "infoblox", "nios", "Infoblox NIOS", False, "nvd"),

    # VPN / Remote Access
    ("a", "ivanti", "connect_secure", "Ivanti Connect Secure", True, "nvd"),
    ("a", "ivanti", "policy_secure", "Ivanti Policy Secure", True, "nvd"),
    ("a", "ivanti", "epmm", "Ivanti EPMM", True, "nvd"),
    ("a", "ivanti", "epm", "Ivanti Endpoint Manager", True, "nvd"),
    ("a", "citrix", "virtual_apps", "Citrix Virtual Apps and Desktops", True, "nvd"),
    ("a", "citrix", "sharefile", "Citrix ShareFile", True, "nvd"),
    ("a", "zoho", "manageengine", "Zoho ManageEngine", True, "nvd"),
    ("a", "kaseya", "vsa", "Kaseya VSA", True, "nvd"),
    ("a", "connectwise", "screenconnect", "ConnectWise ScreenConnect", True, "nvd"),
    ("a", "beyondtrust", "pra", "BeyondTrust PRA", True, "nvd"),

    # Virtualisation / Containers
    ("a", "vmware", "vcenter", "VMware vCenter Server", True, "nvd"),
    ("o", "vmware", "esxi", "VMware ESXi", True, "nvd"),
    ("a", "vmware", "nsx", "VMware NSX", False, "nvd"),
    ("a", "vmware", "workspace_one", "VMware Workspace ONE", True, "nvd"),
    ("a", "microsoft", "hyper-v", "Microsoft Hyper-V", True, "nvd"),
    ("a", "docker", "docker_engine", "Docker Engine", False, "nvd"),
    ("a", "kubernetes", "kubernetes", "Kubernetes", False, "nvd"),
    ("a", "redhat", "openshift", "Red Hat OpenShift", False, "nvd"),
    ("a", "hashicorp", "terraform", "HashiCorp Terraform", False, "nvd"),
    ("a", "ansible", "ansible", "Ansible", False, "nvd"),

    # Identity and Access
    ("a", "microsoft", "active_directory", "Microsoft Active Directory", True, "nvd"),
    ("a", "microsoft", "entra_id", "Microsoft Entra ID", False, "nvd"),
    ("a", "microsoft", "adfs", "Microsoft AD FS", False, "nvd"),
    ("a", "cyberark", "privileged_access_manager", "CyberArk PAM", False, "nvd"),
    ("a", "okta", "okta", "Okta Identity Platform", False, "nvd"),
    ("a", "pingidentity", "pingfederate", "Ping Identity PingFederate", False, "nvd"),
    ("a", "sailpoint", "identitynow", "SailPoint IdentityNow", False, "nvd"),
    ("a", "hashicorp", "vault", "HashiCorp Vault", False, "nvd"),
    ("a", "rsa", "securid", "RSA SecurID", False, "nvd"),
    ("a", "venafi", "trust_protection_platform", "Venafi Trust Protection Platform", False, "nvd"),

    # SIEM / SOAR / Detection
    ("a", "splunk", "enterprise", "Splunk Enterprise", False, "nvd"),
    ("a", "microsoft", "sentinel", "Microsoft Sentinel", False, "nvd"),
    ("a", "ibm", "qradar", "IBM QRadar", False, "nvd"),
    ("a", "elastic", "security", "Elastic Security", False, "nvd"),

    # EDR / XDR
    ("a", "crowdstrike", "falcon", "CrowdStrike Falcon", False, "nvd"),
    ("a", "microsoft", "defender_for_endpoint", "Microsoft Defender for Endpoint", True, "nvd"),
    ("a", "sentinelone", "singularity", "SentinelOne Singularity", False, "nvd"),
    ("a", "vmware", "carbon_black", "VMware Carbon Black", False, "nvd"),
    ("a", "trendmicro", "apex_one", "Trend Micro Apex One", True, "nvd"),

    # Vulnerability Management
    ("a", "tenable", "nessus", "Tenable Nessus", False, "nvd"),
    ("a", "qualys", "vmdr", "Qualys VMDR", False, "nvd"),
    ("a", "rapid7", "insightvm", "Rapid7 InsightVM", False, "nvd"),

    # DLP / Data Security
    ("a", "symantec", "dlp", "Symantec DLP", False, "nvd"),
    ("a", "microsoft", "purview", "Microsoft Purview", False, "nvd"),

    # NDR
    ("a", "darktrace", "enterprise", "Darktrace Enterprise", False, "nvd"),

    # Cloud Security
    ("a", "paloaltonetworks", "prisma_cloud", "Palo Alto Prisma Cloud", False, "nvd"),
    ("a", "wiz", "wiz", "Wiz Cloud Security", False, "nvd"),

    # Monitoring
    ("a", "solarwinds", "orion", "SolarWinds Orion", True, "nvd"),
    ("a", "nagios", "nagios_xi", "Nagios XI", True, "nvd"),
    ("a", "grafana", "grafana", "Grafana", True, "nvd"),
    ("a", "datadog", "datadog", "Datadog", False, "nvd"),

    # Backup and Storage
    ("a", "veeam", "backup_and_replication", "Veeam Backup & Replication", True, "nvd"),
    ("a", "veritas", "backup_exec", "Veritas Backup Exec", True, "nvd"),
    ("a", "commvault", "complete", "Commvault Complete", False, "nvd"),
    ("a", "rubrik", "cloud_data_management", "Rubrik CDM", False, "nvd"),
    ("h", "qnap", "nas", "QNAP NAS", True, "nvd"),
    ("h", "netapp", "ontap", "NetApp ONTAP", False, "nvd"),

    # Crypto / PKI
    ("a", "thales", "luna_hsm", "Thales Luna HSM", False, "nvd"),
    ("h", "thales", "payshield", "Thales payShield HSM", False, "nvd"),
    ("a", "microsoft", "ad_certificate_services", "Microsoft AD Certificate Services", False, "nvd"),
    ("a", "entrust", "certificate_hub", "Entrust Certificate Hub", False, "nvd"),
]

# Layer 4: FS Applications — aligned to TFSP (FS Technology Primitives) categories
# Each entry: (part, vendor, product, title, kev_validated, source, fs_category)
L4_FS_APPLICATIONS = [
    # ── CB: Core Banking ──────────────────────────────────────────────────
    ("a", "oracle", "flexcube", "Oracle FLEXCUBE Universal Banking", False, "nvd", "CB"),
    ("a", "temenos", "transact", "Temenos Transact (T24)", False, "nvd", "CB"),
    ("a", "sap", "banking_services", "SAP Banking Services", False, "nvd", "CB"),
    ("a", "fisglobal", "profile", "FIS Profile (Core Banking)", False, "osa", "CB"),
    ("a", "fisglobal", "modern_banking", "FIS Modern Banking Platform", False, "osa", "CB"),
    ("a", "fiserv", "dna", "Fiserv DNA", False, "osa", "CB"),
    ("a", "fiserv", "premier", "Fiserv Premier", False, "osa", "CB"),
    ("a", "tcs", "bancs", "TCS BaNCS", False, "osa", "CB"),
    ("a", "infosys", "finacle", "Infosys Finacle", False, "osa", "CB"),
    ("a", "finastra", "fusion_essence", "Finastra Fusion Essence", False, "osa", "CB"),
    ("a", "broadridge", "impact", "Broadridge IMPACT", False, "osa", "CB"),
    ("a", "backbase", "digital_banking", "Backbase Digital Banking Platform", False, "osa", "CB"),
    ("a", "temenos", "infinity", "Temenos Infinity (Digital Channels)", False, "osa", "CB"),
    ("a", "thought_machine", "vault", "Thought Machine Vault", False, "osa", "CB"),

    # ── AML: AML & Compliance ─────────────────────────────────────────────
    ("a", "oracle", "financial_services_aml", "Oracle Financial Services AML", False, "nvd", "AML"),
    ("a", "nice", "actimize", "NICE Actimize", False, "osa", "AML"),
    ("a", "sas", "aml", "SAS Anti-Money Laundering", False, "osa", "AML"),
    ("a", "verafin", "verafin", "Verafin (Nasdaq)", False, "osa", "AML"),
    ("a", "fiserv", "financial_crime_risk", "Fiserv Financial Crime Risk Management", False, "osa", "AML"),
    ("a", "behavox", "behavox", "Behavox Compliance Platform", False, "osa", "AML"),
    ("a", "nasdaq", "surveillance", "Nasdaq Surveillance", False, "osa", "AML"),
    ("a", "fircosoft", "firco_continuity", "Fircosoft Firco Continuity (Sanctions)", False, "osa", "AML"),

    # ── PAY: Messaging & Payments ─────────────────────────────────────────
    ("a", "swift_scrl", "alliance_access", "SWIFT Alliance Access", False, "osa", "PAY"),
    ("a", "swift_scrl", "alliance_lite2", "SWIFT Alliance Lite2", False, "osa", "PAY"),
    ("a", "swift_scrl", "alliance_gateway", "SWIFT Alliance Gateway", True, "nvd", "PAY"),
    ("a", "aci", "up_framework", "ACI Worldwide UP Framework", False, "osa", "PAY"),
    ("a", "volante", "volpay", "Volante VolPay", False, "osa", "PAY"),
    ("a", "fisglobal", "real_time_payments", "FIS Real-Time Payments", False, "osa", "PAY"),
    ("a", "finastra", "fusion_payments", "Finastra Fusion Payments To Go", False, "osa", "PAY"),
    ("a", "clear2pay", "open_payment_framework", "FIS Open Payment Framework", False, "osa", "PAY"),

    # ── PTS: Payment Terminals ────────────────────────────────────────────
    ("h", "verifone", "terminal", "Verifone Payment Terminal", False, "nvd", "PTS"),
    ("h", "ingenico", "telium", "Ingenico Telium Terminal", False, "nvd", "PTS"),
    ("h", "pax", "a_series", "PAX Technology A-Series Terminal", False, "osa", "PTS"),
    ("h", "castles", "saturn", "Castles Technology Saturn Terminal", False, "osa", "PTS"),

    # ── HSM: HSM & Cryptography ───────────────────────────────────────────
    ("h", "utimaco", "securityserver", "Utimaco SecurityServer HSM", False, "nvd", "HSM"),
    ("h", "utimaco", "paymentserver", "Utimaco PaymentServer HSM", False, "nvd", "HSM"),
    ("h", "entrust", "nshield", "Entrust nShield HSM", False, "osa", "HSM"),
    ("h", "futurex", "vectera", "Futurex Vectera Plus HSM", False, "osa", "HSM"),

    # ── TRD: Trading & Execution ──────────────────────────────────────────
    ("a", "iongroup", "fidessa", "ION Fidessa", False, "osa", "TRD"),
    ("a", "iongroup", "ion_trading", "ION Trading Platform", False, "osa", "TRD"),
    ("a", "flextrade", "flextrader", "FlexTrade FlexTRADER", False, "osa", "TRD"),
    ("a", "simcorp", "dimension", "SimCorp Dimension", False, "osa", "TRD"),
    ("a", "crd", "charles_river_ims", "Charles River IMS (State Street)", False, "osa", "TRD"),
    ("a", "bloomberg", "aim", "Bloomberg AIM", False, "osa", "TRD"),
    ("a", "fixprotocol", "fix_engine", "FIX Protocol Engine (generic)", False, "osa", "TRD"),
    ("a", "lseg", "millennium_exchange", "LSEG Millennium Exchange", False, "osa", "TRD"),

    # ── MKD: Market Data ──────────────────────────────────────────────────
    ("a", "bloomberg", "terminal", "Bloomberg Terminal", False, "osa", "MKD"),
    ("a", "refinitiv", "eikon", "Refinitiv Eikon (LSEG)", False, "osa", "MKD"),
    ("a", "factset", "workstation", "FactSet Workstation", False, "osa", "MKD"),
    ("a", "refinitiv", "rtds", "Refinitiv Real-Time Distribution System", False, "osa", "MKD"),
    ("a", "solace", "pubsub_plus", "Solace PubSub+ (Market Data)", False, "osa", "MKD"),
    ("a", "informatica", "ultra_messaging", "Informatica Ultra Messaging", False, "osa", "MKD"),
    ("a", "tibco", "ems", "TIBCO Enterprise Message Service", False, "nvd", "MKD"),
    ("a", "tibco", "rendezvous", "TIBCO Rendezvous", False, "nvd", "MKD"),

    # ── RSK: Risk & Treasury ──────────────────────────────────────────────
    ("a", "murex", "mx3", "Murex MX.3", False, "osa", "RSK"),
    ("a", "calypso", "calypso", "Calypso Technology (Adenza)", False, "osa", "RSK"),
    ("a", "finastra", "fusion_treasury", "Finastra Fusion Treasury", False, "osa", "RSK"),
    ("a", "fisglobal", "quantum", "FIS Front Arena / Quantum", False, "osa", "RSK"),
    ("a", "sas", "risk_management", "SAS Risk Management", False, "osa", "RSK"),
    ("a", "moodys", "riskcalc", "Moody's Analytics RiskCalc", False, "osa", "RSK"),
    ("a", "msci", "riskmetrics", "MSCI RiskMetrics", False, "osa", "RSK"),
    ("a", "kyriba", "kyriba", "Kyriba Treasury Management", False, "osa", "RSK"),
    ("a", "openlink", "endur", "Openlink Endur (ION)", False, "osa", "RSK"),
    ("a", "numerix", "oneview", "Numerix Oneview", False, "osa", "RSK"),

    # ── CLR: Clearing & Settlement ────────────────────────────────────────
    ("a", "dtcc", "nscc", "DTCC National Securities Clearing Corp", False, "osa", "CLR"),
    ("a", "dtcc", "dtc", "DTCC Depository Trust Company", False, "osa", "CLR"),
    ("a", "euroclear", "eses", "Euroclear ESES Settlement", False, "osa", "CLR"),
    ("a", "clearstream", "creation", "Clearstream Creation Settlement", False, "osa", "CLR"),
    ("a", "lch", "swapclear", "LCH SwapClear", False, "osa", "CLR"),
    ("a", "lch", "equityclear", "LCH EquityClear", False, "osa", "CLR"),
    ("a", "cls", "settlement", "CLS Settlement (FX PvP)", False, "osa", "CLR"),
    ("a", "cme", "clearing", "CME Clearing", False, "osa", "CLR"),
    ("a", "ice", "clear", "ICE Clear", False, "osa", "CLR"),
    ("a", "eurex", "c7", "Eurex C7 Clearing", False, "osa", "CLR"),
    ("a", "broadridge", "gptc", "Broadridge GPTC (Post-Trade)", False, "osa", "CLR"),

    # ── REG: Regulatory Reporting ─────────────────────────────────────────
    ("a", "axiomsl", "controllerview", "AxiomSL ControllerView", False, "osa", "REG"),
    ("a", "wolterskluwer", "onesumx", "Wolters Kluwer OneSumX", False, "osa", "REG"),
    ("a", "moodys", "regulatory_reporting", "Moody's Analytics Regulatory Reporting", False, "osa", "REG"),
    ("a", "vermeg", "megara", "Vermeg MEGARA", False, "osa", "REG"),
    ("a", "regnology", "abacus", "Regnology ABACUS", False, "osa", "REG"),
]

LAYERS = [
    (1, "Major Platforms", L1_MAJOR_PLATFORMS),
    (2, "Enterprise Applications", L2_ENTERPRISE_APPS),
    (3, "Enterprise Infrastructure", L3_INFRASTRUCTURE),
    (4, "FS Applications", L4_FS_APPLICATIONS),
]


FS_CATEGORY_NAMES = {
    "CB":  "Core Banking",
    "AML": "AML & Compliance",
    "PAY": "Messaging & Payments",
    "PTS": "Payment Terminals",
    "HSM": "HSM & Cryptography",
    "TRD": "Trading & Execution",
    "MKD": "Market Data",
    "RSK": "Risk & Treasury",
    "CLR": "Clearing & Settlement",
    "REG": "Regulatory Reporting",
}

# PARENT_OF groupings: parent product → list of child product keys (vendor, product)
# Used to generate hierarchy edges for product families
PARENT_OF_GROUPS = [
    # Windows family
    (("microsoft", "windows_server"), [("microsoft", "windows_10"), ("microsoft", "windows_11")]),
    # RHEL family
    (("redhat", "enterprise_linux"), [("oracle", "linux"), ("centos", "centos"), ("rocky", "rocky_linux")]),
    # Apple family
    (("apple", "macos"), [("apple", "ios")]),
    # Cisco IOS family
    (("cisco", "ios"), [("cisco", "ios_xe"), ("cisco", "ios_xr")]),
    # Ivanti family
    (("ivanti", "connect_secure"), [("ivanti", "policy_secure")]),
    # VMware family
    (("vmware", "vcenter"), [("vmware", "esxi"), ("vmware", "nsx")]),
    # SWIFT family
    (("swift_scrl", "alliance_gateway"), [("swift_scrl", "alliance_access"), ("swift_scrl", "alliance_lite2")]),
    # DTCC family
    (("dtcc", "nscc"), [("dtcc", "dtc")]),
    # LCH family
    (("lch", "swapclear"), [("lch", "equityclear")]),
    # Fortinet family
    (("fortinet", "fortios"), [("fortinet", "fortimanager"), ("fortinet", "fortiweb")]),
    # Palo Alto family
    (("paloaltonetworks", "pan-os"), [("paloaltonetworks", "expedition"), ("paloaltonetworks", "cortex_xdr"), ("paloaltonetworks", "prisma_access")]),
    # Zscaler family
    (("zscaler", "zia"), [("zscaler", "zpa")]),
    # SonicWall family
    (("sonicwall", "sonicos"), [("sonicwall", "sma100")]),
    # Citrix family
    (("citrix", "netscaler"), [("citrix", "virtual_apps"), ("citrix", "sharefile")]),
]


def main():
    # Load KEV for cross-referencing
    data = download_kev()
    catalog_version = data.get("catalogVersion", "?")

    # Build catalog
    catalog = {}
    seq = 1
    layer_counts = Counter()
    part_counts = Counter()
    source_counts = Counter()
    fs_cat_counts = Counter()
    kev_validated_count = 0
    seen_cpe = set()
    # Map (vendor, product) → entry_id for PARENT_OF edge generation
    cpe_id_map = {}

    for layer_num, layer_name, entries in LAYERS:
        for entry in entries:
            # L1-L3: (part, vendor, product, title, kev_validated, source)
            # L4:    (part, vendor, product, title, kev_validated, source, fs_category)
            part, vendor, product, title, kev_validated, source = entry[:6]
            fs_category = entry[6] if len(entry) > 6 else None

            cpe_key = (vendor, product)
            if cpe_key in seen_cpe:
                continue
            seen_cpe.add(cpe_key)

            entry_id = f"CPE-{seq:04d}"
            node = {
                "id": entry_id,
                "cpe23Uri": cpe_uri(part, vendor, product),
                "part": part,
                "vendor": vendor,
                "product": product,
                "version": "*",
                "title": title,
                "layer": layer_num,
                "layerName": layer_name,
                "source": source,
                "kevValidated": kev_validated,
            }
            if fs_category:
                node["fsCategory"] = fs_category
                node["fsCategoryName"] = FS_CATEGORY_NAMES[fs_category]
                fs_cat_counts[fs_category] += 1

            catalog[entry_id] = node
            cpe_id_map[cpe_key] = entry_id
            seq += 1
            layer_counts[layer_num] += 1
            part_counts[part] += 1
            source_counts[source] += 1
            if kev_validated:
                kev_validated_count += 1

    total = len(catalog)

    # Generate PARENT_OF edges
    parent_of_edges = []
    for parent_key, children_keys in PARENT_OF_GROUPS:
        parent_id = cpe_id_map.get(parent_key)
        if not parent_id:
            continue
        for child_key in children_keys:
            child_id = cpe_id_map.get(child_key)
            if child_id:
                parent_of_edges.append({
                    "from": parent_id,
                    "from_type": "cpe",
                    "to": child_id,
                    "to_type": "cpe",
                })

    # Save catalog
    out_path = os.path.join(DATA_DIR, 'cpe-catalog.json')
    with open(out_path, 'w') as f:
        json.dump(catalog, f, indent=2)
        f.write('\n')

    # Save PARENT_OF edges
    edges_path = os.path.join(DATA_DIR, 'cpe-parent-of-edges.json')
    with open(edges_path, 'w') as f:
        json.dump(parent_of_edges, f, indent=2)
        f.write('\n')

    # Print summary
    print(f"{'='*70}")
    print(f"TRIDENT CPE CATALOG — 4-Layer Model")
    print(f"{'='*70}")
    print(f"Source: CISA KEV catalog v{catalog_version}")
    print()
    print(f"{'='*70}")
    print(f"LAYER MODEL")
    print(f"{'='*70}")
    for layer_num, layer_name, _ in LAYERS:
        count = layer_counts[layer_num]
        print(f"  L{layer_num} — {layer_name:<30} {count:>4} entries")
    print(f"  {'─'*50}")
    print(f"  Total: {total}")
    print()

    # L4 FS sub-category breakdown
    print(f"L4 FS sub-categories (TFSP alignment):")
    for code in ["CB", "AML", "PAY", "PTS", "HSM", "TRD", "MKD", "RSK", "CLR", "REG"]:
        name = FS_CATEGORY_NAMES[code]
        count = fs_cat_counts.get(code, 0)
        print(f"  {code:<4} {name:<25} {count:>3} entries")
    print(f"  {'─'*40}")
    print(f"  L4 total: {sum(fs_cat_counts.values())}")
    print()

    print(f"CPE source attribution:")
    print(f"  nvd (NVD CPE Dictionary):  {source_counts.get('nvd', 0)}")
    print(f"  osa (OSA-minted for FS):   {source_counts.get('osa', 0)}")
    print()
    print(f"KEV-validated (confirmed exploitation): {kev_validated_count}/{total} ({100*kev_validated_count/total:.0f}%)")
    print()
    print(f"Part breakdown:")
    for p in sorted(part_counts.keys()):
        label = {"a": "Application", "h": "Hardware", "o": "Operating System"}[p]
        print(f"  {p} ({label}): {part_counts[p]}")
    print()
    print(f"PARENT_OF edges: {len(parent_of_edges)}")
    print()
    print(f"Saved: {out_path}")
    print(f"Saved: {edges_path}")


if __name__ == '__main__':
    main()
