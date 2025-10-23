import streamlit as st
import numpy as np
import pickle
import pandas as pd
from pathlib import Path
import os

# ==================== 全局配置 ====================
st.set_page_config(
    page_title='工程計算工具集',
    page_icon="⚙️",
    layout='wide',
    initial_sidebar_state="expanded"
)

# ==================== 材料與核心數據 ====================
MATERIAL_DENSITY = {
    '鋁 (Aluminum)': 2.70,
    '銅 (Copper)': 8.96,
    'PI (Polyimide)': 1.42,
    '無': 0.0
}

CORE_TYPES = {
    '鋁管': 5000,
    '紙管': 500
}

ADHESIVE_DENSITY = 0.92

# ==================== 認證密碼 ====================
CORRECT_PASSWORD = "12345"


# ==================== 認證檢查 ====================
def check_authentication():
    """檢查用戶是否已認證"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.title("🔐 工程計算工具集")
            st.subheader("請輸入密碼登入")

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


# ==================== 主應用程式 ====================
if check_authentication():

    # ==================== 側邊欄導航 ====================
    with st.sidebar:
        st.title('⚙️ 工具選單')

        tool_selection = st.radio(
            "選擇工具",
            options=['捲材計算器', 'KNN 分類預測器'],
            label_visibility="collapsed"
        )

        st.divider()

        # 用戶信息
        st.caption(f"✅ 已登入")

        # 登出按鈕
        if st.button("🚪 登出", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

        st.divider()
        st.caption("工程計算工具集 v1.0")

    # ==================== 應用1：捲材計算器 ====================
    if tool_selection == '捲材計算器':
        st.title('📊 捲材計算器')

        st.subheader('基本參數')
        col_core1, col_core2 = st.columns(2)
        with col_core1:
            core_type = st.selectbox('管材類型', list(CORE_TYPES.keys()))
        with col_core2:
            inner_diameter = st.number_input('管材內徑 (mm)', value=164.0, step=1.0)

        st.subheader('第一層材料')
        col1, col2 = st.columns(2)
        with col1:
            material_1 = st.selectbox('第一層材料', list(MATERIAL_DENSITY.keys()), index=1)
        with col2:
            thickness_1 = st.number_input('第一層厚度 (μm)', value=45.0, step=1.0)

        st.subheader('第二層材料')
        col3, col4 = st.columns(2)
        with col3:
            material_2 = st.selectbox('第二層材料', list(MATERIAL_DENSITY.keys()), index=1, key='mat2')
        with col4:
            thickness_2 = st.number_input('第二層厚度 (μm)', value=45.0, step=1.0)

        st.subheader('第三層材料')
        col5, col6 = st.columns(2)
        with col5:
            material_3 = st.selectbox('第三層材料', list(MATERIAL_DENSITY.keys()), index=3, key='mat3')
        with col6:
            thickness_3 = st.number_input('第三層厚度 (μm)', value=0.0, step=1.0)

        st.subheader('膠層')
        adhesive_thickness = st.number_input('膠層厚度 (μm)', value=250.0, step=1.0)

        st.subheader('尺寸')
        col7, col8 = st.columns(2)
        with col7:
            width = st.number_input('料寬 (mm)', value=560.0, step=1.0)
        with col8:
            length_m = st.number_input('長度 (m)', value=700.0, step=1.0)

        if st.button('計算', type='primary', use_container_width=True):
            thickness_1_mm = thickness_1 * 1e-3
            thickness_2_mm = thickness_2 * 1e-3
            thickness_3_mm = thickness_3 * 1e-3
            adhesive_thickness_mm = adhesive_thickness * 1e-3
            length_mm = length_m * 1000

            total_thickness = thickness_1_mm + thickness_2_mm + thickness_3_mm + adhesive_thickness_mm

            r = inner_diameter / 2
            R_squared = r * r + (length_mm * total_thickness) / np.pi
            R = np.sqrt(R_squared)
            outer_diameter = 2 * R

            density_1 = MATERIAL_DENSITY[material_1]
            density_2 = MATERIAL_DENSITY[material_2]
            density_3 = MATERIAL_DENSITY[material_3]

            volume_1 = (length_mm / 10) * (width / 10) * (thickness_1_mm / 10)
            volume_2 = (length_mm / 10) * (width / 10) * (thickness_2_mm / 10)
            volume_3 = (length_mm / 10) * (width / 10) * (thickness_3_mm / 10)
            adhesive_volume = (length_mm / 10) * (width / 10) * (adhesive_thickness_mm / 10)

            weight_1 = volume_1 * density_1
            weight_2 = volume_2 * density_2
            weight_3 = volume_3 * density_3
            adhesive_weight = adhesive_volume * ADHESIVE_DENSITY
            core_weight = CORE_TYPES[core_type]
            total_weight = weight_1 + weight_2 + weight_3 + adhesive_weight + core_weight

            st.divider()
            st.subheader('計算結果')

            st.metric('單層總厚度', f'{total_thickness:.4f} mm')
            st.metric('收卷外徑', f'{outer_diameter:.2f} mm ({outer_diameter / 10:.2f} cm)')

            st.divider()

            col9, col10, col11, col12 = st.columns(4)
            with col9:
                st.metric(f'{material_1}重量', f'{weight_1 / 1000:.3f} kg')
            with col10:
                st.metric(f'{material_2}重量', f'{weight_2 / 1000:.3f} kg')
            with col11:
                st.metric(f'{material_3}重量', f'{weight_3 / 1000:.3f} kg')
            with col12:
                st.metric('膠層重量', f'{adhesive_weight / 1000:.3f} kg')

            st.divider()
            st.metric('成品總重', f'{total_weight / 1000:.3f} kg',
                      delta=f'{(total_weight - core_weight) / 1000:.3f} kg (不含{core_type})')


    # ==================== 應用2：KNN 分類預測器 ====================
    elif tool_selection == 'KNN 分類預測器':

        @st.cache_resource
        def load_model_package():
            """載入模型包"""
            model_dir = Path(__file__).parent / "model"

            if not model_dir.exists():
                st.error(f"模型目錄不存在: {model_dir}")
                return None

            pkl_files = list(model_dir.glob("*model_package*.pkl"))

            if not pkl_files:
                st.error(f"模型目錄中沒有 model_package pkl 檔案: {model_dir}")
                return None

            latest_model = max(pkl_files, key=os.path.getmtime)

            try:
                with open(latest_model, 'rb') as f:
                    model_package = pickle.load(f)
                return model_package
            except Exception as e:
                st.error(f"載入模型包失敗: {str(e)}")
                return None


        def encode_input(model_package, input_dict):
            """編碼輸入"""
            try:
                original_features = model_package.get('original_features', ['x1', 'x2', 'x3'])
                feature_names = model_package.get('feature_names', [])

                input_df = pd.DataFrame([input_dict])
                encoded_df = pd.get_dummies(input_df, columns=original_features, drop_first=False)

                for col in feature_names:
                    if col not in encoded_df.columns:
                        encoded_df[col] = 0

                X_input = encoded_df[feature_names].values

                return X_input
            except Exception as e:
                st.error(f"特徵編碼失敗: {str(e)}")
                return None


        # ==================== 標題 ====================
        st.title("🔮 KNN 分類模型預測器")
        st.markdown("---")

        # 載入模型包
        model_package = load_model_package()

        if model_package is None:
            st.error("❌ 無法載入模型，請檢查模型路徑")
        else:
            # 提取模型信息
            model = model_package.get('model')
            n_classes = model_package.get('n_classes', 3)
            class_info = model_package.get('class_info', {})
            feature_encoding = model_package.get('feature_encoding', {})
            original_features = model_package.get('original_features', ['x1', 'x2', 'x3'])
            metadata = model_package.get('metadata', {})

            # ==================== 主要內容區 ====================
            st.header("🎯 特徵選擇")

            input_values = {}

            cols = st.columns(len(original_features))

            for idx, feature in enumerate(original_features):
                with cols[idx]:
                    if feature in feature_encoding:
                        encoding_info = feature_encoding[feature]
                        unique_values = encoding_info.get('unique_values', [])

                        st.subheader(feature)
                        selected_value = st.selectbox(
                            f"選擇 {feature} 的值",
                            options=unique_values,
                            label_visibility="collapsed",
                            key=f"feature_{feature}"
                        )
                        input_values[feature] = selected_value

            # ==================== 預測按鈕 ====================
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 2])

            with col1:
                predict_btn = st.button("🔮 預測", use_container_width=True, type="primary")

            with col2:
                clear_btn = st.button("🗑️ 清除", use_container_width=True)

            if clear_btn:
                st.session_state.clear()
                st.rerun()

            # ==================== 預測結果 ====================
            if predict_btn:
                X_input = encode_input(model_package, input_values)

                if X_input is not None:
                    prediction = model.predict(X_input)[0]

                    prediction_proba = None
                    try:
                        proba = model.predict_proba(X_input)[0]
                        prediction_proba = proba
                    except:
                        pass

                    st.markdown("---")
                    st.header("📈 預測結果")

                    col_left, col_right = st.columns([2, 1])

                    with col_left:
                        # 預測結果
                        st.subheader("⭐ 預測分類")
                        if prediction in class_info:
                            class_data = class_info[prediction]
                            st.success(
                                f"### 類別 {prediction}\n\n"
                                f"**y 值範圍:** [{class_data['min']:.2f}, {class_data['max']:.2f}]\n\n"
                                f"**平均值:** {class_data['mean']:.2f}"
                            )

                        st.divider()

                        # 模型信息
                        st.subheader("📊 模型信息")
                        info_col1, info_col2 = st.columns(2)
                        with info_col1:
                            st.metric("分類數", n_classes)
                        with info_col2:
                            st.metric("LOOCV 準確度", f"{metadata.get('loocv_accuracy', 0):.4f}")

                    with col_right:
                        st.subheader("📝 備註")
                        notes = st.text_area("", height=150, placeholder="輸入備註", label_visibility="collapsed")

                    st.divider()

                    # 類別定義
                    st.subheader("📈 類別定義")
                    class_cols = st.columns(n_classes)
                    for class_id in sorted(class_info.keys()):
                        info = class_info[class_id]
                        with class_cols[class_id]:
                            st.info(
                                f"**類別 {class_id}**\n"
                                f"• 範圍: [{info['min']:.2f}, {info['max']:.2f}]\n"
                                f"• 平均: {info['mean']:.2f}\n"
                                f"• 樣本: {info['count']}"
                            )

                    st.divider()

                    # 預測圖表
                    if prediction_proba is not None:
                        st.subheader("📊 預測概率分布")

                        prob_data = []
                        for i, prob in enumerate(prediction_proba):
                            prob_data.append({
                                "類別": f"類別 {i}",
                                "概率": prob
                            })

                        prob_df = pd.DataFrame(prob_data)

                        # 使用 st.bar_chart 顯示概率分布
                        st.bar_chart(prob_df.set_index("類別"))

            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.caption("🔧 技術: KNN 分類")
            with col2:
                st.caption(f"📅 訓練日期: {metadata.get('training_date', 'N/A')}")
            with col3:
                st.caption(f"📊 訓練樣本: {metadata.get('n_training_samples', 'N/A')}")