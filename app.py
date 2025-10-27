import hmac
import hashlib
import random
import string
import streamlit as st

#
# 1. هسته منطقی (دقیقا همان تابع قبلی، با رفع اشکال منطقی)
#
def generate_password(master_secret, site_key, version, length):
    """
    پسورد قطعی را بر اساس ورودی‌ها تولید می‌کند.
    این نسخه اصلاح شده و تضمین می‌کند هر 4 نوع کاراکتر وجود داشته باشند.
    """
    
    # 1. تعریف مجموعه کاراکترها (مجموعه ویژه قوی‌تر شد)
    SPECIAL_CHARS = "!@#$%!"
    UPPER_CHARS = string.ascii_uppercase
    LOWER_CHARS = string.ascii_lowercase
    DIGITS = string.digits

    # 2. بررسی حداقل طول
    if length < 4:
        raise ValueError("طول پسورد باید حداقل 4 باشد تا تمام قوانین رعایت شوند.")

    # 3. ایجاد "پیام" برای هش کردن
    message = f"{site_key.lower().strip()}:{version}"

    # 4. تولید هش قطعی (Seed) با HMAC-SHA256
    seed_bytes = hmac.new(
        master_secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()

    # 5. ساخت RNG مستقل (این روش عالی است و آن را حفظ می‌کنیم)
    seed_int = int.from_bytes(seed_bytes, byteorder='big', signed=False)
    rng = random.Random(seed_int)

    # 6. ساخت پسورد با تضمین رعایت قوانین (هر 4 نوع)
    password_chars = []
    password_chars.append(rng.choice(UPPER_CHARS))
    password_chars.append(rng.choice(LOWER_CHARS)) # <-- رفع مشکل: تضمین حرف کوچک
    password_chars.append(rng.choice(DIGITS))
    password_chars.append(rng.choice(SPECIAL_CHARS))

    pool = UPPER_CHARS + LOWER_CHARS + DIGITS + SPECIAL_CHARS

    # محاسبه طول باقی‌مانده بر اساس 4 کاراکتر تضمینی
    remaining_length = length - 4 # <-- رفع مشکل: از 3 به 4 تغییر کرد

    for _ in range(remaining_length):
        password_chars.append(rng.choice(pool))

    rng.shuffle(password_chars)

    # 7. بازگرداندن پسورد نهایی
    return "".join(password_chars)


#
# 2. رابط کاربری وب (Streamlit)
#

# تنظیمات اولیه صفحه
st.set_page_config(page_title="تولید کننده پسورد قطعی", layout="centered")

st.title("🔑 تولید کننده پسورد قطعی")
st.caption("بر اساس همان منطق HMAC-SHA256 برنامه دسکتاپ")

# --- فیلدهای ورودی ---
# معادل ویجت‌های tkinter

master_secret = st.text_input(
    "🔑 رمز اصلی (Master Secret)", 
    type="password",
    help="این رمز اصلی شماست. آن را فراموش نکنید!"
)

site_key = st.text_input(
    "🏷️ کلید سایت (Site Key)", 
    placeholder="e.g., google.com, my-bank, ...",
    help="نام وب‌سایت یا سرویسی که برای آن پسورد می‌خواهید."
)

# ایجاد دو ستون برای نسخه و طول
col1, col2 = st.columns(2)

with col1:
    version = st.number_input(
        "🔄 نسخه (Version)", 
        min_value=0, 
        max_value=99, 
        value=0, 
        step=1,
        help="اگر نیاز به تغییر پسورد یک سایت داشتید، فقط نسخه را بالا ببرید."
    )

with col2:
    length = st.number_input(
        "📏 طول پسورد", 
        min_value=4, 
        max_value=64, 
        value=10, # مقدار 16 به عنوان پیش‌فرض امن‌تر است
        step=1,
        help="طول پسورد نهایی. حداقل 4."
    )

st.divider()

# --- دکمه تولید و منطق آن ---

# استفاده از session_state برای نگهداری پسورد تولید شده
if 'generated_password' not in st.session_state:
    st.session_state.generated_password = ""

if st.button("🚀 تولید پسورد", use_container_width=True, type="primary"):
    # معادل on_generate_click
    
    if not master_secret or not site_key:
        st.warning("رمز اصلی و کلید سایت نمی‌توانند خالی باشند.", icon="⚠️")
        st.session_state.generated_password = ""
    else:
        try:
            # تولید پسورد
            password = generate_password(master_secret, site_key, version, int(length))
            
            # ذخیره پسورد در state
            st.session_state.generated_password = password
            st.success("✅ پسورد با موفقیت تولید شد.")
            
        except ValueError as e:
            st.error(f"خطا در ورودی: {e}", icon="❌")
            st.session_state.generated_password = ""
        except Exception as e:
            st.error(f"بروز خطای ناشناخته: {e}", icon="🔥")
            st.session_state.generated_password = ""

# --- نمایش نتیجه و دکمه کپی ---

if st.session_state.generated_password:
    st.info("🔒 پسورد تولید شده (برای کپی روی آیکون کلیک کنید):")
    
    # این ویجت معادل Entry readonly + دکمه Copy است

    st.code(st.session_state.generated_password, language=None)
