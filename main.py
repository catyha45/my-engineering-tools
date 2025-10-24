import streamlit as st
from pathlib import Path

# ==================== 配置 ====================
st.set_page_config(
    page_title='工程計算工具集',
    page_icon="⚙️",
    layout='wide',
    initial_sidebar_state="expanded"
)

CORRECT_PASSWORD = "12345"


# ==================== 認證 ====================
def check_authentication():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.title("技術中心AI預測工具集")
            st.subheader("🔐請輸入密碼登入")
            password_input = st.text_input("密碼", type="password")

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("登入", use_container_width=True, type="primary"):
                    if password_input == CORRECT_PASSWORD:
                        st.session_state.authenticated = True
                        st.rerun()
                    else:
                        st.error("❌ 密碼錯誤")
            with col_b:
                if st.button("清除", use_container_width=True):
                    st.session_state.clear()
                    st.rerun()
        return False
    return True


# ==================== 主程序 ====================
if check_authentication():

    # 側邊欄
    with st.sidebar:
        st.title('⚙️ 工具選單')

        pages = {
            '捲材計算器': 'modules.roll_calculator',  # ← 改這裡
            '塗貼AI預測工具': 'modules.bonding_predictor',  # ← 改這裡
            '塗環AI預測工具': 'modules.coating_predictor'  # ← 改這裡
        }

        tool_selection = st.radio(
            "選擇工具",
            options=list(pages.keys()),
            label_visibility="collapsed"
        )

        st.divider()
        st.caption("✅ 已登入")

        if st.button("🚪 登出", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

        st.divider()
        st.caption("工程計算工具集 v1.0")
        st.caption("Terry | 📍技術中心 - 設備技術部")

    # 動態載入頁面
    module_name = pages[tool_selection]
    module = __import__(module_name, fromlist=['render'])
    module.render()