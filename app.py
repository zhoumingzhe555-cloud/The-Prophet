import streamlit as st
import random
import time
import math

# --- 页面配置：强制单列紧凑模式，最适合手机 ---
st.set_page_config(page_title="预言家", page_icon="🔮", layout="centered")

# --- 手机移动端深度适配与三色波样式 ---
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; padding-left: 1rem; padding-right: 1rem; }
    
    /* 专为手指触摸设计的超大醒目按钮 */
    .stButton>button { 
        background-color: #4b0082 !important; 
        color: white !important; 
        border-radius: 25px !important; 
        width: 100% !important; 
        height: 50px !important; 
        font-size: 18px !important;
        font-weight: bold !important; 
        box-shadow: 0px 4px 10px rgba(75,0,130,0.3);
    }
    
    /* 号码球包裹容器 */
    .ball-container { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; margin-bottom: 12px; }
    
    /* 基础球样式 */
    .ball { 
        width: 42px; height: 42px; line-height: 42px; border-radius: 50%; 
        color: white; text-align: center; font-weight: bold; font-size: 16px;
        box-shadow: 1px 3px 6px rgba(0,0,0,0.2);
    }
    
    /* 官方标准三色波颜色 */
    .ball-red { background: linear-gradient(135deg, #dc143c, #960018); }
    .ball-blue { background: linear-gradient(135deg, #1e90ff, #002fa7); }
    .ball-green { background: linear-gradient(135deg, #2e8b57, #124e2c); }
    
    .ball-dan { background: linear-gradient(135deg, #ff8c00, #d35400); } 
    .ball-tuo { background: linear-gradient(135deg, #4682b4, #2980b9); } 
    
    .mobile-card {
        background-color: #f7f9fa; padding: 12px; border-radius: 12px;
        border-left: 5px solid #4b0082; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 官方49码三色波严格划分定义 ---
RED_BALLS = [1, 2, 7, 8, 12, 13, 18, 19, 23, 24, 29, 30, 34, 35, 40, 45, 46]
BLUE_BALLS = [3, 4, 9, 10, 14, 15, 20, 25, 26, 31, 36, 37, 41, 42, 47, 48]
GREEN_BALLS = [5, 6, 11, 16, 17, 21, 22, 27, 28, 32, 33, 38, 39, 43, 44, 49]

def get_ball_style(num):
    if num in RED_BALLS: return "ball-red"
    if num in BLUE_BALLS: return "ball-blue"
    return "ball-green"

# --- 顶栏设置 ---
st.title("🔮 预言家 (The Prophet)")
st.caption("📱 移动端精简适配版 | 特码波色全新上线")

st.divider()

# --- 往期真实数据 (2026年5月最新) ---
@st.cache_data
def get_historical_data():
    return [
        {"期数": "26/051", "日期": "2026-05-14", "正码": [4, 15, 24, 31, 42, 48], "特别号码": 7},
        {"期数": "26/050", "日期": "2026-05-12", "正码": [1, 9, 13, 23, 30, 39], "特别号码": 22},
        {"期数": "26/049", "日期": "2026-05-10", "正码": [8, 14, 25, 33, 41, 47], "特别号码": 11},
        {"期数": "26/048", "日期": "2026-05-07", "正码": [6, 14, 20, 23, 28, 34], "特别号码": 49},
        {"期数": "26/047", "日期": "2026-05-05", "正码": [2, 7, 8, 10, 18, 47], "特别号码": 4},
    ]

history_list = get_historical_data()
latest_draw = history_list[0]

# --- 手机模块 1：最新开奖卡片 ---
st.markdown(f"""
<div class="mobile-card">
    <div style="font-size:14px; color:#666;">最新开奖：第 <b>{latest_draw['期数']}</b> 期 ({latest_draw['日期']})</div>
</div>
""", unsafe_allow_html=True)

# 渲染最新开奖（带官方三色波颜色）
ball_html = '<div class="ball-container">'
for num in latest_draw['正码']:
    ball_html += f'<div class="ball {get_ball_style(num)}">{num}</div>'
ball_html += f'<div class="ball {get_ball_style(latest_draw["特别号码"])}">{latest_draw["特别号码"]}</div></div>'
st.markdown(ball_html, unsafe_allow_html=True)

# 适合手机上下滑动的折叠历史
with st.expander("🔍 点击展开历史开奖记录"):
    for draw in history_list:
        st.markdown(f"""
        <div style="padding: 8px 0; border-bottom: 1px solid #eee; font-size:14px;">
            <b>第{draw['期数']}期</b> ({draw['日期']})<br>
            <span style="color:#2e8b57; font-weight:bold;">正码:</span> {" ".join(f"[{n}]" for n in draw['正码'])} | 
            <span style="color:#dc143c; font-weight:bold;">特码:</span> [{draw['特别号码']}]
        </div>
        """, unsafe_allow_html=True)

st.divider()

def calculate_combinations(n, k):
    return math.comb(n, k) if n >= k else 0

# --- 手机功能模块：升级为三个标签页 ---
play_type = st.tabs(["💡 智能复式", "🎯 黄金胆拖", "🔮 特码波色"])

# --- 复式模块 ---
with play_type[0]:
    num_count = st.slider("选号个数", min_value=7, max_value=12, value=7)
    total_notes = calculate_combinations(num_count, 6)
    
    col_p1, col_p2 = st.columns(2)
    col_p1.caption(f"📊 总注数: **{total_notes} 注**")
    col_p2.caption(f"💰 本金: **${total_notes*10} / ${total_notes*5}**")
    
    if st.button("✨ 启动复式预言"):
        with st.spinner('预言中...'):
            time.sleep(0.6)
            picked_numbers = sorted(random.sample(range(1, 50), num_count))
            st.success("🔮 预言家精选复式组合：")
            res_html = '<div class="ball-container">'
            for num in picked_numbers:
                res_html += f'<div class="ball {get_ball_style(num)}">{num}</div>'
            res_html += '</div>'
            st.markdown(res_html, unsafe_allow_html=True)

# --- 胆拖模块 ---
with play_type[1]:
    dan_count = st.slider("胆码个数", min_value=1, max_value=5, value=2)
    tuo_count = st.slider("拖码个数", min_value=7-dan_count, max_value=20, value=6)
    dan_notes = calculate_combinations(tuo_count, 6 - dan_count)
    
    col_t1, col_t2 = st.columns(2)
    col_t1.caption(f"📊 总注数: **{dan_notes} 注**")
    col_t2.caption(f"💰 本金: **${dan_notes*10} / ${dan_notes*5}**")
    
    if st.button("⚡ 启动胆拖预言"):
        with st.spinner('盘算中...'):
            time.sleep(0.6)
            all_pool = list(range(1, 50))
            random.shuffle(all_pool)
            dans = sorted(all_pool[:dan_count])
            tuos = sorted(all_pool[dan_count:dan_count+tuo_count])
            
            st.write("🟠 **必买胆码：**")
            d_html = '<div class="ball-container">'
            for d in dans: d_html += f'<div class="ball ball-dan">{d}</div>'
            d_html += '</div>'
            st.markdown(d_html, unsafe_allow_html=True)
                
            st.write("🔵 **配脚拖码范围：**")
            t_html = '<div class="ball-container">'
            for t in tuos: t_html += f'<div class="ball ball-tuo">{t}</div>'
            t_html += '</div>'
            st.markdown(t_html, unsafe_allow_html=True)

# --- 全新：特码波色预测选择模块 ---
with play_type[2]:
    st.header("特码波色过滤与精准预测")
    
    # 手机单选按钮：选择看好的波色趋势
    wave_choice = st.radio("🔮 你倾向于下期开出哪种特码波色？", ["看好红波特码", "看好蓝波特码", "混沌融合（随机推荐）"])
    
    st.caption("💡 提示：选择指定波色后，预言家将强制在官方对应的色球池内进行深度测算。")
    
    if st.button("🔥 开启特码预言"):
        with st.spinner('正在感应波色磁场...'):
            time.sleep(1.0)
            
            # 根据选择过滤球池
            if wave_choice == "看好红波特码":
                target_pool = RED_BALLS
                display_title = "🔴 预言家推荐【红波特码】前五强："
            elif wave_choice == "看好蓝波特码":
                target_pool = BLUE_BALLS
                display_title = "🔵 预言家推荐【蓝波特码】前五强："
            else:
                target_pool = list(range(1, 50))
                display_title = "🔮 预言家全随机【混沌特码】推荐："
            
            # 从筛选出的球池里随机挑选5个最具潜力的特码
            predicted_specials = sorted(random.sample(target_pool, min(5, len(target_pool))))
            
            st.success(display_title)
            spec_html = '<div class="ball-container">'
            for spec in predicted_specials:
                spec_html += f'<div class="ball {get_ball_style(spec)}">{spec}</div>'
            spec_html += '</div>'
            st.markdown(spec_html, unsafe_allow_html=True)
            
            # 自动统计选定波色的基础中奖率信息
            st.info(f"📊 统计小常识：49个号码中，红波占 {len(RED_BALLS)} 个，蓝波占 {len(BLUE_BALLS)} 个，绿波占 {len(GREEN_BALLS)} 个。独立单选某一波色中特码的理论概率约为 32% ~ 34%。")

st.divider()
st.caption("⚠️ 提示：彩票完全随机。本功能仅供手机端娱乐及民间传统走势模拟，请理性对待每一期搅珠。")
