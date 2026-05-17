import streamlit as st
import random
import math
import pandas as pd
from datetime import datetime

# --- 页面基础配置 ---
st.set_page_config(page_title="预言家娱乐模拟盘 v20.0", page_icon="🔮", layout="wide")

# --- 🎯 顶级移动端紧凑样式表（双模独立隔离版） ---
st.markdown("""
    <style>
    .block-container { padding-top: 0.3rem !important; padding-bottom: 0.3rem !important; padding-left: 0.3rem !important; padding-right: 0.3rem !important; }
    
    /* 预言家核心大横幅 */
    .prophet-logo-title {
        text-align: center !important; font-size: 22px !important; font-weight: 900 !important;
        background: linear-gradient(135deg, #ffd700, #8a2be2, #00f2fe) !important;
        -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important;
        margin-bottom: 8px !important; letter-spacing: 2px !important;
    }
    
    /* 强控手机端所有列容器必须横排 */
    div[data-testid="stHorizontalBlock"] { display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: 2px !important; margin-bottom: 1px !important; padding: 0px !important; width: 100% !important; }
    div[data-testid="stHorizontalBlock"] > div { flex: 1 1 0% !important; min-width: 0 !important; padding: 0 !important; margin: 0 !important; }
    
    /* 🔢 1-49 号码按钮完美正圆体样式 */
    .num-ball-wrap button {
        color: white !important; font-weight: bold !important; font-size: 15px !important; border: none !important;
        border-radius: 50% !important; width: 100% !important; aspect-ratio: 1 / 1 !important; padding: 0px !important; margin: 0px auto !important;
        display: flex !important; align-items: center !important; justify-content: center !important;
    }
    .ball-r button { background: linear-gradient(135deg, #ff4d4d, #cc0000) !important; color: white !important; }
    .ball-b button { background: linear-gradient(135deg, #4da6ff, #0066cc) !important; color: white !important; }
    .ball-g button { background: linear-gradient(135deg, #47d147, #009900) !important; color: white !important; }
    .ball-s button { background: linear-gradient(135deg, #ffd700, #ff8c00) !important; color: #1a1a1a !important; font-weight: 900 !important; border: 1.5px solid #ffffff !important; box-shadow: 0px 0px 5px #ffd700 !important; }
    
    /* 开奖号排布 */
    .draw-container { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 4px; justify-content: center; }
    .draw-ball { width: 36px; height: 36px; line-height: 36px; border-radius: 50%; color: white; text-align: center; font-weight: bold; font-size: 14px; box-shadow: 1px 2px 4px rgba(0,0,0,0.15); }
    .draw-red { background: linear-gradient(135deg, #ff4d4d, #cc0000); }
    .draw-blue { background: linear-gradient(135deg, #4da6ff, #0066cc); }
    .draw-green { background: linear-gradient(135deg, #47d147, #009900); }
    
    .wallet-card-mini { background: linear-gradient(135deg, #111, #222); color: #ffd700; padding: 6px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 12px; border: 1px solid #333; }
    .rank-badge { background: #8a2be2; color: white; padding: 1px 4px; border-radius: 5px; font-size: 10px; margin-left: 2px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🧱 官方49码严格定义波色模块 ---
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

# --- 💾 核心商用数据库字典树状态初始化 ---
if 'user_db' not in st.session_state:
    st.session_state.user_db = {
        "admin": {"pwd": "666", "status": "approved", "balance": 999999.0},
        "test01": {"pwd": "123", "status": "locked", "balance": 0.0}
    }
if 'pending_deposits' not in st.session_state: st.session_state.pending_deposits = []
if 'logged_user' not in st.session_state: st.session_state.logged_user = None
if 'user_role' not in st.session_state: st.session_state.user_role = None

# 投注临时篮子与选项初始化
if 'manual_ping' not in st.session_state: st.session_state.manual_ping = []
if 'manual_te' not in st.session_state: st.session_state.manual_te = []
if 'bet_history' not in st.session_state: st.session_state.bet_history = []
if 'current_tab' not in st.session_state: st.session_state.current_tab = "自选平特"
if 'last_win_msg' not in st.session_state: st.session_state.last_win_msg = ""
if 'count_f' not in st.session_state: st.session_state.count_f = 7
if 'count_dan' not in st.session_state: st.session_state.count_dan = 2
if 'count_tuo' not in st.session_state: st.session_state.count_tuo = 6

# --- 📡 仿真网络开奖库（100%消灭网络断连导致的TypeError报错） ---
latest_draw = {"issue": "26/052", "date": "2026-05-18", "numbers": [1, 14, 19, 23, 27, 34], "special": 49}

# ==================== 🛠️ 顶层布局分流控制 ====================
st.markdown('<div class="prophet-logo-title">🔮 预言家 (The Prophet) 模拟双模大厅</div>', unsafe_allow_html=True)

# 1. 未登录状态网关
if st.session_state.logged_user is None:
    st.subheader("🔑 独立账户网关中心")
    log_tab1, log_tab2 = st.tabs(["🔒 用户登录入口", "📝 申请开设有奖账号"])
    
    with log_tab1:
        in_user = st.text_input("请输入账号名称:", key="login_u").strip()
        in_pwd = st.text_input("请输入登录密码:", type="password", key="login_p").strip()
        if st.button("🚀 安全确认登录", use_container_width=True):
            if in_user in st.session_state.user_db:
                if st.session_state.user_db[in_user]["pwd"] == in_pwd:
                    if st.session_state.user_db[in_user]["status"] == "approved":
                        st.session_state.logged_user = in_user
                        st.session_state.user_role = "admin" if in_user == "admin" else "user"
                        st.success(f"🎉 账户【{in_user}】登录验证通过！正在跳转大厅...")
                        st.rerun()
                    else:
                        st.error("❌ 登录失败！您的账户当前尚未通过管理员批准审核，请联系主理人开启权限！")
                else: st.error("❌ 密码错误，请重新输入！")
            else: st.error("❌ 该账号名称不存在，请先前往开户申请！")
            
    with log_tab2:
        reg_user = st.text_input("自定义新账号名称:", key="reg_u").strip()
        reg_pwd = st.text_input("设置高强度登录密码:", type="password", key="reg_p").strip()
        if st.button("📨 提交开户申请给管理员", use_container_width=True):
            if not reg_user or not reg_pwd: st.warning("⚠️ 账号和密码不能为空！")
            elif reg_user in st.session_state.user_db: st.error("❌ 该账号名称已被注册，请换一个名称试一试！")
            else:
                st.session_state.user_db[reg_user] = {"pwd": reg_pwd, "status": "locked", "balance": 0.0}
                st.success(f"🎉 申请成功！账号【{reg_user}】已成功上报，请等待管理员点击批准后即可登录！")

# 2. 验证成功登录后的前台/后台大分流
else:
    # 顶部状态与安全退出挂件
    col_out1, col_out2 = st.columns([3, 1])
    with col_out1:
        st.markdown(f"👤 当前在线: **{st.session_state.logged_user}** ({'✨ 超级管理员' if st.session_state.user_role=='admin' else '普通彩民'})")
    with col_out2:
        if st.button("⚠️ 安全登出", use_container_width=True):
            st.session_state.logged_user = None
            st.session_state.user_role = None
            st.rerun()
            
    st.divider()

    # ==================== 🛠️ 【ADMIN】超级管理员后台控制台 ====================
    if st.session_state.user_role == "admin":
        st.header("⚙️ 预言家超级上帝控制后台")
        
        adm_box1, adm_box2, adm_box3 = st.tabs(["👥 审批账号与直接修改余额", "🪙 充值审核流水链", "🎰 前台投注实测"])
        
        with adm_box1:
            st.subheader("⚡ 账号库动态直接控制面板")
            for u_name, u_info in list(st.session_state.user_db.items()):
                if u_name == "admin": continue
                c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
                c1.write(f"**用户**: `{u_name}`")
                c2.write(f"状态: `{'🟢 已通过' if u_info['status']=='approved' else '🔴 待通过'}`")
                
                # 动作A：审核允许开户登录
                if u_info['status'] == "locked":
                    if c3.button("✅ 批准开户", key=f"appr_{u_name}"):
                        st.session_state.user_db[u_name]["status"] = "approved"
                        st.success(f"账号【{u_name}】已被允许登录！")
                        st.rerun()
                else:
                    if c3.button("🔒 封禁冻结", key=f"lock_{u_name}"):
                        st.session_state.user_db[u_name]["status"] = "locked"
                        st.rerun()
                        
                # 动作B：直接无损硬改余额
                new_bal = c4.number_input(f"硬改【{u_name}】余额:", value=float(u_info["balance"]), step=100.0, key=f"bal_edit_{u_name}")
                if new_bal != u_info["balance"]:
                    st.session_state.user_db[u_name]["balance"] = float(new_bal)
                    st.toast(f"已直接将【{u_name}】的模拟余额修改为: ${new_bal}")
                    st.rerun()
                    
        with adm_box2:
            st.subheader("📥 待确认充值交易单明细")
            if not st.session_state.pending_deposits:
                st.caption("📂 暂无任何普通用户提交的充值申请流水。")
            else:
                for idx, item in enumerate(st.session_state.pending_deposits):
                    dc1, dc2, dc3, dc4 = st.columns(4)
                    dc1.write(f"申请人: `{item['user']}`")
                    dc2.write(f"欲充值金额: **${item['amount']}**")
                    if dc3.button("👍 同意充值", key=f"agree_{idx}"):
                        st.session_state.user_db[item['user']]["balance"] += float(item['amount'])
                        st.session_state.pending_deposits.pop(idx)
                        st.success("资金已真正注入该用户钱包！")
                        st.rerun()
                    if dc4.button("❌ 驳回作废", key=f"rej_{idx}"):
                        st.session_state.pending_deposits.pop(idx)
                        st.rerun()
                        
        with adm_box3:
            st.caption("💡 管理员可在此查看前台系统运行稳定性。")

    # ==================== 📱 【USER】普通合法用户前台投注台 ====================
    if st.session_state.user_role == "user" or st.session_state.user_role == "admin":
        if st.session_state.user_role == "admin":
            st.markdown("---")
            st.subheader("🎰 模拟盘前台预览")
            
        cur_user = st.session_state.logged_user
        user_balance = st.session_state.user_db[cur_user]["balance"]
        
        # 🎯【置顶：置顶开奖号码盘】
        ball_html = '<div class="draw-container">'
        for num in latest_draw['numbers']:
            ball_html += f'<div class="draw-ball {get_ball_style(num)}">{num}</div>'
        ball_html += f'<div class="draw-ball {get_ball_style(latest_draw["special"])}">{latest_draw["special"]}</div></div>'
        st.markdown(ball_html, unsafe_allow_html=True)
        
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.markdown(f"<div style='font-size:12px;color:#333;font-weight:bold;'>📡 第 {latest_draw['issue']} 期开奖 </div>", unsafe_allow_html=True)
        with col_info2:
            st.markdown("<div style='font-size:12px;color:#8a2be2;font-weight:bold;text-align:right;'>📢 下期截止：05-19 21:15</div>", unsafe_allow_html=True)
            
        # 🪙【核心机制：只有当管理员通过充值后，余额栏才会亮起数额】
        col_w1, col_w2 = st.columns(2)
        with col_w1:
            if user_balance > 0:
                st.markdown(f'<div class="wallet-card-mini">🪙 您的余额: ${user_balance:,.0f} <span class="rank-badge">🌟预言家</span></div>', unsafe_allow_html=True)
            else:
                st.markdown("<div class='wallet-card-mini' style='color:#aaa;'>🪙 余额: $0 (充值等待管理员批准)</div>", unsafe_allow_html=True)
        with col_w2:
            col_input, col_btn = st.columns([2, 1])
            with col_input:
                req_amt = st.number_input("充值额", min_value=100, max_value=50000, value=5000, step=100, label_visibility="collapsed", key="user_dep_input")
            with col_btn:
                if st.button("🧧 申请充值", key="user_dep_btn", use_container_width=True):
                    st.session_state.pending_deposits.append({"user": cur_user, "amount": req_amt})
                    st.toast(f"充值申请已上报！请等待管理员确认通过。")
                    st.rerun()
                    
        # 🛠️ 纯原生药丸玩法导航大厅
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
        
        # 🎰 巧克力矩阵核心选号区
        st.markdown('<div class="num-ball-wrap">', unsafe_allow_html=True)
        
        if st.session_state.current_tab == "自选平特":
            st.markdown(f"🛒 选号篮子：平码【{len(st.session_state.manual_ping)}/5】 | 特码【{len(st.session_state.manual_te)}/1】")
            st.markdown("**🟠 选 5 个【平码（正码）】：**")
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
                            
            st.write("")
            st.markdown("**🔵 选 1 个【特码（特别号码）】：**")
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
                            
            st.write("")
            col_o1, col_o2 = st.columns(2)
            if col_o1.button("🗑️ 清空篮子", key="clear_m"):
                st.session_state.manual_ping, st.session_state.manual_te = [], []
                st.rerun()
            if col_o2.button("🛒 确认下注扣款", key="submit_m"):
                intersect = set(st.session_state.manual_ping) & set(st.session_state.manual_te)
                if user_balance < 10: st.error("❌ 余额不足或尚未获得管理员充值批准！")
                elif len(st.session_state.manual_ping) != 5 or len(st.session_state.manual_te) != 1: st.error("⚠️ 数量未选满！")
                elif len(intersect) > 0: st.error("⚠️ 平码与特码选了重复数字！")
                else:
                    st.session_state.user_db[cur_user]["balance"] -= 10
                    st.session_state.bet_history.append({"玩法": "手选单式", "所选号码": f"平:{sorted(st.session_state.manual_ping)} 特:{st.session_state.manual_te}", "原始数据": {"ping": sorted(st.session_state.manual_ping), "te": st.session_state.manual_te}, "状态": "等待开奖"})
                    st.session_state.manual_ping, st.session_state.manual_te = [], []
                    st.success("🎉 下注成功！")
                    st.rerun()

        elif st.session_state.current_tab == "一马中特":
            st.markdown("### 🎯 一马中特单挑（每注$50）")
            for row in range(7):
                cols = st.columns(7)
                for col in range(7):
                    num = row * 7 + col + 1
                    if num <= 49:
                        with cols[col]:
                            st.markdown(f'<div class="{get_ball_color_class(num)}">', unsafe_allow_html=True)
                            if st.button(f"{num}", key=f"one_match_{num}"):
                                if user_balance < 50: st.error("❌ 余额不足或账户尚未审核充值！")
                                else:
                                    st.session_state.user_db[cur_user]["balance"] -= 50
                                    st.session_state.bet_history.append({"玩法": "一马中特", "所选号码": f"特码:[{num:02d}]", "原始数据": {"ping": [], "te": num}, "状态": "等待开奖"})
                                    st.success(f"🎉 特码【{num:02d}】成功下注！")
                                    st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.current_tab == "标准复式":
            st.markdown("### 📊 标准复式加减盘")
            col_f_sub, col_f_val, col_f_add = st.columns(3)
            with col_f_sub:
                if st.button("➖ 减少 1 码", key="sub_f_num") and st.session_state.count_f > 7: st.session_state.count_f -= 1; st.rerun()
            with col_f_val: st.markdown(f"<h4 style='text-align:center;'>选择大底：{st.session_state.count_f} 个号</h4>", unsafe_allow_html=True)
            with col_f_add:
                if st.button("➕ 增加 1 码", key="add_f_num") and st.session_state.count_f < 12: st.session_state.count_f += 1; st.rerun()
            total_notes = math.comb(st.session_state.count_f, 6)
            cost_f = total_notes * 10
            st.info(f"📊 该复式折合共 **{total_notes}** 注 | 需从钱包扣除：**HK$ {cost_f}**")
            if st.button("🛒 确认提交复式投注", key="sub_f_bet"):
                if user_balance < cost_f: st.error("❌ 余额不足！")
                else:
                    st.session_state.user_db[cur_user]["balance"] -= cost_f
                    f_nums = sorted(random.sample(range(1, 50), st.session_state.count_f))
                    st.session_state.bet_history.append({"玩法": f"复式({st.session_state.count_f}码)", "所选号码": str(f_nums), "原始数据": {"ping": f_nums, "te": None}, "状态": "等待开奖"})
                    st.success("🎉 复式注单生成成功！"); st.rerun()

        elif st.session_state.current_tab == "黄金胆拖":
            st.markdown("### 🎲 胆拖组合盘")
            st.write("1. 调节【胆码】个数 (1-5个)：")
            cd1, cd2, cd3 = st.columns(3)
            if cd1.button("➖ 减胆", key="d_sub") and st.session_state.count_dan > 1: st.session_state.count_dan -= 1; st.rerun()
            cd2.markdown(f"<div style='text-align:center;font-weight:bold;'>当前胆码：{st.session_state.count_dan} 个</div>", unsafe_allow_html=True)
            if cd3.button("➕ 加胆", key="d_add") and st.session_state.count_dan < 5: st.session_state.count_dan += 1; st.rerun()
            st.write("2. 调节【拖码】个数：")
            ct1, ct2, ct3 = st.columns(3)
            if ct1.button("➖ 减拖", key="t_sub") and st.session_state.count_tuo > (7 - st.session_state.count_dan): st.session_state.count_tuo -= 1; st.rerun()
            ct2.markdown(f"<div style='text-align:center;font-weight:bold;'>当前拖码：{st.session_state.count_tuo} 个</div>", unsafe_allow_html=True)
            if ct3.button("➕ 加拖", key="t_add") and st.session_state.count_tuo < 15: st.session_state.count_tuo += 1; st.rerun()
            total_notes_dt = math.comb(st.session_state.count_tuo, 6 - st.session_state.count_dan)
            cost_dt = total_notes_dt * 10
            st.info(f"📊 该胆拖组合折合共 **{total_notes_dt}** 注 | 需模拟金：**HK$ {cost_dt}**")
            if st.button("🛒 确认提交胆拖投注", key="sub_dt_bet"):
                if user_balance < cost_dt: st.error("❌ 余额不足！")
                else:
                    st.session_state.user_db[cur_user]["balance"] -= cost_dt
                    pool = list(range(1, 50))
                    random.shuffle(pool)
                    dans = sorted(pool[:st.session_state.count_dan])
                    tuos = sorted(pool[st.session_state.count_dan : st.session_state.count_dan + st.session_state.count_tuo])
                    st.session_state.bet_history.append({"玩法": "胆拖组合", "所选号码": f"胆:{dans} 拖:{tuos}", "原始数据": {"ping": tuos, "te": dans}, "状态": "等待开奖"})
                    st.success("🎉 胆拖组合下注成功！"); st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        # --- 账单存根派彩 ---
        st.divider()
        st.header("🧾 模拟投注账单存根")
        if st.session_state.bet_history:
            if st.button("🔥 一键对奖·全量结算", key="pay_eng"):
                win_main = latest_draw["numbers"]
                win_special = latest_draw["special"]
                for bet in st.session_state.bet_history:
                    if bet["状态"] == "等待开奖":
                        raw = bet["原始数据"]
                        if "ping" in raw:
                            match_m = len(set(raw["ping"]) & set(win_main))
                            match_s = (raw["te"] == win_special)
                            if match_m == 6: st.session_state.user_db[cur_user]["balance"] += 50000.0; bet["状态"] = "🎉 头奖！+$5万"
                            elif match_m == 3: st.session_state.user_db[cur_user]["balance"] += 40.0; bet["状态"] = "🎉 七奖+$40"
                            elif match_s: st.session_state.user_db[cur_user]["balance"] += 20.0; bet["状态"] = "🎉 中特码"
                            else: bet["状态"] = "❌ 未中奖"
                st.rerun()
            st.dataframe(pd.DataFrame(st.session_state.bet_history), use_container_width=True, hide_index=True)
        else:
            st.caption("📂 暂无下注流水。")
