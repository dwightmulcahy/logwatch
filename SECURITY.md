# Security Policy

## Supported versions

Only the latest published release receives security updates. Users should
upgrade to the newest semantic-versioned release before reporting a problem.

## Reporting a vulnerability

Use the repository's private vulnerability reporting form at
`https://github.com/dwightmulcahy/logwatcher/security/advisories/new`. If private reporting
is unavailable, open an issue requesting a private contact channel without
including exploit details, credentials, tokens, private URLs, or screenshots.

Include the affected version, deployment architecture, impact, and minimal
reproduction steps. Do not test against systems or accounts you do not own or
have permission to assess.

Never commit credentials, access tokens, `.env` files, production data,
browser profiles, or diagnostic captures containing private information.

## Deployment notes

logwatch mounts `/var/run/docker.sock`, which is root-equivalent access to the
host even when mounted `:ro`. Pull the image only from
`dwightmulcahy/logwatcher`, keep any locally mounted `logwatch.py` read-only and
owned by root, and keep `.env` at mode `600`.
