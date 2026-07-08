import streamlit as st
import pandas as pd
import sqlite3

# --- 1. إعداد قاعدة البيانات ---
def get_db_connection():
    conn = sqlite3.connect('quran_data.db')
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # جدول الطلاب
    c.execute('''CREATE TABLE IF NOT EXISTS students 
                 (المعرف INTEGER PRIMARY KEY AUTOINCREMENT, الاسم_الثلاثي TEXT, اللقب TEXT, تاريخ_الولادة TEXT, بطاقة_التعريف TEXT, المهنة TEXT)''')
    # جدول الدرجات
    c.execute('''CREATE TABLE IF NOT EXISTS grades 
                 (المعرف INTEGER PRIMARY KEY, الحفظ REAL, الرواية REAL, الدراية REAL, الحضور REAL)''')
    # جدول الضوارب (جدول جديد)
    c.execute('''CREATE TABLE IF NOT EXISTS settings 
                 (id INTEGER PRIMARY KEY, w_hifz REAL, w_riwaya REAL, w_diraya REAL, w_hodoor REAL)''')
    
    # التأكد من وجود قيم افتراضية
    c.execute("SELECT count(*) FROM settings")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO settings (id, w_hifz, w_riwaya, w_diraya, w_hodoor) VALUES (1, 3.0, 2.0, 2.0, 1.0)")
    
    conn.commit()
    conn.close()

init_db()

# --- 2. إعدادات الصفحة ---
st.set_page_config(page_title="نظام الفرع المحلي للرابطة الوطنية للقرآن الكريم بالمكناسي", layout="wide", page_icon="🕌")

st.markdown("""
    <style>
    [data-testid="stSidebar"], .main .block-container, div[data-testid="stForm"], .stDataFrame { direction: rtl !important; text-align: right !important; }
    th, td, .stMarkdown, p, h1, h2, h3, h4, h5, h6, label { text-align: right !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color: #1E4620; text-align: center;'>🕌 نظام الفرع المحلي للرابطة الوطنية للقرآن الكريم بالمكناسي</h1>", unsafe_allow_html=True)

# --- 3. قائمة التحكم (تمت إضافة الخيار هنا) ---
menu = ["تسجيل طالب جديد", "رصد وتعديل الدرجات", "تعديل ضوارب المواد", "استخراج بطاقة الأعداد", "حذف طالب"]
choice = st.sidebar.selectbox("قائمة التحكم والتنقل", menu)

# --- 4. العمليات ---
if choice == "تسجيل طالب جديد":
    # ... (نفس كود التسجيل السابق) ...
    st.subheader("📝 استمارة بطاقة إرشادات طالب جديد")
    # (باقي كود التسجيل كما هو...)

elif choice == "رصد وتعديل الدرجات":
    # ... (نفس كود رصد الدرجات السابق) ...
    st.subheader("📊 دفتر رصد أعداد وتقييمات الطلاب")
    # (باقي كود الدرجات كما هو...)

elif choice == "تعديل ضوارب المواد":
    st.subheader("⚙️ ضبط ضوارب (معاملات) المواد")
    conn = get_db_connection()
    weights = pd.read_sql_query("SELECT * FROM settings WHERE id=1", conn).iloc[0]
    
    with st.form("weights_form"):
        w1 = st.number_input("ضارب الحفظ", value=float(weights['w_hifz']), min_value=0.1)
        w2 = st.number_input("ضارب الرواية", value=float(weights['w_riwaya']), min_value=0.1)
        w3 = st.number_input("ضارب الدراية", value=float(weights['w_diraya']), min_value=0.1)
        w4 = st.number_input("ضارب الحضور", value=float(weights['w_hodoor']), min_value=0.1)
        
        if st.form_submit_button("حفظ الضوارب الجديدة"):
            conn.execute("UPDATE settings SET w_hifz=?, w_riwaya=?, w_diraya=?, w_hodoor=? WHERE id=1", (w1, w2, w3, w4))
            conn.commit()
            st.success("✅ تم تحديث الضوارب بنجاح!")
    conn.close()

elif choice == "استخراج بطاقة الأعداد":
    # (قم بتحديث كود استخراج الأعداد ليقرأ من جدول settings)
    # ...
