# streamlit.py
# 🎬 Shortform Scenario Agent (scenario → scene prompts only)
# - video.py 완전 제거 버전
# - 시나리오 생성(유튜브/광고 톤 옵션 포함) → 씬별 2D 애니 프롬프트 생성

# --- 표준 임포트 (E402 방지) ---
import os
import sys
import json
from typing import Any, Dict, Optional, List

import streamlit as st
from dotenv import load_dotenv

# ===== 기본 부트스트랩 =====
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
    # 네가 가진 기존 모듈들 그대로 사용
    from casts.pipeline import generate as _generate  # noqa: F401
    from casts.formatter import to_text_script as _to_text_script  # noqa: F401
    from casts.mj_scene import build_scene_prompts as _build_scene_prompts  # noqa: F401
    from casts.mj import build_midjourney_prompt as _build_main_prompt  # noqa: F401
    from casts.brief import parse_brief as _parse_brief  # noqa: F401
except Exception as e:
    _import_error = f"{type(e).__name__}: {e}"

# ================= 공통 UI =================
st.title("🎬 Shortform Scenario Agent")
st.caption("OpenRouter `gpt-oss-20b:free` 기반 — ① 시나리오 → ② 씬별 2D 애니 프롬프트 (video.py 미사용)")

with st.sidebar:
    st.header("⚙️ Settings")
    key_exists = bool(os.getenv("OPENROUTER_API_KEY"))
    if key_exists:
        st.success("OPENROUTER_API_KEY: detected", icon="🔑")
    else:
        st.warning("Set OPENROUTER_API_KEY in .env", icon="⚠️")

    # 시나리오 옵션
    equalize = st.toggle("Equalize cut times", value=True)
    out_format = st.radio("Scenario Output", ["JSON", "TEXT"], horizontal=True, index=0)

    # 프롬프트 옵션 (stylize 제거)
    mj_ar = st.selectbox("MJ Aspect Ratio", ["9:16", "3:4", "1:1", "4:5"], index=0)
    mj_version = st.selectbox("MJ Version", ["6.0", "6.1"], index=0)
    mj_quality = st.selectbox("MJ Quality", ["1.0", "0.5", "2.0"], index=0)

    st.markdown("---")
    st.markdown("Flow: ① 시나리오 → ② 프롬프트 (영상 합성 없음)")

# 임포트 에러 공지
if _import_error:
    st.error(f"Import error: {_import_error}")
    st.info("agent/casts 경로/파일들을 확인해줘. 그래도 폼은 표시됨.")

# 세션 상태
if "scenario_data" not in st.session_state:
    st.session_state["scenario_data"] = None
if "brief_text" not in st.session_state:
    st.session_state["brief_text"] = ""

# ===== 유틸: KV 조립 =====
def _kv_line(k: str, v: Optional[str]) -> str:
    return f"{k}={v}" if v else ""

def _arr_line(k: str, arr: List[str]) -> str:
    arr = [x for x in arr if x]
    return f"{k}=" + ", ".join(arr) if arr else ""

# ================= 1) 광고형 시나리오 생성 =================
with st.form("scenario_form"):
    st.subheader("📝 1) 광고형 시나리오 생성 (YouTube Ad tone)")

    st.markdown("#### 📣 Ad Controls")
    ad_col1, ad_col2, ad_col3 = st.columns(3)
    with ad_col1:
        ad_framework = st.selectbox("광고 프레임워크", ["AIDA", "PAS", "BAB"], index=0)
    with ad_col2:
        ad_format = st.selectbox("유튜브 광고 포맷", ["6초 Bumper", "15초 Skippable", "60초 Longform"], index=2)
    with ad_col3:
        unique_cut_count = st.number_input("컷 수(0=자동)", min_value=0, max_value=12, value=6, step=1)

    st.markdown("#### 🧾 Brand & Offer")
    b1, b2, b3 = st.columns(3)
    with b1:
        brand = st.text_input("브랜드명", placeholder="예: RÉCIT")
    with b2:
        offer = st.text_input("오퍼/혜택", placeholder="예: 첫 구매 20% OFF")
    with b3:
        cta = st.text_input("CTA 문구", placeholder="예: 지금 바로 신청하기")

    st.markdown("#### 🧩 Creative Brief")
    col1, col2 = st.columns(2)
    with col1:
        product = st.text_input("제품/서비스", placeholder="예: 복숭아 향수")
        target = st.text_input("타깃", placeholder="예: 10~20대, 상큼한 무드 선호")
        background = st.text_input("배경/상황", placeholder="예: 봄날 캠퍼스, 분홍빛 꽃바람")
        tone = st.text_input("톤(쉼표로 구분)", placeholder="예: 핑크, 맑음, 미니멀")
    with col2:
        message = st.text_input("핵심 메시지/USP", placeholder="예: 상큼한 첫인상, 오래가는 잔향")
        narration = st.text_input("나레이션/대사 스타일", placeholder="예: 담백하고 현실적, 15자 내")
        music = st.text_input("음악 키워드", placeholder="예: 어쿠스틱 팝, 경쾌")
        banned = st.text_input("금지어(쉼표로 구분)", placeholder="예: 치료, 다이어트")

    st.markdown("#### ⏱️ 길이")
    # 포맷에 맞춰 기본값 제안
    default_duration = 6 if ad_format.startswith("6초") else 15 if ad_format.startswith("15초") else 60
    duration = st.number_input("영상 길이(초)", min_value=5, max_value=120, value=default_duration, step=1)

    btn_generate = st.form_submit_button("🚀 시나리오 생성")

