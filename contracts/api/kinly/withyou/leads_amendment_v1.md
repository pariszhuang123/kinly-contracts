---
Domain: withYou
Capability: Leads Amendment
Scope: backend
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0
---

# Contract — Leads Table Amendment for withYou v1.0

## Purpose

Amend the existing `public.leads` table to support multi-source lead capture for withYou, while preserving backward compatibility with existing Kinly lead flows.

## Current State

- **Table**: `public.leads`
- **Current uniqueness**: `unique(email)` via `citext`
- **Current source allowlist**: `kinly_web_get`, `kinly_dating_web_get`, `kinly_rent_web_get`

## Required Changes

### Uniqueness Change

- **DROP**: `unique(email)`
- **ADD**: unique index on `(email, source)`

### Source Allowlist Update

Add `'withyou_web_get'` to the check constraint on `source`:

```sql
check (source in (
  'kinly_web_get',
  'kinly_dating_web_get',
  'kinly_rent_web_get',
  'withyou_web_get'
))
```

## Conflict Behavior Change

**Old**: same email → always update (only one row per email).

**New**:
- Same email + same source → MUST update existing row (upsert on `(email, source)`)
- Same email + different source → MUST insert new row

## RPC Impact

`public.leads_upsert_v1` MUST be updated to:

- Use `ON CONFLICT (email, source)` instead of `ON CONFLICT (email)`
- Accept `p_source = 'withyou_web_get'` as valid

## Migration Safety

- This is a backward-compatible change for existing Kinly sources
- Existing rows with `kinly_web_get` remain valid
- The RPC default for `p_source` MUST remain `kinly_web_get`
- No data loss expected

## Rollback Plan

If issues arise:

1. Revert the unique index back to `unique(email)`
2. Remove `withyou_web_get` from the allowlist
3. Dedup any duplicate-source rows inserted during the window
