import sqlite3
import subprocess
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "school.db")

def generate_student_card():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get student info
    cursor.execute("""
        SELECT u.id, u.name, s.class_id, s.grade 
        FROM users u 
        JOIN students s ON u.id = s.id 
        WHERE u.id = 3
    """)
    student = cursor.fetchone()
    
    # Get attendance summary
    cursor.execute("SELECT status, COUNT(*) as count FROM attendance WHERE student_id = 3 GROUP BY status")
    attendance = {row["status"]: row["count"] for row in cursor.fetchall()}
    present = attendance.get("حاضر", 0)
    absent = attendance.get("غایب", 0)
    delay = attendance.get("تاخیر", 0)
    
    # Get grades (weekly marks)
    cursor.execute("SELECT subject, grade_val, date, description FROM grades WHERE student_id = 3")
    weekly_grades = cursor.fetchall()
    
    # Calculate average
    grades_sum = sum(row["grade_val"] for row in weekly_grades)
    grades_count = len(weekly_grades)
    avg_grade = round(grades_sum / grades_count, 2) if grades_count > 0 else 0
    
    # Get quiz attempts
    cursor.execute("""
        SELECT q.title, qa.score, qa.date 
        FROM quiz_attempts qa 
        JOIN quizzes q ON qa.quiz_id = q.id 
        WHERE qa.student_id = 3
    """)
    quizzes = cursor.fetchall()
    
    # Get submissions
    cursor.execute("SELECT assignment_title, file_path, score, feedback, date FROM submissions WHERE student_id = 3")
    submissions = cursor.fetchall()
    
    # Get announcements
    cursor.execute("SELECT title, text, date FROM announcements WHERE target IN ('all', 'students')")
    announcements = cursor.fetchall()
    
    # Get calendar events
    cursor.execute("SELECT title, date, type FROM events WHERE grade = 9")
    events = cursor.fetchall()
    
    conn.close()
    
    # Generate HTML
    html_content = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<style>
    body {{
        font-family: 'Noto Sans Arabic', 'DejaVu Sans', sans-serif;
        direction: rtl;
        text-align: right;
        background-color: #ffffff;
        color: #1F2937;
        margin: 0;
        padding: 40px;
        line-height: 1.6;
    }}
    .header {{
        border-bottom: 3px double #1E3A8A;
        padding-bottom: 15px;
        margin-bottom: 25px;
        text-align: center;
    }}
    .school-title {{
        font-size: 24px;
        font-weight: bold;
        color: #1E3A8A;
        margin: 0;
    }}
    .report-title {{
        font-size: 18px;
        color: #D97706;
        margin: 10px 0 0 0;
        font-weight: bold;
    }}
    .meta-grid {{
        display: table;
        width: 100%;
        margin-bottom: 25px;
        border: 1px solid #E5E7EB;
        background-color: #F9FAFB;
        border-collapse: collapse;
    }}
    .meta-row {{
        display: table-row;
    }}
    .meta-cell {{
        display: table-cell;
        padding: 10px 15px;
        border: 1px solid #E5E7EB;
        font-size: 13px;
        width: 33.33%;
    }}
    .meta-label {{
        font-weight: bold;
        color: #4B5563;
    }}
    .rank-section {{
        display: table;
        width: 100%;
        margin-bottom: 25px;
        border-spacing: 10px 0;
    }}
    .rank-card {{
        display: table-cell;
        width: 33.33%;
        background-color: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
        vertical-align: middle;
    }}
    .rank-card.highlight {{
        background-color: #FEF3C7;
        border-color: #FCD34D;
    }}
    .rank-title {{
        font-size: 13px;
        color: #4B5563;
    }}
    .rank-val {{
        font-size: 24px;
        font-weight: bold;
        color: #1E3A8A;
        margin-top: 5px;
    }}
    .rank-card.highlight .rank-val {{
        color: #B45309;
    }}
    .section-title {{
        font-size: 15px;
        font-weight: bold;
        color: #1E3A8A;
        border-right: 4px solid #D97706;
        padding-right: 10px;
        margin: 25px 0 12px 0;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 20px;
        font-size: 13px;
    }}
    th, td {{
        border: 1px solid #D1D5DB;
        padding: 8px 10px;
        text-align: center;
        vertical-align: middle;
    }}
    th {{
        background-color: #1E3A8A;
        color: white;
        font-weight: bold;
    }}
    tr:nth-child(even) {{
        background-color: #F9FAFB;
    }}
    .attendance-table {{
        display: table;
        width: 100%;
        margin-bottom: 20px;
        border-spacing: 10px 0;
    }}
    .attendance-card {{
        display: table-cell;
        width: 33.33%;
        background-color: #F3F4F6;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
    }}
    .att-title {{
        font-size: 13px;
        color: #4B5563;
    }}
    .att-val {{
        font-size: 20px;
        font-weight: bold;
        margin-top: 5px;
    }}
    .att-present {{ color: #10B981; }}
    .att-absent {{ color: #EF4444; }}
    .att-delay {{ color: #F59E0B; }}
    .feedback-box {{
        background-color: #FDF2F8;
        border: 1px dashed #FBCFE8;
        border-radius: 6px;
        padding: 15px;
        font-size: 13px;
        color: #DB2777;
        margin-top: 20px;
    }}
    .signature-section {{
        margin-top: 40px;
        display: table;
        width: 100%;
    }}
    .signature-column {{
        display: table-cell;
        width: 50%;
        text-align: center;
        font-size: 13px;
        font-weight: bold;
        color: #374151;
    }}
    .footer-note {{
        text-align: center;
        margin-top: 35px;
        font-size: 11px;
        color: #9CA3AF;
        border-top: 1px solid #E5E7EB;
        padding-top: 10px;
    }}
</style>
</head>
<body>

<div class="header">
    <div class="school-title">آموزشگاه شهید مفتح شهرستان جاسک</div>
    <div class="report-title">کارنامه تحصیلی مستمر ماهانه (درس ریاضی)</div>
</div>

<div class="meta-grid">
    <div class="meta-row">
        <div class="meta-cell"><span class="meta-label">نام و نام‌خانوادگی:</span> {student["name"]}</div>
        <div class="meta-cell"><span class="meta-label">پایه تحصیلی:</span> کلاس {student["class_id"]} (پایه {student["grade"]}م)</div>
        <div class="meta-cell"><span class="meta-label">ماه تحصیلی:</span> مهر ماه 1405</div>
    </div>
    <div class="meta-row">
        <div class="meta-cell"><span class="meta-label">نام دبیر:</span> رستم سوری نسب</div>
        <div class="meta-cell"><span class="meta-label">معدل مستمر ماه:</span> {avg_grade} از ۲۰</div>
        <div class="meta-cell"><span class="meta-label">کارت‌های تشویقی:</span> 1 کارت طلایی ⭐</div>
    </div>
</div>

<div class="section-title">وضعیت رتبه‌بندی تحصیلی در مدرسه</div>
<div class="rank-section">
    <div class="rank-card">
        <div class="rank-title">رتبه در کلاس</div>
        <div class="rank-val">2</div>
    </div>
    <div class="rank-card highlight">
        <div class="rank-title">رتبه در پایه ({student["grade"]}م)</div>
        <div class="rank-val">2</div>
    </div>
    <div class="rank-card">
        <div class="rank-title">رتبه در کل مدرسه</div>
        <div class="rank-val">5</div>
    </div>
</div>

<div class="section-title">نمرات مستمر هفتگی (در طول ماه)</div>
<table>
    <thead>
        <tr>
            <th width="30%">عنوان مستمر هفتگی</th>
            <th width="50%">موضوع ارزیابی</th>
            <th width="20%">نمره کسب شده (از ۲۰)</th>
        </tr>
    </thead>
    <tbody>
"""
    for idx, row in enumerate(weekly_grades):
        weeks = ["اول", "دوم", "سوم", "چهارم"]
        week_str = f"هفته {weeks[idx]}" if idx < len(weeks) else "ارزیابی کلاسی"
        html_content += f"""
        <tr>
            <td>{week_str}</td>
            <td>{row["description"]}</td>
            <td style="font-weight: bold; color: #1E3A8A;">{row["grade_val"]}</td>
        </tr>
"""
        
    html_content += """
    </tbody>
</table>

<div class="section-title">آزمون‌های آنلاین چهارگزینه‌ای</div>
<table>
    <thead>
        <tr>
            <th width="40%">عنوان آزمون آنلاین</th>
            <th width="20%">تاریخ برگزاری</th>
            <th width="20%">نمره تستی (از ۲۰)</th>
            <th width="20%">وضعیت قبولی</th>
        </tr>
    </thead>
    <tbody>
"""
    for row in quizzes:
        status_quiz = "عالی" if row["score"] >= 18 else "خوب" if row["score"] >= 14 else "نیاز به تلاش"
        html_content += f"""
        <tr>
            <td>{row["title"]}</td>
            <td>{row["date"]}</td>
            <td style="font-weight: bold; color: #10B981;">{row["score"]}</td>
            <td style="font-weight: bold; color: #10B981;">{status_quiz}</td>
        </tr>
"""
    if not quizzes:
        html_content += """<tr><td colspan="4">هیچ آزمون آنلاینی ثبت نشده است.</td></tr>"""

    html_content += """
    </tbody>
</table>

<div class="section-title">کاربرگ‌ها و تکالیف مکتوب تحویلی</div>
<table>
    <thead>
        <tr>
            <th width="30%">عنوان تکلیف</th>
            <th width="15%">تاریخ تحویل</th>
            <th width="15%">نمره مکتوب</th>
            <th width="40%">بازخورد دبیر ریاضی</th>
        </tr>
    </thead>
    <tbody>
"""
    for row in submissions:
        html_content += f"""
        <tr>
            <td>{row["assignment_title"]}</td>
            <td>{row["date"]}</td>
            <td style="font-weight: bold; color: #1E3A8A;">{row["score"]}</td>
            <td style="text-align: right; font-style: italic;">{row["feedback"]}</td>
        </tr>
"""
    if not submissions:
        html_content += """<tr><td colspan="4">هیچ تکلیفی تحویل داده نشده است.</td></tr>"""

    html_content += f"""
    </tbody>
</table>

<div class="section-title">خلاصه وضعیت حضور و غیاب</div>
<div class="attendance-table">
    <div class="attendance-card">
        <div class="att-title">تعداد جلسات حضور</div>
        <div class="att-val att-present">{present} جلسه</div>
    </div>
    <div class="attendance-card">
        <div class="att-title">تعداد غیبت‌های غیرموجه</div>
        <div class="att-val att-absent">{absent} جلسه</div>
    </div>
    <div class="attendance-card">
        <div class="att-title">تعداد تاخیر ورود</div>
        <div class="att-val att-delay">{delay} جلسه</div>
    </div>
</div>

<div class="section-title">تقویم آموزشی و برنامه امتحانات پیش‌رو</div>
<table>
    <thead>
        <tr>
            <th width="40%">عنوان رویداد / امتحان</th>
            <th width="30%">تاریخ برگزاری</th>
            <th width="30%">نوع رویداد</th>
        </tr>
    </thead>
    <tbody>
"""
    for row in events:
        type_str = "امتحان کلاسی 📝" if row["type"] == "exam" else "رویداد کلاسی 🏫"
        html_content += f"""
        <tr>
            <td>{row["title"]}</td>
            <td>{row["date"]}</td>
            <td>{type_str}</td>
        </tr>
"""
    if not events:
        html_content += """<tr><td colspan="3">هیچ برنامه ثبت‌شده‌ای وجود ندارد.</td></tr>"""

    html_content += """
    </tbody>
</table>

<div class="feedback-box">
    💡 <strong>توصیه تحصیلی دبیر (آقای سوری نسب):</strong> با توجه به استعداد بسیار خوب دانش‌آموز در بخش جبر و توان، شایسته است تمرین‌های تکمیلی ریاضی نهم را با تمرکز بیشتری پیگیری کرده و در آزمون‌های تستی دوره‌ای شرکت فعال داشته باشد.
</div>

<div class="signature-section">
    <div class="signature-column">امضا و مهر مدیر آموزشگاه:<br><br><span style="color:#9CA3AF; font-size:12px;">علی احمدی</span></div>
    <div class="signature-column">امضا و مهر دبیر ریاضی:<br><br><span style="color:#9CA3AF; font-size:12px;">رستم سوری نسب</span></div>
</div>

<div class="footer-note">
    سامانه هوشمند ارتباطی پُل (دبیرستان شهید مفتح جاسک) - طراحی شده بر اساس جدیدترین متدهای آموزشی
</div>

</body>
</html>
"""
    
    # Write to HTML in scratch and build PDF
    html_path = os.path.join(os.path.dirname(__file__), "student-card.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    pdf_path = os.path.join(os.path.dirname(__file__), "student-report-card-sample.pdf")
    subprocess.run(["wkhtmltopdf", "--page-size", "A4", "--margin-top", "15", "--margin-bottom", "15", html_path, pdf_path])

def generate_rankings_card():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Calculate GPAs of all students and ranks
    cursor.execute("""
        SELECT u.id, u.name, s.class_id, s.grade, AVG(g.grade_val) as avg_gpa
        FROM users u
        JOIN students s ON u.id = s.id
        LEFT JOIN grades g ON u.id = g.student_id
        GROUP BY u.id
        ORDER BY avg_gpa DESC
    """)
    students_list = cursor.fetchall()
    conn.close()
    
    html_content = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<style>
    body {
        font-family: 'Noto Sans Arabic', 'DejaVu Sans', sans-serif;
        direction: rtl;
        text-align: right;
        background-color: #ffffff;
        color: #1F2937;
        margin: 0;
        padding: 40px;
        line-height: 1.6;
    }
    .header {
        border-bottom: 3px double #1E3A8A;
        padding-bottom: 15px;
        margin-bottom: 25px;
        text-align: center;
    }
    .school-title {
        font-size: 24px;
        font-weight: bold;
        color: #1E3A8A;
        margin: 0;
    }
    .report-title {
        font-size: 18px;
        color: #D97706;
        margin: 10px 0 0 0;
        font-weight: bold;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 20px;
        font-size: 13px;
    }
    th, td {
        border: 1px solid #D1D5DB;
        padding: 10px 12px;
        text-align: center;
        vertical-align: middle;
    }
    th {
        background-color: #1E3A8A;
        color: white;
        font-weight: bold;
    }
    tr:nth-child(even) {
        background-color: #F9FAFB;
    }
    .gold { background-color: #FEF3C7 !important; font-weight: bold; }
    .silver { background-color: #F3F4F6 !important; font-weight: bold; }
    .bronze { background-color: #EFF6FF !important; font-weight: bold; }
    .medal { font-size: 16px; margin-right: 5px; }
</style>
</head>
<body>

<div class="header">
    <div class="school-title">آموزشگاه شهید مفتح شهرستان جاسک</div>
    <div class="report-title">جدول رتبه‌بندی عمومی دانش‌آموزان بر اساس نمرات مستمر (مهر ماه)</div>
</div>

<table>
    <thead>
        <tr>
            <th width="10%">رتبه کل</th>
            <th width="30%">نام و نام‌خانوادگی</th>
            <th width="20%">کلاس تحصیلی</th>
            <th width="20%">پایه تحصیلی</th>
            <th width="20%">معدل مستمر (از ۲۰)</th>
        </tr>
    </thead>
    <tbody>
"""
    for rank, row in enumerate(students_list, 1):
        gpa_val = round(row["avg_gpa"], 2) if row["avg_gpa"] else 0.0
        class_str = f"کلاس {row['class_id']}" if row['class_id'] else "نامشخص"
        grade_str = f"پایه {row['grade']}م" if row['grade'] else "نامشخص"
        
        # Style rows for top 3
        row_class = ""
        medal = ""
        if rank == 1:
            row_class = 'class="gold"'
            medal = '<span class="medal">🥇</span>'
        elif rank == 2:
            row_class = 'class="silver"'
            medal = '<span class="medal">🥈</span>'
        elif rank == 3:
            row_class = 'class="bronze"'
            medal = '<span class="medal">🥉</span>'
            
        html_content += f"""
        <tr {row_class}>
            <td>{rank}</td>
            <td>{row["name"]} {medal}</td>
            <td>{class_str}</td>
            <td>{grade_str}</td>
            <td style="font-weight: bold;">{gpa_val}</td>
        </tr>
"""
        
    html_content += """
    </tbody>
</table>

</body>
</html>
"""
    
    html_path = os.path.join(os.path.dirname(__file__), "school-rankings.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    pdf_path = os.path.join(os.path.dirname(__file__), "school-rankings-sample.pdf")
    subprocess.run(["wkhtmltopdf", "--page-size", "A4", "--margin-top", "15", "--margin-bottom", "15", html_path, pdf_path])

if __name__ == "__main__":
    generate_student_card()
    generate_rankings_card()
    print("Generated student report PDF and school rankings PDF successfully!")
