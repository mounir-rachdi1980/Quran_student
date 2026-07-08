import streamlit as st
import pandas as pd
import sqlite3

# --- 1. إعداد قاعدة البيانات ---
def get_db_connection():
    return sqlite3.connect('quran_data.db')

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students 
                 (المعرف INTEGER PRIMARY KEY AUTOINCREMENT, الاسم_الثلاثي TEXT, اللقب TEXT, المرحلة TEXT, الوحدة INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS grades 
                 (المعرف INTEGER PRIMARY KEY, u1 REAL, u2 REAL, u3 REAL, u4 REAL)''')
    conn.commit()
    conn.close()

init_db()

# --- 2. التنسيق ---
st.set_page_config(page_title="نظام الرابطة", layout="wide", page_icon="🕌")
st.markdown("""
    <style>
    .stApp { direction: rtl !important; text-align: right !important; }
    [data-testid="stSidebar"] { direction: rtl !important; text-align: right !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🕌 نظام الفرع المحلي للرابطة الوطنية للقرآن الكريم بالمكناسي</h1>", unsafe_allow_html=True)

# --- 3. القائمة ---
menu = ["تسجيل طالب جديد", "رصد الدرجات والارتقاء", "بطاقة متابعة الطالب"]
choice = st.sidebar.selectbox("قائمة التحكم والتنقل", menu)

# --- 4. العمليات ---
if choice == "تسجيل طالب جديد":
    st.subheader("📝 استمارة طالب جديد")
    with st.form("student_form", clear_on_submit=True):
        name = st.text_input("الاسم الثلاثي")
        last_name = st.text_input("اللقب")
        stage = st.selectbox("المرحلة الدراسية", 
                             ["المرحلة الأولى: رواية قالون (4 وحدات)", 
                              "المرحلة الثانية: قراءة نافع وحفص (3 وحدات)", 
                              "المرحلة الثالثة: أهل سما وقراءات (4 وحدات)"])
        if st.form_submit_button("حفظ الطالب"):
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("INSERT INTO students (الاسم_الثلاثي, اللقب, المرحلة, الوحدة) VALUES (?,?,?,?)", (name, last_name, stage, 1))
            c.execute("INSERT INTO grades (المعرف, u1, u2, u3, u4) VALUES (?,0,0,0,0)", (c.lastrowid,))
            conn.commit()
            conn.close()
            st.success("✅ تم تسجيل الطالب في الوحدة 1!")

elif choice == "رصد الدرجات والارتقاء":
    st.subheader("📊 رصد الدرجات والارتقاء")
    df = pd.read_sql_query("SELECT * FROM students", get_db_connection())
    if not df.empty:
        s_id = st.selectbox("اختر الطالب", df['المعرف'].tolist())
        s_data = df[df['المعرف'] == s_id].iloc[0]
        grades = pd.read_sql_query(f"SELECT * FROM grades WHERE المعرف={s_id}", get_db_connection()).iloc[0]
        
        st.write(f"الطالب: {s_data['الاسم_الثلاثي']} | المرحلة: {s_data['المرحلة']} | **الوحدة الحالية: {s_data['الوحدة']}**")
        
        current_unit = s_data['الوحدة']
        new_grade = st.number_input(f"أدخل درجة الوحدة {current_unit}", min_value=0.0, max_value=20.0)
        
        if st.button("حفظ النتيجة"):
            conn = get_db_connection()
            conn.execute(f"UPDATE grades SET u{current_unit}=? WHERE المعرف=?", (new_grade, s_id))
            if new_grade >= 10:
                new_unit = current_unit + 1
                conn.execute("UPDATE students SET الوحدة=? WHERE المعرف=?", (new_unit, s_id))
                st.success(f"🎉 أحسنت! تم الارتقاء إلى الوحدة {new_unit}")
            else:
                st.warning("⚠️ الدرجة أقل من 10، يرجى إعادة المحاولة للبقاء في نفس الوحدة.")
            conn.commit()
            conn.close()

elif choice == "بطاقة متابعة الطالب":
    st.subheader("📋 كشف درجات الطالب")
    df = pd.read_sql_query("SELECT * FROM students", get_db_connection())
    if not df.empty:
        s_id = st.selectbox("اختر الطالب", df['المعرف'].tolist())
        row = df[df['المعرف'] == s_id].iloc[0]
        g = pd.read_sql_query(f"SELECT * FROM grades WHERE المعرف={s_id}", get_db_connection()).iloc[0]
        
        st.write(f"### {row['الاسم_الثلاثي']} {row['اللقب']}")
        st.write(f"**المرحلة:** {row['المرحلة']}")
        st.write(f"**الوحدة الحالية:** {row['الوحدة']}")
        
        df_grades = pd.DataFrame({
            "الوحدة": ["الوحدة 1", "الوحدة 2", "الوحدة 3", "الوحدة 4"],
            "الدرجة": [g['u1'], g['u2'], g['u3'], g['u4']]
        })
        st.table(df_grades)