def _build_brief_text() -> str:
    tone_list = [t.strip() for t in (st.session_state.get("_tone_raw") or "").split(",") if t.strip()]
    banned_list = [t.strip() for t in (st.session_state.get("_banned_raw") or "").split(",") if t.strip()]
    # 광고 지시문(LLM이 광고 톤으로 쓰게 룰 제공)
    ad_rules = [
        f"광고_프레임워크={st.session_state.get('_ad_framework')}",
        f"광고_포맷={st.session_state.get('_ad_format')}",
        "광고_룰=첫 0~3초 강한 훅(스킵 방지), 마지막 3초 브랜드/오퍼/CTA 확실히 노출",
        "광고_룰=각 대사 15자 이내(한글), 컷 6~10 내 권장",
        "광고_룰=유튜브 광고 톤(YouTube ad-like), 바로 이해되는 시각/행동",
        "광고_룰=브랜드 세이프티 준수(금지어 미사용), 과장·허위 금지",
        "광고_룰=텍스트는 전부 한국어",
        f"브랜드={st.session_state.get('_brand')}",
        f"오퍼={st.session_state.get('_offer')}",
        f"CTA={st.session_state.get('_cta')}",
    ]
    lines = [
        _kv_line("제품", st.session_state.get("_product")),
        _kv_line("메시지", st.session_state.get("_message")),
        _kv_line("타깃", st.session_state.get("_target")),
        _kv_line("배경", st.session_state.get("_background")),
        _arr_line("톤", tone_list),
        _kv_line("길이", str(st.session_state.get("_duration") or "")),
        _kv_line("컷", str(st.session_state.get("_cuts") or "")),
        _kv_line("나레이션", st.session_state.get("_narration")),
        _kv_line("음악", st.session_state.get("_music")),
        _arr_line("금지어", banned_list),
        *ad_rules,
    ]
    return "\n".join([x for x in lines if x])

# 폼 제출 처리
if btn_generate:
    if _generate is None or _to_text_script is None:
        st.error("내부 모듈 로드 실패. 위 임포트 에러 확인.")
    else:
        # 폼 입력값 세션에 저장
        st.session_state["_ad_framework"] = ad_framework
        st.session_state["_ad_format"] = ad_format
        st.session_state["_brand"] = brand
        st.session_state["_offer"] = offer
        st.session_state["_cta"] = cta

        st.session_state["_product"] = product
        st.session_state["_message"] = message
        st.session_state["_target"] = target
        st.session_state["_background"] = background
        st.session_state["_tone_raw"] = tone
        st.session_state["_narration"] = narration
        st.session_state["_music"] = music
        st.session_state["_banned_raw"] = banned

        st.session_state["_duration"] = duration
        st.session_state["_cuts"] = int(unique_cut_count) if unique_cut_count > 0 else ""

        brief_text = _build_brief_text()
        st.session_state["brief_text"] = brief_text

        with st.status("Generating scenario (YouTube Ad style)...", expanded=False) as status:
            status.update(label="Calling OpenRouter & building scenario", state="running")
            try:
                # 광고 지시문이 들어간 브리프 전달
                data: Dict[str, Any] = _generate(
                    brief_text,
                    equalize=equalize,
                    mj_generate=False,  # 여기서는 MJ 프롬프트 생성 안 함
                )  # type: ignore
            except Exception as err:
                st.error(f"Unexpected error: {type(err).__name__}: {err}")
                status.update(label="Failed", state="error")
            else:
                status.update(label="Done", state="complete")
                st.success("시나리오 생성 완료! ✅")
                st.session_state["scenario_data"] = data

                # 출력
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
