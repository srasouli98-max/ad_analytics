import streamlit as st
import pandas as pd
import tempfile
import os
from utils import load_and_standardize

# تنظیمات صفحه
st.set_page_config(
    page_title="تحلیل‌گر تبلیغات",
    page_icon="📊",
    layout="wide"
)

# عنوان اصلی
st.title("📊 آنالیز خودکار فایل تبلیغات")
st.markdown("فایل اکسل یا CSV خود را آپلود کنید تا به‌صورت خودکار ستون‌های هزینه، تاریخ و تبدیل شناسایی شده و گزارش استاندارد دریافت کنید.")

# بخش آپلود فایل
uploaded_file = st.file_uploader(
    "فایل اکسل یا CSV خود را آپلود کنید",
    type=["csv", "xlsx", "xls"],
    help="فایل‌های با ستون‌های Date، Cost و Conversions را پشتیبانی می‌کند."
)

if uploaded_file is not None:
    with st.spinner("در حال پردازش فایل..."):
        try:
            # ذخیره موقت فایل آپلود شده (برای سازگاری با تابع load_and_standardize)
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                tmp_path = tmp_file.name

            # فراخوانی تابع اصلی برای استانداردسازی
            df_std = load_and_standardize(tmp_path)

            # حذف فایل موقت
            os.unlink(tmp_path)

            # نمایش موفقیت
            st.success("✅ تشخیص خودکار با موفقیت انجام شد!")

            # نمایش دیتافریم استاندارد
            st.subheader("داده‌های استاندارد شده")
            st.dataframe(df_std)

            # نمایش آمار خلاصه
            st.subheader("خلاصه آمار")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("تعداد رکوردها", len(df_std))
            with col2:
                st.metric("میانگین هزینه", f"{df_std['cost'].mean():,.0f}")
            with col3:
                st.metric("مجموع تبدیل‌ها", f"{df_std['conversions'].sum():,.0f}")

            # نمایش توضیحات آماری
            with st.expander("نمایش آمار توصیفی"):
                st.write(df_std.describe())

            # دکمه دانلود خروجی
            csv = df_std.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 دانلود فایل استاندارد شده (CSV)",
                data=csv,
                file_name="data_standardized.csv",
                mime="text/csv",
            )

        except Exception as e:
            st.error(f"❌ خطا: {e}")
            st.info("لطفاً بررسی کنید که فایل شامل ستون‌های مناسب (تاریخ، هزینه، تبدیل) باشد.")
else:
    st.info("👈 لطفاً یک فایل انتخاب کنید تا تحلیل شروع شود.")
