import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="Balmatik",
    page_icon="🧳",
    layout="centered"
)

# --- ضع روابط Supabase الخاصة بك هنا لتفعيل الربط السحابي ---
SUPABASE_URL = "ضع_رابط_المشروع_هنا"
SUPABASE_KEY = "ضع_الرمز_الطويل_هنا"

# ترويسة الطلبات للاتصال بقاعدة البيانات
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

PRICE_PER_PIECE = 550

# --- التنسيق الجمالي الفاتح والعصري ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght=400;600;700;900&display=swap');
    * { font-family: 'Cairo', sans-serif !important; direction: RTL !important; text-align: right !important; }
    .stApp { background: #F8F9FA !important; }
    [data-testid="stSidebarCollapseButton"], [data-testid="collapsedControl"] { display: none !important; }
    .main-title-container {
        background: linear-gradient(135deg, #2E7D32 0%, #1B5E20 100%);
        padding: 20px !important; border-radius: 16px !important;
        box-shadow: 0 6px 20px rgba(46, 125, 50, 0.15); margin-bottom: 30px !important; text-align: center !important;
    }
    .main-title { font-size: 28px !important; font-weight: 900 !important; color: #FFFFFF !important; text-align: center !important; margin: 0 !important; }
    .stRadio > div { background-color: #FFFFFF !important; padding: 10px !important; border-radius: 14px !important; border: 1px solid #E0E0E0 !important; gap: 10px !important; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    .stRadio [data-testid="stMarkdownContainer"] p { font-weight: 600 !important; font-size: 14px !important; color: #333333 !important; }
    .premium-card { background: #FFFFFF; border: 1px solid #E0E0E0; border-right: 6px solid #4CAF50; padding: 20px !important; border-radius: 16px !important; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 20px; }
    .card-label { color: #666666 !important; font-size: 14px !important; font-weight: 600 !important; margin-bottom: 6px; }
    .card-value { color: #2E7D32 !important; font-size: 28px !important; font-weight: 700 !important; }
    .card-value-wages { color: #D4AF37 !important; font-size: 28px !important; font-weight: 700 !important; }
    [data-testid="stTable"], [data-testid="stDataFrame"] { background-color: #FFFFFF !important; border-radius: 12px !important; overflow: hidden !important; border: 1px solid #E0E0E0 !important; }
    h3 { color: #1B5E20 !important; font-size: 20px !important; font-weight: 700 !important; margin-top: 25px !important; border-right: 4px solid #4CAF50; padding-right: 10px !important; }
    div.stButton > button { background: linear-gradient(135deg, #2E7D32 0%, #4CAF50 100%) !important; color: #ffffff !important; font-weight: 700 !important; padding: 12px !important; border-radius: 12px !important; border: none !important; width: 100% !important; }
    .delete-btn div.stButton > button { background: linear-gradient(135deg, #C62828 0%, #E53935 100%) !important; }
    .stSelectbox div[data-baseweb="select"], .stNumberInput input, .stTextInput input, .stDateInput input { background-color: #FFFFFF !important; color: #111111 !important; border-radius: 10px !important; border: 1px solid #CCCCCC !important; }
    input { color: #111111 !important; -webkit-text-fill-color: #111111 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- دالات التعامل مع قاعدة البيانات السحابية عبر REST API ---
def get_data(table_name, params=""):
    url = f"{SUPABASE_URL}/rest/v1/{table_name}?{params}"
    res = requests.get(url, headers=headers)
    return res.json() if res.status_code == 200 else []

def insert_data(table_name, payload):
    url = f"{SUPABASE_URL}/rest/v1/{table_name}"
    requests.post(url, headers=headers, json=payload)

def delete_data(table_name, row_id):
    url = f"{SUPABASE_URL}/rest/v1/{table_name}?id=eq.{row_id}"
    requests.delete(url, headers=headers)

# --- تم تعديل الاسم هنا ليصبح Balmatik وبجانبه حقيبة سفر ---
st.markdown('<div class="main-title-container"><h1 class="main-title">🧳 Balmatik</h1></div>', unsafe_allow_html=True)

page = st.radio("📌 لوحة التحكم السريعة:", ["📊 التقارير والأيام", "📝 تسجيل الإنتاج", "⚙️ إدارة العمال والألوان"], horizontal=True)

# تحقق من إدخال الروابط أولاً
if SUPABASE_URL == "ضع_رابط_المشروع_هنا" or SUPABASE_KEY == "ضع_الرمز_الطويل_هنا":
    st.warning("⚠️ يرجى تزويد الكود بروابط اتصال Supabase الخاصة بك لتفعيل المزامنة الفورية.")
else:
    # --- 1. صفحة التقارير ---
    if page == "📊 التقارير والأيام":
        st.markdown("### 🔍 مراجعة التقارير والإنتاج السحابي المشترك")
        selected_date = st.date_input("📅 اختر اليوم تفقد سجلاته المشتركة:", datetime.now().date())
        formatted_date = selected_date.strftime("%Y-%m-%d")
        
        prod_data = get_data("daily_production", f"production_date=eq.{formatted_date}")
        
        total_bags = sum([item['quantity'] for item in prod_data]) if prod_data else 0
        total_wages = sum([item['quantity'] * item['price_per_piece'] for item in prod_data]) if prod_data else 0
        
        st.markdown(f"""
        <div class="premium-card">
            <div class="card-label">📦 إجمالي الحقائب المنتجة بالورشة لليوم ({formatted_date})</div>
            <div class="card-value">{total_bags} حقيبة جاهزة</div>
        </div>
        <div class="premium-card" style="border-right-color: #D4AF37;">
            <div class="card-label">💰 مستحقات الأجور الإجمالية الحالية لجميع الهواتف</div>
            <div class="card-value-wages">{total_wages:,.0f} دج</div>
        </div>
        """, unsafe_allow_html=True)
        
        if prod_data:
            df_prod = pd.DataFrame(prod_data)
            st.dataframe(df_prod[['id', 'worker_name', 'color_name', 'quantity']], use_container_width=True)
            
            st.write("---")
            st.markdown("### 🔴 إلغاء وتصحيح الحركات")
            record_to_delete = st.selectbox("اختر الحركة المراد إلغاؤها من السحابة:", df_prod['id'].tolist())
            st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
            if st.button("🗑️ إزالة الحركة المحددة فوراً من جميع الأجهزة", use_container_width=True):
                delete_data("daily_production", record_to_delete)
                st.success("✨ تم الحذف من الخادم السحابي بنجاح!")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info(f"💡 لا توجد أي بيانات مسجلة سحابياً في تاريخ {formatted_date}.")

    # --- 2. صفحة تسجيل الإنتاج ---
    elif page == "📝 تسجيل الإنتاج":
        st.markdown("### 📝 إدخال حركة إنتاج (ستظهر عند الجميع فوراً)")
        prod_date = st.date_input("📅 حدد تاريخ حركة الإنتاج:", datetime.now().date())
        formatted_prod_date = prod_date.strftime("%Y-%m-%d")
        
        workers = get_data("workers")
        colors = get_data("colors")
        
        if workers and colors:
            worker_opt = st.selectbox("👤 اختر اسم العامل:", [w['name'] for w in workers])
            color_opt = st.selectbox("🎨 اختر لون قماش الحقيبة:", [c['color_name'] for c in colors])
            qty = st.number_input("🔢 الكمية المنجزة:", min_value=1, value=10, step=1)
            
            if st.button("🚀 حفظ وإرسال البيانات للسحابة", use_container_width=True):
                payload = {
                    "production_date": formatted_prod_date,
                    "worker_name": worker_opt,
                    "color_name": color_opt,
                    "quantity": int(qty),
                    "price_per_piece": PRICE_PER_PIECE
                }
                insert_data("daily_production", payload)
                st.success(f"🎉 تم الحفظ بنجاح وتحديث كافة هواتف العمال والأصدقاء!")
        else:
            st.warning("يرجى التأكد من إضافة أسماء العمال والألوان أولاً في صفحة الإعدادات.")

    # --- 3. إدارة العمال والألوان ---
    elif page == "⚙️ إدارة العمال والألوان":
        st.markdown("### 👥 إدارة طاقم العمال السحابي")
        new_worker = st.text_input("اسم العامل الجديد:")
        if st.button("➕ إدراج العامل"):
            if new_worker.strip():
                insert_data("workers", {"name": new_worker.strip()})
                st.success("✅ تم الإضافة للسحابة!")
                st.rerun()
                
        st.write("---")
        st.markdown("### 🎨 تسيير قائمة ألوان الحقائب")
        new_color = st.text_input("اسم اللون الجديد:")
        if st.button("➕ إضافة خيار اللون"):
            if new_color.strip():
                insert_data("colors", {"color_name": new_color.strip()})
                st.success("🎨 تم تفعيل خيار اللون في السحابة!")
                st.rerun()
                
