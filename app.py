import streamlit as st
import random
import math
import pandas as pd
import requests
import time
import copy
from datetime import datetime

# --- 页面基本配置 ---
st.set_page_config(page_title="预言家娱乐全控盘", page_icon="🔮", layout="centered")

# --- 🎯 v26.0 全网跨设备共享数据总线终极稳固版样式表 ---
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

# --- 官方49码波色划分 ---
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

# --- 👑 全网唯一共享资源数据库中心 ---
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

# 提取物理唯一的单例数据结构
global_db = init_global_shared_db()

# 会话隔离私有身份状态锁
if 'logged_in_user' not in st.session_state: st.session_state.logged_in_user = None
if 'manual_ping' not in st.session_state: st.session_state.manual_ping = []
if 'manual_te' not in st.session_state: st.session_state.manual_te = []
if 'current_tab' not in st.session_state: st.session_state.current_tab = "自选平特"
if 'last_win_msg' not in st.session_state: st.session_state.last_win_msg = ""
if 'count_f' not in st.session_state: st.session_state.count_f = 7
if 'count_dan' not in st.session_state: st.session_state.count_dan = 2
if 'count_tuo' not in st.session_state: st.session_state.count_tuo = 6

# --- 📡 联网数据采集引擎与熔断器 ---
@st.cache_data(ttl=3600)
def fetch_live_data_50():
    fallback_data = [{"issue": "2026/058", "date": "2026-05-18", "numbers": [1, 8, 12, 23, 29, 34], "special": 7}]
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
latest_draw = history_50[0] if (history_50 and isinstance(history_50, list)) else {"issue": "2026/058", "date": "2026-05-18", "numbers": [1, 8, 12, 23, 29, 34], "special": 7}

# 统计历史频次
freq_map = {i: 0 for i in range(1, 50)}
for draw in history_50:
    if "numbers" in draw:
        for n in draw.get("numbers", []) + [draw.get("special", 7)]:
            if n in freq_map: freq_map[n] += 1

# ----------------- 🚨【管理员全局红牌新用户申请提示系统】 -----------------
if st.session_state.logged_in_user == "admin":
    pending_reg_count = len([k for k, v in global_db["reg_requests"].items() if v.get("status") == "pending"])
    pending_dep_count = len([d for d in global_db["deposit_requests"] if d.get("status") == "pending"])
    if pending_reg_count > 0 or pending_dep_count > 0:
        st.markdown(f"""
        <div class="admin-alert-banner">
            🔴 紧急待办通知：当前有 <b>{pending_reg_count}</b> 个新用户申请、<b>{pending_dep_count}</b> 笔充值订单等待您审核处理！
        </div>
        """, unsafe_allow_html=True)

# ----------------- 🔮 统一置顶看板 -----------------
st.markdown('<div class="prophet-logo-title">🔮 预言家模拟控制大厅</div>', unsafe_allow_html=True)

ball_html = '<div class="draw-container">'
for num in latest_draw['numbers']:
    ball_html += f'<div class="draw-ball {get_ball_style(num)}">{num}</div>'
ball_html += f'<div class="draw-ball {get_ball_style(latest_draw["special"])}">{latest_draw["special"]}</div></div>'
st.markdown(ball_html, unsafe_allow_html=True)

col_info1, col_info2 = st.columns(2)

# --- 完美无缝闭合报错节点 ---
with col_info1: 
    st.markdown(f"<div style='font-size:12px;color:#888;font-weight:bold;text-align:left;'>📡 最新期号: {latest_draw['issue']} ({latest_draw['date']})</div>", unsafe_allow_html=True)
with col_info2:
    current_user = st.session_state.logged_in_user
    wallet_val = global_db["users"][current_user]["wallet"] if current_user in global_db["users"] else 0.0
    role_badge = f"<span class='rank-badge'>管理员</span>" if current_user == "admin" else (f"<span class='rank-badge'>玩家</span>" if current_user else "")
    user_display = f"{current_user}{role_badge}" if current_user else "未登录"
    st.markdown(f"<div class='wallet-card-mini'>👤 {user_display} | 💰 钱包: ¥{wallet_val:,.2f}</div>", unsafe_allow_html=True)

st.write("---")

# ----------------- 🔐 账户与登录管理面板 -----------------
if not st.session_state.logged_in_user:
    st.subheader("🔑 预言家核心数据总线隔离登录")
    tab_log, tab_reg = st.tabs(["🔐 账户登录", "📝 新用户注册申请"])
    
    with tab_log:
        login_user = st.text_input("用户名", key="log_u", placeholder="请输入用户名")
        login_pwd = st.text_input("密码", type="password", key="log_p", placeholder="请输入密码")
        if st.button("🔥 立即重载并登录验证"):
            if login_user in global_db["users"] and global_db["users"][login_user]["password"] == login_pwd:
                if global_db["users"][login_user].get("status") == "active" or login_user == "admin":
                    st.session_state.logged_in_user = login_user
                    st.success(f"🎉 登录成功！欢迎进入控制盘，当前身份：{login_user}")
                    st.rerun()
                else:
                    st.error("❌ 该账号尚未通过管理员审核或已被禁用！")
            else:
                st.error("❌ 用户名或密码错误，请检查！")
                
    with tab_reg:
        reg_user = st.text_input("期望用户名", key="reg_u", placeholder="数字或英文字母")
        reg_pwd = st.text_input("设置登录密码", type="password", key="reg_p")
        if st.button("🚀 提交入网审核申请"):
            if reg_user in global_db["users"] or reg_user in global_db["reg_requests"]:
                st.error("⚠️ 该用户名已存在或正在审核中，请更换！")
            elif not reg_user or not reg_pwd:
                st.error("⚠️ 用户名和密码不能为空！")
            else:
                global_db["reg_requests"][reg_user] = {"password": reg_pwd, "status": "pending", "time": datetime.now().strftime("%Y-%m-%d %H:%M")}
                st.success("🎯 申请已提交物理单例总线！请联系管理员实时过审。")

