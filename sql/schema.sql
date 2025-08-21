-- slate_runner: VFX Production Pipeline Schema
-- Defines projects, assets, shots, tasks, versions, publishes, render jobs, and events,
-- with UIDs auto-generated, timestamps for versioning, and foreign keys for integrity.

-- Drop in dependency order
DROP TABLE IF EXISTS publishes, versions, tasks, shots, assets, projects, render_jobs, events CASCADE;

-- Required for gen_random_bytes()
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Helper: UID generator (PREFIX_XXXXXX)
CREATE OR REPLACE FUNCTION gen_uid(prefix TEXT)
RETURNS TEXT AS $$
BEGIN
  RETURN prefix || '_' || upper(substr(encode(gen_random_bytes(4), 'hex'), 1, 6));
END;
$$ LANGUAGE plpgsql;

-- Helper: keep updated_at fresh
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at := now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- PROJECTS
CREATE TABLE projects (
  id          SERIAL PRIMARY KEY,
  uid         TEXT UNIQUE DEFAULT gen_uid('PROJ'),
  name        TEXT UNIQUE NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_projects_updated BEFORE UPDATE ON projects
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ASSETS
CREATE TABLE assets (
  id          SERIAL PRIMARY KEY,
  uid         TEXT UNIQUE DEFAULT gen_uid('ASSET'),
  project_id  TEXT NOT NULL REFERENCES projects(uid) ON DELETE CASCADE,
  name        TEXT NOT NULL,
  type        TEXT NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(project_id, name)
);
CREATE TRIGGER trg_assets_updated BEFORE UPDATE ON assets
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- SHOTS
CREATE TABLE shots (
  id          SERIAL PRIMARY KEY,
  uid         TEXT UNIQUE DEFAULT gen_uid('SHOT'),
  project_id  TEXT NOT NULL REFERENCES projects(uid) ON DELETE CASCADE,
  seq         TEXT NOT NULL,
  shot        TEXT NOT NULL,
  frame_in    INT  NOT NULL,
  frame_out   INT  NOT NULL,
  fps         NUMERIC(6,3) DEFAULT 24.0,
  colorspace  TEXT DEFAULT 'sRGB',
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(project_id, seq, shot)
);
CREATE TRIGGER trg_shots_updated BEFORE UPDATE ON shots
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- TASKS
CREATE TABLE tasks (
  id          SERIAL PRIMARY KEY,
  uid         TEXT UNIQUE DEFAULT gen_uid('TASK'),
  project_id  TEXT REFERENCES projects(uid),
  parent_type TEXT NOT NULL CHECK (parent_type IN ('asset','shot')),
  parent_id   TEXT NOT NULL,
  name        TEXT NOT NULL,
  assignee    TEXT,
  status      TEXT NOT NULL DEFAULT 'WIP' CHECK (status IN ('WIP','READY','HOLD','DONE')),
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_tasks_updated BEFORE UPDATE ON tasks
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- VERSIONS
CREATE TABLE versions (
  id          SERIAL PRIMARY KEY,
  uid         TEXT UNIQUE DEFAULT gen_uid('VER'),
  project_id  TEXT REFERENCES projects(uid),
  task_id     TEXT NOT NULL REFERENCES tasks(uid) ON DELETE CASCADE,
  vnum        INT  NOT NULL,
  status      TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','review','approved','rejected')),
  created_by  TEXT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(task_id, vnum)
);
CREATE TRIGGER trg_versions_updated BEFORE UPDATE ON versions
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- PUBLISHES
CREATE TABLE publishes (
  id             SERIAL PRIMARY KEY,
  uid            TEXT UNIQUE DEFAULT gen_uid('PUB'),
  project_id     TEXT REFERENCES projects(uid) ON DELETE CASCADE,
  version_id     TEXT NOT NULL REFERENCES versions(uid) ON DELETE CASCADE,
  type           TEXT NOT NULL,
  representation TEXT,
  path           TEXT NOT NULL,
  metadata       JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_publishes_updated BEFORE UPDATE ON publishes
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- RENDER JOBS
CREATE TABLE render_jobs (
  id           SERIAL PRIMARY KEY,
  uid          TEXT UNIQUE DEFAULT gen_uid('RJ'),
  project_id   TEXT REFERENCES projects(uid),
  version_id   TEXT REFERENCES versions(uid) ON DELETE SET NULL,
  context      JSONB NOT NULL,
  adapter      TEXT NOT NULL,
  status       TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued','running','succeeded','failed')),
  logs         TEXT,
  submitted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_render_jobs_updated BEFORE UPDATE ON render_jobs
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- EVENTS
CREATE TABLE events (
  id         SERIAL PRIMARY KEY,
  uid        TEXT UNIQUE DEFAULT gen_uid('EVENT'),
  project_id TEXT REFERENCES projects(uid),
  kind       TEXT NOT NULL,
  payload    JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_events_updated BEFORE UPDATE ON events
FOR EACH ROW EXECUTE FUNCTION set_updated_at();
