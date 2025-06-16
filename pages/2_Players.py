import streamlit as st
import sys
import os

# 현재 파일의 디렉토리(pages)의 부모 디렉토리(루트)를 sys.path에 추가
# 이렇게 하면 루트 디렉토리에 있는 dataLoad.py를 임포트할 수 있습니다.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dataLoad import load_players, STATIC_DIR # 데이터 로딩 함수 및 경로 임포트

st.set_page_config(page_title="선수 정보", layout="wide")
st.title("🧑‍💻 선수 정보")

# Streamlit 1.31+ 에서는 st.query_params 사용
# 이전 버전에서는 st.experimental_get_query_params()
try:
    current_query_params = st.query_params
    player_id_from_query = current_query_params.get("id")
except AttributeError:
    current_query_params_dict = st.experimental_get_query_params()
    player_id_from_query = current_query_params_dict.get("id", [None])[0]

try:
    all_players = load_players()
except ImportError as e:
    st.error(f"데이터 로딩 모듈을 가져오는 중 오류 발생: {e}")
    st.error("dataLoad.py 파일이 app.py와 동일한 디렉토리에 있는지 확인하세요.")
    all_players = []
except Exception as e:
    st.error(f"선수 데이터 로딩 중 예상치 못한 오류 발생: {e}")
    all_players = []

if player_id_from_query and any(p['id'] == player_id_from_query for p in all_players):
    # --- 상세 페이지 표시 ---
    player = next((p for p in all_players if p['id'] == player_id_from_query), None)

    if player:
        st.header(player.get('nickname', '이름 없음'))

        cols = st.columns([1, 3]) # 프로필 이미지와 정보를 위한 컬럼

        with cols[0]: # 왼쪽 컬럼 (프로필 이미지)
            if 'profile_image' in player and player['profile_image']:
                image_filename = player['profile_image']
                image_path = STATIC_DIR / 'images' / image_filename
                # 실제 이미지 파일이 있는지 확인하는 로직 (예시)
                # if image_path.exists():
                #     st.image(str(image_path), width=200) # 이미지 크기 조절 가능
                # else:
                #     st.caption(f"이미지 없음: {image_filename}")
                # 임시로 텍스트만 표시 (실제 이미지 파일이 static/images에 있어야 함)
                st.image(f"https://via.placeholder.com/200x200.png?text={player.get('nickname', 'Player')}", caption=player.get('nickname'), width=200)
                # st.caption(f"이미지 경로: static/images/{image_filename} (실제 파일 필요)")
            else:
                st.image("https://via.placeholder.com/200x200.png?text=No+Image", caption="프로필 이미지 없음", width=200)


        with cols[1]: # 오른쪽 컬럼 (선수 정보)
            if player.get('real_name'):
                st.markdown(f"**본명:** {player.get('real_name')}")
            if player.get('country'):
                st.markdown(f"**국적:** {player.get('country')}")
            if player.get('team'):
                st.markdown(f"**소속팀:** {player.get('team')}")

            social_links = []
            if player.get('twitter'):
                social_links.append(f"[Twitter](https://twitter.com/{player['twitter']})")
            if player.get('twitch'):
                social_links.append(f"[Twitch](https://twitch.tv/{player['twitch']})")
            if player.get('youtube'):
                social_links.append(f"[YouTube](https://youtube.com/@{player['youtube']})") # YouTube 핸들 형식

            if social_links:
                st.markdown("**소셜 미디어:** " + " | ".join(social_links))

        st.markdown("---")
        if 'content_html' in player:
            st.markdown(player['content_html'], unsafe_allow_html=True)
        else:
            st.info("선수 소개 내용이 없습니다.")

        if st.button("◀ 선수 목록으로 돌아가기"):
            try:
                st.query_params.clear()
            except AttributeError:
                st.experimental_set_query_params()
            st.rerun()
    else:
        st.error("선택한 ID의 선수 정보를 찾을 수 없습니다.")
        if st.button("◀ 선수 목록으로 돌아가기"):
            try:
                st.query_params.clear()
            except AttributeError:
                st.experimental_set_query_params()
            st.rerun()
else:
    # --- 목록 페이지 표시 ---
    st.subheader("선수 목록")
    search_term = st.text_input("선수 검색 (닉네임)", key="player_search")

    if not all_players:
        st.info("등록된 선수가 없습니다.")
    else:
        filtered_players = [
            p for p in all_players
            if search_term.lower() in p.get('nickname', '').lower() or \
               search_term.lower() in p.get('real_name', '').lower()
        ]

        if not filtered_players:
            st.info("검색 결과가 없습니다.")
        else:
            # 선수 목록을 카드로 표시 (예: 3열 그리드)
            num_columns = 3
            cols = st.columns(num_columns)
            for index, p in enumerate(filtered_players):
                col_index = index % num_columns
                with cols[col_index]:
                    with st.container(border=True): # Streamlit 1.29+ 에서 border=True 사용 가능
                        if 'profile_image' in p and p['profile_image']:
                            # 목록에서는 작은 이미지 또는 플레이스홀더 사용
                            # image_path = STATIC_DIR / 'images' / p['profile_image']
                            # if image_path.exists():
                            #     st.image(str(image_path), use_column_width='auto')
                            # else:
                            #     st.image("https://via.placeholder.com/150x150.png?text=No+Image", use_column_width='auto')
                            st.image(f"https://via.placeholder.com/150x150.png?text={p.get('nickname','P')}", use_container_width='auto')
                        else:
                            st.image("https://via.placeholder.com/150x150.png?text=No+Image", use_container_width='auto')

                        st.markdown(f"#### {p.get('nickname', '이름 없음')}")
                        if p.get('country'):
                            st.caption(f"국적: {p.get('country')}")
                        if p.get('team'):
                            st.caption(f"팀: {p.get('team')}")

                        if st.button("자세히 보기", key=f"detail_btn_{p['id']}", use_container_width=True):
                            try:
                                st.query_params["id"] = p['id']
                            except AttributeError:
                                st.experimental_set_query_params(id=p['id'])
                            st.rerun()
                        # st.markdown("---") # 카드 간 구분을 위해 컨테이너 사용 시 불필요할 수 있음