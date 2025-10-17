-- slate_runner: VFX Production Pipeline Schema
-- Defines projects, assets, shots, tasks, versions, publishes, render jobs, and events,
-- with UIDs auto-generated, timestamps for versioning, and foreign keys for integrity.

DROP TABLE IF EXISTS publishes,
    versions,
    tasks,
    shots,
    assets,
    projects,
    render_jobs,
    events CASCADE;

-- Required for gen_random_bytes()
CREATE
EXTENSION IF NOT EXISTS pgcrypto;

-- Helper: UID generator (PREFIX_XXXXXX)
CREATE
OR REPLACE FUNCTION gen_uid(prefix TEXT) RETURNS TEXT AS $$
BEGIN
RETURN prefix || '_' || upper(substr(encode(gen_random_bytes(4), 'hex'), 1, 6));
END;
$$
LANGUAGE plpgsql;

-- Helper: keep updated_at fresh
CREATE
OR REPLACE FUNCTION set_updated_at() RETURNS TRIGGER AS $$
BEGIN NEW.updated_at
:= now();
RETURN NEW;
END;
$$
LANGUAGE plpgsql;

-- CORE TABLE 

-- PROJECTS
CREATE TABLE projects
(
    id         SERIAL PRIMARY KEY,
    uid        TEXT UNIQUE          DEFAULT gen_uid('PROJ'),
    name       TEXT        NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TRIGGER trg_projects_updated
    BEFORE
        UPDATE
    ON projects
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ASSETS
CREATE TABLE assets
(
    id          SERIAL PRIMARY KEY,
    uid         TEXT UNIQUE          DEFAULT gen_uid('ASSET'),
    project_uid TEXT        NOT NULL REFERENCES projects (uid) ON DELETE CASCADE,
    name        TEXT        NOT NULL,
    type        TEXT        NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TRIGGER trg_assets_updated
    BEFORE
        UPDATE
    ON assets
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- SHOTS
CREATE TABLE shots
(
    id          SERIAL PRIMARY KEY,
    uid         TEXT UNIQUE            DEFAULT gen_uid('SHOT'),
    project_uid TEXT          NOT NULL REFERENCES projects (uid) ON DELETE CASCADE,
    seq         TEXT          NOT NULL,
    shot        TEXT          NOT NULL,
    frame_in    INT           NOT NULL,
    frame_out   INT           NOT NULL,
    fps         NUMERIC(6, 3) NOT NULL DEFAULT 24.0,
    colorspace  TEXT          NOT NULL DEFAULT 'sRGB',
    created_at  TIMESTAMPTZ   NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ   NOT NULL DEFAULT now()
);

CREATE TRIGGER trg_shots_updated
    BEFORE
        UPDATE
    ON shots
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- TASKS
CREATE TABLE tasks
(
    id          SERIAL PRIMARY KEY,
    uid         TEXT UNIQUE          DEFAULT gen_uid('TASK'),
    project_uid TEXT        NOT NULL REFERENCES projects (uid) ON DELETE CASCADE,
    parent_type TEXT        NOT NULL CHECK (parent_type IN ('asset', 'shot')),
    parent_uid  TEXT        NOT NULL,
    name        TEXT        NOT NULL,
    assignee    TEXT,
    status      TEXT        NOT NULL DEFAULT 'WIP' CHECK (status IN ('WIP', 'READY', 'HOLD', 'DONE')),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TRIGGER trg_tasks_updated
    BEFORE
        UPDATE
    ON tasks
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- VERSIONS
CREATE TABLE versions
(
    id          SERIAL PRIMARY KEY,
    uid         TEXT UNIQUE          DEFAULT gen_uid('VER'),
    project_uid TEXT        NOT NULL REFERENCES projects (uid) ON DELETE CASCADE,
    task_uid    TEXT        NOT NULL REFERENCES tasks (uid) ON DELETE CASCADE,
    vnum        INT         NOT NULL,
    status      TEXT        NOT NULL DEFAULT 'draft' CHECK (
        status IN ('draft', 'review', 'approved', 'rejected')
        ),
    created_by  TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (task_uid, vnum)
);

CREATE TRIGGER trg_versions_updated
    BEFORE
        UPDATE
    ON versions
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- PUBLISHES
CREATE TABLE publishes
(
    id             SERIAL PRIMARY KEY,
    uid            TEXT UNIQUE          DEFAULT gen_uid('PUB'),
    project_uid    TEXT        NOT NULL REFERENCES projects (uid) ON DELETE CASCADE,
    version_uid    TEXT        NOT NULL REFERENCES versions (uid) ON DELETE CASCADE,
    type           TEXT        NOT NULL,
    representation TEXT,
    path           TEXT        NOT NULL,
    metadata       JSONB       NOT NULL DEFAULT '{}'::jsonb,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TRIGGER trg_publishes_updated
    BEFORE
        UPDATE
    ON publishes
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- RENDER JOBS
CREATE TABLE render_jobs
(
    id           SERIAL PRIMARY KEY,
    uid          TEXT UNIQUE          DEFAULT gen_uid('RJ'),
    project_uid  TEXT        NOT NULL REFERENCES projects (uid) ON DELETE CASCADE,
    version_uid  TEXT        REFERENCES versions (uid) ON DELETE
        SET NULL,
    context      JSONB       NOT NULL,
    adapter      TEXT        NOT NULL,
    status       TEXT        NOT NULL DEFAULT 'queued' CHECK (
        status IN ('queued', 'running', 'succeeded', 'failed')
        ),
    logs         TEXT,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TRIGGER trg_render_jobs_updated
    BEFORE
        UPDATE
    ON render_jobs
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- EVENTS
CREATE TABLE events
(
    id          SERIAL PRIMARY KEY,
    uid         TEXT UNIQUE          DEFAULT gen_uid('EVENT'),
    project_uid TEXT        NOT NULL REFERENCES projects (uid) ON DELETE CASCADE,
    kind        TEXT        NOT NULL,
    payload     JSONB       NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TRIGGER trg_events_updated
    BEFORE
        UPDATE
    ON events
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ALTERATIONS FOR SOFT DELETES & CASCADES

-- Add deleted_at columns to all tables
ALTER TABLE projects
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE assets
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE shots
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE tasks
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE versions
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE publishes
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE render_jobs
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE events
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- Remove old unique constraints
ALTER TABLE projects DROP CONSTRAINT IF EXISTS projects_name_key;
ALTER TABLE assets DROP CONSTRAINT IF EXISTS assets_project_uid_name_key;
ALTER TABLE shots DROP CONSTRAINT IF EXISTS shots_project_uid_seq_shot_key;

-- Create partial unique indexes (enforce uniqueness only for non-deleted records)
CREATE UNIQUE INDEX IF NOT EXISTS idx_projects_name_unique ON projects(name)
    WHERE deleted_at IS NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_assets_project_name_unique ON assets(project_uid, name)
    WHERE deleted_at IS NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_shots_project_seq_shot_unique ON shots(project_uid, seq, shot)
    WHERE deleted_at IS NULL;

-- Soft delete cascade function for projects
CREATE
OR REPLACE FUNCTION cascade_soft_delete_project() RETURNS TRIGGER AS $$
BEGIN IF
NEW.deleted_at IS NOT NULL
  AND OLD.deleted_at IS NULL THEN
UPDATE assets
SET deleted_at = NEW.deleted_at
WHERE project_uid = NEW.uid
  AND deleted_at IS NULL;
UPDATE shots
SET deleted_at = NEW.deleted_at
WHERE project_uid = NEW.uid
  AND deleted_at IS NULL;
UPDATE tasks
SET deleted_at = NEW.deleted_at
WHERE project_uid = NEW.uid
  AND deleted_at IS NULL;
UPDATE versions
SET deleted_at = NEW.deleted_at
WHERE project_uid = NEW.uid
  AND deleted_at IS NULL;
UPDATE publishes
SET deleted_at = NEW.deleted_at
WHERE project_uid = NEW.uid
  AND deleted_at IS NULL;
UPDATE render_jobs
SET deleted_at = NEW.deleted_at
WHERE project_uid = NEW.uid
  AND deleted_at IS NULL;
UPDATE events
SET deleted_at = NEW.deleted_at
WHERE project_uid = NEW.uid
  AND deleted_at IS NULL;
END IF;
RETURN NEW;
END;
$$
LANGUAGE plpgsql;

-- Soft delete cascade function for tasks
CREATE
OR REPLACE FUNCTION cascade_soft_delete_task() RETURNS TRIGGER AS $$
BEGIN IF
NEW.deleted_at IS NOT NULL
  AND OLD.deleted_at IS NULL THEN
UPDATE versions
SET deleted_at = NEW.deleted_at
WHERE task_uid = NEW.uid
  AND deleted_at IS NULL;
END IF;
RETURN NEW;
END;
$$
LANGUAGE plpgsql;

-- Soft delete cascade function for versions
CREATE
OR REPLACE FUNCTION cascade_soft_delete_version() RETURNS TRIGGER AS $$
BEGIN IF
NEW.deleted_at IS NOT NULL
  AND OLD.deleted_at IS NULL THEN
UPDATE publishes
SET deleted_at = NEW.deleted_at
WHERE version_uid = NEW.uid
  AND deleted_at IS NULL;
UPDATE render_jobs
SET deleted_at = NEW.deleted_at
WHERE version_uid = NEW.uid
  AND deleted_at IS NULL;
END IF;
RETURN NEW;
END;
$$
LANGUAGE plpgsql;

-- Drop existing triggers if they exist
DROP TRIGGER IF EXISTS trg_cascade_soft_delete_project ON projects;
DROP TRIGGER IF EXISTS trg_cascade_soft_delete_task ON tasks;
DROP TRIGGER IF EXISTS trg_cascade_soft_delete_version ON versions;

-- Create soft delete cascade triggers
CREATE TRIGGER trg_cascade_soft_delete_project
    AFTER
        UPDATE
    ON projects
    FOR EACH ROW EXECUTE FUNCTION cascade_soft_delete_project();
CREATE TRIGGER trg_cascade_soft_delete_task
    AFTER
        UPDATE
    ON tasks
    FOR EACH ROW EXECUTE FUNCTION cascade_soft_delete_task();
CREATE TRIGGER trg_cascade_soft_delete_version
    AFTER
        UPDATE
    ON versions
    FOR EACH ROW EXECUTE FUNCTION cascade_soft_delete_version();