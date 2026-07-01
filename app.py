import streamlit as st
import pandas as pd
import tempfile
import os
from utils import load_and_standardize

st.set_page_config(page_title="تحلیل‌گر تبلیغات", layout="wide")
st.title("📊 آنالیز خودکار فایل تبلیغات")

uploaded_file = st.file_uploader(
    "فایل اکسل یا CSV خود را آپلود کنید",
    type=["csv", "xlsx", "xls"]
)

if uploaded_file is not None:
    with st.spinner("در حال پردازش..."):
        try:
            # ذخیره موقت فایل آپلود شده
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                tmp_path = tmp_file.name
            
            # ارسال مسیر فایل به تابع
            df_std = load_and_standardize(tmp_path)
            
            # پاک کردن فایل موقت
            os.unlink(tmp_path)
            
            st.success("✅ تشخیص خودکار موفق!")
            st.dataframe(df_std)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("تعداد رکوردها", len(df_std))
            with col2:
                st.metric("میانگین هزینه", f"{df_std['cost'].mean():,.0f}")
            with col3:
                st.metric("مجموع تبدیل‌ها", f"{df_std['conversions'].sum():,.0f}")

            csv = df_std.to_csv(index=False).encode('utf-8')
            st.download_button("📥 دانلود CSV", data=csv, file_name="data_standardized.csv", mime="text/csv")

        except Exception as e:
            st.error(f"❌ خطا: {e}")
else:
    st.info("👈 فایل خود را آپلود کنید.")
