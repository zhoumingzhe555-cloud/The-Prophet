import streamlit as st
import random
import math
import pandas as pd
import requests
import time
from datetime import datetime

# --- 页面基本配置 ---
st.set_page_config(page_title="预言家全控模拟盘", page_icon="🔮", layout="centered")

# --- 🎯 v24.5 终极像素级紧凑正圆巧克力矩阵样式表 ---
st.markdown("""
    <style>
    .block-container { padding-top: 0.2rem !important; padding-bottom: 0.2rem !important; padding-left: 0.2rem !important; padding-right: 0.2rem !important; }
    
    /* 🔴 管理后台：至尊顶层待办红牌警告灯 */
    .admin-alert-banner {
        background: linear-gradient(135deg, #ff3b30, #ff9500) !important;
        color: white !important; padding: 10px; border-radius: 8px; text-align: center;
        font-weight: 900 !important; font-size: 14px !important; margin-bottom: 10px !important;
        box-shadow: 0px 4px 10px rgba(255,59,48,0.3);
    }
    
    /* 预言家顶层核心标志样式 */
    .prophet-logo-title {
        text-align: center !important; font-size: 20px !important; font-weight: 900 !important;
        background: linear-gradient(135deg, #ffd700, #8a2be2, #00f2fe) !important;
        -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important;
        margin-top: 2px !important; margin-bottom: 4px !important; letter-spacing: 2px !important;
    }
    
    /* 核心行动大按钮 */
    div[data-testid="stVerticalBlock"] .stButton>button { 
        background: linear-gradient(135deg, #4b0082, #8a2be2) !important; 
        color: white !important; border-radius: 25px !important; width: 100% !important; height: 42px !important; font-size: 15px !important; font-weight: bold !important; border: none !important;
    }
    
    /* 强控手机端所有列容器必须横排 */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: 2px !important;            
        margin-top: 0px !important; margin-bottom: 1px !important; padding: 0px !important; width: 100% !important;
    }
    div[data-testid="stHorizontalBlock"] > div {
        flex: 1 1 0% !important; min-width: 0 !important; padding: 0 !important; margin: 0 !important;
    }
    
    /* 将 1-49 所有原生按钮强行雕刻成完美正圆 */
    .num-ball-wrap button {
        color: white !important; font-weight: bold !important; font-size: 15px !important; border: none !important;
        border-radius: 50% !important; width: 100% !important; aspect-ratio: 1 / 1 !important; padding: 0px !important; margin: 0px auto !important;
        display: flex !important; align-items: center !important; justify-content: center !important;
    }
    
    /* 三色球高光底色 */
    .ball-r button { background: linear-gradient(135deg, #ff4d4d, #cc0000) !important; color: white !important; }
    .ball-b button { background: linear-gradient(135deg, #4da6ff, #0066cc) !important; color: white !important; }
    .ball-g button { background: linear-gradient(135deg, #47d147, #009900) !important; color: white !important; }
    
    /* 勾选高亮立体黄金球 */
    .ball-s button {
        background: linear-gradient(135deg, #ffd700, #ff8c00) !important;
        color: #1a1a1a !important; font-weight: 900 !important; border: 1.5px solid #ffffff !important; box-shadow: 0px 0px 5px #ffd700 !important;
    }
    
    /* 置顶开奖区 */
    .draw-container { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 1px; margin-bottom: 2px; justify-content: center; }
    .draw-ball { width: 36px; height: 36px; line-height: 36px; border-radius: 50%; color: white; text-align: center; font-weight: bold; font-size: 14px; box-shadow: 1px 2px 4px rgba(0,0,0,0.15); }
    .draw-red { background: linear-gradient(135deg, #ff4d4d, #cc0000); }
    .draw-blue { background: linear-gradient(135deg, #4da6ff, #0066cc); }
    .draw-green { background: linear-gradient(135deg, #47d147, #009900); }
    
    .wallet-card-mini { background: linear-gradient(135deg, #111, #222); color: #ffd700; padding: 6px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 12px; border: 1px solid #333; height: 42px; line-height: 28px; }
    .rank-badge { background: #8a2be2; color: white; padding: 1px 4px; border-radius: 5px; font-size: 10px; margin-left: 2px; }
    </style>
    """, unsafe_allow_html=True)

