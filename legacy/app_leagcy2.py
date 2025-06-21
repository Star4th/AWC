import streamlit as st
import yaml
import markdown # Markdown 처리를 위해 필요 (load_players, load_news에서 사용)
import os # 현재 코드에서는 직접 사용되지 않지만, 데이터 로딩 함수에서 필요할 수 있음
import base64
from pathlib import Path

# --- 전역 변수 및 경로 설정 ---
CONTENT_DIR = Path('content')
LOGO_IMAGE_FILE = Path(__file__).parent / "static" / "images" / "awc_logo.png"
# 작은 로고용 이미지 파일 (만약 다른 이미지를 사용한다면 경로 수정)
# 동일한 이미지를 사용하고 CSS로 크기만 조절할 수도 있습니다.
SMALL_LOGO_IMAGE_FILE = Path(__file__).parent / "static" / "images" / "awc_logo_legacy.png" # 작은 로고용 이미지 경로 (없으면 LOGO_IMAGE_FILE 사용)

# --- Helper 함수 ---
def get_image_as_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

def local_css(file_name):
    try:
        with open(file_name, encoding='utf-8') as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"CSS 파일을 찾을 수 없습니다: {file_name}")

# --- 데이터 로딩 함수 (이전과 동일, 여기서는 생략) ---
@st.cache_data
def load_tournaments():
    # ... (이전 코드와 동일)
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
# load_players, load_news 함수도 필요하다면 여기에 포함

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="AWC 정보 허브",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 로컬 CSS 파일 로드 ---
local_css("style.css") # style.css에 사이드바 숨김 및 기타 스타일 포함

# --- 로고 이미지 데이터 준비 ---
main_logo_base64 = get_image_as_base64(LOGO_IMAGE_FILE)
# 작은 로고가 별도로 없다면 메인 로고를 사용하고 CSS로 크기 조절
small_logo_base64 = get_image_as_base64(SMALL_LOGO_IMAGE_FILE) if SMALL_LOGO_IMAGE_FILE.exists() else main_logo_base64


# --- 1. 상단 네비게이션 바 ---
# 좌측 작은 로고 (메인 링크) + 우측 메뉴 아이템
top_nav_bar_html = f"""
<style>
    .top-nav-container {{
        background-color: #1A1A2E; /* adofai.gg 상단 바 배경색과 유사하게 */
        padding: 0 40px; /* 좌우 패딩 증가 */
        height: 60px; /* 네비게이션 바 높이 */
        display: flex;
        align-items: center;
        justify-content: space-between; /* 로고와 메뉴 아이템 양쪽 정렬 */
        border-bottom: 1px solid #2A2A45; /* 하단 구분선 */
    }}
    .top-nav-container .nav-logo a img {{
        height: 32px; /* 작은 로고 높이 */
        width: auto;
        display: block; /* 이미지 아래 불필요한 공간 제거 */
    }}
    .top-nav-container .nav-menu-items a {{
        color: #C0C0E0; /* 약간 밝은 텍스트 색상 */
        text-decoration: none;
        margin-left: 35px; /* 링크 간 간격 */
        font-size: 0.95em; /* 폰트 크기 */
        font-weight: 500;
        transition: color 0.2s ease-in-out;
    }}
    .top-nav-container .nav-menu-items a:hover {{
        color: #9A7FFF; /* 호버 시 강조색 */
    }}
    /* 모바일 화면 대응 (선택 사항) */
    @media (max-width: 768px) {{
        .top-nav-container {{
            padding: 0 20px; /* 모바일에서 좌우 패딩 줄임 */
        }}
        .top-nav-container .nav-menu-items a {{
            margin-left: 20px;
            font-size: 0.9em;
        }}
    }}
</style>
<div class="top-nav-container">
    <div class="nav-logo">
        {'<a href="/" target="_self"><img src="data:image/png;base64,' + small_logo_base64 + '" alt="AWC 홈"></a>' if small_logo_base64 else '<a href="/" target="_self" style="color:white; text-decoration:none; font-weight:bold;">AWC</a>'}
    </div>
    <div class="nav-menu-items">
        <a href="/Tournaments" target="_self">대회 정보</a>
        <a href="/Players" target="_self">선수 정보</a>
        <a href="/News" target="_self">뉴스/공지</a>
    </div>
</div>
"""
st.markdown(top_nav_bar_html, unsafe_allow_html=True)


# --- 2. 중앙 로고 (클릭 기능 없음, 크기 조절) ---
if main_logo_base64:
    # 중앙 로고 크기 (adofai.gg 메인 로고 참고하여 비율 조정)
    # 너무 크지 않게, 화면 너비에 따라 유동적으로 보이도록 max-width 사용 가능
    centered_main_logo_html = f"""
    <style>
        .main-logo-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 60px 20px 40px 20px; /* 위, 좌우, 아래 여백 */
        }}
        .main-logo-container img {{
            max-width: 350px; /* 최대 너비 설정 (이 값을 조절하여 크기 변경) */
            width: 60%;       /* 화면 너비의 60%를 차지하도록 (더 작게 하려면 % 줄임) */
            height: auto;
            display: block;
        }}
        @media (max-width: 768px) {{
            .main-logo-container img {{
                max-width: 280px;
                width: 70%;
            }}
            .main-logo-container {{
                padding: 40px 20px 30px 20px;
            }}
        }}
    </style>
    <div class="main-logo-container">
        <img src="data:image/png;base64,{main_logo_base64}" alt="AWC 로고">
    </div>
    """
