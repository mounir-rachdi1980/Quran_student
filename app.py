import streamlit as st
import pandas as pd
import sqlite3

# --- 1. إعداد قاعدة البيانات وتحديث الجداول والأعمدة تلقائياً ---
def get_db_connection():
    return sqlite3.connect('quran_data.db')

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # إنشاء جدول الطلاب إذا لم يكن موجوداً
    c.execute('''CREATE TABLE IF NOT EXISTS students 
                 (المعرف INTEGER PRIMARY KEY AUTOINCREMENT, الاسم_الثلاثي TEXT, اللقب TEXT, 
                  تاريخ_الولادة TEXT, بطاقة_التعريف TEXT, المهنة TEXT, المستوى_التعليمي TEXT, المرحلة TEXT, الوحدة INTEGER, رقم_الترسيم TEXT, المرسم_ب TEXT, المركز TEXT)''')
    
    # التحقق من الأعمدة الناقصة في جدول students وإضافتها تلقائياً إن لم تكن موجودة
    cursor = c.execute("PRAGMA table_info(students)")
    existing_student_columns = [column[1] for column in cursor.fetchall()]
    
    students_columns_to_add = {
        'رقم_الترسيم': 'TEXT',
        'المرسم_ب': 'TEXT',
        'المركز': 'TEXT',
        'المهنة': 'TEXT',
        'المستوى_التعليمي': 'TEXT',
        'بطاقة_التعريف': 'TEXT'
    }
    
    for col, col_type in students_columns_to_add.items():
        if col not in existing_student_columns:
            c.execute(f"ALTER TABLE students ADD COLUMN {col} {col_type}")

    # إنشاء جدول الدرجات إذا لم يكن موجوداً
    c.execute('''CREATE TABLE IF NOT EXISTS grades 
                 (المعرف INTEGER PRIMARY KEY, u1 REAL, u2 REAL, u3 REAL, u4 REAL, 
                  hifz_d REAL DEFAULT 0, riwaya_d REAL DEFAULT 0, diraya_d REAL DEFAULT 0, hodoor_d REAL DEFAULT 0,
                  diraya_kitabya REAL DEFAULT 0, mowadaba REAL DEFAULT 0, taqeem_mudarris REAL DEFAULT 0, diraya_shafowya REAL DEFAULT 0)''')
    
    # إنشاء جدول الإعدادات إذا لم يكن موجوداً
    c.execute('''CREATE TABLE IF NOT EXISTS settings 
                 (id INTEGER PRIMARY KEY, w_hifz REAL, w_riwaya REAL, w_diraya REAL, w_hodoor REAL,
                  w_diraya_kitabya REAL DEFAULT 2.0, w_mowadaba REAL DEFAULT 1.0, w_taqeem_mudarris REAL DEFAULT 1.0, w_hifz_item REAL DEFAULT 1.0, w_diraya_shafowya REAL DEFAULT 1.0)''')
    
    c.execute("SELECT count(*) FROM settings")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO settings (id, w_hifz, w_riwaya, w_diraya, w_hodoor, w_diraya_kitabya, w_mowadaba, w_taqeem_mudarris, w_hifz_item, w_diraya_shafowya) VALUES (1, 3.0, 2.0, 2.0, 1.0, 2.0, 1.0, 1.0, 1.0, 1.0)")
    
    # التحقق من الأعمدة الناقصة في جدول settings وإضافتها تلقائياً
    cursor = c.execute("PRAGMA table_info(settings)")
    existing_settings_columns = [column[1] for column in cursor.fetchall()]
    
    settings_columns_to_add = {
        'w_diraya_kitabya': 'REAL DEFAULT 2.0',
        'w_mowadaba': 'REAL DEFAULT 1.0',
        'w_taqeem_mudarris': 'REAL DEFAULT 1.0',
        'w_hifz_item': 'REAL DEFAULT 1.0',
        'w_diraya_shafowya': 'REAL DEFAULT 1.0'
    }
    
    for col, col_type in settings_columns_to_add.items():
        if col not in existing_settings_columns:
            c.execute(f"ALTER TABLE settings ADD COLUMN {col} {col_type}")

    conn.commit()
    conn.close()

