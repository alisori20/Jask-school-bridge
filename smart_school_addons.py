import streamlit as st
import sqlite3
import pandas as pd
import os
import random
from datetime import datetime

# --- CREATOR LICENSE SETTINGS (Easily customizable by Mr. Souri Nasab) ---
CREATOR_NAME = "رستم سوری نسب (طراح و توسعه‌دهنده سامانه)"
CREATOR_CARD = "۶۰۳۷-۹۹۷۹-۱۲۳۴-۵۶۷۸" # شماره کارت واقعی جهت واریز هزینه فعال‌سازی
CREATOR_BANK = "ملی ایران"
CREATOR_PRICE = 450000 # هزینه فعال‌سازی به تومان

def check_license_status(get_connection):
    """
    Checks the trial and activation status of the application.
    Returns: (status, days_left)
    - status can be: 'trial', 'expired', 'activated'
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Ensure school_settings table exists
    cursor.execute("CREATE TABLE IF NOT EXISTS school_settings (key TEXT PRIMARY KEY, val TEXT)")
    
    # Check activation state
    cursor.execute("SELECT val FROM school_settings WHERE key = 'is_activated'")
    row_act = cursor.fetchone()
    is_activated = row_act['val'] if row_act else '0'
    
    if is_activated == '1':
        conn.close()
        return 'activated', 0
        
    # Check installation date
    cursor.execute("SELECT val FROM school_settings WHERE key = 'installation_date'")
    row_date = cursor.fetchone()
    
    if not row_date:
        # First boot, save today's date
        now_str = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("INSERT OR REPLACE INTO school_settings (key, val) VALUES ('installation_date', ?)", (now_str,))
        cursor.execute("INSERT OR REPLACE INTO school_settings (key, val) VALUES ('is_activated', '0')")
        conn.commit()
        conn.close()
        return 'trial', 10
        
    try:
        installation_date = datetime.strptime(row_date['val'], "%Y-%m-%d")
    except Exception:
        installation_date = datetime.now()
        
    conn.close()
    
    days_passed = (datetime.now() - installation_date).days
    days_left = 10 - days_passed
    
    if days_left <= 0:
        return 'expired', 0
    return 'trial', days_left

def render_activation_gateway(get_connection):
    """
    Renders a highly realistic Shaparak mock payment gateway for activating the app license.
    """
    st.markdown(f"""
    <div style="background-color: #FEF2F2; border: 2px solid #FCA5A5; border-radius: 12px; padding: 25px; margin-top: 10px; font-family: 'Noto Sans Arabic', sans-serif; text-align: right; direction: rtl;">
        <div style="text-align: center; border-bottom: 2px solid #EF4444; padding-bottom: 15px; margin-bottom: 20px;">
            <h2 style="color: #991B1B; margin: 0; font-size: 24px; font-family: 'Noto Sans Arabic', sans-serif !important;">🔑 فعال‌سازی دائمی و تمدید لایسنس نرم‌افزار</h2>
            <p style="color: #991B1B; margin: 5px 0 0 0; font-size: 14px; font-family: 'Noto Sans Arabic', sans-serif !important;">مهلت استفاده آزمایشی رایگان ۱۰ روزه این مدرسه به پایان رسیده است.</p>
        </div>
        <p style="font-size: 15px; line-height: 1.8; color: #7F1D1D; font-family: 'Noto Sans Arabic', sans-serif !important;">
            جهت فعال‌سازی دائمی تمامی امکانات سامانه هوشمند پُل (شامل کلاس‌های آنلاین زنده، آزمون‌ساز هوشمند هوش مصنوعی، پنل دبیران، اولیاء و کارنامه‌های چاپی)، لطفا هزینه لایسنس تعیین‌شده را به حساب طراح و توسعه‌دهنده سامانه واریز نمایید. بلافاصله پس از پرداخت موفقیت‌آمیز، قفل نرم‌افزار به صورت خودکار و دائمی فعال شده و تمامی محدودیت‌ها حذف می‌گردند.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_pay1, col_pay2 = st.columns(2)
    with col_pay1:
        st.markdown(f"""
        <div style="background-color: #EFF6FF; border-right: 5px solid #2563EB; padding: 15px; border-radius: 6px; margin-top: 15px; text-align: right; direction: rtl;">
            <p style="margin: 0; font-weight: bold; color: #1E3A8A; font-family: 'Noto Sans Arabic', sans-serif !important;">👤 حساب مقصد (طراح و توسعه‌دهنده):</p>
            <p style="margin: 5px 0 0 0; font-size: 14px; font-family: 'Noto Sans Arabic', sans-serif !important;"><b>نام دریافت‌کننده:</b> {CREATOR_NAME}</p>
            <p style="margin: 5px 0 0 0; font-size: 14px; font-family: 'Noto Sans Arabic', sans-serif !important;"><b>نام بانک:</b> {CREATOR_BANK}</p>
            <p style="margin: 5px 0 0 0; font-size: 14px; color: #2563EB; font-family: monospace; letter-spacing: 1px;"><b>شماره کارت:</b> {CREATOR_CARD}</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_pay2:
        st.markdown(f"""
        <div style="background-color: #FEF3C7; border-right: 5px solid #D97706; padding: 15px; border-radius: 6px; margin-top: 15px; text-align: right; direction: rtl;">
            <p style="margin: 0; font-weight: bold; color: #92400E; font-family: 'Noto Sans Arabic', sans-serif !important;">💰 هزینه لایسنس فعال‌سازی:</p>
            <p style="margin: 10px 0 0 0; font-size: 24px; font-weight: bold; color: #B45309; font-family: 'Noto Sans Arabic', sans-serif !important;">{CREATOR_PRICE:,} تومان</p>
            <p style="margin: 5px 0 0 0; font-size: 12px; color: #92400E; font-family: 'Noto Sans Arabic', sans-serif !important;">پرداخت یک‌باره و لایسنس مادام‌العمر برای کل سیستم مدرسه.</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.write("")
    with st.form("creator_activation_payment_form"):
        st.write("🔒 **درگاه شبیه‌سازی‌شده امن شاپرک - پرداخت مستقیم به سازنده:**")
        col_c1, col_c2 = st.columns([2, 1])
        with col_c1:
            card_no = st.text_input("شماره ۱۶ رقمی کارت بانکی شما", placeholder="6037997912345678", max_chars=16)
        with col_c2:
            cvv2 = st.text_input("کد امنیتی CVV2", placeholder="123", type="password", max_chars=4)
            
        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            exp_month = st.selectbox("ماه انقضا", [f"{i:02d}" for i in range(1, 13)])
        with col_exp2:
            exp_year = st.selectbox("سال انقضا", [str(i) for i in range(1403, 1415)])
            
        col_otp1, col_otp2 = st.columns([2, 1])
        with col_otp1:
            otp_val = st.text_input("رمز دوم / رمز پویا", placeholder="کد پیامک‌شده را وارد کنید")
        with col_otp2:
            st.write("")
            st.write("")
            if st.form_submit_button("📩 دریافت رمز پویا"):
                st.toast("🔑 رمز پویا شبیه‌سازی‌شده به شماره مدیریت ارسال شد: 99421", icon="💬")
                
        pay_btn = st.form_submit_button("🚀 تایید و فعال‌سازی دائمی سامانه")
        if pay_btn:
            if len(card_no) == 16 and cvv2 and otp_val:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO school_settings (key, val) VALUES ('is_activated', '1')")
                conn.commit()
                conn.close()
                st.success("🎉 تراکنش موفقیت‌آمیز بود! قفل سیستم با موفقیت به صورت دائمی باز شد. از اعتماد و حمایت شما سپاسگزاریم.")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ اطلاعات کارت بانکی یا رمز دوم اشتباه است.")

def upgrade_db_schema(get_connection):
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. School settings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS school_settings (
        key TEXT PRIMARY KEY,
        val TEXT
    )
    """)
    # Seed default school name if not exists
    cursor.execute("INSERT OR IGNORE INTO school_settings (key, val) VALUES ('school_name', 'دبیرستان متوسطه اول شهید مفتح جاسک')")
    cursor.execute("INSERT OR IGNORE INTO school_settings (key, val) VALUES ('school_theme', 'آبی هوشمند')")

    # 2. Remedial classes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS remedial_classes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        grade INTEGER NOT NULL,
        capacity INTEGER NOT NULL,
        price REAL NOT NULL,
        schedule TEXT,
        status TEXT DEFAULT 'active'
    )
    """)

    # 3. Teacher payment gateway settings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teacher_gateways (
        teacher_id INTEGER PRIMARY KEY,
        card_number TEXT,
        sheba TEXT,
        bank_name TEXT,
        gateway_type TEXT DEFAULT 'direct',
        merchant_id TEXT
    )
    """)

    # 4. Class payments/registrations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS class_payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        class_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        card_number TEXT,
        tracking_code TEXT,
        status TEXT DEFAULT 'pending',
        date TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

def show_mock_payment_gateway(class_info, teacher_gateway, on_success_callback):
    st.markdown("""
    <div style="background-color: #F8FAFC; border: 2px solid #E2E8F0; border-radius: 12px; padding: 25px; margin-top: 20px; font-family: 'Noto Sans Arabic', sans-serif;">
        <div style="text-align: center; border-bottom: 2px solid #3B82F6; padding-bottom: 15px; margin-bottom: 20px;">
            <h2 style="color: #1E3A8A; margin: 0; font-size: 22px; font-family: 'Noto Sans Arabic', sans-serif !important;">💳 درگاه پرداخت الکترونیک شاپرک</h2>
            <p style="color: #64748B; margin: 5px 0 0 0; font-size: 14px; font-family: 'Noto Sans Arabic', sans-serif !important;">سامانه پرداخت مدارس هوشمند ایران</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.info(f"📍 شما در حال پرداخت هزینه ثبت‌نام کلاس «{class_info['title']}» هستید.")
    
    col_pay1, col_pay2 = st.columns(2)
    with col_pay1:
        st.markdown(f"""
        <div style="background-color: #EFF6FF; border-right: 5px solid #3B82F6; padding: 15px; border-radius: 6px; margin-bottom: 20px; text-align: right; direction: rtl;">
            <p style="margin: 0; font-weight: bold; color: #1E3A8A; font-family: 'Noto Sans Arabic', sans-serif !important;">👤 اطلاعات دبیر و حساب مقصد:</p>
            <p style="margin: 5px 0 0 0; font-size: 14px; font-family: 'Noto Sans Arabic', sans-serif !important;"><b>نام دبیر:</b> {class_info['teacher_name']}</p>
            <p style="margin: 5px 0 0 0; font-size: 14px; font-family: 'Noto Sans Arabic', sans-serif !important;"><b>نام بانک:</b> {teacher_gateway['bank_name'] if teacher_gateway['bank_name'] else 'ملی ایران'}</p>
            <p style="margin: 5px 0 0 0; font-size: 14px; color: #2563EB; font-family: monospace; letter-spacing: 1px;"><b>شماره کارت:</b> {teacher_gateway['card_number'] if teacher_gateway['card_number'] else '۶۰۳۷-۹۹۷۹-XXXX-XXXX'}</p>
            {"<p style='margin: 5px 0 0 0; font-size: 12px; font-family: Noto Sans Arabic !important;'><b>شماره شبا:</b> " + teacher_gateway['sheba'] + "</p>" if teacher_gateway['sheba'] else ""}
        </div>
        """, unsafe_allow_html=True)
        
    with col_pay2:
        st.markdown(f"""
        <div style="background-color: #FEF2F2; border-right: 5px solid #EF4444; padding: 15px; border-radius: 6px; margin-bottom: 20px; text-align: right; direction: rtl;">
            <p style="margin: 0; font-weight: bold; color: #991B1B; font-family: 'Noto Sans Arabic', sans-serif !important;">💰 مبلغ قابل پرداخت:</p>
            <p style="margin: 10px 0 0 0; font-size: 24px; font-weight: bold; color: #DC2626; font-family: 'Noto Sans Arabic', sans-serif !important;">{class_info['price']:,} تومان</p>
            <p style="margin: 5px 0 0 0; font-size: 12px; color: #7F1D1D; font-family: 'Noto Sans Arabic', sans-serif !important;">تراکنش تحت پروتکل امن SSL شاپرک انجام می‌شود.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with st.form("shaparak_payment_form"):
        st.write("🔒 **لطفاً اطلاعات کارت بانکی خود را وارد کنید:**")
        col_c1, col_c2 = st.columns([2, 1])
        with col_c1:
            card_no = st.text_input("شماره ۱۶ رقمی کارت", placeholder="6037997912345678", max_chars=16)
        with col_c2:
            cvv2 = st.text_input("کد امنیتی CVV2", placeholder="123", type="password", max_chars=4)
            
        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            exp_month = st.selectbox("ماه انقضا", [f"{i:02d}" for i in range(1, 13)])
        with col_exp2:
            exp_year = st.selectbox("سال انقضا", [str(i) for i in range(1403, 1415)])
            
        col_otp1, col_otp2 = st.columns([2, 1])
        with col_otp1:
            otp_val = st.text_input("رمز پویا / رمز دوم", placeholder="کد پیامک‌شده را وارد کنید")
        with col_otp2:
            st.write("")
            st.write("")
            if st.form_submit_button("📩 دریافت رمز پویا"):
                st.toast("🔑 رمز پویا به شماره همراه شبیه‌سازی‌شده شما ارسال شد: 58213", icon="💬")
                st.session_state.mock_otp_sent = True
                
        pay_btn = st.form_submit_button("🚀 تایید و پرداخت نهایی هزینه")
        if pay_btn:
            if len(card_no) == 16 and cvv2 and otp_val:
                trk_code = f\"TRK-{random.randint(10000000, 99999999)}\"
                on_success_callback(trk_code, card_no[-4:])
            else:
                st.error("❌ لطفاً شماره کارت ۱۶ رقمی، CVV2 و رمز دوم را به درستی وارد کنید.")
                
    st.markdown("</div>", unsafe_allow_html=True)

def render_teacher_classes_panel(get_connection, teacher_id):
    st.header("🏫 مدیریت کلاس‌های تقویتی و خصوصی دبیرستان")
    
    t1, t2, t3 = st.tabs([
        "➕ تعریف کلاس جدید",
        "👥 مدیریت ثبت‌نامی‌ها و تراکنش‌ها",
        "💳 تنظیم درگاه پرداخت شخصی"
    ])
    
    with t3:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM teacher_gateways WHERE teacher_id = ?", (teacher_id,))
        gateway = cursor.fetchone()
        conn.close()
        
        current_card = gateway['card_number'] if gateway else ""
        current_sheba = gateway['sheba'] if gateway else ""
        current_bank = gateway['bank_name'] if gateway else ""
        current_merchant = gateway['merchant_id'] if gateway else ""
        current_type = gateway['gateway_type'] if gateway else "direct"
        
        st.subheader("💳 مشخصات درگاه پرداخت شخصی")
        st.write("با پر کردن این بخش، هزینه دوره‌ها بدون واسطه مستقیماً به کارت شما واریز خواهد شد:")
        
        with st.form("teacher_gateway_form_addons"):
            bank_name = st.text_input("نام بانک صادرکننده کارت", value=current_bank, placeholder="مثلاً: ملی، ملت، صادرات")
            card_number = st.text_input("شماره کارت ۱۶ رقمی شما", value=current_card, placeholder="۶۰۳۷-۹۹۷۹-XXXX-XXXX")
            sheba = st.text_input("شماره شبا حساب شما", value=current_sheba, placeholder="IRXXXXXXXXXXXXXXXXXXXXXXXX")
            
            st.write("---")
            gateway_type = st.radio("روش تسویه حساب:", ["واریز کارت به کارت مستقیم (شبیه‌سازی کارت)", "اتصال به مرچنت اختصاصی زرین‌پال"], index=0 if current_type == "direct" else 1)
            merchant_id = st.text_input("مرچنت کد زرین‌پال (اختیاری)", value=current_merchant, placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
            
            submit_g = st.form_submit_button("💾 ذخیره درگاه شخصی")
            if submit_g:
                if bank_name and card_number:
                    g_type = "direct" if "کارت" in gateway_type else "zarinpal"
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                    INSERT INTO teacher_gateways (teacher_id, card_number, sheba, bank_name, gateway_type, merchant_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(teacher_id) DO UPDATE SET
                        card_number = excluded.card_number,
                        sheba = excluded.sheba,
                        bank_name = excluded.bank_name,
                        gateway_type = excluded.gateway_type,
                        merchant_id = excluded.merchant_id
                    """, (teacher_id, card_number, sheba, bank_name, g_type, merchant_id))
                    conn.commit()
                    conn.close()
                    st.success("✅ درگاه شخصی شما با موفقیت ذخیره و فعال شد!")
                    st.rerun()
                else:
                    st.warning("⚠️ تکمیل کادرهای نام بانک و شماره کارت الزامی است.")
                    
    with t1:
        st.subheader("➕ تعریف کلاس جدید")
        st.write("مشخصات کلاس یا دوره فشرده تقویتی خود را ثبت نمایید:")
        
        with st.form("create_class_form_addons", clear_on_submit=True):
            title = st.text_input("عنوان کلاس", placeholder="مثال: مینی‌دوره تقویت هوش هندسی نهم")
            grade = st.selectbox("پایه تحصیلی هدف", [7, 8, 9], index=2)
            price = st.number_input("هزینه ثبت‌نام آنلاین (تومان)", min_value=0, value=30000, step=5000)
            capacity = st.number_input("حداکثر ظرفیت ثبت‌نام (نفر)", min_value=1, value=20)
            schedule = st.text_input("روزها و ساعات برگزاری کلاس", placeholder="مثال: پنجشنبه‌ها ساعت ۱۰:۰۰ الی ۱۲:۰۰")
            description = st.text_area("توضیحات تکمیلی و اهداف دوره")
            
            submit_c = st.form_submit_button("🚀 انتشار و شروع ثبت‌نام")
            if submit_c:
                if title and schedule and price >= 0:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                    INSERT INTO remedial_classes (teacher_id, title, description, grade, capacity, price, schedule)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (teacher_id, title, description, grade, capacity, price, schedule))
                    conn.commit()
                    conn.close()
                    st.success(f"🎉 کلاس «{title}» با موفقیت فعال شد و در پنل دانش‌آموزان پایه {grade} قرار گرفت!")
                    st.balloons()
                else:
                    st.error("❌ لطفا تمام فیلدهای الزامی را پر کنید.")
                    
    with t2:
        st.subheader("👥 مدیریت ثبت‌نامی‌ها و تراکنش‌ها")
        conn = get_connection()
        df_classes = pd.read_sql_query(f"SELECT * FROM remedial_classes WHERE teacher_id = {teacher_id}", conn)
        conn.close()
        
        if df_classes.empty:
            st.info("💡 شما هنوز کلاس تقویتی تعریف نکرده‌اید.")
        else:
            class_options = {row['title']: row['id'] for idx, row in df_classes.iterrows()}
            selected_class_title = st.selectbox("🎯 انتخاب کلاس جهت بررسی:", list(class_options.keys()))
            
            if selected_class_title:
                class_id = class_options[selected_class_title]
                conn = get_connection()
                df_payments = pd.read_sql_query(f"""
                    SELECT cp.id as payment_id, u.name as student_name, cp.amount, cp.card_number, cp.tracking_code, cp.status, cp.date
                    FROM class_payments cp
                    JOIN users u ON cp.student_id = u.id
                    WHERE cp.class_id = {class_id}
                    ORDER BY cp.id DESC
                """, conn)
                conn.close()
                
                if df_payments.empty:
                    st.warning("⚠️ هنوز هیچ پرداختی ثبت نشده است.")
                else:
                    for idx, row in df_payments.iterrows():
                        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
                        with col1:
                            st.write(f"👤 **دانش‌آموز:** {row['student_name']}")
                            st.write(f"📅 **تاریخ:** {row['date']}")
                        with col2:
                            st.write(f"💰 **مبلغ واریزی:** {row['amount']:,} تومان")
                            st.write(f"💳 **۴ رقم آخر کارت:** {row['card_number']}")
                        with col3:
                            st.write(f"🔑 **کد پیگیری:** `{row['tracking_code']}`")
                            status_label = "⏳ در انتظار تایید" if row['status'] == 'pending' else ("✔️ تایید شده" if row['status'] == 'paid' else "❌ رد شده")
                            color = "orange" if row['status'] == 'pending' else ("green" if row['status'] == 'paid' else "red")
                            st.markdown(f"وضعیت: <b style='color:{color};'>{status_label}</b>", unsafe_allow_html=True)
                        with col4:
                            if row['status'] == 'pending':
                                col_b1, col_b2 = st.columns(2)
                                with col_b1:
                                    if st.button("✔️ تایید", key=f"t_app_{row['payment_id']}"):
                                        conn = get_connection()
                                        cursor = conn.cursor()
                                        cursor.execute("UPDATE class_payments SET status = 'paid' WHERE id = ?", (row['payment_id'],))
                                        cursor.execute("UPDATE remedial_classes SET capacity = capacity - 1 WHERE id = ?", (class_id,))
                                        conn.commit()
                                        conn.close()
                                        st.success("تایید شد!")
                                        st.rerun()
                                with col_b2:
                                    if st.button("❌ رد", key=f"t_rej_{row['payment_id']}"):
                                        conn = get_connection()
                                        cursor = conn.cursor()
                                        cursor.execute("UPDATE class_payments SET status = 'rejected' WHERE id = ?", (row['payment_id'],))
                                        conn.commit()
                                        conn.close()
                                        st.error("رد شد!")
                                        st.rerun()
                        st.markdown("---")

