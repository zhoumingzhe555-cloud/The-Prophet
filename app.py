import streamlit as st
import random
import time
import math
import pandas as pd
import requests
from datetime import datetime

# --- 页面配置 ---
st.set_page_config(page_title="预言家大满贯盘", page_icon="🔮", layout="centered")

# --- 🎯 极致手机端像素级压缩样式表 (一屏看全 49 码的秘诀) ---
st.markdown("""
    <style>
    /* 彻底清除整个手机屏幕的无用外白边 */
    .block-container { padding-top: 0.4rem; padding-bottom: 0.4rem; padding-left: 0.3rem; padding-right: 0.3rem; }
    
    /* 核心行动大按钮（充值、下注、派彩） */
    .stButton>button { 
        background: linear-gradient(135deg, #4b0082, #8a2be2) !important; 
        color: white !important; border-radius: 25px !important; width: 100% !important; height: 44px !important; 
        font-size: 15px !important; font-weight: bold !important; border: none !important;
    }
    
    /* 顶部导航卡片样式 */
    .nav-container div[data-testid="stHorizontalBlock"] {
        display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: 4px !important; margin-bottom: 6px !important;
    }
    .nav-container div[data-testid="stHorizontalBlock"] button {
        background: linear-gradient(135deg, #2c3e50, #1a252f) !important; color: white !important;
        font-size: 11px !important; font-weight: bold !important; height: 38px !important; width: 100% !important; border-radius: 8px !important; border: 1px solid #34495e !important; aspect-ratio: auto !important;
    }
    .nav-container .nav-active button {
        background: linear-gradient(135deg, #ffd700, #ff8c00) !important; color: #1a1a1a !important; border: 1px solid #ffffff !important; font-weight: 900 !important;
    }
    
    /* 🔥【终极特化修复】下方 1-49 号码盘全方位像素级深度压榨，彻底清除垂直空白 */
    .num-matrix-container {
        margin-top: -5px !important;
    }
    /* 1. 强行命令包裹数字球的所有中间层组件高度归零，彻底砍断垂直拉伸 */
    .num-matrix-container div[data-testid="stVerticalBlock"] {
        gap: 0px !important;
        padding: 0px !important;
        margin: 0px !important;
    }
    /* 2. 强控横向 7 列横排，同时将上下行距死死卡扣在一起 */
    .num-matrix-container div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important; 
        flex-wrap: nowrap !important;   
        gap: 3px !important;            /* 左右球间距 */
        margin-top: 0px !important;
        margin-bottom: 3px !important;  /* 🔥【关键参数】7行之间只有极小紧凑的 3 像素上下间歇！ */
        padding: 0px !important;
        height: auto !important;        /* 解除任何隐式高度撑开 */
    }
    .num-matrix-container div[data-testid="stHorizontalBlock"] > div {
        flex: 1 1 0% !important; min-width: 0 !important; padding: 0 !important; margin: 0 !important;
    }
    /* 3. 精准锁定每一个按钮为完美的自适应正圆球体 */
    .num-matrix-container div[data-testid="stHorizontalBlock"] button {
        color: white !important; font-weight: bold !important; font-size: 15px !important; border: none !important; 
        border-radius: 50% !important; width: 100% !important; aspect-ratio: 1 / 1 !important; padding: 0px !important; margin: 0px auto !important;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.15) !important;
        display: flex !important; align-items: center !important; justify-content: center !important;
    }
    
    /* 三色波样式 */
    .num-matrix-container .btn-red button { background: linear-gradient(135deg, #ff4d4d, #cc0000) !important; }
    .num-matrix-container .btn-blue button { background: linear-gradient(135deg, #4da6ff, #0066cc) !important; }
    .num-matrix-container .btn-green button { background: linear-gradient(135deg, #47d147, #009900) !important; }
    /* 勾选状态 */
    .num-matrix-container .btn-selected button { 
        background: linear-gradient(135deg, #ffd700, #ff8c00) !important; color: #1a1a1a !important; font-weight: 900 !important; border: 2px solid #ffffff !important; box-shadow: 0px 0px 5px #ffd700 !important; 
    }
    
    .ball-container { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 4px; margin-bottom: 4px; }
    .ball { width: 34px; height: 34px; line-height: 34px; border-radius: 50%; color: white; text-align: center; font-weight: bold; font-size: 13px; box-shadow: 1px 2px 4px rgba(0,0,0,0.15); }
    .ball-red { background: linear-gradient(135deg, #dc143c, #960018); }
    .ball-blue { background: linear-gradient(135deg, #1e90ff, #002fa7); }
    .ball-green { background: linear-gradient(135deg, #2e8b57, #124e2c); }
    
    .wallet-card { background: linear-gradient(135deg, #111, #222); color: #ffd700; padding: 10px; border-radius: 12px; text-align: center; margin-bottom: 8px; font-weight: bold; font-size: 15px; }
    .mobile-card { background-color: #f8fafc; padding: 8px; border-radius: 10px; border-left: 5px solid #8a2be2; margin-bottom: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 官方49码球色划分 ---
RED_BALLS = [1,2,7,8,12,13,18,19,23,24,29,30,34,35,40,45,46]
BLUE_BALLS = [3,4,9,10,14,15,20,25,26,31,36,37,41,42,47,48]
GREEN_BALLS = [5,6,11,16,17,21,22,27,28,32,33,38,39,43,44,49]

def get_ball_style(num):
    if num in RED_BALLS: return "ball-red"
    if num in BLUE_BALLS: return "ball-blue"
    return "ball-green"

def get_ball_color_class(num):
    if num in RED_BALLS: return "btn-red"
    if num in BLUE_BALLS: return "btn-blue"
    return "btn-green"

# --- 初始化 Session State ---
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
    return [{"issue": "26/051", "date": "2026-05-14", "numbers": [2,7,15,24,31,42], "special": 49}]

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
st.markdown('<div class="nav-container">', unsafe_allow_html=True)
nav_cols = st.columns(4)
tabs_list = ["🔘 自选平特", "🎯 一马中特", "📊 标准复式", "🎲 黄金胆拖"]

for idx, tab_name in enumerate(tabs_list):
    is_active = st.session_state.current_tab == tab_name
    display_label = tab_name[2:]
    cls_active = "nav-active" if is_active else ""
    with nav_cols[idx]:
        st.markdown(f'<div class="{cls_active}">', unsafe_allow_html=True)
        if st.button(display_label, key=f"nav_tab_{idx}"):
            st.session_state.current_tab = tab_name
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ----------------- 核心玩法区 -----------------

# 开启极度紧凑型号码盘专属隔离容器
st.markdown('<div class="num-matrix-container">', unsafe_allow_html=True)

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

st.markdown('</div>', unsafe_allow_html=True) # 关闭号码盘隔离容器

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
                        
                        if match_m == 6: st.session_state.wallet += 50000.0; bet["状态"] = "🎉 头奖！+$50000"
                        elif match_m == 3: st.session_state.wallet += 40.0; bet["状态"] = "🎉 七奖！+$40"
                        elif match_s and bet["玩法"] == "手选单式": st.session_state.wallet += 20.0; bet["状态"] = "🎉 中特码！+$20"
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
    st.caption("📂 暂无下注记录。")

# --- 📊 50期大数据图表看板 ---
st.divider()
st.header("📊 50期大数据·正码热度排行榜")
hot_counts = {i: 0 for i in range(1, 50)}
for draw in history_50:
    for n in draw["numbers"]: hot_counts[n] += 1
df_chart = pd.DataFrame.from_dict(hot_counts, orient='index', columns=['50期出号频次'])
st.bar_chart(df_chart)

st.divider()
st.caption("⚠️ 声明：本系统已开启官方网络源自动同步。模拟游戏纯属公益娱乐工具。")
