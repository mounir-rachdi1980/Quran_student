import streamlit as st
import pandas as pd
import sqlite3

# --- 1. إعداد قاعدة البيانات ---
def get_db_connection():
    return sqlite3.connect('quran_data.db')

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # إنشاء الجداول إذا لم تكن موجودة
    c.execute('''CREATE TABLE IF NOT EXISTS students 
                 (المعرف INTEGER PRIMARY KEY AUTOINCREMENT, الاسم_الثلاثي TEXT, اللقب TEXT, 
                  تاريخ_الولادة TEXT, بطاقة_التعريف TEXT, المهنة TEXT, المستوى_التعليمي TEXT, المرحلة TEXT, الوحدة INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS grades (المعرف INTEGER PRIMARY KEY, u1 REAL, u2 REAL, u3 REAL, u4 REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY, w_hifz REAL, w_riwaya REAL, w_diraya REAL, w_hodoor REAL)''')
    conn.commit()
    conn.close()

init_db()

# --- 2. التنسيق ---
st.set_page_config(page_title="نظام الرابطة", layout="wide")
st.markdown("""<style>.stApp { direction: rtl !important; text-align: right !important; } [data-testid="stSidebar"] { direction: rtl !important; }</style>""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #1A5276;'>إدارة الفرع المحلي للرابطة الوطنية للقرآن الكريم بالمكناسي</h1>", unsafe_allow_html=True)

# --- 3. القائمة الجانبية ---
menu = ["تسجيل طالب جديد", "المتابعة البيداغوجية", "استخراج بطاقة أعداد", "تغيير الضوارب", "حذف طالب"]
choice = st.sidebar.selectbox("قائمة التحكم", menu)

# --- 4. العمليات ---

# تسجيل طالب جديد
if choice == "تسجيل طالب جديد":
    st.subheader("📝 تسجيل طالب جديد")
    with st.form("student_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        name = col1.text_input("الاسم الثلاثي")
        last_name = col2.text_input("اللقب")
        cin = col1.text_input("رقم بطاقة التعريف")
        edu_level = col2.text_input("المستوى التعليمي")
        stage = st.selectbox("اختر المرحلة", [
            "المرحلة الأولى: قالون", 
            "المرحلة الثانية: نافع وحفص", 
            "المرحلة الثالثة: القراءات"
        ])
        submitted = st.form_submit_button("حفظ الطالب")
    
    if submitted:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO students (الاسم_الثلاثي, اللقب, بطاقة_التعريف, المستوى_التعليمي, المرحلة, الوحدة) VALUES (?,?,?,?,?,?)", 
                  (name, last_name, cin, edu_level, stage, 1))
        c.execute("INSERT INTO grades (المعرف, u1, u2, u3, u4) VALUES (?,0,0,0,0)", (c.lastrowid,))
        conn.commit()
        st.success(f"✅ تم التسجيل! المعرف الخاص بالطالب هو: {c.lastrowid}")
        conn.close()

# المتابعة البيداغوجية
elif choice == "المتابعة البيداغوجية":
    st.subheader("📊 المتابعة البيداغوجية")
    df = pd.read_sql_query("SELECT * FROM students", get_db_connection())
    if not df.empty:
        # جعل الاختيار يعرض المعرف والاسم لسهولة التحديد
        df['عرض'] = df['المعرف'].astype(str) + " - " + df['الاسم_الثلاثي'] + " " + df['القب']
        selected_option = st.selectbox("اختر الطالب:", df['عرض'].tolist())
        s_id = df[df['عرض'] == selected_option]['المعرف'].values[0]
        
        row = df[df['المعرف'] == s_id].iloc[0]
        st.markdown(f"### 👤 الطالب: {row['الاسم_الثلاثي']} {row['القب']} | المعرف (ID): {row['المعرف']}")
        st.info(f"🎓 المرحلة الحالية: {row['المرحلة']} | 📖 الوحدة الحالية: {row['الوحدة']}")
        
        new_grade = st.number_input("أدخل درجة الوحدة الحالية", 0.0, 20.0)
        if st.button("تحديث الدرجة والارتقاء"):
            conn = get_db_connection()
            conn.execute(f"UPDATE grades SET u{row['الوحدة']}=? WHERE المعرف=?", (new_grade, s_id))
            if new_grade >= 10 and row['الوحدة'] < 4:
                conn.execute("UPDATE students SET الوحدة=? WHERE المعرف=?", (row['الوحدة'] + 1, s_id))
                st.success("🎉 تهانينا! تم الارتقاء للوحدة التالية.")
            conn.commit()
            conn.close()

# استخراج بطاقة أعداد
elif choice == "استخراج بطاقة أعداد":
    st.subheader("🖨️ معاينة وطباعة بطاقة الأعداد")
    df = pd.read_sql_query("SELECT * FROM students", get_db_connection())
    if not df.empty:
        df['عرض'] = df['المعرف'].astype(str) + " - " + df['الاسم_الثلاثي'] + " " + df['القب']
        selected_option = st.selectbox("اختر الطالب للمعاينة", df['عرض'].tolist())
        s_id = df[df['عرض'] == selected_option]['المعرف'].values[0]
        
        student = df[df['المعرف'] == s_id].iloc[0]
        grades = pd.read_sql_query(f"SELECT * FROM grades WHERE المعرف={s_id}", get_db_connection()).iloc[0]
        
        st.markdown("---")
        st.markdown(f"### 📋 بطاقة أعداد الطالب: {student['الاسم_الثلاثي']} {student['القب']}")
        st.markdown(f"**المعرف (ID):** {student['المعرف']} | **المرحلة:** {student['المرحلة']} | **الوحدة الحالية:** {student['الوحدة']}")
        
        st.table(pd.DataFrame({
            "الوحدة": ["الوحدة 1", "الوحدة 2", "الوحدة 3", "الوحدة 4"],
            "الدرجة": [grades['u1'], grades['u2'], grades['u3'], grades['u4']]
        }))
        
        st.info("للطباعة: اضغط Ctrl+P في لوحة المفاتيح.")

# حذف طالب
elif choice == "حذف طالب":
    st.subheader("🗑️ حذف طالب")
    df = pd.read_sql_query("SELECT * FROM students", get_db_connection())
    if not df.empty:
        df['عرض'] = df['المعرف'].astype(str) + " - " + df['الاسم_الثلاثي']
        del_option = st.selectbox("اختر الطالب للحذف:", df['عرض'].tolist())
        del_id = df[df['عرض'] == del_option]['المعرف'].values[0]
        
        if st.button("حذف نهائي للطالب"):
            conn = get_db_connection()
            conn.execute("DELETE FROM students WHERE المعرف=?", (del_id,))
            conn.execute("DELETE FROM grades WHERE المعرف=?", (del_id,))
            conn.commit()
            conn.close()
            st.error("⚠️ تم حذف الطالب بنجاح!")
            st.rerun()
