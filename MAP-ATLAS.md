MAP-ATLAS.md - Atlas MVP Planning for API Metrics (API Metrics MVP)

Overview
- Objective: Define and measure key API metrics to drive product decisions, ensure reliability, and demonstrate value with a minimal, well-scoped MVP.
- Scope: Instrumentation, data collection, dashboards, and reporting for a limited API surface. Avoid scope creep. Iterative delivery with lightweight kanban.

Goals & Success Metrics
- SLI/SLO for API latency, error rate, throughput (p50/p95 latency targets).
- Availability targets for critical endpoints.
- Observability: trace/span coverage, logging quality.
- Actionable dashboards for product/eng-for decisions.
- Lightweight data model enabling extensibility to additional endpoints.

Metrics to collect
- Latency: p50, p95, p99 per endpoint
- Error rate: 4xx/5xx ratio
- Throughput: requests per minute
- Saturation: RPS vs capacity
- Availability: endpoint uptime
- Payload size distribution
- Cache hit ratio (if applicable)

Data sources & instrumentation
- API gateway / reverse proxy metrics
- Backend service metrics (instrumented)
- Middleware logs (weighted sampling)
- Frontend synthetic tests (optional for MVP)

Data model (minimal viable)
- endpoint, method, status, latency_ms, payload_size, timestamp, trace_id, service
- attributes: region, version, user_tier (if available)

Milestones
1) Discovery & scope alignment (2 weeks)
   - Define list of endpoints in scope
   - Agree on SLO targets and data retention policy
   - Identify data sources and instrumentation plan
2) Instrumentation plan & baseline (2 weeks)
   - Instrument endpoints with latency and error tracking
   - Implement logging/trace hooks and sampling plan
   - Establish data ingestion pipeline (streaming preferred)
3) API metrics data model & schema (1 week)
   - Define minimal schema; implement adapters
   - Create test events to validate schema
4) Dashboards & reporting (1 week)
   - Build dashboards for latency, error rate, throughput, availability
   - Define alerting rules (if out of tolerance)
5) MVP validation & rollout (2 weeks)
   - Run MVP on subset of endpoints; collect feedback
   - Iterate on improvement backlog

Acceptance Criteria (Definition of Done)
- Metrics captured for at least 2 representative API endpoints in scope with p50/p95 latency and error rate collected for 14 days baseline
- Ingested data stored with durable schema and accessible by query
- Dashboards exist and display real metrics for live endpoints
- Alerts/SLIs defined and tested with sample incidents
- Documentation updated with data model, instrumentation, and dashboards

Kanban tasks (lightweight)
To Do
- [ ] List in-scope endpoints and agree on SLO targets
- [ ] Design minimal data model schema
- [ ] Choose ingestion/storage approach and configure wiring
- [ ] Draft initial dashboard sketches
- [ ] Draft rollout plan and permissions
In Progress
- [ ] Implement latency and error tracking on instrumented endpoints
- [ ] Instrument gateway/backend with tracing hooks
- [ ] Set up data validation and sampling rules
Done
- [ ] Baseline data collection run (14 days) planning
- [ ] Publish MAP-ATLAS.md and share with team

Notes
- Keep MVP small; iterate quickly
- Ensure privacy and data minimization; avoid PII in metrics
- Schedule regular reviews to adapt metrics as product evolves