def show_student_remedial_classes(get_connection, student_id, student_grade):
    st.subheader("🏫 ثبت‌نام کلاس‌های تقویتی و خصوصی")
    st.write("دوره‌های کمکی فعال ویژه پایه تحصیلی شما در زیر لیست شده است. می‌توانید هزینه را با درگاه شخصی هر دبیر پرداخت و در کلاس عضو شوید:")
    
    conn = get_connection()
    df_classes = pd.read_sql_query(f"""
        SELECT rc.*, u.name as teacher_name
        FROM remedial_classes rc
        JOIN users u ON rc.teacher_id = u.id
        WHERE rc.grade = {student_grade} AND rc.status = 'active'
    """, conn)
    conn.close()
    
    if df_classes.empty:
        st.info("💡 در حال حاضر هیچ کلاس تقویتی فعالی برای پایه شما تعریف نشده است.")
        return
        
    for idx, row in df_classes.iterrows():
        # Get payment
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM class_payments WHERE student_id = ? AND class_id = ?", (student_id, row['id']))
        payment = cursor.fetchone()
        
        # Get teacher gateway
        cursor.execute("SELECT * FROM teacher_gateways WHERE teacher_id = ?", (row['teacher_id'],))
        gateway = cursor.fetchone()
        conn.close()
        
        st.markdown(f"""
        <div style="background-color: #EFF6FF; border-right: 5px solid #2563EB; padding: 15px; border-radius: 8px; margin-bottom: 10px; text-align: right; direction: rtl;">
            <h4 style="margin:0; color:#1E3A8A; font-family: 'Noto Sans Arabic', sans-serif !important;">🏫 {row['title']}</h4>
            <p style="margin:5px 0 0 0; font-size:14px; font-family: 'Noto Sans Arabic', sans-serif !important;">👨‍🏫 <b>مدرس:</b> {row['teacher_name']} | 📅 <b>برنامه زمانی:</b> {row['schedule']}</p>
            <p style="margin:5px 0 0 0; font-size:14px; font-family: 'Noto Sans Arabic', sans-serif !important;">👥 <b>ظرفیت باقیمانده:</b> {row['capacity']} نفر | 💰 <b>مبلغ:</b> {row['price']:,} تومان</p>
            {"<p style='margin:5px 0 0 0; font-size:12px; color:#4B5563; font-family: Noto Sans Arabic !important;'><b>توضیحات:</b> " + row['description'] + "</p>" if row['description'] else ""}
        </div>
        """, unsafe_allow_html=True)
        
        if payment:
            if payment['status'] == 'paid':
                st.success(f"✔️ شما با موفقیت در این کلاس عضو شده‌اید. (کد پیگیری تراکنش: {payment['tracking_code']})")
            elif payment['status'] == 'pending':
                st.warning(f"⏳ پرداخت شما به مبلغ {payment['amount']:,} ثبت شده و منتظر تایید دبیر است. (کد پیگیری: {payment['tracking_code']})")
            elif payment['status'] == 'rejected':
                st.error("❌ پرداخت شما تایید نشد. در صورت تمایل می‌توانید دوباره هزینه را پرداخت کنید.")
                if st.button("💳 پرداخت مجدد و ثبت‌نام", key=f"re_pay_{row['id']}"):
                    st.session_state.paying_for_class_id = row['id']
                    st.rerun()
        else:
            if row['capacity'] <= 0:
                st.error("🚫 ظرفیت ثبت‌نام آنلاین این کلاس پر شده است.")
            else:
                if st.button("💳 پرداخت آنلاین و ثبت‌نام در کلاس", key=f"pay_start_{row['id']}"):
                    st.session_state.paying_for_class_id = row['id']
                    st.rerun()
                    
        if "paying_for_class_id" in st.session_state and st.session_state.paying_for_class_id == row['id']:
            t_gateway = {
                "bank_name": gateway["bank_name"] if gateway else "ملی ایران",
                "card_number": gateway["card_number"] if gateway else "۶۰۳۷-۹۹۷۹-۰۰۰۰-۰۰۰۰",
                "sheba": gateway["sheba"] if gateway else ""
            }
            
            def on_pay_complete(trk, last4):
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO class_payments (student_id, class_id, amount, card_number, tracking_code, date)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (student_id, row['id'], row['price'], last4, trk, datetime.now().strftime("%Y/%m/%d %H:%M:%S")))
                conn.commit()
                conn.close()
                st.success("✅ تراکنش با موفقیت به بانک ارسال شد! کد رهگیری بانک شما جهت تایید دبیر صادر گردید.")
                st.balloons()
                del st.session_state.paying_for_class_id
                st.rerun()
                
            show_mock_payment_gateway(
                class_info={"title": row['title'], "price": row['price'], "teacher_name": row['teacher_name']},
                teacher_gateway=t_gateway,
                on_success_callback=on_pay_complete
            )
            
            if st.button("❌ انصراف از پرداخت", key=f"cncl_p_{row['id']}"):
                del st.session_state.paying_for_class_id
                st.rerun()
        st.write("---")

