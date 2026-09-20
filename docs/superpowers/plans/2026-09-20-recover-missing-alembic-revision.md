# Recover Missing Alembic Revision Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore Alembic revision `d4e9a2c1f7b0`, reconcile the split migration graph, and prove the configured PostgreSQL database can migrate to one head.

**Architecture:** Preserve the recovered historical revision ID so databases already stamped with it remain valid. Make the recovered migration tolerate the newer rewritten base schema, then add a no-op Alembic merge revision joining `d4e9a2c1f7b0` and `e2f3a4b5c6d7` without deleting production data.

**Tech Stack:** Python 3.12, Alembic, SQLAlchemy, PostgreSQL, pytest

**Spec:** User request in the active Codex task.

## Global Constraints

- Do not rewrite the value stored in `alembic_version` by hand.
- Do not delete crawler data or obsolete columns while repairing migration lineage.
- Preserve revision ID `d4e9a2c1f7b0` and its recovered parent `7b93f28d9c1a`.
- Finish with exactly one Alembic head.

## Review Focus

- A database already stamped at `d4e9a2c1f7b0` must have a valid upgrade path.
- A fresh database based on the rewritten `7b93f28d9c1a` schema must not fail because `transcript` or `summary` is absent.
- A database on the `e2f3a4b5c6d7` sibling branch must join the same final head.
- Existing crawler rows and columns must not be deleted.
- The application must connect after migration.

---

### Task 1: Pin the migration graph regression

**Files:**
- Create: `tests/test_alembic_migration_graph.py`

**Interfaces:**
- Consumes: `alembic.ini` and `alembic/versions/*.py`
- Produces: regression assertions for the recovered revision and single merged head

- [ ] Write a failing pytest asserting that revision `d4e9a2c1f7b0` exists, descends from `7b93f28d9c1a`, and belongs to a graph with one head that also includes `e2f3a4b5c6d7`.
- [ ] Run the focused test and confirm it fails because `d4e9a2c1f7b0` is missing.

### Task 2: Restore and merge the history

**Files:**
- Create: `alembic/versions/d4e9a2c1f7b0_make_crawler_enrichment_optional.py`
- Create: `alembic/versions/f1a2b3c4d5e6_merge_crawler_migration_heads.py`

**Interfaces:**
- Consumes: the migration recovered from `stash@{1}^3`
- Produces: one Alembic head reachable from both prior heads

- [ ] Restore the recovered migration metadata and nullable-column intent.
- [ ] Inspect existing columns before altering them so the rewritten fresh schema is supported.
- [ ] Add a no-op merge revision with parents `d4e9a2c1f7b0` and `e2f3a4b5c6d7`.
- [ ] Run the focused test and confirm it passes.

### Task 3: Verify against PostgreSQL and the application

**Files:**
- Modify only if verification exposes another root-cause defect.

**Interfaces:**
- Consumes: configured `DATABASE_URL`, Docker Compose services, Alembic CLI
- Produces: migrated live database and recorded verification evidence

- [ ] Start the existing PostgreSQL service.
- [ ] Record current Alembic state and crawler column metadata.
- [ ] Run `alembic upgrade head` and confirm one current/head revision.
- [ ] Run the migration regression test and relevant backend tests.
- [ ] Run an application/database health check and report any unrelated failures.
