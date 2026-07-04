import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="Balmatik",
    page_icon="🧳",
    layout="centered"
)

# --- التنسيق الجمالي العصري باللون الأزرق الفاتح (تم قفله وإصلاحه بالكامل) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght=400;600;700;900&display=swap');
    
    /* ضبط الخطوط والاتجاه العام */
    * {
        font-family: 'Cairo', sans-serif !important;
        direction: RTL !important;
        text-align: right !important;
    }
    
    /* خلفية التطبيق: أزرق فاتح وناعم ومريح جداً للعين */
    .stApp {
        background: linear-gradient(135deg, #EBF3FC 0%, #D6E4F0 100%) !important;
    }
    
    /* إخفاء القوائم الجانبية المزعجة على الهاتف */
    [data-testid="stSidebarCollapseButton"], [data-testid="collapsedControl"] {
        display: none !important;
    }
    
    /* العنوان الرئيسي: بتصميم أزرق ملكي فاخر وانحناءات عصرية */
    .main-title-container {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 22px !important;
        border-radius: 20px !important;
        box-shadow: 0 8px 24px rgba(30, 58, 138, 0.2);
        margin-bottom: 30px !important;
        text-align: center !important;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .main-title {
        font-size: 32px !important;
        font-weight: 900 !important;
        color: #FFFFFF !important;
        text-align: center !important;
        margin: 0 !important;
    }
    
    /* أزرار اختيار الصفحات العلوية */
    .stRadio > div {
        background-color: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(10px);
        padding: 12px !important;
        border-radius: 16px !important;
        border: 1px solid #B9D1EA !important;
        gap: 12px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
    }
    .stRadio [data-testid="stMarkdownContainer"] p {
        font-weight: 700 !important;
        font-size: 14px !important;
        color: #1E3A8A !important;
    }
    
    /* كروت عرض البيانات والإحصائيات */
    .premium-card {
        background: #FFFFFF;
        border: 1px solid #D6E4F0;
        border-right: 6px solid #3B82F6;
        padding: 20px !important;
        border-radius: 18px !important;
        box-shadow: 0 6px 16px rgba(30, 58, 138, 0.05);
        margin-bottom: 20px;
    }
    .card-label {
        color: #64748B !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        margin-bottom: 6px;
    }
    .card-value {
        color: #1E3A8A !important;
        font-size: 30px !important;
        font-weight: 700 !important;
    }
    .card-value-wages {
        color: #D97706 !important;
        font-size: 30px !important;
        font-weight: 700 !important;
    }
    
    /* تصميم الجداول */
    [data-testid="stTable"], [data-testid="stDataFrame"] {
        background-color: #FFFFFF !important;
        border-radius: 16px !important;
        overflow: hidden !important;
        border: 1px solid #D6E4F0 !important;
    }
    
    /* العناوين الفرعية */
    h3 {
        color: #1E3A8A !important;
        font-size: 22px !important;
        font-weight: 700 !important;
        margin-top: 25px !important;
        border-right: 5px solid #3B82F6;
        padding-right: 12px !important;
    }
    
    /* الأزرار الرئيسية */
    div.stButton > button {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        padding: 14px !important;
        border-radius: 14px !important;
        border: none !important;
        width: 100% !important;
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.3) !important;
    }
    
    /* زر الحذف والتراجع الأحمر */
    .delete-btn div.stButton > button {
        background: linear-gradient(135deg, #DC2626 0%, #EF4444 100%) !important;
    }
    
    /* حقول الإدخال */
    .stSelectbox div[data-baseweb="select"], .stNumberInput input, .stTextInput input, .stDateInput input {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border-radius: 12px !important;
        border: 1px solid #CBD5E1 !important;
        font-weight: 600 !important;
    }
    
    /* تثبيت لون النص عند الكتابة ليكون أسود داكن واضح */
    input {
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
    }
    
    .stAlert p {
        color: #1E293B !important;
    }
    </style>
    """, unsafe_allow_html=True)

# مسار قاعدة البيانات الآمنة محلياً على الهاتف
DB_DIR = os.path.expanduser("~")
DB_NAME = os.path.join(DB_DIR, "factory_secure_web.db")
PRICE_PER_PIECE = 550

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS workers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, is_active INTEGER DEFAULT 1)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS colors (id INTEGER PRIMARY KEY AUTOINCREMENT, color_name TEXT UNIQUE)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS daily_production (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        production_date DATE, worker_id INTEGER, color_id INTEGER, quantity INTEGER, price_per_piece REAL,
                        FOREIGN KEY(worker_id) REFERENCES workers(id), FOREIGN KEY(color_id) REFERENCES colors(id))''')
    
    cursor.execute("SELECT COUNT(*) FROM workers")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO workers (name) VALUES (?)", [("عامل 1",), ("عامل 2",), ("عامل 3",)])
    cursor.execute("SELECT COUNT(*) FROM colors")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO colors (color_name) VALUES (?)", [("أسود",), ("رمادي",), ("بيج",), ("أخضر",)])
    conn.commit()
    conn.close()

init_db()

# الشعار الرئيسي المطور
st.markdown('<div class="main-title-container"><h1 class="main-title">🧳 Balmatik</h1></div>', unsafe_allow_html=True)

page = st.radio("📌 لوحة التحكم السريعة:", ["📊 التقارير والأيام", "📝 تسجيل الإنتاج", "⚙️ إدارة العمال والألوان", "💾 الأمان والنسخ"], horizontal=True)

st.write(" ")

# --- 1. صفحة التقارير ---
if page == "📊 التقارير والأيام":
    st.markdown("### 🔍 مراجعة التقارير والإنتاج السابق")
    selected_date = st.date_input("📅 اختر اليوم تفقد سجلاته:", datetime.now().date())
    formatted_date = selected_date.strftime("%Y-%m-%d")
    
    conn = sqlite3.connect(DB_NAME)
    query = f"SELECT p.id, w.name as worker_name, c.color_name, p.quantity, (p.quantity * p.price_per_piece) as wages FROM daily_production p JOIN workers w ON p.worker_id = w.id JOIN colors c ON p.color_id = c.id WHERE p.production_date = '{formatted_date}'"
    df_prod = pd.read_sql_query(query, conn)
    
    total_bags = df_prod['quantity'].sum() if not df_prod.empty else 0
    total_wages = df_prod['wages'].sum() if not df_prod.empty else 0
    
    st.markdown(f"""
    <div class="premium-card">
        <div class="card-label">📦 إجمالي الحقائب المنتجة ليوم ({formatted_date})</div>
        <div class="card-value">{total_bags} حقيبة جاهزة</div>
    </div>
    <div class="premium-card" style="border-right-color: #D97706;">
        <div class="card-label">💰 مستحقات الأجور الإجمالية للعمال</div>
        <div class="card-value-wages">{total_wages:,.0f} دج</div>
    </div>
    """, unsafe_allow_html=True)
    
    if not df_prod.empty:
        display_df = df_prod[["id", "worker_name", "color_name", "quantity", "wages"]].copy()
        display_df.columns = ["الرقم", "اسم العامل", "اللون", "الكمية", "الأجر (دج)"]
        st.dataframe(display_df.set_index("الرقم"), use_container_width=True)
        
        st.write("---")
        st.markdown("### 🔴 تعديل الأخطاء وإلغاء الحركات")
        record_to_delete = st.selectbox("اختر الحركة المراد إلغاؤها وحذفها نهائياً:", df_prod['id'].tolist(), format_func=lambda x: f"حركة رقم {x} ➔ لـ {df_prod[df_prod['id']==x]['worker_name'].values[0]}")
        
        st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
        if st.button("🗑️ إزالة الحركة المحددة فوراً", use_container_width=True):
            cursor = conn.cursor()
            cursor.execute("DELETE FROM daily_production WHERE id = ?", (int(record_to_delete),))
            conn.commit()
            st.success("✨ تم حذف السجل بنجاح!")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info(f"💡 لا توجد أي بيانات مسجلة في تاريخ {formatted_date}.")
    conn.close()

# --- 2. صفحة تسجيل الإنتاج ---
elif page == "📝 تسجيل الإنتاج":
    st.markdown("### 📝 إدخال حركة إنتاج جديدة للعمال")
    prod_date = st.date_input("📅 حدد تاريخ حركة الإنتاج:", datetime.now().date())
    formatted_prod_date = prod_date.strftime("%Y-%m-%d")
    
    conn = sqlite3.connect(DB_NAME)
    workers = pd.read_sql_query("SELECT id, name FROM workers WHERE is_active=1", conn)
    colors = pd.read_sql_query("SELECT id, color_name FROM colors", conn)
    
    if not workers.empty:
        worker_opt = st.selectbox("👤 اختر اسم العامل الحرفي:", workers['name'].tolist())
        color_opt = st.selectbox("🎨 اختر لون قماش الحقيبة:", colors['color_name'].tolist())
        qty = st.number_input("🔢 الكمية المنجزة (عدد القطع):", min_value=1, value=10, step=1)
        
        if st.button("🚀 حفظ الحركة وتأكيد السجل", use_container_width=True):
            w_id = workers[workers['name'] == worker_opt]['id'].values[0]
            c_id = colors[colors['color_name'] == color_opt]['id'].values[0]
            
            cursor = conn.cursor()
            cursor.execute("INSERT INTO daily_production (production_date, worker_id, color_id, quantity, price_per_piece) VALUES (?, ?, ?, ?, ?)",
                           (formatted_prod_date, int(w_id), int(c_id), int(qty), PRICE_PER_PIECE))
            conn.commit()
            st.success(f"🎉 ممتاز! تم حفظ {qty} حقائب بنجاح للعامل: {worker_opt}")
    else:
        st.warning("الرجاء إضافة عمال أولاً من صفحة الإعدادات والإدارة.")
    conn.close()

# --- 3. صفحة إدارة العمال والألوان ---
elif page == "⚙️ إدارة العمال والألوان":
    st.markdown("### 👥 تعديل وإدارة طاقم العمال")
    conn = sqlite3.connect(DB_NAME)
    
    workers_df = pd.read_sql_query("SELECT id, name FROM workers WHERE is_active=1", conn)
    if not workers_df.empty:
        worker_to_edit = st.selectbox("اختر الاسم المراد تعديله حالياً:", workers_df['name'].tolist())
        new_name_input = st.text_input("اكتب الاسم الجديد الصحيح هنا:")
        if st.button("💾 حفظ وتثبيت الاسم الجديد"):
            if new_name_input.strip():
                try:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE workers SET name = ? WHERE name = ?", (new_name_input.strip(), worker_to_edit))
                    conn.commit()
                    st.success(f"✨ تم تحديث قاعدة البيانات بنجاح!")
                    st.rerun()
                except:
                    st.error("⚠️ هذا الاسم مستخدم لعامل آخر بالفعل.")
                    
    st.write("---")
    st.markdown("#### 👤 تسجيل عامل جديد بالمصنع")
    new_worker = st.text_input("اسم العامل الجديد بالكامل:")
    if st.button("➕ إدراج العامل الجديد"):
        if new_worker.strip():
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO workers (name) VALUES (?)", (new_worker.strip(),))
                conn.commit()
                st.success(f"✅ تم تفعيل حساب العامل الجديد: {new_worker}")
                st.rerun()
            except:
                st.error("⚠️ الاسم مضاف مسبقاً.")
                
    st.write("---")
    st.markdown("### 🎨 تسيير قائمة ألوان الحقائب")
    new_color = st.text_input("اسم تدرج اللون الجديد:")
    if st.button("➕ إضافة خيار اللون"):
        if new_color.strip():
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO colors (color_name) VALUES (?)", (new_color.strip(),))
                conn.commit()
                st.success(f"🎨 تم إضافة اللون بنجاح!")
                st.rerun()
            except:
                st.error("⚠️ هذا اللون مضاف مسبقاً.")
    conn.close()

# --- 4. صفحة الأمان والنسخ الاحتياطي ---
elif page == "💾 الأمان والنسخ":
    st.markdown("### 💾 مركز النسخ الاحتياطي والأمان")
    try:
        with open(DB_NAME, "rb") as f:
            st.download_button(
                label="📥 تحميل ملف قاعدة البيانات لحفظه بهاتفك (.db)",
                data=f,
                file_name=f"factory_backup_{datetime.now().strftime('%Y%m%d')}.db",
                use_container_width=True
            )
    except:
        st.info("لا توجد بيانات متاحة للتحميل حالياً.")

