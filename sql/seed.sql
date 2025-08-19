-- slate_runner: Film Production DB Init
-- Clears existing data and seeds projects, assets, shots, tasks, versions, and publishes
-- with sample films (Alien, Avatar, Interstellar) to illustrate the pipeline workflow
-- and fixed human-readable UIDs and randomised created_at times.

-- Clear existing data
TRUNCATE publishes, versions, tasks, shots, assets, projects RESTART IDENTITY CASCADE;

-- Projects
INSERT INTO projects (uid, name) VALUES
  ('PROJ_AL13N5', 'Alien'),
  ('PROJ_ARR1VL', 'Arrival'),
  ('PROJ_AV4TAR', 'Avatar'),
  ('PROJ_BL4DER', 'BladeRunner'),
  ('PROJ_EV3RYT', 'EverythingEverywhere'),
  ('PROJ_GR4VIT', 'Gravity'),
  ('PROJ_GR33NK', 'GreenKnight'),
  ('PROJ_1NTER5', 'Interstellar'),
  ('PROJ_K1NGK0', 'KingKong'),
  ('PROJ_OPP3NH', 'Oppenheimer');

-- Assets
INSERT INTO assets (uid, project_id, name, type) VALUES
  ('ASSET_HEPTA1', 'PROJ_ARR1VL', 'HeptapodShip',     'Vehicle'),
  ('ASSET_KSP1NN', 'PROJ_BL4DER', 'KSpinner',         'Vehicle'),
  ('ASSET_X3N0MO', 'PROJ_AL13N5', 'Xenomorph',        'Creature'),
  ('ASSET_ENDUR1', 'PROJ_1NTER5', 'EnduranceShip',    'Vehicle'),
  ('ASSET_NEYT1R', 'PROJ_AV4TAR', 'Neytiri',          'Character'),
  ('ASSET_NUKEFX', 'PROJ_OPP3NH', 'NuclearBombFX',    'Effect'),
  ('ASSET_GRNKT1', 'PROJ_GR33NK', 'GreenKnight',      'Character'),
  ('ASSET_B4GELF', 'PROJ_EV3RYT', 'BagelFX',          'Effect'),
  ('ASSET_EMPSC1', 'PROJ_K1NGK0', 'EmpireStateScene', 'Environment'),
  ('ASSET_DEBR15', 'PROJ_GR4VIT', 'DebrisField',      'Environment');

-- Shots
INSERT INTO shots (uid, project_id, seq, shot, frame_in, frame_out, fps, colorspace) VALUES
  ('SHOT_ARR010', 'PROJ_ARR1VL', 'SEQ01', 'SHOTN_010', 1001, 1060, 24.000, 'sRGB'),
  ('SHOT_BLD020', 'PROJ_BL4DER', 'SEQ02', 'SHOTN_020', 2001, 2080, 24.000, 'sRGB'),
  ('SHOT_ALN030', 'PROJ_AL13N5', 'SEQ03', 'SHOTN_030', 3001, 3050, 24.000, 'sRGB'),
  ('SHOT_INT040', 'PROJ_1NTER5', 'SEQ01', 'SHOTN_040', 4001, 4100, 24.000, 'sRGB'),
  ('SHOT_AVT050', 'PROJ_AV4TAR', 'SEQ05', 'SHOTN_050', 5001, 5120, 24.000, 'sRGB'),
  ('SHOT_EVE060', 'PROJ_EV3RYT', 'SEQ07', 'SHOTN_060', 6001, 6100, 24.000, 'sRGB'),
  ('SHOT_GRV070', 'PROJ_GR4VIT', 'SEQ01', 'SHOTN_070', 7001, 7060, 24.000, 'sRGB'),
  ('SHOT_KNG080', 'PROJ_K1NGK0', 'SEQ03', 'SHOTN_080', 8001, 8080, 24.000, 'sRGB'),
  ('SHOT_OPP090', 'PROJ_OPP3NH', 'SEQ04', 'SHOTN_090', 9001, 9060, 24.000, 'sRGB'),
  ('SHOT_GRN100', 'PROJ_GR33NK', 'SEQ02', 'SHOTN_100', 10001, 10080, 24.000, 'sRGB');

-- Tasks
INSERT INTO tasks (uid, parent_type, parent_id, name, assignee, status, project_id) VALUES
  ('TASK_MD1ALN', 'asset', 'ASSET_HEPTA1', 'Modeling',     'Jane',    'WIP',   'PROJ_ARR1VL'),
  ('TASK_RG1XEN', 'asset', 'ASSET_X3N0MO', 'Rigging',      'Alex',    'READY', 'PROJ_AL13N5'),
  ('TASK_CP1ALN', 'shot',  'SHOT_ALN030',  'Compositing',  'Lucas',   'WIP',   'PROJ_AL13N5'),
  ('TASK_FX1INT', 'shot',  'SHOT_INT040',  'FXSim',        'Claire',  'HOLD',  'PROJ_1NTER5'),
  ('TASK_AN1BGL', 'asset', 'ASSET_B4GELF', 'Animation',    'Evelyn',  'WIP',   'PROJ_EV3RYT'),
  ('TASK_LY1DBR', 'asset', 'ASSET_DEBR15', 'Layout',       'Kowalski','READY', 'PROJ_GR4VIT'),
  ('TASK_FX1KNG', 'shot',  'SHOT_KNG080',  'FXExplosion',  'Ann',     'WIP',   'PROJ_K1NGK0'),
  ('TASK_CP1GRN', 'shot',  'SHOT_GRN100',  'CompPrep',     'Dev',     'READY', 'PROJ_GR33NK'),
  ('TASK_SM1OPP', 'shot',  'SHOT_OPP090',  'SimExplosion', 'Nolan',   'HOLD',  'PROJ_OPP3NH'),
  ('TASK_TX1NEY', 'asset', 'ASSET_NEYT1R', 'TexturePaint', 'Riley',   'WIP',   'PROJ_AV4TAR');

