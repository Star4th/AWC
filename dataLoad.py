# dataLoad.py (최종 버전)

import streamlit as st
import yaml
from pathlib import Path

CONTENT_DIR = Path('content')

@st.cache_data
def load_tournaments():
    tournaments = []
    tournaments_path = CONTENT_DIR / 'tournaments'
    if not tournaments_path.exists(): return tournaments
    
    for filepath in tournaments_path.glob('*.yaml'):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            data['id'] = filepath.stem
            
            # YAML 파일에 bg_image_class가 명시적으로 있으면 그것을 사용하고,
            # 없으면 제목을 기반으로 동적으로 생성합니다. (더 안정적인 방식)
            if 'bg_image_class' not in data:
                year = data.get('year', '')
                if year:
                    data['bg_image_class'] = f'tournament_bg_{year}'
                else:
                    data['bg_image_class'] = ''
            
            tournaments.append(data)
            
    tournaments.sort(key=lambda t: t.get('year', '0000'), reverse=True)
    return tournaments

# dataLoad.py 파일에 추가

@st.cache_data
def load_levels():
    levels = []
    levels_path = CONTENT_DIR / 'levels'
    if not levels_path.exists(): return levels
    
    for filepath in levels_path.glob('*.yaml'):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            data['id'] = filepath.stem
            levels.append(data)
            
    # 레벨 이름순으로 정렬 (선택 사항)
    levels.sort(key=lambda l: l.get('title', ''))
    return levels