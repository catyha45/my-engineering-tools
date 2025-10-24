import streamlit as st
import pickle
import pandas as pd
from pathlib import Path
import os

DEFAULT_NOTES_KNN = """類別3完全無參考價值(因為樣本少)
這次的模型只對類別1跟2準確率有7成"""


@st.cache_resource
@st.cache_resource
def load_model():
    """載入模型包 - 支持多種環境"""
    # 嘗試多個可能的路徑
    possible_paths = [
        Path(__file__).parent / "model",  # 本地：modules/model
        Path(__file__).parent.parent / "model",  # 本地：work_project/model
        Path("./model"),  # 相對路徑
    ]

    model_dir = None
    for path in possible_paths:
        if path.exists():
            model_dir = path
            break

    if model_dir is None:
        st.error("❌ 找不到模型目錄")
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


def render():
    """渲染塗貼AI預測工具頁面"""
    st.title("🔮 塗貼AI預測工具")
    st.markdown("---")

    model_package = load_model()

    if model_package is None:
        st.error("❌ 無法載入模型，請檢查模型路徑")
        return

    model = model_package.get('model')
    n_classes = model_package.get('n_classes', 3)
    class_info = model_package.get('class_info', {})
    feature_encoding = model_package.get('feature_encoding', {})
    original_features = model_package.get('original_features', ['x1', 'x2', 'x3'])
    metadata = model_package.get('metadata', {})

    st.header("🎯 特徵選擇")

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
                    key=f"feature_{feature}"
                )
                input_values[feature] = selected_value

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        predict_btn = st.button("🔮 預測", use_container_width=True, type="primary")

    with col2:
        clear_btn = st.button("🗑️ 清除", use_container_width=True)

    if clear_btn:
        st.session_state.clear()
        st.rerun()

    if predict_btn:
        X_input = encode_input(model_package, input_values)

        if X_input is not None:
            prediction = model.predict(X_input)[0]

            st.markdown("---")
            st.header("📈 預測結果")

            col_left, col_right = st.columns([2, 1])

            with col_left:
                st.subheader("⭐ 預測分類")
                if prediction in class_info:
                    class_data = class_info[prediction]
                    st.success(
                        f"### 類別 {prediction}\n\n"
                        f"**y(離型力) 值範圍:** [{class_data['min']:.2f}, {class_data['max']:.2f}]"
                    )

                st.divider()

                st.subheader("📊 模型資訊")
                info_col1, info_col2 = st.columns(2)
                with info_col1:
                    st.metric("分類數", n_classes)
                with info_col2:
                    st.metric("LOOCV 準確度", f"{metadata.get('loocv_accuracy', 0):.4f}")

            with col_right:
                st.subheader("📝 備註")
                st.text(DEFAULT_NOTES_KNN)

            st.divider()

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

        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption("🔧 技術: KNN 分類")
        with col2:
            st.caption(f"📅 訓練日期: {metadata.get('training_date', 'N/A')}")
        with col3:
            st.caption(f"📊 訓練樣本: {metadata.get('n_training_samples', 'N/A')}")