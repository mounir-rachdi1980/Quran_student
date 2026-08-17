import streamlit as st
import pandas as pd
import sqlite3

# --- شعار الرابطة (رابط مباشر موثوق يظهر على السحابة) ---
logo_html = '<img src="https://i.ibb.co/3s688Z3/logo.jpg" style="width: 90px; height: 90px; border-radius: 50%; object-fit: cover; margin-bottom: 10px; border: 2px solid #2E86C1;" />'

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
                 (المعرف INTEGER PRIMARY KEY, u1 REAL, u2 REAL, u3 REAL, u4 REAL, 
                  hifz_d REAL DEFAULT 0, riwaya_d REAL DEFAULT 0, diraya_d REAL DEFAULT 0, hodoor_d REAL DEFAULT 0)''')
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

# --- 3. القائمة ---
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
        
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #D35400;'>🎓 المرحلة الدراسية ووحدة الطالب</h3>", unsafe_allow_html=True)
        
        stage = st.selectbox("اختر المرحلة", [
            "المرحلة الأولى: قالون (4 وحدات)", 
            "المرحلة الثانية: نافع وحفص (3 وحدات)", 
            "المرحلة الثالثة: سما وقراءات (4 وحدات)"
        ])
        
        unit = st.number_input("اختر الوحدة الحالية", min_value=1, max_value=4, value=1, step=1)
        
        submitted = st.form_submit_button("حفظ الطالب")

    if submitted:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO students (الاسم_الثلاثي, اللقب, تاريخ_الولادة, بطاقة_التعريف, المهنة, المستوى_التعليمي, المرحلة, الوحدة) VALUES (?,?,?,?,?,?,?,?)", 
                  (name, last_name, str(dob), cin, job, edu_level, stage, int(unit)))
        c.execute("INSERT INTO grades (المعرف, u1, u2, u3, u4, hifz_d, riwaya_d, diraya_d, hodoor_d) VALUES (?,0,0,0,0,0,0,0,0)", (c.lastrowid,))
        conn.commit()
        conn.close()
        st.success(f"✅ تم تسجيل الطالب بنجاح! (المعرف ID: {c.lastrowid})")

elif choice == "المتابعة البيداغوجية":
    st.subheader("📊 رصد الدرجات والارتقاء (حفظ، رواية، دراية، حضور)")
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM students", conn)
    conn.close()
    
    if not df.empty:
        s_id = st.selectbox("اختر الطالب (عن طريق المعرف ID)", df['المعرف'].tolist())
        row = df[df['المعرف'] == s_id].iloc[0]
        
        s_name = row.get('الاسم_الثلاثي', '')
        s_last = row.get('اللقب', '')
        s_edu = row.get('المستوى_التعليمي', 'غير متوفر')
        s_unit = row.get('الوحدة', 1)
        
        st.write(f"الطالب: {s_name} {s_last} | المستوى: {s_edu} | الوحدة الحالية: {s_unit}")
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        hifz = col1.number_input("درجة الحفظ", 0.0, 20.0, value=0.0)
        riwaya = col2.number_input("درجة الرواية", 0.0, 20.0, value=0.0)
        diraya = col1.number_input("درجة الدراية", 0.0, 20.0, value=0.0)
        hodoor = col2.number_input("درجة الحضور", 0.0, 20.0, value=0.0)
        
        if st.button("تحديث الدرجات والارتقاء"):
            conn = get_db_connection()
            w = pd.read_sql_query("SELECT * FROM settings WHERE id=1", conn).iloc[0]
            
            total_weights = w['w_hifz'] + w['w_riwaya'] + w['w_diraya'] + w['w_hodoor']
            avg = (hifz * w['w_hifz'] + riwaya * w['w_riwaya'] + diraya * w['w_diraya'] + hodoor * w['w_hodoor']) / total_weights
            
            unit_col = f"u{s_unit}"
            conn.execute(f"UPDATE grades SET {unit_col} = ?, hifz_d = ?, riwaya_d = ?, diraya_d = ?, hodoor_d = ? WHERE المعرف = ?", 
                        (avg, hifz, riwaya, diraya, hodoor, s_id))
            
            if avg >= 10 and s_unit < 4:
                conn.execute("UPDATE students SET الوحدة = الوحدة + 1 WHERE المعرف = ?", (s_id,))
                st.success(f"🎉 تم الارتقاء للوحدة الموالية! المعدل المحصل عليه: {avg:.2f}")
            else:
                st.info(f"📌 تم تسجيل المعدل بنجاح ({avg:.2f}).")
                
            conn.commit()
            conn.close()

elif choice == "بطاقة الأعداد":
    st.subheader("📄 استخراج بطاقة أعداد طالب")
    conn = get_db_connection()
    df_students = pd.read_sql_query("SELECT * FROM students", conn)
    df_grades = pd.read_sql_query("SELECT * FROM grades", conn)
    df_settings = pd.read_sql_query("SELECT * FROM settings WHERE id=1", conn).iloc[0]
    conn.close()
    
    if not df_students.empty:
        s_id = st.selectbox("اختر الطالب لاستخراج البطاقة", df_students['المعرف'].tolist())
        student = df_students[df_students['المعرف'] == s_id].iloc[0]
        grade_row = df_grades[df_grades['المعرف'] == s_id].iloc[0]
        
        s_name = student.get('الاسم_الثلاثي', '')
        s_last = student.get('اللقب', '')
        
        edu_key = next((col for col in student.index if 'المستوى' in col), 'المستوى_التعليمي')
        s_edu = student.get(edu_key, '')
        
        stage_key = next((col for col in student.index if 'المرحلة' in col), 'المرحلة')
        s_stage = student.get(stage_key, '')
        
        s_unit = student.get('الوحدة', 1)
        
        h_d = grade_row.get('hifz_d', 0.0)
        r_d = grade_row.get('riwaya_d', 0.0)
        d_d = grade_row.get('diraya_d', 0.0)
        hd_d = grade_row.get('hodoor_d', 0.0)
        
        w_h = df_settings['w_hifz']
        w_r = df_settings['w_riwaya']
        w_d = df_settings['w_diraya']
        w_hd = df_settings['w_hodoor']
        
        total_weights = w_h + w_r + w_d + w_hd
        if total_weights > 0:
            current_avg = (h_d * w_h + r_d * w_r + d_d * w_d + hd_d * w_hd) / total_weights
        else:
            current_avg = 0.0
        
        result_status = "ارتقاء" if current_avg >= 10 else "رسوب"
        result_color = "#27AE60" if current_avg >= 10 else "#C0392B"
        
        if current_avg < 10:
            note = "متوسط"
        elif 10 <= current_avg < 12:
            note = "فوق المتوسط"
        elif 12 <= current_avg < 14:
            note = "قريب من الحسن"
        elif 14 <= current_avg < 16:
            note = "حسن"
        else:
            note = "حسن جدا"

        st.markdown("---")
        st.markdown(f"""
        <div style="border: 2px solid #2E86C1; padding: 25px; border-radius: 12px; background-color: #ffffff; color: #000; font-family: Tahoma, sans-serif;">
            <div style="text-align: center;">
                {logo_html}
                <h3 style="color: #2E86C1; font-size: 22px; font-weight: bold; margin-bottom: 5px;">الرابطة الوطنية للقرآن الكريم - فرع المكناسي</h3>
                <h4 style="color: #555; font-size: 18px; font-weight: bold; margin-top: 0;">بطاقة أعداد الطالب</h4>
            </div>
            <hr style="border: 0.5px solid #ccc; margin: 15px 0;">
            <div style="font-size: 16px; line-height: 1.8; direction: rtl; text-align: right;">
                <p><b>الاسم الكامل:</b> <span style="font-weight: bold; color: #111;">{s_name} {s_last}</span></p>
                <p><b>المستوى التعليمي:</b> {s_edu} &nbsp;|&nbsp; <b>المرحلة:</b> {s_stage}</p>
                <p><b>الوحدة الحالية:</b> {s_unit}</p>
            </div>
            <br>
            <table style="width:100%; text-align: right; border-collapse: collapse; font-size: 15px;">
                <thead>
                    <tr style="background-color: #f2f2f2;">
                        <th style="border: 1px solid #ddd; padding: 10px;">مكونات التقييم</th>
                        <th style="border: 1px solid #ddd; padding: 10px;">إعداد المواد (الدرجة)</th>
                        <th style="border: 1px solid #ddd; padding: 10px;">الضارب (المعامل)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px;">الحفظ</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">{h_d}</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">{w_h}</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px;">الرواية</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">{r_d}</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">{w_r}</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px;">الدراية</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">{d_d}</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">{w_d}</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px;">الحضور</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">{hd_d}</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">{w_hd}</td>
                    </tr>
                </tbody>
            </table>
            <br>
            <div style="text-align: center; background-color: #f9f9f9; padding: 15px; border-radius: 8px; border: 1px dashed #2E86C1;">
                <p style="font-size: 17px; margin: 5px 0;"><b>المعدل العام للوحدة:</b> <span style="color: #2E86C1; font-weight: bold; font-size: 19px;">{current_avg:.2f} / 20</span></p>
                <p style="font-size: 17px; margin: 5px 0;"><b>النتيجة النهائية:</b> <span style="color: {result_color}; font-weight: bold; font-size: 19px;">{result_status}</span></p>
                <p style="font-size: 17px; margin: 5px 0;"><b>الملاحظة:</b> <span style="color: #8E44AD; font-weight: bold; font-size: 19px;">{note}</span></p>
            </div>
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
        w4 = st.number_input("ضارب الحضور", value=float(w['w_hodoor']))
        if st.form_submit_button("حفظ الضوارب"):
            conn.execute("UPDATE settings SET w_hifz=?, w_riwaya=?, w_diraya=?, w_hodoor=? WHERE id=1", (w1, w2, w3, w4))
            conn.commit()
            st.success("✅ تم تحديث الضوارب بنجاح!")
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
