import streamlit as st
from pathlib import Path
import sys

# ==================== 配置 ====================
st.set_page_config(
    page_title='工程計算工具集',
    page_icon="⚙️",
    layout='wide',
    initial_sidebar_state="expanded"
)

CORRECT_PASSWORD = "12345"

# ==================== 工具映射 ====================
# 在這裡添加新工具，格式：'顯示名稱': '模塊路徑'
TOOLS = {
    '📊 捲材計算器': 'modules.roll_calculator',
    '🔮 塗貼AI預測工具': 'modules.bonding_predictor',
    '🎨 塗環AI預測工具': 'modules.coating_predictor'
}


# ==================== 認證函數 ====================
def check_authentication():
    """檢查用戶認證"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.title("技術中心 - AI預測模型")
            st.subheader("🔐 請輸入密碼登入")
            password_input = st.text_input("密碼", type="password", placeholder="輸入密碼")

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("登入", use_container_width=True, type="primary"):
                    if password_input == CORRECT_PASSWORD:
                        st.session_state.authenticated = True
                        st.rerun()
                    else:
                        st.error("❌ 密碼錯誤，請重試")
            with col_b:
                if st.button("清除", use_container_width=True):
                    st.session_state.clear()
                    st.rerun()
        return False
    return True


def load_module(module_name):
    """動態載入模塊"""
    try:
        module = __import__(module_name, fromlist=['render'])
        if hasattr(module, 'render'):
            return module
        else:
            st.error(f"❌ 模塊 {module_name} 沒有 render() 函數")
            return None
    except ImportError as e:
        st.error(f"❌ 無法載入模塊 {module_name}: {str(e)}")
        return None


# ==================== 主程序 ====================
if check_authentication():

    # ==================== 側邊欄導航 ====================
    with st.sidebar:
        st.title('⚙️ 工具選單')

        # 工具選擇
        tool_selection = st.radio(
            "選擇工具",
            options=list(TOOLS.keys()),
            label_visibility="collapsed"
        )

        st.divider()

        # 用戶信息
        st.caption("✅ 已登入")

        # 登出按鈕
        if st.button("🚪 登出", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

        st.divider()


        st.subheader("📍技術中心開發")
        st.caption("技術設備部")
        st.caption("開發者: Terry")



    # ==================== 動態載入頁面 ====================
    module_name = TOOLS[tool_selection]
    module = load_module(module_name)

    if module is not None:
        module.render()