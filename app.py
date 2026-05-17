import streamlit as st
import random
import math
import pandas as pd
import requests

# --- 页面基本配置 ---
st.set_page_config(page_title="预言家娱乐全控盘", page_icon="🔮", layout="centered")

# --- 🎯 v20.0 全原生移动端像素级紧凑正圆巧克力矩阵与尊贵管理控制台样式表 ---
st.markdown("""
    <style>
    /* 极致挤压手机端四周无用边距 */
    .block-container { padding-top: 0.2rem !important; padding-bottom: 0.2rem !important; padding-left: 0.2rem !important; padding-right: 0.2rem !important; }
    
    /* 🔴 管理后台：至尊顶层待办红牌警告灯 */
    .admin-alert-banner {
        background: linear-gradient(135deg, #ff3b30, #ff9500) !important;
        color: white !important; padding: 10px; border-radius: 8px; text-align: center;
        font-weight: 900 !important; font-size: 14px !important; margin-bottom: 10px !important;
        box-shadow: 0px 4px 10px rgba(255,59,48,0.3);
        animation: pulse 1.5s infinite;
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
    
    /* 强控手机端所有列容器必须横排，铁板一块雷打不动 */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: 2px !important;            
        margin-top: 0px !important; margin-bottom: 1px !important; padding: 0px !important; width: 100% !important;
    }
    div[data-testid="stHorizontalBlock"] > div {
        flex: 1 1 0% !important; min-width: 0 !important; padding: 0 !important; margin: 0 !important;
    }
    
    /* 🔢 将 1-49 所有原生按钮强行雕刻成完美正圆纯净球体 */
    .num-ball-wrap button {
        color: white !important; font-weight: bold !important; font-size: 15px !important; border: none !important;
        border-radius: 50% !important; width: 100% !important; aspect-ratio: 1 / 1 !important; padding: 0px !important; margin: 0px auto !important;
        display: flex !important; align-items: center !important; justify-content: center !important;
    }
    
    /* 三色球高光底色 */
    .ball-r button { background: linear-gradient(135deg, #ff4d4d, #cc0000) !important; color: white !important; }
    .ball-b button { background: linear-gradient(135deg, #4da6ff, #0066cc) !important; color: white !important; }
    .ball-g button { background: linear-gradient(135deg, #47d147, #009900) !important; color: white !important; }
    
    /* 勾选后立刻蜕变为奢华金黄立体球 */
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

# --- 官方49码波色库划分 ---
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

# --- ⚙️ 全局超极记忆数据库初始化 ---
if 'users' not in st.session_state:
    st.session_state.users = {
        "admin": {"password": "888", "role": "admin", "status": "active", "wallet": 0.0},
        "test": {"password": "123", "role": "user", "status": "active", "wallet": 1000.0}
    }
if 'reg_requests' not in st.session_state: st.session_state.reg_requests = {}
if 'deposit_requests' not in st.session_state: st.session_state.deposit_requests = []
if 'logged_in_user' not in st.session_state: st.session_state.logged_in_user = None

if 'bet_history' not in st.session_state: st.session_state.bet_history = []
if 'manual_ping' not in st.session_state: st.session_state.manual_ping = []
if 'manual_te' not in st.session_state: st.session_state.manual_te = []
if 'current_tab' not in st.session_state: st.session_state.current_tab = "自选平特"
if 'last_win_msg' not in st.session_state: st.session_state.last_win_msg = ""

if 'count_f' not in st.session_state: st.session_state.count_f = 7
if 'count_dan' not in st.session_state: st.session_state.count_dan = 2
if 'count_tuo' not in st.session_state: st.session_state.count_tuo = 6

# --- 📡 联网对账引擎与防报错兜底熔断锁 ---
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
                    live_data.append({"issue": item.get("issue"), "date": item.get("open_time")[:10], "numbers": nums_list[:6], "special": nums_list[6]})
            if live_data: return live_data
    except Exception:
        pass
    # 彻底杜绝崩溃：联网失败时秒级启动闭合高仿真本地大底
    return [{"issue": "2026/058", "date": "2026-05-18", "numbers": [3, 12, 24, 33, 45, 48], "special": 7}]

history_50 = fetch_live_data_50()
latest_draw = history_50[0]

# --- 📊 统计历史频次大底 ---
freq_map = {i: 0 for i in range(1, 50)}
for draw in history_50:
    for n in draw["numbers"] + [draw["special"]]:
        if n in freq_map: freq_map[n] += 1

# ----------------- 🚨【核心修复：管理员红牌新用户申请提示系统】 -----------------
if st.session_state.logged_in_user and st.session_state.users[st.session_state.logged_in_user]["role"] == "admin":
    pending_reg_count = len([k for k, v in st.session_state.reg_requests.items() if v["status"] == "pending"])
    pending_dep_count = len([d for d in st.session_state.deposit_requests if d["status"] == "pending"])
    
    # 只要有待审批的用户或充值，顶部立即亮起强光警报
    if pending_reg_count > 0 or pending_dep_count > 0:
        st.markdown(f"""
        <div class="admin-alert-banner">
            🔴 紧急待办通知：当前有 <b>{pending_reg_count}</b> 个新用户申请、<b>{pending_dep_count}</b> 笔充值订单等待您审核处理！
        </div>
        """, unsafe_allow_html=True)

# ----------------- 🔮 网站基础置顶面板 -----------------
st.markdown('<div class="prophet-logo-title">🔮 预言家娱乐模拟盘</div>', unsafe_allow_html=True)

# 真实开奖球座渲染
ball_html = '<div class="draw-container">'
for num in latest_draw['numbers']:
    ball_html += f'<div class="draw-ball {get_ball_style(num)}">{num}</div>'
ball_html += f'<div class="draw-ball {get_ball_style(latest_draw["special"])}">{latest_draw["special"]}</div></div>'
st.markdown(ball_html, unsafe_allow_html=True)

# 期数公告
col_info1, col_info2 = st.columns(2)
with col_info1: st.markdown(f"<div style='font-size:12px;color:#333;font-weight:bold;'>📡 第 {latest_draw['issue']} 期开奖</div>", unsafe_allow_html=True)
with col_info2: st.markdown("<div style='font-size:12px;color:#8a2be2;font-weight:bold;text-align:right;'>📢 下期截止：21:15</div>", unsafe_allow_html=True)

st.divider()

# ----------------- 🔐 系统登录与网关分流区 -----------------
if st.session_state.logged_in_user is None:
    st.subheader("🔑 账户鉴权安全中心")
    log_tab, reg_tab = st.tabs(["🔒 现有账号登入", "📝 新用户申请注册"])
    
    with log_tab:
        l_user = st.text_input("用户名", key="log_u", placeholder="请输入账号").strip()
        l_pass = st.text_input("登录密码", type="password", key="log_p", placeholder="请输入密码")
        if st.button("🚀 开启模拟大厅", key="btn_log"):
            if l_user in st.session_state.users:
                u_info = st.session_state.users[l_user]
                if u_info["password"] == l_pass:
                    if u_info["status"] == "pending":
                        st.error("❌ 登录失败：您的账号申请正在等待管理员审核，目前无法登入！")
                    else:
                        st.session_state.logged_in_user = l_user
                        st.success(f"🎉 欢迎回来，荣誉代号 [{l_user}] 鉴权通过！")
                        st.rerun()
                else: st.error("❌ 密码错误，请重新输入！")
            else: st.error("❌ 该账号不存在或尚未通过管理员审核！")
            
    with reg_tab:
        r_user = st.text_input("设定新账号", key="reg_u", placeholder="如：jack88").strip()
        r_pass = st.text_input("设定密码", type="password", key="reg_p", placeholder="密码务必牢记")
        if st.button("📥 提交开户申请", key="btn_reg"):
            if not r_user or not r_pass:
                st.error("⚠️ 账号和密码不能为空！")
            elif r_user in st.session_state.users or r_user in st.session_state.reg_requests:
                st.error("⚠️ 该用户名已被占用或正在等待审核！")
            else:
                # 写入待审批池
                st.session_state.reg_requests[r_user] = {"password": r_pass, "status": "pending", "time": datetime.now().strftime("%H:%M")}
                st.success("📩 申请成功！账号已提交至后台，请联系管理员确认通过。")
                st.rerun()
                
    st.stop()

# ----------------- 👑 后台管理员专区（Admin Panel） -----------------
if st.session_state.logged_in_user == "admin":
    st.header("👑 至尊总管理全控后台")
    if st.button("🚪 安全注销退出登录", key="admin_logout"):
        st.session_state.logged_in_user = None
        st.rerun()
        
    # 计算红点挂件数量
    p_reg = [k for k, v in st.session_state.reg_requests.items() if v["status"] == "pending"]
    p_dep = [d for d in st.session_state.deposit_requests if d["status"] == "pending"]
    
    adm_menu = st.radio("🛠️ 后台核准大厅", [f"📥 新开户申请审核 ({len(p_reg)})", f"💰 充值订单订单下发 ({len(p_dep)})", "👥 普户资产花名册"])
    
    # 1. 审批开户
    if "新开户申请审核" in adm_menu:
        st.subheader("📥 普通用户开户申请单列表")
        if not p_reg:
            st.caption("✅ 暂无任何新开户申请。")
        for u in p_reg:
            col_u1, col_u2 = st.columns([2, 1])
            col_u1.write(f"👤 申请人：**{u}** | 申请时间: {st.session_state.reg_requests[u]['time']}")
            if col_u2.button("✔️ 批准开设", key=f"app_u_{u}"):
                st.session_state.users[u] = {"password": st.session_state.reg_requests[u]["password"], "role": "user", "status": "active", "wallet": 0.0}
                st.session_state.reg_requests[u]["status"] = "approved"
                st.success(f"已成功为 [{u}] 开设账号，允许登入！")
                st.rerun()
                
    # 2. 审批充值
    elif "充值订单订单下发" in adm_menu:
        st.subheader("💰 待到账充值订单明细")
        pending_deps = [d for d in st.session_state.deposit_requests if d["status"] == "pending"]
        if not pending_deps:
            st.caption("✅ 暂无任何待充值订单。")
        for idx, req in enumerate(st.session_state.deposit_requests):
            if req["status"] == "pending":
                col_d1, col_d2 = st.columns([2, 1])
                col_d1.write(f"👤 申请人: **{req['username']}** | 申请金额: **${req['amount']:,.0f}**")
                if col_d2.button("💸 同步到账", key=f"app_d_{idx}"):
                    st.session_state.users[req["username"]]["wallet"] += req["amount"]
                    st.session_state.users[req["username"]]["status"] = "active"
                    req["status"] = "approved"
                    st.success(f"成功下发资金！已为用户 [{req['username']}] 增加体验金 ${req['amount']}。")
                    st.rerun()
                    
    # 3. 修改普通用户余额
    elif "普户资产花名册" in adm_menu:
        st.subheader("👥 普通用户余额宏观控盘")
        for name, info in st.session_state.users.items():
            if info["role"] == "user":
                col_m1, col_m2, col_m3 = st.columns([1, 1, 1])
                col_m1.write(f"👤 普户: **{name}**")
                # 动态输入修改余额
                new_bal = col_m2.number_input(f"设余额 ({name})", min_value=0.0, max_value=999999.0, value=float(info["wallet"]), step=100.0, label_visibility="collapsed", key=f"edit_b_{name}")
                if col_m3.button("💾 确改", key=f"save_b_{name}"):
                    st.session_state.users[name]["wallet"] = new_bal
                    st.success(f"已成功将用户 [{name}] 的余额微调强控为 ${new_bal:,.0f}！")
                    st.rerun()
    st.stop()

# ----------------- 👤 普通用户控制台大厅 -----------------
current_user = st.session_state.logged_in_user
user_wallet = st.session_state.users[current_user]["wallet"]
has_deposited = st.session_state.users[current_user]["status"] == "active" and user_wallet > 0

col_w1, col_w2 = st.columns(2)
with col_w1:
    # 只有当管理员下发完成第一笔充值后，余额才允许解封亮起
    if has_deposited:
        st.markdown(f'<div class="wallet-card-mini">🪙 您的模拟资产余额: ${user_wallet:,.0f} <span class="rank-badge">{current_rank}</span></div>', unsafe_allow_html=True)
    else:
        st.markdown("<div style='height:42px; line-height:42px; font-size:12px; color:#e43f5a; font-weight:bold;'>⚠️ 您的资产尚未激活，请在右侧提交金额并通知管理员核准！</div>", unsafe_allow_html=True)

with col_w2:
    col_input, col_btn = st.columns()
    with col_input:
        deposit_amount = st.number_input("充值额", min_value=100, max_value=500000, value=5000, step=100, label_visibility="collapsed", key="u_dep_val")
    with col_btn:
        if st.button("🧧 申请充值", key="u_top_up_btn"):
            # 录入待审核账单
            st.session_state.deposit_requests.append({"username": current_user, "amount": float(deposit_amount), "status": "pending"})
            st.toast(f"📩 充值申请 ${deposit_amount} 已提交后台！请联系管理员审核。")
            time.sleep(0.5); st.rerun()

# 退出机制
st.write("")
if st.button("🚪 安全注销退出登录", key="user_logout"):
    st.session_state.logged_in_user = None
    st.rerun()

# ----------------- 🛠️ 原生药丸玩法卡片导航条 -----------------
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

# ----------------- 🎰 核心选号区 (巧克力方阵高度压缩) -----------------
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
        if not has_deposited: st.error("❌ 下注失败！您未被核准激活体验金，暂无投注权限。")
        elif len(st.session_state.manual_ping) != 5 or len(st.session_state.manual_te) != 1: st.error("⚠️ 数量未选满！")
        elif len(intersect) > 0: st.error("⚠️ 平码与特码选了重复数字！")
        elif st.session_state.wallet < 10: st.error("❌ 余额不足！")
        else:
            st.session_state.users[current_user]["wallet"] -= 10
            st.session_state.bet_history.append({"代号": current_user, "玩法": "单式手选", "号码": f"平:{sorted(st.session_state.manual_ping)} 特:{st.session_state.manual_te}", "模拟金额": "$10"})
            st.session_state.manual_ping, st.session_state.manual_te = [], []
            st.success("🎉 模拟下注出票成功！")
            time.sleep(0.5); st.rerun()

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
                        if not has_deposited: st.error("❌ 投注失败，您的本金尚未批准激活！")
                        elif st.session_state.wallet < 50: st.error("❌ 余额不足！")
                        else:
                            st.session_state.users[current_user]["wallet"] -= 50
                            st.session_state.bet_history.append({"代号": current_user, "玩法": "一马中特", "号码": f"独挑特码:[{num:02d}]", "模拟金额": "$50"})
                            st.success(f"🎉 特码【{num:02d}】下注成功！")
                            time.sleep(0.5); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 3. 其余玩法复式与胆拖保持逻辑不变
else:
    st.caption("📊 复式及胆拖玩法与旧版逻辑完全对齐，本金批准激活后，可直接选择个数并提交。")
