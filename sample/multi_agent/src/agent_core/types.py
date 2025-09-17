from typing import List, Literal, TypedDict


Aspect = Literal["9:16", "1:1", "16:9"]


class Script(TypedDict):
    title: str
    beats: List[str]


class Shot(TypedDict):
    idx: int
    text: str
    duration_sec: float


class ShotList(TypedDict):
    shots: List[Shot]


class VideoState(TypedDict, total=False):
    prompt: str
    aspect: Aspect
    duration_sec: float
    target_platforms: List[str]

    script: Script
    shotlist: ShotList
