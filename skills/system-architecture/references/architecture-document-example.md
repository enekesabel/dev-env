# Example: Ledgerly

A made-up system, filled into the [template](architecture-document.md).

```markdown
# Architecture

## Context

Ledgerly lets small businesses send invoices and get paid online.

### Actors
- **Business users**: staff of the small businesses using Ledgerly
  - Goal: invoice their customers and get paid
  - Evidence: verified: `apps/web/src/routes/app/`
- **Customers**: the businesses' clients
  - Goal: see what they owe and pay it
  - Evidence: verified: `apps/web/src/routes/pay/`
- **Support staff**: Ledgerly employees who help businesses, working through the admin console
  - Goal: look up accounts and fix billing problems
  - Evidence: verified: `apps/admin/src/routes/`
- **Accounting tools**: software that reads the businesses' invoices and payments
  - Goal: keep the books in sync with invoices and payments
  - Evidence: verified: `services/api/src/routes/public_api.py`

### External systems
- **Payment provider**
  - Provides: card payment processing and payouts
  - Evidence: verified: `services/api/src/payments/client.py`
- **Email provider**
  - Provides: e-mail delivery
  - Evidence: verified: `services/api/src/mail/sender.py`
- **Identity provider**
  - Provides: sign-in for business users and support staff
  - Evidence: inferred: OIDC settings in `apps/web/src/auth/oidc.ts` name no provider
- **Tax-rate service**
  - Provides: sales-tax and VAT rates by region
  - Evidence: verified: `services/api/src/tax/rates.py`
- **Error tracking**
  - Provides: collection and alerting of crash reports
  - Evidence: verified: `services/api/src/observability/errors.py`
- **Analytics**
  - Provides: product usage statistics
  - Evidence: verified: `apps/web/src/analytics.ts`

## Containers

### Web app
- Responsibility: the screens for business users and the public invoice page for customers
- Technology: TypeScript single-page app
- Evidence: verified: `apps/web/`

### Admin console
- Responsibility: the screens support staff use to look up and correct accounts
- Technology: TypeScript single-page app
- Evidence: verified: `apps/admin/`

### API service
- Responsibility: invoices, customers, payments, tax, and API access for the apps and for accounting tools
- Technology: Python web service
- Evidence: verified: `services/api/src/main.py`

### Worker
- Responsibility: runs background jobs: sends e-mails, requests PDFs, finds overdue invoices for reminders, and updates the search index
- Technology: Python process from the API service's codebase
- Evidence: verified: `services/api/src/cli/worker.py`

### Scheduler
- Responsibility: puts recurring work on the job queue: reminders, recurring invoices, and nightly search reindexing
- Technology: Python process from the API service's codebase
- Evidence: verified: `services/api/src/cli/scheduler.py`

### PDF renderer
- Responsibility: turns invoices into PDFs
- Technology: headless-browser render service
- Evidence: verified: `services/renderer/`

### Invoice database
- Responsibility: stored invoices, customers, payments, and accounts
- Technology: PostgreSQL
- Evidence: verified: `services/api/db/migrations/`

### Job queue
- Responsibility: holds background jobs until the worker takes them
- Evidence: verified: `services/api/src/jobs/`

### Cache
- Responsibility: sessions, rate limits, and recently fetched tax rates
- Technology: Redis
- Evidence: verified: `services/api/src/cache/client.py`

### Document storage
- Responsibility: rendered invoice PDFs, business logos, and uploaded attachments
- Technology: S3-compatible object storage
- Evidence: verified: `services/api/src/storage/documents.py`

### Search index
- Responsibility: full-text search over invoices and customers
- Technology: OpenSearch
- Evidence: verified: `services/api/src/search/`

## Communication
- **Business users → Web app**
  - Flows:
    - → invoice, customer, and settings edits
    - ← invoices, PDFs, payment status
  - Evidence: verified: `apps/web/src/routes/app/`
- **Customers → Web app**
  - Flows:
    - → invoice link opens
    - ← invoice view and PDF download
  - Evidence: verified: `apps/web/src/routes/pay/`
- **Support staff → Admin console**
  - Flows:
    - → account lookups and billing corrections
    - ← account and billing details
  - Evidence: verified: `apps/admin/src/routes/`
- **Accounting tools → API service**
  - Flows:
    - → invoice and payment queries
    - ← invoices and payments
  - Evidence: verified: `services/api/src/routes/public_api.py`
- **Payment provider → API service**
  - Flows:
    - → payment results
  - Evidence: verified: `services/api/src/routes/payment_webhooks.py`
- **Web app → Payment provider**
  - Flows:
    - → card details
    - ← payment confirmation
  - Evidence: verified: `apps/web/src/routes/pay/checkout.ts`
- **Web app → Identity provider**
  - Flows:
    - → sign-in request
    - ← identity token
  - Evidence: inferred: OIDC settings in `apps/web/src/auth/oidc.ts`
- **Web app → Error tracking**
  - Flows:
    - → browser crash reports
  - Evidence: verified: `apps/web/src/observability.ts`
- **Web app → Analytics**
  - Flows:
    - → usage events
  - Evidence: verified: `apps/web/src/analytics.ts`
- **Web app → API service**
  - Flows:
    - → invoice, customer, and settings edits
    - ← invoices, payment status, PDFs
  - Evidence: verified: `apps/web/src/api/client.ts`
- **Admin console → Identity provider**
  - Flows:
    - → sign-in request
    - ← identity token
  - Evidence: inferred: OIDC settings in `apps/admin/src/auth/oidc.ts`
- **Admin console → API service**
  - Flows:
    - → account lookups and billing corrections
    - ← account and billing details
  - Evidence: verified: `apps/admin/src/api/client.ts`
- **API service → Accounting tools**
  - Flows:
    - → invoice and payment change notifications
  - Evidence: verified: `services/api/src/webhooks/outgoing.py`
- **API service → Payment provider**
  - Flows:
    - → charges and refunds
    - ← payment status
  - Evidence: verified: `services/api/src/payments/client.py`
- **API service → Tax-rate service**
  - Flows:
    - → region lookups
    - ← tax rates
  - Evidence: verified: `services/api/src/tax/rates.py`
- **API service → Error tracking**
  - Flows:
    - → server errors
  - Evidence: verified: `services/api/src/observability/errors.py`
- **API service → Invoice database**
  - Flows:
    - → invoice, customer, and payment writes
    - ← stored records
  - Evidence: verified: `services/api/src/db/`
- **API service → Job queue**
  - Flows:
    - → e-mail, PDF, and indexing jobs
  - Evidence: verified: `services/api/src/jobs/enqueue.py`
- **API service → Cache**
  - Flows:
    - → session and tax-rate lookups
    - ← cached values
  - Evidence: verified: `services/api/src/cache/client.py`
- **API service → Document storage**
  - Flows:
    - → logos and attachments
    - ← PDFs and attachments
  - Evidence: verified: `services/api/src/storage/documents.py`
- **API service → Search index**
  - Flows:
    - → search queries
    - ← matching invoices and customers
  - Evidence: verified: `services/api/src/search/queries.py`
- **Worker → Email provider**
  - Flows:
    - → invoice and reminder e-mails
  - Evidence: verified: `services/api/src/mail/sender.py`
- **Worker → PDF renderer**
  - Flows:
    - → invoice data
    - ← rendered PDFs
  - Evidence: verified: `services/api/src/pdf/client.py`
- **Worker → Invoice database**
  - Flows:
    - → reminder status
    - ← overdue invoices
  - Evidence: verified: `services/api/src/jobs/reminders.py`
- **Worker → Job queue**
  - Flows:
    - ← e-mail, PDF, and indexing jobs
  - Evidence: verified: `services/api/src/cli/worker.py`
- **Worker → Document storage**
  - Flows:
    - → rendered PDFs
  - Evidence: verified: `services/api/src/jobs/render_pdf.py`
- **Worker → Search index**
  - Flows:
    - → index updates
  - Evidence: inferred: `services/api/src/search/indexer.py` is named like an indexing job, but nothing seen calls it from the worker
- **Scheduler → Job queue**
  - Flows:
    - → reminder, recurring-invoice, and reindex jobs
  - Evidence: verified: `services/api/src/cli/scheduler.py`

## Environments

### local
- Purpose: development on a laptop
- Evidence: verified: `docker-compose.yml`
- Containers:
  - **Web app**: development build with hot reload
    - Deployment node: local dev-server process
    - Evidence: verified: `apps/web/package.json`
  - **Admin console**: development build with hot reload
    - Deployment node: local dev-server process
    - Evidence: verified: `apps/admin/package.json`
  - **API service**: image built from `services/api/`, started with the `serve` command
    - Deployment node: ledgerly-local Compose project
    - Evidence: verified: `docker-compose.yml`
  - **Worker**: the API image, started with the `worker` command
    - Deployment node: ledgerly-local Compose project
    - Evidence: verified: `docker-compose.yml`
  - **Scheduler**: the API image, started on demand with `docker compose run scheduler`
    - Deployment node: ledgerly-local Compose project
    - Evidence: verified: `docker-compose.yml`
  - **PDF renderer**: image built from `services/renderer/`
    - Deployment node: ledgerly-local Compose project
    - Evidence: verified: `docker-compose.yml`
  - **Invoice database**: official PostgreSQL image
    - Deployment node: ledgerly-local Compose project
    - Evidence: verified: `docker-compose.yml`
  - **Job queue**: Redis image
    - Deployment node: ledgerly-local Compose project
    - Evidence: verified: `docker-compose.yml`
  - **Cache**: Redis image
    - Deployment node: ledgerly-local Compose project
    - Evidence: verified: `docker-compose.yml`
  - **Document storage**: MinIO image
    - Deployment node: ledgerly-local Compose project
    - Evidence: verified: `docker-compose.yml`
  - **Search index**: official OpenSearch image, started only with `--profile search`
    - Deployment node: ledgerly-local Compose project
    - Evidence: verified: `docker-compose.yml`
- External systems:
  - **Payment provider**: the provider's sandbox account
    - Evidence: verified: `.env.example`
  - **Email provider**: Mailpit, catching every outgoing e-mail
    - Evidence: verified: `docker-compose.yml`
  - **Identity provider**: mock OIDC server
    - Evidence: verified: `docker-compose.yml`
  - **Tax-rate service**: mock server returning fixed rates
    - Evidence: verified: `docker-compose.yml`
  - **Error tracking**: disabled, a no-op client
    - Evidence: verified: `.env.example`
  - **Analytics**: disabled, a no-op client
    - Evidence: verified: `.env.example`

### e2e
- Purpose: end-to-end tests in CI
- Evidence: verified: `.ci/pipeline.yml`
- Containers:
  - **Web app**: image serving the production build
    - Deployment node: ledgerly-e2e Compose project
    - Evidence: verified: `e2e/docker-compose.yml`
  - **Admin console**: image serving the production build
    - Deployment node: ledgerly-e2e Compose project
    - Evidence: verified: `e2e/docker-compose.yml`
  - **API service**: image built from `services/api/`, running jobs inline
    - Deployment node: ledgerly-e2e Compose project
    - Evidence: verified: `e2e/docker-compose.yml`
  - **Worker**: does not run here; the API service runs jobs inline
    - Evidence: verified: `e2e/docker-compose.yml`
  - **Scheduler**: does not run here; tests trigger recurring work directly
    - Evidence: verified: `e2e/docker-compose.yml`
  - **PDF renderer**: image built from `services/renderer/`
    - Deployment node: ledgerly-e2e Compose project
    - Evidence: verified: `e2e/docker-compose.yml`
  - **Invoice database**: official PostgreSQL image
    - Deployment node: ledgerly-e2e Compose project
    - Evidence: verified: `e2e/docker-compose.yml`
  - **Job queue**: does not run here; jobs run inline, so nothing is queued
    - Evidence: verified: `e2e/docker-compose.yml`
  - **Cache**: Redis image
    - Deployment node: ledgerly-e2e Compose project
    - Evidence: verified: `e2e/docker-compose.yml`
  - **Document storage**: MinIO image
    - Deployment node: ledgerly-e2e Compose project
    - Evidence: verified: `e2e/docker-compose.yml`
  - **Search index**: official OpenSearch image
    - Deployment node: ledgerly-e2e Compose project
    - Evidence: verified: `e2e/docker-compose.yml`
- External systems:
  - **Payment provider**: mock server
    - Evidence: verified: `e2e/docker-compose.yml`
  - **Email provider**: Mailpit, catching every outgoing e-mail
    - Evidence: verified: `e2e/docker-compose.yml`
  - **Identity provider**: mock OIDC server
    - Evidence: verified: `e2e/docker-compose.yml`
  - **Tax-rate service**: mock server returning fixed rates
    - Evidence: verified: `e2e/docker-compose.yml`
  - **Error tracking**: disabled, a no-op client
    - Evidence: verified: `e2e/docker-compose.yml`
  - **Analytics**: disabled, a no-op client
    - Evidence: verified: `e2e/docker-compose.yml`

### staging
- Purpose: pre-release checks against sandbox accounts
- Evidence: verified: `infra/staging/`
- Containers:
  - **Web app**: static build
    - Deployment node: ledgerly-staging Pages project
    - Evidence: verified: `infra/staging/web.tf`
  - **Admin console**: static build
    - Deployment node: ledgerly-admin-staging Pages project
    - Evidence: verified: `infra/staging/admin.tf`
  - **API service**: Kubernetes deployment of the API image, started with the `serve` command
    - Deployment node: ledgerly-staging cluster
    - Evidence: verified: `infra/staging/api.tf`
  - **Worker**: Kubernetes deployment of the API image, started with the `worker` command
    - Deployment node: ledgerly-staging cluster
    - Evidence: verified: `infra/staging/worker.tf`
  - **Scheduler**: single-replica Kubernetes deployment of the API image, started with the `scheduler` command
    - Deployment node: ledgerly-staging cluster
    - Evidence: verified: `infra/staging/scheduler.tf`
  - **PDF renderer**: Kubernetes deployment of the renderer image
    - Deployment node: ledgerly-staging cluster
    - Evidence: verified: `infra/staging/renderer.tf`
  - **Invoice database**: Amazon RDS
    - Deployment node: invoices-staging RDS instance
    - Evidence: verified: `infra/staging/database.tf`
  - **Job queue**: Amazon SQS
    - Deployment node: jobs-staging SQS queue
    - Evidence: inferred: `services/api/src/jobs/config.py` reads a queue URL from the environment; no infrastructure definition in this repository
  - **Cache**: Amazon ElastiCache
    - Deployment node: cache-staging ElastiCache cluster
    - Evidence: inferred: `services/api/src/cache/client.py` reads a cache URL from the environment; no infrastructure definition in this repository
  - **Document storage**: Amazon S3
    - Deployment node: ledgerly-documents-staging S3 bucket
    - Evidence: verified: `infra/staging/storage.tf`
  - **Search index**: Amazon OpenSearch Service
    - Deployment node: search-staging OpenSearch domain
    - Evidence: verified: `infra/staging/search.tf`
- External systems:
  - **Payment provider**: sandbox account
    - Evidence: verified: `infra/staging/config.yaml`
  - **Email provider**: sandbox account, delivering only to internal addresses
    - Evidence: verified: `infra/staging/config.yaml`
  - **Identity provider**: a staging tenant
    - Evidence: inferred: OIDC settings in `apps/web/src/auth/oidc.ts` name no provider
  - **Tax-rate service**: sandbox account
    - Evidence: verified: `infra/staging/config.yaml`
  - **Error tracking**: a separate staging project
    - Evidence: verified: `infra/staging/config.yaml`
  - **Analytics**: a separate staging project
    - Evidence: verified: `infra/staging/config.yaml`

### production
- Purpose: serves real businesses and their customers
- Evidence: verified: `infra/production/`
- Containers:
  - **Web app**: static build
    - Deployment node: ledgerly-production Pages project
    - Evidence: verified: `infra/production/web.tf`
  - **Admin console**: static build
    - Deployment node: ledgerly-admin-production Pages project
    - Evidence: verified: `infra/production/admin.tf`
  - **API service**: Kubernetes deployment of the API image, started with the `serve` command
    - Deployment node: ledgerly-production cluster
    - Evidence: verified: `infra/production/api.tf`
  - **Worker**: Kubernetes deployment of the API image, started with the `worker` command
    - Deployment node: ledgerly-production cluster
    - Evidence: verified: `infra/production/worker.tf`
  - **Scheduler**: single-replica Kubernetes deployment of the API image, started with the `scheduler` command
    - Deployment node: ledgerly-production cluster
    - Evidence: verified: `infra/production/scheduler.tf`
  - **PDF renderer**: Kubernetes deployment of the renderer image
    - Deployment node: ledgerly-production cluster
    - Evidence: verified: `infra/production/renderer.tf`
  - **Invoice database**: Amazon RDS
    - Deployment node: invoices-production RDS instance
    - Evidence: verified: `infra/production/database.tf`
  - **Job queue**: Amazon SQS
    - Deployment node: jobs-production SQS queue
    - Evidence: inferred: `services/api/src/jobs/config.py` reads a queue URL from the environment; no infrastructure definition in this repository
  - **Cache**: Amazon ElastiCache
    - Deployment node: cache-production ElastiCache cluster
    - Evidence: inferred: `services/api/src/cache/client.py` reads a cache URL from the environment; no infrastructure definition in this repository
  - **Document storage**: Amazon S3
    - Deployment node: ledgerly-documents-production S3 bucket
    - Evidence: verified: `infra/production/storage.tf`
  - **Search index**: Amazon OpenSearch Service
    - Deployment node: search-production OpenSearch domain
    - Evidence: verified: `infra/production/search.tf`
- External systems:
  - **Payment provider**: live account
    - Evidence: verified: `infra/production/config.yaml`
  - **Email provider**: live account
    - Evidence: verified: `infra/production/config.yaml`
  - **Identity provider**: the production tenant
    - Evidence: inferred: OIDC settings in `apps/web/src/auth/oidc.ts` name no provider
  - **Tax-rate service**: live account
    - Evidence: verified: `infra/production/config.yaml`
  - **Error tracking**: the production project
    - Evidence: verified: `infra/production/config.yaml`
  - **Analytics**: the production project
    - Evidence: verified: `infra/production/config.yaml`
```
