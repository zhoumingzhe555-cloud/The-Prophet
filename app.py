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
    
    /* 1-49数字方阵点号按钮专用样式 */
    div[data-testid="stHorizontalBlock"] button {
        background: #ffffff !important;
        color: #333333 !important;
        border: 1px solid #cccccc !important;
        border-radius: 8px !important;
        width: 100% !important;
        height: 38px !important;
        padding: 0px !important;
        font-weight: bold !important;
        font-size: 14px !important;
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

# --- 初始化Session State ---
if 'wallet' not in st.session_state: st.session_state.wallet = 10000.0
if 'bet_history' not in st.session_state: st.session_state.bet_history = []
if 'manual_ping' not in st.session_state: st.session_state.manual_ping = []
if 'manual_te' not in st.session_state: st.session_state.manual_te = []

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
            res_json = response.json()
            item = res_json.get("data", [{}])[0]
            return {"issue": item.get("issue"), "date": item.get("open_time")[:10], "numbers": [int(x) for x in item.get("numbers")[:6]], "special": int(item.get("numbers")[6])}
    except Exception:
        pass
    return {"issue": "26/051", "date": "2026-05-14", "numbers": [2, 7, 15, 24, 31, 42], "special": 49}

latest_draw = fetch_live_data()

# --- 手机顶栏 ---
st.title("🎰 预言家 - 模拟娱乐盘")
st.markdown(f'<div class="wallet-card">💰 个人模拟钱包余额：HK$ {st.session_state.wallet:,.2f}</div>', unsafe_allow_html=True)

if st.button("🧧 一键免费充值 $5000 模拟金"):
    st.session_state.wallet += 5000.0
    st.rerun()

# --- 开奖看板 ---
st.markdown(f'<div class="mobile-card"><div style="font-size:13px; color:#666;">📡 <b>最新搅珠基准</b>：第 <b>{latest_draw["issue"]}</b> 期 ({latest_draw["date"]})</div></div>', unsafe_allow_html=True)
ball_html = '<div class="ball-container">'
for num in latest_draw['numbers']: ball_html += f'<div class="ball {get_ball_style(num)}">{num}</div>'
ball_html += f'<div class="ball {get_ball_style(latest_draw["special"])}">{latest_draw["special"]}</div></div>'
st.markdown(ball_html, unsafe_allow_html=True)

st.divider()

# --- 功能面板大厅 ---
st.subheader("📝 请选择模拟投注大厅")
bet_tabs = st.tabs(["🔘 分离自选大厅", "📊 专业复式盘", "📌 智能机选盘"])

# 1. 精准分离自选大厅
with bet_tabs[0]:
    st.markdown("### 🟢 平码与特码分开选号")
    bet_price = st.radio("自选下注单价", ["全注 ($10)", "半注 ($5)"], horizontal=True, key="p_manual")
    cost_manual = 10 if "全注" in bet_price else 5

    # 篮子状态常驻提示
    st.info(f"🛒 篮子状态：平码【{len(st.session_state.manual_ping)}/5】 | 特码【{len(st.session_state.manual_te)}/1】")

    # --- 区域A：平码盘（5个） ---
    st.markdown("#### 🟠 第一步：选择 5 个【平码（正码）】")
    for row in range(7):
        cols = st.columns(7)
        for col in range(7):
            num = row * 7 + col + 1
            if num <= 49:
                lbl = f"{num:02d} 🟠" if num in st.session_state.manual_ping else f"{num:02d}"
                if cols[col].button(lbl, key=f"ping_{num}"):
                    if num in st.session_state.manual_ping:
                        st.session_state.manual_ping.remove(num)
                    elif len(st.session_state.manual_ping) < 5:
                        st.session_state.manual_ping.append(num)
                    else:
                        st.warning("平码已选满5个！如需更换请先点击已选数字取消。")
                    st.rerun()

    st.write("")
    # --- 区域B：特码盘（1个） ---
    st.markdown("#### 🔵 第二步：选择 1 个【特码（特别号码）】")
    for row in range(7):
        cols = st.columns(7)
        for col in range(7):
            num = row * 7 + col + 1
            if num <= 49:
                lbl = f"{num:02d} 🔵" if num in st.session_state.manual_te else f"{num:02d}"
                if cols[col].button(lbl, key=f"te_{num}"):
                    if num in st.session_state.manual_te:
                        st.session_state.manual_te.remove(num)
                    elif len(st.session_state.manual_te) < 1:
                        st.session_state.manual_te.append(num)
                    else:
                        st.session_state.manual_te = [num] # 直接替换
                    st.rerun()

    # 控制按钮
    st.write("")
    col_op1, col_op2 = st.columns(2)
    if col_op1.button("🗑️ 清空当前选择"):
        st.session_state.manual_ping = []
        st.session_state.manual_te = []
        st.rerun()

    if col_op2.button("🛒 确认提交平特自选注单"):
        # 交叉重号及数量完整性检测
        intersect = set(st.session_state.manual_ping) & set(st.session_state.manual_te)
        
        if len(st.session_state.manual_ping) != 5:
            st.error("⚠️ 提交失败：平码池必须且只能选择 5 个号码！")
        elif len(st.session_state.manual_te) != 1:
            st.error("⚠️ 提交失败：特码池必须选择 1 个号码！")
        elif len(intersect) > 0:
            st.error(f"⚠️ 提交失败：号码 {list(intersect)} 在平码和特码中重复勾选，不符合投注规则！")
        elif st.session_state.wallet < cost_manual:
            st.error("❌ 提交失败：您的虚拟余额不足！")
        else:
            st.session_state.wallet -= cost_manual
            r_code = f"平码:{sorted(st.session_state.manual_ping)} | 特码:{st.session_state.manual_te}"
            st.session_state.bet_history.append({
                "时间": datetime.now().strftime("%H:%M:%S"),
                "玩法": "精准分离自选",
                "所选号码": r_code,
                "模拟下注金额": f"${cost_manual}"
            })
            st.session_state.manual_ping = []
            st.session_state.manual_te = []
            st.success("🎉 模拟投注单成功打印存根！")
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
        if st.session_state.wallet < cost_f: st.error("❌ 余额不足！")
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
        if st.session_state.wallet < total_cost: st.error("❌ 余额不足！")
        else:
            st.session_state.wallet -= total_cost
            for _ in range(notes_to_gen):
                line_nums = sorted(random.sample(range(1, 50), 6))
                st.session_state.bet_history.append({"时间": datetime.now().strftime("%H:%M:%S"), "玩法": "智能机选", "所选号码": str(line_nums), "模拟下注金额": f"${cost_dt}"})
            st.success("🎉 智能机选多注成功！")
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
