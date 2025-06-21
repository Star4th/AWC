# app.py (최종 리팩토링 버전)

import streamlit as st
from pathlib import Path
from ui_components import inject_local_css, create_top_nav_bar, create_tournament_card, get_image_as_base64
from dataLoad import load_tournaments

# --- 전역 변수 및 경로 설정 ---
LOGO_IMAGE_FILE = Path(__file__).parent / "static" / "images" / "awc_logo.png"
SMALL_LOGO_IMAGE_FILE = Path(__file__).parent / "static" / "images" / "awc_logo_small.png"

# --- 메인 앱 실행 로직 ---
if __name__ == "__main__":
    st.set_page_config(page_title="AWC 정보 허브", layout="wide", initial_sidebar_state="collapsed")
    inject_local_css("style.css")

    # --- 상단 네비게이션 바 ---
    small_logo_base64 = get_image_as_base64(SMALL_LOGO_IMAGE_FILE)
    create_top_nav_bar(small_logo_base64, active_page="")

    # --- 중앙 로고 ---
    main_logo_base64 = get_image_as_base64(LOGO_IMAGE_FILE)
    if main_logo_base64:
        st.markdown(f'<div class="main-logo-container"><img src="data:image/png;base64,{main_logo_base64}" alt="AWC 로고"></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="text-align: center; padding: 60px 20px 40px 20px;"><h1 style="font-size: 3em;">AWC 정보 허브</h1></div>', unsafe_allow_html=True)

    # --- 메인 콘텐츠 (대회 카드 목록) ---
    loaded_tournaments = load_tournaments()

    if loaded_tournaments:
        # 첫 번째 카드 (하이라이트)
        st.markdown(create_tournament_card(loaded_tournaments[0], is_highlighted=True), unsafe_allow_html=True)

        # 나머지 카드들
        remaining_tournaments = loaded_tournaments[1:]
        if remaining_tournaments:
            num_columns = 3
            cols = st.columns(num_columns)
            for i, tournament in enumerate(remaining_tournaments):
                cols[i % num_columns].markdown(create_tournament_card(tournament), unsafe_allow_html=True)
    else:
        st.info("등록된 대회가 없습니다.")

    # --- 푸터 ---
    st.markdown('<div class="footer">© 에셋 저작권은 AWC, ADOFAI.gg에 있으며, 해당 사이트는 ADOFAI.gg에서 운영하지 않습니다.</div>', unsafe_allow_html=True)