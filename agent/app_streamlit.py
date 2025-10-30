# streamlit.py
# 🎬 Shortform Scenario → (button) 2D Animation Prompts → (optional) Image→Video

# --- 표준 임포트 (E402 위반 방지) ---
import os
import sys
import json
from typing import Any, Dict, Optional, List

from dotenv import load_dotenv
import streamlit as st

# ===== 경로/환경 부트스트랩 =====
st.set_page_config(page_title="Shortform Scenario Agent", page_icon="🎬", layout="centered")
load_dotenv()

def _bootstrap_paths() -> None:
    """agent/ 내부 모듈 임포트를 위해 sys.path 보정"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)

_bootstrap_paths()

# ===== 내부 모듈 임포트 (실패해도 UI는 뜨게) =====
_generate = None
_to_text_script = None
_build_scene_prompts = None
_build_main_prompt = None
_parse_brief = None
_import_error: Optional[str] = None
try:
    from casts.pipeline import generate as _generate  # noqa: F401
    from casts.formatter import to_text_script as _to_text_script  # noqa: F401
    from casts.mj_scene import build_scene_prompts as _build_scene_prompts  # noqa: F401
    from casts.mj import build_midjourney_prompt as _build_main_prompt  # noqa: F401
    from casts.brief import parse_brief as _parse_brief  # noqa: F401
except Exception as e:
    _import_error = f"{type(e).__name__}: {e}"

# =====(선택) 비디오 합성 의존성 (없어도 앱 구동됨)=====
_has_moviepy = True
try:
    from moviepy.editor import (
        ImageClip,
        AudioFileClip,
        CompositeVideoClip,
        concatenate_videoclips,
        TextClip,
        vfx,
    )
    import numpy as np
except Exception:
    _has_moviepy = False


# ================= 공통 UI =================
st.title("🎬 Shortform Scenario Agent")
st.caption("OpenRouter `gpt-oss-20b:free` 기반 — 2-Step: 시나리오 → (버튼) 씬별 2D 애니 프롬프트")

with st.sidebar:
    st.header("⚙️ Settings")
    key_exists = bool(os.getenv("OPENROUTER_API_KEY"))
    if key_exists:
        st.success("OPENROUTER_API_KEY: detected", icon="🔑")
    else:
        st.warning("Set OPENROUTER_API_KEY in env.", icon="⚠️")

    # 시나리오 옵션
    equalize = st.toggle("Equalize cut times", value=True)
    out_format = st.radio("Scenario Output", ["JSON", "TEXT"], horizontal=True, index=0)

    # 프롬프트 옵션 (stylize 제거됨)
    mj_ar = st.selectbox("MJ Aspect Ratio", ["9:16", "3:4", "1:1", "4:5"], index=0)
    mj_version = st.selectbox("MJ Version", ["6.0", "6.1"], index=0)
    mj_quality = st.selectbox("MJ Quality", ["1.0", "0.5", "2.0"], index=0)

    st.markdown("---")
    st.markdown("Flow: ① 시나리오 → ② 프롬프트 → (옵션) ③ 영상합성")

# 임포트 에러 공지
if _import_error:
    st.error(f"Import error: {_import_error}")
    st.info("폴더 구조/경로를 확인해주세요. 그래도 폼은 표시됩니다.")

# 세션 상태
if "scenario_data" not in st.session_state:
    st.session_state["scenario_data"] = None
if "brief_text" not in st.session_state:
    st.session_state["brief_text"] = ""

# ================= 1) 시나리오 생성 =================
with st.form("scenario_form"):
    st.subheader("📝 1) 시나리오 생성")

    col1, col2 = st.columns(2)
    with col1:
        product = st.text_input("제품", placeholder="예: 치킨")
        message = st.text_input("핵심 메시지/USP", placeholder="예: 바삭함과 육즙")
        target = st.text_input("타깃", placeholder="예: 10대~20대")
        background = st.text_input("배경", placeholder="예: 퇴근길 작은 포장마차")
    with col2:
        tone = st.text_input("톤(쉼표로 구분)", placeholder="예: 따뜻함, 레트로")
        narration = st.text_input("나레이션/대사 스타일", placeholder="예: 담백하고 현실적으로")
        music = st.text_input("음악 키워드", placeholder="예: 어쿠스틱 기타")
        banned = st.text_input("금지어(쉼표로 구분)", placeholder="예: 치료, 다이어트")

    st.markdown("### ⏱️ 길이 & 컷")
    dur_col, cuts_col = st.columns(2)
    with dur_col:
        duration = st.number_input("길이(초)", min_value=5, max_value=120, value=60, step=5)
    with cuts_col:
        cuts = st.number_input("컷 수(0=자동)", min_value=0, max_value=12, value=6, step=1)

    btn_generate = st.form_submit_button("🚀 시나리오 생성")


def _kv_line(k: str, v: str) -> str:
    return f"{k}={v}" if v is not None and v != "" else ""


def _build_kv_text() -> str:
    lines = [
        _kv_line("제품", product),
        _kv_line("메시지", message),
        _kv_line("타깃", target),
        _kv_line("톤", tone),
        _kv_line("배경", background),
        _kv_line("길이", str(duration)),
        _kv_line("컷", str(cuts) if cuts > 0 else ""),
        _kv_line("나레이션", narration),
        _kv_line("음악", music),
        _kv_line("금지어", banned),
    ]
    return "\n".join([x for x in lines if x])


if btn_generate:
    if _generate is None or _to_text_script is None:
        st.error("내부 모듈 로드 실패. 위 임포트 에러 확인.")
    else:
        brief_text = _build_kv_text()
        st.session_state["brief_text"] = brief_text
        with st.status("Generating scenario...", expanded=False) as status:
            status.update(label="Calling OpenRouter & building scenario", state="running")
            try:
                # 1단계는 시나리오만 생성 (MJ 프롬프트 끔)
                data: Dict[str, Any] = _generate(
                    brief_text,
                    equalize=equalize,
                    mj_generate=False,
                )  # type: ignore
            except Exception as err:
                st.error(f"Unexpected error: {type(err).__name__}: {err}")
                status.update(label="Failed", state="error")
            else:
                status.update(label="Done", state="complete")
                st.success("시나리오 생성 완료! ✅")
                st.session_state["scenario_data"] = data

                if isinstance(data, dict) and data.get("error"):
                    st.error(f"Error: {data.get('error')}")
                    detail = data.get("detail") or data.get("raw")
                    if detail:
                        with st.expander("Raw response"):
                            st.code(str(detail))
                else:
                    if out_format == "TEXT":
                        try:
                            script = _to_text_script(data)  # type: ignore
                        except Exception:
                            script = json.dumps(data, ensure_ascii=False, indent=2)
                        st.code(script)
                    else:
                        try:
                            st.json(data)
                        except Exception:
                            st.code(json.dumps(data, ensure_ascii=False, indent=2))

# ================= 2) 씬별 2D 애니 프롬프트 =================
st.markdown("---")
st.subheader("🎨 2) 씬별 프롬프트 생성 (2D Animation, stylize 없음)")

btn_prompts = st.button("✨ 씬별 프롬프트 생성")

if btn_prompts:
    data = st.session_state.get("scenario_data")
    brief_text = st.session_state.get("brief_text", "")
    if not data:
        st.warning("먼저 시나리오를 생성해 주세요.")
    elif _build_scene_prompts is None or _parse_brief is None or _build_main_prompt is None:
        st.error("내부 모듈 로드 실패. 위 임포트 에러 확인.")
    else:
        try:
            brief = _parse_brief(brief_text)
            # 씬별 2D 프롬프트 (stylize 제거)
            scene_prompts = _build_scene_prompts(
                brief,
                data,
                aspect_ratio=mj_ar,
                version=mj_version,
            )
            data["scene_prompts"] = scene_prompts

            # 대표 썸네일 프롬프트(2D, stylize 없음)
            data["midjourney_prompt"] = _build_main_prompt(
                brief,
                data,
                beat_index=0,
                aspect_ratio=mj_ar,
                version=mj_version,
                quality=float(mj_quality),
            )

            st.success("프롬프트 생성 완료! ✅")
            st.markdown("#### 🎬 Scene Prompts (2D animation)")
            for i, p in enumerate(scene_prompts, 1):
                st.markdown(f"**Scene {i}:**")
                st.code(p)

            st.markdown("#### 🖼️ Main Thumbnail Prompt (2D animation)")
            st.code(data["midjourney_prompt"])

            # 세션 업데이트
            st.session_state["scenario_data"] = data

        except Exception as err:
            st.error(f"Unexpected error: {type(err).__name__}: {err}")

# ================= 3) (옵션) 이미지 → 영상 합성 =================
st.markdown("---")
st.subheader("🎞 3) (선택) 이미지 업로드 후 영상 합성")

if not _has_moviepy:
    st.info("MoviePy/Numpy 미설치 상태입니다. 영상 합성을 사용하려면:\n\n"
            "`uv add moviepy pillow numpy` 후 다시 실행하세요.")
else:
    colA, colB = st.columns([2, 1])
    with colA:
        uploaded = st.file_uploader(
            "씬별 이미지 업로드 (beats 순서대로 여러 장 선택)",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True,
        )
        bgm = st.file_uploader("BGM(Optional)", type=["mp3", "wav", "m4a"], accept_multiple_files=False)
    with colB:
        out_name = st.text_input("출력 파일명", value="output.mp4")
        crossfade = st.slider("크로스페이드(초)", 0.0, 1.0, 0.4, 0.1)

    btn_video = st.button("🎬 영상 만들기")

    # ===== 비디오 합성 유틸 =====
    W, H, FPS = 1080, 1920, 30

    def _ken_burns(img_path: str, duration: float, zoom_start: float = 1.03, zoom_end: float = 1.10):
        clip = ImageClip(img_path).resize(height=H).on_color(size=(W, H), color=(0, 0, 0))
        def scaler(t):
            r = t / max(0.0001, duration)
            return zoom_start + (zoom_end - zoom_start) * r
        return clip.fx(vfx.resize, scaler).set_duration(duration)

    def _subtitle(dialog: str, duration: float):
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
            size=(int(W * 0.85), None),
            align="center",
        ).set_duration(duration)
        return txt.set_position(("center", H - 220))

    def _durations_from_beats(beats: List[Dict[str, Any]]) -> List[float]:
        starts = [int(b.get("t", 0)) for b in beats]
        durs: List[float] = []
        for i in range(len(starts)):
            if i < len(starts) - 1:
                durs.append(max(1.0, starts[i + 1] - starts[i]))
            else:
                durs.append(max(1.5, float(np.median(durs) if durs else 3.0)))
        return durs

    def build_video_from_images(
        images: List[str],
        beats: List[Dict[str, Any]],
        out_path: str,
        *,
        bgm_path: Optional[str] = None,
        crossfade_sec: float = 0.4,
        fps: int = FPS,
    ) -> str:
        if not beats:
            raise ValueError("beats가 비어있습니다.")
        durs = _durations_from_beats(beats)
        if len(images) < len(beats):
            if images:
                images = images + [images[-1]] * (len(beats) - len(images))
            else:
                raise ValueError("이미지 목록이 비어있습니다.")

        vclips = []
        for i, (b, img) in enumerate(zip(beats, images)):
            dialog = b.get("dialog", "")
            dur = float(durs[i])
            kb = _ken_burns(img, dur)
            sub = _subtitle(dialog, dur)
            comp = CompositeVideoClip([kb, sub], size=(W, H)).set_duration(dur) if sub else kb
            vclips.append(comp)

        video = concatenate_videoclips(vclips, method="compose", padding=-crossfade_sec).set_fps(fps)

        if bgm_path and os.path.isfile(bgm_path):
            bgm_clip = AudioFileClip(bgm_path).volumex(0.4)
            if bgm_clip.duration < video.duration:
                loops = int(video.duration // bgm_clip.duration) + 1
                bgm_clip = concatenate_videoclips([bgm_clip] * loops).audio.set_duration(video.duration)
            else:
                bgm_clip = bgm_clip.audio.set_duration(video.duration)
            video = video.set_audio(bgm_clip)

        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        video.write_videofile(out_path, fps=fps, codec="libx264", audio_codec="aac", threads=4, preset="medium")
        return out_path

    # ===== 실행 =====
    if btn_video:
        data = st.session_state.get("scenario_data")
        if not data or not isinstance(data, dict) or "beats" not in data:
            st.warning("먼저 시나리오를 생성하세요.")
        elif not uploaded:
            st.error("이미지를 업로드해야 합니다.")
        else:
            try:
                import tempfile

                tmpdir = tempfile.mkdtemp(prefix="sfv_")
                img_paths: List[str] = []
                for i, uf in enumerate(uploaded):
                    p = os.path.join(tmpdir, f"scene_{i:02d}.png")
                    with open(p, "wb") as f:
                        f.write(uf.read())
                    img_paths.append(p)

                bgm_path = None
                if bgm:
                    bgm_path = os.path.join(tmpdir, "bgm_" + bgm.name)
                    with open(bgm_path, "wb") as f:
                        f.write(bgm.read())

                out_path = os.path.join(tmpdir, out_name)
                with st.status("렌더링 중...", expanded=False) as status:
                    status.update(label="FFmpeg 렌더링 진행", state="running")
                    result = build_video_from_images(
                        images=img_paths,
                        beats=data["beats"],
                        out_path=out_path,
                        bgm_path=bgm_path,
                        crossfade_sec=float(crossfade),
                        fps=30,
                    )
                    status.update(label="완료", state="complete")

                st.success("영상 합성 완료! ✅")
                st.video(result)
                st.download_button("⬇️ MP4 다운로드", data=open(result, "rb"), file_name=out_name, mime="video/mp4")

            except Exception as err:
                st.error(f"Unexpected error: {type(err).__name__}: {err}")
