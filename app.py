import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="إدارة مصنع الحقائب",
    page_icon="💼",
    layout="centered"
)

# --- التنسيق الجمالي الفاتح والعصري (تم تصحيح ألوان الخطوط هنا) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght=400;600;700;900&display=swap');
    
    /* ضبط الخطوط والاتجاه العام */
    * {
        font-family: 'Cairo', sans-serif !important;
        direction: RTL !important;
        text-align: right !important;
    }
    
    /* خلفية التطبيق الفاتحة والمريحة */
    .stApp {
        background: #F8F9FA !important;
    }
    
    /* إخفاء القوائم الجانبية المزعجة تماماً */
    [data-testid="stSidebarCollapseButton"], [data-testid="collapsedControl"] {
        display: none !important;
    }
    
    /* العنوان الرئيسي بتصميم فاتح جذاب */
    .main-title-container {
        background: linear-gradient(135deg, #2E7D32 0%, #1B5E20 100%);
        padding: 20px !important;
        border-radius: 16px !important;
        box-shadow: 0 6px 20px rgba(46, 125, 50, 0.15);
        margin-bottom: 30px !important;
        text-align: center !important;
    }
    .main-title {
        font-size: 26px !important;
        font-weight: 900 !important;
        color: #FFFFFF !important;
        text-align: center !important;
        margin: 0 !important;
    }
    
    /* أزرار اختيار الصفحات العلوية بتصميم مريح للهاتف */
    .stRadio > div {
        background-color: #FFFFFF !important;
        padding: 10px !important;
        border-radius: 14px !important;
        border: 1px solid #E0E0E0 !important;
        gap: 10px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .stRadio [data-testid="stMarkdownContainer"] p {
        font-weight: 600 !important;
        font-size: 14px !important;
        color: #333333 !important;
    }
    
    /* كروت البيانات الفاتحة والواضحة */
    .premium-card {
        background: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-right: 6px solid #4CAF50;
        padding: 20px !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }
    .premium-card:hover {
        transform: translateY(-2px);
    }
    .card-label {
        color: #666666 !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        margin-bottom: 6px;
    }
    .card-value {
        color: #2E7D32 !important;
        font-size: 28px !important;
        font-weight: 700 !important;
    }
    .card-value-wages {
        color: #D4AF37 !important;
        font-size: 28px !important;
        font-weight: 700 !important;
    }
    
    /* تجميل الجداول الفاتحة */
    [data-testid="stTable"], [data-testid="stDataFrame"] {
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1px solid #E0E0E0 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }
    
    /* العناوين الفرعية */
    h3 {
        color: #1B5E20 !important;
        font-size: 20px !important;
        font-weight: 700 !important;
        margin-top: 25px !important;
        margin-bottom: 15px !important;
        border-right: 4px solid #4CAF50;
        padding-right: 10px !important;
    }
    h4 {
        color: #333333 !important;
        font-size: 16px !important;
        font-weight: 600 !important;
    }
    
    /* الأزرار الرئيسية الزاهية */
    div.stButton > button {
        background: linear-gradient(135deg, #2E7D32 0%, #4CAF50 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        padding: 12px !important;
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.2) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%) !important;
        box-shadow: 0 6px 16px rgba(76, 175, 80, 0.3) !important;
        transform: translateY(-2px) !important;
    }
    
    /* زر الحذف الأحمر */
    .delete-btn div.stButton > button {
        background: linear-gradient(135deg, #C62828 0%, #E53935 100%) !important;
        box-shadow: 0 4px 12px rgba(229, 57, 53, 0.2) !important;
    }
    .delete-btn div.stButton > button:hover {
        background: linear-gradient(135deg, #B71c1c 0%, #C62828 100%) !important;
        box-shadow: 0 6px 16px rgba(229, 57, 53, 0.3) !important;
    }
    
    /* إصلاح جذري لألوان حقول المدخلات والخطوط لتصبح سوداء وواضحة جداً */
    .stSelectbox div[data-baseweb="select"], .stNumberInput input, .stTextInput input, .stDateInput input {
        background-color: #FFFFFF !important;
        color: #111111 !important; /* لون الخط أسود داكن */
        border-radius: 10px !important;
    }
    
    /* التأكيد على ظهور النص داخل حقول الإدخال */
    input {
        color: #111111 !important;
        -webkit-text-fill-color: #111111 !important;
    }
    
    .stAlert p {
        color: #333333 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# مسار قاعدة البيانات الآمن
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

st.markdown('<div class="main-title-container"><h1 class="main-title">🏭 مصنع الحقائب الذكي • Smart Factory</h1></div>', unsafe_allow_html=True)

page = st.radio("📌 لوحة التحكم السريعة:", ["📊 التقارير والأيام", "📝 تسجيل الإنتاج", "⚙️ إدارة العمال والألوان", "💾 الأمان والنسخ"], horizontal=True)

st.write(" ")

# --- 1. صفحة لوحة التحكم والتقارير ---
if page == "📊 التقارير والأيام":
    st.markdown("### 🔍 مراجعة التقارير والإنتاج السابق")
    
    selected_date = st.date_input("📅 اختر اليوم الذي تريد العودة إليه لتفقد سجلاته:", datetime.now().date())
    formatted_date = selected_date.strftime("%Y-%m-%d")
    
    conn = sqlite3.connect(DB_NAME)
    query = "SELECT p.id, w.name as worker_name, c.color_name, p.quantity, (p.quantity * p.price_per_piece) as wages FROM daily_production p JOIN workers w ON p.worker_id = w.id JOIN colors c ON p.color_id = c.id WHERE p.production_date = '" + formatted_date + "'"
    df_prod = pd.read_sql_query(query, conn)
    
    total_bags = df_prod['quantity'].sum() if not df_prod.empty else 0
    total_wages = df_prod['wages'].sum() if not df_prod.empty else 0
    
    st.markdown(f"""
    <div class="premium-card">
        <div class="card-label">📦 إجمالي الحقائب المنتجة ليوم ({formatted_date})</div>
        <div class="card-value">{total_bags} حقيبة جاهزة</div>
    </div>
    <div class="premium-card" style="border-right-color: #D4AF37;">
        <div class="card-label">💰 مستحقات الأجور الإجمالية للعمال</div>
        <div class="card-value-wages">{total_wages:,.0f} دج</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📋 جدول الحركات والإنتاج بالتفصيل")
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
            st.success("✨ تم حذف السجل وإعادة احتساب الأرقام بنجاح!")
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
        
        st.write(" ")
        if st.button("🚀 حفظ الحركة وتأكيد السجل", use_container_width=True):
            w_id = workers[workers['name'] == worker_opt]['id'].values[0]
            c_id = colors[colors['color_name'] == color_opt]['id'].values[0]
            
            cursor = conn.cursor()
            cursor.execute("INSERT INTO daily_production (production_date, worker_id, color_id, quantity, price_per_piece) VALUES (?, ?, ?, ?, ?)",
                           (formatted_prod_date, int(w_id), int(c_id), int(qty), PRICE_PER_PIECE))
            conn.commit()
            st.success(f"🎉 ممتاز! تم حفظ {qty} حقائب بنجاح للعامل المبدع: {worker_opt}")
    else:
        st.warning("الرجاء إضافة عمال أولاً من صفحة الإعدادات والإدارة.")
    conn.close()

# --- 3. صفحة تعديل وإدارة العمال والألوان ---
elif page == "⚙️ إدارة العمال والألوان":
    st.markdown("### 👥 تعديل وإدارة طاقم العمال")
    conn = sqlite3.connect(DB_NAME)
    
    st.markdown("#### ✏️ تعديل وتصحيح اسم عامل")
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
                    st.success(f"✨ تم تحديث قاعدة البيانات بنجاح إلى: [{new_name_input}]")
                    st.rerun()
                except:
                    st.error("⚠️ هذا الاسم مستخدم لعامل آخر بالفعل.")
    else:
        st.info("لا يوجد عمال في النظام.")

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
    st.markdown("#### 🔴 شطب وحذف اسم عامل نهائياً")
    if not workers_df.empty:
        worker_to_delete = st.selectbox("اختر الاسم المراد الاستغناء عنه وحذفه:", workers_df['name'].tolist(), key="del_work")
        st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
        if st.button("🗑️ شطب العامل قطعيًا من السجلات", use_container_width=True):
            cursor = conn.cursor()
            cursor.execute("DELETE FROM workers WHERE name = ?", (worker_to_delete,))
            conn.commit()
            st.success(f"تم حذف {worker_to_delete} بنجاح من أنظمة المصنع.")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("---")
    st.markdown("### 🎨 تسيير قائمة ألوان الحقائب")
    new_color = st.text_input("اسم تدرج اللون الجديد:")
    if st.button("➕ إضافة خيار اللون"):
        if new_color.strip():
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO colors (color_name) VALUES (?)", (new_color.strip(),))
                conn.commit()
                st.success(f"🎨 تم تفعيل خيار اللون الجديد: {new_color}")
                st.rerun()
            except:
                st.error("⚠️ هذا اللون مضاف مسبقاً.")
    conn.close()

# --- 4. صفحة الأمان والنسخ الاحتياطي ---
elif page == "💾 الأمان والنسخ":
    st.markdown("### 💾 مركز النسخ الاحتياطي والأمان السحابي")
    st.write("لضمان حماية بيانات مصنعك لعدة سنوات، يرجى حفظ نسخة دورية:")
    
    st.markdown("#### 1️⃣ تنزيل النسخة الاحتياطية الحالية")
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
        
    st.write("---")
    st.markdown("#### 2️⃣ استرجاع كافة السجلات السابقة بملف")
    st.write("في حال قمت بتغيير الهاتف أو ضياع البيانات مستقبلاً، ارفع ملفك هنا ليعود كل شيء في ثانية واحدة:")
    
    uploaded_file = st.file_uploader("اختر ملف الـ .db الاحتياطي من ذاكرة هاتفك:", type=["db"])
    if uploaded_file is not None:
        if st.button("🔄 تأكيد استرجاع كامل السجلات والأسماء", use_container_width=True):
            try:
                with open(DB_NAME, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success("🔥 تم استرجاع كافة أسماء عمالك وحركات إنتاجك بنجاح تام! تفقد لوحة التحكم الآن.")
                st.rerun()
            except Exception as e:
                st.error(f"حدث خطأ أثناء الرفع: {e}")
