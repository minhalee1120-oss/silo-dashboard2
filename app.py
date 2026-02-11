import streamlit as st

st.set_page_config(layout="wide", page_title="대한싸이로 재고현황판")

# 디자인 설정: 7x2 네모 격자 틀 위에 6개씩의 원을 배치
st.markdown("""
<style>
    .dashboard-outer { display: flex; justify-content: center; padding-top: 60px; background-color: white; }
    .grid-container {
        position: relative;
        display: grid;
        grid-template-columns: repeat(7, 100px); /* 가로 7칸으로 수정 */
        grid-template-rows: repeat(2, 100px);    /* 세로 2줄 */
        border: 1.5px solid #333;
        background-color: white;
    }
    .grid-cell {
        border: 1.5px solid #333;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        position: relative;
    }
    
    /* 원형 싸이로: 격자 세로선(꼭짓점)에 위치 */
    .circle-unit {
        position: absolute;
        width: 90px; height: 90px;
        border: 2px solid #333; border-radius: 50%;
        background-color: white;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        z-index: 20;
        transform: translate(-50%, -50%);
    }

    /* 텍스트 스타일 */
    .blue-grain { color: #0000FF; font-weight: bold; font-size: 14px; }
    .brown-grain { color: #8B4513; font-weight: bold; font-size: 14px; }
    .stock-val { color: black; font-weight: bold; font-size: 13px; margin: 1px 0; }
    .loc-id { color: #90EE90; font-size: 10px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

def get_style(grain, amt):
    if not grain or not grain.upper().startswith('W'):
        return {"style": "", "grain": "-", "amt": "0"}
    blue = ['WASW', 'WASWP', 'WUSH', 'WUSL9.0']
    style = "blue-grain" if grain.upper() in blue else "brown-grain"
    return {"style": style, "grain": grain, "amt": amt}

col_dash, col_input = st.columns([3, 1])
with col_input:
    st.subheader("📋 데이터 입력")
    raw_data = st.text_area("엑셀 데이터를 붙여넣으세요", height=500)

with col_dash:
    st.markdown("<h1 style='text-align: center; text-decoration: underline;'>일 일 재 고 현 황 표</h1>", unsafe_allow_html=True)
    
    inv = {}
    if raw_data:
        for line in raw_data.strip().split('\n'):
            parts = line.split()
            if len(parts) >= 3:
                try: amt = "{:,.0f}".format(float(parts[2].replace(',', '')))
                except: amt = parts[2]
                inv[parts[0].strip()] = {"grain": parts[1].strip(), "amt": amt}

    # 대시보드 렌더링
    html = '<div class="dashboard-outer"><div class="grid-container">'

    # 1. 네모칸 데이터 배치 (A201~A207, A401~A407 - 가로 7칸)
    for r_idx, r_code in enumerate([2, 4]):
        for c in range(1, 8): # 7칸으로 확장
            loc = f"A{r_code}0{c}"
            d = get_style(inv.get(loc, {}).get('grain'), inv.get(loc, {}).get('amt'))
            html += f'<div class="grid-cell">' \
                    f'<div class="{d["style"]}">{d["grain"]}</div>' \
                    f'<div class="stock-val">{d["amt"]}</div>' \
                    f'<div class="loc-id">{loc}</div></div>'

    # 2. 원형 데이터 배치 (A101~A506 - 가로 6개씩 3줄)
    # 위치: 격자 세로선(0, 100, 200, 300, 400, 500, 600, 700) 중 사진 구조에 맞게 배치
    for r_idx, r_code in enumerate([1, 3, 5]):
        for c in range(1, 7): # 원형은 6개 유지
            loc = f"A{r_code}0{c}"
            d = get_style(inv.get(loc, {}).get('grain'), inv.get(loc, {}).get('amt'))
            top = r_idx * 100
            left = (c - 1) * 100 + 100 # 첫 번째 세로선부터 시작하여 칸 사이에 위치
            
            # 사진처럼 첫 번째 원형이 맨 왼쪽 선에 붙어야 한다면 아래 수치로 조정 가능
            left = (c - 1) * 116 + 60 # 7칸 전체 폭에 맞춰 균등 배분 (약간의 조정 필요)
            
            # 보다 직관적인 위치 계산 (7개 칸의 경계선 위치)
            left = (c - 1) * 100 + 100 if c < 7 else 600

            html += f'<div class="circle-unit" style="top:{top}px; left:{left}px;">' \
                    f'<div class="{d["style"]}">{d["grain"]}</div>' \
                    f'<div class="stock-val">{d["amt"]}</div>' \
                    f'<div class="loc-id">{loc}</div></div>'

    html += '</div></div>'
    st.markdown(html, unsafe_allow_html=True)