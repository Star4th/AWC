import streamlit as st
import yaml
import markdown
import os
import base64
from pathlib import Path

# --- 전역 변수 및 경로 설정 ---
CONTENT_DIR = Path('content')
# STATIC_DIR = Path('static') # 현재 코드에서 직접 사용되지 않으므로 주석 처리 (필요시 활성화)
LOGO_IMAGE_FILE = Path(__file__).parent / "static" / "images" / "awc_logo.png" # 로고 파일 경로

# --- Helper 함수 ---
def get_image_as_base64(file_path):
    """이미지 파일을 Base64 문자열로 인코딩합니다."""
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        # st.warning(f"이미지 파일을 찾을 수 없습니다: {file_path}") # 개발 중 확인용
        return None

def local_css(file_name):
    """로컬 CSS 파일을 읽어와 앱에 적용합니다."""
    try:
        with open(file_name, encoding='utf-8') as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"CSS 파일을 찾을 수 없습니다: {file_name}")

# --- 데이터 로딩 함수 ---
@st.cache_data
def load_tournaments():
    tournaments = []
    tournaments_path = CONTENT_DIR / 'tournaments'
    if not tournaments_path.exists(): return tournaments
    for filepath in tournaments_path.glob('*.yaml'):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            data['id'] = filepath.stem
            tournaments.append(data)
    tournaments.sort(key=lambda t: t.get('date', '0000-00-00'), reverse=True)
    return tournaments

@st.cache_data
def load_players(): # 현재 app.py에서는 직접 사용 안함 (다른 페이지용)
    players = []
    players_path = CONTENT_DIR / 'players'
    if not players_path.exists(): return players
    # (이하 플레이어 로딩 로직은 제공된 코드와 동일하게 유지)
    for filepath in players_path.glob('*.md'):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            try:
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    meta_data = yaml.safe_load(parts[1])
                    actual_content_md = parts[2].strip()
                    html_content = markdown.markdown(actual_content_md)
                else:
                    meta_data = {}
                    html_content = markdown.markdown(content)
            except Exception as e:
                print(f"Error parsing MD frontmatter for player {filepath}: {e}")
                meta_data = {}
                html_content = markdown.markdown(content)
            data = meta_data
            data['id'] = filepath.stem
            data['content_html'] = html_content
            players.append(data)
    players.sort(key=lambda p: p.get('nickname', ''))
    return players

@st.cache_data
def load_news(): # 현재 app.py에서는 직접 사용 안함 (다른 페이지용)
    news_items = []
    news_path = CONTENT_DIR / 'news'
    if not news_path.exists(): return news_items
    # (이하 뉴스 로딩 로직은 제공된 코드와 동일하게 유지)
    for filepath in news_path.glob('*.md'):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            try:
                parts = content.split('---', 2)
                if len(parts) >= 3 and parts[0].strip() == '':
                    meta_data = yaml.safe_load(parts[1])
                    if meta_data is None: meta_data = {}
                    actual_content_md = parts[2].strip()
                else:
                    meta_data = {}
                    actual_content_md = content.strip()
                html_content = markdown.markdown(actual_content_md)
            except Exception as e:
                print(f"Error parsing MD frontmatter for news {filepath}: {e}")
                meta_data = {}
                html_content = markdown.markdown(content)
            data = meta_data
            data['id'] = filepath.stem
            data['content_html'] = html_content
            news_items.append(data)
        except Exception as e:
            print(f"Error loading news file {filepath}: {e}")
    news_items.sort(key=lambda item: str(item.get('date', '0000-00-00')), reverse=True)
    return news_items

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="AWC 정보 허브",
    layout="wide",
    initial_sidebar_state="collapsed" # 사이드바 초기 상태 (CSS로 완전히 숨길 예정)
)

# --- 로컬 CSS 파일 로드 ---
local_css("style.css") # style.css에 사이드바 및 토글 버튼 숨김 CSS 포함 필요

# --- 로고 이미지 데이터 준비 ---
logo_base64 = get_image_as_base64(LOGO_IMAGE_FILE)

