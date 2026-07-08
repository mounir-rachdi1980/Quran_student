import streamlit as st
import pandas as pd
import sqlite3

# --- 1. إعداد قاعدة البيانات ---
def get_db_connection():
    return sqlite3.connect('quran_data.db')

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # الجدول الشامل: يحتوي على البيانات القديمة + أعمدة المرحلة والوحدة الجديدة
    c.execute('''CREATE TABLE IF NOT EXISTS students 
                 (المعرف INTEGER PRIMARY KEY AUTOINCREMENT, الاسم_الثلاثي TEXT, اللقب TEXT, 
                  تاريخ_الولادة TEXT, بطاقة_التعريف TEXT, المهنة TEXT, المرحلة TEXT, الوحدة INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS grades 
                 (المعرف INTEGER PRIMARY KEY, u1 REAL, u2 REAL, u3 REAL, u4 REAL)''')
    conn.commit()
    conn.close()

init_db()

# --- 2. التنسيق ---
st.set_page_config(page_title="نظام الرابطة", layout="wide", page_icon="🕌")
st.markdown("""<style>.stApp { direction: rtl !important; text-align: right !important; } [data-testid="stSidebar"] { direction: rtl !important; }</style>""", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;'>🕌 نظام الفرع المحلي للرابطة</h1>", unsafe_allow_html=True)

# --- 3. القائمة ---
menu = ["تسجيل طالب جديد", "المتابعة البيداغوجية والدرجات", "قاعدة البيانات"]
choice = st.sidebar.selectbox("قائمة التحكم", menu)

# --- 4. العمليات ---
if choice == "تسجيل طالب جديد":
    st.subheader("📝 استمارة تسجيل طالب جديد")
    with st.form("full_student_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        name = col1.text_input("الاسم الثلاثي")
        last_name = col2.text_input("اللقب")
        dob = col1.date_input("تاريخ الولادة")
        cin = col2.text_input("رقم بطاقة التعريف")
        job = st.text_input("المهنة")
        stage = st.selectbox("المرحلة الدراسية", [
            "المرحلة الأولى: قالون (4 وحدات)", 
            "المرحلة الثانية: نافع وحفص (3 وحدات)", 
            "المرحلة الثالثة: سما وقراءات (4 وحدات)"
        ])
        if st.form_submit_button("حفظ الطالب بالكامل"):
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("INSERT INTO students (الاسم_الثلاثي, اللقب, تاريخ_الولادة, بطاقة_التعريف, المهنة, المرحلة, الوحدة) VALUES (?,?,?,?,?,?,?)", 
                      (name, last_name, str(dob), cin, job, stage, 1))
            c.execute("INSERT INTO grades (المعرف, u1, u2, u3, u4) VALUES (?,0,0,0,0)", (c.lastrowid,))
            conn.commit()
            conn.close()
            st.success("✅ تم حفظ الطالب مع كامل بياناته!")

elif choice == "المتابعة البيداغوجية والدرجات":
    st.subheader("📊 رصد الدرجات والارتقاء")
    df = pd.read_sql_query("SELECT * FROM students", get_db_connection())
    if not df.empty:
        s_id = st.selectbox("اختر الطالب", df['المعرف'].tolist())
        row = df[df['المعرف'] == s_id].iloc[0]
        st.info(f"الطالب: {row['الاسم_الثلاثي']} | المرحلة: {row['المرحلة']} | الوحدة الحالية: {row['الوحدة']}")
        
        curr_unit = row['الوحدة']
        new_grade = st.number_input(f"درجة الوحدة {curr_unit}", 0.0, 20.0)
        
        if st.button("تحديث الدرجة والارتقاء"):
            conn = get_db_connection()
            conn.execute(f"UPDATE grades SET u{curr_unit}=? WHERE المعرف=?", (new_grade, s_id))
            if new_grade >= 10:
                conn.execute("UPDATE students SET الوحدة=? WHERE المعرف=?", (curr_unit + 1, s_id))
                st.success("🎉 تم التحديث والارتقاء للوحدة التالية!")
            else:
                st.warning("⚠️ الدرجة غير كافية للارتقاء.")
            conn.commit()
            conn.close()

elif choice == "قاعدة البيانات":
    st.subheader("🗂️ عرض بيانات الطلاب")
    df = pd.read_sql_query("SELECT * FROM students", get_db_connection())
    st.dataframe(df).rerun()
