# --- START OF FILE 1_Tournaments.py ---

import streamlit as st
import sys
import os

# 현재 파일의 디렉토리(pages)의 부모 디렉토리(루트)를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dataLoad import load_tournaments, STATIC_DIR

st.set_page_config(page_title="대회 정보", layout="wide")
st.title("🏆 대회 정보")

# --- st.query_params 사용으로 통일 ---
# URL query parameter를 사용하여 상세 페이지를 표시할지 결정
# st.query_params는 딕셔너리처럼 동작하는 속성입니다.
current_query_params = st.query_params
tournament_id_from_query = current_query_params.get("id") # .get("id")는 값이 없으면 None을 반환

try:
    all_tournaments = load_tournaments()
except ImportError as e:
    st.error(f"데이터 로딩 모듈을 가져오는 중 오류 발생: {e}")
    st.error("dataLoad.py 파일이 app.py와 동일한 디렉토리에 있는지, 필요한 라이브러리(PyYAML, Markdown)가 설치되었는지 확인하세요.")
    all_tournaments = []
except Exception as e:
    st.error(f"데이터 로딩 중 예상치 못한 오류 발생: {e}")
    all_tournaments = []


if tournament_id_from_query and any(t['id'] == tournament_id_from_query for t in all_tournaments):
    # --- 상세 페이지 표시 ---
    tournament = next((t for t in all_tournaments if t['id'] == tournament_id_from_query), None)
    if tournament:
        st.header(tournament['title'])
        st.markdown(f"**날짜:** {tournament.get('date', '미정')}")
        st.markdown(f"**주최:** {tournament.get('organizer', 'N/A')}")
        st.markdown(f"**상금:** {tournament.get('prize', 'N/A')}")
        st.markdown(f"**우승자:** {tournament.get('winner', '미정')}")
        st.markdown(f"**상태:** {tournament.get('status', 'N/A')}")

        if 'description' in tournament:
            st.markdown("---")
            st.markdown(tournament['description'], unsafe_allow_html=True)

        if 'bracket_image' in tournament and tournament['bracket_image']:
            image_filename = tournament['bracket_image']
            # STATIC_DIR이 Path 객체이므로 올바르게 경로를 결합합니다.
            # image_path = STATIC_DIR / 'images' / image_filename
            # if image_path.exists():
            #     st.image(str(image_path), caption="대진표")
            # else:
            #     st.warning(f"대진표 이미지를 찾을 수 없습니다: {image_path}")
            st.markdown(f"**대진표 이미지:** {image_filename} (이미지 표시는 경로 설정 및 파일 필요)")
            # 예시 플레이스홀더 이미지
            st.image(f"https://via.placeholder.com/600x400.png?text=Bracket+{image_filename.split('.')[0]}", caption="대진표 (예시)")


        if tournament.get('vod_links'):
            st.subheader("관련 영상")
            for vod in tournament['vod_links']:
                st.markdown(f"- [{vod.get('title', '제목 없음')}]({vod.get('url', '#')})")

        if st.button("◀ 대회 목록으로 돌아가기"):
            # st.query_params를 사용하여 query params 초기화
            st.query_params.clear()
            st.rerun() # st.experimental_rerun() 대신 st.rerun() 사용 권장
    else:
        st.error("선택한 ID의 대회 정보를 찾을 수 없습니다.")
        if st.button("◀ 대회 목록으로 돌아가기"):
            st.query_params.clear()
            st.rerun()

else:
    # --- 목록 페이지 표시 ---
    st.subheader("대회 목록")
    search_term = st.text_input("대회 검색", key="tournament_search")
    
    filtered_tournaments = []
    if all_tournaments: # all_tournaments가 비어있지 않을 때만 필터링
        filtered_tournaments = [
            t for t in all_tournaments 
            if search_term.lower() in t.get('title', '').lower()
        ]

    if not filtered_tournaments and not all_tournaments: # 등록된 대회가 아예 없는 경우
        st.info("등록된 대회가 없습니다.")
    elif not filtered_tournaments and all_tournaments : # 등록된 대회는 있지만 검색 결과가 없는 경우
        st.info("검색 결과가 없습니다.")
    else:
        for t in filtered_tournaments:
            with st.container(border=True): # Streamlit 1.29+
                st.markdown(f"### {t.get('title', '제목 없음')}")
                st.caption(f"날짜: {t.get('date', '미정')} | 상태: {t.get('status', 'N/A')}")
                # 상세 페이지로 이동하는 링크 (또는 버튼 후 query_params 설정)
                if st.button("자세히 보기", key=f"detail_btn_{t['id']}", use_container_width=True):
                    # st.query_params를 사용하여 query params 설정
                    st.query_params["id"] = t['id']
                    st.rerun()
                # st.markdown("---") # 컨테이너 사용 시 불필요할 수 있음

# --- END OF FILE 1_Tournaments.py ---