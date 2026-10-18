---
title: API Reference
subtitle: "{{project_name}}"
version: 1.0.0
date: "{{YYYY-MM-DD}}"
author: "{{author}}"
project: "{{project_name}}"
doc_id: api-reference
confidential: false
---

<!-- guide: Source priority: OpenAPI/Swagger spec (scan.openapi) > route files (scan.routes,
with confidence). State which source you used. Show only endpoints that exist. Example
payloads must match schemas/DTOs/models in the code; if you infer a shape, mark it ⟨assumption⟩. -->

## Overview

| | |
|---|---|
| Base URL | `{{api_base_url}}` |
| Format | {{JSON}} |
| Source | {{openapi.yaml / route detection (confidence)}} |
| Version | {{from spec info.version or package version}} |

## Authentication

<!-- guide: From auth middleware, security schemes, dependency injection (FastAPI Depends),
passport strategies, etc. Show the header format. Never show a real token. -->

```http
Authorization: Bearer <token>
```

{{how to obtain a token}}

## Endpoints

<!-- guide: Group by resource/tag. Summary table first, then one subsection per endpoint. -->

| Method | Path | Summary | Auth |
|---|---|---|---|
| `GET` | `{{/path}}` | {{summary}} | {{yes/no}} |

### `{{METHOD}} {{/path}}`

{{one-line description}} (`{{source file}}`)

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| {{name}} | {{path/query/header}} | {{type}} | {{yes/no}} | {{description}} |

**Request**

```bash
curl -X {{METHOD}} "{{api_base_url}}{{/path}}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{{json body}}'
```

**Response** `{{200}}`

```json
{{response example}}
```

## Error codes

<!-- guide: From exception handlers, error classes, HTTPException usages, spec responses. -->

| Status | Code / type | Meaning | When |
|---|---|---|---|
| 400 | {{code}} | {{meaning}} | {{when}} |

## Related documents

[Integration Guide](integration-guide.md) · [Data Model](data-model.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | {{item}} | assumption | {{reason}} | {{role}} |