# --- 官方49码红蓝绿波严格划分 ---
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

# --- 👑【跨设备全网数据总线】全局数据库 ---
@st.cache_resource
def init_global_shared_db():
    return {
        "users": {
            "admin": {"password": "888", "role": "admin", "status": "approved", "wallet": 0.0},
            "test": {"password": "123", "role": "user", "status": "active", "wallet": 1000.0}
        },
        "reg_requests": {},
        "deposit_requests": [],
        "bet_history": []
    }

db = init_global_shared_db()

# 会话隔离私有身份状态锁
if 'logged_in_user' not in st.session_state: st.session_state.logged_in_user = None
if 'manual_ping' not in st.session_state: st.session_state.manual_ping = []
if 'manual_te' not in st.session_state: st.session_state.manual_te = []
if 'current_tab' not in st.session_state: st.session_state.current_tab = "自选平特"
if 'last_win_msg' not in st.session_state: st.session_state.last_win_msg = ""
if 'count_f' not in st.session_state: st.session_state.count_f = 7
if 'count_dan' not in st.session_state: st.session_state.count_dan = 2
if 'count_tuo' not in st.session_state: st.session_state.count_tuo = 6

# --- 📡【高容错核心加固】全自动数据采集引擎 ---
@st.cache_data(ttl=3600)
def fetch_live_data_50():
    # 🎯【核心修复】完整补全离线兜底大底，格式100%安全
    fallback_data = [{"issue": "2026/058", "date": "2026-05-18", "numbers": [1, 2, 3, 4, 5, 6], "special": 7}]
    try:
        url = "https://cpdata.io"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            res_json = response.json()
            live_data = []
            for item in res_json.get("data", []):
                nums_list = [int(x) for x in item.get("numbers", [])]
                if len(nums_list) >= 7:
                    live_data.append({"issue": item.get("issue"), "date": item.get("open_time")[:10], "numbers": nums_list[:6], "special": nums_list[6]})
            if live_data: return live_data
    except Exception:
        pass
    return fallback_data

history_50 = fetch_live_data_50()

# 🎯【核心类型加固锁】确保 history_50 是有效列表，latest_draw 强锁为字典对象
if not isinstance(history_50, list) or len(history_50) == 0:
    history_50 = [{"issue": "2026/058", "date": "2026-05-18", "numbers": [1, 2, 3, 4, 5, 6], "special": 7}]

latest_draw = history_50[0]

# 统计历史频次
freq_map = {i: 0 for i in range(1, 50)}
for draw in history_50:
    if isinstance(draw, dict) and "numbers" in draw:
        for n in draw.get("numbers", []) + [draw.get("special", 7)]:
            if n in freq_map: freq_map[n] += 1

# ----------------- 🚨【管理员全局红牌新用户申请提示系统】 -----------------
if st.session_state.logged_in_user == "admin":
    pending_reg_count = len([k for k, v in db["reg_requests"].items() if v.get("status") == "pending"])
    pending_dep_count = len([d for d in db["deposit_requests"] if d.get("status") == "pending"])
    if pending_reg_count > 0 or pending_dep_count > 0:
        st.markdown(f"""
        <div class="admin-alert-banner">
            🔴 紧急待办通知：当前有 <b>{pending_reg_count}</b> 个新用户申请、<b>{pending_dep_count}</b> 笔充值订单等待您审核处理！
        </div>
        """, unsafe_allow_html=True)

# ----------------- 🔮 统一置顶面板 -----------------
st.markdown('<div class="prophet-logo-title">🔮 预言家模拟控制大厅</div>', unsafe_allow_html=True)

# 渲染置顶开奖球
ball_html = '<div class="draw-container">'
for num in latest_draw['numbers']:
    ball_html += f'<div class="draw-ball {get_ball_style(num)}">{num}</div>'
ball_html += f'<div class="draw-ball {get_ball_style(latest_draw["special"])}">{latest_draw["special"]}</div></div>'
st.markdown(ball_html, unsafe_allow_html=True)

