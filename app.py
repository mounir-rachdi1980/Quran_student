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

st.markdown("""
    <h1 style="color: #1A5276; font-family: 'Arial', sans-serif; text-align: center; margin-bottom: 30px;">
        إدارة الفرع المحلي للرابطة الوطنية للقرآن الكريم بالمكناسي
    </h1>
    """, unsafe_allow_html=True)

# --- 3. القائمة ---
menu = ["تسجيل طالب جديد", "المتابعة البيداغوجية", "استخراج بطاقة الأعداد", "تغيير الضوارب", "حذف طالب"]
choice = st.sidebar.selectbox("قائمة التحكم", menu)

# --- 4. العمليات ---
if choice == "تسجيل طالب جديد":
    st.markdown("<div style='text-align: center;'><h2 style='color: #2E86C1;'>📝 استمارة تسجيل طالب جديد</h2></div>", unsafe_allow_html=True)
    with st.form("student_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        name = col1.text_input("الاسم الثلاثي")
        last_name = col2.text_input("اللقب")
        dob = col1.date_input("تاريخ الولادة")
        cin = col2.text_input("رقم بطاقة التعريف")
        job = col1.text_input("المهنة")
        edu_level = col2.text_input("المستوى التعليمي")
        submitted = st.form_submit_button("حفظ الطالب")

    st.markdown("<div style='text-align: center; margin-top: 30px;'><h3 style='color: #D35400;'>🎓 المرحلة الدراسية للطالب</h3></div>", unsafe_allow_html=True)
    stage = st.selectbox("اختر المرحلة", [
        "المرحلة الأولى: قالون (4 وحدات)", 
        "المرحلة الثانية: نافع وحفص (3 وحدات)", 
        "المرحلة الثالثة: سما وقراءات (4 وحدات)"
    ], label_visibility="collapsed")
    
    if submitted:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO students (الاسم_الثلاثي, اللقب, تاريخ_الولادة, بطاقة_التعريف, المهنة, المستوى_التعليمي, المرحلة, الوحدة) VALUES (?,?,?,?,?,?,?,?)", 
                  (name, last_name, str(dob), cin, job, edu_level, stage, 1))
        c.execute("INSERT INTO grades (المعرف, u1, u2, u3, u4) VALUES (?,0,0,0,0)", (c.lastrowid,))
        conn.commit()
        conn.close()
        st.success(f"✅ تم تسجيل الطالب بنجاح! (المعرف ID: {c.lastrowid})")

elif choice == "المتابعة البيداغوجية":
    st.subheader("📊 رصد الدرجات الأربع")
    df = pd.read_sql_query("SELECT * FROM students", get_db_connection())
    if not df.empty:
        s_id = st.selectbox("اختر الطالب (عن طريق المعرف ID)", df['المعرف'].tolist())
        row = df[df['المعرف'] == s_id].iloc[0]
        st.write(f"الطالب: {row['الاسم_الثلاثي']} {row['اللقب']} | المستوى: {row['المستوى_التعليمي']}")
        
        with st.form("grades_form"):
            col1, col2 = st.columns(2)
            hifz = col1.number_input("درجة الحفظ", 0.0, 20.0, value=0.0)
            riwaya = col2.number_input("درجة الرواية", 0.0, 20.0, value=0.0)
            diraya = col1.number_input("درجة الدراية", 0.0, 20.0, value=0.0)
            hodoor = col2.number_input("درجة المواظبة", 0.0, 20.0, value=0.0)
            
            if st.form_submit_button("حفظ الدرجات"):
                conn = get_db_connection()
                conn.execute("UPDATE grades SET u1=?, u2=?, u3=?, u4=? WHERE المعرف=?", (hifz, riwaya, diraya, hodoor, s_id))
                conn.commit()
                conn.close()
                st.success("✅ تم حفظ الدرجات الأربع بنجاح!")

