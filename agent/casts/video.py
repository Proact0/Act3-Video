from __future__ import annotations
import os
from typing import List, Dict, Any, Optional

from moviepy.editor import (
    ImageClip, 
    AudioFileClip, 
    CompositeVideoClip, 
    concatenate_videoclips, 
    TextClip, 
    vfx
)
import numpy as np

# 기본 영상 설정
W, H = 1080, 1920
FPS = 30

def _ken_burns(
    img_path: str,
    duration: float,
    zoom_start: float = 1.05,
    zoom_end: float = 1.15,
    pan: str = "center"
) -> ImageClip:
    """
    간단 Ken Burns: 시작/끝 줌만 적용(+선택 팬).
    pan: 'center' | 'top' | 'bottom' | 'left' | 'right'
    """
    clip = ImageClip(img_path).resize(height=H).on_color(size=(W, H), color=(0,0,0))
    # scale 애니메이션
    def scaler(t):
        # t ∈ [0, duration]
        r = t / max(0.0001, duration)
        z = zoom_start + (zoom_end - zoom_start)*r
        return z
    animated = clip.fx(vfx.resize, scaler)

    # 팬을 position으로 흉내
    if pan == "top":
        pos = ("center", "top")
    elif pan == "bottom":
        pos = ("center", "bottom")
    elif pan == "left":
        pos = ("left", "center")
    elif pan == "right":
        pos = ("right", "center")
    else:
        pos = ("center", "center")

    animated = animated.set_position(pos).set_duration(duration)
    return animated

def _subtitle(dialog: str, duration: float) -> Optional[TextClip]:
    if not dialog:
        return None
    txt = TextClip(
        dialog,
        fontsize=54,
        font="AppleSDGothicNeo-Bold" if os.name == "posix" else "Arial",
        color="white",
        stroke_color="black",
        stroke_width=2,
        method="caption",
        size=(int(W*0.85), None),
        align="center"
    ).set_duration(duration)
    # 하단 안전영역
    return txt.set_position(("center", H - 220))

def _pan_pattern(i: int) -> str:
    # 컷 번갈아가며 팬 방향 바꾸기
    return ["center","left","right","top","bottom"][i % 5]

def build_video_from_images(
    images: List[str],
    beats: List[Dict[str, Any]],
    out_path: str,
    *,
    bgm_path: Optional[str] = None,
    tts_path: Optional[str] = None,
    crossfade: float = 0.4,
    fps: int = FPS
) -> str:
    """
    images: 씬별 이미지 경로(길이는 beats 이상/동일 권장; 부족하면 마지막 이미지 반복)
    beats: [{"t": sec, "scene": "...", "dialog": "..."}]
    """
    if not beats:
        raise ValueError("beats가 비어있습니다.")
    # 각 컷 duration 계산: 다음 컷 시작 - 현재 컷 시작 (마지막 컷은 평균값/혹은 3초)
    starts = [int(b.get("t", 0)) for b in beats]
    # duration 추정
    durs = []
    for i in range(len(starts)):
        if i < len(starts) - 1:
            durs.append(max(1.0, starts[i+1] - starts[i]))
        else:
            # 마지막 컷 fallback 3초
            durs.append(max(1.5, np.median(durs) if durs else 3.0))

    # 이미지 수 보정
    if len(images) < len(beats):
        if images:
            images = images + [images[-1]] * (len(beats) - len(images))
        else:
            raise ValueError("이미지 목록이 비어있습니다.")

    # 컷 조립
    vclips = []
    for i, (b, img) in enumerate(zip(beats, images)):
        dialog = b.get("dialog", "")
        dur = float(durs[i])
        pan = _pan_pattern(i)
        kb = _ken_burns(img, dur, zoom_start=1.03, zoom_end=1.11, pan=pan)
        sub = _subtitle(dialog, dur)
        if sub is not None:
            comp = CompositeVideoClip([kb, sub], size=(W, H)).set_duration(dur)
        else:
            comp = kb
        vclips.append(comp)

    # 크로스페이드로 붙이기
    video = concatenate_videoclips(vclips, method="compose", padding=-crossfade)
    video = video.set_fps(fps)

    # 오디오 믹스
    audiotracks = []
    if bgm_path and os.path.isfile(bgm_path):
        bgm = AudioFileClip(bgm_path).volumex(0.4)
        if bgm.duration < video.duration:
            # 루프
            loops = int(video.duration // bgm.duration) + 1
            bgm = concatenate_videoclips([bgm] * loops).audio.set_duration(video.duration)
        else:
            bgm = bgm.audio.set_duration(video.duration)
        audiotracks.append(bgm)
    if tts_path and os.path.isfile(tts_path):
        tts = AudioFileClip(tts_path).volumex(0.9).audio.set_duration(video.duration)
        audiotracks.append(tts)
    if audiotracks:
        from moviepy.audio.AudioClip import CompositeAudioClip
        audio = CompositeAudioClip(audiotracks).set_duration(video.duration)
        video = video.set_audio(audio)

    # 렌더
    out_dir = os.path.dirname(out_path) or "."
    os.makedirs(out_dir, exist_ok=True)
    video.write_videofile(
        out_path,
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="medium",
        bitrate="6500k"
    )
    return out_path
