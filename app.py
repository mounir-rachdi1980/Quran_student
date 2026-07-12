def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # حذف الجداول القديمة تماماً لضمان عدم وجود تضارب في الأعمدة
    c.execute('DROP TABLE IF EXISTS students')
    c.execute('DROP TABLE IF EXISTS grades')
    
    # إنشاء الجداول من جديد بالهيكل الجديد المحدث (المواد الأربعة)
    c.execute('''CREATE TABLE students 
                 (المعرف INTEGER PRIMARY KEY AUTOINCREMENT, الاسم_الثلاثي TEXT, اللقب TEXT, 
                  تاريخ_الولادة TEXT, مكان_الولادة TEXT, المهنة TEXT, بطاقة_التعريف TEXT, 
                  المستوى_التعليمي TEXT, المرحلة TEXT, الوحدة INTEGER)''')
    
    c.execute('''CREATE TABLE grades 
                 (المعرف INTEGER PRIMARY KEY, hifz REAL, riwaya REAL, diraya REAL, hodoor REAL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS settings 
                 (id INTEGER PRIMARY KEY, w_hifz REAL, w_riwaya REAL, w_diraya REAL, w_hodoor REAL)''')
    
    c.execute("INSERT OR IGNORE INTO settings (id, w_hifz, w_riwaya, w_diraya, w_hodoor) VALUES (1, 3.0, 2.0, 2.0, 1.0)")
    
    conn.commit()
    conn.close()
