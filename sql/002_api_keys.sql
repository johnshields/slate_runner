-- slate_runner: API Keys + RLS with Roles
-- Defines api_keys table, timestamps, expiry, roles, and access policies.

-- Helper: UID generator (PREFIX_XXXXXX)
CREATE OR REPLACE FUNCTION gen_uid(prefix TEXT)
RETURNS TEXT AS $$
BEGIN
  RETURN prefix || '_' || upper(substr(encode(gen_random_bytes(4), 'hex'), 1, 6));
END;
$$ LANGUAGE plpgsql;

-- ====================
-- Drop all policies (safety cleanup)
-- ====================
DO $$
DECLARE r RECORD;
BEGIN
  FOR r IN SELECT schemaname, tablename, policyname
           FROM pg_policies
           WHERE schemaname = 'public'
  LOOP
    EXECUTE format('DROP POLICY IF EXISTS %I ON %I.%I', r.policyname, r.schemaname, r.tablename);
  END LOOP;
END$$;

-- ====================
-- API_KEYS Table
-- ====================
DROP TABLE IF EXISTS api_keys CASCADE;

CREATE TABLE api_keys (
  id          SERIAL PRIMARY KEY,
  uid         TEXT UNIQUE DEFAULT gen_uid('APIK'),
  token       TEXT UNIQUE NOT NULL,
  description TEXT,
  role        TEXT NOT NULL CHECK (role IN (
                  'admin','td','atd','artist','producer','supervisor',
                  'service','system','client'
                )),
  is_admin    BOOLEAN NOT NULL DEFAULT false,
  expires_at  TIMESTAMPTZ,  -- NULL = never expires
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- keep updated_at fresh
CREATE TRIGGER trg_api_keys_updated
BEFORE UPDATE ON api_keys
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- ==============
-- Helper Functions
-- ==============
CREATE OR REPLACE FUNCTION is_valid_api_token() RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM api_keys k
    WHERE k.token = current_setting('app.current_token', true)
      AND (k.expires_at IS NULL OR k.expires_at > now())
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION has_role(target_role TEXT) RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM api_keys k
    WHERE k.token = current_setting('app.current_token', true)
      AND k.role = target_role
      AND (k.expires_at IS NULL OR k.expires_at > now())
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ====================
-- RLS for API_KEYS
-- ====================
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS api_keys_admin_policy ON api_keys;

-- Only admins manage api_keys
CREATE POLICY api_keys_admin_policy ON api_keys
  FOR ALL USING (
    is_valid_api_token() AND (has_role('admin') OR EXISTS (
      SELECT 1 FROM api_keys k WHERE k.token = current_setting('app.current_token', true) AND k.is_admin = true
    ))
  ) WITH CHECK (
    is_valid_api_token() AND (has_role('admin') OR EXISTS (
      SELECT 1 FROM api_keys k WHERE k.token = current_setting('app.current_token', true) AND k.is_admin = true
    ))
  );

-- ====================
-- RLS for pipeline tables
-- ====================
-- Pattern: SELECT allowed for all valid roles,
--          INSERT/UPDATE/DELETE limited by role granularity.

-- PROJECTS
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS projects_select_policy ON projects;
DROP POLICY IF EXISTS projects_write_policy ON projects;

CREATE POLICY projects_select_policy ON projects
  FOR SELECT USING (is_valid_api_token());

CREATE POLICY projects_write_policy ON projects
  FOR ALL USING (
    is_valid_api_token() AND (
      has_role('admin') OR has_role('td') OR has_role('supervisor')
    )
  ) WITH CHECK (
    is_valid_api_token() AND (
      has_role('admin') OR has_role('td') OR has_role('supervisor')
    )
  );

-- ASSETS
ALTER TABLE assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE assets FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS assets_select_policy ON assets;
DROP POLICY IF EXISTS assets_write_policy ON assets;

CREATE POLICY assets_select_policy ON assets
  FOR SELECT USING (is_valid_api_token());

CREATE POLICY assets_write_policy ON assets
  FOR ALL USING (
    is_valid_api_token() AND (
      has_role('admin') OR has_role('td') OR has_role('supervisor')
    )
  ) WITH CHECK (
    is_valid_api_token() AND (
      has_role('admin') OR has_role('td') OR has_role('supervisor')
    )
  );

-- SHOTS
ALTER TABLE shots ENABLE ROW LEVEL SECURITY;
ALTER TABLE shots FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS shots_select_policy ON shots;
DROP POLICY IF EXISTS shots_write_policy ON shots;

CREATE POLICY shots_select_policy ON shots
  FOR SELECT USING (is_valid_api_token());

CREATE POLICY shots_write_policy ON shots
  FOR ALL USING (
    is_valid_api_token() AND (
      has_role('admin') OR has_role('td') OR has_role('supervisor')
    )
  ) WITH CHECK (
    is_valid_api_token() AND (
      has_role('admin') OR has_role('td') OR has_role('supervisor')
    )
  );

-- TASKS
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS tasks_select_policy ON tasks;
DROP POLICY IF EXISTS tasks_write_policy ON tasks;

CREATE POLICY tasks_select_policy ON tasks
  FOR SELECT USING (is_valid_api_token());

CREATE POLICY tasks_write_policy ON tasks
  FOR ALL USING (
    is_valid_api_token() AND (
      has_role('admin') OR has_role('td') OR has_role('supervisor')
    )
  ) WITH CHECK (
    is_valid_api_token() AND (
      has_role('admin') OR has_role('td') OR has_role('supervisor')
    )
  );

-- VERSIONS
ALTER TABLE versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE versions FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS versions_select_policy ON versions;
DROP POLICY IF EXISTS versions_write_policy ON versions;

CREATE POLICY versions_select_policy ON versions
  FOR SELECT USING (is_valid_api_token());

-- artists can write their versions; supervisors/td/admin can too
CREATE POLICY versions_write_policy ON versions
  FOR ALL USING (
    is_valid_api_token() AND (
      has_role('admin') OR has_role('td') OR has_role('supervisor') OR has_role('artist')
    )
  ) WITH CHECK (
    is_valid_api_token() AND (
      has_role('admin') OR has_role('td') OR has_role('supervisor') OR has_role('artist')
    )
  );

-- PUBLISHES
ALTER TABLE publishes ENABLE ROW LEVEL SECURITY;
ALTER TABLE publishes FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS publishes_select_policy ON publishes;
DROP POLICY IF EXISTS publishes_write_policy ON publishes;

CREATE POLICY publishes_select_policy ON publishes
  FOR SELECT USING (is_valid_api_token());

CREATE POLICY publishes_write_policy ON publishes
  FOR ALL USING (
    is_valid_api_token() AND (
      has_role('admin') OR has_role('td') OR has_role('supervisor') OR has_role('artist')
    )
  ) WITH CHECK (
    is_valid_api_token() AND (
      has_role('admin') OR has_role('td') OR has_role('supervisor') OR has_role('artist')
    )
  );

-- RENDER JOBS
ALTER TABLE render_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE render_jobs FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS render_jobs_select_policy ON render_jobs;
DROP POLICY IF EXISTS render_jobs_write_policy ON render_jobs;

CREATE POLICY render_jobs_select_policy ON render_jobs
  FOR SELECT USING (is_valid_api_token());

-- services and admins can write render jobs
CREATE POLICY render_jobs_write_policy ON render_jobs
  FOR ALL USING (
    is_valid_api_token() AND (
      has_role('admin') OR has_role('td') OR has_role('service')
    )
  ) WITH CHECK (
    is_valid_api_token() AND (
      has_role('admin') OR has_role('td') OR has_role('service')
    )
  );

-- EVENTS
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE events FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS events_select_policy ON events;
DROP POLICY IF EXISTS events_write_policy ON events;

CREATE POLICY events_select_policy ON events
  FOR SELECT USING (is_valid_api_token());

-- system + admin write events
CREATE POLICY events_write_policy ON events
  FOR ALL USING (
    is_valid_api_token() AND (
      has_role('admin') OR has_role('td') OR has_role('system')
    )
  ) WITH CHECK (
    is_valid_api_token() AND (
      has_role('admin') OR has_role('td') OR has_role('system')
    )
  );

-- ====================
-- Example seed (safe dummy roles)
-- ====================
INSERT INTO api_keys (token, description, role, is_admin, expires_at) VALUES
  ('dev-admin-token',     'Admin (full access)',         'admin',     true,  NULL),
  ('dev-td-token',        'TD (pipeline full access)',   'td',        true, NULL),
  ('dev-atd-token',       'ATD (read-only)',             'atd',       false, NULL),
  ('dev-artist-token',    'Artist (versions/publishes)', 'artist',    false, NULL),
  ('dev-producer-token',  'Producer (read-only)',        'producer',  false, NULL),
  ('dev-supervisor-token','Supervisor (approve tasks)',  'supervisor',false, NULL),
  ('dev-service-token',   'Service (render farm)',       'service',   false, NULL),
  ('dev-system-token',    'System (events/logging)',     'system',    false, NULL),
  ('dev-client-token',    'Client (read-only)',          'client',    false, NULL);


