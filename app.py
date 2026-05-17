import streamlit as st
import random
import time
import math
import pandas as pd
import requests
from datetime import datetime

# --- 页面配置 ---
st.set_page_config(page_title="预言家大满贯盘", page_icon="🔮", layout="centered")

# --- 🎯 v11.5 终极首屏开奖置顶与极致无缝巧克力方阵 UI 样式表 ---
st.markdown("""
    <style>
    .block-container { padding-top: 0.4rem; padding-bottom: 0.4rem; padding-left: 0.2rem; padding-right: 0.2rem; }
    
    /* 核心行动大按钮 */
    .stButton>button { 
        background: linear-gradient(135deg, #4b0082, #8a2be2) !important; 
        color: white !important; border-radius: 25px !important; width: 100% !important; height: 44px !important; 
        font-size: 15px !important; font-weight: bold !important; border: none !important;
        box-shadow: 0px 4px 10px rgba(138,43,226,0.3);
    }
    
    /* 原生 HTML 玩法导航大厅卡片样式 */
    .html-nav-container { display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: 3px !important; width: 100% !important; max-width: 360px !important; margin: 0 auto 10px auto !important; padding: 0 !important; }
    .html-nav-btn {
        flex: 1 1 0% !important; height: 38px !important; border-radius: 8px !important;
        background: linear-gradient(135deg, #2c3e50, #1a252f) !important; color: #cccccc !important;
        font-size: 11px !important; font-weight: bold !important; display: flex !important; align-items: center !important; justify-content: center !important;
        border: 1px solid #34495e !important; text-decoration: none !important; cursor: pointer !important; -webkit-tap-highlight-color: transparent !important;
    }
    .html-nav-active { background: linear-gradient(135deg, #ffd700, #ff8c00) !important; color: #1a1a1a !important; border: 1px solid #ffffff !important; font-weight: 900 !important; box-shadow: 0px 0px 6px rgba(255,215,0,0.4) !important; }
    
    /* 原生 HTML 1-49 巧克力无缝矩阵 */
    .html-grid-matrix { display: flex !important; flex-direction: row !important; flex-wrap: wrap !important; justify-content: flex-start !important; gap: 2px !important; row-gap: 2px !important; width: 100% !important; max-width: 350px !important; margin: 0 auto !important; padding: 2px 0 !important; }
    .html-ball-btn {
        flex: 0 0 calc((100% - 12px) / 7) !important; aspect-ratio: 1 / 1 !important; color: white !important; font-size: 14px !important; font-weight: bold !important; border: none !important; border-radius: 50% !important;
        display: flex !important; align-items: center !important; justify-content: center !important; box-shadow: 1px 1px 2px rgba(0,0,0,0.15) !important; cursor: pointer !important; -webkit-tap-highlight-color: transparent !important;
    }
    .hb-red { background: linear-gradient(135deg, #ff4d4d, #cc0000) !important; }
    .hb-blue { background: linear-gradient(135deg, #4da6ff, #0066cc) !important; }
    .hb-green { background: linear-gradient(135deg, #47d147, #009900) !important; }
    .hb-selected { background: linear-gradient(135deg, #ffd700, #ff8c00) !important; color: #1a1a1a !important; font-weight: 900 !important; border: 1.5px solid #ffffff !important; box-shadow: 0px 0px 5px #ffd700 !important; }
    
    /* 置顶巨型开奖号布局 */
    .ball-container { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 5px; margin-bottom: 5px; justify-content: center; }
    .ball { width: 44px; height: 44px; line-height: 44px; border-radius: 50%; color: white; text-align: center; font-weight: bold; font-size: 16px; box-shadow: 1px 3px 6px rgba(0,0,0,0.2); }
    .ball-red { background: linear-gradient(135deg, #ff4d4d, #cc0000); }
    .ball-blue { background: linear-gradient(135deg, #4da6ff, #0066cc); }
    .ball-green { background: linear-gradient(135deg, #47d147, #009900); }
    
    .wallet-card-mini { background: linear-gradient(135deg, #111, #222); color: #ffd700; padding: 8px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 13px; border: 1px solid #333; }
    .rank-badge { background: #8a2be2; color: white; padding: 1px 6px; border-radius: 8px; font-size: 10px; margin-left: 3px; }
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

def get_html_ball_class(num):
    if num in RED_BALLS: return "hb-red"
    if num in BLUE_BALLS: return "hb-blue"
    return "hb-green"

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
                    "special": int(item.get("numbers"))
                })
            if live_data: return live_data
    except Exception:
        pass
    return [{"issue": "26/051", "date": "2026-05-14", "numbers": [2, 7, 15, 24, 31, 42], "special": 49}]

history_50 = fetch_live_data_50()
latest_draw = history_50[0]

# ----------------- 📡 🔥【核心优化：开奖结果绝对置顶】 -----------------
st.markdown(f"<div style='font-size:14px;color:#555;font-weight:bold;margin-bottom:2px;text-align:center;'>📡 官方同步最新开奖：第 {latest_draw['issue']} 期 ({latest_draw['date']})</div>", unsafe_allow_html=True)

# 渲染巨型开奖号码球
ball_html = '<div class="ball-container">'
for num in latest_draw['numbers']:
    ball_html += f'<div class="ball {get_ball_style(num)}">{num}</div>'
ball_html += f'<div class="ball {get_ball_style(latest_draw["special"])}">{latest_draw["special"]}</div></div>'
st.markdown(ball_html, unsafe_allow_html=True)

st.write("")

# ----------------- 📡 高级接口事件捕获系统 -----------------
click_event = st.query_params

if "set_tab" in click_event:
    st.session_state.current_tab = str(click_event.get("set_tab"))
    st.query_params.clear(); st.rerun()

if "click_ping" in click_event:
    clicked_num = int(click_event.get("click_ping"))
    if clicked_num in st.session_state.manual_ping: st.session_state.manual_ping.remove(clicked_num)
    elif len(st.session_state.manual_ping) < 5: st.session_state.manual_ping.append(clicked_num)
    st.query_params.clear(); st.rerun()

if "click_te" in click_event:
    clicked_num = int(click_event.get("click_te"))
    if clicked_num in st.session_state.manual_te: st.session_state.manual_te.remove(clicked_num)
    else: st.session_state.manual_te = [clicked_num]
    st.query_params.clear(); st.rerun()

if "click_one" in click_event:
    clicked_num = int(click_event["click_one"])
    if st.session_state.wallet < 50: st.error("❌ 模拟余额不足！")
    else:
        st.session_state.wallet -= 50
        st.session_state.bet_history.append({"玩法": "一马中特", "所选号码": f"特码:[{clicked_num:02d}]", "单价": 50, "原始数据": {"ping": [], "te": clicked_num}, "状态": "等待开奖"})
        st.toast(f"🎉 特码【{clicked_num:02d}】成功下注！")
    st.query_params.clear(); st.rerun()


# --- 🪙 压缩版紧凑资产监控挂件（左右双列缩减垂直高度） ---
def get_player_rank(balance):
    if balance >= 50000: return "🏆神算"
    if balance >= 20000: return "💎金手"
    return "🌟预言家"

current_rank = get_player_rank(st.session_state.wallet)

col_w1, col_w2 = st.columns(2)
with col_w1:
    st.markdown(f'<div class="wallet-card-mini">🪙 余额: ${st.session_state.wallet:,.0f} <span class="rank-badge">{current_rank}</span></div>', unsafe_allow_html=True)
with col_w2:
    if st.button("🧧 充值 $5000 体验金", key="top_up_v11"):
        st.session_state.wallet += 5000.0
        st.rerun()

# --- 🛠️ 原生 HTML 玩法导航大厅 ---
tabs_map = {"自选平特": "自选平特", "一马中特": "一马中特", "标准复式": "标准复式", "黄金胆拖": "黄金胆拖"}
html_nav = '<div class="html-nav-container">'
for key_name, display_name in tabs_map.items():
    is_active = (st.session_state.current_tab == key_name)
    active_cls = "html-nav-active" if is_active else ""
    html_nav += f'<a href="?set_tab={key_name}" target="_self" class="html-nav-btn {active_cls}" style="text-decoration:none;">{display_name}</a>'
html_nav += '</div>'
st.markdown(html_nav, unsafe_allow_html=True)

# ----------------- 核心玩法区 -----------------
st.markdown('<div class="num-matrix-container">', unsafe_allow_html=True)

if st.session_state.current_tab == "自选平特":
    st.markdown("### 🟢 分离自选（5平码 + 1特码）")
    st.info(f"🛒 篮子状态：平码【{len(st.session_state.manual_ping)}/5】 | 特码【{len(st.session_state.manual_te)}/1】")
    st.markdown("**🟠 选 5 个【平码（正码）】：**")
    html_ping_matrix = '<div class="html-grid-matrix">'
    for num in range(1, 50):
        is_sel = num in st.session_state.manual_ping
        cls = "hb-selected" if is_sel else get_html_ball_class(num)
        html_ping_matrix += f'<a href="?click_ping={num}" target="_self" class="html-ball-btn {cls}" style="text-decoration:none;">{num}</a>'
    st.markdown(html_ping_matrix + '</div>', unsafe_allow_html=True)
    st.write("")
    st.markdown("**🔵 选 1 个【特码（特别号码）】：**")
    html_te_matrix = '<div class="html-grid-matrix">'
    for num in range(1, 50):
        is_sel = num in st.session_state.manual_te
        cls = "hb-selected" if is_sel else get_html_ball_class(num)
        html_te_matrix += f'<a href="?click_te={num}" target="_self" class="html-ball-btn {cls}" style="text-decoration:none;">{num}</a>'
    st.markdown(html_te_matrix + '</div>', unsafe_allow_html=True)
    st.write("")
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
            st.session_state.bet_history.append({"玩法": "手选单式", "所选号码": f"平:{sorted(st.session_state.manual_ping)} 特:{st.session_state.manual_te}", "单价": 10, "原始数据": {"ping": sorted(st.session_state.manual_ping), "te": st.session_state.manual_te}, "状态": "等待开奖"})
            st.session_state.manual_ping, st.session_state.manual_te = [], []
            st.success("🎉 下注成功！")
            st.rerun()

elif st.session_state.current_tab == "一马中特":
    st.markdown("### 🎯 巧克力正圆网格：一马中特单挑（每注$50）")
    html_one_matrix = '<div class="html-grid-matrix">'
    for num in range(1, 50):
        cls = get_html_ball_class(num)
        html_one_matrix += f'<a href="?click_one={num}" target="_self" class="html-ball-btn {cls}" style="text-decoration:none;">{num}</a>'
    st.markdown(html_one_matrix + '</div>', unsafe_allow_html=True)

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

st.markdown('</div>', unsafe_allow_html=True)

# --- 模拟账单存根与一键派彩系统 ---
st.divider()
st.header("🧾 模拟投注账单存根总账")

if st.session_state.bet_history:
    col_pay1, col_pay2 = st.columns(2)
    if col_pay1.button("🔥 一键对奖·自动派彩", key="auto_payout_engine"):
        with st.spinner("数据对冲 Axel 中..."):
            time.sleep(0.5)
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
            
            st.session_state.last_win_msg = f"🔮【预言家娱乐模拟盘·喜报】\n本轮共计斩获模拟体验金：HK$ {win_sum:,.0f}！\n💰 当前荣誉身价：HK$ {st.session_state.wallet:,.0f}！🔥"
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

# --- 大数据直方图 ---
st.divider()
st.header("📊 50期正码热度排行榜")
hot_counts = {i: 0 for i in range(1, 50)}
for draw in history_50:
    for n in draw["numbers"]: hot_counts[n] += 1
df_chart = pd.DataFrame(pd.Series(hot_counts), columns=['50期出号频次'])
st.bar_chart(df_chart)
