import streamlit as st

st.markdown("## 🧠 Thông tin Mô hình (Model Info)")
st.markdown("Mô hình Học máy hiện tại đang phục vụ hệ thống là **XGBoost Regressor**.")

st.markdown("### Tổng quan Chỉ số (Metrics)")
col1, col2, col3 = st.columns(3)
col1.metric("Root Mean Squared Error (RMSE)", "10.45", delta="-3.2 vs Baseline", delta_color="normal")
col2.metric("Mean Absolute Error (MAE)", "7.12", delta="-2.8 vs Baseline", delta_color="normal")
col3.metric("R-Squared (R²)", "65.4%", delta="+15% vs Baseline", delta_color="normal")

st.info("Mô hình XGBoost có khả năng bắt được các mối quan hệ phi tuyến tính phức tạp của dữ liệu âm nhạc, đem lại độ tin cậy cao cho các dự báo.")