init_db()

# --- 2. التنسيق العام ---
st.set_page_config(page_title="نظام الرابطة", layout="wide", page_icon="🕌")
st.markdown("""
<style>
    .stApp { direction: rtl !important; text-align: right !important; }
    [data-testid="stSidebar"] { direction: rtl !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🕌 نظام الفرع المحلي للرابطة الوطنية للقرآن الكريم بالمكناسي</h1>", unsafe_allow_html=True)

# --- 3. القائمة الجانبية ---
menu = ["تسجيل طالب جديد", "المتابعة البيداغوجية", "بطاقة الأعداد", "تغيير الضوارب", "حذف طالب", "الإعدادات"]
choice = st.sidebar.selectbox("قائمة التحكم", menu)

# --- 4. العمليات ---
if choice == "تسجيل طالب جديد":
    st.markdown("<h2 style='color: #2E86C1; text-align: center;'>📝 استمارة تسجيل طالب جديد</h2>", unsafe_allow_html=True)
    
    with st.form("student_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        name = col1.text_input("الاسم الثلاثي")
        last_name = col2.text_input("اللقب")
        dob = col1.date_input("تاريخ الولادة")
        cin = col2.text_input("رقم بطاقة التعريف")
        job = col1.text_input("المهنة")
        edu_level = col2.text_input("المستوى التعليمي")
        
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #D35400;'>🎓 بيانات الترسيم والإدارة</h3>", unsafe_allow_html=True)
        
        col3, col4, col5 = st.columns(3)
        num_tarsim = col3.text_input("رقم الترسيم")
        morsam_b = col4.text_input("المرسم بـ (المستوى/الفصل)")
        markaz = col5.text_input("المركز")
        
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
        c.execute("INSERT INTO students (الاسم_الثلاثي, اللقب, تاريخ_الولادة, بطاقة_التعريف, المهنة, المستوى_التعليمي, المرحلة, الوحدة, رقم_الترسيم, المرسم_ب, المركز) VALUES (?,?,?,?,?,?,?,?,?,?,?)", 
                  (name, last_name, str(dob), cin, job, edu_level, stage, int(unit), num_tarsim, morsam_b, markaz))
        c.execute("INSERT INTO grades (المعرف, u1, u2, u3, u4) VALUES (?,0,0,0,0)", (c.lastrowid,))
        conn.commit()
        conn.close()
        st.success(f"✅ تم تسجيل الطالب بنجاح! (المعرف ID: {c.lastrowid})")

elif choice == "المتابعة البيداغوجية":
    st.subheader("📊 رصد الاختبارات والدرجات")
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM students", conn)
    conn.close()
    
    if not df.empty:
        s_id = st.selectbox("اختر الطالب (عن طريق المعرف ID)", df['المعرف'].tolist())
        row = df[df['المعرف'] == s_id].iloc[0]
        
        s_name = row.get('الاسم_الثلاثي', '')
        s_last = row.get('اللقب', '')
        s_unit = row.get('الوحدة', 1)
        
        st.write(f"الطالب: {s_name} {s_last} | الوحدة الحالية: {s_unit}")
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        diraya_kitabya = col1.number_input("دراية كتابيا (عدد من 20)", 0.0, 20.0, value=0.0)
        mowadaba = col2.number_input("المواظبة (عدد من 20)", 0.0, 20.0, value=0.0)
        taqeem_mudarris = col1.number_input("تقييم المدرس (عدد من 20)", 0.0, 20.0, value=0.0)
        hifz = col2.number_input("الحفظ (عدد من 20)", 0.0, 20.0, value=0.0)
        diraya_shafowya = col1.number_input("دراية شفويا (عدد من 20)", 0.0, 20.0, value=0.0)
        
        if st.button("تحديث الدرجات والحساب"):
            conn = get_db_connection()
            w = pd.read_sql_query("SELECT * FROM settings WHERE id=1", conn).iloc[0]
            
            h_dk = diraya_kitabya * w['w_diraya_kitabya']
            h_mw = mowadaba * w['w_mowadaba']
            h_tm = taqeem_mudarris * w['w_taqeem_mudarris']
            h_hf = hifz * w['w_hifz_item']
            h_ds = diraya_shafowya * w['w_diraya_shafowya']
            
            total_weights = w['w_diraya_kitabya'] + w['w_mowadaba'] + w['w_taqeem_mudarris'] + w['w_hifz_item'] + w['w_diraya_shafowya']
            total_scores = h_dk + h_mw + h_tm + h_hf + h_ds
            
            avg = total_scores / total_weights if total_weights > 0 else 0
            
            unit_col = f"u{s_unit}"
            conn.execute(f"UPDATE grades SET {unit_col} = ?, diraya_kitabya = ?, mowadaba = ?, taqeem_mudarris = ?, hifz_d = ?, diraya_shafowya = ? WHERE المعرف = ?", 
                        (avg, diraya_kitabya, mowadaba, taqeem_mudarris, hifz, diraya_shafowya, s_id))
            
            if avg >= 10 and s_unit < 4:
                conn.execute("UPDATE students SET الوحدة = الوحدة + 1 WHERE المعرف = ?", (s_id,))
                st.success(f"🎉 تم الارتقاء للوحدة الموالية! المعدل المحصل عليه: {avg:.2f}")
            else:
                st.info(f"📌 تم تسجيل المعدل بنجاح ({avg:.2f}).")
                
            conn.commit()
            conn.close()

elif choice == "بطاقة الأعداد":
    st.subheader("📄 استخراج بطاقة أعداد طالب بالشكل الرسمي")
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
        num_tarsim = student.get('رقم_الترسيم', 'غير متوفر')
        morsam_b = student.get('المرسم_ب', 'غير متوفر')
        markaz = student.get('المركز', 'غير متوفر')
        
        dk = grade_row.get('diraya_kitabya', 0.0)
        mw = grade_row.get('mowadaba', 0.0)
        tm = grade_row.get('taqeem_mudarris', 0.0)
        hf = grade_row.get('hifz_d', 0.0)
        ds = grade_row.get('diraya_shafowya', 0.0)
        
        w_dk = df_settings['w_diraya_kitabya']
        w_mw = df_settings['w_mowadaba']
        w_tm = df_settings['w_taqeem_mudarris']
        w_hf = df_settings['w_hifz_item']
        w_ds = df_settings['w_diraya_shafowya']
        
        h_dk = dk * w_dk
        h_mw = mw * w_mw
        h_tm = tm * w_tm
        h_hf = hf * w_hf
        h_ds = ds * w_ds
        
        total_weights = w_dk + w_mw + w_tm + w_hf + w_ds
        total_scores = h_dk + h_mw + h_tm + h_hf + h_ds
        current_avg = total_scores / total_weights if total_weights > 0 else 0.0
        
        result_status = "يرتقي" if current_avg >= 10 else "لا يرتقي"
        
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

        logo_html = '<img src="https://i.ibb.co/3s688Z3/logo.jpg" style="width: 70px; height: 70px; border-radius: 50%; object-fit: cover; border: 2px solid #2E86C1;" />'

        st.markdown("---")
        card_html = f"""
        <div style="border: 2px solid #333; padding: 30px; border-radius: 5px; background-color: #ffffff; color: #000; font-family: Tahoma, sans-serif; max-width: 800px; margin: auto;">
            
            <table style="width: 100%; border: none; margin-bottom: 20px;">
                <tr>
                    <td style="width: 30%; text-align: right; vertical-align: top; font-size: 13px; line-height: 1.6;">
                        <b>الجمهورية التونسية</b><br>
                        الجمعية المحافظة على القرآن الكريم والأخلاق الفاضلة بصفاقس<br>
                        (القراءات)
                    </td>
                    <td style="width: 40%; text-align: center; vertical-align: middle;">
                        {logo_html}
                    </td>
                    <td style="width: 30%; text-align: left; vertical-align: top; font-size: 13px; line-height: 1.6;">
                        الحمد لله وحده<br>
                        صفاقس في 13 محرم 1448<br>
                        الموافق لـ: 28 جوان 2026<br>
                        2025-2026
                    </td>
                </tr>
            </table>

            <div style="text-align: center; margin: 20px 0;">
                <div style="display: inline-block; border: 2px solid #333; padding: 8px 30px; border-radius: 8px; font-size: 20px; font-weight: bold;">
                    بطاقة الاعداد
                </div>
            </div>

            <table style="width: 100%; border: none; margin-bottom: 20px; font-size: 15px;">
                <tr>
                    <td style="width: 50%;"><b>الاسم واللقب:</b> {s_name} {s_last}</td>
                    <td style="width: 50%;"><b>رقم الترسيم:</b> {num_tarsim}</td>
                </tr>
                <tr>
                    <td style="width: 50%; padding-top: 8px;"><b>المرسم بـ:</b> {morsam_b}</td>
                    <td style="width: 50%; padding-top: 8px;"><b>المركز:</b> {markaz}</td>
                </tr>
            </table>

            <table style="width: 100%; border-collapse: collapse; text-align: center; margin-bottom: 25px; font-size: 14px;">
                <thead>
                    <tr style="background-color: #f8f9fa;">
                        <th style="border: 1px solid #333; padding: 8px; width: 40%;">الإختبار</th>
                        <th style="border: 1px solid #333; padding: 8px; width: 20%;">الضارب</th>
                        <th style="border: 1px solid #333; padding: 8px; width: 20%;">العدد</th>
                        <th style="border: 1px solid #333; padding: 8px; width: 20%;">الحاصل</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="border: 1px solid #333; padding: 8px; text-align: right;">دراية كتابيا</td>
                        <td style="border: 1px solid #333; padding: 8px;">{w_dk}</td>
                        <td style="border: 1px solid #333; padding: 8px;">{dk}</td>
                        <td style="border: 1px solid #333; padding: 8px;">{h_dk:.1f}</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #333; padding: 8px; text-align: right;">المواظبة</td>
                        <td style="border: 1px solid #333; padding: 8px;">{w_mw}</td>
                        <td style="border: 1px solid #333; padding: 8px;">{mw}</td>
                        <td style="border: 1px solid #333; padding: 8px;">{h_mw:.1f}</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #333; padding: 8px; text-align: right;">تقييم المدرس</td>
                        <td style="border: 1px solid #333; padding: 8px;">{w_tm}</td>
                        <td style="border: 1px solid #333; padding: 8px;">{tm}</td>
                        <td style="border: 1px solid #333; padding: 8px;">{h_tm:.1f}</td>
                    </tr>
                    <tr style="background-color: #fdfdfd;">
                        <td style="border: 1px solid #333; padding: 8px; text-align: right; font-weight: bold;">الجمع</td>
                        <td style="border: 1px solid #333; padding: 8px;">-</td>
                        <td style="border: 1px solid #333; padding: 8px;">-</td>
                        <td style="border: 1px solid #333; padding: 8px; font-weight: bold;">{h_dk + h_mw + h_tm:.1f}</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #333; padding: 8px; text-align: right;">الحفظ</td>
                        <td style="border: 1px solid #333; padding: 8px;">{w_hf}</td>
                        <td style="border: 1px solid #333; padding: 8px;">{hf}</td>
                        <td style="border: 1px solid #333; padding: 8px;">{h_hf:.1f}</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #333; padding: 8px; text-align: right;">دراية شفويا</td>
                        <td style="border: 1px solid #333; padding: 8px;">{w_ds}</td>
                        <td style="border: 1px solid #333; padding: 8px;">{ds}</td>
                        <td style="border: 1px solid #333; padding: 8px;">{h_ds:.1f}</td>
                    </tr>
                    <tr style="background-color: #f8f9fa; font-weight: bold;">
                        <td style="border: 1px solid #333; padding: 8px; text-align: right;">المجموع</td>
                        <td style="border: 1px solid #333; padding: 8px;">{total_weights}</td>
                        <td style="border: 1px solid #333; padding: 8px;">-</td>
                        <td style="border: 1px solid #333; padding: 8px;">{total_scores:.1f}</td>
                    </tr>
                </tbody>
            </table>

            <table style="width: 100%; border: none; margin-bottom: 20px;">
                <tr>
                    <td style="width: 48%; vertical-align: top;">
                        <table style="width: 100%; border-collapse: collapse; text-align: center;">
                            <tr>
                                <td style="border: 1px solid #333; padding: 8px; font-size: 13px; background-color: #f8f9fa;">المعدل /20</td>
                            </tr>
                            <tr>
                                <td style="border: 1px solid #333; padding: 18px; font-size: 22px; font-weight: bold;">{current_avg:.2f}</td>
                            </tr>
                        </table>
                    </td>
                    <td style="width: 4%;"></td>
                    <td style="width: 48%; vertical-align: top;">
                        <table style="width: 100%; border-collapse: collapse; text-align: center;">
                            <tr>
                                <td style="border: 1px solid #333; padding: 8px; font-size: 13px; background-color: #f8f9fa;">المعدل العام /20</td>
                            </tr>
                            <tr>
                                <td style="border: 1px solid #333; padding: 18px; font-size: 22px; font-weight: bold;">{current_avg:.2f}</td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>

            <table style="width: 100%; border-collapse: collapse; text-align: right; font-size: 15px;">
                <tr>
                    <td style="border: 1px solid #333; padding: 12px;">
                        <b>النتيجة:</b> &nbsp; {result_status} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>الملاحظة:</b> &nbsp; {note}
                    </td>
                </tr>
            </table>

        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
        st.info("💡 يمكنك الضغط على زر الطباعة في متصفحك (Ctrl + P) لطباعة هذه البطاقة مباشرة.")

elif choice == "تغيير الضوارب":
    st.subheader("⚙️ تعديل ضوارب الاختبارات")
    conn = get_db_connection()
    w = pd.read_sql_query("SELECT * FROM settings WHERE id=1", conn).iloc[0]
    with st.form("weights_form"):
        w_dk = st.number_input("ضارب دراية كتابيا", value=float(w['w_diraya_kitabya']))
        w_mw = st.number_input("ضارب المواظبة", value=float(w['w_mowadaba']))
        w_tm = st.number_input("ضارب تقييم المدرس", value=float(w['w_taqeem_mudarris']))
        w_hf = st.number_input("ضارب الحفظ", value=float(w['w_hifz_item']))
        w_ds = st.number_input("ضارب دراية شفويا", value=float(w['w_diraya_shafowya']))
        
        if st.form_submit_button("حفظ الضوارب"):
            conn.execute("UPDATE settings SET w_diraya_kitabya=?, w_mowadaba=?, w_taqeem_mudarris=?, w_hifz_item=?, w_diraya_shafowya=? WHERE id=1", 
                         (w_dk, w_mw, w_tm, w_hf, w_ds))
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
    st.info("هذه لوحة التحكم الخاصة بالإعدادات العامة للبرنامج.")
    if st.button("التحقق من اتصال قاعدة البيانات"):
        conn = get_db_connection()
        st.success("✅ اتصال قاعدة البيانات يعمل بشكل سليم!")
        conn.close()
