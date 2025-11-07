import streamlit as st
import numpy as np

CORE_TYPES = {
    '鋁管': 5000,
    '紙管': 500
}

ADHESIVE_DENSITY = 0.92


def render():
    """渲染捲材計算器頁面"""
    st.title('📊 捲材計算器')

    st.subheader('基本參數')
    col_core1, col_core2 = st.columns(2)
    with col_core1:
        core_type = st.selectbox('管材類型', list(CORE_TYPES.keys()))
    with col_core2:
        inner_diameter = st.number_input('管材內徑 (mm)', value=164.0, step=1.0)

    st.subheader('材料密度設定 (g/cm³)')
    st.info('密度參考 - 鋁: 2.70/ 銅: 8.96/ PI: 1.42/ EPOXY: 1.25/ PET: 1.37')
    density_col1, density_col2, density_col3 = st.columns(3)
    with density_col1:
        density_aluminum = st.number_input('材料密度(一)', value=2.70, step=0.01, format='%.2f')
    with density_col2:
        density_copper = st.number_input('材料密度(二)', value=8.96, step=0.01, format='%.2f')
    with density_col3:
        density_pi = st.number_input('材料密度(三)', value=1.42, step=0.01, format='%.2f')

    material_density_custom = {
        '材料密度(一)': density_aluminum,
        '材料密度(二)': density_copper,
        '材料密度(三)': density_pi,
        '無': 0.0
    }

    st.subheader('第一層材料')
    col1, col2 = st.columns(2)
    with col1:
        material_1 = st.selectbox('第一層材料', list(material_density_custom.keys()), index=1)
    with col2:
        thickness_1 = st.number_input('第一層厚度 (μm)', value=45.0, step=1.0)

    st.subheader('第二層材料')
    col3, col4 = st.columns(2)
    with col3:
        material_2 = st.selectbox('第二層材料', list(material_density_custom.keys()), index=1, key='mat2')
    with col4:
        thickness_2 = st.number_input('第二層厚度 (μm)', value=45.0, step=1.0)

    st.subheader('第三層材料')
    col5, col6 = st.columns(2)
    with col5:
        material_3 = st.selectbox('第三層材料', list(material_density_custom.keys()), index=3, key='mat3')
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

        density_1 = material_density_custom[material_1]
        density_2 = material_density_custom[material_2]
        density_3 = material_density_custom[material_3]

        volume_1 = (length_mm * width * thickness_1_mm) / 1000
        volume_2 = (length_mm * width * thickness_2_mm) / 1000
        volume_3 = (length_mm * width * thickness_3_mm) / 1000
        adhesive_volume = (length_mm * width * adhesive_thickness_mm) / 1000

        weight_1 = volume_1 * density_1
        weight_2 = volume_2 * density_2
        weight_3 = volume_3 * density_3
        adhesive_weight = adhesive_volume * ADHESIVE_DENSITY
        core_weight = CORE_TYPES[core_type]
        total_weight = weight_1 + weight_2 + weight_3 + adhesive_weight + core_weight

        st.divider()
        st.subheader('計算結果')

        st.metric('一單位總厚度(膠+第一層+第二層+第三層)', f'{total_thickness:.4f} mm')
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


if __name__ == '__main__':
    render()