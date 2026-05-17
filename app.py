import streamlit as st
import random
import time
import math
import pandas as pd
import requests
from datetime import datetime

# --- 页面配置 ---
st.set_page_config(page_title="预言家旗舰投注盘", page_icon="🎰", layout="centered")

# --- 手机移动端样式适配 (经典高端博弈主题风格) ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; padding-left: 0.8rem; padding-right: 0.8rem; }
    
    /* 模拟平台专用幻彩绿色按钮 */
    .stButton>button { 
        background: linear-gradient(135deg, #009688, #004d40) !important; 
        color: white !important; border-radius: 25px !important; width: 100% !important; height: 48px !important; 
        font-size: 15px !important; font-weight: bold !important; border: none !important;
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

# --- 初始化Session State ---
if 'wallet' not in st.session_state: st.session_state.wallet = 10000.0
if 'bet_history' not in st.session_state: st.session_state.bet_history = []
if 'manual_ping' not in st.session_state: st.session_state.manual_ping = []
if 'manual_te' not in st.session_state: st.session_state.manual_te = []

# --- 官方49码球色划分 ---
RED_BALLS = [1, 2, 7, 8, 12, 13, 18, 19, 23, 24, 29, 30, 34, 35, 40, 45, 46]
BLUE_BALLS = [3, 4, 9, 10, 14, 15, 20, 25, 26, 31, 36, 37, 41, 42, 47, 48]
GREEN_BALLS = [5, 6, 11, 16, 17, 21, 22, 27, 28, 32, 33, 38, 39, 43, 44, 49]

def get_ball_style(num):
    if num in RED_BALLS: return "ball-red"
    if num in BLUE_BALLS: return "ball-blue"
    return "ball-green"

# --- 数据同步 ---
@st.cache_data(ttl=3600)
def fetch_live_data():
    try:
        url = "https://cpdata.io"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            item = response.json().get("data", [{}])[0]
            return {"issue": item.get("issue"), "date": item.get("open_time")[:10], "numbers": [int(x) for x in item.get("numbers")[:6]], "special": int(item.get("numbers")[6])}
    except Exception:
        pass
    return {"issue": "26/051", "date": "2026-05-14", "numbers": [2, 7, 15, 24, 31, 42], "special": 49}

latest_draw = fetch_live_data()

# --- 钱包吊顶 ---
st.title("🎰 预言家 - 全功能娱乐盘")
st.markdown(f'<div class="wallet-card">💰 个人模拟钱包余额：HK$ {st.session_state.wallet:,.2f}</div>', unsafe_allow_html=True)

if st.button("🧧 一键免费充值 $5000 模拟金"):
    st.session_state.wallet += 5000.0
    st.rerun()

st.markdown(f'<div class="mobile-card"><div style="font-size:13px; color:#666;">📡 <b>最新开奖基准</b>：第 <b>{latest_draw["issue"]}</b> 期 ({latest_draw["date"]})</div></div>', unsafe_allow_html=True)
ball_html = '<div class="ball-container">'
for num in latest_draw['numbers']: ball_html += f'<div class="ball {get_ball_style(num)}">{num}</div>'
ball_html += f'<div class="ball {get_ball_style(latest_draw["special"])}">{latest_draw["special"]}</div></div>'
st.markdown(ball_html, unsafe_allow_html=True)

st.divider()

# --- 核心大升级：全主流投注玩法大厅 ---
st.subheader("🔮 模拟投注大厅（已囊括官方与双面全玩法）")
bet_tabs = st.tabs(["🔘 自选平特", "🎯 一马中特", "📊 标准复式", "🎲 黄金胆拖", "🌈 趣味双面"])

# 玩法1：平特分离自选
with bet_tabs[0]:
    st.markdown("### 🟢 单式手选（5平码 + 1特码）")
    cost_m = 10
    st.info(f"🛒 篮子状态：平码【{len(st.session_state.manual_ping)}/5】 | 特码【{len(st.session_state.manual_te)}/1】")

    with st.expander("🟠 点击展开/收起 ——【5个平码选择键盘】", expanded=True):
        for row in range(7):
            cols = st.columns(7)
            for col in range(7):
                num = row * 7 + col + 1
                if num <= 49:
                    lbl = f"{num:02d} 🟠" if num in st.session_state.manual_ping else f"{num:02d}"
                    if cols[col].button(lbl, key=f"p1_{num}"):
                        if num in st.session_state.manual_ping: st.session_state.manual_ping.remove(num)
                        elif len(st.session_state.manual_ping) < 5: st.session_state.manual_ping.append(num)
                        st.rerun()

    with st.expander("🔵 点击展开/收起 ——【1个特码选择键盘】", expanded=True):
        for row in range(7):
            cols = st.columns(7)
            for col in range(7):
                num = row * 7 + col + 1
                if num <= 49:
                    lbl = f"{num:02d} 🔵" if num in st.session_state.manual_te else f"{num:02d}"
                    if cols[col].button(lbl, key=f"t1_{num}"):
                        if num in st.session_state.manual_te: st.session_state.manual_te.remove(num)
                        else: st.session_state.manual_te = [num]
                        st.rerun()

    col_o1, col_o2 = st.columns(2)
    if col_op1 := col_o1.button("🗑️ 清空自选", key="clear_m"):
        st.session_state.manual_ping, st.session_state.manual_te = [], []
        st.rerun()
    if col_op2 := col_o2.button("🛒 确认下注", key="submit_m"):
        intersect = set(st.session_state.manual_ping) & set(st.session_state.manual_te)
        if len(st.session_state.manual_ping) != 5 or len(st.session_state.manual_te) != 1: st.error("⚠️ 数量不符规则！")
        elif len(intersect) > 0: st.error("⚠️ 平码与特码不能重号！")
        elif st.session_state.wallet < cost_m: st.error("❌ 余额不足！")
        else:
            st.session_state.wallet -= cost_m
            st.session_state.bet_history.append({"时间": datetime.now().strftime("%H:%M:%S"), "玩法": "单式手选", "所选号码": f"平:{sorted(st.session_state.manual_ping)} 特:{st.session_state.manual_te}", "下注金额": f"${cost_m}"})
            st.session_state.manual_ping, st.session_state.manual_te = [], []
            st.success("🎉 下注成功！")
            st.rerun()

# 玩法2：一马中特大厅
with bet_tabs[1]:
    st.markdown("### 🎯 精准一马中特单挑（每注$50）")
    st.caption("从1-49中直接选出且仅选出一个核心特码，回报率极高！")
    cost_one = 50
    
    selected_one = st.selectbox("请在下方挑选您的孤注一掷绝杀特码球", options=[i for i in range(1, 50)], index=18)
    if st.button("🔥 确认提交一马中特注单", key="sub_one_bet"):
        if st.session_state.wallet < cost_one: st.error("❌ 余额不足！")
        else:
            st.session_state.wallet -= cost_one
            st.session_state.bet_history.append({"时间": datetime.now().strftime("%H:%M:%S"), "玩法": "一马中特", "所选号码": f"单选特码:[{selected_one:02d}]", "下注金额": f"${cost_one}"})
            st.success(f"🎉 一马中特【{selected_one:02d}】出票成功！已写入存根。")
            st.rerun()

# 玩法3：专业复式盘
with bet_tabs[2]:
    st.markdown("### 📊 标准官方复式多组盘")
    num_count = st.slider("请选择复式包裹号码个数", 7, 12, 7, key="sl_f")
    total_notes = math.comb(num_count, 6)
    cost_f = total_notes * 10
    st.info(f"📊 该复式折合 **{total_notes}** 注 | 总计需模拟金：**HK$ {cost_f}**")
    
    if st.button("确认提交复式投注", key="sub_f_bet"):
        if st.session_state.wallet < cost_f: st.error("❌ 余额不足！")
        else:
            st.session_state.wallet -= cost_f
            f_nums = sorted(random.sample(range(1, 50), num_count))
            st.session_state.bet_history.append({"时间": datetime.now().strftime("%H:%M:%S"), "玩法": f"复式({num_count}码)", "所选号码": str(f_nums), "下注金额": f"${cost_f}"})
            st.success(f"🎉 复式注单下注成功！大底号码：{f_nums}")
            st.rerun()

# 玩法4：黄金胆拖盘
with bet_tabs[3]:
    st.markdown("### 🎲 官方胆拖稳健盘")
    dan_count = st.slider("胆码个数（每注必有核心死码）", 1, 5, 2, key="sl_d")
    tuo_count = st.slider("拖码个数（外围配脚范围）", 7-dan_count, 15, 6, key="sl_t")
    total_notes_dt = math.comb(tuo_count, 6 - dan_count)
    cost_dt = total_notes_dt * 10
    st.info(f"📊 该胆拖折合 **{total_notes_dt}** 注 | 总计需模拟金：**HK$ {cost_dt}**")
    
    if st.button("确认提交胆拖投注", key="sub_dt_bet"):
        if st.session_state.wallet < cost_dt: st.error("❌ 余额不足！")
        else:
            st.session_state.wallet -= cost_dt
            pool = list(range(1, 49))
            random.shuffle(pool)
            dans = sorted(pool[:dan_count])
            tuos = sorted(pool[dan_count:dan_count+tuo_count])
            st.session_state.bet_history.append({"时间": datetime.now().strftime("%H:%M:%S"), "玩法": f"胆拖({dan_count}胆{tuo_count}拖)", "所选号码": f"胆:{dans} 拖:{tuos}", "下注金额": f"${cost_dt}"})
            st.success("🎉 模拟胆拖注单已成功出票！")
            st.rerun()

# 玩法5：趣味双面盘
with bet_tabs[4]:
    st.markdown("### 🌈 民间趣味特码双面盘（定额一注$20）")
    st.caption("支持快速下注特码的波色趋势、大小区间以及单双属性。")
    cost_side = 20
    
    side_mode = st.selectbox("请选择双面投注细分玩法", ["特码波色单挑", "特码大小单挑", "特码单双单挑"])
    
    if side_mode == "特码波色单挑":
        side_pick = st.radio("请点选看好的特码波色", ["红波特码池", "蓝波特码池", "绿波特码池"], horizontal=True)
    elif side_mode == "特码大小单挑":
        side_pick = st.radio("请点选看好的特码大小", ["大球群 (25-49)", "小球群 (01-24)"], horizontal=True)
    else:
        side_pick = st.radio("请点选看好的特码单双", ["特码开单数 (1,3,5...)", "特码开双数 (2,4,6...)"], horizontal=True)
        
    if st.button("⚡ 确认提交双面玩法注单", key="sub_side_bet"):
        if st.session_state.wallet < cost_side: st.error("❌ 余额不足！")
        else:
            st.session_state.wallet -= cost_side
            st.session_state.bet_history.append({"时间": datetime.now().strftime("%H:%M:%S"), "玩法": f"双面盘({side_mode})", "所选号码": f"勾选方向:[{side_pick}]", "下注金额": f"${cost_side}"})
            st.success(f"🎉 双面盘 [{side_pick}] 虚拟出票成功！")
            st.rerun()

# --- 历史注单存根总账本 ---
st.divider()
st.header("🧾 个人模拟投注账单存根")
if st.session_state.bet_history:
    df_history = pd.DataFrame(st.session_state.bet_history)
    st.dataframe(df_history, use_container_width=True, hide_index=True)
    if st.button("🗑️ 清空账本历史记录", key="clear_all_history"):
        st.session_state.bet_history = []
        st.rerun()
else:
    st.caption("📂 暂无任何模拟下注记录，请在上方选择玩法并点击“确认下注”。")

st.divider()
st.caption("⚠️ 本娱乐模拟盘仅供亲友圈概率逻辑推演、策略预算演练与数字组合娱乐。系统不包含任何真钱交易机制，纯属公益娱乐工具。")
