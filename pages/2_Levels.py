# pages/2_Levels.py (상세 페이지 기능이 포함된 최종 버전)

import streamlit as st
import sys
import os

# --- 모듈 경로 설정 및 공통 컴포넌트 임포트 ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dataLoad import load_levels, load_tournaments
from ui_components import inject_local_css, create_top_nav_bar
from app import get_image_as_base64, SMALL_LOGO_IMAGE_FILE

# --- 페이지 기본 설정 및 스타일 적용 ---
st.set_page_config(page_title="레벨 목록", layout="wide", initial_sidebar_state="collapsed")
inject_local_css("style.css")

# --- 상단 네비게이션 바 표시 ---
small_logo_base64 = get_image_as_base64(SMALL_LOGO_IMAGE_FILE)
create_top_nav_bar(small_logo_base64, active_page="Levels")

# --- 데이터 로딩 ---
all_levels = load_levels()
all_tournaments = load_tournaments()
query_params = st.query_params
level_id = query_params.get("id")

# --- 라우팅: URL에 'id'가 있으면 상세 페이지, 없으면 목록 페이지 표시 ---
if level_id and any(lvl['id'] == level_id for lvl in all_levels):
    # --- 1. 레벨 상세 페이지 ---
    level = next((lvl for lvl in all_levels if lvl['id'] == level_id), None)
    
    if level:
        # 페이지 제목
        st.markdown(f"<h1 class='detail-title'>{level.get('title', '레벨 정보')}</h1>", unsafe_allow_html=True)
        
        # 메인 콘텐츠 (영상 + 정보 박스)
        main_cols = st.columns([2, 1], gap="large")
        
        with main_cols[0]: # 왼쪽: 유튜브 영상
            video_id = level.get('youtube_video_id')
            if video_id:
                st.markdown(f"""
                <div class="video-container">
                    <iframe src="https://www.youtube.com/embed/{video_id}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("이 레벨의 대표 영상이 없습니다.")
        
        with main_cols[1]: # 오른쪽: 정보 박스
            st.markdown(f"""
            <div class="level-info-box">
                <h3>레벨 정보</h3>
                <p><strong>아티스트:</strong> {level.get('artist', 'N/A')}</p>
                <p>{level.get('detail_artist', '')}</p>
                <p><strong>제작자:</strong> {level.get('creator', 'N/A')}</p>
                <p>({level.get('detail_creator', 'N/A')})</p>
                <p><strong>난이도:</strong> {level.get('difficulty_rating', 'N/A')}</p>
                <p><strong>BPM:</strong> {level.get('bpm', 'N/A')}</p>
                <p><strong>타일 수:</strong> {level.get('tiles', 'N/A')}</p>
                <a href="{level.get('download_url', '#')}" target="_blank" class="download-button">레벨 다운로드</a>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<hr class='custom-hr'>", unsafe_allow_html=True)
        if st.button("◀ 레벨 목록으로 돌아가기"):
            st.query_params.clear()
            st.rerun()
    else:
        st.error("요청한 레벨을 찾을 수 없습니다.")

else:
    # --- 2. 레벨 목록 페이지 (필터링 기능 포함) ---
    st.markdown("<h1 class='page-title'>🎶 레벨 목록</h1>", unsafe_allow_html=True)

    # 필터링 UI
    tournament_title_to_id = {t.get('title'): t.get('id') for t in all_tournaments}
    tournament_id_to_title = {v: k for k, v in tournament_title_to_id.items()}
    sorted_tournaments = sorted(all_tournaments, key=lambda t: t.get('year', '0000'), reverse=True)
    tournament_options = ["전체"] + [t.get('title') for t in sorted_tournaments]
    
    tournament_id_from_query = query_params.get("tournament_id")
    default_title = tournament_id_to_title.get(tournament_id_from_query)
    default_index = tournament_options.index(default_title) if default_title in tournament_options else 0

    filter_cols = st.columns([3, 8])
    with filter_cols[0]:
        selected_tournament_title = st.selectbox("대회 필터", options=tournament_options, index=default_index, key="tournament_filter")
    with filter_cols[1]:
        search_term = st.text_input("레벨, 아티스트, 제작자 검색", placeholder="검색어를 입력하세요...")

    # 필터링 로직
    display_levels = all_levels
    if selected_tournament_title != "전체":
        selected_tournament_id = tournament_title_to_id.get(selected_tournament_title)
        display_levels = [lvl for lvl in display_levels if lvl.get('tournament_id') == selected_tournament_id]
    if search_term:
        search_term_lower = search_term.lower()
        display_levels = [
            lvl for lvl in display_levels 
            if search_term_lower in lvl.get('title', '').lower() or \
               search_term_lower in lvl.get('artist', '').lower() or \
               search_term_lower in lvl.get('creator', '').lower()
        ]

    # 테이블 헤더
    st.markdown("""
    <div class="level-list-table">
        <div class="header-row">
            <div class="row-content">
                <div class="cell cell-title">제목</div>
                <div class="cell cell-artist">아티스트</div>
                <div class="cell cell-creator">제작자</div>
                <div class="cell cell-minititle">대회</div>
                <div class="cell cell-difficulty">난이도</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 테이블 내용
    if display_levels:
        for level in display_levels:
            st.markdown(f"""
            <a href="/Levels?id={level.get('id')}" target="_self" class="level-row">
                <div class="row-content">
                    <div class="cell cell-title">{level.get('title', 'N/A')}</div>
                    <div class="cell cell-artist">{level.get('artist', 'N/A')}</div>
                    <div class="cell cell-creator">{level.get('creator', 'N/A')}</div>
                    <div class="cell cell-tournament">{level.get('minititle', 'N/A')}</div>
                    <div class="cell cell-difficulty">{level.get('difficulty_rating', 'N/A')}</div>
                </div>
            </a>
            """, unsafe_allow_html=True)
    else:
        st.info("표시할 레벨이 없습니다.")