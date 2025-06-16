import streamlit as st
from dataLoad import load_tournaments, load_news # 데이터 로딩 함수 임포트

# --- 데이터 로딩 함수 (위의 예시 코드) ---
import yaml
import markdown
import os
import base64
from pathlib import Path


CONTENT_DIR = Path('content')
STATIC_DIR = Path('static') # 이미지 경로 등에 사용

#base64
def get_image_as_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None # 오류 대신 None 반환

# local css
def local_css(file_name):
    with open(file_name, encoding='utf-8') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Streamlit의 캐싱 기능을 사용하면 데이터 로딩 속도를 높일 수 있습니다.
@st.cache_data # 데이터가 변경되지 않으면 캐시된 결과를 사용
def load_tournaments():
    tournaments = []
    tournaments_path = CONTENT_DIR / 'tournaments'
    if not tournaments_path.exists(): return tournaments
    for filepath in tournaments_path.glob('*.yaml'):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            data['id'] = filepath.stem # 파일명 (확장자 제외)을 ID로 사용
            tournaments.append(data)
    tournaments.sort(key=lambda t: t.get('date', '0000-00-00'), reverse=True)
    return tournaments

@st.cache_data
def load_players():
    players = []
    players_path = CONTENT_DIR / 'players'
    if not players_path.exists(): return players
    md_parser = markdown.Markdown(extensions=['meta']) # 'meta'는 frontmatter와 유사

    for filepath in players_path.glob('*.md'):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            html_content = md_parser.convert(content)
            # frontmatter (meta) 데이터 접근
            # markdown 라이브러리의 'meta' 확장은 frontmatter를 md_parser.Meta 로 저장
            # PyYAML을 사용해 frontmatter를 파싱하는 것이 더 일반적일 수 있음
            # 여기서는 간단히 YAML frontmatter를 가정하고 수동 파싱 예시
            try:
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    meta_data = yaml.safe_load(parts[1])
                    actual_content_md = parts[2].strip()
                    html_content = markdown.markdown(actual_content_md)
                else: # frontmatter 없는 경우
                    meta_data = {}
                    html_content = markdown.markdown(content)

            except Exception as e:
                print(f"Error parsing MD frontmatter for {filepath}: {e}")
                meta_data = {}
                html_content = markdown.markdown(content)


            data = meta_data
            data['id'] = filepath.stem
            data['content_html'] = html_content
            players.append(data)
    players.sort(key=lambda p: p.get('nickname', ''))
    return players

# load_news() 함수도 유사하게 작성 (날짜 필드 기준으로 정렬)
@st.cache_data
def load_news():
    news_items = []
    news_path = CONTENT_DIR / 'news'
    if not news_path.exists():
        # st.warning(f"'content/news' 디렉토리를 찾을 수 없습니다.") # 디버깅용
        return news_items

    for filepath in news_path.glob('*.md'): # 뉴스 파일 확장자가 .md라고 가정
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Frontmatter 파싱 (load_players와 동일한 로직 사용)
            try:
                parts = content.split('---', 2)
                if len(parts) >= 3 and parts[0].strip() == '': # 첫번째 --- 앞에 아무것도 없어야 함
                    meta_data = yaml.safe_load(parts[1])
                    if meta_data is None: meta_data = {} # YAML 파싱 결과가 None일 경우 빈 딕셔너리로 처리
                    actual_content_md = parts[2].strip()
                else: # frontmatter 없는 경우 또는 형식이 다른 경우
                    meta_data = {}
                    actual_content_md = content.strip()
                
                html_content = markdown.markdown(actual_content_md)

            except yaml.YAMLError as e:
                # st.warning(f"YAML frontmatter 파싱 오류 ({filepath}): {e}. 메타데이터 없이 진행합니다.")
                print(f"YAML frontmatter parsing error for news {filepath}: {e}") # 콘솔에 오류 출력
                meta_data = {} # 오류 발생 시 메타데이터는 비움
                html_content = markdown.markdown(content) # 원본 전체를 마크다운으로 처리
            except Exception as e:
                # st.error(f"MD 파일 처리 중 오류 ({filepath}): {e}")
                print(f"Error processing news MD file {filepath}: {e}") # 콘솔에 오류 출력
                meta_data = {}
                html_content = markdown.markdown(content)

            # 필수 필드가 없는 경우를 대비하여 .get() 사용 및 기본값 설정
            data = meta_data
            data['id'] = filepath.stem
            data['content_html'] = html_content # 뉴스 본문도 HTML로 변환
            # title, date, author 등은 meta_data에서 가져오므로, pages/3_📰_News.py에서 .get()으로 안전하게 접근
            news_items.append(data)
        except Exception as e:
            st.error(f"{filepath} 뉴스 파일 로딩 중 오류: {e}")
            print(f"Error loading news file {filepath}: {e}") # 콘솔에 오류 출력

    # 날짜 필드('date')를 기준으로 최신순으로 정렬
    # 날짜 형식이 'YYYY-MM-DD' 등으로 일관되어야 올바르게 정렬됩니다.
    # 날짜가 없는 경우를 대비해 기본값 '0000-00-00' 사용
    news_items.sort(key=lambda item: str(item.get('date', '0000-00-00')), reverse=True)
    return news_items

# ----------------------------------------

st.set_page_config(page_title="AWC 정보 허브 - 메인", layout="wide", initial_sidebar_state="collapsed")

local_css("style.css") #style.css 불러오기

#---------custom above bar-----------

