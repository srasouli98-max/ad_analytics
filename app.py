import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(
    page_title="DataFlow AI",
    page_icon="📊",
    layout="wide"
)

st.title("📊 DataFlow AI")
st.subheader("دستیار هوشمند داده برای مارکترها")
st.caption("تمیز کردن سریع گزارش‌های تبلیغاتی")

st.markdown("---")

uploaded_files = st.file_uploader(
    "فایل اکسل یا CSV آپلود کنید",
    type=["csv", "xlsx", "xls"],
    accept_multiple_files=True
)

if uploaded_files:
    for file in uploaded_files:
        st.write(f"**📄 فایل:** {file.name}")
        
        try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            st.info(f"تعداد ردیف: **{len(df):,}** | تعداد ستون: **{len(df.columns)}**")
            st.dataframe(df.head(10), use_container_width=True)
            
            if st.button(f"🔄 پردازش {file.name}", key=file.name):
                with st.spinner("در حال تمیز کردن داده‌ها..."):
                    cleaned = df.copy()
                    st.success("✅ پردازش با موفقیت انجام شد!")
                    st.dataframe(cleaned.head(10), use_container_width=True)
                    
                    # دانلود
                    output = BytesIO()
                    cleaned.to_excel(output, index=False)
                    output.seek(0)
                    
                    st.download_button(
                        label="⬇️ دانلود فایل تمیز شده",
                        data=output,
                        file_name=f"cleaned_{file.name}",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        except Exception as e:
            st.error(f"خطا در خواندن فایل: {e}")
