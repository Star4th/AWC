# 1_Tournaments.py (최종 리팩토링 버전)

import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dataLoad import load_tournaments
from ui_components import inject_local_css, create_top_nav_bar, create_tournament_card, get_image_as_base64
from app import SMALL_LOGO_IMAGE_FILE # 경로 변수는 app.py에서 가져와도 괜찮음

st.set_page_config(page_title="대회 정보", layout="wide", initial_sidebar_state="collapsed")
inject_local_css("style.css")

small_logo_base64 = get_image_as_base64(SMALL_LOGO_IMAGE_FILE)
create_top_nav_bar(small_logo_base64, active_page="Tournaments")

all_tournaments = load_tournaments()
tournament_id = st.query_params.get("id")

if tournament_id and any(t['id'] == tournament_id for t in all_tournaments):
    # --- 1. 상세 페이지 ---
    tournament = next((t for t in all_tournaments if t['id'] == tournament_id), None)
    
    if tournament:
        
        # 1-1. 유튜브 영상 임베드
        video_id = tournament.get('youtube_video_id')
        if video_id:
            #st.markdown("<h2 class='section-title'>대표 영상</h2>", unsafe_allow_html=True)
            video_cols = st.columns([1, 3, 1])
            with video_cols[1]:
                st.markdown(f"""
                <div class="video-container">
                    <iframe src="https://www.youtube.com/embed/{video_id}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
                </div>
                """, unsafe_allow_html=True)

        # 1-2. 대회 제목
        st.markdown(f"<h1 class='detail-title'>{tournament.get('title', '제목 없음')}</h1>", unsafe_allow_html=True)
        
        # 1-3. 바로가기 (위치 변경)
        links = tournament.get('shortcut_links', [])
        if links:
            #st.markdown("<h2 class='section-title'></h2>", unsafe_allow_html=True)
            link_cols = st.columns(len(links) if len(links) <= 5 else 5)
            for i, link in enumerate(links):
                with link_cols[i % 5]:
                    st.markdown(f'<a href="{link.get("url", "#")}" target="_blank" class="detail-button-link">{link.get("icon", "")} {link.get("label", "링크")}</a>', unsafe_allow_html=True)
        
        # 1-4. 레벨 정렬
        st.markdown(f'<a href="/Levels?tournament_id={tournament.get("id")}" target="_self" class="detail-button-link">📜 오리지널 레벨 목록 보기</a>', unsafe_allow_html=True)

        # 1-5. 목록으로 돌아가기 버튼
        st.markdown("<hr class='custom-hr'>", unsafe_allow_html=True)
        if st.button("◀ 대회 목록으로 돌아가기"):
            st.query_params.clear()
            st.rerun()
    else:
        st.error("선택한 대회를 찾을 수 없습니다.")
        if st.button("◀ 대회 목록으로 돌아가기"):
            st.query_params.clear()
            st.rerun()

else:
    # --- 목록 페이지 (개선된 카드 디자인 적용) ---
    st.markdown("""
    <div class="text-center">
        <h1 class='page-title'>🏆 대회 정보</h1>
        <p>자세히 보고 싶은 대회를 클릭하세요.</p>
    </div>
    """, unsafe_allow_html=True)
    # st.markdown("<br>", unsafe_allow_html=True)

    if all_tournaments:
        num_columns = 4
        cols = st.columns(num_columns)
        for i, tournament in enumerate(all_tournaments):
            # 카드 생성 함수 사용
            cols[i % num_columns].markdown(create_tournament_card(tournament), unsafe_allow_html=True)
    else:
        st.info("등록된 대회가 없습니다.")