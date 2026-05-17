# --- 接您未写完的置顶看板数据渲染 ---
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
            dan_balls = st.multiselect("选择胆码（必开核心码）", range(1, 50), max_selections=3)
        with col_tuo:
            tuo_balls = st.multiselect("选择拖码（辅助组合码）", [x for x in range(1, 50) if x not in dan_balls])
            
        if dan_balls and tuo_balls:
            comb_count = math.comb(len(tuo_balls), 2)  # 示例：以选2个拖码为例计算组合数
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
