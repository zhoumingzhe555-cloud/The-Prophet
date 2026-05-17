import streamlit as st
import random
import time
import math
import pandas as pd
import requests

# --- 页面配置 ---
st.set_page_config(page_title="预言家投注助手", page_icon="🔮", layout="centered")

# --- 手机移动端样式适配 ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; padding-left: 0.8rem; padding-right: 0.8rem; }
    .stButton>button { 
        background: linear-gradient(135deg, #228b22, #006400) !important; /* 投注站经典绿色 */
        color: white !important; border-radius: 25px !important; width: 100% !important; height: 52px !important; 
        font-size: 18px !important; font-weight: bold !important; border: none !important;
        box-shadow: 0px 5px 15px rgba(34,139,34,0.4);
    }
    .ball-container { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 5px; margin-bottom: 5px; }
    .ball { 
        width: 38px; height: 38px; line-height: 38px; border-radius: 50%; 
        color: white; text-align: center; font-weight: bold; font-size: 14px;
        box-shadow: 1px 2px 5px rgba(0,0,0,0.15);
    }
    .ball-red { background: linear-gradient(135deg, #dc143c, #960018); }
    .ball-blue { background: linear-gradient(135deg, #1e90ff, #002fa7); }
    .ball-green { background: linear-gradient(135deg, #2e8b57, #124e2c); }
    .ball-dan { background: linear-gradient(135deg, #ff8c00, #d35400); } 
    .ball-tuo { background: linear-gradient(135deg, #4682b4, #2980b9); } 
    .mobile-card {
        background-color: #f8fafc; padding: 12px; border-radius: 12px;
        border-left: 6px solid #228b22; margin-bottom: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 官方49码球色定义 ---
RED_BALLS = [1, 2, 7, 8, 12, 13, 18, 19, 23, 24, 29, 30, 34, 35, 40, 45, 46]
BLUE_BALLS = [3, 4, 9, 10, 14, 15, 20, 25, 26, 31, 36, 37, 41, 42, 47, 48]
GREEN_BALLS = [5, 6, 11, 16, 17, 21, 22, 27, 28, 32, 33, 38, 39, 43, 44, 49]

def get_ball_style(num):
    if num in RED_BALLS: return "ball-red"
    if num in BLUE_BALLS: return "ball-blue"
    return "ball-green"

# --- 数据采集模块 ---
@st.cache_data(ttl=3600)
def fetch_live_lottery_data():
    try:
        url = "https://cpdata.io"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            res_json = response.json()
            live_data = []
            for item in res_json.get("data", []):
                live_data.append({
                    "issue": item.get("issue"),
                    "date": item.get("open_time")[:10],
                    "numbers": [int(x) for x in item.get("numbers")[:6]],
                    "special": int(item.get("numbers")[6])
                })
            if live_data: return live_data
    except Exception:
        pass
    return [{"issue": "26/051", "date": "2026-05-14", "numbers": [6, 14, 20, 23, 28, 34], "special": 49}]

history_data = fetch_live_lottery_data()
latest_draw = history_data[0]

# --- 界面顶栏 ---
st.title("🎰 预言家 - 模拟投注助手")
st.caption("📱 移动端自适应 | 官方注数推算与虚拟电子注单系统")

# --- 开奖看板 ---
st.markdown(f"""
<div class="mobile-card">
    <div style="font-size:14px; color:#555;">📡 <b>最新开奖参考</b>：第 <b>{latest_draw['issue']}</b> 期 ({latest_draw['date']})</div>
</div>
""", unsafe_allow_html=True)

ball_html = '<div class="ball-container">'
for num in latest_draw['numbers']:
    ball_html += f'<div class="ball {get_ball_style(num)}">{num}</div>'
ball_html += f'<div class="ball {get_ball_style(latest_draw["special"])}">{latest_draw["special"]}</div></div>'
st.markdown(ball_html, unsafe_allow_html=True)

st.divider()

# --- 模拟投注核心功能区 ---
st.subheader("📝 选择您的投注方式")
bet_tabs = st.tabs(["📌 单式投注", "📊 复式投注", "🎯 胆拖投注"])

# 1. 单式投注
with bet_tabs[0]:
    st.markdown("### 选项1：单式机选（每注$10）")
    bet_lines = st.slider("请选择需要生成的注数", min_value=1, max_value=5, value=1)
    bet_price = st.radio("单注金额", ["全注 ($10)", "半注 ($5)"], horizontal=True)
    unit_cost = 10 if "全注" in bet_price else 5
    
    if st.button("生成单式电子注单"):
        st.success(f"📋 虚拟电子投注单生成成功（总额: HK$ {bet_lines * unit_cost}）")
        ticket_text = f"--- 预言家虚拟投注单 (单式) ---\n"
        for line in range(bet_lines):
            line_nums = sorted(random.sample(range(1, 50), 6))
            ticket_text += f"第{line+1}注: {', '.join(map(str, line_nums))}\n"
            
            # 显示精美球色
            st.markdown(f"**第 {line+1} 注：**")
            html_line = '<div class="ball-container">'
            for n in line_nums: html_line += f'<div class="ball {get_ball_style(n)}">{n}</div>'
            st.markdown(html_line + '</div>', unsafe_allow_html=True)
            
        st.text_area("📋 长按下方区域可以全选复制注单", value=ticket_text, height=130)

# 2. 复式投注
with bet_tabs[1]:
    st.markdown("### 选项2：复式智能选号")
    num_count = st.slider("选择复式选号个数", min_value=7, max_value=12, value=7, help="复式玩法从选满7个字开始算起")
    
    total_notes = math.comb(num_count, 6)
    st.metric("该复式组合拆解后包含", f"{total_notes} 注")
    
    col_f1, col_f2 = st.columns(2)
    col_f1.info(f"💰 全注金额: HK$ {total_notes * 10}")
    col_f2.success(f"🌗 半注金额: HK$ {total_notes * 5}")
    
    if st.button("生成复式电子注单"):
        picked_numbers = sorted(random.sample(range(1, 50), num_count))
        st.success("🔮 模拟投注成功！选中的复式组合如下：")
        
        res_html = '<div class="ball-container">'
        for num in picked_numbers: res_html += f'<div class="ball {get_ball_style(num)}">{num}</div>'
        st.markdown(res_html + '</div>', unsafe_allow_html=True)
        
        multi_text = f"--- 预言家虚拟投注单 (复式) ---\n选号共 {num_count} 码: {', '.join(map(str, picked_numbers))}\n总计: {total_notes} 注"
        st.text_area("📋 复制复式注单", value=multi_text, height=90)

# 3. 胆拖投注
with bet_tabs[2]:
    st.markdown("### 选项3：胆拖稳健组合")
    dan_count = st.slider("选择‘胆码’个数", min_value=1, max_value=5, value=2, help="作为死码，每注里都必须包含的数字")
    tuo_count = st.slider("选择‘拖码’个数", min_value=7-dan_count, max_value=20, value=6, help="配合胆码组合的配脚数字")
    
    dan_notes = math.comb(tuo_count, 6 - dan_count)
    st.metric("该胆拖组合拆解后包含", f"{dan_notes} 注")
    
    col_t1, col_t2 = st.columns(2)
    col_t1.info(f"💰 全注金额: HK$ {dan_notes * 10}")
    col_t2.success(f"🌗 半注金额: HK$ {dan_notes * 5}")
    
    if st.button("生成胆拖电子注单"):
        all_pool = list(range(1, 50))
        random.shuffle(all_pool)
        dans = sorted(all_pool[:dan_count])
        tuos = sorted(all_pool[dan_count:dan_count+tuo_count])
        
        st.write("🟠 **您锁定的‘胆码’：**")
        d_html = '<div class="ball-container">'
        for d in dans: d_html += f'<div class="ball ball-dan">{d}</div>'
        st.markdown(d_html + '</div>', unsafe_allow_html=True)
            
        st.write("🔵 **您的配脚‘拖码’：**")
        t_html = '<div class="ball-container">'
        for t in tuos: t_html += f'<div class="ball ball-tuo">{t}</div>'
        st.markdown(t_html + '</div>', unsafe_allow_html=True)
        
        dt_text = f"--- 预言家虚拟投注单 (胆拖) ---\n胆码: {', '.join(map(str, dans))}\n拖码: {', '.join(map(str, tuos))}\n总计: {dan_notes} 注"
        st.text_area("📋 复制胆拖注单", value=dt_text, height=100)

st.divider()
st.caption("⚠️ 合规安全提示：本工具仅供模拟投注演练、资金预算推算与数学概率研究。软件不具备任何线上金钱投注功能，购买实体彩票请前往合法的境外官方网点。")
