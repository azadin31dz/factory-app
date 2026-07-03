import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# إجبار التصميم على أن يكون عمودياً وبسيطاً
st.set_page_config(layout="centered")

st.markdown("""
    <style>
    /* تصغير الخطوط وتنسيق العرض للهواتف */
    [data-testid="stAppViewContainer"] {
        padding: 10px;
    }
    h1 { font-size: 24px !important; text-align: center; }
    [data-testid="stMetricValue"] { font-size: 24px !important; }
    </style>
""", unsafe_allow_html=True)

st.title("💼 إدارة مصنع الحقائب")

# إعداد بسيط لقاعدة البيانات
conn = sqlite3.connect("factory_web.db")
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS production (id INTEGER PRIMARY KEY, qty INTEGER, date TEXT)")
conn.commit()

# واجهة بسيطة جداً
qty = st.number_input("عدد الحقائب:", min_value=0)
if st.button("حفظ الإنتاج"):
    c.execute("INSERT INTO production (qty, date) VALUES (?, ?)", (qty, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    st.success("تم الحفظ!")

st.subheader("إحصائيات اليوم")
df = pd.read_sql("SELECT * FROM production", conn)
st.dataframe(df.tail(5), use_container_width=True)
conn.close()
