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
st.markdown("<h1 style='text-align: center;'>🕌 نظام الفرع المحلي للرابطة الوطنية للقرآن الكريم بالمكناسي</h1>", unsafe_allow_html=True)

# --- 3. القائمة (تمت إضافة بطاقة الأعداد) ---
menu = ["تسجيل طالب جديد", "المتابعة البيداغوجية", "بطاقة الأعداد", "تغيير الضوارب", "حذف طالب", "الإعدادات"]
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
    st.subheader("📊 رصد الدرجات والارتقاء")
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM students", conn)
    conn.close()
    
    if not df.empty:
        s_id = st.selectbox("اختر الطالب (عن طريق المعرف ID)", df['المعرف'].tolist())
        row = df[df['المعرف'] == s_id].iloc[0]
        st.write(f"الطالب: {row['الاسم_الثلاثي']} {row['اللقب']} | المستوى: {row['المستوى_التعليمي']} | الوحدة: {row['الوحدة']}")
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        hifz = col1.number_input("درجة الحفظ", 0.0, 20.0)
        riwaya = col2.number_input("درجة الرواية", 0.0, 20.0)
        diraya = col1.number_input("درجة الدراية", 0.0, 20.0)
        hodoor = col2.number_input("درجة المواظبة", 0.0, 20.0)
        
        if st.button("تحديث الدرجات والارتقاء"):
            conn = get_db_connection()
            w = pd.read_sql_query("SELECT * FROM settings WHERE id=1", conn).iloc[0]
            # حساب المعدل
            avg = (hifz*w['w_hifz'] + riwaya*w['w_riwaya'] + diraya*w['w_diraya'] + hodoor*w['w_hodoor']) / (w['w_hifz'] + w['w_riwaya'] + w['w_diraya'] + w['w_hodoor'])
            
            conn.execute(f"UPDATE grades SET u{row['الوحدة']}=? WHERE المعرف=?", (avg, s_id))
            if avg >= 10:
                conn.execute("UPDATE students SET الوحدة=? WHERE المعرف=?", (row['الوحدة'] + 1, s_id))
                st.success(f"🎉 تم الارتقاء! المعدل هو: {avg:.2f}")
            else:
                st.warning(f"⚠️ المعدل {avg:.2f} غير كافٍ للارتقاء.")
            conn.commit()
            conn.close()

elif choice == "بطاقة الأعداد":
    st.subheader("📄 استخراج بطاقة أعداد طالب")
    conn = get_db_connection()
    df_students = pd.read_sql_query("SELECT * FROM students", conn)
    df_grades = pd.read_sql_query("SELECT * FROM grades", conn)
    conn.close()
    
    if not df_students.empty:
        s_id = st.selectbox("اختر الطالب لاستخراج البطاقة", df_students['المعرف'].tolist())
        student = df_students[df_students['المعرف'] == s_id].iloc[0]
        grade_row = df_grades[df_grades['المعرف'] == s_id].iloc[0]
        
        st.markdown("---")
        # تصميم شكل بطاقة الأعداد
        st.markdown(f"""
        <div style="border: 2px solid #2E86C1; padding: 20px; border-radius: 10px; background-color: #f9f9f9; color: #000;">
            <h3 style="text-align: center; color: #2E86C1;">الرابطة الوطنية للقرآن الكريم - فرع المكناسي</h3>
            <h4 style="text-align: center;">بطاقة أعداد الطالب</h4>
            <hr>
            <p><b>الاسم الكامل:</b> {student['الاسم_الثلاثي']} {student['اللقب']}</p>
            <p><b>المستوى التعليمي:</b> {student['المستوى_التعليمي']} | <b>المرحلة:</b> {student['المرحلة']}</p>
            <p><b>الوحدة الحالية:</b> {student['الوحدة']}</p>
            <br>
            <table style="width:100%; text-align: right; border-collapse: collapse;">
                <tr>
                    <th style="border-bottom: 1px solid #ddd; padding: 8px;">الوحدة</th>
                    <th style="border-bottom: 1px solid #ddd; padding: 8px;">المعدل المسجل</th>
                </tr>
                <tr>
                    <td style="padding: 8px;">الوحدة الأولى (u1)</td>
                    <td style="padding: 8px;">{grade_row['u1']}</td>
                </tr>
                <tr>
                    <td style="padding: 8px;">الوحدة الثانية (u2)</td>
                    <td style="padding: 8px;">{grade_row['u2']}</td>
                </tr>
                <tr>
                    <td style="padding: 8px;">الوحدة الثالثة (u3)</td>
                    <td style="padding: 8px;">{grade_row['u3']}</td>
                </tr>
                <tr>
                    <td style="padding: 8px;">الوحدة الرابعة (u4)</td>
                    <td style="padding: 8px;">{grade_row['u4']}</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("💡 يمكنك الضغط على زر الطباعة في متصفحك (Ctrl + P) لطباعة هذه البطاقة مباشرة.")

elif choice == "تغيير الضوارب":
    st.subheader("⚙️ تعديل الضوارب (المعاملات)")
    conn = get_db_connection()
    w = pd.read_sql_query("SELECT * FROM settings WHERE id=1", conn).iloc[0]
    with st.form("weights_form"):
        w1 = st.number_input("ضارب الحفظ", value=float(w['w_hifz']))
        w2 = st.number_input("ضارب الرواية", value=float(w['w_riwaya']))
        w3 = st.number_input("ضارب الدراية", value=float(w['w_diraya']))
        w4 = st.number_input("ضارب المواظبة", value=float(w['w_hodoor']))
        if st.form_submit_button("حفظ الضوارب"):
            conn.execute("UPDATE settings SET w_hifz=?, w_riwaya=?, w_diraya=?, w_hodoor=? WHERE id=1", (w1, w2, w3, w4))
            conn.commit()
            st.success("✅ تم تحديث الضوارب!")
    conn.close()

elif choice == "حذف طالب":
    st.subheader("🗑️ حذف طالب")
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM students", conn)
    conn.close()
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

elif choice == "الإعدادات":
    st.subheader("🛠️ إعدادات النظام العامة")
    st.info("هذه لوحة التحكم الخاصة بالإعدادات العامة للبرنامج وتتضمن حالياً ضبط المعاملات والضوارب الخاصة بالتقييم واختبار الاتصال.")
    if st.button("التحقق من اتصال قاعدة البيانات"):
        conn = get_db_connection()
        st.success("✅ اتصال قاعدة البيانات يعمل بشكل سليم!")
        conn.close()