col_info1, col_info2 = st.columns(2)
with col_info1: st.markdown(f"<div style='font-size:12px;color:#333;font-weight:bold;'>📡 第 {latest_draw['issue']} 期开奖</div>", unsafe_allow_html=True)
with col_info2: st.markdown("<div style='font-size:12px;color:#8a2be2;font-weight:bold;text-align:right;'>📢 下期截止：21:15</div>", unsafe_allow_html=True)

st.divider()

# ----------------- 🔐 全网统一鉴权登录注册网关 -----------------
if st.session_state.logged_in_user is None:
    st.subheader("🔑 账户鉴权安全中心")
    log_tab, reg_tab = st.tabs(["🔒 现有账号登入", "📝 新用户申请注册"])
    
    with log_tab:
        l_user = st.text_input("用户名", key="log_u", placeholder="请输入账号").strip()
        l_pass = st.text_input("登录密码", type="password", key="log_p", placeholder="请输入密码")
        if st.button("🚀 开启模拟大厅", key="btn_log"):
            if l_user in db["users"]:
                u_info = db["users"][l_user]
                if u_info["password"] == l_pass:
                    st.session_state.logged_in_user = l_user
                    st.success(f"🎉 荣誉代号 [{l_user}] 鉴权通过！")
                    st.rerun()
                else: st.error("❌ 密码错误！")
            elif l_user in db["reg_requests"] and db["reg_requests"][l_user]["status"] == "pending":
                st.error("❌ 账号处于 [待审核] 状态，请联系管理员核准开通。")
            else: st.error("❌ 该账号未提交申请或密码不匹配！")
            
    with reg_tab:
        r_user = st.text_input("设定新账号", key="reg_u", placeholder="如：jack88").strip()
        r_pass = st.text_input("设定密码", type="password", key="reg_p", placeholder="密码务必牢记")
        if st.button("📥 提交开户申请", key="btn_reg"):
            if not r_user or not r_pass: st.error("⚠️ 账号和密码不能为空！")
            elif r_user in db["users"] or r_user in db["reg_requests"]: st.error("⚠️ 该用户名已被占用或正在等待审核！")
            else:
                db["reg_requests"][r_user] = {"password": r_pass, "status": "pending", "time": datetime.now().strftime("%H:%M")}
                st.success("📩 申请成功！账号已打入全网共享大厅，请通知管理员审批。")
                time.sleep(0.4); st.rerun()
    st.stop()

# ----------------- 👑 后台管理员控制大厅 -----------------
if st.session_state.logged_in_user == "admin":
    st.header("👑 至尊总管理全控后台")
    if st.button("🚪 安全注销退出登录", key="admin_logout"):
        st.session_state.logged_in_user = None
        st.rerun()
        
    p_reg = [k for k, v in db["reg_requests"].items() if v.get("status") == "pending"]
    p_dep = [d for d in db["deposit_requests"] if d.get("status") == "pending"]
    
    adm_menu = st.radio("🛠️ 后台核准大厅", [f"📥 新开户申请审核 ({len(p_reg)})", f"💰 充值订单订单下发 ({len(p_dep)})", "👥 普户资产花名册"])
    
    if "新开户申请审核" in adm_menu:
        st.subheader("📥 普通用户开户申请单列表")
        if not p_reg: st.caption("✅ 暂无任何新开户申请。")
        for u in p_reg:
            col_u1, col_u2 = st.columns(2)
            col_u1.write(f"👤 申请人：**{u}** | 申请时间: {db['reg_requests'][u]['time']}")
            if col_u2.button("✔️ 批准开设", key=f"app_u_{u}"):
                db["users"][u] = {"password": db["reg_requests"][u]["password"], "role": "user", "status": "approved", "wallet": 0.0}
                db["reg_requests"][u]["status"] = "approved"
                st.success(f"已成功为 [{u}] 开设账号，允许登入！")
                st.rerun()
                
    elif "充值订单订单下发" in adm_menu:
        st.subheader("💰 待到账充值订单明细")
        if not p_dep: st.caption("✅ 暂无任何待充值订单。")
        for idx, req in enumerate(db["deposit_requests"]):
            if req.get("status") == "pending":
                col_d1, col_d2 = st.columns(2)
                col_d1.write(f"👤 申请人: **{req['username']}** | 申请金额: **\${req['amount']:,.0f}**")
                if col_d2.button("💸 同步到账", key=f"app_d_{idx}"):
                    db["users"][req["username"]]["wallet"] += req["amount"]
                    db["users"][req["username"]]["status"] = "active" 
                    req["status"] = "approved"
                    st.success(f"成功下发资金！已为用户 [{req['username']}] 增加体验金 \${req['amount']}。")
                    st.rerun()
                    
    elif "普户资产花名册" in adm_menu:
        st.subheader("👥 普通用户余额宏观控盘")
        for name, info in db["users"].items():
            if info.get("role") == "user":
                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.write(f"👤 普户: **{name}**")
                new_bal = col_m2.number_input(f"设余额 ({name})", min_value=0.0, max_value=999999.0, value=float(info["wallet"]), step=100.0, label_visibility="collapsed", key=f"edit_b_{name}")
                if col_m3.button("💾 确改", key=f"save_b_{name}"):
                    db["users"][name]["wallet"] = new_bal
                    if new_bal > 0: db["users"][name]["status"] = "active"
                    st.success(f"已成功将用户 [{name}] 的余额微调强控为 \${new_bal:,.0f}！")
                    st.rerun()
    st.stop()

