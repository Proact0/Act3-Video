# --- 표준 임포트 (E402 준수: 반드시 맨 위에) ---
import os
import sys
import json
from typing import Any, Dict, Optional

from dotenv import load_dotenv
import streamlit as st


# --- Streamlit 설정 (import 다음에 호출) ---
st.set_page_config(page_title="Shortform Scenario Agent", page_icon="🎬", layout="centered")


def _bootstrap_paths() -> None:
    """agent/ 내부 모듈 임포트를 위해 sys.path 보정"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)


_bootstrap_paths()
load_dotenv()

# 내부 모듈 임포트는 실패해도 UI가 보이도록 try/except로 감싸기
_generate = None
_to_text_script = None
_import_error: Optional[str] = None
try:
    from casts.pipeline import generate as _generate  # noqa: F401
    from casts.formatter import to_text_script as _to_text_script  # noqa: F401
except Exception as e:
    _import_error = f"{type(e).__name__}: {e}"

# ================= UI =================

st.title("🎬 Shortform Scenario Agent")
st.caption("OpenRouter `gpt-oss-20b:free` 기반 — 60초 쇼츠 시나리오 생성")

with st.sidebar:
    st.header("⚙️ Settings")
    key_exists = bool(os.getenv("OPENROUTER_API_KEY"))
    if key_exists:
        st.success("OPENROUTER_API_KEY: 감지됨", icon="🔑")
    else:
        st.warning("환경변수에 OPENROUTER_API_KEY가 없습니다.", icon="⚠️")

    equalize = st.toggle("컷 시간 균등 분배(권장)", value=True)
    out_format = st.radio("출력 형식", ["JSON", "텍스트"], horizontal=True, index=0)
    st.markdown("---")
    st.markdown("Tip: 컷 수를 6으로 지정하면 0,10,20,30,40,50초로 자동 분배됩니다.")

# 임포트 에러가 있으면 최상단에서 보여주고도 폼은 계속 렌더
if _import_error:
    st.error(f"내부 모듈 임포트 실패: {_import_error}")
    st.info("폴더 구조/경로를 확인해주세요. 그래도 폼은 표시됩니다.")

with st.form("scenario_form"):
    st.subheader("📝 Brief")

    col1, col2 = st.columns(2)
    with col1:
        product = st.text_input("제품", placeholder="예: 복숭아향 향수")
        message = st.text_input("핵심 메시지/USP", placeholder="예: 첫사랑의 향기처럼 설렘")
        target = st.text_input("타깃", placeholder="예: 10대~20대 여학생")
        background = st.text_input("배경", placeholder="예: 햇살 드는 교실 창가")
    with col2:
        tone = st.text_input("톤(쉼표로 구분)", placeholder="예: 핑크, 맑음, 투명")
        narration = st.text_input("나레이션/대사 스타일", placeholder="예: 잔잔하고 몽환적으로")
        music = st.text_input("음악 키워드", placeholder="예: 로맨틱 피아노")
        banned = st.text_input("금지어(쉼표로 구분)", placeholder="예: 다이어트, 치료")

    st.markdown("### ⏱️ 길이 & 컷")
    dur_col, cuts_col = st.columns(2)
    with dur_col:
        duration = st.number_input("길이(초)", min_value=5, max_value=120, value=60, step=5)
    with cuts_col:
        cuts = st.number_input("컷 수(0=자동)", min_value=0, max_value=12, value=6, step=1)

    submitted = st.form_submit_button("🚀 시나리오 생성")


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


# ================= RUN =================
if submitted:
    brief_text = _build_kv_text()

    # 사전 체크: 모듈 임포트/키/네트워크 안내
    if _generate is None or _to_text_script is None:
        st.error("내부 모듈이 로드되지 않아 실행할 수 없습니다. 위의 임포트 에러를 확인하세요.")
    else:
        with st.status("생성 중...", expanded=False) as status:
            status.update(label="OpenRouter 호출 & 시나리오 생성", state="running")
            try:
                data: Dict[str, Any] = _generate(brief_text, equalize=equalize)  # type: ignore
            except Exception as err:
                st.error(f"예상치 못한 에러: {type(err).__name__}: {err}")
                status.update(label="실패", state="error")
            else:
                status.update(label="완료", state="complete")
                st.success("시나리오 생성 완료!", icon="✅")

                if isinstance(data, dict) and data.get("error"):
                    st.error(f"에러: {data.get('error')}")
                    detail = data.get("detail") or data.get("raw")
                    if detail:
                        with st.expander("상세 보기"):
                            st.code(str(detail))
                else:
                    if out_format == "텍스트":
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

# 하단 도움말
with st.expander("입력 예시 보기"):
    st.code(
        """제품=복숭아향 향수
메시지=첫사랑의 향기처럼 설렘
타깃=10대~20대 여학생
톤=핑크, 맑음, 투명
배경=햇살 드는 교실 창가
길이=60
컷=6
나레이션=잔잔하고 몽환적으로
음악=로맨틱 피아노
금지어=다이어트, 치료""",
        language="text",
    )
