import streamlit as st
import random
import math
import pandas as pd
import requests

# --- 页面配置 ---
st.set_page_config(page_title="预言家大满贯盘", page_icon="🔮", layout="centered")

# --- 🎯 v17.0 终极原生像素级紧凑正圆巧克力矩阵样式表 ---
st.markdown("""
    <style>
    /* 极致挤压手机端四周无用边距 */
    .block-container { padding-top: 0.2rem !important; padding-bottom: 0.2rem !important; padding-left: 0.2rem !important; padding-right: 0.2rem !important; }
    
    /* 预言家顶层核心防伪标志样式 */
    .prophet-logo-title {
        text-align: center !important;
        font-size: 20px !important;
        font-weight: 900 !important;
        background: linear-gradient(135deg, #ffd700, #8a2be2, #00f2fe) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        margin-top: 2px !important;
        margin-bottom: 4px !important;
        letter-spacing: 2px !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.1) !important;
    }
    
    /* 核心行动大按钮 */
    div[data-testid="stVerticalBlock"] .stButton>button { 
        background: linear-gradient(135deg, #4b0082, #8a2be2) !important; 
        color: white !important; border-radius: 25px !important; width: 100% !important; height: 42px !important; 
        font-size: 15px !important; font-weight: bold !important; border: none !important;
        box-shadow: 0px 4px 10px rgba(138,43,226,0.3);
    }
    
    /* 强控手机端所有列容器必须横排，铁板一块雷打不动 */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 2px !important;            
        margin-top: 0px !important;
        margin-bottom: 1px !important;  
        padding: 0px !important;
        width: 100% !important;
    }
    div[data-testid="stHorizontalBlock"] > div {
        flex: 1 1 0% !important; min-width: 0 !important; padding: 0 !important; margin: 0 !important;
    }
    
    /* 🔢 将 1-49 所有原生按钮强行雕刻成完美正圆纯净球体 */
    .num-ball-wrap button {
        color: white !important;
        font-weight: bold !important;
        font-size: 15px !important;
        border: none !important;
        border-radius: 50% !important;   
        width: 100% !important;
        aspect-ratio: 1 / 1 !important;  /* 高宽死锁 1:1 正圆 */
        padding: 0px !important;
        margin: 0px auto !important;
        box-shadow: 1px 1px 2px rgba(0,0,0,0.15) !important;
        display: flex !important; align-items: center !important; justify-content: center !important;
    }
    
    /* 三色球高光底色 */
    .ball-r button { background: linear-gradient(135deg, #ff4d4d, #cc0000) !important; color: white !important; }
    .ball-b button { background: linear-gradient(135deg, #4da6ff, #0066cc) !important; color: white !important; }
    .ball-g button { background: linear-gradient(135deg, #47d147, #009900) !important; color: white !important; }
    
    /* 🔥【升级核心修复】勾选后蜕变为奢华金黄立体球，强行覆盖原有颜色 */
    .ball-s button {
        background: linear-gradient(135deg, #ffd700, #ff8c00) !important;
        color: #1a1a1a !important;   /* 字体变为深黑更易阅读 */
        font-weight: 900 !important;
        border: 2px solid #ffffff !important;
        box-shadow: 0px 0px 6px #ffd700 !important;
    }
    
    /* 置顶巨型开奖号码盘样式 */
    .draw-container { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 1px; margin-bottom: 2px; justify-content: center; }
    .draw-ball { width: 38px; height: 38px; line-height: 38px; border-radius: 50%; color: white; text-align: center; font-weight: bold; font-size: 15px; box-shadow: 1px 2px 4px rgba(0,0,0,0.15); }
    .draw-red { background: linear-gradient(135deg, #ff4d4d, #cc0000); }
    .draw-blue { background: linear-gradient(135deg, #4da6ff, #0066cc); }
    .draw-green { background: linear-gradient(135deg, #47d147, #009900); }
    
    .wallet-card-mini { background: linear-gradient(135deg, #111, #222); color: #ffd700; padding: 6px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 12px; border: 1px solid #333; }
    .rank-badge { background: #8a2be2; color: white; padding: 1px 4px; border-radius: 5px; font-size: 10px; margin-left: 2px; }
    </style>
    """, unsafe_allow_html=True)

