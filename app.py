import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(layout="wide", page_title="대한싸이로 재고현황판 v2")

# 2. 스타일 설정 (기존 유지)
st.markdown("""
<style>
    .dashboard-outer { display: flex; justify-content: center; padding-top: 60px; background-color: white; }
    .grid-container {
        position: relative; display: grid;
        grid-template-columns: repeat(7, 100px); grid-template-rows: repeat(2, 100px);
        border: 1.5px solid #333; background-color: white;
    }
    .grid-cell {
        border: 1.5px solid #333; display: flex; flex-direction: column;
        justify-content: center; align-items: center; position: relative;
    }
    .circle-unit {
        position: absolute; width: 90px; height: 90px;
        border: 2px solid #333; border-radius: 50%; background-color: white;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        z-index: 20; transform: translate(-50%, -50%);
    }
    .blue-grain { color: #0000FF; font-weight: bold; font-size: 14px; }
    .brown-grain { color: #8B4513; font-weight: bold; font-size: 14px; }
    .stock-val { color: black; font-weight: bold; font-size: 13px; margin: 1px 0; }
    .loc-id { color: #90EE90; font-size: 10px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 데이터 서식 함수
def get_style(grain, amt):
    if not grain or not str(grain).upper().startswith('W'):
        return {"style": "", "grain": "-", "amt": "0"}
    blue = ['WASW', 'WASWP', 'WUSH', 'WUSL9.0']
    style = "blue-grain" if str(grain).upper() in blue else "brown-grain"
    # 숫자 포맷팅
    try:
        formatted_amt = "{:,.0f}".format(float(str(amt).replace(',', '')))
    except:
        formatted_amt = amt
    return {"style": style, "grain": grain, "amt": formatted_amt}

# 3. 구글 시트 연결
# 시트 주소: https://docs.google.com/spreadsheets/d/1o_RIw7DWvMrz9Y1z1akXlgJY6LiW46QT7fHxEqpymSs/edit
conn = st.connection("gsheets", type=GSheetsConnection)

# 4. 상단 컨트롤 바
col_title, col_date = st.columns([2, 1])
with col_title:
    st.markdown("<h1 style='text-decoration: underline;'>일 일 재 고 현 황 표</h1>", unsafe_allow_html=True)

# 시트에서 데이터 읽기
df = conn.read(spreadsheet="https://docs.google.com/spreadsheets/d/1o_RIw7DWvMrz9Y1z1akXlgJY6LiW46QT7fHxEqpymSs/edit")

# 만약 '날짜' 컬럼이 없다면 오늘 날짜로 임시 생성 (히스토리 기능을 위해)
if '날짜' not in df.columns:
    df['날짜'] = datetime.now().strftime("%Y-%m-%d")

with col_date:
    unique_dates = df['날짜'].unique().tolist()
    selected_date = st.selectbox("📅 조회할 날짜 선택", unique_dates[::-1]) # 최신순

# 선택된 날짜 데이터 필터링
filtered_df = df[df['날짜'] == selected_date]
inv = filtered_df.set_index('장치장').to_dict('index')

# 5. 대시보드 출력
html = '<div class="dashboard-outer"><div class="grid-container">'

# 네모칸 (A201~A207, A401~A407)
for r_idx, r_code in enumerate([2, 4]):
    for c in range(1, 8):
        loc = f"A{r_code}0{c}"
        cell_data = inv.get(loc, {"곡종": "-", "재고량": "0"})
        d = get_style(cell_data['곡종'], cell_data['재고량'])
        html += f'<div class="grid-cell"><div class="{d["style"]}">{d["grain"]}</div><div class="stock-val">{d["amt"]}</div><div class="loc-id">{loc}</div></div>'

# 원형 (A101~A506)
for r_idx, r_code in enumerate([1, 3, 5]):
    for c in range(1, 7):
        loc = f"A{r_code}0{c}"
        cell_data = inv.get(loc, {"곡종": "-", "재고량": "0"})
        d = get_style(cell_data['곡종'], cell_data['재고량'])
        top = r_idx * 100
        left = (c - 1) * 116 + 60 # 7칸 폭에 맞춘 정밀 조정
        html += f'<div class="circle-unit" style="top:{top}px; left:{left}px;"><div class="{d["style"]}">{d["grain"]}</div><div class="stock-val">{d["amt"]}</div><div class="loc-id">{loc}</div></div>'

html += '</div></div>'
st.markdown(html, unsafe_allow_html=True)

# 데이터 새로고침 버튼
if st.button("🔄 시트 데이터 새로고침"):
    st.rerun()
