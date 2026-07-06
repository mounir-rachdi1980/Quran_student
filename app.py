import streamlit as st
import pandas as pd
import os

# --- إعدادات الواجهة ---
st.set_page_config(page_title="نظام الفرع المحلي للرابطة الوطنية للقرآن الكريم بالمكناسي", layout="wide", page_icon="🕌")

# --- دالة تحميل وحفظ البيانات ---
def load_data(filename, columns):
    if not os.path.exists(filename):
        df = pd.DataFrame(columns=columns)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
    return pd.read_csv(filename)

def save_data(df, filename):
    df.to_csv(filename, index=False, encoding='utf-8-sig')

# --- تهيئة البيانات ---
if 'students_db' not in st.session_state:
    st.session_state.students_db = load_data('students.csv', ['المعرف', 'الاسم الثلاثي', 'اللقب', 'تاريخ الولادة', 'بطاقة التعريف', 'المهنة'])
if 'grades_db' not in st.session_state:
    st.session_state.grades_db = load_data('grades.csv', ['المعرف', 'الحفظ', 'الرواية', 'الدراية', 'الحضور'])
if 'weights' not in st.session_state:
    st.session_state.weights = {'الحفظ': 3.0, 'الرواية': 2.0, 'الدراية': 2.0, 'الحضور': 1.0}

w = st.session_state.weights

# --- التنسيق (CSS) ---
st.markdown("""
    <style>
    [data-testid="stSidebar"], .main { direction: rtl; text-align: right; }
    th, td, .stMarkdown { text-align: right !important; }
    </style>
""", unsafe_allow_html=True)

# --- واجهة التطبيق ---
st.title("🕌 نظام الفرع المحلي للرابطة الوطنية للقرآن الكريم بالمكناسي")

menu = ["تسجيل طالب جديد", "رصد وتعديل الدرجات", "استخراج بطاقة الأعداد"]
choice = st.sidebar.selectbox("قائمة التحكم", menu)

# --- تسجيل طالب ---
if choice == "تسجيل طالب جديد":
    with st.form("student_form", clear_on_submit=True):
        name = st.text_input("الاسم الثلاثي")
        last_name = st.text_input("اللقب")
        cin = st.text_input("رقم بطاقة التعريف")
        dob = st.date_input("تاريخ الولادة")
        job = st.text_input("المهنة")
        if st.form_submit_button("حفظ الطالب"):
            next_id = 20260001 + len(st.session_state.students_db)
            new_s = pd.DataFrame([{'المعرف': next_id, 'الاسم الثلاثي': name, 'اللقب': last_name, 'تاريخ الولادة': str(dob), 'بطاقة التعريف': cin, 'المهنة': job}])
            st.session_state.students_db = pd.concat([st.session_state.students_db, new_s], ignore_index=True)
            save_data(st.session_state.students_db, 'students.csv')
            
            new_g = pd.DataFrame([{'المعرف': next_id, 'الحفظ': 0.0, 'الرواية': 0.0, 'الدراية': 0.0, 'الحضور': 0.0}])
            st.session_state.grades_db = pd.concat([st.session_state.grades_db, new_g], ignore_index=True)
            save_data(st.session_state.grades_db, 'grades.csv')
            st.success(f"تم التسجيل! المعرف: {next_id}")

    st.dataframe(st.session_state.students_db)

# --- رصد الدرجات ---
elif choice == "رصد وتعديل الدرجات":
    if not st.session_state.students_db.empty:
        s_id = st.selectbox("اختر الطالب", st.session_state.students_db['المعرف'])
        g_row = st.session_state.grades_db[st.session_state.grades_db['المعرف'] == s_id].iloc[0]
        
        h = st.number_input("الحفظ", value=float(g_row['الحفظ']))
        r = st.number_input("الرواية", value=float(g_row['الرواية']))
        d = st.number_input("الدراية", value=float(g_row['الدراية']))
        a = st.number_input("الحضور", value=float(g_row['الحضور']))
        
        if st.button("حفظ الدرجات"):
            st.session_state.grades_db.loc[st.session_state.grades_db['المعرف'] == s_id, ['الحفظ', 'الرواية', 'الدراية', 'الحضور']] = [h, r, d, a]
            save_data(st.session_state.grades_db, 'grades.csv')
            st.success("تم تحديث الدرجات!")