else:
    # 로고 이미지가 없을 경우 대체 텍스트 헤더
    centered_main_logo_html = """
    <div style="text-align: center; padding: 60px 20px 40px 20px;">
        <h1 style="color: #F0F0F0; font-size: 3em; font-weight: 700;">AWC 정보 허브</h1>
    </div>
    """
st.markdown(centered_main_logo_html, unsafe_allow_html=True)

# --- 구분선 (선택 사항) ---
# st.markdown("<hr style='border-top: 1px solid #3A3A5A; margin: 0px 0 30px 0;'>", unsafe_allow_html=True) # 중앙 로고와 카드 사이 간격 조정


# --- 3. 메인 콘텐츠 (대회 카드 목록) ---

st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)

tournaments = load_tournaments() # 예시 데이터 로드

st.header("대회 목록")

# Streamlit 컬럼을 사용하여 카드 배치 (반응형)
# 예시: 2개의 컬럼으로 나누기
num_columns = 2
cols = st.columns(num_columns)

if tournaments:
    for i, tournament_data in enumerate(tournaments):
        # 배경 이미지 클래스 (데이터에 따라 동적으로 할당 가능)
        # 예: tournament_data 딕셔너리에 'bg_image_class': 'card-bg-tournament-1' 와 같이 저장
        bg_class = tournament_data.get('bg_image_class', '') # 기본값은 빈 문자열 (기본 배경 사용)
        
        # 또는 카드마다 다른 배경 이미지를 직접 인라인 스타일로 지정할 수도 있습니다.
        # bg_style = f"background-image: url('static/images/{tournament_data.get('bg_image_filename', 'card_bg_default.jpg')}');"
        # card_html = f"""<div class="custom-styled-card" style="{bg_style}"> ... </div>"""

        card_html = f"""
        <div class="custom-styled-card {bg_class}">
            <div class="card-content">
                <div>
                    <h3>{tournament_data.get('title', '제목 없음')}</h3>
                    <p>{tournament_data.get('short_description', '설명 없음')}</p>
                </div>
                <a href="/Tournaments?id={tournament_data.get('id', '')}" target="_self" class="card-button-link">자세히 보기</a>
            </div>
        </div>
        """
        # 현재 컬럼에 카드 추가
        cols[i % num_columns].markdown(card_html, unsafe_allow_html=True)
else:
    st.info("등록된 대회가 없습니다.")

st.markdown('</div>', unsafe_allow_html=True)

# 카드 스타일은 style.css의 .custom-card 클래스에 정의되어 있다고 가정
# 실제 데이터 로딩 (예시)
# all_tournaments = load_tournaments()
# if all_tournaments:
#     for t in all_tournaments[:3]: # 최근 3개 대회만 표시
#         st.markdown(f"""
#         <div class="custom-card">
#             <h3>{t.get('title', '제목 없음')}</h3>
#             <p>{t.get('date', '날짜 미정')}</p>
#             <a href="/Tournaments/{t.get('id', '')}" target="_self" class="card-link-button">상세 보기</a>
#         </div>
#         """, unsafe_allow_html=True)
# else:
#     st.info("등록된 대회가 없습니다.")

# 하드코딩된 카드 (테스트용)
st.markdown("""
<div class="custom-card">
    <h3>ADOFAI World Championship 2026</h3>
    <p>2024.12.9 - 2025.2.22</p>
    <!-- <a href="/Tournaments/awc2025" target="_self" class="card-link-button">상세 보기</a> -->
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="custom-card">
    <h3>ADOFAI World Championship 2025</h3>
    <p>2024.12.9 - 2025.2.22</p>
    <!-- <a href="/Tournaments/awc2025" target="_self" class="card-link-button">상세 보기</a> -->
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="custom-card">
    <h3>ADOFAI World Championship 2024</h3>
    <p>2023.12.8 - 2024.3.2</p>
    <!-- <a href="/Tournaments/awc2024" target="_self" class="card-link-button">상세 보기</a> -->
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="custom-card">
    <h3>ADOFAI World Championship 2023</h3>
    <p>2022.12.6 - 2023.2.15</p>
    <!-- <a href="/Tournaments/awc2023" target="_self" class="card-link-button">상세 보기</a> -->
</div>
""", unsafe_allow_html=True)


# --- 푸터 (선택 사항, 이전과 동일) ---
footer_html = """
<style>
    .footer {
        text-align: center;
        padding: 40px 20px;
        color: #888888;
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