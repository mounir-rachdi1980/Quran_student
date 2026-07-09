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
                 (المعرف INTEGER PRIMARY KEY AUTOINCREMENT, الاسم_الثلاثي TEXT, اللقب TEXT, 
                  تاريخ_الولادة TEXT, بطاقة_التعريف TEXT, المهنة TEXT, المستوى_التعليمي TEXT, المرحلة TEXT, الوحدة INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS grades 
                 (المعرف INTEGER PRIMARY KEY, u1 REAL, u2 REAL, u3 REAL, u4 REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings 
                 (id INTEGER PRIMARY KEY, w_hifz REAL, w_riwaya REAL, w_diraya REAL, w_hodoor REAL)''')
    
    c.execute("SELECT count(*) FROM settings")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO settings (id, w_hifz, w_riwaya, w_diraya, w_hodoor) VALUES (1, 3.0, 2.0, 2.0, 1.0)")
    conn.commit()
    conn.close()

init_db()

# --- 2. التنسيق ---
st.set_page_config(page_title="نظام الرابطة", layout="wide", page_icon="🕌")
st.markdown("""<style>.stApp { direction: rtl !important; text-align: right !important; } [data-testid="stSidebar"] { direction: rtl !important; }</style>""", unsafe_allow_html=True)

st.markdown("""<h1 style="color: #1A5276; font-family: 'Arial', sans-serif; text-align: center; margin-bottom: 30px;">إدارة الفرع المحلي للرابطة الوطنية للقرآن الكريم بالمكناسي</h1>""", unsafe_allow_html=True)

# --- 3. القائمة ---
menu = ["تسجيل طالب جديد", "المتابعة البيداغوجية", "استخراج بطاقة الأعداد", "تغيير الضوارب", "حذف طالب"]
choice = st.sidebar.selectbox("قائمة التحكم", menu)

# --- 4. العمليات ---
if choice == "تسجيل طالب جديد":
    with st.form("student_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        name = col1.text_input("الاسم الثلاثي")
        last_name = col2.text_input("اللقب")
        stage = col1.selectbox("اختر المرحلة", ["المرحلة الأولى: قالون", "المرحلة الثانية: نافع وحفص", "المرحلة الثالثة: سما وقراءات"])
        unit = col2.number_input("رقم الوحدة", min_value=1, max_value=10, value=1)
        submitted = st.form_submit_button("حفظ الطالب")

    if submitted:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO students (الاسم_الثلاثي, اللقب, المرحلة, الوحدة) VALUES (?,?,?,?)", (name, last_name, stage, unit))
        c.execute("INSERT INTO grades (المعرف, u1, u2, u3, u4) VALUES (?,0,0,0,0)", (c.lastrowid,))
        conn.commit()
        conn.close()
        st.success(f"✅ تم التسجيل بنجاح! المعرف: {c.lastrowid}")

elif choice == "المتابعة البيداغوجية":
    df = pd.read_sql_query("SELECT * FROM students", get_db_connection())
    if not df.empty:
        s_id = st.selectbox("اختر الطالب", df['المعرف'].tolist())
        with st.form("grades_form"):
            col1, col2 = st.columns(2)
            hifz = col1.number_input("درجة الحفظ", 0.0, 20.0)
            riwaya = col2.number_input("درجة الرواية", 0.0, 20.0)
            diraya = col1.number_input("درجة الدراية", 0.0, 20.0)
            hodoor = col2.number_input("درجة المواظبة", 0.0, 20.0)
            if st.form_submit_button("حفظ الدرجات"):
                conn = get_db_connection()
                conn.execute("UPDATE grades SET u1=?, u2=?, u3=?, u4=? WHERE المعرف=?", (hifz, riwaya, diraya, hodoor, s_id))
                conn.commit()
                conn.close()
                st.success("✅ تم حفظ الدرجات!")

elif choice == "استخراج بطاقة الأعداد":
    conn = get_db_connection()
    students_df = pd.read_sql_query("SELECT * FROM students", conn)
    grades_df = pd.read_sql_query("SELECT * FROM grades", conn)
    settings = pd.read_sql_query("SELECT * FROM settings WHERE id=1", conn).iloc[0]
    conn.close()

    if not students_df.empty:
        s_id = st.selectbox("اختر الطالب", students_df['المعرف'])
        s = students_df[students_df['المعرف'] == s_id].iloc[0]
        g = grades_df[grades_df['المعرف'] == s_id].iloc[0]
        
        final_score = round(((g['u1']*settings['w_hifz']) + (g['u2']*settings['w_riwaya']) + (g['u3']*settings['w_diraya']) + (g['u4']*settings['w_hodoor'])) / (settings['w_hifz']+settings['w_riwaya']+settings['w_diraya']+settings['w_hodoor']), 2)
        
        if final_score < 10: res, note = "يرسب", "-"
        else:
            res = "يرتقي"
            if final_score < 12: note = "متوسط"
            elif final_score < 14: note = "فوق المتوسط"
            elif final_score < 16: note = "قريب من الحسن"
            elif final_score < 18: note = "حسن"
            else: note = "حسن جدا"

        st.markdown(f"""
        <div style="border: 3px double #1E4620; padding: 25px; border-radius: 10px; background-color: #FAFAFA; direction: rtl;">
            <h2 style="text-align: center; color: #1E4620; margin-bottom: 5px;">بطاقة تقييم وكشف أعداد طالب سنوي</h2>
            <h4 style="text-align: center; color: gray; margin-top: 0;">الفرع المحلي للرابطة الوطنية للقرآن الكريم بالمكناسي</h4>
            <hr style="border-top: 2px solid #1E4620; margin: 20px 0;">
            <div style="display: flex; justify-content: space-between; font-size: 18px; margin-bottom: 10px;">
                <p><b>الاسم واللقب:</b> {s['الاسم_الثلاثي']} {s['اللقب']}</p>
                <p><b>المعرف:</b> {s['المعرف']}</p>
            </div>
            <p style="font-size: 18px; margin-bottom: 20px;"><b>المرسم بالوحدة:</b> الوحدة رقم {s['الوحدة']} من {s['المرحلة']} | <b>المركز:</b> المكناسي</p>
            <table style="width: 100%; border-collapse: collapse; text-align: center; font-size: 18px;">
                <tr style="background: #1E4620; color: white;"><th style="padding: 10px;">المادة التقييمية</th><th style="padding: 10px;">العدد (من 20)</th></tr>
                <tr><td style="padding: 10px; border: 1px solid #ddd;">الحفظ</td><td style="padding: 10px; border: 1px solid #ddd;">{g['u1']}</td></tr>
                <tr><td style="padding: 10px; border: 1px solid #ddd;">الرواية</td><td style="padding: 10px; border: 1px solid #ddd;">{g['u2']}</td></tr>
                <tr><td style="padding: 10px; border: 1px solid #ddd;">الدراية</td><td style="padding: 10px; border: 1px solid #ddd;">{g['u3']}</td></tr>
                <tr><td style="padding: 10px; border: 1px solid #ddd;">المواظبة</td><td style="padding: 10px; border: 1px solid #ddd;">{g['u4']}</td></tr>
            </table>
            <div style="margin-top: 20px; font-weight: bold; color: #1E4620; font-size: 20px;">
                <p>المعدل العام: {final_score} / 20 | النتيجة: {res}</p>
                <p>الملاحظة: {note}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

elif choice == "تغيير الضوارب":
    conn = get_db_connection()
    w = pd.read_sql_query("SELECT * FROM settings WHERE id=1", conn).iloc[0]
    with st.form("weights_form"):
        w1, w2, w3, w4 = st.number_input("ضارب الحفظ", value=float(w['w_hifz'])), st.number_input("ضارب الرواية", value=float(w['w_riwaya'])), st.number_input("ضارب الدراية", value=float(w['w_diraya'])), st.number_input("ضارب الحضور", value=float(w['w_hodoor']))
        if st.form_submit_button("حفظ الضوارب"):
            conn.execute("UPDATE settings SET w_hifz=?, w_riwaya=?, w_diraya=?, w_hodoor=? WHERE id=1", (w1, w2, w3, w4))
            conn.commit()
            st.success("✅ تم التحديث!")
    conn.close()

elif choice == "حذف طالب":
    df = pd.read_sql_query("SELECT * FROM students", get_db_connection())
    if not df.empty:
        del_id = st.selectbox("اختر الطالب للحذف", df['المعرف'].tolist())
        if st.button("حذف نهائي"):
            conn = get_db_connection()
            conn.execute("DELETE FROM students WHERE المعرف=?", (del_id,))
            conn.execute("DELETE FROM grades WHERE المعرف=?", (del_id,))
            conn.commit()
            conn.close()
            st.rerun()      
