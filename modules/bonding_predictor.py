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


def render():
    """渲染塗貼AI預測工具主頁面"""
    st.title("🔮 塗貼AI預測工具")
    st.markdown("---")

    # 初始化 session_state
    if 'prediction_tab' not in st.session_state:
        st.session_state.prediction_tab = 0

    # 2行2列按鈕網格
    row1_col1, row1_col2 = st.columns(2)

    # 第一行
    with row1_col1:
        if st.button("🎯 離型力預測", use_container_width=True,
                     type="primary" if st.session_state.prediction_tab == 0 else "secondary",
                     key="btn_release_force"):
            st.session_state.prediction_tab = 0
            st.rerun()

    with row1_col2:
        st.button("📊 粗糙度預測", use_container_width=True,
                  type="secondary", disabled=True, key="btn_roughness")

    # 第二行（預留給未來功能）
    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st.button("🔧 待開發功能1", use_container_width=True,
                  type="secondary", disabled=True, key="btn_future1")

    with row2_col2:
        st.button("🔧 待開發功能2", use_container_width=True,
                  type="secondary", disabled=True, key="btn_future2")

    st.divider()

    # 只顯示離型力預測
    if st.session_state.prediction_tab == 0:
        render_release_force_tab()