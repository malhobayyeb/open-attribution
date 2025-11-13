# PROGRESS.md

## Snapshot (2024-03-05)
- **Postback API:** Stable ingress endpoints live; working on cache automation and Kafka observability.
- **Analytics (ClickHouse):** Core tables + MVs deployed; integration tests pending.
- **Dashboard Backend:** Overview endpoint functional; pagination + RBAC in progress.
- **Dashboard Frontend:** Analytics UI live; needs tests and heavy-load optimizations.

---

## Completed Milestones
- ✅ Postback validation + enrichment pipeline (UUID/IFA checks, GeoIP).
- ✅ Kafka → ClickHouse ingestion pipeline with installs/attribution views.
- ✅ Dashboard MVP (overview charts, admin CRUD, date-range redirects).
- ✅ Marketing site + docs scaffolding.

---

## In Progress
- ⟳ Metadata cache automation (share links / `.well-known` refresh hooks).  
  - *Owner:* Backend team  
  - *Dependencies:* Postgres change events
- ⟳ ClickHouse integration tests using synthetic datasets.  
  - *Owner:* Data team  
  - *Status:* Schema fixtures ready
- ⟳ Dashboard API pagination & RBAC.  
  - *Owner:* Platform team  
  - *Status:* API contract drafted, awaiting frontend wiring
- ⟳ Frontend test suite (filters, tables, forms).  
  - *Owner:* UI team  
  - *Status:* Component harness under review

---

## Blockers / Risks
- ⚠ Lack of automated tests across services — delaying CI adoption.
- ⚠ No centralized logging/metrics; difficult to triage Kafka/ClickHouse issues.
- ⚠ Frontend client-side aggregation may struggle with large datasets.

---

## Metrics
- **Commits (last 14 days):** 28
- **Issues Resolved:** 6 (postback validation #102, share link UX #117, dash filters #123, etc.)
- **Open Issues:** 12 (testing, observability, pagination, docs)

---

## Next Updates
- [ ] Add CI workflows for backend + frontend tests.
- [ ] Document schema contracts for SDKs and analytics.
- [ ] Publish operator runbook for deploying docker-compose stack.
- [ ] Build ClickHouse attribution test harness that replays sample payloads end-to-end.
- [ ] Automate metadata cache refresh between dashboard CRUD endpoints and postback runtime stores.
- [ ] Instrument Kafka/ClickHouse/dash services with basic health and lag metrics.