# --- 1. 상단 네비게이션 바 (메뉴 링크만) ---
menu_html_nav_only = """
<style>
    .top-nav-bar {
        background-color: #1E1E2E; /* 다크 테마 배경색 */
        padding: 10px 25px; /* 좌우 패딩 증가 */
        display: flex;
        align-items: center;
        justify-content: flex-end; /* 메뉴 아이템 오른쪽 정렬 */
        border-bottom: 1px solid #3A3A5A; /* 약간 밝은 구분선 */
        height: 55px; /* 네비게이션 바 높이 */
    }
    .top-nav-bar .menu-items a {
        color: #E0E0E0; /* 밝은 텍스트 색상 */
        text-decoration: none;
        margin-left: 30px; /* 링크 간 간격 */
        font-size: 1.05em; /* 폰트 크기 약간 증가 */
        font-weight: 500; /* 폰트 두께 */
        transition: color 0.2s ease-in-out; /* 부드러운 색상 변경 효과 */
    }
    .top-nav-bar .menu-items a:hover {
        color: #8A6FFF; /* 호버 시 강조색 (adofai.gg 스타일 참고) */
    }
</style>
<div class="top-nav-bar">
    <div class="menu-items">
        <a href="/Tournaments" target="_self">대회 정보</a>
        <a href="/Players" target="_self">선수 정보</a>
        <a href="/News" target="_self">뉴스/공지</a>
    </div>
</div>
"""
st.markdown(menu_html_nav_only, unsafe_allow_html=True)

# --- 2. 중앙 로고 및 타이틀 헤더 ---
if logo_base64:
    logo_width = 250  # 로고 너비 (px)
    logo_alt_text = "AWC 로고 - 메인으로 가기"

    centered_logo_header_html = f"""
    <style>
        .centered-logo-header {{
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 50px 20px 30px 20px; /* 위, 좌우, 아래 여백 */
            text-align: center;
        }}
        .centered-logo-header .logo-link img {{
            width: {logo_width}px;
            height: auto;
            margin-bottom: 20px; /* 로고와 타이틀 사이 간격 */
            transition: transform 0.2s ease-in-out; /* 호버 시 약간 커지는 효과 */
        }}
        .centered-logo-header .logo-link:hover img {{
            transform: scale(1.05); /* 호버 시 이미지 약간 확대 */
        }}
        .centered-logo-header .main-title {{
            color: #F0F0F0; /* 매우 밝은 텍스트 색상 */
            font-size: 2.5em; /* 타이틀 크기 */
            font-weight: 700; /* 폰트 두께 */
            margin: 0;
            letter-spacing: 1px; /* 글자 간격 */
        }}
        @media (max-width: 768px) {{ /* 태블릿 및 모바일 화면 대응 */
            .centered-logo-header .logo-link img {{
                width: {logo_width * 0.8}px;
                margin-bottom: 15px;
            }}
            .centered-logo-header .main-title {{
                font-size: 2em;
            }}
        }}
    </style>
    <div class="centered-logo-header">
        <a href="/" target="_self" class="logo-link">
            <img src="data:image/png;base64,{logo_base64}" alt="{logo_alt_text}">
        </a>
    </div>
    """
else:
    # 로고 이미지가 없을 경우 대체 텍스트 헤더
    centered_logo_header_html = """
    <div style="text-align: center; padding: 50px 20px 30px 20px;">
        <h1 style="color: #F0F0F0; font-size: 2.5em; font-weight: 700;">AWC 정보 허브</h1>
    </div>
    """
st.markdown(centered_logo_header_html, unsafe_allow_html=True)

# --- 구분선 (선택 사항, 스타일은 style.css에서 .content-divider 등으로 정의 가능) ---
st.markdown("<hr style='border-top: 1px solid #3A3A5A; margin: 30px 0;'>", unsafe_allow_html=True)


# --- 3. 메인 콘텐츠 (대회 카드 목록) ---
# st.header("최신 대회 정보") # 중앙 타이틀이 있으므로 이 헤더는 선택 사항

# 현재 하드코딩된 카드 (나중에 load_tournaments() 결과로 대체)
# 카드 스타일은 style.css의 .custom-card 클래스에 정의되어 있다고 가정
st.markdown("""
<div class="custom-card">
    <h3>ADOFAI World Championship 2025</h3>
    <p>2024.12.9 - 2025.2.22</p>
    <!-- <a href="/Tournaments/awc2025" target="_self"><button>상세 보기</button></a> -->
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="custom-card">
    <h3>ADOFAI World Championship 2024</h3>
    <p>2023.12.8 - 2024.3.2</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="custom-card">
    <h3>ADOFAI World Championship 2023</h3>
    <p>2022.12.6 - 2023.2.15</p>
</div>
""", unsafe_allow_html=True)

# --- 푸터 (선택 사항) ---
footer_html = """
<style>
    .footer {
        text-align: center;
        padding: 40px 20px;
        color: #888888; /* 어두운 회색 */
        font-size: 0.9em;
        border-top: 1px solid #3A3A5A;
        margin-top: 50px;
    }
</style>
<div class="footer">
    © 2024 AWC 정보 허브. All rights reserved.
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)