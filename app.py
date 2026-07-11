import streamlit as st
import pandas as pd
import sqlite3

# --- 1. إعداد قاعدة البيانات ---
def get_db_connection():
    return sqlite3.connect('quran_data.db')

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # إنشاء الجدول بالهيكل الجديد المحدث
    c.execute('''CREATE TABLE IF NOT EXISTS students 
                 (المعرف INTEGER PRIMARY KEY AUTOINCREMENT, الاسم_الثلاثي TEXT, اللقب TEXT, 
                  تاريخ_الولادة TEXT, مكان_الولادة TEXT, المهنة TEXT, بطاقة_التعريف TEXT, 
                  المستوى_التعليمي TEXT, المرحلة TEXT, الوحدة INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS grades (المعرف INTEGER PRIMARY KEY, u1 REAL, u2 REAL, u3 REAL, u4 REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY, w_hifz REAL, w_riwaya REAL, w_diraya REAL, w_hodoor REAL)''')
    conn.commit()
    conn.close()

init_db()

# --- 2. التنسيق ---
st.set_page_config(page_title="نظام الرابطة", layout="wide")
st.markdown("""<style>.stApp { direction: rtl !important; text-align: right !important; } [data-testid="stSidebar"] { direction: rtl !important; }</style>""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #1A5276;'>إدارة الفرع المحلي للرابطة الوطنية للقرآن الكريم بالمكناسي</h1>", unsafe_allow_html=True)

# --- 3. القائمة ---
menu = ["تسجيل طالب جديد", "المتابعة البيداغوجية", "استخراج بطاقة أعداد", "تغيير الضوارب", "حذف طالب"]
choice = st.sidebar.selectbox("قائمة التحكم", menu)

# --- 4. العمليات ---

if choice == "تسجيل طالب جديد":
    st.subheader("📝 تسجيل طالب جديد")
    with st.form("student_form", clear_on_submit=True):
        st.markdown("### 👤 البيانات الشخصية")
        col1, col2 = st.columns(2)
        name = col1.text_input("الاسم الثلاثي")
        last_name = col2.text_input("اللقب")
        dob = col1.date_input("تاريخ الولادة")
        place_birth = col2.text_input("مكان الولادة")
        cin = col1.text_input("رقم بطاقة التعريف")
        job = col2.text_input("المهنة")
        edu_level = col1.text_input("المستوى التعليمي")
        
        st.markdown("### 🎓 بيانات المرحلة الدراسية")
        col3, col4 = st.columns(2)
        stage = col3.selectbox("المرحلة:", ["المرحلة الأولى: قالون", "المرحلة الثانية: نافع وحفص", "المرحلة الثالثة: القراءات"])
        unit = col4.number_input("رقم الوحدة:", min_value=1, max_value=4, value=1)
        
        submitted = st.form_submit_button("حفظ الطالب")
    
    if submitted:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO students (الاسم_الثلاثي, اللقب, تاريخ_الولادة, مكان_الولادة, المهنة, بطاقة_التعريف, المستوى_التعليمي, المرحلة, الوحدة) VALUES (?,?,?,?,?,?,?,?,?)", 
                  (name, last_name, str(dob), place_birth, job, cin, edu_level, stage, unit))
        c.execute("INSERT INTO grades (المعرف, u1, u2, u3, u4) VALUES (?,0,0,0,0)", (c.lastrowid,))
        conn.commit()
        st.success(f"✅ تم تسجيل الطالب. المعرف الخاص (ID) هو: {c.lastrowid}")
        conn.close()

elif choice == "المتابعة البيداغوجية":
    st.subheader("📊 المتابعة البيداغوجية")
    df = pd.read_sql_query("SELECT * FROM students", get_db_connection())
    if not df.empty:
        df['label'] = df['المعرف'].astype(str) + " - " + df['الاسم_الثلاثي']
        selection = st.selectbox("اختر الطالب:", df['label'].tolist())
        s_id = df[df['label'] == selection]['المعرف'].iloc[0]
        row = df[df['المعرف'] == s_id].iloc[0]
        
        st.markdown(f"### 👤 الطالب: {row['الاسم_الثلاثي']} {row['اللقب']} | المعرف (ID): {row['المعرف']}")
        st.info(f"🎓 المرحلة: {row['المرحلة']} | 📖 الوحدة الحالية: {row['الوحدة']}")
        
        new_grade = st.number_input("أدخل درجة الوحدة الحالية", 0.0, 20.0)
        if st.button("تحديث الدرجة"):
            conn = get_db_connection()
            conn.execute(f"UPDATE grades SET u{row['الوحدة']}=? WHERE المعرف=?", (new_grade, s_id))
            conn.commit()
            conn.close()
            st.success("✅ تم تحديث الدرجة!")

elif choice == "استخراج بطاقة أعداد":
    st.subheader("🖨️ استخراج بطاقة الأعداد")
    df = pd.read_sql_query("SELECT * FROM students", get_db_connection())
    if not df.empty:
        df['label'] = df['المعرف'].astype(str) + " - " + df['الاسم_الثلاثي']
        selection = st.selectbox("اختر الطالب للطباعة:", df['label'].tolist())
        s_id = df[df['label'] == selection]['المعرف'].iloc[0]
        
        student = df[df['المعرف'] == s_id].iloc[0]
        grades = pd.read_sql_query(f"SELECT * FROM grades WHERE المعرف={s_id}", get_db_connection()).iloc[0]
        
        st.markdown("---")
        st.markdown(f"### 📋 بطاقة أعداد الطالب")
        st.write(f"**الاسم:** {student['الاسم_الثلاثي']} {student['اللقب']} | **المعرف (ID):** {student['المعرف']}")
        st.write(f"**تاريخ الولادة:** {student['تاريخ_الولادة']} في {student['مكان_الولادة']} | **المهنة:** {student['المهنة']}")
        st.write(f"**المرحلة:** {student['المرحلة']} | **الوحدة:** {student['الوحدة']}")
        
        st.table(pd.DataFrame({
            "الوحدة": ["الوحدة 1", "الوحدة 2", "الوحدة 3", "الوحدة 4"],
            "الدرجة": [grades['u1'], grades['u2'], grades['u3'], grades['u4']]
        }))
        
        if st.button("طباعة البطاقة"):
            st.info("استخدم Ctrl+P في المتصفح لطباعة هذه البطاقة.")

elif choice == "تغيير الضوارب":
    st.subheader("⚙️ تعديل الضوارب")
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
        df['label'] = df['المعرف'].astype(str) + " - " + df['الاسم_الثلاثي']
        del_option = st.selectbox("اختر الطالب للحذف:", df['label'].tolist())
        del_id = df[df['label'] == del_option]['المعرف'].iloc[0]
        if st.button("حذف نهائي للطالب"):
            conn = get_db_connection()
            conn.execute("DELETE FROM students WHERE المعرف=?", (del_id,))
            conn.execute("DELETE FROM grades WHERE المعرف=?", (del_id,))
            conn.commit()
            conn.close()
            st.error("⚠️ تم حذف الطالب بنجاح!")
            st.rerun()
