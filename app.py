import streamlit as st
import random
import time
import math
import pandas as pd

# --- 页面配置：强制单列紧凑模式，最适合手机 ---
st.set_page_config(page_title="预言家", page_icon="🔮", layout="centered")

# --- 手机移动端深度适配样式 ---
st.markdown("""
    <style>
    /* 适配手机屏幕：去除多余的边距 */
    .block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; padding-left: 1rem; padding-right: 1rem; }
    
    /* 专为手指触摸设计的超大醒目按钮 */
    .stButton>button { 
        background-color: #4b0082 !important; 
        color: white !important; 
        border-radius: 25px !important; 
        width: 100% !important; 
        height: 50px !important; 
        font-size: 18px !important;
        font-weight: bold !important; 
        box-shadow: 0px 4px 10px rgba(75,0,130,0.3);
    }
    
    /* 号码球包裹容器：允许自动换行，防止手机横向溢出 */
    .ball-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 8px;
        margin-bottom: 12px;
    }
    
    /* 手机端完美圆球，文字居中，带微立体阴影 */
    .ball { 
        width: 42px; 
        height: 42px; 
        line-height: 42px; 
        border-radius: 50%; 
        background: linear-gradient(135deg, #2e8b57, #1e5c38); 
        color: white; 
        text-align: center; 
        font-weight: bold; 
        font-size: 16px;
        box-shadow: 1px 3px 6px rgba(0,0,0,0.2);
    }
    .ball-dan { background: linear-gradient(135deg, #ff8c00, #d35400); } 
    .ball-tuo { background: linear-gradient(135deg, #4682b4, #2980b9); } 
    .ball-special { background: linear-gradient(135deg, #dc143c, #c0392b); }
    
    /* 专门为手机设计的紧凑卡片背景 */
    .mobile-card {
        background-color: #f7f9fa;
        padding: 12px;
        border-radius: 12px;
        border-left: 5px solid #4b0082;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 顶栏设置 ---
st.title("🔮 预言家 (The Prophet)")
st.caption("📱 移动端精简适配版 | 随时随地，尽在掌握")

st.divider()

# --- 往期真实数据 ---
@st.cache_data
def get_historical_data():
    return [
        {"期数": "26/051", "日期": "2026-05-14", "正码": [8, 13, 21, 25, 34, 46], "特别号码": 7},
        {"期数": "26/050", "日期": "2026-05-12", "正码": [1, 15, 23, 27, 40, 48], "特别号码": 22},
        {"期数": "26/049", "日期": "2026-05-10", "正码": [5, 12, 19, 31, 38, 42], "特别号码": 11},
        {"期数": "26/048", "日期": "2026-05-07", "正码": [6, 14, 20, 23, 28, 34], "特别号码": 49},
        {"期数": "26/047", "日期": "2026-05-05", "正码": [2, 7, 8, 10, 18, 47], "特别号码": 4},
        {"期数": "26/046", "日期": "2026-05-02", "正码": [2, 3, 8, 28, 30, 48], "特别号码": 9},
    ]

history_list = get_historical_data()
latest_draw = history_list[0]

# --- 手机模块 1：最新开奖卡片 ---
st.markdown(f"""
<div class="mobile-card">
    <div style="font-size:14px; color:#666;">最新搅珠：第 <b>{latest_draw['期数']}</b> 期 ({latest_draw['日期']})</div>
</div>
""", unsafe_allow_html=True)

# 渲染最新一期球
ball_html = '<div class="ball-container">'
for num in latest_draw['正码']:
    ball_html += f'<div class="ball">{num}</div>'
ball_html += f'<div class="ball ball-special">{latest_draw["特别号码"]}</div></div>'
st.markdown(ball_html, unsafe_allow_html=True)

# 适合手机上下滑动的折叠历史
with st.expander("🔍 点击展开历史开奖（带期数和日期）"):
    for draw in history_list:
        drawn_txt = "  ".join(f"[{n}]" for n in draw['正码'])
        st.markdown(f"""
        <div style="padding: 8px 0; border-bottom: 1px solid #eee; font-size:14px;">
            <b>第{draw['期数']}期</b> ({draw['日期']})<br>
            <span style="color:#2e8b57; font-weight:bold;">正码:</span> {drawn_txt} 
            <span style="color:#dc143c; font-weight:bold;">特别:</span> [{draw['特别号码']}]
        </div>
        """, unsafe_allow_html=True)

st.divider()

# --- 组合数计算 ---
def calculate_combinations(n, k):
    return math.comb(n, k) if n >= k else 0

# --- 手机模块 2：双弄标签页 ---
play_type = st.tabs(["💡 智能复式", "🎯 黄金胆拖"])

# --- 复式模块 ---
with play_type[0]:
    num_count = st.slider("选号个数", min_value=7, max_value=12, value=7, help="滑动选择需要生成的复式总字数")
    total_notes = calculate_combinations(num_count, 6)
    
    # 手机紧凑双排显示预算
    col_p1, col_p2 = st.columns(2)
    col_p1.caption(f"📊 总注数: **{total_notes} 注**")
    col_p2.caption(f"💰 全注/半注: **${total_notes*10} / ${total_notes*5}**")
    
    if st.button("✨ 启动复式预言"):
        with st.spinner('预言中...'):
            time.sleep(0.8)
            picked_numbers = sorted(random.sample(range(1, 50), num_count))
            st.success("🔮 预言家精选复式组合：")
            
            res_html = '<div class="ball-container">'
            for num in picked_numbers:
                res_html += f'<div class="ball">{num}</div>'
            res_html += '</div>'
            st.markdown(res_html, unsafe_allow_html=True)
            
            # 方便手机用户一键转发给朋友
            st.text_area("📋 文本复制区（长按全选复制）", value=f"预言家复式推荐（{num_count}码）：" + ", ".join(map(str, picked_numbers)), height=70)

# --- 胆拖模块 ---
with play_type[1]:
    dan_count = st.slider("胆码个数", min_value=1, max_value=5, value=2)
    tuo_count = st.slider("拖码个数", min_value=7-dan_count, max_value=20, value=6)
    
    dan_notes = calculate_combinations(tuo_count, 6 - dan_count)
    
    col_t1, col_t2 = st.columns(2)
    col_t1.caption(f"📊 总注数: **{dan_notes} 注**")
    col_t2.caption(f"💰 全注/半注: **${dan_notes*10} / ${dan_notes*5}**")
    
    if st.button("⚡ 启动胆拖预言"):
        with st.spinner('盘算中...'):
            time.sleep(0.8)
            all_pool = list(range(1, 50))
            random.shuffle(all_pool)
            
            dans = sorted(all_pool[:dan_count])
            tuos = sorted(all_pool[dan_count:dan_count+tuo_count])
            
            st.write("🟠 **必买胆码：**")
            d_html = '<div class="ball-container">'
            for d in dans: d_html += f'<div class="ball ball-dan">{d}</div>'
            d_html += '</div>'
            st.markdown(d_html, unsafe_allow_html=True)
                
            st.write("🔵 **配脚拖码范围：**")
            t_html = '<div class="ball-container">'
            for t in tuos: t_html += f'<div class="ball ball-tuo">{t}</div>'
            t_html += '</div>'
            st.markdown(t_html, unsafe_allow_html=True)

st.divider()
st.caption("⚠️ 提示：彩票完全随机。本工具仅供手机端参考和数学概率研究，请理性娱乐。")
