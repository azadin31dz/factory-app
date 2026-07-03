import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="إدارة مصنع الحقائب",
    page_icon="💼",
    layout="centered"
)

# --- التنسيق الجمالي الاحترافي المطور للهواتف ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif !important;
        direction: RTL !important;
        text-align: right !important;
    }
    
    .stApp {
        background-color: #121212 !important;
    }
    
    [data-testid="stSidebarCollapseButton"], [data-testid="collapsedControl"] {
        display: none !important;
    }
    
    .main-title {
        font-size: 24px !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
        text-align: center !important;
        padding: 15px 0 !important;
        border-bottom: 3px solid #2E7D32;
        margin-bottom: 20px !important;
    }
    
    /* تصميم الكروت الحديثة */
    .custom-card {
        background: linear-gradient(135deg, #1E1E1E 0%, #151515 100%);
        border: 1px solid #2C2C2C;
        border-right: 6px solid #4CAF50;
        padding: 15px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin-bottom: 15px;
    }
    .card-label {
        color: #AAAAAA !important;
        font-size: 13px !important;
        font-weight: 600 !important;
    }
    .card-value {
        color: #4CAF50 !important;
        font-size: 24px !important;
        font-weight: 700 !important;
    }
    .card-value-wages {
        color: #FFD700 !important;
        font-size: 24px !important;
        font-weight: 700 !important;
    }
    
    /* أزرار اختيار الصفحات لتصبح عريضة وسهلة اللمس */
    .stRadio > div {
        background-color: #1E1E1E !important;
        padding: 8px !important;
        border-radius: 10px !important;
        border: 1px solid #2C2C2C !important;
        gap: 8px !important;
    }
    
    /* تجميل عام للأزرار */
    div.stButton > button {
        background: linear-gradient(90deg, #2E7D32 0%, #4CAF50 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        padding: 10px !important;
        border-radius: 8px !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(76, 175, 80, 0.2) !important;
    }
    
    /* زر الحذف باللون الأحمر */
    .delete-btn div.stButton > button {
        background: linear-gradient(90deg, #C62828 0%, #E53935 100%) !important;
        box-shadow: 0 4px 10px rgba(229, 57, 53, 0.2) !important;
    }
    </style>
    """, unsafe_allow_html=True)

DB_NAME = "factory_web.db"
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
        cursor.executemany("INSERT INTO workers (name) VALUES (?)", [(f"عامل {i}",) for i in range(1, 6)])
    cursor.execute("SELECT COUNT(*) FROM colors")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO colors (color_name) VALUES (?)", [("أسود",), ("رمادي",), ("بيج",), ("أخضر",)])
    conn.commit()
    conn.close()

init_db()

st.markdown('<div class="main-title">💼 نظام إدارة مصنع الحقائب واحتساب الأجور</div>', unsafe_allow_html=True)

# قائمة تصفح عصرية ومريحة للهاتف
page = st.radio("📌 انتقل بين الصفحات:", ["📊 لوحة التحكم", "📝 تسجيل الإنتاج", "⚙️ إدارة العمال والألوان", "💾 نسخة احتياطية"], horizontal=True)

st.write(" ")

# --- 1. صفحة لوحة التحكم ---
if page == "📊 لوحة التحكم":
    current_date = datetime.now().date().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_NAME)
    df_prod = pd.read_sql_query(f"""
        SELECT p.id, w.name as worker_name, c.color_name, p.quantity, (p.quantity * p.price_per_piece) as wages
        FROM daily_production p 
        JOIN workers w ON p.worker_id = w.id 
        JOIN colors c ON p.color_id = c.id
        WHERE p.production_date = '{current_date}'
    """, conn)
    
    total_bags = df_prod['quantity'].sum() if not df_prod.empty else 0
    total_wages = df_prod['wages'].sum() if not df_prod.empty else 0
    
    st.markdown(f"""
    <div class="custom-card">
        <div class="card-label">📦 إجمالي الحقائب اليوم</div>
        <div class="card-value">{total_bags} حقيبة</div>
    </div>
    <div class="custom-card" style="border-right-color: #FFD700;">
        <div class="card-label">💰 إجمالي أجور اليوم</div>
        <div class="card-value-wages">{total_wages:,.0f} دج</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📋 سجلات إنتاج اليوم")
    if not df_prod.empty:
        display_df = df_prod[["worker_name", "color_name", "quantity", "wages"]].copy()
        display_df.columns = ["اسم العامل", "اللون", "الكمية", "الأجر (دج)"]
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد حركات مسجلة لليوم بعد.")
    conn.close()

# --- 2. صفحة تسجيل الإنتاج ---
elif page == "📝 تسجيل الإنتاج":
    st.markdown("### 📝 تسجيل حركة إنتاج جديدة")
    conn = sqlite3.connect(DB_NAME)
    workers = pd.read_sql_query("SELECT id, name FROM workers WHERE is_active=1", conn)
    colors = pd.read_sql_query("SELECT id, color_name FROM colors", conn)
    
    if not workers.empty:
        worker_opt = st.selectbox("👤 اسم العامل الحرفي:", workers['name'].tolist())
        color_opt = st.selectbox("🎨 لون الحقيبة:", colors['color_name'].tolist())
        qty = st.number_input("🔢 عدد الحقائب المصنوعة:", min_value=1, value=10, step=1)
        
        if st.button("✅ حفظ وإدراج الحركة فوراً", use_container_width=True):
            w_id = workers[workers['name'] == worker_opt]['id'].values[0]
            c_id = colors[colors['color_name'] == color_opt]['id'].values[0]
            current_date = datetime.now().date().strftime("%Y-%m-%d")
            
            cursor = conn.cursor()
            cursor.execute("INSERT INTO daily_production (production_date, worker_id, color_id, quantity, price_per_piece) VALUES (?, ?, ?, ?, ?)",
                           (current_date, int(w_id), int(c_id), int(qty), PRICE_PER_PIECE))
            conn.commit()
            st.success(f"🎉 تم تسجيل {qty} حقائب بنجاح للعامل: {worker_opt}")
    else:
        st.warning("الرجاء إضافة عمال أولاً من صفحة الإعدادات.")
    conn.close()

# --- 3. صفحة تعديل وإدارة العمال والألوان ---
elif page == "⚙️ إدارة العمال والألوان":
    st.markdown("### 👥 إدارة وتعديل أسماء العمال")
    conn = sqlite3.connect(DB_NAME)
    
    # قسم تعديل وتغيير اسم عامل موجود
    st.markdown("#### ✏️ تغيير اسم عامل موجود")
    workers_df = pd.read_sql_query("SELECT id, name FROM workers WHERE is_active=1", conn)
    if not workers_df.empty:
        worker_to_edit = st.selectbox("اختر العامل الذي تريد تغيير اسمه:", workers_df['name'].tolist())
        new_name_input = st.text_input("اكتب الاسم الجديد بدقة:")
        if st.button("💾 حفظ الاسم الجديد"):
            if new_name_input.strip():
                try:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE workers SET name = ? WHERE name = ?", (new_name_input.strip(), worker_to_edit))
                    conn.commit()
                    st.success(f"تم تغيير الاسم بنجاح من [{worker_to_edit}] إلى [{new_name_input}]!")
                    st.rerun()
                except:
                    st.error("⚠️ هذا الاسم موجود بالفعل لعامل آخر.")
    else:
        st.info("لا يوجد عمال مسجلين حالياً.")

    st.write("---")
    
    # قسم إضافة عامل جديد
    st.markdown("#### 👤 إضافة عامل جديد")
    new_worker = st.text_input("اكتب اسم العامل الجديد لإضافته:")
    if st.button("➕ إضافة العامل الجديد"):
        if new_worker.strip():
            try:
                conn.execute("INSERT INTO workers (name) VALUES (?)", (new_worker.strip(),))
                conn.commit()
                st.success(f"تمت إضافة العامل {new_worker} بنجاح!")
                st.rerun()
            except: st.error("⚠️ الاسم مسجل بالفعل.")
            
    st.write("---")
    
    # قسم حذف عامل
    st.markdown("#### 🔴 حذف عامل من النظام")
    if not workers_df.empty:
        worker_to_delete = st.selectbox("اختر العامل المراد حذفه نهائياً:", workers_df['name'].tolist(), key="del_work")
        st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
        if st.button("🗑️ حذف العامل المختار قطعيًا", use_container_width=True):
            cursor = conn.cursor()
            # لضمان عدم حدوث مشاكل برمجية نقوم بحذفه أو جعله غير نشط
            cursor.execute("DELETE FROM workers WHERE name = ?", (worker_to_delete,))
            conn.commit()
            st.success(f"تم حذف العامل {worker_to_delete} من النظام.")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("---")
    st.markdown("### 🎨 إضافة ألوان الحقائب")
    new_color = st.text_input("اكتب اسم اللون الجديد:")
    if st.button("➕ إضافة اللون"):
        if new_color.strip():
            try:
                conn.execute("INSERT INTO colors (color_name) VALUES (?)", (new_color.strip(),))
                conn.commit()
                st.success(f"تمت إضافة اللون {new_color}!")
