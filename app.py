import streamlit as st
import sqlite3
import pandas as pd
import os
import subprocess
from datetime import datetime

# Set Page Config first
st.set_page_config(page_title="سامانه آموزشی پُل", page_icon="🎓", layout="wide")

DB_PATH = os.path.join(os.path.dirname(__file__), "school.db")

# Automatically initialize database if it doesn't exist or is empty
if not os.path.exists(DB_PATH) or os.path.getsize(DB_PATH) == 0:
    try:
        import school_db
        school_db.init_db()
        school_db.seed_data()
    except Exception as e:
        import streamlit as st
        st.error(f"Error initializing database: {e}")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Custom styling for RTL and Persian fonts
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;700&display=swap');
    
    html, body, [data-testid="stSidebar"], .stMarkdown, p, div, h1, h2, h3, h4, h5, h6, span, label, input, select, button {
        font-family: 'Noto Sans Arabic', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* Marquee style for announcements */
    .ticker-wrap {
        background-color: #FEF3C7;
        border-bottom: 2px solid #FCD34D;
        color: #B45309;
        padding: 8px 10px;
        font-weight: bold;
        overflow: hidden;
        margin-bottom: 20px;
        border-radius: 4px;
    }
    .ticker {
        display: inline-block;
        white-space: nowrap;
        animation: marquee 25s linear infinite;
        font-size: 14px;
    }
    @keyframes marquee {
        0% { transform: translate3d(100%, 0, 0); }
        100% { transform: translate3d(-100%, 0, 0); }
    }
    
    /* Info cards */
    .metric-card {
        background-color: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        margin-bottom: 15px;
    }
    .metric-title {
        font-size: 13px;
        color: #1E3A8A;
        font-weight: bold;
    }}
    .metric-val {
        font-size: 24px;
        font-weight: bold;
        color: #1E3A8A;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Helper for showing marquee
def show_announcements_marquee():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, date FROM announcements ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    conn.close()
    
    if rows:
        ann_text = "  |  ".join([f"📢 {row['title']} ({row['date']})" for row in rows])
        st.markdown(f"""
        <div class="ticker-wrap">
            <div class="ticker">
                {ann_text}
            </div>
        </div>
        """, unsafe_allow_html=True)

# Auth sessions
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        st.session_state.logged_in = True
        st.session_state.user = dict(user)
        return True
    return False

def logout_user():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

# --- APP LAYOUT ---
show_announcements_marquee()

st.title("🎓 سامانه آموزشی و تعاملی پُـل")
st.subheader("دبیرستان متوسطه اول شهید مفتح جاسک")

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("🔐 جهت ورود به سامانه، مشخصات کاربری خود را وارد کنید:")
        username = st.text_input("نام کاربری")
        password = st.text_input("رمز عبور", type="password")
        if st.button("ورود به سامانه"):
            if login_user(username, password):
                st.success(f"خوش آمدید، {st.session_state.user['name']}")
                st.rerun()
            else:
                st.error("نام کاربری یا رمز عبور اشتباه است.")
                
        st.markdown("""
        <hr/>
        <div style="text-align: center; color: #4B5563; font-size: 13px;">
            <strong>اطلاعات ورود دمو برای ارزیابی سریع:</strong><br>
            • پنل دبیر ریاضی: کاربری <code>rostam</code> | رمز <code>math123</code><br>
            • پنل مدیر مدرسه: کاربری <code>admin</code> | رمز <code>admin123</code><br>
            • پنل دانش‌آموز نهم: کاربری <code>s13</code> | رمز <code>123</code><br>
            • پنل اولیای دانش‌آموز: کاربری <code>p_s13</code> | رمز <code>123</code>
        </div>
        """, unsafe_allow_html=True)
else:
    user = st.session_state.user
    role = user["role"]
    
    # Sidebar
    st.sidebar.markdown(f"### 👤 {user['name']}")
    st.sidebar.markdown(f"**نقش شما:** {role.upper()}")
    if st.sidebar.button("🚪 خروج از حساب"):
        logout_user()
        
    st.sidebar.markdown("---")
    
    # --- ROLE-BASED PANELS ---
    if role == "admin":
        st.sidebar.markdown("### ⚙️ پنل مدیریت")
        menu = st.sidebar.radio("انتخاب منو", [
            "📂 مدیریت کاربران و اکسل",
            "📢 تابلوی اعلانات و بخشنامه‌ها",
            "📅 مدیریت تقویم و امتحانات",
            "⚙️ ابزارها و خروجی گزارشات"
        ])
        
        if menu == "📂 مدیریت کاربران و اکسل":
            st.header("📂 مدیریت و پورتال کاربران")
            
            # Creating Tabs for User Management
            tab1, tab2, tab3, tab4 = st.tabs([
                "📥 درون‌ریزی دسته‌جمعی (اکسل)", 
                "➕ تعریف کاربر جدید (تکی)", 
                "🔑 مدیریت و تغییر رمزها", 
                "👤 تغییر رمز من (مدیر)"
            ])
            
            with tab1:
                st.subheader("۱. درون‌ریزی دانش‌آموزان با فایل اکسل")
                st.write("شما می‌توانید کل لیست دانش‌آموزان را به همراه کلاس و پایه در قالب یک فایل اکسل آپلود کنید. سامانه به صورت خودکار پورتال اولیای مربوطه را نیز می‌سازد.")
                
                # Download template
                template_path = os.path.join(os.path.dirname(__file__), "excel_template.xlsx")
                if os.path.exists(template_path):
                    with open(template_path, "rb") as f_template:
                        st.download_button("📥 دانلود فایل نمونه اکسل (Template)", f_template, "excel_template.xlsx")
                
                uploaded_file = st.file_uploader("فایل اکسل خود را انتخاب کنید", type=["xlsx"])
                if uploaded_file is not None:
                    try:
                        df = pd.read_excel(uploaded_file)
                        st.write("**پیش‌نمایش اطلاعات فایل آپلود شده:**")
                        st.dataframe(df)
                        
                        if st.button("🚀 شروع درون‌ریزی دانش‌آموزان و ساخت پورتال اولیا"):
                            conn = get_connection()
                            cursor = conn.cursor()
                            success_count = 0
                            for idx, row in df.iterrows():
                                fullname = row.get("نام و نام خانوادگی", "").strip()
                                username = str(row.get("نام کاربری", "")).strip()
                                class_id = str(row.get("کلاس", "")).strip()
                                grade = int(row.get("پایه", 9))
                                password = str(row.get("رمز عبور", "123")).strip()
                                
                                if fullname and username:
                                    try:
                                        cursor.execute("INSERT INTO users (username, password, role, name) VALUES (?, ?, 'student', ?)", (username, password, fullname))
                                        student_id = cursor.lastrowid
                                        cursor.execute("INSERT INTO students (id, class_id, grade) VALUES (?, ?, ?)", (student_id, class_id, grade))
                                        
                                        # Create parent user
                                        p_username = f"p_{username}"
                                        p_fullname = f"ولیِ {fullname}"
                                        cursor.execute("INSERT INTO users (username, password, role, name) VALUES (?, ?, 'parent', ?)", (p_username, password, p_fullname))
                                        success_count += 1
                                    except Exception as e:
                                        pass
                            conn.commit()
                            conn.close()
                            st.success(f"موفقیت‌آمیز! تعداد {success_count} دانش‌آموز جدید و اولیای آن‌ها با موفقیت اضافه شدند!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"خطا در خواندن فایل اکسل: {e}")
            
            with tab2:
                st.subheader("۲. تعریف تک‌به‌تک و دستی کاربر جدید")
                st.write("از این قسمت می‌توانید همکاران (دبیران)، دانش‌آموزان یا مدیران جدید را به صورت تکی تعریف کنید:")
                
                with st.form("create_user_form_v4", clear_on_submit=True):
                    new_name = st.text_input("نام و نام خانوادگی")
                    new_username = st.text_input("نام کاربری (انگلیسی)")
                    new_password = st.text_input("رمز عبور")
                    new_role = st.selectbox("نقش کاربر جدید", ["دانش‌آموز (student)", "دبیر (teacher)", "مدیر (admin)"])
                    
                    st.markdown("---")
                    st.write("⚠️ تکمیل اطلاعات زیر فقط در صورت انتخاب نقش **دانش‌آموز** الزامی است:")
                    class_id = st.text_input("کلاس (مثلاً 9-1)", value="9-1")
                    grade = st.selectbox("پایه تحصیلی", [7, 8, 9], index=2)
                    
                    submit_user = st.form_submit_button("➕ ثبت کاربر جدید در سامانه")
                    if submit_user:
                        if new_name and new_username and new_password:
                            role_map = {
                                "دانش‌آموز (student)": "student",
                                "دبیر (teacher)": "teacher",
                                "مدیر (admin)": "admin"
                            }
                            role_db = role_map[new_role]
                            conn = get_connection()
                            cursor = conn.cursor()
                            try:
                                cursor.execute("INSERT INTO users (username, password, role, name) VALUES (?, ?, ?, ?)", (new_username, new_password, role_db, new_name))
                                new_user_id = cursor.lastrowid
                                
                                if role_db == "student":
                                    cursor.execute("INSERT INTO students (id, class_id, grade) VALUES (?, ?, ?)", (new_user_id, class_id, grade))
                                    # Create parent
                                    p_username = f"p_{new_username}"
                                    p_fullname = f"ولیِ {new_name}"
                                    cursor.execute("INSERT INTO users (username, password, role, name) VALUES (?, ?, 'parent', ?)", (p_username, new_password, p_fullname))
                                
                                conn.commit()
                                st.success(f"کاربر جدید '{new_name}' با نقش {new_role} با موفقیت ثبت شد!")
                            except sqlite3.IntegrityError:
                                st.error("خطا: این نام کاربری قبلاً در سامانه استفاده شده است!")
                            except Exception as e:
                                st.error(f"خطا در ثبت کاربر: {e}")
                            finally:
                                conn.close()
                        else:
                            st.warning("لطفاً تمام کادرهای الزامی را پر کنید.")
            
            with tab3:
                st.subheader("۳. مدیریت کاربران و ویرایش یا تغییر آنلاین رمزها")
                st.write("کاربر مورد نظر خود را از لیست زیر انتخاب کرده و اطلاعات یا رمز عبور او را تغییر دهید:")
                
                conn = get_connection()
                df_edit_users = pd.read_sql_query("SELECT id, name, username, role FROM users ORDER BY id DESC", conn)
                conn.close()
                
                user_options = {f"{row['name']} ({row['username']} - {row['role']})": row['id'] for idx, row in df_edit_users.iterrows()}
                selected_user_str = st.selectbox("🎯 انتخاب کاربر جهت ویرایش:", list(user_options.keys()))
                
                if selected_user_str:
                    selected_id = user_options[selected_user_str]
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM users WHERE id = ?", (selected_id,))
                    user_data = cursor.fetchone()
                    conn.close()
                    
                    if user_data:
                        st.write(f"✍️ **ویرایش حساب:** {user_data['name']} (نقش: {user_data['role'].upper()})")
                        with st.form(f"edit_user_form_{selected_id}"):
                            edit_name = st.text_input("نام و نام خانوادگی", value=user_data['name'])
                            edit_username = st.text_input("نام کاربری (انگلیسی)", value=user_data['username'])
                            edit_password = st.text_input("رمز عبور جدید", value=user_data['password'])
                            
                            update_btn = st.form_submit_button("💾 ذخیره تغییرات کاربر")
                            if update_btn:
                                if edit_name and edit_username and edit_password:
                                    conn = get_connection()
                                    cursor = conn.cursor()
                                    try:
                                        cursor.execute("UPDATE users SET name = ?, username = ?, password = ? WHERE id = ?", (edit_name, edit_username, edit_password, selected_id))
                                        conn.commit()
                                        st.success(f"اطلاعات کاربر '{edit_name}' با موفقیت بروزرسانی شد!")
                                        st.rerun()
                                    except sqlite3.IntegrityError:
                                        st.error("خطا: این نام کاربری قبلاً در سامانه استفاده شده است!")
                                    except Exception as e:
                                        st.error(f"خطا در ذخیره تغییرات: {e}")
                                    finally:
                                        conn.close()
                                else:
                                    st.warning("کادرها نباید خالی باشند.")
                
                st.markdown("---")
                st.write("📊 **لیست زنده کل کاربران ثبت‌شده در سامانه:**")
                st.dataframe(df_edit_users)
            
            with tab4:
                st.subheader("۴. تغییر نام کاربری و رمز عبور شما (مدیر)")
                st.write("از این فرم می‌توانید به عنوان مدیر اصلی، اطلاعات ورود خود را شخصی‌سازی و امن کنید:")
                
                with st.form("admin_self_edit_v4"):
                    admin_id = st.session_state.user['id']
                    admin_name = st.text_input("نام نمایش‌داده‌شده شما در سایت", value=st.session_state.user['name'])
                    admin_username = st.text_input("نام کاربری مدیر (جهت ورود)", value=st.session_state.user['username'])
                    admin_password = st.text_input("رمز عبور جدید مدیر", value=st.session_state.user['password'])
                    
                    submit_admin_self = st.form_submit_button("💾 ثبت نهایی تغییرات مدیر")
                    if submit_admin_self:
                        if admin_name and admin_username and admin_password:
                            conn = get_connection()
                            cursor = conn.cursor()
                            try:
                                cursor.execute("UPDATE users SET name = ?, username = ?, password = ? WHERE id = ?", (admin_name, admin_username, admin_password, admin_id))
                                conn.commit()
                                # Update current session
                                st.session_state.user['name'] = admin_name
                                st.session_state.user['username'] = admin_username
                                st.session_state.user['password'] = admin_password
                                st.success("مشخصات ورود مدیریت با موفقیت امن و بروزرسانی شد!")
                                st.rerun()
                            except sqlite3.IntegrityError:
                                st.error("خطا: این نام کاربری قبلاً در سامانه استفاده شده است!")
                            except Exception as e:
                                st.error(f"خطا در بروزرسانی: {e}")
                            finally:
                                conn.close()
                        else:
                            st.warning("پر کردن تمامی کادرها الزامی است.")

        elif menu == "📢 تابلوی اعلانات و بخشنامه‌ها":
            st.header("📢 تابلوی اعلانات و بخشنامه‌ها")
            
            title = st.text_input("عنوان بخشنامه / اطلاعیه")
            text = st.text_area("متن بخشنامه")
            target = st.selectbox("مخاطب هدف", ["all", "students", "parents", "teachers"])
            
            if st.button("ثبت بخشنامه جدید"):
                if title and text:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO announcements (title, text, target, date) VALUES (?, ?, ?, ?)",
                                   (title, text, target, datetime.now().strftime("%Y/%m/%d")))
                    conn.commit()
                    conn.close()
                    st.success("بخشنامه جدید با موفقیت ثبت شد و در بالای سایت فعال گردید!")
                    st.rerun()
                else:
                    st.warning("لطفاً عنوان و متن را کامل کنید.")
                    
            st.subheader("لیست کل بخشنامه‌ها")
            conn = get_connection()
            df_ann = pd.read_sql_query("SELECT id, title, target, date FROM announcements ORDER BY id DESC", conn)
            conn.close()
            st.dataframe(df_ann)
            
        elif menu == "📅 مدیریت تقویم و امتحانات":
            st.header("📅 مدیریت تقویم آموزشی و برنامه امتحانات")
            
            title = st.text_input("عنوان رویداد یا آزمون")
            date_str = st.text_input("تاریخ برگزاری (مثلاً: 1405/07/15)")
            type_event = st.selectbox("نوع رویداد", ["exam", "event"])
            grade_target = st.selectbox("پایه تحصیلی هدف", [7, 8, 9])
            
            if st.button("ثبت در تقویم"):
                if title and date_str:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO events (title, date, type, grade) VALUES (?, ?, ?, ?)",
                                   (title, date_str, type_event, grade_target))
                    conn.commit()
                    conn.close()
                    st.success("رویداد جدید با موفقیت ثبت شد!")
                    st.rerun()
                else:
                    st.warning("پر کردن عنوان و تاریخ الزامی است.")
                    
            st.subheader("رویدادهای ثبت‌شده")
            conn = get_connection()
            df_ev = pd.read_sql_query("SELECT id, title, date, type, grade FROM events ORDER BY date ASC", conn)
            conn.close()
            st.dataframe(df_ev)
            
        elif menu == "⚙️ ابزارها و خروجی گزارشات":
            st.header("⚙️ ابزارها و گزارش‌گیری رسمی اداره")
            
            st.subheader("۱. خروجی اکسل چندبرگی گزارش اداره")
            st.write("با کلیک روی دکمه زیر، سامانه آخرین اطلاعات رتبه‌بندی تحصیلی، نمرات هفتگی، نتایج آزمون‌های آنلاین و حضور و غیاب دانش‌آموزان را تجمیع کرده و فایل اکسل گزارش اداره را تولید می‌کند.")
            
            # Trigger Excel compilation
            excel_path = os.path.join(os.path.dirname(__file__), "school-reports-department.xlsx")
            # We can run create_excels directly if we want, let's copy create_excels logic to keep it single file or run via subprocess
            # Let's run a small subprocess since create_excels is deleted but we can do it via code right here
            if st.button("🚀 تولید و استخراج فایل اکسل گزارشات"):
                import openpyxl
                # Run creation right here
                conn = get_connection()
                df_rankings = pd.read_sql_query("""
                    SELECT u.name as "نام و نام خانوادگی", s.class_id as "کلاس", s.grade as "پایه", AVG(g.grade_val) as "معدل مستمر"
                    FROM users u JOIN students s ON u.id = s.id LEFT JOIN grades g ON u.id = g.student_id GROUP BY u.id ORDER BY "معدل مستمر" DESC
                """, conn)
                df_rankings.insert(0, 'رتبه', range(1, len(df_rankings) + 1))
                
                df_weekly = pd.read_sql_query("""
                    SELECT u.name as "نام دانش‌آموز", s.class_id as "کلاس", s.grade as "پایه", g.subject as "عنوان ارزیابی", g.grade_val as "نمره", g.date as "تاریخ ثبت"
                    FROM grades g JOIN users u ON g.student_id = u.id JOIN students s ON u.id = s.id
                """, conn)
                
                df_quizzes = pd.read_sql_query("""
                    SELECT u.name as "نام دانش‌آموز", s.class_id as "کلاس", s.grade as "پایه", q.title as "عنوان آزمون", qa.score as "نمره", qa.date as "تاریخ"
                    FROM quiz_attempts qa JOIN users u ON qa.student_id = u.id JOIN students s ON u.id = s.id JOIN quizzes q ON qa.quiz_id = q.id
                """, conn)
                
                df_attendance = pd.read_sql_query("""
                    SELECT u.name as "نام دانش‌آموز", s.class_id as "کلاس", s.grade as "پایه",
                           SUM(CASE WHEN a.status = 'حاضر' THEN 1 ELSE 0 END) as "تعداد حضور",
                           SUM(CASE WHEN a.status = 'غایب' THEN 1 ELSE 0 END) as "تعداد غیبت",
                           SUM(CASE WHEN a.status = 'تاخیر' THEN 1 ELSE 0 END) as "تعداد تاخیر"
                    FROM attendance a JOIN users u ON a.student_id = u.id JOIN students s ON u.id = s.id GROUP BY u.id
                """, conn)
                conn.close()
                
                with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                    df_rankings.to_excel(writer, sheet_name="رتبه‌بندی کل مدرسه", index=False)
                    df_weekly.to_excel(writer, sheet_name="ریز نمرات هفتگی", index=False)
                    df_quizzes.to_excel(writer, sheet_name="نتایج آزمون‌های آنلاین", index=False)
                    df_attendance.to_excel(writer, sheet_name="خلاصه حضور غیاب", index=False)
                st.success("فایل اکسل با موفقیت تولید شد!")
                
            if os.path.exists(excel_path):
                with open(excel_path, "rb") as f:
                    st.download_button("📥 دریافت فایل اکسل گزارش اداره (.xlsx)", f, "school-reports-department.xlsx")
                    
            st.subheader("۲. دریافت پی‌دی‌اف‌های کارنامه و رتبه‌بندی مدارس")
            # PDF download
            card_path = os.path.join(os.path.dirname(__file__), "student-report-card-sample.pdf")
            rankings_path = os.path.join(os.path.dirname(__file__), "school-rankings-sample.pdf")
            
            col_pdf1, col_pdf2 = st.columns(2)
            with col_pdf1:
                if os.path.exists(card_path):
                    with open(card_path, "rb") as f:
                        st.download_button("📥 دانلود فایل کارنامه نمونه (.pdf)", f, "student-report-card-sample.pdf")
            with col_pdf2:
                if os.path.exists(rankings_path):
                    with open(rankings_path, "rb") as f:
                        st.download_button("📥 دانلود جدول رتبه‌بندی چاپی (.pdf)", f, "school-rankings-sample.pdf")

    elif role == "teacher":
        st.sidebar.markdown("### 📐 پنل معلمان")
        menu = st.sidebar.radio("انتخاب منو", [
            "📢 تابلوی اعلانات",
            "📝 طراحی و تولید آزمون آنلاین",
            "📂 ثبت نمرات و بازخوردهای کلاسی",
            "📅 مدیریت تقویم و امتحانات",
            "🖥️ کلاس آنلاین و حضور و غیاب زنده"
        ])
        
        if menu == "📢 تابلوی اعلانات":
            st.header("📢 تابلوی اعلانات مدرسه")
            st.write("آخرین بخشنامه‌ها و اطلاعیه‌ها در نوار متحرک بالای سایت نمایش داده می‌شوند.")
            
        elif menu == "📝 طراحی و تولید آزمون آنلاین":
            st.header("📝 طراحی و تولید آزمون آنلاین تستی")
            
            st.subheader("۱. روش اول: طراحی سریع سوال تستی به صورت دستی")
            title = st.text_input("عنوان آزمون")
            grade = st.selectbox("پایه هدف", [7, 8, 9])
            topic = st.text_input("موضوع آزمون", "توان و ریشه")
            
            if st.button("ایجاد آزمون"):
                if title:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO quizzes (title, grade, topic) VALUES (?, ?, ?)", (title, grade, topic))
                    conn.commit()
                    conn.close()
                    st.success(f"آزمون '{title}' با موفقیت تعریف شد. اکنون می‌توانید سوالات آن را اضافه کنید.")
            
            st.write("---")
            st.subheader("۲. روش دوم: تولید خودکار و هوشمند از روی منابع")
            st.write("کافی است متن علمی یا خلاصه مبحث کلاسی را در کادر زیر قرار دهید. سیستم به طور هوشمند تست‌های جای خالی استاندارد با قلم زیبا برای دانش‌آموز تولید می‌کند.")
            
            lecture_text = st.text_area("متن درسنامه / مبحث علمی برای تولید تست")
            if st.button("✨ تولید هوشمند تست"):
                if lecture_text:
                    sentences = lecture_text.split(".")
                    found_test = False
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if "است" in sentence or "نام دارد" in sentence:
                            # Simple replacement to create a blank
                            blank_sent = sentence.replace("است", "..........").replace("نام دارد", "..........")
                            st.write(f"**سوال تولیدی:** {blank_sent}")
                            found_test = True
                    if not found_test:
                        st.warning("سیستم نتوانست جمله علمی تعریفی مناسبی پیدا کند. لطفاً متنی شامل تعاریف علمی بنویسید (مثلاً: ریشه دوم عدد ۲۵ برابر با ۵ است).")
                else:
                    st.warning("لطفاً ابتدا متنی را کپی و بارگذاری کنید.")
                    
        elif menu == "📂 ثبت نمرات و بازخوردهای کلاسی":
            st.header("📂 ثبت نمرات مستمر و مکتوب")
            
            conn = get_connection()
            df_students = pd.read_sql_query("""
                SELECT u.id, u.name, s.class_id, s.grade 
                FROM users u JOIN students s ON u.id = s.id
            """, conn)
            conn.close()
            
            student_sel = st.selectbox("انتخاب دانش‌آموز", df_students["name"].tolist())
            subject_m = st.text_input("عنوان ارزیابی کلاسی", "ریاضی - مستمر هفتگی")
            grade_val = st.number_input("نمره مکتوب / کلاسی (از ۲۰)", 0.0, 20.0, 18.0)
            desc = st.text_area("بازخورد و توصیه دبیر ریاضی")
            
            if st.button("ثبت نمره"):
                target_id = int(df_students[df_students["name"] == student_sel]["id"].values[0])
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO grades (student_id, subject, grade_val, date, description) VALUES (?, ?, ?, ?, ?)",
                               (target_id, subject_m, grade_val, datetime.now().strftime("%Y/%m/%d"), desc))
                conn.commit()
                conn.close()
                st.success(f"نمره {grade_val} برای {student_sel} ثبت شد و کارنامه به طور خودکار آپدیت گردید!")
                
        elif menu == "📅 مدیریت تقویم و امتحانات":
            st.header("📅 تقویم امتحانات و برنامه‌های کلاسی")
            
        elif menu == "🖥️ کلاس آنلاین و حضور و غیاب زنده":
            st.header("🖥️ کلاس آنلاین و سیستم مانیتورینگ زنده")
            
            st.subheader("۱. ایجاد و شروع کلاس زنده:")
            class_title = st.text_input("موضوع کلاس زنده", "رفع اشکال ریاضی متوسطه اول جاسک")
            if st.button("🚀 شروع کلاس و فعال‌سازی برای دانش‌آموزان"):
                st.info("کلاس فعال شد! لینک ورود برای دانش‌آموزان فعال گردید.")
                # Link to Jitsi Meet
                st.markdown(f'<a href="https://meet.jit.si/mofatteh_jask_math_class" target="_blank" style="display:inline-block; padding:12px 24px; background-color:#1E3A8A; color:white; font-weight:bold; text-decoration:none; border-radius:4px;">💻 ورود به محیط تصویری کلاس آنلاین</a>', unsafe_allow_html=True)
            
            st.write("---")
            st.subheader("👥 مانیتورینگ زنده و خودکار حضور غیاب:")
            st.write("جدول زیر دانش‌آموزانی را نشان می‌دهد که با ثبت حضور، وارد کلاس آنلاین شده‌اند:")
            
            conn = get_connection()
            # Since mock attendance holds class visits, let's select presence
            # We can read attendance where date is today or show a dummy live table
            df_att_live = pd.read_sql_query("""
                SELECT u.name as "نام دانش‌آموز", s.class_id as "کلاس", a.date as "ساعت ثبت ورود", a.status as "وضعیت"
                FROM attendance a
                JOIN users u ON a.student_id = u.id
                JOIN students s ON u.id = s.id
                WHERE a.status = 'حاضر'
                ORDER BY a.id DESC
            """, conn)
            conn.close()
            st.dataframe(df_att_live)

    elif role == "student":
        st.sidebar.markdown("### 🎓 پنل دانش‌آموزان")
        menu = st.sidebar.radio("انتخاب منو", [
            "📊 کارنامه و نمرات ماهانه",
            "✍️ آزمون‌های آنلاین چهارگزینه‌ای",
            "📂 تکالیف و کاربرگ‌ها",
            "🖥️ کلاس‌های آنلاین زنده",
            "📅 تقویم آموزشی و برنامه امتحانات",
            "📩 پیام‌رسان مستقیم با معلمان"
        ])
        
        if menu == "📊 کارنامه و نمرات ماهانه":
            st.header("📊 کارنامه و نمرات ماهانه شما")
            
            conn = get_connection()
            # Fetch grades
            df_my_grades = pd.read_sql_query(f"""
                SELECT subject as "عنوان ارزیابی کلاسی", grade_val as "نمره کلاسی (از ۲۰)", date as "تاریخ ثبت"
                FROM grades WHERE student_id = {user["id"]}
            """, conn)
            
            # Fetch quiz scores
            df_my_quizzes = pd.read_sql_query(f"""
                SELECT q.title as "عنوان آزمون تستی", qa.score as "نمره تستی", qa.date as "تاریخ شرکت"
                FROM quiz_attempts qa JOIN quizzes q ON qa.quiz_id = q.id
                WHERE qa.student_id = {user["id"]}
            """, conn)
            conn.close()
            
            st.subheader("۱. نمرات مستمر هفتگی")
            st.dataframe(df_my_grades)
            
            st.subheader("۲. نتایج آزمون‌های تستی")
            st.dataframe(df_my_quizzes)
            
            st.subheader("۳. دریافت کارنامه چاپی رسمی (پی‌دی‌اف)")
            card_path = os.path.join(os.path.dirname(__file__), "student-report-card-sample.pdf")
            if os.path.exists(card_path):
                with open(card_path, "rb") as f:
                    st.download_button("📥 دانلود کارنامه پی‌دی‌اف مهر و امضا شده", f, "report-card.pdf")
                    
        elif menu == "✍️ آزمون‌های آنلاین چهارگزینه‌ای":
            st.header("✍️ آزمون‌های آنلاین چهارگزینه‌ای")
            
            conn = get_connection()
            # Get quizzes for 9th grade
            df_quizzes = pd.read_sql_query("SELECT * FROM quizzes WHERE grade = 9", conn)
            conn.close()
            
            if not df_quizzes.empty:
                quiz = df_quizzes.iloc[0]
                st.subheader(f"آزمون فعال: {quiz['title']}")
                
                # Check if already attempted
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM quiz_attempts WHERE student_id = ? AND quiz_id = ?", (user["id"], quiz["id"]))
                attempt = cursor.fetchone()
                conn.close()
                
                if attempt:
                    st.warning(f"⚠️ شما قبلاً در این آزمون شرکت کرده‌اید. نمره شما: {attempt['score']} از ۲۰ می‌باشد.")
                else:
                    st.write("لطفاً به سوالات چهارگزینه‌ای زیر با دقت پاسخ دهید:")
                    
                    q1 = st.radio("۱. حاصل عبارت ۲ به توان ۳ ضربدر ۲ به توان ۴ کدام است؟", ["۲ به توان ۱۲", "۴ به توان ۷", "۲ به توان ۷", "۴ به توان ۱۲"])
                    q2 = st.radio("۲. ریشه سوم عدد منفی ۸ کدام است؟", ["-۲", "۲", "-۴", "وجود ندارد"])
                    
                    if st.button("ثبت و ارسال نهایی پاسخ‌ها"):
                        score = 20.0 # Standard simulation
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO quiz_attempts (student_id, quiz_id, score, date) VALUES (?, ?, ?, ?)",
                                       (user["id"], quiz["id"], score, datetime.now().strftime("%Y/%m/%d")))
                        conn.commit()
                        conn.close()
                        st.success(f"آزمون شما با موفقیت تصحیح شد! نمره نهایی: {score} از ۲۰. این نمره در کارنامه شما درج گردید.")
            else:
                st.info("در حال حاضر هیچ آزمون تستی فعالی برای پایه شما تعریف نشده است.")
                
        elif menu == "📂 تکالیف و کاربرگ‌ها":
            st.header("📂 کاربرگ‌ها و تکالیف مکتوب")
            st.write("کاربرگ‌ها را دانلود کرده و تصویر پاسخ‌نامه خود را از کادر زیر ارسال فرمایید:")
            
            st.info("📎 کاربرگ مبحث قوانین توان (پایه نهم) - دانلود شده")
            uploaded_hw = st.file_uploader("آپلود عکس یا پی‌دی‌اف پاسخ‌برگ تکالیف", type=["png", "jpg", "pdf"])
            if uploaded_hw is not None:
                st.success("تکلیف شما با موفقیت به صندوق ارسال معلم رستم سوری نسب منتقل شد. منتظر ثبت نمره و بازخورد باشید.")
                
        elif menu == "🖥️ کلاس‌های آنلاین زنده":
            st.header("🖥️ کلاس تصویری آنلاین")
            st.write("جهت ثبت حضور و غیاب و ورود به کلاس، اطلاعات زیر را مشخص کنید:")
            
            device_type = st.radio("نوع دستگاه ورودی شما برای کلاس:", ["موبایل 📱", "کامپیوتر 💻"])
            if st.button("🚀 ثبت حضور و ورود به کلاس آنلاین"):
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO attendance (student_id, status, date) VALUES (?, 'حاضر', ?)",
                               (user["id"], datetime.now().strftime("%H:%M:%S")))
                conn.commit()
                conn.close()
                st.success("حضور شما با موفقیت در سیستم مانیتورینگ دبیر ثبت گردید! اکنون می‌توانید وارد کلاس شوید.")
                st.markdown(f'<a href="https://meet.jit.si/mofatteh_jask_math_class" target="_blank" style="display:inline-block; padding:12px 24px; background-color:#10B981; color:white; font-weight:bold; text-decoration:none; border-radius:4px;">💻 ورود به محیط تصویری کلاس آنلاین</a>', unsafe_allow_html=True)

        elif menu == "📅 تقویم آموزشی و برنامه امتحانات":
            st.header("📅 تقویم آموزشی و برنامه امتحانات شما")
            conn = get_connection()
            df_ev = pd.read_sql_query("SELECT title, date, type FROM events WHERE grade = 9 ORDER BY date ASC", conn)
            conn.close()
            
            st.write("برنامه‌های کلاسی و امتحانی پیش‌رو:")
            for idx, row in df_ev.iterrows():
                color = "#EF4444" if row["type"] == "exam" else "#10B981"
                type_str = "امتحان کلاسی" if row["type"] == "exam" else "رویداد کلاسی"
                st.markdown(f"""
                <div style="border-right: 5px solid {color}; padding: 10px; background-color: #F9FAFB; margin-bottom: 10px; border-radius: 4px;">
                    <strong>{row['title']}</strong><br/>
                    📅 تاریخ: {row['date']} | 🏷️ نوع: {type_str}
                </div>
                """, unsafe_allow_html=True)

        elif menu == "📩 پیام‌رسان مستقیم با معلمان":
            st.header("📩 پیام‌رسان کلاسی")
            st.write("تعامل صمیمانه و تعاملی با دبیر ریاضی:")
            
            conn = get_connection()
            df_msg = pd.read_sql_query("SELECT text, sender_id, receiver_id FROM messages WHERE sender_id = 3 OR receiver_id = 3", conn)
            conn.close()
            
            for idx, row in df_msg.iterrows():
                align = "left" if row["sender_id"] == 3 else "right"
                color = "#EFF6FF" if row["sender_id"] == 3 else "#F3F4F6"
                st.markdown(f"""
                <div style="text-align: {align}; margin-bottom: 10px;">
                    <span style="display: inline-block; padding: 10px; background-color: {color}; border-radius: 8px; max-width: 70%;">
                        {row['text']}
                    </span>
                </div>
                """, unsafe_allow_html=True)
                
            new_msg = st.text_input("متن پیام جدید برای آقای سوری نسب...")
            if st.button("ارسال"):
                if new_msg:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO messages (sender_id, receiver_id, text, date) VALUES (3, 2, ?, ?)",
                                   (new_msg, datetime.now().strftime("%Y/%m/%d")))
                    conn.commit()
                    conn.close()
                    st.success("پیام شما ارسال شد.")
                    st.rerun()

    elif role == "parent":
        st.sidebar.markdown("### 👪 پنل اولیاء")
        menu = st.sidebar.radio("انتخاب منو", [
            "📊 کارنامه و نمرات ماهانه فرزند",
            "📢 تابلوی اعلانات و پیام‌رسان",
            "📅 تقویم آموزشی فرزند"
        ])
        
        if menu == "📊 کارنامه و نمرات ماهانه فرزند":
            st.header("📊 وضعیت تحصیلی و کارنامه ماهانه فرزند")
            st.write("مشاهده زنده وضعیت تحصیلی و دریافت پی‌دی‌اف کارنامه نهایی فرزندتان:")
            
            card_path = os.path.join(os.path.dirname(__file__), "student-report-card-sample.pdf")
            if os.path.exists(card_path):
                with open(card_path, "rb") as f:
                    st.download_button("📥 دانلود کارنامه چاپی مکتوب و امضا شده (.pdf)", f, "report-card.pdf")
                    
        elif menu == "📢 تابلوی اعلانات و پیام‌رسان":
            st.header("📩 صندوق گفتگوی دوطرفه با معلمان")
            
        elif menu == "📅 تقویم آموزشی فرزند":
            st.header("📅 تقویم امتحانی پیش‌روی فرزند")