# --- 官方49码球色严格定义 ---
RED_BALLS = [1, 2, 7, 8, 12, 13, 18, 19, 23, 24, 29, 30, 34, 35, 40, 45, 46]
BLUE_BALLS = [3, 4, 9, 10, 14, 15, 20, 25, 26, 31, 36, 37, 41, 42, 47, 48]
GREEN_BALLS = [5, 6, 11, 16, 17, 21, 22, 27, 28, 32, 33, 38, 39, 43, 44, 49]

def get_ball_style(num):
    if num in RED_BALLS: return "draw-red"
    if num in BLUE_BALLS: return "draw-blue"
    return "draw-green"

def get_ball_color_class(num):
    if num in RED_BALLS: return "ball-r"
    if num in BLUE_BALLS: return "ball-b"
    return "ball-g"

# --- 初始化 Session State ---
if 'wallet' not in st.session_state: st.session_state.wallet = 10000.0
if 'bet_history' not in st.session_state: st.session_state.bet_history = []
if 'manual_ping' not in st.session_state: st.session_state.manual_ping = []
if 'manual_te' not in st.session_state: st.session_state.manual_te = []
if 'current_tab' not in st.session_state: st.session_state.current_tab = "自选平特"
if 'last_win_msg' not in st.session_state: st.session_state.last_win_msg = ""

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
                    "special": int(item.get("numbers")[6])
                })
            if live_data: return live_data
    except Exception:
        pass
    return [{"issue": "26/051", "date": "2026-05-14", "numbers": [1, 14, 19, 23, 27, 34], "special": 49}]

history_50 = fetch_live_data_50()
latest_draw = history_50[0]

# ----------------- 🔮【置顶一：预言家大厅标志】 -----------------
st.markdown('<div class="prophet-logo-title">🔮 预言家 (The Prophet) 模拟大厅</div>', unsafe_allow_html=True)

# ----------------- 🎰【置顶二：官方实时中奖彩球】 -----------------
ball_html = '<div class="draw-container">'
for num in latest_draw['numbers']:
    ball_html += f'<div class="draw-ball {get_ball_style(num)}">{num}</div>'
ball_html += f'<div class="draw-ball {get_ball_style(latest_draw["special"])}">{latest_draw["special"]}</div></div>'
st.markdown(ball_html, unsafe_allow_html=True)

# ----------------- 📅【置顶三：开奖期数与公告对齐】 -----------------
col_info1, col_info2 = st.columns(2)
with col_info1:
    st.markdown(f"<div style='font-size:12px;color:#333;font-weight:bold;margin-top:2px;'>📡 第 {latest_draw['issue']} 期开奖 ({latest_draw['date']})</div>", unsafe_allow_html=True)
with col_info2:
    st.markdown("<div style='font-size:12px;color:#8a2be2;font-weight:bold;text-align:right;'>📢 下期截止：05-19 21:15</div>", unsafe_allow_html=True)

# ----------------- 🪙【第四步：资产钱包小挂件】 -----------------
def get_player_rank(balance):
    if balance >= 50000: return "🏆神算"
    if balance >= 20000: return "💎金手"
    return "🌟预言家"

current_rank = get_player_rank(st.session_state.wallet)

col_w1, col_w2 = st.columns(2)
with col_w1:
    st.markdown(f'<div class="wallet-card-mini">🪙 余额: ${st.session_state.wallet:,.0f} <span class="rank-badge">{current_rank}</span></div>', unsafe_allow_html=True)
with col_w2:
    if st.button("🧧 充值 $5000 体验金", key="top_up_v15"):
        st.session_state.wallet += 5000.0
        st.rerun()

# ----------------- 🛠️【第五步：纯原生药丸长条玩法大厅】 -----------------
nav_cols = st.columns(4)
tabs_list = ["自选平特", "一马中特", "标准复式", "黄金胆拖"]

for idx, tab_name in enumerate(tabs_list):
    is_active = (st.session_state.current_tab == tab_name)
    display_label = f"⭐ {tab_name}" if is_active else tab_name
    with nav_cols[idx]:
        if st.button(display_label, key=f"nav_tab_{idx}"):
            st.session_state.current_tab = tab_name
            st.rerun()

