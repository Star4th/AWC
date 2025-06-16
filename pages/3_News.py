import streamlit as st
import sys
import os

# 현재 파일의 디렉토리(pages)의 부모 디렉토리(루트)를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dataLoad import load_news # 데이터 로딩 함수 임포트 (STATIC_DIR은 뉴스에서 직접 사용 안 할 수 있음)

st.set_page_config(page_title="최신 뉴스", layout="wide")
st.title("📰 최신 뉴스")

# Streamlit 1.31+ 에서는 st.query_params 사용
# 이전 버전에서는 st.experimental_get_query_params()
try:
    current_query_params = st.query_params
    news_id_from_query = current_query_params.get("id")
except AttributeError:
    current_query_params_dict = st.experimental_get_query_params()
    news_id_from_query = current_query_params_dict.get("id", [None])[0]

try:
    all_news_items = load_news()
except ImportError as e:
    st.error(f"데이터 로딩 모듈을 가져오는 중 오류 발생: {e}")
    st.error("dataLoad.py 파일이 app.py와 동일한 디렉토리에 있는지 확인하세요.")
    all_news_items = []
except Exception as e:
    st.error(f"뉴스 데이터 로딩 중 예상치 못한 오류 발생: {e}")
    all_news_items = []

if news_id_from_query and any(n['id'] == news_id_from_query for n in all_news_items):
    # --- 상세 페이지 표시 ---
    news_item = next((n for n in all_news_items if n['id'] == news_id_from_query), None)

    if news_item:
        st.header(news_item.get('title', '제목 없음'))
        st.caption(f"게시일: {news_item.get('date', '날짜 미정')} | 작성자: {news_item.get('author', 'N/A')}")

        if news_item.get('tags'):
            tags_str = ", ".join([f"`{tag}`" for tag in news_item.get('tags', [])])
            st.markdown(f"**태그:** {tags_str}")

        st.markdown("---")

        if 'content_html' in news_item:
            st.markdown(news_item['content_html'], unsafe_allow_html=True)
        else:
            st.info("뉴스 내용이 없습니다.")

        if st.button("◀ 뉴스 목록으로 돌아가기"):
            try:
                st.query_params.clear()
            except AttributeError:
                st.experimental_set_query_params()
            st.rerun()
    else:
        st.error("선택한 ID의 뉴스 정보를 찾을 수 없습니다.")
        if st.button("◀ 뉴스 목록으로 돌아가기"):
            try:
                st.query_params.clear()
            except AttributeError:
                st.experimental_set_query_params()
            st.rerun()
else:
    # --- 목록 페이지 표시 ---
    st.subheader("뉴스 목록")
    search_term = st.text_input("뉴스 검색 (제목 또는 태그)", key="news_search")

    if not all_news_items:
        st.info("등록된 뉴스가 없습니다.")
    else:
        filtered_news = []
        if search_term:
            search_term_lower = search_term.lower()
            for item in all_news_items:
                title_match = search_term_lower in item.get('title', '').lower()
                tags_match = False
                if item.get('tags'):
                    tags_match = any(search_term_lower in tag.lower() for tag in item.get('tags', []))
                if title_match or tags_match:
                    filtered_news.append(item)
        else:
            filtered_news = all_news_items


        if not filtered_news:
            st.info("검색 결과가 없습니다.")
        else:
            for item in filtered_news:
                with st.container(border=True): # Streamlit 1.29+
                    st.markdown(f"### {item.get('title', '제목 없음')}")
                    st.caption(f"게시일: {item.get('date', '날짜 미정')} | 작성자: {item.get('author', 'N/A')}")
                    if item.get('tags'):
                        tags_str = ", ".join([f"`{tag}`" for tag in item.get('tags', [])])
                        st.markdown(f"태그: {tags_str}")

                    # 뉴스 내용 일부 미리보기 (예: 첫 200자)
                    if 'content_html' in item:
                        # HTML 태그 제거 후 텍스트만 추출 (간단한 방식, 완벽하지 않음)
                        import re
                        plain_text_content = re.sub('<[^<]+?>', '', item['content_html'])
                        preview_text = (plain_text_content[:200] + '...') if len(plain_text_content) > 200 else plain_text_content
                        st.markdown(preview_text)

                    if st.button("자세히 보기", key=f"detail_btn_{item['id']}", use_container_width=True):
                        try:
                            st.query_params["id"] = item['id']
                        except AttributeError:
                            st.experimental_set_query_params(id=item['id'])
                        st.rerun()
                    # st.markdown("---") # 컨테이너 사용 시 불필요