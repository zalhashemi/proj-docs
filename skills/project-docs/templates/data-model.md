---
title: Data Model
subtitle: "{{project_name}}"
version: 1.0.0
date: "{{YYYY-MM-DD}}"
author: "{{author}}"
project: "{{project_name}}"
doc_id: data-model
confidential: false
---

<!-- guide: Source of truth order: schema file (schema.prisma, schema.rb, schema.sql) >
latest migrations > ORM model classes. State which you used. If there is no database,
say so in one line and describe any persisted files/caches instead. -->

## Overview

| | |
|---|---|
| Database | {{engine, from compose/env/ORM config}} |
| ORM / access | {{ORM}} |
| Source | `{{schema/migrations/models path}}` |
| Entities | {{count}} |

## Entity relationship diagram

<!-- guide: Mermaid erDiagram. Include all entities if ≤12, otherwise core entities plus a list of the rest. -->

```mermaid
erDiagram
  {{ENTITY_A}} ||--o{ {{ENTITY_B}} : "{{relation}}"
  {{ENTITY_A}} {
    string id PK
  }
```

## Entities

<!-- guide: One subsection per entity. Mark PK/FK/unique/nullable from the schema. -->

### {{Entity}}

{{purpose}} (`{{path}}`)

| Field | Type | Null | Key | Notes |
|---|---|---|---|---|
| `id` | {{type}} | no | PK | |

## Relationships

| From | To | Cardinality | On delete | Evidence |
|---|---|---|---|---|
| {{A}} | {{B}} | 1:N | {{cascade/restrict}} | `{{path}}` |

## Indexes and constraints

| Table | Index / constraint | Columns | Type |
|---|---|---|---|
| {{table}} | {{name}} | {{columns}} | {{unique/btree}} |

## Migrations

<!-- guide: Tool, location, how to create/apply (commands from scripts), count and latest migration. -->

- Tool: {{tool}} · Location: `{{path}}` · Count: {{n}} · Latest: `{{name}}`

```bash
{{migrate command}}
```

## Related documents

[Architecture](architecture.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | {{item}} | assumption | {{reason}} | {{role}} |
