from datetime import date
import streamlit as st
import requests
from Sales.create_report import make_sales_form
import pandas as pd


url = "https://ahmed620.pythonanywhere.com"
server = ""


sales_headers = ["اسم الصنف", "كمية", "سعر", "اجمالي", "خصم", "صافي"]

st.markdown("""
<style>
button[kind="primary"] { direction: rtl; text-align: center; }
</style>
""", unsafe_allow_html=True)


today = date.today()

def ar(text: str, side: str="right", size: int=1):
    return f'<h{size} dir="rtl" style="text-align: {side};">{text}</h{size}>'


def check_server():
    resp = requests.get(f"{server}/check")
    return resp.ok


def get_query(method, query):
    params = {'method': method, 'query': query}
    resp = requests.get(f"{server}/get_query", params=params)
    return resp.json()


try:
    response = requests.get(f"{url}/get_value")
    if response.ok:
        server = response.json()  # or response.json() if JSON
        if check_server():
            st.write("Server response:", True)

            if "active_report" not in st.session_state:
                st.session_state.active_report = None

            if 'file_cache' not in st.session_state:
                st.session_state.file_cache = {'key': None, 'data': None}

            with st.sidebar:
                if st.button("تقرير انتهاء الصلاحية", width="stretch"):
                    st.session_state.active_report = "expiry"
                if st.button("تقرير المبيعات", width="stretch"):
                    st.session_state.active_report = "sales"
                if st.button("تقرير سلع المندوبين", width="stretch"):
                    st.session_state.active_report = "suppliers"
                if st.button("تقرير الأجور", width="stretch"):
                    st.session_state.active_report = "salaries"

            if st.session_state.active_report == "sales":
                st.markdown(ar("تقرير المبيعات", "center", 4), unsafe_allow_html=True)
                from_date = st.date_input("من تاريخ:", max_value=today, format="DD-MM-YYYY", key="from_date")
                to_date = st.date_input("إلى تاريخ:", max_value=today, format="DD-MM-YYYY", key="to_date")

                # Fetch data
                try:
                    with st.spinner("جاري التحميل..."):
                        rows = get_query("get_sales_data", [from_date, to_date])  # Local rows
                        df = pd.DataFrame(rows, columns=sales_headers)
                except Exception as e:
                    st.error(f"خطأ في الاستعلام: {e}")
                    df = pd.DataFrame()

                # Display results
                if not df.empty:
                    st.markdown(ar("نتائج الاستعلام", "center", 5), unsafe_allow_html=True)
                    st.dataframe(df, use_container_width=True)  # Interactive table

                    st.markdown(ar("إنشاء التقرير", "center", 5), unsafe_allow_html=True)
                    excel_format = st.checkbox("Excel", key="excel_sales")
                    pdf_format = st.checkbox("Pdf", key="pdf_sales")

                    if excel_format or pdf_format:
                        cache_key = f"{from_date}_{to_date}_{excel_format}_{pdf_format}"
                        try:
                            # Generate file only if cache miss or dates/format changed
                            if st.session_state.file_cache['key'] != cache_key or st.session_state.file_cache[
                                'data'] is None:
                                with st.spinner("جاري إنشاء الملف..."):
                                    if excel_format:
                                        excel_buffer = df.to_excel(index=False, excel_writer=None, engine="openpyxl")
                                        st.session_state.file_cache['data'] = excel_buffer
                                        st.session_state.file_cache['format'] = "excel"
                                    if pdf_format:
                                        file_ = make_sales_form(from_date, to_date, rows)
                                        st.session_state.file_cache['data'] = file_.getvalue()
                                        st.session_state.file_cache['format'] = "pdf"
                                    st.session_state.file_cache['key'] = cache_key

                            # Download button based on format
                            if st.session_state.file_cache['format'] == "excel":
                                st.download_button(
                                    label="تحميل Excel",
                                    data=st.session_state.file_cache['data'],
                                    file_name="report.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                            else:
                                st.download_button(
                                    label="تحميل PDF",
                                    data=st.session_state.file_cache['data'],
                                    file_name="report.pdf",
                                    mime="application/pdf"
                                )
                        except Exception as e:
                            st.error(f"خطأ أثناء إنشاء الملف: {e}")
                else:
                    st.markdown(ar("لا توجد بيانات متاحة لهذا النطاق الزمني", "center", 3), unsafe_allow_html=True)




    else:
        st.write("Failed to get value from server.")
except Exception as e:
    st.error(f"Error connecting to server: {e}")

st.write("hello_world")