elif choice == "استخراج بطاقة الأعداد":
    st.subheader("🖨️ استخراج وطباعة كشف الأعداد السنوي")
    conn = get_db_connection()
    students_df = pd.read_sql_query("SELECT * FROM students", conn)
    grades_df = pd.read_sql_query("SELECT * FROM grades", conn)
    settings = pd.read_sql_query("SELECT * FROM settings WHERE id=1", conn).iloc[0]
    conn.close()

    if students_df.empty:
        st.warning("⚠️ لا توجد بيانات طلاب متوفرة لاستخراج الكشوفات.")
    else:
        s_id = st.selectbox("اختر معرف الطالب لإنتاج كشفه", students_df['المعرف'])
        s_info = students_df[students_df['المعرف'] == s_id].iloc[0]
        g_info = grades_df[grades_df['المعرف'] == s_id].iloc[0]
        
        total_points = (g_info['u1'] * settings['w_hifz']) + \
                       (g_info['u2'] * settings['w_riwaya']) + \
                       (g_info['u3'] * settings['w_diraya']) + \
                       (g_info['u4'] * settings['w_hodoor'])
        
        sum_weights = settings['w_hifz'] + settings['w_riwaya'] + settings['w_diraya'] + settings['w_hodoor']
        final_score = round(total_points / sum_weights, 2)
        
        # المنطق الجديد للنتيجة والملاحظة
        if final_score >= 10.0:
            result = "مرتقٍ (ناجح) 🎉"
            note = "مبارك للطالب، نوصيه بمواصلة الجد والاجتهاد في المرحلة القادمة."
            result_color = "#1E4620"
        else:
            result = "راسب (لم يرتقِ) 📑"
            note = "نوصي الطالب بمضاعفة الجهود والتركيز أكثر في الفترات القادمة."
            result_color = "#8B0000"
        
        st.markdown(f"""
        <div style="border: 3px double #1E4620; padding: 25px; border-radius: 10px; background-color: #FAFAFA; direction: rtl; font-family: 'Arial', sans-serif; text-align: right;">
            <div style="text-align: center;">
                <h2 style="margin: 0; color: #1E4620;">بطاقة تقييم وكشف أعداد طالب سنوي</h2>
                <h4 style="color: gray; margin-top: 5px;">الفرع المحلي للرابطة الوطنية للقرآن الكريم بالمكناسي</h4>
                <hr style="border-top: 2px solid #1E4620; margin: 15px 0;">
            </div>
            <table style="width: 100%; font-size: 18px; margin-bottom: 20px; text-align: right; border: none;">
                <tr><td><b>المعرف:</b> {s_info['المعرف']}</td><td><b>الاسم:</b> {s_info['الاسم_الثلاثي']} {s_info['اللقب']}</td></tr>
                <tr><td><b>المهنة:</b> {s_info['المهنة']}</td><td><b>تاريخ الولادة:</b> {s_info['تاريخ_الولادة']}</td></tr>
            </table>
            <table style="width: 100%; border-collapse: collapse; text-align: center; font-size: 18px;">
                <tr style="background-color: #1E4620; color: white;">
                    <th style="padding: 10px; border: 1px solid black;">المادة التقييمية</th>
                    <th style="padding: 10px; border: 1px solid black;">العدد (من 20)</th>
                </tr>
                <tr><td style="border: 1px solid black; padding: 10px;">الحفظ</td><td style="border: 1px solid black; padding: 10px;">{g_info['u1']}</td></tr>
                <tr><td style="border: 1px solid black; padding: 10px;">الرواية</td><td style="border: 1px solid black; padding: 10px;">{g_info['u2']}</td></tr>
                <tr><td style="border: 1px solid black; padding: 10px;">الدراية</td><td style="border: 1px solid black; padding: 10px;">{g_info['u3']}</td></tr>
                <tr><td style="border: 1px solid black; padding: 10px;">المواظبة</td><td style="border: 1px solid black; padding: 10px;">{g_info['u4']}</td></tr>
            </table>
            <div style="margin-top: 20px; font-weight: bold; color: #1E4620;">
                <p style="font-size: 22px;">المعدل العام: {final_score} / 20</p>
                <p style="color: {result_color}; font-size: 20px;">القرار النهائي: {result}</p>
                <p style="color: #444; font-size: 16px; font-style: italic;">ملاحظة اللجنة: {note}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

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
        del_id = st.selectbox("اختر الطالب للحذف (عن طريق المعرف ID)", df['المعرف'].tolist())
        if st.button("حذف نهائي للطالب"):
            conn = get_db_connection()
            conn.execute("DELETE FROM students WHERE المعرف=?", (del_id,))
            conn.execute("DELETE FROM grades WHERE المعرف=?", (del_id,))
            conn.commit()
            conn.close()
            st.error("⚠️ تم حذف الطالب وجميع بياناته بنجاح!")
            st.rerun()
