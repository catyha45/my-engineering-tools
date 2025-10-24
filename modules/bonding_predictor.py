import streamlit as st
import pickle
import pandas as pd
from pathlib import Path
import os

DEFAULT_NOTES_KNN = """類別3完全無參考價值(因為樣本少)
這次的模型只對類別1跟2準確率有7成"""


def get_model_by_pattern(pattern):
    """根據模式名稱載入模型"""
    possible_paths = [
        Path(__file__).parent.parent / "model",
        Path(__file__).parent / "model",
        Path("./model"),
    ]

    model_dir = None
    for path in possible_paths:
        if path.exists():
            model_dir = path
            break

    if model_dir is None:
        return None

    # 尋找匹配的模型文件
    pkl_files = list(model_dir.glob(f"*{pattern}*.pkl"))

    if not pkl_files:
        return None

    latest_model = max(pkl_files, key=os.path.getmtime)

    try:
        with open(latest_model, 'rb') as f:
            return pickle.load(f)
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

        return encoded_df[feature_names].values
    except Exception as e:
        st.error(f"特徵編碼失敗: {str(e)}")
        return None


def show_prediction_result(model_package, prediction, class_info, metadata, result_type=""):
    """顯示預測結果"""
    st.markdown("---")
    st.header("📈 預測結果")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("⭐ 預測分類")
        if prediction in class_info:
            class_data = class_info[prediction]
            st.success(
                f"### 類別 {prediction}\n\n"
                f"**{result_type}值範圍:** [{class_data['min']:.2f}, {class_data['max']:.2f}]"
            )

        st.divider()

        st.subheader("📊 模型資訊")
        info_col1, info_col2 = st.columns(2)
        with info_col1:
            st.metric("分類數", len(class_info))
        with info_col2:
            st.metric("LOOCV 準確度", f"{metadata.get('loocv_accuracy', 0):.4f}")

    with col_right:
        st.subheader("📝 備註")
        st.text(DEFAULT_NOTES_KNN)

    st.divider()

    st.subheader("📈 類別定義")
    n_classes = len(class_info)
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

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption("🔧 技術: KNN 分類")
    with col2:
        st.caption(f"📅 訓練日期: {metadata.get('training_date', 'N/A')}")
    with col3:
        st.caption(f"📊 訓練樣本: {metadata.get('n_training_samples', 'N/A')}")


def render_release_force_tab():
    """離型力預測標籤頁"""
    st.header("離型力預測")

    model_package = get_model_by_pattern("3class")

    if model_package is None:
        st.error("❌ 無法載入離型力預測模型")
        return

    model = model_package.get('model')
    class_info = model_package.get('class_info', {})
    feature_encoding = model_package.get('feature_encoding', {})
    original_features = model_package.get('original_features', ['x1', 'x2', 'x3'])
    metadata = model_package.get('metadata', {})

    st.info("📋 請輸入塗貼工藝參數進行離型力預測")

    st.subheader("🎯 特徵選擇")

    input_values = {}
    cols = st.columns(len(original_features))

    for idx, feature in enumerate(original_features):
        with cols[idx]:
            if feature in feature_encoding:
                unique_values = feature_encoding[feature].get('unique_values', [])
                st.subheader(feature)
                selected_value = st.selectbox(
                    f"選擇 {feature} 的值",
                    options=unique_values,
                    label_visibility="collapsed",
                    key=f"release_force_{feature}"
                )
                input_values[feature] = selected_value

    st.markdown("---")
    col1, col2 = st.columns([1, 1])

    with col1:
        predict_btn = st.button("🔮 預測", use_container_width=True, type="primary", key="release_force_predict")

    with col2:
        clear_btn = st.button("🗑️ 清除", use_container_width=True, key="release_force_clear")

    if clear_btn:
        for key in list(st.session_state.keys()):
            if key.startswith("release_force"):
                del st.session_state[key]
        st.rerun()

    if predict_btn:
        X_input = encode_input(model_package, input_values)

        if X_input is not None:
            prediction = model.predict(X_input)[0]
            show_prediction_result(model_package, prediction, class_info, metadata, "離型力")


