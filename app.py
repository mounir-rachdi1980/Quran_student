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
        grade_row = df_grades[df_grades['المعرف'] == s_id].iloc[0] if not df_grades[df_grades['المعرف'] == s_id].empty else {}
        
        s_name = student.get('الاسم_الثلاثي', '')
        s_last = student.get('اللقب', '')
        num_tarsim = student.get('رقم_الترسيم', 'غير متوفر')
        morsam_b = student.get('المرسم_ب', 'غير متوفر')
        markaz = student.get('المركز', 'غير متوفر')
        
        dk = grade_row.get('diraya_kitabya', 0.0) if hasattr(grade_row, 'get') else 0.0
        mw = grade_row.get('mowadaba', 0.0) if hasattr(grade_row, 'get') else 0.0
        tm = grade_row.get('taqeem_mudarris', 0.0) if hasattr(grade_row, 'get') else 0.0
        hf = grade_row.get('hifz_d', 0.0) if hasattr(grade_row, 'get') else 0.0
        ds = grade_row.get('diraya_shafowya', 0.0) if hasattr(grade_row, 'get') else 0.0
        
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

        st.markdown("---")

        card_html = f"""
        <div style="direction: rtl; border: 2px solid #333; padding: 30px; border-radius: 5px; background-color: #ffffff; color: #000; font-family: Tahoma, sans-serif; max-width: 800px; margin: auto;">
            
            <table style="width: 100%; border: none; margin-bottom: 20px;">
                <tr>
                    <td style="width: 40%; text-align: right; vertical-align: top; font-size: 13px; line-height: 1.6;">
                        <b>الجمهورية التونسية</b><br>
                        الجمعية المحافظة على القرآن الكريم والأخلاق الفاضلة بصفاقس<br>
                        (القراءات)
                    </td>
                    <td style="width: 20%;"></td>
                    <td style="width: 40%; text-align: left; vertical-align: top; font-size: 13px; line-height: 1.6;">
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
        st.components.v1.html(card_html, height=750, scrolling=True)
        st.info("💡 يمكنك طباعة هذه البطاقة أو معاينتها بشكل كامل داخل الإطار أعلاه.")
