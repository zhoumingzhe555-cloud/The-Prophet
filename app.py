import streamlit as st
import random
import time
import math
import pandas as pd
import requests
from datetime import datetime

# --- 页面配置 ---
st.set_page_config(page_title="预言家自选投注盘", page_icon="🎰", layout="centered")

# --- 手机移动端样式适配 (绿色高端投注站风格) ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; padding-left: 0.8rem; padding-right: 0.8rem; }
    
    /* 模拟平台专用绿色幻彩按钮 */
    .stButton>button { 
        background: linear-gradient(135deg, #009688, #004d40) !important; 
        color: white !important; border-radius: 25px !important; width: 100% !important; height: 50px !important; 
        font-size: 16px !important; font-weight: bold !important; border: none !important;
        box-shadow: 0px 4px 12px rgba(0,150,136,0.3);
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
    
    .wallet-card {
        background: linear-gradient(135deg, #1a1a1a, #333333); color: #ffd700;
        padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 15px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.2); font-weight: bold;
    }
    .mobile-card {
        background-color: #f8fafc; padding: 12px; border-radius: 12px;
        border-left: 6px solid #009688; margin-bottom: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 初始化虚拟钱包与注单历史 (Session State) ---
if 'wallet' not in st.session_state:
    st.session_state.wallet = 10000.0  # 初始赠送1万虚拟体验金

if 'bet_history' not in st.session_state:
    st.session_state.bet_history = []

# --- 官方49码球色定义 ---
RED_BALLS = [1, 2, 7, 8, 12, 13, 18, 19, 23, 24, 29, 30, 34, 35, 40, 45, 46]
BLUE_BALLS = [3, 4, 9, 10, 14, 15, 20, 25, 26, 31, 36, 37, 41, 42, 47, 48]
GREEN_BALLS = [5, 6, 11, 16, 17, 21, 22, 27, 28, 32, 33, 38, 39, 43, 44, 49]

def get_ball_style(num):
    if num in RED_BALLS: return "ball-red"
    if num in BLUE_BALLS: return "ball-blue"
    return "ball-green"

# --- 数据采集 ---
@st.cache_data(ttl=3600)
def fetch_live_data():
    try:
        url = "https://cpdata.io"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            item = response.json().get("data", [])
            return {"issue": item.get("issue"), "date": item.get("open_time")[:10], "numbers": [int(x) for x in item.get("numbers")[:6]], "special": int(item.get("numbers"))}
    except Exception:
        pass
    return {"issue": "26/051", "date": "2026-05-14", "numbers": [6, 14, 20, 23, 28, 34], "special": 49}

latest_draw = fetch_live_data()

# --- 手机顶栏：高档模拟盘钱包挂件 ---
st.title("🎰 预言家 - 模拟娱乐盘")
st.markdown(f"""
<div class="wallet-card">
    💰 个人模拟钱包余额：HK$ {st.session_state.wallet:,.2f}
</div>
""", unsafe_allow_html=True)

# 充值体验金
if st.button("🧧 余额不足？一键免费充值 $5000 模拟金"):
    st.session_state.wallet += 5000.0
    st.rerun()

# --- 开奖看板 ---
st.markdown(f"""
<div class="mobile-card">
    <div style="font-size:13px; color:#666;">📡 <b>最新搅珠基准</b>：第 <b>{latest_draw['issue']}</b> 期 ({latest_draw['date']})</div>
</div>
""", unsafe_allow_html=True)
ball_html = '<div class="ball-container">'
for num in latest_draw['numbers']: ball_html += f'<div class="ball {get_ball_style(num)}">{num}</div>'
ball_html += f'<div class="ball {get_ball_style(latest_draw["special"])}">{latest_draw["special"]}</div></div>'
st.markdown(ball_html, unsafe_allow_html=True)

st.divider()

# --- 三大官方主流模拟投注选号盘 ---
st.subheader("📝 请选择模拟投注大厅")
bet_tabs = st.tabs(["🎯 手动精准点号盘", "📊 专业复式盘", "📌 智能机选盘"])

# 1. 核心全新升级：手动精准点号盘
with bet_tabs[0]:
    st.markdown("### 🟢 精准自选：平码 ＋ 特码")
    st.caption("请在下方下拉点号方阵中，手动挑选您的5个平码和1个特码组合。")
    
    bet_price = st.radio("自选下注单价", ["全注 ($10)", "半注 ($5)"], horizontal=True, key="p_manual")
    cost_manual = 10 if "全注" in bet_price else 5
    
    # 构建1-49的字符串选项方便点击
    all_options = [i for i in range(1, 50)]
    
    # 手机交互式多选点号盘
    selected_ping = st.multiselect("👉 请点击点选 【5个平码（正码）】", options=all_options, help="必须正好选择5个号码")
    selected_te = st.multiselect("👉 请点击点选 【1个特码（特别号码）】", options=all_options, help="必须确认选择1个号码")
    
    # 动态数量提示防呆
    st.info(f"当前状态：已选平码 {len(selected_ping)}/5 个 | 已选特码 {len(selected_te)}/1 个")
    
    if st.button("🛒 确认提交精准自选注单"):
        # 执行全方位的严格逻辑自检
        if len(selected_ping) != 5:
            st.error("⚠️ 拦截失败：平码数量不正确！必须且只能选择 5 个平码号码。")
        elif len(selected_te) != 1:
            st.error("⚠️ 拦截失败：特码数量不正确！必须且只能选择 1 个特码号码。")
        elif len(set(selected_ping) & set(selected_te)) > 0:
            intersect = set(selected_ping) & set(selected_te)
            st.error(f"⚠️ 拦截失败：发现重号！号码 {list(intersect)} 同时存在于平码和特码中，请重新调整！")
        elif st.session_state.wallet < cost_manual:
            st.error("❌ 拦截失败：您的模拟钱包余额不足，请在顶栏免费充值。")
        else:
            # 扣款并打入注单总账
            st.session_state.wallet -= cost_manual
            sorted_ping = sorted(selected_ping)
            final_te = selected_te[0]
            
            # 格式化存根数据结构
            receipt_code = f"平码:{sorted_ping} | 特码:[{final_te}]"
            st.session_state.bet_history.append({
                "时间": datetime.now().strftime("%H:%M:%S"),
                "玩法": "精准自选(5平1特)",
                "所选号码": receipt_code,
                "模拟下注金额": f"${cost_manual}"
            })
            st.success(f"🎉 下注成功！电子存根已成功打印至账本底部。")
            st.rerun()

# 2. 专业复式盘
with bet_tabs[1]:
    st.markdown("### 🟢 复式多段组合盘")
    num_count = st.slider("请选择复式包裹号码个数", 7, 12, 7)
    total_notes = math.comb(num_count, 6)
    bet_price_f = st.radio("复式下注单价", ["全注 ($10)", "半注 ($5)"], horizontal=True, key="p2")
    cost_f = total_notes * (10 if "全注" in bet_price_f else 5)
    
    st.info(f"📊 该复式包含 **{total_notes}** 注 | 总计需模拟金：**HK$ {cost_f}**")
    
    if st.button("确认提交复式投注"):
        if st.session_state.wallet < cost_f:
            st.error("❌ 余额不足！")
        else:
            st.session_state.wallet -= cost_f
            f_nums = sorted(random.sample(range(1, 50), num_count))
            st.session_state.bet_history.append({"时间": datetime.now().strftime("%H:%M:%S"), "玩法": f"复式({num_count}码)", "所选号码": str(f_nums), "模拟下注金额": f"${cost_f}"})
            st.success(f"🎉 复式注单下注成功！大底号码：{f_nums}")
            st.rerun()

# 3. 智能机选盘
with bet_tabs[2]:
    st.markdown("### 🟢 智能机选大厅")
    bet_price_dt = st.radio("机选下注单价", ["全注 ($10)", "半注 ($5)"], horizontal=True, key="p3")
    cost_dt = 10 if "全注" in bet_price_dt else 5
    notes_to_gen = st.slider("想要机选下注几注？", 1, 5, 1, key="sl_gen")
    total_cost = notes_to_gen * int(cost_dt)
    
    st.info(f"📊 预计本次机选下注将从钱包扣除：HK$ {total_cost}")
    
    if st.button("确认提交机选下注"):
        if st.session_state.wallet < total_cost:
            st.error("❌ 余额不足！")
        else:
            st.session_state.wallet -= total_cost
            for _ in range(notes_to_gen):
                line_nums = sorted(random.sample(range(1, 50), 6))
                st.session_state.bet_history.append({
                    "时间": datetime.now().strftime("%H:%M:%S"),
                    "玩法": "智能机选",
                    "所选号码": str(line_nums),
                    "模拟下注金额": f"${cost_dt}"
                })
            st.success("🎉 智能机选多注成功！已同步录入下方总账。")
            st.rerun()

# --- 历史注单存根总账本 ---
st.divider()
st.header("🧾 个人模拟投注账单存根")
if st.session_state.bet_history:
    df_history = pd.DataFrame(st.session_state.bet_history)
    st.dataframe(df_history, use_container_width=True, hide_index=True)
    if st.button("🗑️ 清空账本历史记录"):
        st.session_state.bet_history = []
        st.rerun()
else:
    st.caption("📂 暂无任何模拟下注记录，请在上方选择玩法并点击“确认下注”。")

st.divider()
st.caption("⚠️ 本娱乐模拟盘仅供亲友圈概率逻辑推演、策略预算演练与数字组合娱乐。系统不包含任何真钱交易机制，纯属公益娱乐工具。")
