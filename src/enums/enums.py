from enum import Enum


class ParentType(str, Enum):
    asset = "asset"
    shot = "shot"


class PublishType(str, Enum):
    geo = "geo"
    rig = "rig"
    comp = "comp"
    fx = "fx"
    layout = "layout"
    prep = "prep"
    tex = "tex"


class Representation(str, Enum):
    usd = "usd"
    abc = "abc"
    exr = "exr"
    vdb = "vdb"
    mov = "mov"
    png = "png"


class VersionStatus(str, Enum):
    draft = "draft"
    review = "review"
    approved = "approved"
    rejected = "rejected"


class TaskStatus(str, Enum):
    WIP = "WIP"
    READY = "READY"
    HOLD = "HOLD"
    DONE = "DONE"


class RenderJobStatus(str, Enum):
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"


class AssetType(str, Enum):
    Vehicle = "Vehicle"
    Creature = "Creature"
    Character = "Character"
    Effect = "Effect"
    Environment = "Environment"