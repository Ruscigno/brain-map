#!/usr/bin/env python3
"""Fill gaps identified by cross-referencing docs/sander-garcia-resume-backend-en-2026.pdf
against the current mind map.

Adds 5 new root branches and patches two surgical additions
(TDD under Testing strategies, APM under Observability and Monitoring).

Idempotent — if a root already exists, it's skipped. If a leaf already
exists in a target parent, it's skipped.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = ROOT / "public" / "mindmap.json"


def detail_title(definition: str, trade_offs: str, application: str) -> str:
    return (
        f"**Definition:** {definition}<br/>"
        f"**Trade-offs:** {trade_offs}<br/>"
        f"**Application Example:** {application}"
    )


# ─── 5 new root branches ─────────────────────────────────────────────────
NEW_ROOTS: list[dict] = [
    {
        "title": "Serverless / FaaS",
        "note": "Run functions or containers on demand without managing servers — pay per invocation, scale to zero, leave capacity planning to the cloud.",
        "children": [
            {"title": "Function-as-a-Service (FaaS)"},
            {"title": "AWS Lambda"},
            {"title": "GCP Cloud Run"},
            {"title": "Cloud Run Jobs (batch / async)"},
            {"title": "Cold starts"},
            {"title": "When to use serverless vs containers"},
        ],
    },
    {
        "title": "Container orchestration",
        "note": "Running containerized services at scale — packaging, scheduling, networking, scaling, and self-healing.",
        "children": [
            {"title": "Docker"},
            {"title": "Kubernetes (core)"},
            {"title": "Pods, Deployments, Services"},
            {"title": "Helm"},
            {"title": "Managed Kubernetes (EKS / GKE / AKS) and ECS"},
            {"title": "Horizontal Pod Autoscaler (HPA)"},
        ],
    },
    {
        "title": "Design Patterns",
        "note": "The Gang-of-Four catalogue plus the architectural patterns senior engineers reach for. Vocabulary that lets you discuss design without re-deriving solutions every time.",
        "children": [
            {
                "title": "Creational",
                "note": "Patterns that abstract **how** objects are created.",
                "children": [
                    {"title": "Singleton"},
                    {"title": "Factory (Method / Abstract Factory)"},
                    {"title": "Builder"},
                ],
            },
            {
                "title": "Structural",
                "note": "Patterns about **how objects are composed** into larger structures.",
                "children": [
                    {"title": "Adapter"},
                    {"title": "Decorator"},
                    {"title": "Facade"},
                ],
            },
            {
                "title": "Behavioral",
                "note": "Patterns about **how objects communicate and coordinate** at runtime.",
                "children": [
                    {"title": "Observer"},
                    {"title": "Strategy"},
                    {"title": "Command"},
                ],
            },
            {
                "title": "Architectural patterns",
                "note": "Patterns operating at the system/service level rather than within one class.",
                "children": [
                    {"title": "Repository"},
                    {"title": "Hexagonal / Ports & Adapters"},
                    {"title": "CQRS"},
                    {"title": "Event Sourcing"},
                ],
            },
        ],
    },
    {
        "title": "Data Warehousing & Analytics",
        "note": "How analytical workloads differ from operational ones — modelling, loading, and querying for reporting at scale.",
        "children": [
            {"title": "OLTP vs OLAP"},
            {"title": "ETL vs ELT"},
            {"title": "Star schema"},
            {"title": "Snowflake schema"},
            {"title": "Fact tables vs Dimension tables"},
            {"title": "Data Lake vs Data Warehouse vs Lakehouse"},
            {"title": "Slowly Changing Dimensions (SCD Type 1 / 2 / 3)"},
            {"title": "Data governance & data quality"},
        ],
    },
    {
        "title": "SOLID & Clean Code Principles",
        "note": "The vocabulary every senior engineer is expected to use comfortably when discussing code quality and design trade-offs.",
        "children": [
            {"title": "SRP — Single Responsibility Principle"},
            {"title": "OCP — Open/Closed Principle"},
            {"title": "LSP — Liskov Substitution Principle"},
            {"title": "ISP — Interface Segregation Principle"},
            {"title": "DIP — Dependency Inversion Principle"},
            {"title": "DRY — Don't Repeat Yourself"},
            {"title": "KISS — Keep It Simple, Stupid"},
            {"title": "YAGNI — You Aren't Gonna Need It"},
        ],
    },
]


# ─── 2 surgical additions to existing roots ──────────────────────────────
# Each entry: (root_title, parent_path_tuple_under_root, leaf_dict_to_append)
SURGICAL: list[tuple[str, tuple[str, ...], dict]] = [
    (
        "Testing strategies",
        (),  # append directly under the root
        {"title": "TDD (Test-Driven Development)"},
    ),
    (
        "Observability and Monitoring",
        (),  # append directly under the root
        {"title": "APM (Application Performance Monitoring)"},
    ),
]


# ─── Details ────────────────────────────────────────────────────────────
DETAILS: dict[str, tuple[str, str, str]] = {
    # ─── Serverless / FaaS
    "Serverless / FaaS > Function-as-a-Service (FaaS)": (
        "Cloud execution model where you deploy individual **functions** that run on demand in fully-managed runtimes; you pay per invocation + per ms of execution, not for idle capacity.",
        "Zero infra ops and elastic auto-scaling from 0, but cold starts, vendor lock-in, execution-time limits, and stateless-only nature constrain the architecture.",
        "An image-resize Lambda triggered by S3 `ObjectCreated` events — scales from 0 to thousands/sec automatically, costs nothing while idle.",
    ),
    "Serverless / FaaS > AWS Lambda": (
        "Amazon's FaaS — runs your function on Amazon-managed micro-VMs (Firecracker), triggered by AWS events (API Gateway, S3, SQS, EventBridge) or direct HTTP.",
        "Deep AWS integration with every event source, but 15-minute max execution, 10 GB memory cap, and cold-start latency (~100 ms–1 s) for the first invocation per concurrency.",
        "A `GET /users/{id}` backed by API Gateway + Lambda + DynamoDB — fully serverless, scales from 1 to 10k RPS without any provisioning.",
    ),
    "Serverless / FaaS > GCP Cloud Run": (
        "GCP's container-based serverless platform — deploy **any container**, GCP scales it from 0 to N based on traffic. Stateless HTTP services with up to 60-minute requests.",
        "More flexible than Lambda (any container, not a constrained function signature) and easier portability, but still has cold starts and request-driven scaling — long-lived connections need Cloud Run on GKE.",
        "A Python FastAPI service deployed as a Cloud Run revision that scales to 0 overnight, spins up 50 instances during the morning burst, scales back down at lunch.",
    ),
    "Serverless / FaaS > Cloud Run Jobs (batch / async)": (
        "Cloud Run variant for **batch / async** work — runs a container to completion (no HTTP), supports parallel tasks, timeouts up to 24 h, retries on failure.",
        "Great for ETL, data migrations, and scheduled batch without managing K8s `CronJobs`, but no persistent state between executions and quota limits per region.",
        "A nightly Python job reconciling invoices, triggered by Cloud Scheduler → Pub/Sub → Cloud Run Jobs — 16 parallel tasks each processing a slice of accounts.",
    ),
    "Serverless / FaaS > Cold starts": (
        "Latency penalty when the platform must initialize a new instance (load runtime, your code, deps) before serving the first request.",
        "Invisible at sustained scale (warm instances absorb most traffic), but kills latency-sensitive APIs with bursty patterns; mitigated by provisioned concurrency, smaller deployment packages, lighter runtimes.",
        "A 512 MB Lambda with a 50 MB Python deployment package shows ~800 ms cold start; switching to Lambda SnapStart or provisioned concurrency drops it to <100 ms.",
    ),
    "Serverless / FaaS > When to use serverless vs containers": (
        "Rule of thumb — **serverless** wins for event-driven, bursty, unpredictable traffic and short-lived tasks; **containers** win for steady traffic, long-lived connections, complex deps, or full runtime control.",
        "Serverless cost scales with usage (great for low/spiky) but can exceed containers at sustained high load; containers have predictable cost but require capacity planning.",
        "Webhook receivers, scheduled jobs, image processing → Lambda / Cloud Run. WebSocket servers, ML model servers, long-running background workers → containers on ECS / GKE.",
    ),
    # ─── Container orchestration
    "Container orchestration > Docker": (
        "Containerization platform that packages an application with its deps into an immutable image and runs it as an isolated process sharing the host kernel via cgroups + namespaces.",
        "Reproducible \"works on my machine → works in prod\" builds with sub-second startup vs VMs, but adds an abstraction layer and a learning curve (Dockerfile, networking, volumes, layer cache).",
        "A multi-stage `Dockerfile` building a Go binary in a `golang:1.22-alpine` builder stage then copying to a 5 MB `gcr.io/distroless/static` runtime stage.",
    ),
    "Container orchestration > Kubernetes (core)": (
        "The de-facto container orchestrator — **declarative** API (YAML manifests describing desired state), self-healing **reconciliation loop**, scheduling, networking, secrets, scaling.",
        "Solves real distributed-systems problems (auto-scaling, rolling deploys, service discovery, health checks) but has a steep learning curve and many sharp edges (networking, storage, security).",
        "A 200-pod e-commerce platform deployed via Helm charts to EKS — HPA on CPU + custom metrics, rolling deploys via ArgoCD, ingress via `nginx-ingress`.",
    ),
    "Container orchestration > Pods, Deployments, Services": (
        "**Pod** = smallest deployable unit (1+ containers sharing network/storage). **Deployment** = declarative spec for N replicas of a Pod with rolling-update strategy. **Service** = stable virtual IP load-balancing across matching Pods.",
        "The fundamental K8s vocabulary; learning these three covers 80 % of daily work, but the abstractions hide complexity (kube-proxy iptables rules, Endpoints controller, DNS).",
        "A `Deployment` of 5 `payments-api` replicas, fronted by a ClusterIP `Service` named `payments`, accessed by other pods as `http://payments.default.svc.cluster.local`.",
    ),
    "Container orchestration > Helm": (
        "Kubernetes package manager — bundles related manifests into a **chart** with templated values and a release lifecycle (install / upgrade / rollback).",
        "De-facto standard for installing third-party software and parametrizing your own deploys, but template debugging is painful and complex charts become spaghetti.",
        "`helm install postgres bitnami/postgresql --values production.yaml` to install a parametrized Postgres release; same chart can deploy dev/staging/prod by swapping values files.",
    ),
    "Container orchestration > Managed Kubernetes (EKS / GKE / AKS) and ECS": (
        "**Managed K8s** = cloud-run control plane (EKS / GKE / AKS); you manage workloads and (optionally) nodes. **ECS** = AWS's simpler non-K8s container orchestrator using task definitions and Fargate.",
        "Managed K8s eliminates painful control-plane ops at the cost of tying you to one cloud's networking/IAM model; ECS has a much shallower learning curve than K8s but less ecosystem.",
        "A startup running GKE Autopilot — no node management at all, just deploy pods and pay per pod-time. A simpler AWS team running ECS Fargate to avoid the K8s learning curve.",
    ),
    "Container orchestration > Horizontal Pod Autoscaler (HPA)": (
        "K8s controller that scales the number of pods in a Deployment based on observed metrics (CPU, memory, or custom metrics like RPS, queue depth).",
        "Automatic capacity that responds to real load, but scale-up has a ramp-up window (image pull, container start, readiness probe), and aggressive scaling thrashes on noisy metrics.",
        "HPA scaling the `api` Deployment between 5 and 200 replicas based on `cpu > 70 %` and `requests-per-second > 1000`, with `kube-state-metrics` exposing the custom metric.",
    ),
    # ─── Design Patterns > Creational
    "Design Patterns > Creational > Singleton": (
        "Restrict a class to a single instance and provide a global access point to it.",
        "Useful for genuine global resources (config, logger, connection pool), but easy to abuse — singletons are global state that breaks testability and hides dependencies; many \"singletons\" should be a dependency-injected interface instead.",
        "A `DBConnectionPool.getInstance()` returning the single shared pool; better-tested alternative: a single instance held by a DI container and injected into every service.",
    ),
    "Design Patterns > Creational > Factory (Method / Abstract Factory)": (
        "Encapsulate object creation behind a method or factory class so callers don't depend on concrete types — `Factory.create(type)` returns the right subclass.",
        "Decouples callers from implementations and enables runtime swapping, at the cost of more classes / indirection for small hierarchies where a simple `switch` would do.",
        "A `PaymentGatewayFactory.create(\"stripe\")` returning a `StripeGateway`; switching providers later is a one-line change in the factory.",
    ),
    "Design Patterns > Creational > Builder": (
        "Construct complex objects step-by-step with a fluent API: `Pizza.builder().crust(\"thin\").addTopping(\"olive\").build()`.",
        "Replaces telescoping constructors and named-argument blocks with a readable, validated build flow, but adds a parallel builder class for every type and most modern languages have ergonomic alternatives (kwargs, options structs).",
        "An `HttpRequest.builder().url(u).header(\"Auth\", t).timeout(2.s).build()` chain in a Java client library; in Go the same shape is usually `Options struct` + functional options.",
    ),
    # ─── Design Patterns > Structural
    "Design Patterns > Structural > Adapter": (
        "Wrap an existing class with a new interface so it fits an expected API — `LegacyAdapter implements ModernAPI` delegating to the legacy implementation.",
        "Lets new code talk to old or third-party APIs without modifying either, but every adapter is a layer of indirection and a maintenance surface.",
        "Wrapping a legacy XML SOAP client in an `OrdersRepository` adapter so the new microservice can talk to `OrdersRepository.findById(id)` and not care about the SOAP envelope.",
    ),
    "Design Patterns > Structural > Decorator": (
        "Wrap an object with another that adds behaviour while preserving its interface — `LoggingHandler(MetricsHandler(BaseHandler))`.",
        "Compose cross-cutting concerns (logging, metrics, retries, caching) without modifying the wrapped class, but stacking many decorators makes the call chain hard to debug.",
        "Go HTTP middleware: `mux.Handle(\"/api\", LoggingMW(AuthMW(MetricsMW(handler))))` — each middleware decorates the handler with one concern.",
    ),
    "Design Patterns > Structural > Facade": (
        "Provide a simple, high-level interface in front of a complex subsystem, hiding its internals from callers.",
        "Massively reduces cognitive load for clients of complex modules, but a facade that grows unbounded becomes a \"god object\" that drags everything else along with it.",
        "An `OrderService.placeOrder(req)` facade hiding inventory checks, payment authorization, fraud screening, and email notification — callers see one method instead of five.",
    ),
    # ─── Design Patterns > Behavioral
    "Design Patterns > Behavioral > Observer": (
        "Define a one-to-many dependency so when one object changes, all its subscribers are notified — the foundation of pub/sub and event-driven UIs.",
        "Decouples publishers from subscribers (publisher doesn't know who's listening), but failure modes are subtle — a slow subscriber can stall the publisher unless notifications are async.",
        "A `User` aggregate publishing `UserSignedUp` events that the email, billing, and analytics services subscribe to independently (the same pattern as the Msg/EDD branch).",
    ),
    "Design Patterns > Behavioral > Strategy": (
        "Define a family of interchangeable algorithms behind a common interface and let the caller pick one at runtime: `sorter.sort(list, strategy)`.",
        "Replace conditional logic with polymorphism so adding a new variant doesn't touch the caller, at the cost of one class per strategy.",
        "A `PricingStrategy` interface with `RegularPricing`, `BlackFridayPricing`, `MemberPricing` implementations swapped at runtime based on campaign config.",
    ),
    "Design Patterns > Behavioral > Command": (
        "Encapsulate a request as an object so it can be queued, logged, undone, or sent over the wire: `cmd := SendEmailCommand{...}; queue.Push(cmd)`.",
        "Decouples the invoker from the executor and enables async / queueing / undo / audit, but introduces a parallel hierarchy of command classes for every operation.",
        "An `ExecuteCommand` interface used by both an in-process executor and a SQS consumer; the same command class is queued in async flows and replayed for audit.",
    ),
    # ─── Design Patterns > Architectural
    "Design Patterns > Architectural patterns > Repository": (
        "Mediate between the domain model and the data layer with a collection-like interface — `userRepo.findById(id)`, `userRepo.save(u)` — hiding SQL, ORM, or cache details.",
        "Centralizes persistence concerns and makes domain code DB-agnostic / mockable, but a generic `Repository<T>` over-abstracts and a thin pass-through repo is just SQL with extra steps.",
        "A `OrderRepository` interface implemented by `PostgresOrderRepository` and `InMemoryOrderRepository` (for tests); the order-service code depends only on the interface.",
    ),
    "Design Patterns > Architectural patterns > Hexagonal / Ports & Adapters": (
        "Put domain logic in the centre with **ports** (interfaces) for everything outside (DB, HTTP, queues); **adapters** implement those ports per technology. Domain depends on nothing infrastructure.",
        "Maximally testable and tech-swappable (you can replace Postgres with Mongo without touching domain), but more upfront design + more files for small projects where the trade-off doesn't pay off.",
        "A `notifier` domain service depending on a `Notifier` port; `SlackAdapter`, `EmailAdapter`, `SmsAdapter` implement the port. Domain has no `import slack`.",
    ),
    "Design Patterns > Architectural patterns > CQRS": (
        "Command-Query Responsibility Segregation — separate write model (commands modifying state) from read model (queries optimized for views), often with different stores and even different schemas.",
        "Lets reads scale independently of writes and tailor read models to UI needs, but doubles the model surface, introduces eventual consistency between sides, and is overkill for CRUD apps.",
        "A trading app where writes go through a normalized `orders` Postgres table and reads come from a denormalized `order_summary_view` materialized in Elasticsearch, refreshed by events.",
    ),
    "Design Patterns > Architectural patterns > Event Sourcing": (
        "Store the application state as a log of immutable events; the current state is **derived** by replaying events. The event log is the source of truth, not the latest row.",
        "Perfect audit trail, time travel, and natural fit for CQRS, but rebuilding state is expensive at scale, schema evolution of old events is hard, and most teams don't actually need it.",
        "A bank ledger storing `MoneyDeposited`, `MoneyWithdrawn` events instead of a `balance` column — the balance is computed by replaying events; corrections are new events, never updates.",
    ),
    # ─── Data Warehousing & Analytics
    "Data Warehousing & Analytics > OLTP vs OLAP": (
        "**OLTP** (Online Transaction Processing) handles many small writes/reads against a normalized schema (banking, e-commerce). **OLAP** (Online Analytical Processing) runs large aggregating reads against denormalized schemas (BI, reporting).",
        "Different access patterns demand different storage and schema: OLTP for row stores (Postgres, MySQL), OLAP for columnar stores (BigQuery, Snowflake, Redshift); mixing them on one DB causes contention.",
        "A retail app keeping `orders`, `items`, `customers` in Postgres for transactions and ETL-loading them into BigQuery for the analytics team's dashboards.",
    ),
    "Data Warehousing & Analytics > ETL vs ELT": (
        "**ETL** = Extract → Transform → Load (transform in a separate stage before loading the warehouse). **ELT** = Extract → Load → Transform (load raw data, transform inside the warehouse with SQL / dbt).",
        "ETL gives more control and works for legacy on-prem warehouses, but ELT exploits modern cloud warehouses' compute and makes transformations versioned, testable, and observable in SQL.",
        "An invoice pipeline doing CDC from Postgres → Pub/Sub → BigQuery raw zone, then dbt models transforming raw rows into reporting tables — pure ELT.",
    ),
    "Data Warehousing & Analytics > Star schema": (
        "Dimensional modelling layout with a central **fact table** (measures, foreign keys) surrounded by **dimension tables** (descriptive attributes) joined directly to the fact.",
        "Easy for BI tools to navigate and very fast aggregation queries, at the cost of dimensional denormalization (the same attribute repeated across rows).",
        "A `fact_sales` table with `customer_id`, `product_id`, `date_id`, `revenue` joined to `dim_customer`, `dim_product`, `dim_date` for sales dashboards.",
    ),
    "Data Warehousing & Analytics > Snowflake schema": (
        "Variant of the star schema where dimension tables are further **normalized** into sub-dimensions (e.g., `dim_product` → `dim_category` → `dim_department`).",
        "Saves storage and reduces update anomalies on rarely-changing attributes, but adds joins that slow common BI queries and complicate tooling.",
        "A retail warehouse where `dim_store` is normalized into `dim_store` → `dim_region` → `dim_country` so renaming a country touches one row, not millions.",
    ),
    "Data Warehousing & Analytics > Fact tables vs Dimension tables": (
        "**Fact tables** hold quantitative measurements (revenue, count, duration) with foreign keys to dimensions. **Dimension tables** hold descriptive attributes (customer, product, date) and act as filter / group-by axes.",
        "Clear separation makes BI semantics explicit and queries fast, but \"is this a fact or a dimension?\" gets blurry for slowly-changing attributes and semi-additive measures.",
        "`fact_orders` with `order_id`, `customer_id`, `product_id`, `date_id`, `amount`; dimension tables described per row — `dim_customer` has 5 M rows of customer attributes.",
    ),
    "Data Warehousing & Analytics > Data Lake vs Data Warehouse vs Lakehouse": (
        "**Data Lake** = raw files (JSON, Parquet, CSV) in object storage with schema-on-read. **Data Warehouse** = curated tables with schema-on-write. **Lakehouse** = warehouse semantics on top of lake storage (Delta Lake, Iceberg, Hudi).",
        "Lake is cheap and flexible but slow to query without indexing; warehouse is fast but expensive and rigid; lakehouse promises the best of both at the cost of more tooling complexity.",
        "Raw clickstream JSON dumped to S3 (lake) → Delta Lake tables with ACID guarantees (lakehouse) → curated marts in Snowflake (warehouse) — different stages, same physical storage tier.",
    ),
    "Data Warehousing & Analytics > Slowly Changing Dimensions (SCD Type 1 / 2 / 3)": (
        "Strategies for tracking dimension attribute changes over time. **Type 1**: overwrite, no history. **Type 2**: insert a new row with `valid_from` / `valid_to`. **Type 3**: keep a `previous_value` column.",
        "Type 2 preserves full history and enables \"point-in-time\" analytics, at the cost of row explosion and join complexity; Type 1 is simplest but loses history.",
        "Customer address changes: Type 2 inserts a new `dim_customer` row with the new address and closes the old row's `valid_to` — yesterday's sales still join to yesterday's address.",
    ),
    "Data Warehousing & Analytics > Data governance & data quality": (
        "Policies, processes, and tools that ensure data is **trustworthy, discoverable, and compliant**: lineage, ownership, glossaries, quality tests, retention, access control, PII handling.",
        "Critical at scale (without it, every dashboard becomes \"are the numbers right?\"), but introduces process overhead, requires cross-team buy-in, and is hard to retrofit onto an existing data swamp.",
        "A dbt project running automated tests (`not_null`, `unique`, custom row-count checks) on every model + an Atlan / OpenMetadata catalog showing ownership, lineage, and last-refreshed-at for every dataset.",
    ),
    # ─── SOLID & Clean Code Principles
    "SOLID & Clean Code Principles > SRP — Single Responsibility Principle": (
        "A class / module should have **one reason to change** — one stakeholder, one axis of variation.",
        "Produces small, focused, easy-to-test units, but \"responsibility\" is fuzzy and over-applied SRP fragments the codebase into hundreds of tiny classes that obscure intent.",
        "Splitting a `UserService` that handled auth, email sending, and DB persistence into `Authenticator`, `EmailSender`, and `UserRepository` — each changes for one independent reason.",
    ),
    "SOLID & Clean Code Principles > OCP — Open/Closed Principle": (
        "Modules should be **open for extension, closed for modification** — add new behaviour by adding new code, not by editing the existing class.",
        "Enables safe extension in stable codebases (plugins, strategies), but premature OCP creates abstract hierarchies for features that never materialize.",
        "Adding a new `BlackFridayPricing` strategy without touching the existing `PricingStrategy` interface or its `RegularPricing` implementation — just one new class.",
    ),
    "SOLID & Clean Code Principles > LSP — Liskov Substitution Principle": (
        "Subtypes must be **substitutable** for their base types without breaking callers — a subclass must honour every contract its parent declared.",
        "Catches the most insidious inheritance bugs (square-is-a-rectangle), but is impossible to verify automatically and gets ignored in dynamic languages.",
        "A `ReadOnlyList` that inherits from `List` and overrides `add()` to throw is an LSP violation — callers expecting `add()` to work break unexpectedly. Fix: `ReadOnlyList` shouldn't inherit from `List` at all.",
    ),
    "SOLID & Clean Code Principles > ISP — Interface Segregation Principle": (
        "Clients should not be forced to depend on methods they don't use — prefer many small, role-specific interfaces over one big general one.",
        "Reduces accidental coupling and keeps test mocks small, but too-many-interfaces creates a forest of one-method types and refactoring costs.",
        "Splitting a fat `IUserRepository` (with `find`, `save`, `delete`, `searchByEmail`, `audit`, `export`) into `Reader`, `Writer`, `Searcher` so the report job only depends on `Reader`.",
    ),
    "SOLID & Clean Code Principles > DIP — Dependency Inversion Principle": (
        "High-level modules should depend on **abstractions**, not on low-level concrete modules; abstractions should not depend on details.",
        "Enables dependency injection, testability, and swap-out of infrastructure, but indirection adds friction for simple cases and can over-abstract.",
        "An `OrderService` depending on a `PaymentGateway` interface (abstraction) rather than `StripeClient` directly — `StripeGateway` and `MockGateway` both implement it.",
    ),
    "SOLID & Clean Code Principles > DRY — Don't Repeat Yourself": (
        "Every piece of knowledge should have a single, unambiguous representation in the system — duplication is the enemy of change.",
        "Eliminates update anomalies (where the same fact changes in some places but not others), but over-applied DRY couples unrelated code that happened to look the same — \"three similar lines is better than a premature abstraction.\"",
        "Extracting a `formatCurrency(amount, locale)` helper used in three views; *not* extracting two 5-line methods that happen to share four lines but model different domain concepts.",
    ),
    "SOLID & Clean Code Principles > KISS — Keep It Simple, Stupid": (
        "Prefer the simplest design that meets the requirement — complexity should be justified by need, not by anticipation.",
        "Faster shipping and easier maintenance, but \"simple\" is subjective and engineers reaching for clever one-liners often mistake them for simple.",
        "Using a 50-line Python script for a one-time migration instead of building a configurable framework; using a list of structs instead of a generic event bus when there are three event types.",
    ),
    "SOLID & Clean Code Principles > YAGNI — You Aren't Gonna Need It": (
        "Don't implement functionality based on speculative future need — add it when the need actually arrives.",
        "Avoids dead code, premature abstractions, and over-engineering, but can be misread as an excuse to ship cardboard — \"you might need it\" abstractions for known infrastructure (auth, logging) are not YAGNI violations.",
        "Resisting the urge to add multi-tenant support to a single-tenant MVP \"in case we add tenants later\" — adding it actually takes one sprint when tenants arrive, vs paying the complexity tax for years.",
    ),
    # ─── Surgical additions
    "Testing strategies > TDD (Test-Driven Development)": (
        "Workflow where you **write a failing test first**, write the minimum production code to make it pass, then refactor — the red-green-refactor cycle.",
        "Drives small, testable designs and gives you an executable spec, but slows down exploratory / spike work and can degenerate into over-mocked tests that pin implementation.",
        "Writing `TestValidEmailReturnsTrue` first, watching it fail, implementing `IsValidEmail` until it passes, then refactoring the implementation while the test keeps it honest.",
    ),
    "Observability and Monitoring > APM (Application Performance Monitoring)": (
        "Tooling that combines distributed tracing, metrics, error tracking, and code-level profiling into one product so you can answer \"why is this request slow?\" without correlating across silos.",
        "Drastically shortens MTTR by stitching traces, metrics, and logs through one UI, but expensive per host / per ingestion volume and ties you to one vendor's instrumentation library.",
        "Datadog APM auto-instrumenting a Go service: every request shows up as a trace with DB query timings, downstream calls, runtime metrics, and a flame graph — incident triage drops from hours to minutes.",
    ),
}


# ─── Application ─────────────────────────────────────────────────────────
def apply_details_to_new_root(root: dict, missing: list[str]) -> int:
    applied = 0

    def walk(node: dict, path: list[str]) -> None:
        nonlocal applied
        children = node.get("children")
        if children:
            for c in children:
                walk(c, path + [c["title"]])
            return
        # leaf
        full_path = " > ".join(path)
        if full_path not in DETAILS:
            missing.append(full_path)
            return
        d, t, x = DETAILS[full_path]
        node["children"] = [{"title": detail_title(d, t, x)}]
        applied += 1

    walk(root, [root["title"]])
    return applied


def add_surgical_leaf(root_children: list[dict], root_title: str, leaf: dict, missing: list[str]) -> bool:
    """Append `leaf` to `root_children`, attaching its Detail child.
    Returns True if added, False if a leaf with the same title was already there."""
    if any(c["title"] == leaf["title"] for c in root_children):
        return False
    full_path = f"{root_title} > {leaf['title']}"
    if full_path not in DETAILS:
        missing.append(full_path)
        return False
    d, t, x = DETAILS[full_path]
    leaf["children"] = [{"title": detail_title(d, t, x)}]
    root_children.append(leaf)
    return True


def main() -> None:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    existing_titles = {c["title"] for c in data["children"]}

    appended: list[str] = []
    skipped_roots: list[str] = []
    surgical_added: list[str] = []
    surgical_skipped: list[str] = []
    missing: list[str] = []
    total_details = 0

    # Roots
    for new_root in NEW_ROOTS:
        if new_root["title"] in existing_titles:
            skipped_roots.append(new_root["title"])
            continue
        n = apply_details_to_new_root(new_root, missing)
        total_details += n
        data["children"].append(new_root)
        appended.append(f"{new_root['title']} ({n} leaves)")

    # Surgical
    for root_title, _parent_path, leaf in SURGICAL:
        root = next((c for c in data["children"] if c["title"] == root_title), None)
        if root is None:
            missing.append(f"Surgical: root {root_title!r} not found")
            continue
        root.setdefault("children", [])
        if add_surgical_leaf(root["children"], root_title, leaf, missing):
            surgical_added.append(f"{root_title} → {leaf['title']}")
            total_details += 1
        else:
            surgical_skipped.append(f"{root_title} → {leaf['title']}")

    if missing:
        print("MISSING / ERROR:")
        for m in missing:
            print(f"  - {m}")
        raise SystemExit(1)

    JSON_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print("Appended root branches:")
    for a in appended:
        print(f"  + {a}")
    if skipped_roots:
        print("Skipped roots (already present):")
        for s in skipped_roots:
            print(f"  · {s}")
    print()
    print("Surgical leaf additions:")
    for s in surgical_added:
        print(f"  + {s}")
    if surgical_skipped:
        print("Skipped surgical (already present):")
        for s in surgical_skipped:
            print(f"  · {s}")
    print()
    print(f"Total new detail nodes added: {total_details}")


if __name__ == "__main__":
    main()
