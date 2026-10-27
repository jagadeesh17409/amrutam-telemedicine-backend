# Architecture and Design

## Scope
The assignment states 100k daily consultations, p95 reads under 200ms, writes under 500ms, and 99.95% availability. This prototype demonstrates design patterns but has not been load-tested and does not claim those targets.

## High-level design
Web/mobile client -> HTTPS gateway/WAF/rate limiter -> modular FastAPI API -> PostgreSQL. Optional Redis can cache public doctor search results. Queue/workers should handle notifications, payment reconciliation and exports. Logs, metrics and traces go to an observability platform. Encrypted backups and point-in-time recovery support disaster recovery.

## Booking transaction
Client sends POST /bookings with an Idempotency-Key. API validates patient, doctor and slot. PostgreSQL locks the slot row using FOR UPDATE, rejects booked slots with 409, otherwise marks it booked and inserts consultation plus audit event in one transaction. A retry with the same key returns the existing booking. Retry only transient failures with capped exponential backoff and jitter.

## Data and scaling
Core tables: users, doctors, availability_slots, consultations, prescriptions, payments, audit_logs. Index foreign keys, status and timestamps; use bounded pagination and connection pooling. Cache only safe read-heavy data. Consider date partitioning for consultations/audit logs after measuring table growth. Use transactional outbox/saga patterns for payment and notification workflows.

## Observability and DR
Starter logs request method/path/status/latency and exposes health/readiness. Production needs OpenTelemetry traces, Prometheus metrics, dashboards, alerts, multi-zone database failover, encrypted backups, point-in-time recovery and tested restore drills. Define RPO/RTO with stakeholders.

## Production gaps
Use OIDC/JWT + MFA, per-object authorization, Alembic migrations, TLS, rate limiting, secret manager/key rotation, dependency/container scanning, load tests and formal privacy/security review.
