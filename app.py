import streamlit as st
import random
import time
import math
import pandas as pd
import requests
from datetime import datetime

# --- 页面配置 ---
st.set_page_config(page_title="预言家娱乐模拟盘", page_icon="🎰", layout="centered")

# --- 手机移动端样式适配 (高度还原绿色投注站风格) ---
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
            item = response.json().get("data", [])[0]
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

# 充值体验金小彩蛋
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
bet_tabs = st.tabs(["📌 单式自选/机选", "📊 专业复式盘", "🎯 黄金胆拖盘"])

# 1. 单式投注盘
with bet_tabs[0]:
    st.markdown("### 🟢 单式选号大厅")
    input_mode = st.radio("选号模式", ["智能机选号码", "手动填写心水码"], horizontal=True)
    bet_price = st.radio("单式下注单价", ["全注 ($10)", "半注 ($5)"], horizontal=True, key="p1")
    cost_per_note = 10 if "全注" in bet_price else 5
    
    if input_mode == "智能机选号码":
        notes_to_gen = st.slider("想要机选下注几注？", 1, 5, 1)
        total_cost = notes_to_gen * cost_per_note
        st.warning(f"预计本次模拟投注将从钱包扣除：HK$ {total_cost}")
        
        if st.button("确认提交机选下注"):
            if st.session_state.wallet < total_cost:
                st.error("❌ 抱歉，您的模拟钱包余额不足，请先免费充值！")
            else:
                st.session_state.wallet -= total_cost
                st.success("🎉 模拟投注出票成功！已记入下方存根。")
                for _ in range(notes_to_gen):
                    nums = sorted(random.sample(range(1, 50), 6))
                    st.session_state.bet_history.append({"时间": datetime.now().strftime("%M:%S"), "玩法": "单式机选", "所选号码": str(nums), "模拟下注金额": f"${cost_per_note}"})
                st.rerun()
                
    else:
        user_code = st.text_input("请输入6个号码（用空格或逗号隔开）", value="1 8 14 23 30 49")
        if st.button("确认提交自选下注"):
            try:
                raw_nums = [int(x) for x in user_code.replace(",", " ").split() if x.strip()]
                clean_nums = sorted(list(set(raw_nums)))
                if len(clean_nums) != 6 or any(n < 1 or n > 49 for n in clean_nums):
                    st.error("⚠️ 格式错误：必须输入6个不重复的 1-49 之间的数字！")
                elif st.session_state.wallet < cost_per_note:
                    st.error("❌ 余额不足！")
                else:
                    st.session_state.wallet -= cost_per_note
                    st.session_state.bet_history.append({"时间": datetime.now().strftime("%M:%S"), "玩法": "单式自选", "所选号码": str(clean_nums), "模拟下注金额": f"${cost_per_note}"})
                    st.success(f"👍 自选注单提交成功！号码为：{clean_nums}")
                    st.rerun()
            except Exception:
                st.error("请输入合法的纯数字组合！")

# 2. 复式投注盘
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
            st.session_state.bet_history.append({"时间": datetime.now().strftime("%M:%S"), "玩法": f"复式({num_count}码)", "所选号码": str(f_nums), "模拟下注金额": f"${cost_f}"})
            st.success(f"🎉 复式注单下注成功！大底号码：{f_nums}")
            st.rerun()

# 3. 胆拖投注盘
with bet_tabs[2]:
    st.markdown("### 🟢 胆拖稳健策略盘")
    dan_count = st.slider("胆码个数（核心死码）", 1, 5, 2)
    tuo_count = st.slider("拖码个数（配脚范围）", 7-dan_count, 15, 6)
    total_notes_dt = math.comb(tuo_count, 6 - dan_count)
    bet_price_dt = st.radio("胆拖下注单价", ["全注 ($10)", "半注 ($5)"], horizontal=True, key="p3")
    cost_dt = total_notes_dt * (10 if "全注" in bet_price_dt else 5)
    
    st.info(f"📊 该胆拖组合折算为 **{total_notes_dt}** 注 | 总计需模拟金：**HK$ {cost_dt}**")
    
    if st.button("确认提交胆拖投注"):
        if st.session_state.wallet < cost_dt:
            st.error("❌ 余额不足！")
        else:
            st.session_state.wallet -= cost_dt
            pool = list(range(1, 50))
            random.shuffle(pool)
            dans = sorted(pool[:dan_count])
            tuos = sorted(pool[dan_count:dan_count+tuo_count])
            
            st.session_state.bet_history.append({"时间": datetime.now().strftime("%M:%S"), "玩法": f"胆拖({dan_count}胆{tuo_count}拖)", "所选号码": f"胆:{dans} | 拖:{tuos}", "模拟下注金额": f"${cost_dt}"})
            st.success("🎉 模拟胆拖注单已成功打印出票！")
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
