#!/usr/bin/env python3
"""One-shot script: for every leaf in public/mindmap.json, append a child
'Detail' node containing **Definition** / **Trade-offs** / **Application Example**.

Idempotent: if a leaf already has a child whose title starts with
'**Definition:**', the script leaves it alone.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = ROOT / "public" / "mindmap.json"

# Map FULL PATH (root > ... > leaf as a single string with " > " separator)
# to (definition, trade_offs, application_example).
# Keys must match the leaf path exactly.
DETAILS: dict[str, tuple[str, str, str]] = {
    # ───────────────────────────────────── Scalability and Load ─────
    "Scalability and Load > Vertical Scalability (Scaling Up)": (
        "Scale-up approach that increases capacity by adding more resources (CPU, RAM, storage, IOPS) to a single machine.",
        "Simple with no application changes and avoids distributed-system complexity, but is bounded by hardware ceilings, becomes exponentially expensive, and leaves a Single Point of Failure (SPOF).",
        "Upgrading a primary OLTP database server to a larger AWS RDS instance class (e.g., db.r6g.large to db.r6g.16xlarge) to absorb traffic spikes before sharding.",
    ),
    "Scalability and Load > Horizontal Scalability (Scaling Out)": (
        "Scale-out approach that adds more machine instances behind a load balancer instead of growing one machine.",
        "Removes the SPOF and scales nearly linearly, but requires the application to be stateless and adds operational complexity (deployments, partial failures, more network hops).",
        "An auto-scaling group of 20 stateless API pods behind an AWS ALB, with HPA adding pods when CPU > 70%.",
    ),
    "Scalability and Load > Load Balancers > Algorithms > Round Robin": (
        "Sends each new request to the next backend in a fixed rotation.",
        "Trivial and uniform when servers are equal, but ignores actual server load — a slow backend gets the same share as a fast one.",
        "An nginx `upstream` block fronting four equally-sized stateless workers with the default round-robin policy.",
    ),
    "Scalability and Load > Load Balancers > Algorithms > Least Connections": (
        "Routes each new request to the backend currently holding the fewest active connections.",
        "Naturally balances long-lived sessions and slow clients, but requires the LB to track per-backend state, which is harder in distributed LB setups.",
        "HAProxy with `balance leastconn` in front of WebSocket servers where some clients hold connections for hours.",
    ),
    "Scalability and Load > Load Balancers > Algorithms > IP Hash": (
        "Hashes the client IP and consistently maps it to the same backend.",
        "Cheap stickiness without a session store, but breaks when clients share a NAT/IP and rebalances poorly when the backend pool changes.",
        "A legacy PHP app needing in-process session affinity, fronted by an nginx upstream configured with `ip_hash`.",
    ),
    "Scalability and Load > Load Balancers > Layers > Layer 4 (TCP)": (
        "Load balancing at the transport layer — routes by IP and port, blind to HTTP semantics.",
        "Extremely fast and protocol-agnostic, but cannot route on URL/headers/cookies or terminate TLS at the LB.",
        "AWS NLB fronting a Postgres or Redis cluster where smart routing is unnecessary and ultra-low latency matters.",
    ),
    "Scalability and Load > Load Balancers > Layers > Layer 7 (HTTP)": (
        "Load balancing at the application layer — inspects HTTP requests to route by host, path, header, or cookie.",
        "Enables smart routing (path-based, A/B, canary) and TLS termination, but is slower than L4 and limited to HTTP-like protocols.",
        "AWS ALB / nginx routing `/api/*` to one service and `/static/*` to another, with a 5% weighted canary to a new release.",
    ),
    "Scalability and Load > Statelessness": (
        "Architectural property where each app instance keeps no client-specific state in memory; any instance can serve any request.",
        "Enables horizontal scaling and zero-downtime deploys, but pushes session, cart, and personalization state to an external store (Redis, JWT, DB), adding a dependency.",
        "A stateless Node.js cluster on Kubernetes with sessions in Redis — pods can be killed and replaced without users noticing.",
    ),
    # ──────────────────────────────────────── CAP and PACELC ─────
    "CAP and PACELC Theorems > Consistency": (
        "Every successful read returns the most recent committed write, or an error.",
        "Eliminates stale-read confusion, but requires synchronous replication or quorums, increasing latency and reducing availability under partitions.",
        "A bank ledger replicated synchronously so a balance read from any region always reflects the last debit, even if it slows reads to ~50ms.",
    ),
    "CAP and PACELC Theorems > Availability": (
        "Every request receives a non-error response, even if some replicas are unreachable.",
        "Maximizes uptime, but allows reads of stale data during partitions.",
        "A DynamoDB-backed shopping cart that always lets the user add items, even if the write hasn't replicated to all regions yet.",
    ),
    "CAP and PACELC Theorems > Partition Tolerance": (
        "The system continues operating despite arbitrary message loss or delays between nodes.",
        "Mandatory for any real distributed system (networks always partition), but forces a CAP choice between Consistency and Availability during the partition.",
        "A multi-region database where the EU and US regions each keep accepting traffic if the WAN link drops, then reconcile when it returns.",
    ),
    "CAP and PACELC Theorems > PACELC": (
        "Extends CAP — under Partition you choose A or C; **E**lse (no partition) you still choose between **L**atency and **C**onsistency.",
        "Forces an honest discussion of normal-operation trade-offs that CAP alone glosses over.",
        "Choosing Cassandra (PA/EL) for a recommendation feed where 5ms p99 matters more than reading the absolute latest write.",
    ),
    # ──────────────────────────────────── Databases and Storage ─────
    'Databases and Storage > SQL (Relational, ACID) > ACID — what each letter means > A — Atomicity': (
        "A transaction is all-or-nothing — either every operation persists or none of them do.",
        "Eliminates partial-update bugs but requires undo logs and rollback machinery, costing throughput and storage.",
        "A money-transfer transaction that debits A and credits B in one BEGIN/COMMIT block; a crash mid-transfer leaves both balances unchanged.",
    ),
    'Databases and Storage > SQL (Relational, ACID) > ACID — what each letter means > C — Consistency': (
        "Every committed transaction leaves the database in a state satisfying all declared constraints (PKs, FKs, checks, triggers).",
        "Catches data-integrity bugs at write time, but enforcing constraints — especially across rows or tables — takes locks and CPU.",
        "A FOREIGN KEY from `orders.customer_id` to `customers.id` rejects an order whose customer was already deleted, preventing orphan rows.",
    ),
    'Databases and Storage > SQL (Relational, ACID) > ACID — what each letter means > I — Isolation': (
        "Concurrent transactions are isolated so the result is equivalent to running them in some serial order.",
        "Tunable from Read Uncommitted to Serializable — stronger isolation prevents anomalies (dirty/non-repeatable/phantom reads) but reduces concurrency.",
        "PostgreSQL `SERIALIZABLE` for a seat-booking system to prevent two users from booking the same seat under concurrent transactions.",
    ),
    'Databases and Storage > SQL (Relational, ACID) > ACID — what each letter means > D — Durability': (
        "Once a transaction commits, its effects survive crashes, power loss, and restarts.",
        "Guarantees no committed data is ever lost, but every commit pays the cost of an `fsync` to disk and replication.",
        "PostgreSQL's WAL is `fsync`-flushed before COMMIT returns and shipped to a synchronous standby for additional durability.",
    ),
    "Databases and Storage > SQL (Relational, ACID) > Examples": (
        "Mature relational systems implementing SQL + ACID — PostgreSQL, MySQL, SQL Server, Oracle.",
        "Decades of tooling, mature replication, and rich query optimizers — but vertical-scale-first and harder to shard than NoSQL siblings.",
        "PostgreSQL as the primary OLTP store for a fintech app, using strict isolation for ledgers and read replicas for reporting.",
    ),
    "Databases and Storage > NoSQL > Key-Value": (
        "Schema-less store mapping keys to opaque values, optimized for O(1) lookup.",
        "Extremely fast and simple, but offers no rich query language and no joins — every access pattern must reduce to a key.",
        "Redis cache holding `session:{id} → user_json`, and DynamoDB storing `user_id → profile` for a mobile backend.",
    ),
    "Databases and Storage > NoSQL > Document": (
        "Stores nested JSON-like documents indexed by ID, with secondary indexes and ad-hoc queries on document fields.",
        "Flexible schemas accelerate iteration and match nested aggregates well, but lack of joins or cross-document transactions can push complexity into the app.",
        "MongoDB collection of e-commerce products where each document holds variants, images, and pricing rules together.",
    ),
    "Databases and Storage > NoSQL > Columnar": (
        "Stores data column-by-column rather than row-by-row, optimized for scans/aggregates over a few columns of many rows.",
        "Massive compression and analytical query speed-ups, but write/update-heavy workloads and single-row lookups are slow.",
        "BigQuery or Snowflake powering BI dashboards over a few-billion-row events table; Cassandra for time-series telemetry.",
    ),
    "Databases and Storage > NoSQL > Graph": (
        "Models data as nodes and edges, optimized for traversal queries (shortest path, friend-of-friend, recommendations).",
        "Vastly faster than SQL self-joins for deep traversals, but smaller ecosystem, harder ops, and overkill if relationships are shallow.",
        'Neo4j powering a fraud-detection feature that asks "is this account within 3 hops of a known bad actor?".',
    ),
    "Databases and Storage > Read Replicas": (
        "Read-only DB copies kept in sync with the primary that absorb SELECT traffic.",
        "Cheap horizontal scaling for reads with no app changes, but introduces replication lag — reads can be stale and writes still bottleneck on the primary.",
        "A reporting service pointed at PostgreSQL replicas; writes go to the primary while heavy analytical SELECTs land on a replica.",
    ),
    "Databases and Storage > Indexes & Query Optimization": (
        "B-tree, hash, GIN, and similar indexes plus query rewriting that avoid full table scans.",
        "Reads get orders-of-magnitude faster, but every index slows writes and consumes storage; bad indexes can hurt more than help.",
        "Adding a composite index on `(user_id, created_at)` to turn a 4-second order-history query into a 5-millisecond one.",
    ),
    # ──────────────────────────────────────── Caching Strategies ─────
    "Caching Strategies > Patterns > Read-through": (
        "App always reads from the cache; on a miss the cache itself fetches from the DB, populates, and returns.",
        "App code is simple and consistent, but the first read after a cold start is slow, and the cache library must understand how to query the source.",
        "AWS ElastiCache (Redis) used in read-through mode in front of DynamoDB for product-catalog reads.",
    ),
    "Caching Strategies > Patterns > Write-through": (
        "Every write goes synchronously to both the cache and the DB before returning success.",
        "Cache always reflects the latest data, but writes pay two round-trips and writes that never get read waste cache space.",
        "A user-profile service writing to PostgreSQL and a Redis user-cache so the next profile read is always a cache hit.",
    ),
    "Caching Strategies > Patterns > Write-back (Write-behind)": (
        "Writes hit the cache only; the cache asynchronously flushes batched changes to the underlying DB.",
        "Extremely fast writes that absorb spikes, but a cache crash before flush risks **data loss** — needs durable cache, replication, or an outbox.",
        "A high-volume metrics ingest pipeline buffering counters in Redis and flushing aggregates to ClickHouse every 5 seconds.",
    ),
    "Caching Strategies > Patterns > Cache-aside (Lazy loading)": (
        "App checks the cache; on a miss, queries the DB and explicitly writes the result back.",
        "Most flexible and the de-facto Redis pattern, but the app must invalidate stale entries and handle the thundering herd of misses on hot keys.",
        "A blog rendering service: `redis.get(post_id)` → on miss `db.query(...)` then `redis.setex(post_id, 300, value)`.",
    ),
    "Caching Strategies > Eviction Policies > LRU — Least Recently Used": (
        "Eviction policy that drops the entry untouched for the longest time when the cache is full.",
        "Excellent default — exploits temporal locality — but pathological under one-time scans that evict the genuinely-hot working set.",
        "Redis configured with `maxmemory-policy allkeys-lru` for a session/object cache where recent users are likely active again.",
    ),
    "Caching Strategies > Eviction Policies > LFU — Least Frequently Used": (
        "Eviction policy that drops the entry with the lowest hit count, regardless of recency.",
        "Better than LRU when popularity is stable, but old hits keep new entries out and shifting popularity is hard to adapt to without decayed counters.",
        "Redis `allkeys-lfu` for a CDN edge cache where a small set of evergreen assets dominates traffic.",
    ),
    "Caching Strategies > Eviction Policies > TTL — Time To Live": (
        "Each entry carries an expiry timestamp; the entry is evicted once that time passes regardless of usage.",
        "Bounds staleness without any access tracking, but doesn't react to memory pressure — a cache with all-fresh entries can still fill up.",
        "Auth-token cache with a 15-minute TTL — tokens age out automatically without explicit invalidation logic.",
    ),
    "Caching Strategies > Eviction Policies > FIFO / Random": (
        "FIFO evicts the oldest insert; Random picks any entry uniformly.",
        "Both are O(1) and trivial, but ignore access patterns and usually underperform LRU/LFU on real workloads.",
        "Embedded systems or fallbacks (e.g., Redis `maxmemory-policy allkeys-random`) where simplicity outweighs efficiency.",
    ),
    "Caching Strategies > Layers > CDN (edge)": (
        "Geographically-distributed PoPs caching static assets close to end users at the network edge.",
        "Dramatic latency wins (10–50ms vs. 200ms+) and origin offload, but invalidation is harder farther from origin and dynamic content is harder to cache.",
        "Cloudflare/Fastly fronting an SPA — JS/CSS/images served from the nearest PoP with `Cache-Control: max-age=31536000, immutable` for hashed bundles.",
    ),
    "Caching Strategies > Layers > Application (in-memory)": (
        "Cache lives inside the service process or a shared store like Redis/Memcached, accessed in microseconds.",
        "Sub-ms reads for hot DB queries and computed views, but consistency between instances is your problem and memory is finite.",
        "A pricing service holding a Redis cache of `sku → price`, populated lazily and invalidated by a Kafka topic of price-change events.",
    ),
    "Caching Strategies > Layers > Database (query/result cache)": (
        "The DB engine caches plans, page buffers, and result sets in its own RAM.",
        "Mostly automatic — the DBA tunes RAM and the app gets free wins — but invalidated aggressively on writes and not a substitute for an app-level cache.",
        "PostgreSQL's `shared_buffers` sized to ~25% of RAM so the working set lives in memory and disk reads are rare on hot tables.",
    ),
    # ──────────────────────────── Messaging and Event-Driven Design ─
    "Messaging and Event-Driven Design > Architectural comparison — with vs. without Msg/EDD > WITHOUT Messaging / EDD (synchronous chain) > Symptom": (
        "Failure mode of a synchronous chain — cascading errors and timeouts that propagate back to the user.",
        "Easy to reason about during incidents (one stack trace), but every downstream blip becomes a user-facing failure.",
        "A signup endpoint returning 500 because the analytics service is down, even though signup itself technically succeeded.",
    ),
    "Messaging and Event-Driven Design > Architectural comparison — with vs. without Msg/EDD > WITHOUT Messaging / EDD (synchronous chain) > Fits when": (
        "Scenarios where synchronous chains are the right call — small systems, few services, low traffic, strong-consistency demand.",
        "Simpler architecture and cheaper to operate, but quickly outgrown as services and traffic grow.",
        "A 3-service internal admin tool where every request is HTTP and the team optimizes for ramp-up speed, not throughput.",
    ),
    "Messaging and Event-Driven Design > Architectural comparison — with vs. without Msg/EDD > WITH Messaging / EDD (asynchronous events) > Symptom": (
        "Failure mode with messaging — growing queue lag and duplicate deliveries, but the core path stays up.",
        "Resilient to downstream outages, but you trade clear stack traces for distributed-trace investigations and idempotency requirements.",
        "After a Stripe outage, the `payments` consumer's lag spikes to 4 hours, then drains; users still completed signup and the payment confirms when Stripe recovers.",
    ),
    "Messaging and Event-Driven Design > Architectural comparison — with vs. without Msg/EDD > WITH Messaging / EDD (asynchronous events) > Fits when": (
        "Scenarios where event-driven design pays off — many independent consumers, spiky load, audit/event-sourcing needs.",
        "Loose coupling and elasticity at the cost of eventual consistency and harder debugging.",
        "An e-commerce platform where `OrderPlaced` triggers shipping, billing, fraud-check, and analytics — each scaling and failing independently.",
    ),
    "Messaging and Event-Driven Design > Queues": (
        "Point-to-point messaging where a message is delivered to exactly one consumer from a worker pool.",
        "Reliable work distribution and back-pressure absorption, but harder to add new consumers without coordinated changes.",
        "SQS holding image-resize jobs picked up by an autoscaling pool of workers.",
    ),
    "Messaging and Event-Driven Design > Pub/Sub": (
        "Topic-based messaging where one published message fans out to many independent subscribers.",
        "Producers and consumers are fully decoupled and new consumers can be added at any time, but each subscriber must independently track failures and offsets.",
        "A `UserSignedUp` topic on Kafka feeding the email, billing, and analytics services in parallel.",
    ),
    "Messaging and Event-Driven Design > Kafka": (
        "Distributed, partitioned, replicated commit log that retains messages and allows replay by offset.",
        "Massive throughput and replayability for event-sourcing, but heavier ops (Zookeeper/KRaft, brokers) and a learning curve compared to classic queues.",
        "A clickstream platform ingesting 1M events/sec into a `pageviews` topic, with downstream stream-processors and S3 archivers reading at their own pace.",
    ),
    "Messaging and Event-Driven Design > RabbitMQ": (
        "Classic AMQP broker with rich exchange/binding routing semantics and per-message acks.",
        "Flexible routing (direct, topic, fanout, headers) and operationally simple, but worse at high-volume retention/replay than Kafka.",
        "A SaaS app routing webhook deliveries through topic exchanges so per-tenant retry policies can be applied.",
    ),
    "Messaging and Event-Driven Design > Async Processing": (
        "Pushing slow or unreliable work onto a queue so the request thread returns instantly while a worker handles it later.",
        "Fast user response and resilience to worker outages, but introduces eventual consistency and the need for status polling/notifications.",
        'A "Generate PDF report" button that enqueues a job and emails the user when ready, instead of blocking the HTTP request for 30 seconds.',
    ),
    # ──────────────────────────────── Sharding and Partitioning ─────
    "Sharding and Partitioning > Range-based": (
        "Partitioning that assigns a contiguous range of the key space to each shard (e.g., users `A–F`, `G–M`).",
        "Range queries are efficient and routing is simple, but skewed data or sequential keys create hot ranges.",
        "A time-series DB sharded by week — the current week's shard takes nearly all writes while older shards are cold.",
    ),
    "Sharding and Partitioning > Hash-based": (
        "Hashes the key and modulos by the number of shards to assign each key to a shard.",
        "Even data distribution, but range queries become scatter-gather and adding/removing shards reshuffles most of the data.",
        "A user-profile DB sharded by `hash(user_id) % 64` so writes spread evenly across 64 shards.",
    ),
    "Sharding and Partitioning > Geo / Directory": (
        "A lookup directory or geographic key (region, tenant ID) decides which shard owns each row.",
        "Locality wins (EU data on EU shards) and explicit control, but the directory becomes a hot dependency that needs its own HA story.",
        "A SaaS app where each customer's data lives entirely on one shard chosen by `tenant_id` from a `tenants → shard_id` directory.",
    ),
    "Sharding and Partitioning > Consistent Hashing": (
        "Maps both keys and shards onto a circular hash space so adding/removing a shard only affects neighbors.",
        "Minimizes data movement during rebalances, at the cost of slightly less even distribution unless virtual nodes are used.",
        "DynamoDB and Cassandra use consistent hashing internally so scaling out to a new node moves only ~1/N of the data.",
    ),
    "Sharding and Partitioning > Hot Partitions": (
        "One shard receiving disproportionately more traffic or data than the others.",
        "The bottleneck even with many shards; mitigations (key salting, write sharding) trade simplicity for balance.",
        "A celebrity profile that dwarfs every other user — solved by salting the key (`user_id#1`, `user_id#2`, …) and reading the shards in parallel.",
    ),
    "Sharding and Partitioning > Consistency trade-offs > Single-shard ops are easy": (
        "Operations whose data lives entirely on one shard inherit that shard's local ACID guarantees.",
        "Fast and consistent, but only attainable when the schema and access patterns are designed around the shard key.",
        "All of one user's posts on the same shard — `INSERT post` and `UPDATE counts` run as a single local transaction.",
    ),
    "Sharding and Partitioning > Consistency trade-offs > Cross-shard transactions are costly": (
        "Atomic writes spanning multiple shards require **2-Phase Commit (2PC)** or distributed-coordination protocols.",
        "Provide strong consistency across shards but slow, block on coordinator failure, and reduce availability.",
        "A money transfer where sender and receiver live on different shards — requires 2PC or a saga; most teams avoid 2PC entirely.",
    ),
    "Sharding and Partitioning > Consistency trade-offs > Sagas as a pragmatic alternative": (
        "Replace one distributed transaction with a sequence of local transactions, each with a compensating action on failure.",
        "Buys availability and decoupling at the cost of eventual consistency and the operational complexity of compensations.",
        'Booking a trip = book flight → book hotel → book car; if the car fails, run "cancel hotel" and "cancel flight" compensations.',
    ),
    "Sharding and Partitioning > Consistency trade-offs > Cross-shard reads & joins": (
        "Reads that need data from multiple shards executed as scatter-gather queries.",
        "Latency is bounded by the slowest shard; results may reflect different points in time, leading to read-your-writes anomalies.",
        'An "all my orders across regions" query that fans out to every regional shard and merges results in the API gateway.',
    ),
    "Sharding and Partitioning > Consistency trade-offs > Rebalancing (resharding)": (
        "Moving data while traffic flows so shards stay balanced as the cluster grows or shrinks.",
        "Necessary as the system evolves, but during the move reads can hit either old or new locations — design for double-writes, idempotency, and a controlled cutover.",
        "Vitess re-sharding a 4-shard MySQL cluster to 8 shards using filtered logical replication and per-key cutover.",
    ),
    "Sharding and Partitioning > Consistency trade-offs > Choosing the shard key matters most": (
        "The single design decision that determines hot spots, query patterns, and rebalance pain.",
        "A good key matches the dominant access pattern; a bad one creates hot shards or forces every query to fan out.",
        "Choosing `(tenant_id, created_at)` instead of just `created_at` so each tenant's data co-locates and per-tenant queries hit one shard.",
    ),
    "Sharding and Partitioning > Consistency trade-offs > Rule of thumb": (
        "Heuristic for sharded systems — keep transactional boundaries inside one shard, accept eventual consistency across shards.",
        'Trades a "perfect" relational model for a system that scales — clients only see idempotent cross-shard operations.',
        "An e-commerce app where each order, items, and inventory updates live on the same shard, and cross-warehouse reports are eventually consistent.",
    ),
    # ────────────────────────── Microservices and Communication ─────
    "Microservices and Communication > Sync Protocols > REST": (
        "HTTP-based, resource-oriented API style using verbs (GET/POST/PUT/DELETE) and JSON.",
        "Universally supported, cacheable, and easy to debug, but verbose, weakly typed, and chatty for fine-grained data.",
        "A public-facing `/api/v1/orders/{id}` endpoint consumed by web, mobile, and third-party integrations.",
    ),
    "Microservices and Communication > Sync Protocols > gRPC": (
        "Schema-first, binary RPC over HTTP/2 using Protocol Buffers.",
        "Fast, strongly typed, supports streaming, but harder to debug from a browser and not natively cacheable.",
        "Internal service-to-service calls in a microservices fleet where 40% lower latency and codegen across 5 languages outweigh debuggability concerns.",
    ),
    "Microservices and Communication > Sync Protocols > GraphQL": (
        "Query language that lets clients request exactly the fields they need from a single endpoint.",
        "Eliminates over-fetching and works for diverse clients, but server-side query analysis (depth limits, cost) and caching are more complex than REST.",
        "A mobile app fetching only the 4 fields it needs from a 50-field user object via a GraphQL `/graphql` endpoint.",
    ),
    "Microservices and Communication > Service Discovery > The two core pieces > Service Registry": (
        "Live database of `service-name → [healthy instances]` updated by self-registration and health checks.",
        "Foundational for dynamic systems, but is itself a critical dependency — must be HA and quickly converge after partitions.",
        "A Consul cluster registering 200 service instances and exposing their addresses via DNS or HTTP API.",
    ),
    "Microservices and Communication > Service Discovery > The two core pieces > Discovery (the lookup)": (
        "The act of asking the registry for an instance of a target service at call time.",
        "Avoids hard-coded addresses and supports dynamic scaling, but adds a registry lookup on every call (usually cached).",
        "Service A's HTTP client resolving `billing.default.svc.cluster.local` via cluster DNS before each request, with a 30-second cache.",
    ),
    "Microservices and Communication > Service Discovery > Two main patterns > Client-side discovery": (
        "The caller queries the registry, picks an instance, and applies its own load-balancing logic.",
        "One fewer hop and smart client routing, but every language/runtime needs the discovery library and routing logic is duplicated.",
        "Netflix Eureka + Ribbon — Spring Cloud apps fetch the live instance list and round-robin among them in the client process.",
    ),
    "Microservices and Communication > Service Discovery > Two main patterns > Server-side discovery": (
        "The caller hits a fixed address (LB / gateway / sidecar) that internally consults the registry.",
        "Clients stay dumb and language-agnostic, but the LB itself must be HA and adds a hop.",
        "A Kubernetes Service IP that kube-proxy uses to round-robin across the live pods behind it — the client sees one stable address.",
    ),
    "Microservices and Communication > Service Discovery > Common implementations > Kubernetes (DNS-based)": (
        "Built-in K8s mechanism that gives every Service a stable DNS name backed by kube-proxy load balancing.",
        "Service discovery for free if you're already on K8s, but coupling with the cluster — cross-cluster needs extra mesh/federation.",
        "A `payments` Service exposed as `payments.default.svc.cluster.local`; pods come and go but the DNS name stays.",
    ),
    "Microservices and Communication > Service Discovery > Common implementations > Consul": (
        "HashiCorp's standalone registry with health checks, KV store, multi-datacenter, and DNS/HTTP lookup.",
        "Stronger feature set than K8s DNS (cross-DC, KV, ACLs), but a separate component to run and secure.",
        "A multi-cloud setup where workloads in AWS and on-prem register in a Consul federation and discover each other across both.",
    ),
    "Microservices and Communication > Service Discovery > Common implementations > Eureka": (
        "Netflix's client-side discovery registry, popular in older Spring Cloud stacks.",
        "Battle-tested in Netflix-scale systems, but largely superseded by K8s-native DNS and service meshes.",
        "A legacy Spring Cloud microservices app using Eureka + Ribbon + Hystrix from the pre-Kubernetes era.",
    ),
    "Microservices and Communication > Service Discovery > Common implementations > Service Mesh (Istio, Linkerd)": (
        "Sidecar proxy attached to every pod that handles discovery, LB, retries, mTLS, and observability transparently.",
        "Most powerful (L7 policies, mTLS for free, rich telemetry), but heaviest — adds a proxy per pod, control plane to run, and a learning curve.",
        "Istio in a 200-service cluster providing automatic mTLS and a global view of request rates and error rates.",
    ),
    "Microservices and Communication > Service Discovery > Health checks — the unsung hero > Liveness": (
        'Health check that asks "is this process running?" — failure triggers a restart.',
        "Recovers from deadlocks and unrecoverable states, but a too-aggressive liveness check during a slow boot can cause restart loops.",
        "A K8s `livenessProbe` hitting `/healthz` every 10s; three failures in a row → kubelet restarts the container.",
    ),
    "Microservices and Communication > Service Discovery > Health checks — the unsung hero > Readiness": (
        'Health check that asks "is this process ready to serve?" — failure removes it from the pool but does **not** restart it.',
        "Lets slow-starting or temporarily-overloaded instances drain traffic without being killed, but requires careful design to avoid flapping.",
        "A `readinessProbe` returning 503 until DB connections are warm and migrations finish; the LB skips the pod until it's truly ready.",
    ),
    "Microservices and Communication > Service Discovery > Why senior engineers care": (
        "Service Discovery is the foundation that makes horizontal scaling, zero-downtime deploys, and self-healing actually work.",
        "Without it every deploy or autoscale event breaks callers; with it the cluster behaves as one elastic system.",
        "A 50-service company shipping 200 deploys/day relies on discovery + health checks so callers never notice the rolling restarts.",
    ),
    "Microservices and Communication > API Gateway": (
        "Single front-door service that handles auth, rate-limiting, routing, and aggregation for downstream microservices.",
        "Centralizes cross-cutting concerns and shields clients from internal topology, but is itself a critical hop and can become a bottleneck.",
        "Kong / AWS API Gateway terminating TLS, validating JWTs, and routing `/orders/*` to the orders service and `/billing/*` to billing.",
    ),
    # ─────────────────────────── Resilience and Fault Tolerance ─────
    "Resilience and Fault Tolerance > Circuit Breaker": (
        'Wrapper around a remote call that "opens" after repeated failures and short-circuits subsequent calls until the dependency recovers.',
        "Stops cascading failure from an overloaded dependency, but a too-sensitive breaker amplifies brief blips into outages.",
        "Resilience4j circuit breaker around the payments API — opens after 5 failures in 10s and fails-fast for 30s before a half-open probe.",
    ),
    "Resilience and Fault Tolerance > Retries with Exponential Backoff": (
        "On transient failure, retry the call with exponentially-growing delays plus jitter.",
        "Recovers from blips automatically, but without backoff/jitter and a cap, retries amplify load on a struggling dependency (retry storms).",
        "AWS SDK's default retry policy: 3 attempts with `2^n × 100ms` plus full jitter and a 20-second cap.",
    ),
    "Resilience and Fault Tolerance > Bulkheads": (
        "Isolate resources (thread pools, connections) per dependency so one slow dependency can't drown the rest.",
        "Contains failures and prevents thread starvation, but partitioned resources mean lower peak utilization.",
        "Two HTTP client thread pools — 30 threads for Stripe, 30 for the search service — so a Stripe slowdown can't exhaust the pool used for search.",
    ),
    "Resilience and Fault Tolerance > Timeouts": (
        "Cap on how long any RPC, query, or task will block before the caller gives up.",
        "Prevents indefinite resource hold-ups and unblocks callers, but too-short timeouts waste good results and trigger unnecessary retries.",
        "A 2-second connect timeout and 5-second read timeout on every outbound HTTP call, with timeouts shorter than the upstream caller's own.",
    ),
    "Resilience and Fault Tolerance > Idempotency": (
        "Property that the same operation can be safely repeated and produce the same result.",
        "Makes retries safe and at-least-once delivery survivable, but requires explicit idempotency keys or natural uniqueness, increasing design effort.",
        "A `POST /payments` accepting an `Idempotency-Key` header so a retry after a network blip doesn't double-charge the customer.",
    ),
    # ────────────────────────────── Object Storage and CDNs ─────
    "Object Storage and CDNs > S3-like Object Storage": (
        'Service that stores arbitrarily-large opaque "objects" (files) addressed by key, with multiple-copy durability.',
        "Cheap, virtually unlimited, and 11-nines durable, but high per-request latency vs. local disk and no in-place mutation.",
        "AWS S3 holding user uploads, ML training data, and DB backups — accessed by `s3://bucket/key` URLs.",
    ),
    "Object Storage and CDNs > CDN": (
        "Distributed cache for static assets and media, served from PoPs close to end users.",
        "Massive latency wins and origin offload, but cache invalidation gets harder farther from origin and costs scale with bandwidth.",
        "Cloudflare in front of an S3 bucket — JS, CSS, images, and HLS video segments served from ~300 PoPs with `max-age=1y, immutable`.",
    ),
    "Object Storage and CDNs > When NOT a DB": (
        "Decision rule — large media, backups, logs, archives, ML datasets belong in object storage, not a database.",
        "Storing blobs in a DB makes them slow and 100× more expensive to host and back up; storing them in S3 keeps the DB lean.",
        "Storing user-uploaded videos in S3 and only keeping `s3_key` + metadata in PostgreSQL.",
    ),
    # ──────────────────────────── Observability and Monitoring ─────
    "Observability and Monitoring > Metrics > RED (for request-driven services) > Rate": (
        "Requests per second, broken down by endpoint, method, and status.",
        "The denominator that lets you compute error rate and a leading capacity-planning signal, but high cardinality (per-endpoint × per-status) costs storage.",
        "A Prometheus counter `http_requests_total{route, status}` scraped every 15s, queried as `rate(... [5m])`.",
    ),
    "Observability and Monitoring > Metrics > RED (for request-driven services) > Errors": (
        "Rate of failed requests — explicit (5xx, exceptions) and implicit (200 OK with wrong content).",
        "The most user-impacting RED signal, but you must alert on the **ratio** (errors / total) so it scales with traffic.",
        "An alert that fires when `rate(http_5xx[5m]) / rate(http_total[5m]) > 0.01` for 5 minutes.",
    ),
    "Observability and Monitoring > Metrics > RED (for request-driven services) > Duration": (
        "Latency distribution per endpoint, tracked at p50/p95/p99 (never the mean).",
        "Reveals tail-latency problems that real users feel, but histogram metrics are expensive to store and aggregate.",
        "Prometheus histogram `http_request_duration_seconds_bucket{route}` queried via `histogram_quantile(0.99, rate(...))`.",
    ),
    "Observability and Monitoring > Metrics > USE (for resources / hardware) > Utilization": (
        "Fraction of time a resource is busy (CPU, disk, NIC).",
        "Easy to interpret, but a 100%-utilized resource isn't always a problem — and a 30% one can still be saturated if its queue is full.",
        "Linux `node_cpu_seconds_total` used to compute per-core CPU utilization at 1-minute resolution.",
    ),
    "Observability and Monitoring > Metrics > USE (for resources / hardware) > Saturation": (
        "Backlog or queue depth waiting on a resource — the leading signal before utilization hits 100%.",
        "Catches problems earlier than utilization, but per-resource saturation metrics often need the OS/runtime to expose them.",
        "Linux `node_load1` over `node_cpu_count` (load average / cores), or a thread-pool's `queue.size` counter.",
    ),
    "Observability and Monitoring > Metrics > USE (for resources / hardware) > Errors": (
        "Resource-level error counts — disk I/O errors, dropped packets, OOM kills, retransmits.",
        "Often catches hardware/OS issues that RED-style errors miss, but tools and locations are scattered (dmesg, `node_exporter`, NIC counters).",
        "An alert on `node_disk_io_now > 0 and node_disk_io_errors_total > 0` to catch a failing SSD before it takes the DB down.",
    ),
    "Observability and Monitoring > Metrics > Four Golden Signals (Google SRE) > Latency": (
        "How long a request takes to be served, tracked separately for success and failure.",
        "Failures can be artificially fast (instant 500s) and skew the mean — always slice success vs. error and look at percentiles.",
        'Splitting `http_request_duration_seconds` by `status="2xx"` vs. `status="5xx"` so a flood of fast 500s doesn\'t make the p99 look healthy.',
    ),
    "Observability and Monitoring > Metrics > Four Golden Signals (Google SRE) > Traffic": (
        "Demand on the system — requests/sec, transactions/sec, messages/sec.",
        "The denominator for ratios and the input to capacity planning, but choosing the right unit (requests vs. bytes vs. transactions) matters.",
        "`rate(http_requests_total[5m])` for an HTTP service or `rate(kafka_messages_consumed_total[5m])` for a streaming worker.",
    ),
    "Observability and Monitoring > Metrics > Four Golden Signals (Google SRE) > Errors": (
        "Rate of failed requests — alert on the ratio so the threshold scales with traffic.",
        "Thresholds tuned at one traffic level break at another; ratios are robust but mask absolute volume during low traffic.",
        "An SLO of 99.9% success → alert when `errors / total > 0.001` over a 30-minute rolling window.",
    ),
    "Observability and Monitoring > Metrics > Four Golden Signals (Google SRE) > Saturation": (
        'How "full" the service is — thread-pool depth, queue length, GC pressure, CPU near 100%.',
        "Best leading indicator of overload, but each runtime exposes a different metric — there's no single number.",
        "Tomcat's `tomcat_threadpool_currentthreadsbusy / max_threads > 0.8` as a saturation alert before requests start queueing.",
    ),
    "Observability and Monitoring > Metrics > Infrastructure metrics > CPU & load average": (
        "User vs. system CPU % plus 1/5/15-minute load averages.",
        "Sustained `load > #cores` indicates contention; sudden spikes often correlate with bad releases, but in containers cgroup quotas make raw % misleading.",
        '`1 - rate(node_cpu_seconds_total{mode="idle"}[5m])` per core, alerting on > 80% sustained.',
    ),
    "Observability and Monitoring > Metrics > Infrastructure metrics > Memory (used / available, swap)": (
        "RSS, heap, available memory, and swap activity.",
        "Swapping kills performance long before OOM, so monitor `swap_in/out` even if total memory looks fine; in containers, watch the cgroup limit.",
        "Alert when `container_memory_working_set_bytes / spec.memory.limit > 0.9` for 5 minutes — the OOMKiller is imminent.",
    ),
    "Observability and Monitoring > Metrics > Infrastructure metrics > Disk (IOPS, latency, free space)": (
        "I/O operations/sec, per-op latency, throughput, queue depth, and free space.",
        "Filling disks crash log writers, brokers, and DBs without warning; alert at 80% used and page at 90%.",
        "`node_filesystem_avail_bytes / node_filesystem_size_bytes < 0.2` alert on every host, plus a `disk_io_time_seconds_total` saturation alert.",
    ),
    "Observability and Monitoring > Metrics > Infrastructure metrics > Network (throughput, errors, retransmits)": (
        "Bytes in/out, packet errors, TCP retransmits, connection counts.",
        "TCP retransmits > 1% indicates a real network problem; raw throughput tells you little without context.",
        "`rate(node_netstat_Tcp_RetransSegs[5m]) / rate(node_netstat_Tcp_OutSegs[5m]) > 0.01` to catch a flaky link.",
    ),
    "Observability and Monitoring > Metrics > Application / runtime metrics > GC pauses, heap usage": (
        "Time spent in garbage collection plus heap-after-GC trends.",
        "GC > 5% of CPU = mis-tuned heap; heap-after-GC steadily growing = leak.",
        '`jvm_gc_pause_seconds_sum / process_cpu_seconds_total > 0.05` alert, plus a panel of `jvm_memory_used_bytes{area="heap"}` after each Old-gen GC.',
    ),
    "Observability and Monitoring > Metrics > Application / runtime metrics > Thread / goroutine counts": (
        "Active and idle counts of OS threads, JVM threads, or Go goroutines.",
        'Steadily-growing counts = leak; sudden plateau at the OS limit = the cause of mysterious "hangs".',
        "Go `go_goroutines` panel; an alert when it exceeds 10,000 because the app rarely needs more than 1,000.",
    ),
    "Observability and Monitoring > Metrics > Application / runtime metrics > DB connection pool: active / idle / waiting": (
        "How many DB connections are in use, available, and how many requests are blocked waiting for one.",
        "`waiting > 0` is the first symptom of every DB-induced outage — either the pool is too small or downstream queries are too slow.",
        "HikariCP `hikaricp_pending_threads > 0` alert; pair with a slow-query log to find the culprit.",
    ),
    "Observability and Monitoring > Metrics > Application / runtime metrics > Cache hit ratio": (
        "`hits / (hits + misses)` for each cache layer.",
        "A drop usually means cache thrash, key churn, or a deploy that changed query keys; measure per-cache (Redis vs. application vs. CDN).",
        "Redis `keyspace_hits / (keyspace_hits + keyspace_misses)` panel; a 95% → 70% drop after a deploy is a smoking gun.",
    ),
    "Observability and Monitoring > Metrics > Business / product metrics > Sign-ups, logins, checkouts per minute": (
        "Real-user activity rates — the highest-fidelity signal something is broken.",
        "A 30% drop in checkouts beats any infrastructure metric — your stack might be green and the business still bleeding.",
        'A "Business KPIs" Grafana board with `rate(checkout_completed_total[5m])` and an alert when it drops > 30% from the same hour last week.',
    ),
    "Observability and Monitoring > Metrics > Business / product metrics > Payment success rate": (
        "Money in / money attempted, fluctuating with provider issues, fraud rules, and expired cards.",
        "Alert on the **rate of decline**, not absolute number — baseline varies by hour and country.",
        "An anomaly alert on `payment_success_total / payment_attempt_total` using a 2-week seasonality model.",
    ),
    "Observability and Monitoring > Metrics > Business / product metrics > Active users, conversion funnels": (
        "DAU/WAU/MAU and per-stage drop-off through the funnel (visit → cart → pay → confirm).",
        "Pinpoints where users abandon — UX or perf regressions show up here before any error count moves.",
        "An Amplitude funnel where the visit → cart step drops 8% after a deploy that slowed the product page.",
    ),
    "Observability and Monitoring > Metrics > Practical guidance > Alert on symptoms, not causes": (
        "Page on user-facing pain (latency, error rate, business KPI) rather than internal resource numbers.",
        "Cause-based alerts (CPU 80%) flap and create alert fatigue without a real impact; symptom-based alerts page on what actually matters.",
        'Pager rule "checkout error rate > 1% for 5 minutes" instead of "API host CPU > 80%".',
    ),
    "Observability and Monitoring > Metrics > Practical guidance > Always use percentiles for latency": (
        "Track p50/p95/p99 of latency, never the mean.",
        "Means hide the long tail that hurts real users; percentiles cost more to store and aggregate but reflect actual UX.",
        "A Prometheus histogram with buckets at 5/25/50/100/250/500/1000ms and a `histogram_quantile(0.99, ...)` panel.",
    ),
    "Observability and Monitoring > Metrics > Practical guidance > Label / tag carefully": (
        "Discipline of choosing useful dimensions (service, endpoint, version, region) without explosive cardinality.",
        "Each unique label combination is a separate time-series — too many destroy your metrics backend's storage and queries.",
        "Labels `{service, endpoint, status}` are fine; adding `user_id` would create millions of series and crash Prometheus.",
    ),
    "Observability and Monitoring > Centralized Logs": (
        "Aggregated, structured, searchable logs from all services in one system.",
        "Essential for incident investigation, but log volume balloons and structured-logging discipline must be enforced.",
        "Fluent Bit shipping JSON logs from every pod into Loki; `service=billing AND level=ERROR AND trace_id=abc123` searches.",
    ),
    "Observability and Monitoring > Distributed Tracing": (
        "Records the path of one request across all services, with per-hop spans and latencies.",
        "Pinpoints the slow service across a 20-hop request, but cost forces sampling and instrumentation must be propagated through every service.",
        "OpenTelemetry SDK in every service exporting to Jaeger; one slow checkout shows the 2.3s spent in the recommendation service.",
    ),
    "Observability and Monitoring > Alerting": (
        "Automated paging on conditions that warrant a human waking up.",
        "Alert on too few things and you miss outages; alert on too many and people stop reading the pages.",
        'PagerDuty rule with one symptom-based alert per SLO, runbook URL, and a 5-minute "for" window to filter blips.',
    ),
    # ──────────────────────────── Decomposition Strategies ─────
    "Decomposition Strategies (Monolith → Microservices) > By Functionality": (
        "Cut services along the existing technical modules of the monolith — auth, email, reporting.",
        "Easy to spot from the codebase, but those modules were drawn for developers, not the business — services share data and chat constantly, recreating the monolith over the network.",
        "A team splitting their Rails app into `auth-service`, `email-service`, `reporting-service` and discovering each one calls the others on every request.",
    ),
    'Decomposition Strategies (Monolith → Microservices) > Domain-Driven Design (DDD) > How DDD differs from "By Functionality" > Starting point': (
        "Where the boundary is discovered — the current code structure (Functionality) vs. the business model (DDD).",
        "Code-first is faster to start; business-first takes more effort up front but produces durable boundaries.",
        "Functionality-first: read the repo and split on existing folders. DDD-first: hold an event-storming workshop with domain experts to map what actually happens in the business.",
    ),
    'Decomposition Strategies (Monolith → Microservices) > Domain-Driven Design (DDD) > How DDD differs from "By Functionality" > Boundaries': (
        "What defines the seam — technical layers (Functionality) vs. **Bounded Contexts** (DDD).",
        'Technical layers cross-cut concerns; bounded contexts let the same word ("Customer") mean different things in Sales vs. Shipping.',
        'A "Customer" in Sales has prospects and quotes; in Shipping it\'s an address and SLA. DDD models them as two distinct types in two services; Functionality forces one shared one.',
    ),
    'Decomposition Strategies (Monolith → Microservices) > Domain-Driven Design (DDD) > How DDD differs from "By Functionality" > Shared model': (
        "Whether services share data — Functionality often shares one DB / DTOs (invisible coupling); DDD has each context own its data.",
        "Sharing is cheaper short-term but couples services so they must deploy together; ownership is more work but enables independent change.",
        "DDD: Sales owns its DB and emits `CustomerSignedUp` events; Shipping subscribes and projects its own view. No shared schema, no shared DB.",
    ),
    'Decomposition Strategies (Monolith → Microservices) > Domain-Driven Design (DDD) > How DDD differs from "By Functionality" > Language': (
        "How the team talks — developer terms (Functionality) vs. **Ubiquitous Language** (DDD) shared with the business.",
        "Ubiquitous Language reduces translation bugs between business and engineering, but takes effort to maintain consistency.",
        'Code, docs, and meetings all use "Quote", "Order", "Shipment" instead of `OrderEntity`, `OrderProcessor`, `ShipmentDTO` — same terms as the salesperson uses.',
    ),
    'Decomposition Strategies (Monolith → Microservices) > Domain-Driven Design (DDD) > How DDD differs from "By Functionality" > Outcome': (
        "The system you end up with — Functionality often produces a *distributed monolith*; DDD produces autonomous services.",
        "A distributed monolith has microservices' costs without the benefits; DDD aligns services to teams and Conway's Law works for you.",
        "Functionality outcome: 12 services that must deploy in lock-step. DDD outcome: 12 services where any team can ship to prod independently on any given day.",
    ),
    'Decomposition Strategies (Monolith → Microservices) > Domain-Driven Design (DDD) > How DDD differs from "By Functionality" > Cost': (
        "Up-front investment vs. long-term payoff — DDD is slower to start, faster to evolve.",
        "DDD's workshops, event storming, and modeling sessions feel like overhead, but they pay back when teams ship independently and boundaries don't need rewriting.",
        "A 3-week Event Storming + bounded-context-mapping kickoff before writing code, vs. starting to code on day one with code-first splits.",
    ),
    "Decomposition Strategies (Monolith → Microservices) > Strangler Fig Pattern": (
        "Migration pattern that routes slices of traffic to new services while gradually retiring the old paths.",
        "Avoids Big-Bang rewrites and keeps the system always-shippable, but the migration period is long and runs two stacks in parallel.",
        "An nginx routing rule that sends `/checkout/*` to a new Go service and everything else to the legacy Rails monolith — the old code shrinks each sprint.",
    ),
    "Decomposition Strategies (Monolith → Microservices) > Data Decomposition": (
        "Splitting the shared monolith DB so each service owns its data — almost always the hardest step.",
        "Eliminates coupling at the data layer (the deepest kind), but breaks foreign keys, joins, and atomic transactions across what used to be one DB.",
        "Extracting the `orders.*` tables into a separate Postgres for the Orders service, with the rest of the monolith reading via API or events instead of a JOIN.",
    ),
}


def detail_title(definition: str, trade_offs: str, application: str) -> str:
    """Format the detail node's title using <br/> for visible line breaks
    inside the markmap node."""
    return (
        f"**Definition:** {definition}<br/>"
        f"**Trade-offs:** {trade_offs}<br/>"
        f"**Application Example:** {application}"
    )


def is_detail_child(child: dict) -> bool:
    return isinstance(child.get("title"), str) and child["title"].startswith("**Definition:**")


def walk_and_apply(node: dict, path: list[str], missing: list[str], applied: int) -> int:
    children = node.get("children")
    if children:
        for c in children:
            applied = walk_and_apply(c, path + [c["title"]], missing, applied)
        return applied
    # leaf
    full_path = " > ".join(path)
    if full_path not in DETAILS:
        missing.append(full_path)
        return applied
    d, t, x = DETAILS[full_path]
    new_child = {"title": detail_title(d, t, x)}
    node["children"] = [new_child]
    return applied + 1


def main() -> None:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    missing: list[str] = []
    applied = 0
    for top in data["children"]:
        applied = walk_and_apply(top, [top["title"]], missing, applied)

    if missing:
        print("MISSING DETAIL ENTRIES:", file=sys.stderr)
        for m in missing:
            print(f"  - {m}", file=sys.stderr)
        sys.exit(1)

    JSON_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Applied {applied} detail nodes; coverage: {applied}/{len(DETAILS)}.")


if __name__ == "__main__":
    main()