# above nevigation bar

# 멀티페이지 앱의 경우, 각 페이지 파일명을 기반으로 링크 생성 가능
# pages 폴더 구조:
# pages/
#   1_🏆_Tournaments.py
#   2_🧑‍💻_Players.py

# 로고 이미지 경로 (static 폴더에 있다고 가정)
LOGO_IMAGE_PATH = "static/images/awc_logo.png" # 실제 경로로 수정

# 로고 이미지 경로2
LOGO_IMAGE_FILE = Path(__file__).parent / "static" / "images" / "awc_logo.png"

# 로고 이미지 표시 (st.image 사용 또는 HTML img 태그)
if Path(LOGO_IMAGE_PATH).exists():
    st.sidebar.image(LOGO_IMAGE_PATH, width=150) # 사이드바에 로고
else:
    st.sidebar.write("[로고]")

# 상단 메뉴 HTML (st.markdown 사용)
# 멀티페이지 링크는 Streamlit이 자동으로 생성하는 URL 패턴을 따라야 합니다.
# 예: /Tournaments, /Players (파일명에서 숫자와 이모티콘, 확장자 제외)
# Streamlit 1.28+ 에서는 st.page_link() 사용 가능
menu_html = """
<style>
    .top-nav {
        background-color: #1E1E2E; /* 배경색 */
        padding: 10px 20px;
        display: flex;
        align-items: center;
        justify-content: space-between; /* 로고와 메뉴 분리 */
        border-bottom: 1px solid #4A4A65;
    }
    .top-nav .logo a {
        color: white;
        text-decoration: none;
        font-size: 1.5em;
        font-weight: bold;
    }
    .top-nav .logo img { /* 로고 이미지를 사용한다면 */
        height: 40px;
        margin-right: 10px;
        vertical-align: middle;
    }
    .top-nav .menu-items a {
        color: #F0F0F0;
        text-decoration: none;
        margin-left: 20px;
        font-size: 1em;
    }
    .top-nav .menu-items a:hover {
        color: #7A5FFF; /* 강조색 */
    }
</style>

<div class="top-nav">
    <div class="logo">
        <!-- <img src="LOGO_IMAGE_PATH" alt="AWC Logo"> --> <!-- 배포시 주의 -->
        <a href="/" target="_self"><img src="LOGO_IMAGE_PATH" alt="AWC Logo"></a> <!-- 메인 페이지 링크 -->
    </div>
    <div class="menu-items">
        <a href="/Tournaments" target="_self">대회 정보</a>
        <a href="/Players" target="_self">선수 정보</a>
        <a href="/News" target="_self">뉴스/공지</a>
        <!-- 추가 메뉴 항목들 -->
    </div>
</div>
<br> <!-- 메뉴바와 콘텐츠 사이에 약간의 간격 -->
"""
#st.image(LOGO_IMAGE_PATH, width = 150)

logo_base64 = get_image_as_base64(LOGO_IMAGE_FILE)
# --- 클릭 가능한 로고 이미지 표시 ---
if logo_base64:
    # 링크 목적지 URL (예: 메인 페이지 "/")
    link_url = "/"
    # 이미지 너비 설정
    image_width = 150

    # HTML <a> 태그로 이미지를 감싸서 링크 생성
    clickable_logo_html = f"""
    <a href="{link_url}" target="_self">
        <img src="data:image/png;base64,{logo_base64}" alt="AWC 로고 - 메인으로 가기" width="{image_width}px">
    </a>
    """
    st.markdown(clickable_logo_html, unsafe_allow_html=True)
else:
    st.warning("로고 이미지를 불러올 수 없습니다.")



st.markdown(menu_html, unsafe_allow_html=True)

# --- 페이지 콘텐츠 ---
#st.header("페이지 제목")
#st.write("이곳에 페이지 내용이 들어갑니다.")

#------------custom abovebar end------------


#st.title("🎮 AWC 정보 허브")

#css 적용 버전
#st.button("스타일 적용된 버튼")
st.markdown("""
<div class="custom-card">
    <h3>ADOFAI World Championship 2025</h3>
    <p>2024.12.9 - 2025.2.22</p>
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


#st.markdown("A Dance of Fire and Ice 월드 챔피언십 팬들을 위한 중앙 정보 허브입니다.")
#st.sidebar.success("위에서 페이지를 선택하세요.") # 사이드바는 자동으로 생성됨

# 데이터 로드
#tournaments = load_tournaments()
# news = load_news()

#st.header("최신 대회")
#if tournaments:
#    for t in tournaments[:3]: # 최근 3개 대회
        # st.subheader(t['title'])
        # st.caption(f"날짜: {t.get('date', '날짜 미정')} | 상태: {t.get('status', 'N/A')}")
        # st.markdown(f"[상세 보기](Tournaments?id={t['id']})") # query_params로 ID 전달
        # 또는
#        with st.container(): # 카드처럼 보이게 하기 위한 컨테이너
#            st.subheader(t['title'])
#            st.write(f"**날짜:** {t.get('date', '미정')}")
#            st.write(f"**상태:** {t.get('status', 'N/A')}")
            # 상세 페이지로 직접 연결하는 버튼은 각 페이지 파일에서 처리하는 것이 더 깔끔할 수 있음
            # 여기서는 간단히 정보만 표시
#            st.markdown("---")
#else:
#    st.info("등록된 대회가 없습니다.")

# 최신 뉴스 표시 (유사하게)
# ...
