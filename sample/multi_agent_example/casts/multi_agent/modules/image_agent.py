import os
import random
import requests
from dotenv import load_dotenv

# .env 로드 (프로젝트 루트에 .env 파일에 UNSPLASH_ACCESS_KEY=... 넣어두세요)
load_dotenv()
ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

# 한국어 → 영어 키워드 매핑 (원하는 키워드 계속 추가 가능)
KW_MAP = {
    "탈모": ["hair loss", "scalp care", "healthy hair", "herbal shampoo", "hair treatment"],
    "치킨": ["fried chicken", "crispy chicken", "chicken meal", "chicken wings"],
    "피자": ["pizza", "cheese pizza", "pepperoni pizza", "pizza slice"],
    "커피": ["coffee", "latte art", "barista", "coffee beans"],
    "햄버거": ["burger", "cheeseburger", "fast food burger"],
}

def _ensure_shots(shotlist_value):
    """shotlist가 dict 또는 list로 올 수 있으니 안전하게 리스트로 변환."""
    if isinstance(shotlist_value, list):
        return shotlist_value
    if isinstance(shotlist_value, dict):
        # {"shots": [...]} 형태 지원
        return shotlist_value.get("shots", [])
    # 그 외는 비어있는 리스트 처리
    return []

def _extract_text(shot_item):
    """샷 항목에서 검색용 텍스트 추출 (키 이름이 달라도 유연 처리)."""
    if isinstance(shot_item, dict):
        for k in ("text", "desc", "description", "beat", "title"):
            if k in shot_item and isinstance(shot_item[k], str) and shot_item[k].strip():
                return shot_item[k].strip()
        return str(shot_item)
    return str(shot_item)

def _pick_search_terms(base_text, prompt):
    """
    프롬프트/샷 텍스트에 포함된 한글 키워드를 찾아 영어 검색어 세트 반환.
    없으면 base_text 자체를 검색어로 사용.
    """
    terms = []
    for ko_kw, en_list in KW_MAP.items():
        if (isinstance(prompt, str) and ko_kw in prompt) or (isinstance(base_text, str) and ko_kw in base_text):
            terms.extend(en_list)
    if not terms:
        # 매핑 없으면 기본 텍스트로 검색
        terms = [base_text]
    return terms

def _search_unsplash(query, per_page=10):
    """
    Unsplash 검색 API 사용 (search/photos).
    per_page 결과 중 하나를 랜덤 선택해 중복 확률 낮춤.
    """
    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": query,
        "per_page": per_page,
        "content_filter": "high",
        "client_id": ACCESS_KEY,
    }
    headers = {"Accept-Version": "v1", "Cache-Control": "no-cache"}
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    if resp.status_code != 200:
        print(f"[image_agent] Unsplash 검색 실패 ({resp.status_code}): {resp.text[:200]}")
        return None
    data = resp.json()
    results = data.get("results", []) or []
    if not results:
        return None
    picked = random.choice(results)
    return picked["urls"]["regular"]

def run(state):
    if not ACCESS_KEY:
        raise RuntimeError("[image_agent] UNSPLASH_ACCESS_KEY 환경변수 없음! (.env에 넣고 재실행하세요)")

    # shotlist 안전 파싱
    raw_shotlist = state.get("shotlist", [])
    shots = _ensure_shots(raw_shotlist)
    if not shots:
        print("[image_agent] shots 없음 → 스킵")
        return state

    prompt = state.get("prompt", "")  # 전체 프롬프트도 힌트로 사용
    out_dir = "outputs/images"
    os.makedirs(out_dir, exist_ok=True)

    image_files = []
    for idx, shot in enumerate(shots, start=1):
        text = _extract_text(shot)
        search_terms = _pick_search_terms(text, prompt)

        # orientation 랜덤으로 다양화
        orientation = random.choice(["landscape", "portrait", "squarish"])
        # 검색어도 랜덤 선택 (중복 줄이기)
        query = random.choice(search_terms)

        # 검색 호출
        img_url = _search_unsplash(query, per_page=10)
        # 검색이 비었으면 샷 텍스트로 마지막 시도
        if not img_url:
            img_url = _search_unsplash(text, per_page=10)

        if not img_url:
            print(f"[image_agent] 이미지 없음: '{text}' (query 후보: {search_terms[:3]})")
            continue

        try:
            img_resp = requests.get(img_url, headers={"Cache-Control": "no-cache"}, timeout=10)
            img_resp.raise_for_status()
            out_path = os.path.join(out_dir, f"shot_{idx}.jpg")
            with open(out_path, "wb") as f:
                f.write(img_resp.content)
            image_files.append(out_path)
            print(f"[image_agent] 저장됨: {out_path}  ← query='{query}', orientation='{orientation}'")
        except Exception as e:
            print(f"[image_agent] 다운로드 실패 (shot {idx}): {e}")

    state["image_files"] = image_files
    return state
