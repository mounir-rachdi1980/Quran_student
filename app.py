import streamlit as st
import pandas as pd
import sqlite3

# --- 1. إعداد قاعدة البيانات ---
def get_db_connection():
    return sqlite3.connect('quran_data.db')

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # إضافة حقل المستوى التعليمي (المستوى_التعليمي)
    c.execute('''CREATE TABLE IF NOT EXISTS students 
                 (المعرف INTEGER PRIMARY KEY AUTOINCREMENT, الاسم_الثلاثي TEXT, اللقب TEXT, 
                  تاريخ_الولادة TEXT, بطاقة_التعريف TEXT, المهنة TEXT, المستوى_التعليمي TEXT, المرحلة TEXT, الوحدة INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS grades 
                 (المعرف INTEGER PRIMARY KEY, u1 REAL, u2 REAL, u3 REAL, u4 REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings 
                 (id INTEGER PRIMARY KEY, w_hifz REAL, w_riwaya REAL, w_diraya REAL, w_hodoor REAL)''')
    conn.commit()
    conn.close()

init_db()

# --- 2. التنسيق ---
st.set_page_config(page_title="نظام الرابطة", layout="wide", page_icon="🕌")
st.markdown("""<style>.stApp { direction: rtl !important; text-align: right !important; } [data-testid="stSidebar"] { direction: rtl !important; }</style>""", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;'>🕌 نظام الفرع المحلي للرابطة الوطنية للقرآن الكريم بالمكناسي</h1>", unsafe_allow_html=True)

# --- 3. قائمة التحكم المحدثة ---
menu = ["تسجيل طالب جديد", "المتابعة البيداغوجية", "تغيير الضوارب", "حذف طالب"]
choice = st.sidebar.selectbox("قائمة التحكم", menu)

# --- 4. العمليات ---
if choice == "تسجيل طالب جديد":
    st.subheader("📝 استمارة تسجيل طالب جديد")
    with st.form("student_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        name = col1.text_input("الاسم الثلاثي")
        last_name = col2.text_input("اللقب")
        dob = col1.date_input("تاريخ الولادة")
        cin = col2.text_input("رقم بطاقة التعريف")
        job = st.text_input("المهنة")
        edu_level = st.text_input("المستوى التعليمي")
        
        submitted = st.form_submit_button("حفظ الطالب")

    st.markdown("---")
    st.markdown("### 🎓 المرحلة الدراسية للطالب")
    stage = st.selectbox("اختر المرحلة", [
        "المرحلة الأولى: قالون (4 وحدات)", 
        "المرحلة الثانية: نافع وحفص (3 وحدات)", 
        "المرحلة الثالثة: سما وقراءات (4 وحدات)"
    ])
    
    if submitted:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO students (الاسم_الثلاثي, اللقب, تاريخ_الولادة, بطاقة_التعريف, المهنة, المستوى_التعليمي, المرحلة, الوحدة) VALUES (?,?,?,?,?,?,?,?)", 
                  (name, last_name, str(dob), cin, job, edu_level, stage, 1))
        c.execute("INSERT INTO grades (المعرف, u1, u2, u3, u4) VALUES (?,0,0,0,0)", (c.lastrowid,))
        conn.commit()
        conn.close()
        st.success(f"✅ تم تسجيل الطالب بنجاح! (تم منح المعرف رقم: {c.lastrowid})")

elif choice == "المتابعة البيداغوجية":
    st.subheader("📊 رصد الدرجات والارتقاء")
    df = pd.read_sql_query("SELECT * FROM students", get_db_connection())
    if not df.empty:
        s_id = st.selectbox("اختر الطالب (عن طريق المعرف)", df['المعرف'].tolist())
        row = df[df['المعرف'] == s_id].iloc[0]
        st.write(f"الطالب: {row['الاسم_الثلاثي']} {row['اللقب']} | المستوى: {row['المستوى_التعليمي']} | الوحدة: {row['الوحدة']}")
        
        new_grade = st.number_input("أدخل درجة الوحدة الحالية", 0.0, 20.0)
        if st.button("تحديث الدرجة والارتقاء"):
            conn = get_db_connection()
            conn.execute(f"UPDATE grades SET u{row['الوحدة']}=? WHERE المعرف=?", (new_grade, s_id))
            if new_grade >= 10:
                conn.execute("UPDATE students SET الوحدة=? WHERE المعرف=?", (row['الوحدة'] + 1, s_id))
                st.success("🎉 تم الارتقاء للوحدة التالية!")
            conn.commit()
            conn.close()

elif choice == "تغيير الضوارب":
    st.subheader("⚙️ تعديل الضوارب (المعاملات)")
    conn = get_db_connection()
    w = pd.read_sql_query("SELECT * FROM settings WHERE id=1", conn).iloc[0]
    with st.form("weights_form"):
        w1 = st.number_input("ضارب الحفظ", value=float(w['w_hifz']))
        w2 = st.number_input("ضارب الرواية", value=float(w['w_riwaya']))
        w3 = st.number_input("ضارب الدراية", value=float(w['w_diraya']))
        w4 = st.number_input("ضارب الحضور", value=float(w['w_hodoor']))
        if st.form_submit_button("حفظ الضوارب"):
            conn.execute("UPDATE settings SET w_hifz=?, w_riwaya=?, w_diraya=?, w_hodoor=? WHERE id=1", (w1, w2, w3, w4))
            conn.commit()
            st.success("✅ تم تحديث الضوارب!")
    conn.close()

elif choice == "حذف طالب":
    st.subheader("🗑️ حذف طالب")
    df = pd.read_sql_query("SELECT * FROM students", get_db_connection())
    if not df.empty:
        del_id = st.selectbox("اختر الطالب للحذف (بناءً على المعرف ID)", df['المعرف'].tolist())
        if st.button("حذف نهائي"):
            conn = get_db_connection()
            conn.execute("DELETE FROM students WHERE المعرف=?", (del_id,))
            conn.execute("DELETE FROM grades WHERE المعرف=?", (del_id,))
            conn.commit()
            conn.close()
            st.error("⚠️ تم حذف الطالب وجميع بياناته!")
            st.rerun()