st.divider()

# ----------------- 🎰【第六步：核心玩法区域分流】 -----------------

if st.session_state.current_tab == "自选平特":
    st.markdown("### 🟢 平特自选（5平码 + 1特码）")
    st.info(f"🛒 选号篮子：平码【{len(st.session_state.manual_ping)}/5】 | 特码【{len(st.session_state.manual_te)}/1】")
    
    # 区域1：平码巧克力矩阵
    st.markdown("**🟠 选 5 个【平码（正码）】：**")
    st.markdown('<div class="num-ball-wrap">', unsafe_allow_html=True)
    for row in range(7):
        cols = st.columns(7) 
        for col in range(7):
            num = row * 7 + col + 1
            if num <= 49:
                is_sel = num in st.session_state.manual_ping
                # 🔥 通过动态调整 css 容器类，已被选中的号码直接注入 ball-s 样式（变成金黄色立体球座）
                cls = "ball-s" if is_sel else get_ball_color_class(num)
                lbl = f"{num}✔" if is_sel else f"{num}"
                with cols[col]:
                    st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
                    if st.button(lbl, key=f"ping_btn_{num}"):
                        if num in st.session_state.manual_ping: st.session_state.manual_ping.remove(num)
                        elif len(st.session_state.manual_ping) < 5: st.session_state.manual_ping.append(num)
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    # 区域2：特码巧克力矩阵
    st.markdown("**🔵 选 1 个【特码（特别号码）】：**")
    st.markdown('<div class="num-ball-wrap">', unsafe_allow_html=True)
    for row in range(7):
        cols = st.columns(7)
        for col in range(7):
            num = row * 7 + col + 1
            if num <= 49:
                is_sel = num in st.session_state.manual_te
                # 🔥 同步特码盘：被选中后秒变金黄色立体球座
                cls = "ball-s" if is_sel else get_ball_color_class(num)
                lbl = f"{num}★" if is_sel else f"{num}"
                with cols[col]:
                    st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
                    if st.button(lbl, key=f"te_btn_{num}"):
                        if num in st.session_state.manual_te: st.session_state.manual_te.remove(num)
                        else: st.session_state.manual_te = [num]
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    col_o1, col_o2 = st.columns(2)
    if col_o1.button("🗑️ 清空篮子", key="clear_m"):
        st.session_state.manual_ping, st.session_state.manual_te = [], []
        st.rerun()
        
    if col_o2.button("🛒 确认下注扣款", key="submit_m"):
        intersect = set(st.session_state.manual_ping) & set(st.session_state.manual_te)
        if len(st.session_state.manual_ping) != 5 or len(st.session_state.manual_te) != 1: 
            st.error("⚠️ 数量未选满！必须在上面勾选齐 5个平码 和 1个特码 后，方可点击确认。")
        elif len(intersect) > 0: 
            st.error("⚠️ 平码与特码选了重复的数字，请检查取消重号！")
        elif st.session_state.wallet < 10: 
            st.error("❌ 余额不足！")
        else:
            st.session_state.wallet -= 10
            st.session_state.bet_history.append({"玩法": "手选单式", "所选号码": f"平:{sorted(st.session_state.manual_ping)} 特:{st.session_state.manual_te}", "单价": 10, "原始数据": {"ping": sorted(st.session_state.manual_ping), "te": st.session_state.manual_te}, "状态": "等待开奖"})
            st.session_state.manual_ping, st.session_state.manual_te = [], []
            st.success("🎉 下注成功！已同步录入底部总账记录。")
            st.rerun()

