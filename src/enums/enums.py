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
