import base64
import re
from pathlib import Path

import streamlit as st

# ────────────────────────────────────────────────────────────
# 기본 설정
# ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="코맥도사 — 오늘의 업계 화제 키워드",
    page_icon="🔮",
    layout="centered",
)

# Streamlit 기본 여백/헤더/푸터를 최대한 걷어내서
# 원본 HTML(모바일 카드 UI)이 꽉 차게 보이도록 함
st.markdown(
    """
    <style>
        .block-container { padding: 0 !important; max-width: 100% !important; }
        header[data-testid="stHeader"] { background: transparent; height: 0; }
        #MainMenu, footer { visibility: hidden; }
        iframe { border: none; }
    </style>
    """,
    unsafe_allow_html=True,
)

BASE_DIR = Path(__file__).parent
HTML_PATH = BASE_DIR / "index.html"
IMAGES_DIR = BASE_DIR / "images"

MIME_MAP = {
    "png": "png",
    "jpg": "jpeg",
    "jpeg": "jpeg",
    "gif": "gif",
    "webp": "webp",
    "svg": "svg+xml",
}


@st.cache_resource(show_spinner=False)
def load_self_contained_html() -> str:
    """index.html을 읽어서 images/*.png 같은 상대경로 이미지를
    base64 data URI로 치환한 완전한(self-contained) HTML 문자열을 반환.
    st.iframe은 HTML 문자열을 iframe으로 렌더링하기 때문에
    상대경로 리소스를 그대로 두면 로드되지 않음."""
    if not HTML_PATH.exists():
        return (
            "<div style='padding:40px;font-family:sans-serif;color:#c33;'>"
            "index.html 파일을 찾을 수 없습니다. app.py와 같은 폴더에 "
            "index.html을 넣어주세요.</div>"
        )

    html = HTML_PATH.read_text(encoding="utf-8")

    def _to_data_uri(match: re.Match) -> str:
        rel_path = match.group(1)
        img_path = BASE_DIR / rel_path
        if img_path.exists():
            ext = img_path.suffix.lstrip(".").lower()
            mime = MIME_MAP.get(ext, ext)
            encoded = base64.b64encode(img_path.read_bytes()).decode("ascii")
            return f'"data:image/{mime};base64,{encoded}"'
        # 파일이 없으면 원본 그대로 둠 (HTML 자체에 img-error 폴백 처리가 있음)
        return match.group(0)

    # tarotImage: "images/xxx.png" 형태의 문자열 리터럴을 전부 치환
    html = re.sub(r'"(images/[^"]+\.(?:png|jpe?g|gif|webp|svg))"', _to_data_uri, html)
    return html


html_content = load_self_contained_html()

# 카드 UI + 랜딩 애니메이션 + 탭 전환 등을 감안해 넉넉한 높이로 렌더링.
# 필요하면 height 값을 조절하세요.
st.iframe(html_content, height=1500)
