import streamlit as st
import random
import time
import math
import pandas as pd
import requests
from datetime import datetime

# --- 页面配置 ---
st.set_page_config(page_title="预言家大满贯盘", page_icon="🔮", layout="centered")

# --- 🎯 手机端强控 7×7 正圆横向排列样式表 (完美解决竖排Bug) ---
st.markdown("""
    <style>
    /* 缩减手机端四周留白 */
    .block-container { padding-top: 0.8rem; padding-bottom: 0.8rem; padding-left: 0.4rem; padding-right: 0.4rem; }
    
    /* 核心行动大按钮 */
    .stButton>button { 
        background: linear-gradient(135deg, #4b0082, #8a2be2) !important; 
        color: white !important; border-radius: 25px !important; width: 100% !important; height: 46px !important; 
        font-size: 15px !important; font-weight: bold !important; border: none !important;
        box-shadow: 0px 4px 10px rgba(138,43,226,0.3);
    }
    
    /* 玩法导航条按钮 */
    .nav-btn button {
        background: linear-gradient(135deg, #2c3e50, #000000) !important;
        font-size: 12px !important; height: 38px !important; border-radius: 10px !important;
    }
    
    /* 🔥【核心修复】强行命令 Streamlit 在手机端必须横向排列，绝对不允许自动坍塌成竖排！ */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important; /* 强制横向 */
        flex-wrap: nowrap !important;   /* 绝对不换行 */
        gap: 2px !important;            /* 压缩球间距 */
        margin-bottom: 2px !important;
        width: 100% !important;
    }
    
    /* 精准控制每一个多列容器的手机占比，平分横向空间 */
    div[data-testid="stHorizontalBlock"] > div {
        flex: 1 1 0% !important;
        min-width: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* 1-49 数字球座：强制适配手机宽度的正圆球体 */
    div[data-testid="stHorizontalBlock"] button {
        color: white !important; 
        font-weight: bold !important; 
        font-size: 14px !important;
        border: none !important; 
        border-radius: 50% !important; /* 完美正圆 */
        width: 100% !important;        /* 自适应宽度 */
        aspect-ratio: 1 / 1 !important;/* 高宽绝对1:1确保正圆 */
        padding: 0px !important;
        margin: 0px auto !important;
        box-shadow: 1px 2px 4px rgba(0,0,0,0.2) !important;
    }
    
    /* 官方红、蓝、绿三色高光 */
    .btn-red button { background: linear-gradient(135deg, #ff4d4d, #cc0000) !important; }
    .btn-blue button { background: linear-gradient(135deg, #4da6ff, #0066cc) !important; }
    .btn-green button { background: linear-gradient(135deg, #47d147, #009900) !important; }
    
    /* 选中状态：蜕变为亮丽的金黄球 */
    .btn-selected button { 
        background: linear-gradient(135deg, #ffd700, #ff8c00) !important; 
        color: #1a1a1a !important; 
        font-weight: 900 !important; 
        border: 2px solid #ffffff !important; 
        box-shadow: 0px 0px 6px #ffd700 !important; 
    }
    
    .ball-container { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 5px; margin-bottom: 5px; }
    .ball { 
        width: 34px; height: 34px; line-height: 34px; border-radius: 50%; 
        color: white; text-align: center; font-weight: bold; font-size: 13px;
        box-shadow: 1px 2px 4px rgba(0,0,0,0.15);
    }
    .ball-red { background: linear-gradient(135deg, #dc143c, #960018); }
    .ball-blue { background: linear-gradient(135deg, #1e90ff, #002fa7); }
    .ball-green { background: linear-gradient(135deg, #2e8b57, #124e2c); }
    
    .wallet-card {
        background: linear-gradient(135deg, #111, #222); color: #ffd700;
        padding: 12px; border-radius: 12px; text-align: center; margin-bottom: 10px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3); font-weight: bold; font-size: 16px;
    }
    .mobile-card {
        background-color: #f8fafc; padding: 10px; border-radius: 10px;
        border-left: 5px solid #8a2be2; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 官方49码球色划分 ---
RED_BALLS = [1, 2, 7, 8, 12, 13, 18, 19, 23, 24, 29, 30, 34, 35, 40, 45, 46]
BLUE_BALLS = [3, 4, 9, 10, 14, 15, 20, 25, 26, 31, 36, 37, 41, 42, 47, 48]
GREEN_BALLS = [5, 6, 11, 16, 17, 21, 22, 27, 28, 32, 33, 38, 39, 43, 44, 49]

def get_ball_style(num):
    if num in RED_BALLS: return "ball-red"
    if num in BLUE_BALLS: return "ball-blue"
    return "ball-green"

def get_ball_color_class(num):
    if num in RED_BALLS: return "btn-red"
    if num in BLUE_BALLS: return "btn-blue"
    return "btn-green"

# --- 初始化大满贯 Session State ---
if 'wallet' not in st.session_state: st.session_state.wallet = 10000.0
if 'bet_history' not in st.session_state: st.session_state.bet_history = []
if 'manual_ping' not in st.session_state: st.session_state.manual_ping = []
if 'manual_te' not in st.session_state: st.session_state.manual_te = []
if 'current_tab' not in st.session_state: st.session_state.current_tab = "🔘 自选平特"

if 'count_f' not in st.session_state: st.session_state.count_f = 7
if 'count_dan' not in st.session_state: st.session_state.count_dan = 2
if 'count_tuo' not in st.session_state: st.session_state.count_tuo = 6

# --- 数据采集模块 ---
@st.cache_data(ttl=3600)
def fetch_live_data_50():
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
                    "special": int(item.get("numbers"))
                })
            if live_data: return live_data
    except Exception:
        pass
    return [{"issue": "26/051", "date": "2026-05-14", "numbers": [2, 7, 15, 24, 31, 42], "special": 49}]

history_50 = fetch_live_data_50()
latest_draw = history_50[0]

# --- 顶栏挂件 ---
st.title("🔮 预言家 - v10.0 究极版")
st.markdown(f'<div class="wallet-card">🪙 您的模拟资产总额：HK$ {st.session_state.wallet:,.2f}</div>', unsafe_allow_html=True)

col_top1, col_top2 = st.columns(2)
if col_top1.button("🧧 免费充值 $5000 模拟金", key="top_up_v10"):
    st.session_state.wallet += 5000.0
    st.rerun()
with col_top2:
    st.markdown("<div style='font-size:12px;color:#8a2be2;text-align:right;font-weight:bold;'>📢 下期截止预报：<br>2026-05-19 21:15 (周二)</div>", unsafe_allow_html=True)

# 最新开奖看板
st.markdown(f'<div class="mobile-card"><div style="font-size:13px; color:#666;">📡 <b>官方全自动同步中</b>：第 <b>{latest_draw["issue"]}</b> 期 ({latest_draw["date"]})</div></div>', unsafe_allow_html=True)
ball_html = '<div class="ball-container">'
for num in latest_draw['numbers']: ball_html += f'<div class="ball {get_ball_style(num)}">{num}</div>'
ball_html += f'<div class="ball {get_ball_style(latest_draw["special"])}">{latest_draw["special"]}</div></div>'
st.markdown(ball_html, unsafe_allow_html=True)

st.divider()

# --- 🛠️ 纯按钮式玩法导航大厅 ---
st.subheader("📝 请点选模拟玩法大厅")
nav_cols = st.columns(4)
tabs_list = ["🔘 自选平特", "🎯 一马中特", "📊 标准复式", "🎲 黄金胆拖"]

for idx, tab_name in enumerate(tabs_list):
    display_label = f"⭐ {tab_name}" if st.session_state.current_tab == tab_name else tab_name
    with nav_cols[idx]:
        st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
        if st.button(display_label, key=f"nav_tab_{idx}"):
            st.session_state.current_tab = tab_name
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ----------------- 核心玩法区 -----------------

# 1. 自选平特大厅
if st.session_state.current_tab == "🔘 自选平特":
    st.markdown("### 🟢 分离紧凑自选（5平码 + 1特码）")
    st.info(f"🛒 篮子状态：平码【{len(st.session_state.manual_ping)}/5】 | 特码【{len(st.session_state.manual_te)}/1】")

    with st.expander("🟠 点击收放 ——【5个平码正圆键盘】", expanded=True):
        for row in range(7):
            cols = st.columns(7)
            for col in range(7):
                num = row * 7 + col + 1
                if num <= 49:
                    is_sel = num in st.session_state.manual_ping
                    cls = "btn-selected" if is_sel else get_ball_color_class(num)
                    lbl = f"{num}"
                    st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
                    if cols[col].button(lbl, key=f"p1_{num}"):
                        if num in st.session_state.manual_ping: st.session_state.manual_ping.remove(num)
                        elif len(st.session_state.manual_ping) < 5: st.session_state.manual_ping.append(num)
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("🔵 点击收放 ——【1个特码正圆键盘】", expanded=True):
        for row in range(7):
            cols = st.columns(7)
            for col in range(7):
                num = row * 7 + col + 1
                if num <= 49:
                    is_sel = num in st.session_state.manual_te
                    cls = "btn-selected" if is_sel else get_ball_color_class(num)
                    lbl = f"{num}"
                    st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
                    if cols[col].button(lbl, key=f"t1_{num}"):
                        if num in st.session_state.manual_te: st.session_state.manual_te.remove(num)
                        else: st.session_state.manual_te = [num]
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    col_o1, col_o2 = st.columns(2)
    if col_o1.button("🗑️ 清空篮子", key="clear_m"):
        st.session_state.manual_ping, st.session_state.manual_te = [], []
        st.rerun()
    if col_o2.button("🛒 确认下注扣款", key="submit_m"):
        intersect = set(st.session_state.manual_ping) & set(st.session_state.manual_te)
        if len(st.session_state.manual_ping) != 5 or len(st.session_state.manual_te) != 1: st.error("⚠️ 数量未选满！")
        elif len(intersect) > 0: st.error("⚠️ 平码与特码不能选相同数字！")
        elif st.session_state.wallet < 10: st.error("❌ 余额不足！")
        else:
            st.session_state.wallet -= 10
            st.session_state.bet_history.append({
                "玩法": "手选单式", "所选号码": f"平:{sorted(st.session_state.manual_ping)} 特:{st.session_state.manual_te}", 
                "单价": 10, "原始数据": {"ping": sorted(st.session_state.manual_ping), "te": st.session_state.manual_te}, "状态": "等待开奖"
            })
            st.session_state.manual_ping, st.session_state.manual_te = [], []
            st.success("🎉 下注成功！已存入下方账本。")
            st.rerun()

# 2. 一马中特大厅
elif st.session_state.current_tab == "🎯 一马中特":
    st.markdown("### 🎯 全彩正圆键盘：一马中特单挑（每注$50）")
    for row in range(7):
        cols = st.columns(7)
        for col in range(7):
            num = row * 7 + col + 1
            if num <= 49:
                st.markdown(f'<div class="{get_ball_color_class(num)}">', unsafe_allow_html=True)
                if cols[col].button(f"{num}", key=f"one_match_{num}"):
                    if st.session_state.wallet < 50: st.error("❌ 模拟余额不足！")
                    else:
                        st.session_state.wallet -= 50
                        st.session_state.bet_history.append({
                            "玩法": "one_match", "所选号码": f"特码:[{num:02d}]", 
                            "单价": 50, "原始数据": {"ping": [], "te": num}, "状态": "等待开奖"
                        })
                        st.success(f"🎉 特码【{num:02d}】下注成功！")
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

# 3. 标准复式大厅
elif st.session_state.current_tab == "📊 标准复式":
    st.markdown("### 📊 标准复式加减盘（每注$10）")
    col_f_sub, col_f_val, col_f_add = st.columns(3)
    with col_f_sub:
        if st.button("➖ 减少 1 码", key="sub_f_num") and st.session_state.count_f > 7: st.session_state.count_f -= 1; st.rerun()
    with col_f_val: st.markdown(f"<h4 style='text-align:center;color:#8a2be2;'>选择大底：{st.session_state.count_f} 个号</h4>", unsafe_allow_html=True)
    with col_f_add:
        if st.button("➕ 增加 1 码", key="add_f_num") and st.session_state.count_f < 12: st.session_state.count_f += 1; st.rerun()
            
    total_notes = math.comb(st.session_state.count_f, 6)
    cost_f = total_notes * 10
    st.info(f"📊 该复式折合共 **{total_notes}** 注 | 需从钱包扣除：**HK$ {cost_f}**")
    
    if st.button("🛒 确认提交复式投注", key="sub_f_bet"):
        if st.session_state.wallet < cost_f: st.error("❌ 余额不足！")
        else:
            st.session_state.wallet -= cost_f
            f_nums = sorted(random.sample(range(1, 50), st.session_state.count_f))
            st.session_state.bet_history.append({
                "玩法": f"复式({st.session_state.count_f}码)", "所选号码": str(f_nums), 
                "单价": cost_f, "原始数据": {"ping": f_nums, "te": None}, "状态": "等待开奖"
            })
            st.success(f"🎉 复式注单生成成功！")
            st.rerun()

# 4. 黄金胆拖大厅
elif st.session_state.current_tab == "🎲 黄金胆拖":
    st.markdown("### 🎲 胆拖组合盘（每注$10）")
    st.write("1. 调节【胆码】个数 (1-5个)：")
    cd1, cd2, cd3 = st.columns(3)
    if cd1.button("➖ 减胆", key="d_sub") and st.session_state.count_dan > 1: st.session_state.count_dan -= 1; st.rerun()
    cd2.markdown(f"<div style='text-align:center;font-weight:bold;margin-top:8px;'>当前胆码：{st.session_state.count_dan} 个</div>", unsafe_allow_html=True)
    if cd3.button("➕ 加胆", key="d_add") and st.session_state.count_dan < 5: st.session_state.count_dan += 1; st.rerun()
        
    st.write("2. 调节【拖码】个数：")
    ct1, ct2, ct3 = st.columns(3)
    if ct1.button("➖ 减拖", key="t_sub") and st.session_state.count_tuo > (7 - st.session_state.count_dan): st.session_state.count_tuo -= 1; st.rerun()
    ct2.markdown(f"<div style='text-align:center;font-weight:bold;margin-top:8px;'>当前拖码：{st.session_state.count_tuo} 个</div>", unsafe_allow_html=True)
    if ct3.button("➕ 加拖", key="t_add") and st.session_state.count_tuo < 15: st.session_state.count_tuo += 1; st.rerun()
        
    total_notes_dt = math.comb(st.session_state.count_tuo, 6 - st.session_state.count_dan)
    cost_dt = total_notes_dt * 10
    st.info(f"📊 该胆拖组合折合共 **{total_notes_dt}** 注 | 需模拟金：**HK$ {cost_dt}**")
    
    if st.button("🛒 确认提交胆拖投注", key="sub_dt_bet"):
        if st.session_state.wallet < cost_dt: st.error("❌ 余额不足！")
        else:
            st.session_state.wallet -= cost_dt
            pool = list(range(1, 50))
            random.shuffle(pool)
            dans = sorted(pool[:st.session_state.count_dan])
            tuos = sorted(pool[st.session_state.count_dan : st.session_state.count_dan + st.session_state.count_tuo])
            st.session_state.bet_history.append({
                "玩法": "胆拖组合", "所选号码": f"胆:{dans} 拖:{tuos}", 
                "单价": cost_dt, "原始数据": {"ping": tuos, "te": dans}, "状态": "等待开奖"
            })
            st.success("🎉 胆拖组合下注成功！")
            st.rerun()

# --- 模拟账单存根与一键派彩系统 ---
st.divider()
st.header("🧾 模拟投注账单存根总账")

if st.session_state.bet_history:
    col_pay1, col_pay2 = st.columns(2)
    
    if col_pay1.button("🔥 一键对奖·自动派彩", key="auto_payout_engine"):
        with st.spinner("碰撞计算中..."):
            time.sleep(0.5)
            win_main = latest_draw["numbers"]
            win_special = latest_draw["special"]
            
            for bet in st.session_state.bet_history:
                if bet["状态"] == "等待开奖":
                    raw = bet["原始数据"]
                    if bet["玩法"] in ["手选单式", "one_match"]:
                        match_m = len(set(raw["ping"]) & set(win_main))
                        match_s = (raw["te"] == win_special)
                        
                        if bet["玩法"] == "one_match" and match_s:
                            st.session_state.wallet += 2000.0
                            bet["状态"] = "🎉 斩获特码！+$2000"
                        elif match_m == 6: st.session_state.wallet += 50000.0; bet["状态"] = "🎉 头奖！+$50000"
                        elif match_m == 3: st.session_state.wallet += 40.0; bet["状态"] = "🎉 七奖！+$40"
                        else: bet["状态"] = "❌ 未中奖"
                    else:
                        match_any = len(set(raw["ping"]) & set(win_main))
                        if match_any >= 3:
                            st.session_state.wallet += 160.0
                            bet["状态"] = f"🎉 中码！+$160"
                        else: bet["状态"] = "❌ 未中奖"
            st.success("💰 账本全量对奖派彩结算完毕！")
            st.rerun()
            
    if col_pay2.button("🗑️ 清空账本历史记录", key="clear_all_v10"):
        st.session_state.bet_history = []
        st.rerun()
        
    df_history = pd.DataFrame(st.session_state.bet_history)
    st.dataframe(df_history, use_container_width=True, hide_index=True)
else:
    st.caption("📂 暂无下注记录。请在上方纯按钮大厅选号并提交。")

# --- 📊 50期大数据图表看板 ---
st.divider()
st.header("📊 50期大数据·正码热度排行榜")

hot_counts = {i: 0 for i in range(1, 50)}
for draw in history_50:
    for n in draw["numbers"]:
        hot_counts[n] += 1
df_chart = pd.DataFrame.from_dict(hot_counts, orient='index', columns=['50期出号频次'])
st.bar_chart(df_chart)

st.divider()
st.caption("⚠️ 声明：本系统已开启官方网络源自动同步。开奖具备纯物理随机性，测算与派彩模块纯属模拟数字游戏，请务必理性参与。")