elif st.session_state.current_tab == "一马中特":
    st.markdown("### 🎯 一马中特单挑（每注$50）")
    st.markdown('<div class="num-ball-wrap">', unsafe_allow_html=True)
    for row in range(7):
        cols = st.columns(7)
        for col in range(7):
            num = row * 7 + col + 1
            if num <= 49:
                with cols[col]:
                    st.markdown(f'<div class="{get_ball_color_class(num)}">', unsafe_allow_html=True)
                    if st.button(f"{num}", key=f"one_match_{num}"):
                        if st.session_state.wallet < 50: st.error("❌ 模拟余额不足！")
                        else:
                            st.session_state.wallet -= 50
                            st.session_state.bet_history.append({"玩法": "一马中特", "所选号码": f"特码:[{num:02d}]", "单价": 50, "原始数据": {"ping": [], "te": num}, "状态": "等待开奖"})
                            st.success(f"🎉 特码【{num:02d}】成功下注！")
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.current_tab == "标准复式":
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
            st.session_state.bet_history.append({"玩法": f"复式({st.session_state.count_f}码)", "所选号码": str(f_nums), "单价": cost_f, "原始数据": {"ping": f_nums, "te": None}, "状态": "等待开奖"})
            st.success("🎉 复式注单生成成功！"); st.rerun()

elif st.session_state.current_tab == "黄金胆拖":
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
            st.session_state.bet_history.append({"玩法": "胆拖组合", "所选号码": f"胆:{dans} 拖:{tuos}", "单价": cost_dt, "原始数据": {"ping": tuos, "te": dans}, "状态": "等待开奖"})
            st.success("🎉 胆拖组合下注成功！"); st.rerun()

# --- 模拟账单存根与一键派彩系统 ---
st.divider()
st.header("🧾 模拟投注账单存根总账")

if st.session_state.bet_history:
    col_pay1, col_pay2 = st.columns(2)
    if col_pay1.button("🔥 一键对奖·自动派彩", key="auto_payout_engine"):
        with st.spinner("碰撞计算中..."):
            win_main = latest_draw["numbers"]
            win_special = latest_draw["special"]
            win_sum = 0
            for bet in st.session_state.bet_history:
                if bet["状态"] == "等待开奖":
                    raw = bet["原始数据"]
                    if bet["玩法"] in ["手选单式", "一马中特"]:
                        match_m = len(set(raw["ping"]) & set(win_main))
                        match_s = (raw["te"] == win_special)
                        if match_m == 6: st.session_state.wallet += 50000.0; win_sum += 50000; bet["状态"] = "🎉 头奖！+$50000"
                        elif match_m == 3: st.session_state.wallet += 40.0; win_sum += 40; bet["状态"] = "🎉 七奖！+$40"
                        elif match_s: 
                            p_amt = 2000.0 if bet["玩法"] == "一马中特" else 20.0
                            st.session_state.wallet += p_amt; win_sum += p_amt
                            bet["状态"] = f"🎉 特码中！+{p_amt}"
                        else: bet["状态"] = "❌ 未中奖"
                    else:
                        match_any = len(set(raw["ping"]) & set(win_main))
                        if match_any >= 3: st.session_state.wallet += 160.0; win_sum += 160; bet["状态"] = f"🎉 中码！+$160"
                        else: bet["状态"] = "❌ 未中奖"
            st.session_state.last_win_msg = f"🔮【预言家喜报】战报：本轮结算结算斩获模拟金 HK$ {win_sum:,.0f}！💰 当前总资产：HK$ {st.session_state.wallet:,.0f}！🔥"
            st.rerun()
            
    if col_pay2.button("🗑️ 清空账本历史记录", key="clear_all_v11"):
        st.session_state.bet_history = []
        st.session_state.last_win_msg = ""
        st.rerun()
    df_history = pd.DataFrame(st.session_state.bet_history)
    st.dataframe(df_history, use_container_width=True, hide_index=True)
    if st.session_state.last_win_msg:
        st.text_area("📋 【中奖喜报】", value=st.session_state.last_win_msg, height=90)
else:
    st.caption("📂 暂无下注记录。")

# --- 📅 历史流水对账明细 ---
with st.expander(f"📅 点击展开/查阅全网最新 50 期开奖真实历史流水记录"):
    for draw in history_50:
        st.markdown(f"""
        <div style="padding: 5px 0; border-bottom: 1px solid #f1f5f9; font-size:13px;">
            <span style="color:#4b0082; font-weight:bold;">第{draw['issue']}期</span> ({draw['date']}) 
            正码: {', '.join(f'{n:02d}' for n in draw['numbers'])} | <span style="color:#dc143c; font-weight:bold;">特别号: {draw['special']:02d}</span>
        </div>
        """, unsafe_allow_html=True)
