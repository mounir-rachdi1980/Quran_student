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
    c.execute('''CREATE TABLE IF NOT EXISTS students 
                 (المعرف INTEGER PRIMARY KEY AUTOINCREMENT, الاسم_الثلاثي TEXT, اللقب TEXT, تاريخ_الولادة TEXT, بطاقة_التعريف TEXT, المهنة TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS grades 
                 (المعرف INTEGER PRIMARY KEY, الحفظ REAL, الرواية REAL, الدراية REAL, الحضور REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings 
                 (id INTEGER PRIMARY KEY, w_hifz REAL, w_riwaya REAL, w_diraya REAL, w_hodoor REAL)''')
    c.execute("SELECT count(*) FROM settings")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO settings (id, w_hifz, w_riwaya, w_diraya, w_hodoor) VALUES (1, 3.0, 2.0, 2.0, 1.0)")
    conn.commit()
    conn.close()

init_db()

# --- 2. إعدادات الصفحة ---
st.set_page_config(page_title="نظام الرابطة", layout="wide", page_icon="🕌")
st.markdown("<style>[data-testid='stSidebar'] { direction: rtl; text-align: right; }</style>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;'>🕌 نظام الفرع المحلي للرابطة الوطنية للقرآن الكريم بالمكناسي</h1>", unsafe_allow_html=True)

# --- 3. قائمة التحكم ---
menu = ["تسجيل طالب جديد", "رصد وتعديل الدرجات", "تعديل ضوارب المواد", "استخراج بطاقة الأعداد", "حذف طالب"]
choice = st.sidebar.selectbox("قائمة التحكم والتنقل", menu)

# --- 4. العمليات ---
if choice == "تسجيل طالب جديد":
    st.subheader("📝 استمارة طالب جديد")
    with st.form("student_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("الاسم الثلاثي")
            dob = st.date_input("تاريخ الولادة")
        with col2:
            last_name = st.text_input("اللقب")
            cin = st.text_input("رقم البطاقة")
        job = st.text_input("المهنة")
        if st.form_submit_button("حفظ"):
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("INSERT INTO students (الاسم_الثلاثي, اللقب, تاريخ_الولادة, بطاقة_التعريف, المهنة) VALUES (?,?,?,?,?)", (name, last_name, str(dob), cin, job))
            s_id = c.lastrowid
            c.execute("INSERT INTO grades (المعرف, الحفظ, الرواية, الدراية, الحضور) VALUES (?,0,0,0,0)", (s_id,))
            conn.commit()
            conn.close()
            st.success("تم التسجيل!")

elif choice == "رصد وتعديل الدرجات":
    st.subheader("📊 رصد الدرجات")
    df = pd.read_sql_query("SELECT * FROM students", get_db_connection())
    if not df.empty:
        s_id = st.selectbox("اختر الطالب", df['المعرف'].tolist())
        grades = pd.read_sql_query(f"SELECT * FROM grades WHERE المعرف={s_id}", get_db_connection()).iloc[0]
        h = st.number_input("الحفظ", value=float(grades['الحفظ']))
        r = st.number_input("الرواية", value=float(grades['الرواية']))
        d = st.number_input("الدراية", value=float(grades['الدراية']))
        ho = st.number_input("الحضور", value=float(grades['الحضور']))
        if st.button("حفظ التغييرات"):
            conn = get_db_connection()
            conn.execute("UPDATE grades SET الحفظ=?, الرواية=?, الدراية=?, الحضور=? WHERE المعرف=?", (h, r, d, ho, s_id))
            conn.commit()
            conn.close()
            st.success("تم التحديث!")

elif choice == "تعديل ضوارب المواد":
    st.subheader("⚙️ ضبط الضوارب")
    conn = get_db_connection()
    w = pd.read_sql_query("SELECT * FROM settings WHERE id=1", conn).iloc[0]
    with st.form("weights_form"):
        w1 = st.number_input("ضارب الحفظ", value=float(w['w_hifz']))
        w2 = st.number_input("ضارب الرواية", value=float(w['w_riwaya']))
        w3 = st.number_input("ضارب الدراية", value=float(w['w_diraya']))
        w4 = st.number_input("ضارب الحضور", value=float(w['w_hodoor']))
        if st.form_submit_button("حفظ"):
            conn.execute("UPDATE settings SET w_hifz=?, w_riwaya=?, w_diraya=?, w_hodoor=? WHERE id=1", (w1, w2, w3, w4))
            conn.commit()
            st.success("تم تحديث الضوارب!")
    conn.close()

elif choice == "استخراج بطاقة الأعداد":
    st.subheader("🖨️ كشف الأعداد")
    df = pd.read_sql_query("SELECT * FROM students", get_db_connection())
    if not df.empty:
        s_id = st.selectbox("اختر الطالب", df['المعرف'].tolist())
        st_data = df[df['المعرف'] == s_id].iloc[0]
        g = pd.read_sql_query(f"SELECT * FROM grades WHERE المعرف={s_id}", get_db_connection()).iloc[0]
        w = pd.read_sql_query("SELECT * FROM settings WHERE id=1", get_db_connection()).iloc[0]
        avg = ((g['الحفظ']*w['w_hifz'])+(g['الرواية']*w['w_riwaya'])+(g['الدراية']*w['w_diraya'])+(g['الحضور']*w['w_hodoor'])) / (w['w_hifz']+w['w_riwaya']+w['w_diraya']+w['w_hodoor'])
        st.write(f"المعدل الموزون للطالب {st_data['الاسم_الثلاثي']}: **{round(avg, 2)}**")

elif choice == "حذف طالب":
    st.subheader("🗑️ حذف طالب")
    df = pd.read_sql_query("SELECT * FROM students", get_db_connection())
    if not df.empty:
        s_id = st.selectbox("اختر الطالب للحذف", df['المعرف'].tolist())
        if st.button("حذف نهائي"):
            conn = get_db_connection()
            conn.execute("DELETE FROM students WHERE المعرف=?", (s_id,))
            conn.execute("DELETE FROM grades WHERE المعرف=?", (s_id,))
            conn.commit()
            conn.close()
            st.rerun()