def render_admin_classes_panel(get_connection):
    st.header("🏫 تنظیمات پورتال مدارس هوشمند")
    
    tab_settings, tab_monitor = st.tabs([
        "⚙️ تنظیمات نام و قالب سامانه",
        "📊 نظارت بر کلاس‌ها و عواید مالی"
    ])
    
    with tab_settings:
        st.subheader("⚙️ بومی‌سازی و سفارشی‌سازی برای کل مدارس کشور")
        st.write("این سامانه کاملاً ماژولار است. می‌توانید نام مدرسه خود را تغییر داده و تم ظاهری شاداب و هوشمندی انتخاب کنید تا در کل صفحات پورتال اعمال شود:")
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT val FROM school_settings WHERE key = 'school_name'")
        sc_name = cursor.fetchone()
        cursor.execute("SELECT val FROM school_settings WHERE key = 'school_theme'")
        sc_theme = cursor.fetchone()
        conn.close()
        
        current_name = sc_name['val'] if sc_name else "دبیرستان متوسطه اول شهید مفتح جاسک"
        current_theme = sc_theme['val'] if sc_theme else "آبی هوشمند"
        
        with st.form("school_general_settings_form"):
            new_school_name = st.text_input("نام رسمی مدرسه شما:", value=current_name)
            new_theme = st.selectbox("انتخاب تم رنگی و استایل شاداب سامانه:", [
                "آبی هوشمند (پیش‌فرض)", 
                "سبز شاداب (طراوت آموزشی)", 
                "نارنجی پرانرژی (خلاقیت و انگیزه)"
            ], index=0 if "آبی" in current_theme else (1 if "سبز" in current_theme else 2))
            
            submit_set = st.form_submit_button("💾 ذخیره و اعمال تغییرات پوسته")
            if submit_set:
                theme_val = "آبی هوشمند" if "آبی" in new_theme else ("سبز شاداب" if "سبز" in new_theme else "نارنجی پرانرژی")
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO school_settings (key, val) VALUES ('school_name', ?)", (new_school_name,))
                cursor.execute("INSERT OR REPLACE INTO school_settings (key, val) VALUES ('school_theme', ?)", (theme_val,))
                conn.commit()
                conn.close()
                st.success("🎉 پوسته و مشخصات جدید با موفقیت اعمال شد و در کسری از ثانیه در تمام پنل‌ها فعال گردید!")
                st.rerun()
                
    with tab_monitor:
        st.subheader("📊 خلاصه درآمدها و وضعیت تراکنش‌ها")
        conn = get_connection()
        
        df_summary = pd.read_sql_query("""
            SELECT rc.title as "عنوان کلاس", u.name as "دبیر مربوطه", rc.price as "هزینه دوره", rc.capacity as "ظرفیت باقیمانده",
                   SUM(CASE WHEN cp.status = 'paid' THEN 1 ELSE 0 END) as "تعداد ثبت‌نامی قطعی",
                   SUM(CASE WHEN cp.status = 'paid' THEN cp.amount ELSE 0 END) as "کل درآمد دریافتی"
            FROM remedial_classes rc
            JOIN users u ON rc.teacher_id = u.id
            LEFT JOIN class_payments cp ON rc.id = cp.class_id
            GROUP BY rc.id
        """, conn)
        conn.close()
        
        if df_summary.empty:
            st.info("💡 در حال حاضر هیچ تراکنش یا کلاسی تعریف نشده است.")
        else:
            st.dataframe(df_summary)
            
            # Show overall statistic
            total_earned = df_summary["کل درآمد دریافتی"].sum()
            st.markdown(f"""
            <div style="background-color: #F0FDF4; border: 1px solid #16A34A; padding: 15px; border-radius: 8px; margin-top: 15px; text-align: center;">
                <h3 style="color: #16A34A; margin: 0; font-family: Noto Sans Arabic !important;">💰 مجموع گردش مالی کلاس‌های فوق برنامه مدرسه:</h3>
                <h2 style="color: #15803D; margin: 5px 0 0 0; font-family: Noto Sans Arabic !important;">{total_earned:,.0f} تومان</h2>
            </div>
            """, unsafe_allow_html=True)
