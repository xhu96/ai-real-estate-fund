# Observability

The repository includes dependency-light observability primitives:

- JSON log formatter
- request ID middleware
- timing middleware
- Prometheus-style metrics endpoint
- audit log with hash-chain verification
- health and readiness endpoints

For production, route logs to your platform collector, scrape `/ops/metrics`, alert on error rate and latency, and verify `/ops/health` from outside the cluster.
