import streamlit as st
import random
import math
import pandas as pd
import requests
import time
import copy
from datetime import datetime

# --- 页面基本配置 ---
st.set_page_config(page_title="预言家娱乐全超控盘", page_icon="🔮", layout="centered")

# --- 🎯 v34.0 资产直调与全要素手机端专属立体样式表 ---
st.markdown("""
    <style>
    .block-container { padding-top: 0.1rem !important; padding-bottom: 0.1rem !important; padding-left: 0.1rem !important; padding-right: 0.1rem !important; }
    
    .admin-alert-banner {
        background: linear-gradient(135deg, #ff3b30, #ff9500) !important;
        color: white !important; padding: 8px; border-radius: 6px; text-align: center;
        font-weight: bold !important; font-size: 13px !important; margin-bottom: 8px !important;
    }
    
    .prophet-logo-title {
        text-align: center !important; font-size: 18px !important; font-weight: 900 !important;
        background: linear-gradient(135deg, #ffd700, #8a2be2, #00f2fe) !important;
        -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important;
        margin-top: 2px !important; margin-bottom: 2px !important; letter-spacing: 1px !important;
    }
    
    div[data-testid="stHorizontalBlock"] {
        display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: 2px !important;            
        margin-top: 0px !important; margin-bottom: 0px !important; padding: 0px !important; width: 100% !important;
    }
    div[data-testid="stHorizontalBlock"] > div {
        flex: 1 1 0% !important; min-width: 0 !important; padding: 0 !important; margin: 0 !important;
    }
    
    .num-ball-wrap button {
        font-weight: 900 !important; font-size: 14px !important; border: none !important;
        border-radius: 50% !important; width: 100% !important; aspect-ratio: 1 / 1 !important; 
        padding: 0px !important; margin: 0px auto !important;
        display: flex !important; align-items: center !important; justify-content: center !important;
        box-shadow: inset -2px -2px 4px rgba(0,0,0,0.4), 1px 2px 3px rgba(0,0,0,0.3) !important;
    }
    
    .ball-r button { background: linear-gradient(135deg, #ff4d4d, #b30000) !important; color: white !important; }
    .ball-b button { background: linear-gradient(135deg, #4da6ff, #0044cc) !important; color: white !important; }
    .ball-g button { background: linear-gradient(135deg, #47d147, #008000) !important; color: white !important; }
    
    .ball-s button {
        background: linear-gradient(135deg, #fff066, #ff9900) !important;
        color: #000000 !important; font-weight: 900 !important; 
        box-shadow: 0px 0px 8px #ffd700, inset -1px -1px 3px rgba(0,0,0,0.5) !important;
    }
    
    .draw-container { display: flex; flex-wrap: nowrap; gap: 3px; margin: 2px auto; justify-content: center; width: 100%; }
    .draw-ball { width: 32px; height: 32px; line-height: 32px; border-radius: 50%; color: white; text-align: center; font-weight: bold; font-size: 13px; box-shadow: 1px 2px 3px rgba(0,0,0,0.2); }
    .draw-red { background: linear-gradient(135deg, #ff4d4d, #cc0000); }
    .draw-blue { background: linear-gradient(135deg, #4da6ff, #0066cc); }
    .draw-green { background: linear-gradient(135deg, #47d147, #009900); }
    
    .wallet-card-mini { 
        background: #1e1e24 !important; color: #ffffff !important; 
        padding: 4px 8px; border-radius: 20px; text-align: center; 
        font-weight: bold; font-size: 12px; border: 1px solid #3a3a43;
        display: inline-block; width: 100%; box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .wallet-gold-txt { color: #ffcc00 !important; font-weight: 900 !important; }
    .rank-badge { background: #8a2be2; color: white; padding: 1px 4px; border-radius: 4px; font-size: 10px; margin-left: 2px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🎯 49码三色波色核心静态数表（✨ 已完美闭合填充） ---
RED_BALLS = [1, 2, 7, 8, 12, 13, 18, 19, 23, 24, 29, 30, 34, 35, 40, 45, 46]
BLUE_BALLS = [3, 4, 9, 10, 14, 15, 20, 25, 26, 31, 36, 37, 41, 42, 47, 48]
GREEN_BALLS = [5, 6, 11, 16, 17, 21, 22, 27, 28, 32, 33, 38, 39, 43, 44, 49]

# 算法智能反推：以 2026 丙午马年（01号为马）顺推全码生肖表，支持核销
ZODIAC_ORDER = ["马", "蛇", "龙", "兔", "虎", "牛", "鼠", "猪", "狗", "鸡", "猴", "羊"]
ZODIAC_MAP = {name: [] for name in ZODIAC_ORDER}
for num in range(1, 50):
    idx = (num - 1) % 12
    ZODIAC_MAP[ZODIAC_ORDER[idx]].append(num)

def get_ball_style(num):
    if num in RED_BALLS: return "draw-red"
    if num in BLUE_BALLS: return "draw-blue"
    return "draw-green"

def get_ball_color_class(num):
    if num in RED_BALLS: return "ball-r"
    if num in BLUE_BALLS: return "ball-b"
    return "ball-g"

def get_num_zodiac(num):
    for k, v in ZODIAC_MAP.items():
        if num in v: return k
    return ""

# --- 👑 全网共享物理单例数据库 ---
@st.cache_resource
def init_global_shared_db():
    return {
        "users": {
            "admin": {"password": "888", "role": "admin", "status": "approved", "wallet": 0.0},
            "test": {"password": "123", "role": "user", "status": "active", "wallet": 1000.0}
        },
        "reg_requests": {}, "deposit_requests": [], "bet_history": [],
        "latest_draw": {"issue": "2026/058", "date": "2026-05-18", "numbers": [1, 8, 12, 23, 29, 34], "special": 7}
    }

global_db = init_global_shared_db()

if 'logged_in_user' not in st.session_state: st.session_state.logged_in_user = None
if 'manual_ping' not in st.session_state: st.session_state.manual_ping = []
if 'manual_te' not in st.session_state: st.session_state.manual_te = None
if 'manual_lian' not in st.session_state: st.session_state.manual_lian = []
if 'current_tab' not in st.session_state: st.session_state.current_tab = "自选平特"

# --- 📡 核心实时同步数据采集 ---
@st.cache_data(ttl=3600)
def fetch_live_data_50():
    try:
        url = "https://cpdata.io"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            res_json = response.json()
            live_data = []
            for item in res_json.get("data", []):
                nums_list = [int(x) for x in item.get("numbers", [])]
                if len(nums_list) >= 7:
                    live_data.append({
                        "issue": item.get("issue"), "date": item.get("open_time")[:10],
                        "numbers": nums_list[:6], "special": nums_list[6]
                    })
            if live_data: return live_data[0]
    except Exception: pass
    return None

api_data = fetch_live_data_50()
if api_data:
    global_db["latest_draw"] = api_data

latest_draw = global_db["latest_draw"]

# --- 🔮 统一置顶看板 ---
st.markdown('<div class="prophet-logo-title">🔮 预言家娱乐模拟全控盘</div>', unsafe_allow_html=True)

ball_html = '<div class="draw-container">'
for num in latest_draw['numbers']:
    ball_html += f'<div class="draw-ball {get_ball_style(num)}">{num}</div>'
ball_html += f'<div class="draw-ball {get_ball_style(latest_draw["special"])}">{latest_draw["special"]}</div></div>'
st.markdown(ball_html, unsafe_allow_html=True)

col_info1, col_info2 = st.columns(2)
with col_info1: 
    st.markdown(f"<div style='font-size:11px;color:#888;font-weight:bold;margin-top:6px;'>📡 官网同步: {latest_draw['issue']}</div>", unsafe_allow_html=True)
with col_info2:
    current_user = st.session_state.logged_in_user
    wallet_val = global_db["users"][current_user]["wallet"] if current_user in global_db["users"] else 0.0
    role_badge = f"<span class='rank-badge'>管理</span>" if current_user == "admin" else (f"<span class='rank-badge'>玩家</span>" if current_user else "")
    user_str = f"{current_user}{role_badge}" if current_user else "未登录"
    st.markdown(f"<div class='wallet-card-mini'>👤 {user_str} | 💰 <span class='wallet-gold-txt'>¥{wallet_val:,.2f}</span></div>", unsafe_allow_html=True)

if st.session_state.logged_in_user == "admin":
    pending_reg_count = len([k for k, v in global_db["reg_requests"].items() if v.get("status") == "pending"])
    pending_dep_count = len([d for d in global_db["deposit_requests"] if d.get("status") == "pending"])
    if pending_reg_count > 0 or pending_dep_count > 0:
        st.markdown(f'<div class="admin-alert-banner">🔴 待办：{pending_reg_count}个新用户 | {pending_dep_count}笔充值待审</div>', unsafe_allow_html=True)

st.write("---")

# ----------------- 🔐 账户与登录管理面板 -----------------
if not st.session_state.logged_in_user:
    tab_log, tab_reg = st.tabs(["🔐 账户登录", "📝 用户注册"])
    with tab_log:
        login_user = st.text_input("用户名", key="log_u")
        login_pwd = st.text_input("密码", type="password", key="log_p")
        if st.button("🔥 立即登录验证"):
            if login_user in global_db["users"] and global_db["users"][login_user]["password"] == login_pwd:
                st.session_state.logged_in_user = login_user
                st.rerun()
            else: st.error("❌ 用户名或密码错误！")
    with tab_reg:
        reg_user = st.text_input("期望用户名", key="reg_u")
        reg_pwd = st.text_input("设置登录密码", type="password", key="reg_p")
        if st.button("🚀 提交入网审核申请"):
            global_db["reg_requests"][reg_user] = {"password": reg_pwd, "status": "pending"}
            st.success("🎯 申请已提交物理单例总线！")
else:
    u_name = st.session_state.logged_in_user

    # ----------------- 👑 管理员独立全盘控制后台 -----------------
    if st.session_state.logged_in_user == "admin":
        with st.sidebar.expander("🛠️ 至尊顶层全盘控制后台", expanded=True):
            st.markdown("### 📡 官网同步数据清算核销")
            if st.button("🎰 同步官方开奖并全盘清算"):
                new_balls = latest_draw["numbers"]
                new_special = latest_draw["special"]
                
                for bet in global_db["bet_history"]:
                    if bet.get("status") == "已结算": continue
                    u = bet["user"]
                    win_amt = 0.0
                    b_type = bet["type"]
                    balls = bet["balls"]
                    amt = bet["amount"]
                    
                    if b_type == "自选平特":
                        hits = len(set(balls) & set(new_balls))
                        if hits > 0: win_amt = amt * (hits * 1.8)
                    elif b_type == "一码中特" and balls == [new_special]:
                        win_amt = amt * 42.0
                    elif b_type == "两面盘":
                        target = balls[0]
                        if "大" in target and new_special >= 25: win_amt = amt * 1.95
                        elif "小" in target and new_special < 25: win_amt = amt * 1.95
                        elif "单" in target and new_special % 2 != 0: win_amt = amt * 1.95
                        elif "双" in target and new_special % 2 == 0: win_amt = amt * 1.95
                    elif b_type == "平特一肖":
                        match_zxs = [get_num_zodiac(n) for n in new_balls + [new_special]]
                        if balls[0] in match_zxs: win_amt = amt * 2.1
                    elif b_type == "连码(三全中)" and set(balls).issubset(set(new_balls)):
                        win_amt = amt * 30.0
                        
                    if win_amt > 0: global_db["users"][u]["wallet"] += win_amt
                    bet["status"] = "已结算"
                st.success("🎰 大盘核销清算完成！")
                st.rerun()

            # ----------------- 🚨 活跃玩家资产后台直调模块 -----------------
            st.markdown("---")
            st.markdown("### 👥 物理总线全盘活跃用户花名册")
            active_users = [name for name in global_db["users"].keys() if name != "admin"]
            
            if active_users:
                for target_u in active_users:
                    current_bal = global_db["users"][target_u]["wallet"]
                    st.markdown(f"**👤 玩家账号**: `{target_u}` | 当前余额: `¥{current_bal:,.2f}`")
                    col_mod_val, col_mod_btn = st.columns([2, 1])
                    with col_mod_val:
                        new_target_val = st.number_input(f"调整金额", min_value=0.0, max_value=9999999.0, step=100.0, value=float(current_bal), key=f"v_mod_{target_u}", label_visibility="collapsed")
                    with col_mod_btn:
                        if st.button("💾 确认", key=f"b_mod_{target_u}"):
                            global_db["users"][target_u]["wallet"] = new_target_val
                            st.success("已校正")
                            st.rerun()
                    st.markdown("<div style='margin-bottom:8px;'></div>", unsafe_allow_html=True)
            else:
                st.info("当前应用总线暂无普通玩家数据。")

            st.markdown("---")
            st.markdown("### 👥 新用户极速过审区")
            for u, v in list(global_db["reg_requests"].items()):
                if v["status"] == "pending" and st.button(f"✅ 批准: {u}"):
                    global_db["users"][u] = {"password": v["password"], "role": "user", "status": "active", "wallet": 1000.0}
                    v["status"] = "approved"; st.rerun()

            st.markdown("### 💰 线上充值订单核销中心")
            for idx, dep in enumerate(global_db["deposit_requests"]):
                if dep["status"] == "pending" and st.button(f"🪙 确认进账 ¥{dep['amount']}: {dep['user']}", key=f"adm_d_{idx}"):
                    global_db["users"][dep['user']]["wallet"] += dep['amount']
                    dep["status"] = "approved"; st.rerun()
            
            if st.button("🚪 退出管理员模式"):
                st.session_state.logged_in_user = None
                st.rerun()

    # ----------------- 🎮 核心模拟下注交互区 -----------------
    st.session_state.current_tab = st.radio("切换下注模拟玩法", ["自选平特", "🔥 一码中特", "📊 两面盘", "🐾 平特一肖", "🔗 连码(三全中)", "🎲 胆拖工具", "💰 财务中心"], horizontal=True)

    def render_matrix(session_key, is_multiselect=False, max_sel=99):
        for i in range(0, 49, 7):
            cols = st.columns(7)
            for j in range(7):
                num = i + j + 1
                if num <= 49:
                    is_sel = num in st.session_state[session_key] if is_multiselect else (num == st.session_state[session_key])
                    cls = "ball-s" if is_sel else get_ball_color_class(num)
                    with cols[j]:
                        st.markdown(f"<div class='num-ball-wrap {cls}'>", unsafe_allow_html=True)
                        if st.button(f"{num:02d}", key=f"m_{session_key}_{num}"):
                            if is_multiselect:
                                if num in st.session_state[session_key]: st.session_state[session_key].remove(num)
                                elif len(st.session_state[session_key]) < max_sel: st.session_state[session_key].append(num)
                            else:
                                st.session_state[session_key] = None if is_sel else num
                            st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)

    def commit_bet(b_type, balls_list, amount):
        if global_db["users"][u_name]["wallet"] < amount: st.error("❌ 余额不足！")
        else:
            global_db["users"][u_name]["wallet"] -= amount
            global_db["bet_history"].append({"user": u_name, "type": b_type, "balls": balls_list, "amount": amount, "status": "待开奖", "time": datetime.now().strftime("%H:%M")})
            st.success("🎯 模拟下注成功！")
            time.sleep(0.4); st.rerun()

    # 1. 自选平特
    if st.session_state.current_tab == "自选平特":
        st.subheader("🔮 49码平特高光自选矩阵")
        render_matrix("manual_ping", is_multiselect=True)
        st.info(f"当前已选平特号码：{sorted(st.session_state.manual_ping)}")
        amt = st.number_input("下单金额 (¥)", min_value=10.0, step=10.0, key="ap")
        if st.button("🔥 确认提交平特模拟注单") and st.session_state.manual_ping:
            commit_bet("自选平特", list(st.session_state.manual_ping), amt)

    # 2. 🔥 一码中特
    elif st.session_state.current_tab == "🔥 一码中特":
        st.subheader("🎯 独赢：狙击第七个开奖球（特码）")
        render_matrix("manual_te", is_multiselect=False)
        if st.session_state.manual_te:
            st.warning(f"💎 已锁中特核心码：【 {st.session_state.manual_te:02d} 】号球")
            amt = st.number_input("中特模拟下单金额 (¥)", min_value=20.0, step=20.0, key="ate")
            st.metric("🎯 模拟胜率回报评估", f"¥ {amt * 49:,.2f}", delta="预估回报 (49倍)")
            if st.button("🚀 封单确认：发射中特注单"):
                commit_bet("一码中特", [st.session_state.manual_te], amt)

    # 3. 两面盘
    elif st.session_state.current_tab == "📊 两面盘":
        st.subheader("📊 特码两面双向独赢")
        lm = st.radio("请押注特码属性", ["大 (>=25)", "小 (<25)", "单", "双"], horizontal=True)
        amt = st.number_input("下注金额 (¥)", min_value=50.0, step=50.0)
        if st.button("提交两面盘注单"):
            commit_bet("两面盘", [lm], amt)

    # 4. 平特一肖
    elif st.session_state.current_tab == "🐾 平特一肖":
        st.subheader("🐾 生肖极速盲押盘")
        sx = st.selectbox("选择目标生肖", list(ZODIAC_MAP.keys()))
        st.caption(f"当前生肖包含号码: {ZODIAC_MAP[sx]}")
        amt = st.number_input("下注金额 (¥)", min_value=10.0, step=10.0)
        if st.button("提交一肖注单"):
            commit_bet("平特一肖", [sx], amt)

    # 5. 连码玩法
    elif st.session_state.current_tab == "🔗 连码(三全中)":
        st.subheader("🔗 连码极客挑战：必须选满3码且全中平码")
        render_matrix("manual_lian", is_multiselect=True, max_sel=3)
        st.info(f"已选连码：{sorted(st.session_state.manual_lian)}")
        amt = st.number_input("连码本金 (¥)", min_value=10.0, step=10.0)
        if st.button("确认提交三全中") and len(st.session_state.manual_lian) == 3:
            commit_bet("连码(三全中)", list(st.session_state.manual_lian), amt)

    # 6. 胆拖工具
    elif st.session_state.current_tab == "🎲 胆拖工具":
        st.subheader("🎲 胆拖高级组合器")
        col_dan, col_tuo = st.columns(2)
        with col_dan: d_balls = st.multiselect("选择胆码(最多2个)", range(1, 50), max_selections=2)
        with col_tuo: t_balls = st.multiselect("选择拖码", [x for x in range(1, 50) if x not in d_balls])
        if d_balls and t_balls:
            st.success(f"💡 智能拆分：共可生成平特组合数：{math.comb(len(t_balls), 3 - len(d_balls))} 组")

    # 7. 财务中心
    elif st.session_state.current_tab == "💰 财务中心":
        st.subheader("💰 模拟财务自助通道")
        st.metric("您的当前物理钱包余额", f"¥ {global_db['users'][u_name]['wallet']:,.2f}")
        dep_amt = st.number_input("请输入模拟充值金额", min_value=100.0, step=100.0)
        if st.button("🏦 提交金流充值工单"):
            global_db["deposit_requests"].append({"user": u_name, "amount": dep_amt, "status": "pending"})
            st.success("🚀 充值工单已提交！")

    # --- 实时注单流水 ---
    st.write("---")
    st.subheader("📋 本机模拟盘实时注单流水")
    my_bets = [b for b in global_db["bet_history"] if b["user"] == u_name]
    if my_bets: st.dataframe(pd.DataFrame(my_bets)[["type", "balls", "amount", "status", "time"]], use_container_width=True)

    if st.button("🚪 退出当前账户"):
        st.session_state.logged_in_user = None
        st.rerun()