else:
    # ----------------- 👑 管理员独立全控后台 -----------------
    if st.session_state.logged_in_user == "admin":
        with st.sidebar.expander("🛠️ 至尊顶层全盘控制后台", expanded=True):
            st.markdown("### 👥 新用户注册极速过审区")
            pending_regs = [k for k, v in global_db["reg_requests"].items() if v.get("status") == "pending"]
            if not pending_regs:
                st.info("暂无待处理的用户注册申请")
            for u in pending_regs:
                col_r1, col_r2 = st.columns(2)
                with col_r1: st.text(f"用户: {u}")
                with col_r2:
                    if st.button("✅ 批准", key=f"app_{u}"):
                        global_db["users"][u] = {"password": global_db["reg_requests"][u]["password"], "role": "user", "status": "active", "wallet": 0.0}
                        global_db["reg_requests"][u]["status"] = "approved"
                        st.success(f"已批准用户 {u}")
                        st.rerun()

            st.markdown("### 💰 线上充值订单核销中心")
            pending_deps = [d for d in global_db["deposit_requests"] if d.get("status") == "pending"]
            if not pending_deps:
                st.info("暂无待核销的充值订单")
            for idx, dep in enumerate(pending_deps):
                col_d1, col_d2 = st.columns(2)
                with col_d1: st.text(f"{dep['user']} 充值 ¥{dep['amount']}")
                with col_d2:
                    if st.button("🪙 确认入账", key=f"dep_{idx}"):
                        if dep['user'] in global_db["users"]:
                            global_db["users"][dep['user']]["wallet"] += dep['amount']
                            dep["status"] = "approved"
                            st.success(f"已为 {dep['user']} 充值 ¥{dep['amount']}")
                            st.rerun()
            
            if st.button("🚪 退出管理员模式"):
                st.session_state.logged_in_user = None
                st.rerun()

    # ----------------- 🎮 核心模拟下注交互区 -----------------
    st.session_state.current_tab = st.radio("切换下注模拟玩法", ["自选平特", "胆拖组合玩法", "财务充值中心"], horizontal=True)

    if st.session_state.current_tab == "自选平特":
        st.subheader("🔮 49码平特高光自选矩阵")
        
        # 49码完美正圆矩阵渲染（每行7个，强控手机端横排）
        selected_balls = st.session_state.manual_ping
        for i in range(0, 49, 7):
            cols = st.columns(7)
            for j in range(7):
                num = i + j + 1
                if num <= 49:
                    is_selected = num in selected_balls
                    color_cls = "ball-s" if is_selected else get_ball_color_class(num)
                    with cols[j]:
                        st.markdown(f"<div class='num-ball-wrap {color_cls}'>", unsafe_allow_html=True)
                        if st.button(f"{num:02d}", key=f"btn_ping_{num}"):
                            if num in selected_balls: selected_balls.remove(num)
                            else: selected_balls.append(num)
                            st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)

        st.info(f"当前已选平特号码：{sorted(selected_balls)}")
        bet_amt = st.number_input("下单金额 (¥)", min_value=10.0, step=10.0, key="amt_p")
        
        if st.button("🔥 确认提交平特模拟注单"):
            u_name = st.session_state.logged_in_user
            if global_db["users"][u_name]["wallet"] < bet_amt:
                st.error("❌ 余额不足！请前往财务中心申请充值。")
            elif not selected_balls:
                st.error("❌ 请至少选择一个号码进行模拟投注！")
            else:
                global_db["users"][u_name]["wallet"] -= bet_amt
                global_db["bet_history"].append({
                    "user": u_name, "type": "自选平特", "balls": list(selected_balls), "amount": bet_amt, "time": datetime.now().strftime("%H:%M:%S")
                })
                st.success("🎯 模拟下注成功！扣款已同步至物理总线。")
                st.session_state.manual_ping = [] # 清空选择
                st.rerun()

    elif st.session_state.current_tab == "胆拖组合玩法":
        st.subheader("🎲 胆拖高级组合器")
        col_dan, col_tuo = st.columns(2)
        with col_dan:
            dan_balls = st.multiselect("选择胆码（必开核心码）", range(1, 49), max_selections=3)
        with col_tuo:
            tuo_balls = st.multiselect("选择拖码（辅助组合码）", [x for x in range(1, 49) if x not in dan_balls])
            
        if dan_balls and tuo_balls:
            comb_count = math.comb(len(tuo_balls), 2)
            st.warning(f"💡 当前组合计算：共可生成平特组合数：{comb_count} 组")

    elif st.session_state.current_tab == "财务充值中心":
        st.subheader("💰 玩家模拟财务自助通道")
        u_name = st.session_state.logged_in_user
        st.metric("您的当前物理钱包余额", f"¥ {global_db['users'][u_name]['wallet']:,.2f}")
        
        dep_amt = st.number_input("请输入模拟充值金额", min_value=100.0, max_value=100000.0, step=100.0)
        if st.button("🏦 提交金流充值工单"):
            global_db["deposit_requests"].append({"user": u_name, "amount": dep_amt, "status": "pending"})
            st.success("🚀 充值工单已打入物理总线后台！请切换至 admin 账户进行‘确认入账’操作。")

    # --- 退出登录大底栏 ---
    st.write("---")
    if st.button("🚪 退出当前玩家账户"):
        st.session_state.logged_in_user = None
        st.rerun()
