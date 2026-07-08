import streamlit as st
import pandas as pd
import sqlite3
import os

# --- 1. إعداد قاعدة البيانات المحلية ---
def get_db_connection():
    conn = sqlite3.connect('quran_data.db')
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students 
                 (المعرف INTEGER PRIMARY KEY AUTOINCREMENT, الاسم_الثلاثي TEXT, اللقب TEXT, تاريخ_الولادة TEXT, بطاقة_التعريف TEXT, المهنة TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS grades 
                 (المعرف INTEGER PRIMARY KEY, الحفظ REAL, الرواية REAL, الدراية REAL, الحضور REAL)''')
    conn.commit()
    conn.close()

init_db()

# --- 2. إعدادات الصفحة ---
st.set_page_config(page_title="نظام الفرع المحلي للرابطة الوطنية للقرآن الكريم بالمكناسي", layout="wide", page_icon="🕌")

st.markdown("""
    <style>
    [data-testid="stSidebar"], .main .block-container, div[data-testid="stForm"], .stDataFrame { direction: rtl !important; text-align: right !important; }
    th, td, .stMarkdown, p, h1, h2, h3, h4, h5, h6, label { text-align: right !important; }
    input, select, textarea { direction: rtl !important; text-align: right !important; }
    div[data-testid="stHorizontalBlock"] { direction: rtl !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color: #1E4620; text-align: center;'>🕌 نظام الفرع المحلي للرابطة الوطنية للقرآن الكريم بالمكناسي</h1>", unsafe_allow_html=True)

# --- 3. قائمة التحكم ---
menu = ["تسجيل طالب جديد", "رصد وتعديل الدرجات", "استخراج بطاقة الأعداد", "حذف طالب"]
choice = st.sidebar.selectbox("قائمة التحكم والتنقل", menu)

# --- 4. العمليات ---
if choice == "تسجيل طالب جديد":
    st.subheader("📝 استمارة بطاقة إرشادات طالب جديد")
    with st.form("student_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("الاسم الثلاثي")
            dob = st.date_input("تاريخ الولادة")
        with col2:
            last_name = st.text_input("اللقب (اسم العائلة)")
            cin = st.text_input("رقم بطاقة التعريف / رقم القيد")
        job = st.text_input("المهنة / المستوى الدراسي")
        
        if st.form_submit_button("حفظ بيانات الطالب"):
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("INSERT INTO students (الاسم_الثلاثي, اللقب, تاريخ_الولادة, بطاقة_التعريف, المهنة) VALUES (?,?,?,?,?)", 
                      (name, last_name, str(dob), cin, job))
            student_id = c.lastrowid
            c.execute("INSERT INTO grades (المعرف, الحفظ, الرواية, الدراية, الحضور) VALUES (?,0,0,0,0)", (student_id,))
            conn.commit()
            conn.close()
            st.success(f"🎉 تم تسجيل الطالب! المعرف الخاص به هو: {student_id}")

    st.write("### 👥 قائمة الطلاب المسجلين:")
    df = pd.read_sql_query("SELECT * FROM students", get_db_connection())
    st.dataframe(df, use_container_width=True)

elif choice == "رصد وتعديل الدرجات":
    st.subheader("📊 دفتر رصد أعداد وتقييمات الطلاب")
    df = pd.read_sql_query("SELECT * FROM students", get_db_connection())
    if df.empty:
        st.warning("⚠️ لا يوجد طلاب مسجلون حالياً.")
    else:
        s_id = st.selectbox("اختر المعرف للطالب", df['المعرف'].tolist())
        grades = pd.read_sql_query(f"SELECT * FROM grades WHERE المعرف={s_id}", get_db_connection()).iloc[0]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1: hifz = st.number_input("الحفظ", value=float(grades['الحفظ']), min_value=0.0, max_value=20.0)
        with col2: riwaya = st.number_input("الرواية", value=float(grades['الرواية']), min_value=0.0, max_value=20.0)
        with col3: diraya = st.number_input("الدراية", value=float(grades['الدراية']), min_value=0.0, max_value=20.0)
        with col4: hodoor = st.number_input("الحضور", value=float(grades['الحضور']), min_value=0.0, max_value=20.0)
        
        if st.button("تحديث وحفظ الدرجات"):
            conn = get_db_connection()
            conn.execute("UPDATE grades SET الحفظ=?, الرواية=?, الدراية=?, الحضور=? WHERE المعرف=?", (hifz, riwaya, diraya, hodoor, s_id))
            conn.commit()
            conn.close()
            st.success("✅ تم تحديث الدرجات بنجاح!")

elif choice == "استخراج بطاقة الأعداد":
    st.subheader("🖨️ استخراج وطباعة كشف الأعداد")
    df = pd.read_sql_query("SELECT * FROM students", get_db_connection())
    if not df.empty:
        s_id = st.selectbox("اختر الطالب لاستخراج كشفه", df['المعرف'].tolist())
        student = df[df['المعرف'] == s_id].iloc[0]
        grades = pd.read_sql_query(f"SELECT * FROM grades WHERE المعرف={s_id}", get_db_connection()).iloc[0]
        
        st.info(f"عرض بطاقة الطالب: {student['الاسم_الثلاثي']} {student['اللقب']}")
        st.write(f"المعدل الحسابي البسيط: {round((grades['الحفظ']+grades['الرواية']+grades['الدراية']+grades['الحضور'])/4, 2)} / 20")
    else:
        st.warning("لا توجد بيانات.")

elif choice == "حذف طالب":
    st.subheader("🗑️ حذف طالب من النظام")
    df = pd.read_sql_query("SELECT * FROM students", get_db_connection())
    if not df.empty:
        s_id = st.selectbox("اختر الطالب للحذف:", df['المعرف'].tolist())
        if st.button("حذف نهائي"):
            conn = get_db_connection()
            conn.execute("DELETE FROM students WHERE المعرف=?", (s_id,))
            conn.execute("DELETE FROM grades WHERE المعرف=?", (s_id,))
            conn.commit()
            conn.close()
            st.error("⚠️ تم حذف بيانات الطالب نهائياً!")
            st.rerun()
    else:
st.info("لا يوجد طلاب للحذف.")
if st.button("حفظ الدرجات"):
