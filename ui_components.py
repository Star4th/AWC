# ui_components.py (최종 완성 버전)

import streamlit as st
import base64

def inject_local_css(file_name):
    """로컬 CSS 파일을 읽어와 앱에 주입하는 함수"""
    try:
        with open(file_name, encoding='utf-8') as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"CSS 파일을 찾을 수 없습니다: {file_name}")

def get_image_as_base64(file_path):
    """이미지 파일을 Base64 문자열로 인코딩하는 함수"""
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

def create_top_nav_bar(logo_base64_data, active_page=""):
    """상단 네비게이션 바 HTML을 생성하는 함수"""
    logo_html = f'<a href="/" target="_self"><img src="data:image/png;base64,{logo_base64_data}" alt="AWC 홈"></a>' if logo_base64_data else '<a href="/" target="_self" style="color:white; text-decoration:none; font-weight:bold;">AWC</a>'
    
    tournaments_class = "active" if active_page == "Tournaments" else ""
    levels_class = "active" if active_page == "Levels" else "" # 'Levels' 추가

    nav_bar_html = f"""
    <div class="top-nav-container">
        <div class="nav-logo">{logo_html}</div>
        <div class="nav-menu-items">
            <a href="/Tournaments" target="_self" class="{tournaments_class}">대회 정보</a>
            <a href="/Levels" target="_self" class="{levels_class}">레벨 목록</a>
        </div>
    </div>
    """
    st.markdown(nav_bar_html, unsafe_allow_html=True)

def create_tournament_card(tournament_data, is_highlighted=False):
    """대회 카드 HTML을 생성하는 헬퍼 함수"""
    bg_class = tournament_data.get('bg_image_class', '')
    highlight_class = "highlighted-card" if is_highlighted else ""
    title = tournament_data.get('title')

    card_html = f"""
    <a href="/Tournaments?id={tournament_data.get('id', '')}" target="_self" class="card-link-wrapper">
        <div class="custom-styled-card {bg_class} {highlight_class}">
            <div class="card-content">
                <h3>{title}</h3>
            </div>
        </div>
    </a>
    """
    return card_html