def render_roughness_tab():
    """粗糙度預測標籤頁"""
    st.header("粗糙度預測")

    model_package = get_model_by_pattern("roughness")

    if model_package is None:
        st.warning("⚠️ 粗糙度預測模型暫未上線，請等待更新")
        st.info("""
        **粗糙度預測模型即將推出**

        功能包括：
        - 表面粗糙度評估
        - 工藝參數影響分析
        - 質量預警
        """)
        return

    model = model_package.get('model')
    class_info = model_package.get('class_info', {})
    feature_encoding = model_package.get('feature_encoding', {})
    original_features = model_package.get('original_features', ['x1', 'x2', 'x3'])
    metadata = model_package.get('metadata', {})

    st.info("📋 請輸入塗貼工藝參數進行粗糙度預測")

    st.subheader("🎯 特徵選擇")

    input_values = {}
    cols = st.columns(len(original_features))

    for idx, feature in enumerate(original_features):
        with cols[idx]:
            if feature in feature_encoding:
                unique_values = feature_encoding[feature].get('unique_values', [])
                st.subheader(feature)
                selected_value = st.selectbox(
                    f"選擇 {feature} 的值",
                    options=unique_values,
                    label_visibility="collapsed",
                    key=f"roughness_{feature}"
                )
                input_values[feature] = selected_value

    st.markdown("---")
    col1, col2 = st.columns([1, 1])

    with col1:
        predict_btn = st.button("🔮 預測", use_container_width=True, type="primary", key="roughness_predict")

    with col2:
        clear_btn = st.button("🗑️ 清除", use_container_width=True, key="roughness_clear")

    if clear_btn:
        for key in list(st.session_state.keys()):
            if key.startswith("roughness"):
                del st.session_state[key]
        st.rerun()

    if predict_btn:
        X_input = encode_input(model_package, input_values)

        if X_input is not None:
            prediction = model.predict(X_input)[0]
            show_prediction_result(model_package, prediction, class_info, metadata, "粗糙度")


def render_adhesion_tab():
    """粘合強度預測標籤頁"""
    st.header("粘合強度預測")

    model_package = get_model_by_pattern("adhesion")

    if model_package is None:
        st.warning("⚠️ 粘合強度預測模型暫未上線，請等待更新")
        st.info("""
        **粘合強度預測模型即將推出**

        功能包括：
        - 粘合強度評估
        - 工藝參數優化
        - 缺陷預警
        """)
        return

    model = model_package.get('model')
    class_info = model_package.get('class_info', {})
    feature_encoding = model_package.get('feature_encoding', {})
    original_features = model_package.get('original_features', ['x1', 'x2', 'x3'])
    metadata = model_package.get('metadata', {})

    st.info("📋 請輸入塗貼工藝參數進行粘合強度預測")

    st.subheader("🎯 特徵選擇")

    input_values = {}
    cols = st.columns(len(original_features))

    for idx, feature in enumerate(original_features):
        with cols[idx]:
            if feature in feature_encoding:
                unique_values = feature_encoding[feature].get('unique_values', [])
                st.subheader(feature)
                selected_value = st.selectbox(
                    f"選擇 {feature} 的值",
                    options=unique_values,
                    label_visibility="collapsed",
                    key=f"adhesion_{feature}"
                )
                input_values[feature] = selected_value

    st.markdown("---")
    col1, col2 = st.columns([1, 1])

    with col1:
        predict_btn = st.button("🔮 預測", use_container_width=True, type="primary", key="adhesion_predict")

    with col2:
        clear_btn = st.button("🗑️ 清除", use_container_width=True, key="adhesion_clear")

    if clear_btn:
        for key in list(st.session_state.keys()):
            if key.startswith("adhesion"):
                del st.session_state[key]
        st.rerun()

    if predict_btn:
        X_input = encode_input(model_package, input_values)

        if X_input is not None:
            prediction = model.predict(X_input)[0]
            show_prediction_result(model_package, prediction, class_info, metadata, "粘合強度")


def render():
    """渲染塗貼AI預測工具主頁面"""
    st.title("🔮 塗貼AI預測工具")
    st.markdown("---")

    # 創建標籤頁
    tab1, tab2, tab3 = st.tabs(["🎯 離型力預測", "📊 粗糙度預測", "💪 粘合強度預測"])

    with tab1:
        render_release_force_tab()

    with tab2:
        render_roughness_tab()

    with tab3:
        render_adhesion_tab()