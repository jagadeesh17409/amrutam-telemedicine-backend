# Security Checklist and Threat Model

Data classes: public doctor specialties; confidential account/appointment data; highly sensitive prescriptions, clinical data and credentials.

| Threat | Mitigation |
|---|---|
| Broken access control | Demo role checks only; production needs authenticated identity and per-record ownership checks |
| Account takeover | Replace demo identity headers with OIDC/JWT, MFA and token rotation |
| Injection | SQLAlchemy parameterized queries and validated inputs |
| Data exposure | TLS, encryption at rest, least privilege, retention controls; do not log clinical details |
| Duplicate booking | Idempotency key, unique constraints, PostgreSQL row lock |
| Abuse | Rate limits, request size limits, monitoring and alerts |
| Secret leakage | Environment variables locally; secret manager and key rotation in production |
| Supply-chain risk | Dependency and container scanning |
| Data loss | Encrypted backups, point-in-time recovery, tested restores |

Checklist: [x] input validation [x] basic role checks [x] booking idempotency [x] avoid clinical details in logs. Remaining before production: real authentication/MFA, per-object authorization, TLS/WAF/rate limits, managed secrets, dependency scans, penetration testing, applicable Indian healthcare/data protection compliance review, backup restore drills and incident response plan.
