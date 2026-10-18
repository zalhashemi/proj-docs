---
title: API Reference
subtitle: "Ledgerline"
version: 1.0.0
date: "2026-10-18"
author: "Ledgerline platform team"
project: "Ledgerline"
doc_id: api-reference
confidential: false
---

## Overview

| | |
|---|---|
| Base URL | `http://localhost:8000` (`Dockerfile`, `docker-compose.yml`) |
| Format | JSON |
| Source | Route detection in `app/main.py` and `app/routers/orders.py` (medium confidence), confirmed by reading the code |
| Version | 0.9.2 (`FastAPI(version=...)` in `app/main.py`) |

FastAPI also serves the generated OpenAPI schema at `/openapi.json` and interactive docs at
`/docs` ⟨untested⟩.

## Authentication

Every `/orders` endpoint requires an API key in the `x-api-key` header
(`dependencies=[Depends(require_api_key)]` in `app/routers/orders.py`). The key is compared
with the `API_KEY` environment variable (`app/auth.py`).

```http
x-api-key: <your API key>
```

| Situation | Response |
|---|---|
| Header missing | `422` validation error (header is required) |
| Wrong key | `401` `{"detail": "invalid API key"}` |
| `API_KEY` not set on the server | `500`: `os.environ["API_KEY"]` raises `KeyError` |

## Endpoints

| Method | Path | Summary | Auth |
|---|---|---|---|
| `GET` | `/health` | Liveness check | no |
| `GET` | `/orders` | List orders | yes |
| `POST` | `/orders` | Create an order | yes |
| `GET` | `/orders/{order_id}` | Get one order | yes |
| `DELETE` | `/orders/{order_id}` | Cancel an order | yes |

### `GET /health`

Returns service status (`app/main.py`).

```bash
curl http://localhost:8000/health
```

**Response** `200`

```json
{"status": "ok"}
```

### `GET /orders`

Lists orders (`list_orders`, `app/routers/orders.py`).

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `limit` | query | int | no | Maximum results, default `50` |

```bash
curl "http://localhost:8000/orders?limit=10" -H "x-api-key: $API_KEY"
```

**Response** `200`: an array of `OrderOut`. The current implementation always returns `[]`.

### `POST /orders`

Creates an order from an `OrderIn` body (`app/schemas.py`).

```bash
curl -X POST http://localhost:8000/orders \
  -H "x-api-key: $API_KEY" -H "Content-Type: application/json" \
  -d '{"customer_id": 42, "sku": "MUG-001", "quantity": 12}'
```

> [!WARNING]
> Not implemented yet: the handler raises `501 {"detail": "not implemented"}`. The declared
> success status is `201`.

### `GET /orders/{order_id}`

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `order_id` | path | int | yes | Order ID |

The current handler always returns `404 {"detail": "order not found"}`.

### `DELETE /orders/{order_id}`

Cancels an order. Returns `204 No Content`.

```bash
curl -X DELETE http://localhost:8000/orders/42 -H "x-api-key: $API_KEY"
```

## Schemas

**OrderIn**

| Field | Type | Required |
|---|---|---|
| `customer_id` | int | yes |
| `sku` | string | yes |
| `quantity` | int | yes |

**OrderOut**: every `OrderIn` field, plus:

| Field | Type | Notes |
|---|---|---|
| `id` | int | Order ID |
| `status` | string | `pending` by default in the database (`app/models.py`) |

## Error codes

| Status | Detail | When |
|---|---|---|
| 401 | `invalid API key` | `x-api-key` doesn't match `API_KEY` |
| 404 | `order not found` | `GET /orders/{order_id}` |
| 422 | validation error | missing header, or a body or path value of the wrong type |
| 501 | `not implemented` | `POST /orders` |

## Related documents

[Data Model](data-model.md) · [Runbook](runbook.md) · [Integration Guide](integration-guide.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | `/docs` and `/openapi.json` are reachable | assumption | FastAPI default, not run | backend lead |
| Q1 | When will `POST /orders` and `GET /orders/{order_id}` be implemented? | open question | handlers are stubs | backend lead |
| Q2 | Should a missing `API_KEY` fail at startup instead of per request? | open question | design choice | backend lead |
