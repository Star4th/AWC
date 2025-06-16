# 예시: utils.py 또는 각 페이지 파일 상단에 정의
import streamlit as st
import yaml
import markdown
import os
from pathlib import Path

CONTENT_DIR = Path('content')
STATIC_DIR = Path('static') # 이미지 경로 등에 사용

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