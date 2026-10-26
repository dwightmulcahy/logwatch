# Security policy

Report vulnerabilities privately at https://github.com/dwightmulcahy/logwatcher/security/advisories/new.
Do not include SMTP credentials, API keys, or unredacted logs in public issues.
Security fixes target the current main branch; deploy a supported current release.

## Docker access

The Docker socket grants host-equivalent Docker control, even when mounted read-only.
Run only trusted images and never expose Logwatcher to untrusted script modifications.
The supplied deployments retain root for QNAP Docker socket compatibility; filesystem,
capability, and resource restrictions reduce exposure but do not isolate Docker privileges.
/data must remain writable. No inbound port is required.