-- Versions
INSERT INTO versions (uid, project_id, task_id, vnum, status, created_by, created_at) VALUES
  ('VER_ALN001', 'PROJ_AL13N5', 'TASK_MD1ALN', 1, 'draft',    'Jane',    now() - (random() * interval '30 days')),
  ('VER_XEN001', 'PROJ_AL13N5', 'TASK_RG1XEN', 1, 'review',   'Alex',    now() - (random() * interval '30 days')),
  ('VER_ALN002', 'PROJ_AL13N5', 'TASK_CP1ALN', 1, 'approved', 'Lucas',   now() - (random() * interval '30 days')),
  ('VER_INT001', 'PROJ_1NTER5', 'TASK_FX1INT', 1, 'rejected', 'Claire',  now() - (random() * interval '30 days')),
  ('VER_BGL001', 'PROJ_EV3RYT', 'TASK_AN1BGL', 1, 'draft',    'Evelyn',  now() - (random() * interval '30 days')),
  ('VER_DBR001', 'PROJ_GR4VIT', 'TASK_LY1DBR', 1, 'review',   'Kowalski',now() - (random() * interval '30 days')),
  ('VER_KNG001', 'PROJ_K1NGK0', 'TASK_FX1KNG', 1, 'approved', 'Ann',     now() - (random() * interval '30 days')),
  ('VER_GRN001', 'PROJ_GR33NK', 'TASK_CP1GRN', 1, 'review',   'Dev',     now() - (random() * interval '30 days')),
  ('VER_OPP001', 'PROJ_OPP3NH', 'TASK_SM1OPP', 1, 'rejected', 'Nolan',   now() - (random() * interval '30 days')),
  ('VER_NEY001', 'PROJ_AV4TAR', 'TASK_TX1NEY', 1, 'draft',    'Riley',   now() - (random() * interval '30 days'));

-- Publishes
INSERT INTO publishes (uid, project_id, version_id, type, representation, path, metadata, created_at) VALUES
  ('PUB_ALN001', 'PROJ_ARR1VL', 'VER_ALN001', 'geo',   'usd', '/assets/heptapod_ship/v001/heptapod.usd',  '{}'::jsonb, now() - (random() * interval '30 days')),
  ('PUB_XEN001', 'PROJ_AL13N5', 'VER_XEN001', 'rig',   'abc', '/assets/xenomorph/v001/xeno_rig.abc',      '{}'::jsonb, now() - (random() * interval '30 days')),
  ('PUB_ALN002', 'PROJ_AL13N5', 'VER_ALN002', 'comp',  'exr', '/shots/alien/shot030/v001/final_comp.exr', '{}'::jsonb, now() - (random() * interval '30 days')),
  ('PUB_INT001', 'PROJ_1NTER5', 'VER_INT001', 'fx',    'vdb', '/shots/interstellar/shot040/v001/nuke.vdb','{}'::jsonb, now() - (random() * interval '30 days')),
  ('PUB_BGL001', 'PROJ_EV3RYT', 'VER_BGL001', 'fx',    'mov', '/assets/everything/bagel/v001/bagelfx.mov','{}'::jsonb, now() - (random() * interval '30 days')),
  ('PUB_DBR001', 'PROJ_GR4VIT', 'VER_DBR001', 'layout','usd', '/shots/gravity/debrisfield/v001/layout.usd','{}'::jsonb,now() - (random() * interval '30 days')),
  ('PUB_KNG001', 'PROJ_K1NGK0', 'VER_KNG001', 'fx',    'vdb', '/shots/kingkong/shot080/v001/explosion.vdb','{}'::jsonb,now() - (random() * interval '30 days')),
  ('PUB_GRN001', 'PROJ_GR33NK', 'VER_GRN001', 'prep',  'exr', '/shots/greenknight/shot100/v001/prep.exr', '{}'::jsonb, now() - (random() * interval '30 days')),
  ('PUB_OPP001', 'PROJ_OPP3NH', 'VER_OPP001', 'fx',    'mov', '/shots/oppenheimer/shot090/v001/explosion.mov','{}'::jsonb,now() - (random() * interval '30 days')),
  ('PUB_NEY001', 'PROJ_AV4TAR', 'VER_NEY001', 'tex',   'png', '/assets/avatar/neytiri/v001/skin_diff.png','{}'::jsonb, now() - (random() * interval '30 days'));

