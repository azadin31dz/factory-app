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

# --- التنسيق الجمالي العصري باللون الأزرق الفاتح ---
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
        letter-spacing: 1px;
    }
    
    /* أزرار اختيار الصفحات العلوية (Tabs التصفح السريع) */
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
    
    /* كروت عرض البيانات والإحصائيات المشعة */
    .premium-card {
        background: #FFFFFF;
        border: 1px solid #D6E4F0;
        border-right: 6px solid #3B82F6; /* حافة زرقاء عصرية */
        padding: 20px !important;
        border-radius: 18px !important;
        box-shadow: 0 6px 16px rgba(30, 58, 138, 0.05);
        margin-bottom: 20px;
        transition: transform 0.2s;
    }
    .premium-card:hover {
        transform: translateY(-2px);
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
        color: #D97706 !important; /* لون ذهبي دافئ وواضح للأجور */
        font-size: 30px !important;
        
                
