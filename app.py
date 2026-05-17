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

# --- 🎯 v28.0 全玩法集成+开奖结算引擎金流样式表 ---
st.markdown("""
    <style>
    .block-container { padding-top: 0.2rem !important; padding-bottom: 0.2rem !important; padding-left: 0.2rem !important; padding-right: 0.2rem !important; }
    
    .admin-alert-banner {
        background: linear-gradient(135deg, #ff3b30, #ff9500) !important;
        color: white !important; padding: 10px; border-radius: 8px; text-align: center;
        font-weight: 900 !important; font-size: 14px !important; margin-bottom: 10px !important;
        box-shadow: 0px 4px 10px rgba(255,59,48,0.3);
    }
    
    .prophet-logo-title {
        text-align: center !important; font-size: 20px !important; font-weight: 900 !important;
        background: linear-gradient(135deg, #ffd700, #8a2be2, #00f2fe) !important;
        -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important;
        margin-top: 2px !important; margin-bottom: 4px !important; letter-spacing: 2px !important;
    }
    
    div[data-testid="stVerticalBlock"] .stButton>button { 
        background: linear-gradient(135deg, #4b0082, #8a2be2) !important; 
        color: white !important; border-radius: 25px !important; width: 100% !important; height: 42px !important; font-size: 15px !important; font-weight: bold !important; border: none !important;
    }
    
    div[data-testid="stHorizontalBlock"] {
        display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: 2px !important;            
        margin-top: 0px !important; margin-bottom: 1px !important; padding: 0px !important; width: 100% !important;
    }
    div[data-testid="stHorizontalBlock"] > div {
        flex: 1 1 0% !important; min-width: 0 !important; padding: 0 !important; margin: 0 !important;
    }
    
    .num-ball-wrap button {
        color: white !important; font-weight: bold !important; font-size: 15px !important; border: none !important;
        border-radius: 50% !important; width: 100% !important; aspect-ratio: 1 / 1 !important; padding: 0px !important; margin: 0px auto !important;
        display: flex !important; align-items: center !important; justify-content: center !important;
    }
    
    .ball-r button { background: linear-gradient(135deg, #ff4d4d, #cc0000) !important; color: white !important; }
    .ball-b button { background: linear-gradient(135deg, #4da6ff, #0066cc) !important; color: white !important; }
    .ball-g button { background: linear-gradient(135deg, #47d147, #009900) !important; color: white !important; }
    
    .ball-s button {
        background: linear-gradient(135deg, #ffd700, #ff8c00) !important;
        color: #1a1a1a !important; font-weight: 900 !important; border: 1.5px solid #ffffff !important; box-shadow: 0px 0px 5px #ffd700 !important;
    }
    
    .draw-container { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 1px; margin-bottom: 2px; justify-content: center; }
    .draw-ball { width: 36px; height: 36px; line-height: 36px; border-radius: 50%; color: white; text-align: center; font-weight: bold; font-size: 14px; box-shadow: 1px 2px 4px rgba(0,0,0,0.15); }
    .draw-red { background: linear-gradient(135deg, #ff4d4d, #cc0000); }
    .draw-blue { background: linear-gradient(135deg, #4da6ff, #0066cc); }
    .draw-green { background: linear-gradient(135deg, #47d147, #009900); }
    
    .wallet-card-mini { background: linear-gradient(135deg, #111, #222); color: #ffd700; padding: 6px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 12px; border: 1px solid #333; height: 42px; line-height: 28px; }
    .rank-badge { background: #8a2be2; color: white; padding: 1px 4px; border-radius: 5px; font-size: 10px; margin-left: 2px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🎯 2026年核心属性静态映射数据表 ---
RED_BALLS = [1, 2, 7, 8, 12, 13, 18, 19, 23, 24, 29, 30, 34, 35, 40, 45, 46]
BLUE_BALLS = [3, 4, 9, 10, 14, 15, 20, 25, 26, 31, 36, 37, 41, 42, 47, 48]
GREEN_BALLS = [5, 6, 11, 16, 17, 21, 22, 27, 28, 32, 33, 38, 39, 43, 44, 49]

# 2026 丙午年十二生肖物理测算对照表
ZODIAC_MAP = {
    "马": [1, 13, 25, 37, 49], "蛇": [2, 14, 26, 38], "龙": [3, 15, 27, 39],
    "兔": [4, 16, 28, 40], "虎": [5, 17, 29, 41], "牛": [6, 18, 30, 42],
    "鼠": [7, 19, 31, 43], "猪": [8, 20, 32, 44], "狗": [9, 21, 33, 45],
    "鸡": [10, 22, 34, 46], "猴": [11, 23, 35, 47], "羊": [12, 24, 36, 48]
}

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

# --- 👑 全网唯一单例数据资源库 ---
@st.cache_resource
def init_global_shared_db():
    return {
        "users": {
            "admin": {"password": "888", "role": "admin", "status": "approved", "wallet": 0.0},
            "test": {"password": "123", "role": "user", "status": "active", "wallet": 10000.0}
        },
        "reg_requests": {}, "deposit_requests": [], "bet_history": [],
        "latest_draw": {"issue": "2026/058", "date": "2026-05-18", "numbers": [1, 8, 12, 23, 29, 34], "special": 7}
    }

global_db = init_global_shared_db()

# 会话私有状态机
if 'logged_in_user' not in st.session_state: st.session_state.logged_in_user = None
if 'manual_ping' not in st.session_state: st.session_state.manual_ping = []
if 'manual_te' not in st.session_state: st.session_state.manual_te = None
if 'manual_lian' not in st.session_state: st.session_state.manual_lian = []
if 'current_tab' not in st.session_state: st.session_state.current_tab = "自选平特"

# --- 📡 置顶数据看板 ---
latest_draw = global_db["latest_draw"]
st.markdown('<div class="prophet-logo-title">🔮 预言家全息娱乐模拟全控盘</div>', unsafe_allow_html=True)

ball_html = '<div class="draw-container">'
for num in latest_draw['numbers']:
    ball_html += f'<div class="draw-ball {get_ball_style(num)}">{num}</div>'
ball_html += f'<div class="draw-ball {get_ball_style(latest_draw["special"])}">{latest_draw["special"]}</div></div>'
st.markdown(ball_html, unsafe_allow_html=True)

col_info1, col_info2 = st.columns(2)
with col_info1: 
    st.markdown(f"<div style='font-size:12px;color:#888;font-weight:bold;'>📡 当期期号: {latest_draw['issue']} ({latest_draw['date']})</div>", unsafe_allow_html=True)
with col_info2:
    current_user = st.session_state.logged_in_user
    wallet_val = global_db["users"][current_user]["wallet"] if current_user in global_db["users"] else 0.0
    role_badge = f"<span class='rank-badge'>管理员</span>" if current_user == "admin" else (f"<span class='rank-badge'>玩家</span>" if current_user else "")
    st.markdown(f"<div class='wallet-card-mini'>👤 {current_user if current_user else '未登录'}{role_badge} | 💰 余额: ¥{wallet_val:,.2f}</div>", unsafe_allow_html=True)

# 🚨 管理员红牌警告提示
if st.session_state.logged_in_user == "admin":
    pending_reg = len([k for k, v in global_db["reg_requests"].items() if v.get("status") == "pending"])
    pending_dep = len([d for d in global_db["deposit_requests"] if d.get("status") == "pending"])
    if pending_reg > 0 or pending_dep > 0:
        st.markdown(f'<div class="admin-alert-banner">🔴 紧急：有 {pending_reg} 个新注册、{pending_dep} 笔充值订单等待核销结算！</div>', unsafe_allow_html=True)

st.write("---")

# ----------------- 🔐 隔离登录控制面板 -----------------
if not st.session_state.logged_in_user:
    tab_log, tab_reg = st.tabs(["🔐 账户登录", "📝 新用户申请"])
    with tab_log:
        login_user = st.text_input("用户名", key="log_u")
        login_pwd = st.text_input("密码", type="password", key="log_p")
        if st.button("🔥 立即重载并登录验证"):
            if login_user in global_db["users"] and global_db["users"][login_user]["password"] == login_pwd:
                st.session_state.logged_in_user = login_user
                st.rerun()
            else: st.error("密码或账户错误！")
    with tab_reg:
        reg_user = st.text_input("期望用户名", key="reg_u")
        reg_pwd = st.text_input("密码", type="password", key="reg_p")
        if st.button("🚀 提交入网审核"):
            global_db["reg_requests"][reg_user] = {"password": reg_pwd, "status": "pending"}
            st.success("工单已打入数据总线！")
else:
    # ----------------- 👑 管理员清算与核销核心 -----------------
    if st.session_state.logged_in_user == "admin":
        with st.sidebar.expander("🛠️ 至尊顶层大盘控制后台", expanded=True):
            st.markdown("### 🎲 2026模拟开奖清算引擎")
            next_issue = st.text_input("下期期号", placeholder="示例: 2026/059")
            
            if st.button("🎰 执行一键全盘自动清算"):
                if not next_issue: st.error("请输入开奖期号！")
                else:
                    # 1. 摇号生成新开奖结果
                    new_balls = sorted(random.sample(range(1, 50), 7))
                    new_special = new_balls.pop(random.randint(0, 6))
                    global_db["latest_draw"] = {
                        "issue": next_issue, "date": datetime.now().strftime("%Y-%m-%d"),
                        "numbers": new_balls, "special": new_special
                    }
                    
                    # 2. 遍历全盘注单实施金流核销
                    sum_draw = sum(new_balls) + new_special
                    spec_zodiac = get_num_zodiac(new_special)
                    
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
                        elif b_type == "一码中特" and balls[0] == new_special:
                            win_amt = amt * 42.0
                        elif b_type == "两面盘":
                            target = balls[0]
                            if target == "大" and new_special >= 25: win_amt = amt * 1.95
                            elif target == "小" and new_special < 25: win_amt = amt * 1.95
                            elif target == "单" and new_special % 2 != 0: win_amt = amt * 1.95
                            elif target == "双" and new_special % 2 == 0: win_amt = amt * 1.95
                        elif b_type == "平特一肖" and target in [get_num_zodiac(n) for n in new_balls + [new_special]]:
                            win_amt = amt * 2.1
                        elif b_type == "连码(三全中)" and set(balls).issubset(set(new_balls)):
                            win_amt = amt * 30.0
                            
                        if win_amt > 0: global_db["users"][u]["wallet"] += win_amt
                        bet["status"] = "已结算"
                    st.success("🎰 大盘数据核销完成！已根据赔率自动派奖。")
                    st.rerun()
                    
            st.markdown("---")
            # 基础充值/用户核销
            for u, v in list(global_db["reg_requests"].items()):
                if v["status"] == "pending" and st.button(f"批准: {u}"):
                    global_db["users"][u] = {"password": v["password"], "role": "user", "status": "active", "wallet": 1000.0}
                    v["status"] = "approved"; st.rerun()

    # ----------------- 🎮 核心模拟下注交互舱 -----------------
    st.session_state.current_tab = st.radio("切换大盘下注玩法", ["自选平特", "🔥 一码中特", "📊 两面盘", "🐾 平特一肖", "🔗 连码(三全中)", "🎲 胆拖工具", "💰 财务中心"], horizontal=True)
    u_name = st.session_state.logged_in_user

    # 渲染49码公共矩阵封装函数
    def render_matrix(session_key, is_multiselect=False, max_sel=99):
        for i in range(0, 49, 7):
            cols = st.columns(7)
            for j in range(7):
                num = i + j + 1
                if num <= 49:
                    if is_multiselect: is_sel = num in st.session_state[session_key]
                    else: is_sel = (num == st.session_state[session_key])
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

    # 基础下单处理
    def commit_bet(b_type, balls_list, amount):
        if global_db["users"][u_name]["wallet"] < amount: st.error("❌ 模拟钱包余额不足！")
        else:
            global_db["users"][u_name]["wallet"] -= amount
            global_db["bet_history"].append({"user": u_name, "type": b_type, "balls": balls_list, "amount": amount, "status": "待开奖", "time": datetime.now().strftime("%H:%M")})
            st.success("🎯 模拟注单已成功锁死打入大盘总线！")
            time.sleep(0.5); st.rerun()

    # 1. 自选平特
    if st.session_state.current_tab == "自选平特":
        st.subheader("🔮 平特多选自选矩阵 (模拟1赔1.8/每中一码)")
        render_matrix("manual_ping", is_multiselect=True)
        st.info(f"已选号码：{sorted(st.session_state.manual_ping)}")
        amt = st.number_input("投注本金 (¥)", min_value=10.0, step=10.0, key="ap")
        if st.button("确认下注平特") and st.session_state.manual_ping:
            commit_bet("自选平特", list(st.session_state.manual_ping), amt)

    # 2. 一码中特
    elif st.session_state.current_tab == "🔥 一码中特":
        st.subheader("🎯 独赢中特特码狙击舱 (模拟1赔42)")
        render_matrix("manual_te", is_multiselect=False)
        if st.session_state.manual_te:
            st.warning(f"已锁定核心码：【 {st.session_state.manual_te:02d} 】")
            amt = st.number_input("特码本金 (¥)", min_value=20.0, step=20.0, key="ate")
            st.metric("预估杠杆回报", f"¥ {amt * 42:,.2f}")
            if st.button("发射特码注单"):
                commit_bet("一码中特", [st.session_state.manual_te], amt)

    # 3. 两面盘
    elif st.session_state.current_tab == "📊 两面盘":
        st.subheader("📊 特码两面双向独赢 (模拟1赔1.95)")
        lm = st.radio("请押注特码属性", ["大 (>=25)", "小 (<25)", "单", "双"], horizontal=True)
        amt = st.number_input("下注金额 (¥)", min_value=50.0, step=50.0)
        if st.button("提交两面盘注单"):
            commit_bet("两面盘", [lm[0]], amt)

    # 4. 平特一肖
    elif st.session_state.current_tab == "🐾 平特一肖":
        st.subheader("🐾 生肖极速盲押盘 (模拟1赔2.1)")
        sx = st.selectbox("选择目标生肖", list(ZODIAC_MAP.keys()))
        st.caption(f"当前生肖包含号码: {ZODIAC_MAP[sx]}")
        amt = st.number_input("下注金额 (¥)", min_value=10.0, step=10.0)
        if st.button("提交一肖注单"):
            commit_bet("平特一肖", [sx], amt)

    # 5. 连码（三全中）
    elif st.session_state.current_tab == "🔗 连码(三全中)":
        st.subheader("🔗 连码极客挑战：必须选满3码且全中平码 (模拟1赔30)")
        render_matrix("manual_lian", is_multiselect=True, max_sel=3)
        st.info(f"已选连码：{sorted(st.session_state.manual_lian)}")
        amt = st.number_input("连码本金 (¥)", min_value=10.0, step=10.0)
        if st.button("确认提交三全中") and len(st.session_state.manual_lian) == 3:
            commit_bet("连码(三全中)", list(st.session_state.manual_lian), amt)

    # 6. 胆拖玩法工具
    elif st.session_state.current_tab == "🎲 胆拖工具":
        st.subheader("🎲 胆拖自动矩阵拆分器")
        col_dan, col_tuo = st.columns(2)
        with col_dan: d_balls = st.multiselect("选择胆码(最多2个)", range(1, 50), max_selections=2)
        with col_tuo: t_balls = st.multiselect("选择拖码", [x for x in range(1, 50) if x not in d_balls])
        if d_balls and t_balls:
            st.success(f"💡 智能矩阵计算：共可为您自动拆分成 {math.comb(len(t_balls), 3 - len(d_balls))} 组标准平特单单。")

    # 7. 财务中心
    elif st.session_state.current_tab == "💰 财务中心":
        st.subheader("💰 模拟玩家实时财务结算台")
        st.metric("您的当前物理钱包余额", f"¥ {global_db['users'][u_name]['wallet']:,.2f}")
        dep_amt = st.number_input("模拟自助充值金额", min_value=100.0, step=100.0)
        if st.button("🏦 立即提交金流工单"):
            global_db["deposit_requests"].append({"user": u_name, "amount": dep_amt, "status": "pending"})
            st.success("充值工单已打入总线后台！请使用 admin 账户进行核销確認。")

    # --- 实时注单追溯历史底牌 ---
    st.write("---")
    st.subheader("📋 本机模拟盘实时注单流水")
    my_bets = [b for b in global_db["bet_history"] if b["user"] == u_name]
    if my_bets: st.dataframe(pd.DataFrame(my_bets)[["type", "balls", "amount", "status", "time"]], use_container_width=True)
    else: st.info("当前数据总线暂无下注记录流水。")

    if st.button("🚪 退出当前账户"):
        st.session_state.logged_in_user = None
        st.rerun()