# ----------------- 👤 普通用户控制台大厅 -----------------
current_user = st.session_state.logged_in_user
user_data = db["users"].get(current_user, {"wallet": 0.0, "status": "approved"})
user_wallet = user_data["wallet"]
has_deposited = user_data.get("status") == "active" and user_wallet > 0

col_w1, col_w2 = st.columns(2)
with col_w1:
    if has_deposited:
        st.markdown(f'<div class="wallet-card-mini">🪙 您的模拟资产余额: \${user_wallet:,.0f}</div>', unsafe_allow_html=True)
    else:
        st.markdown("<div style='height:42px; line-height:42px; font-size:11px; color:#ff3b30; font-weight:bold;'>⚠️ 资产未激活，请在右侧提交金额并通知管理员开通！</div>", unsafe_allow_html=True)

with col_w2:
    col_input, col_btn = st.columns(2)
    with col_input: deposit_amount = st.number_input("充值额", min_value=100, max_value=500000, value=5000, step=100, label_visibility="collapsed", key="u_dep_val")
    with col_btn:
        if st.button("🧧 申请充值", key="u_top_up_btn"):
            db["deposit_requests"].append({"username": current_user, "amount": float(deposit_amount), "status": "pending"})
            st.toast(f"📩 充值申请 \${deposit_amount} 已提交后台！请联系管理员审核。")
            time.sleep(0.4); st.rerun()

st.write("")
if st.button("🚪 安全注销退出登录", key="user_logout"):
    st.session_state.logged_in_user = None
    st.rerun()

# ----------------- 🛠️ 原生药丸玩法导航条 -----------------
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

# ----------------- 🎰 核心选号区 (巧克力方阵) -----------------
if st.session_state.current_tab == "自选平特":
    st.markdown("### 🟢 平特自选（5平码 + 1特码）")
    st.info(f"🛒 篮子明细：平码【{len(st.session_state.manual_ping)}/5】 | 特码【{len(st.session_state.manual_te)}/1】")
    
    st.markdown("**🟠 选 5 个【平码（正码）】：**")
    st.markdown('<div class="num-ball-wrap">', unsafe_allow_html=True)
    for row in range(7):
        cols = st.columns(7) 
        for col in range(7):
            num = row * 7 + col + 1
            if num <= 49:
                is_sel = num in st.session_state.manual_ping
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
    st.markdown("**🔵 选 1 个【特码（特别号码）】：**")
    st.markdown('<div class="num-ball-wrap">', unsafe_allow_html=True)
    for row in range(7):
        cols = st.columns(7)
        for col in range(7):
            num = row * 7 + col + 1
            if num <= 49:
                is_sel = num in st.session_state.manual_te
                cls = "ball-s" if is_sel else get_ball_color_class(num)
                lbl = f"{num}★" if is_sel else f"{num}"
                with cols[col]:
                    st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
                    if st.button(lbl, key=f"te_btn_{num}"):
                        if num in st.session_state.manual_te: st.session_state.manual_te.remove(
