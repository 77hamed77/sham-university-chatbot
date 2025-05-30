import re

def clean_text_data(paragraphs):
    """
    تقوم بتنظيف قائمة من الفقرات النصية.

    المعلمات:
    paragraphs (list): قائمة من السلاسل النصية (الفقرات) المراد تنظيفها.

    النتائج:
    list: قائمة بالفقرات النصية النظيفة والفريدة.
    """
    cleaned_unique_paragraphs = set() # استخدام مجموعة لضمان التفرد تلقائياً

    # قائمة بالعبارات الشائعة وغير المفيدة التي تم ملاحظتها في بياناتك
    unwanted_phrases = [
        "نهتم دوما بالاستماع إلى مقترحاتكم وآرائكم.",
        "Copyright ©جميع الحقوق محفوظة لجامعة الشام",
        "جامعة الشام",
        "Sham university",
        "المزيد", # للتعامل مع فقرات "المزيد" التي لا تحتوي على نص آخر
        "Copyright ©جميع الحقوق محفوظة لمركز شام للدراسات والبحث العلمي",
        "Sham university" # مكررة ولكن للتأكيد
    ]

    for text in paragraphs:
        # 1. إزالة المسافات البيضاء الزائدة من البداية والنهاية
        text = text.strip()

        # 2. إزالة النصوص غير المفيدة والمكررة
        # نستخدم الاستبدال بمسافة فارغة لضمان عدم ترك بقايا نصية
        for phrase in unwanted_phrases:
            text = text.replace(phrase, "")

        # 3. إزالة أي أرقام وحروف غير أبجدية (مع الحفاظ على الحروف العربية والإنجليزية والمسافات)
        # هذا التعبير العادي يحافظ على الحروف العربية (ابتداءً من أ إلى ي)، والحروف الإنجليزية (a-z, A-Z)، والمسافات.
        # يمكن تعديله ليحتفظ بعلامات ترقيم معينة إذا كانت مهمة للسياق.
        text = re.sub(r'[^\u0600-\u06FF\sA-Za-z]', '', text)

        # 4. توحيد المسافات البيضاء المتعددة إلى مسافة واحدة
        text = re.sub(r'\s+', ' ', text).strip()

        # 5. تحويل النص إلى أحرف صغيرة (مفيد للنصوص الإنجليزية لتوحيدها، لا يؤثر على العربية)
        text = text.lower()

        # 6. إزالة الفقرات الفارغة بعد التنظيف أو التي تحتوي على مسافات فقط
        if text and len(text) > 5: # تجاهل الفقرات القصيرة جداً (أقل من 5 أحرف)
            cleaned_unique_paragraphs.add(text) # إضافة الفقرة النظيفة للمجموعة

    # تحويل المجموعة مرة أخرى إلى قائمة لسهولة الاستخدام
    return list(cleaned_unique_paragraphs)

# يجب قراءة الفقرات من الملف الذي تم إنشاؤه في الخطوة السابقة
# تأكد من أن ملف 'all_university_paragraphs.txt' موجود في نفس مسار تشغيل الكود
try:
    with open("all_university_paragraphs.txt", "r", encoding="utf-8") as f:
        raw_paragraphs = f.readlines()
    print(f"تم قراءة {len(raw_paragraphs)} فقرة من الملف.")
except FileNotFoundError:
    print("خطأ: لم يتم العثور على ملف 'all_university_paragraphs.txt'. يرجى التأكد من تشغيل كود الزحف أولاً.")
    raw_paragraphs = []

if raw_paragraphs:
    cleaned_paragraphs = clean_text_data(raw_paragraphs)

    print(f"\nتم تنظيف واستخراج {len(cleaned_paragraphs)} فقرة فريدة.")
    print("\n--- أول 20 فقرة نظيفة وفريدة ---")
    for i, p in enumerate(cleaned_paragraphs[:20]):
        print(f"{i+1}. {p}")

    # حفظ الفقرات النظيفة في ملف جديد
    output_cleaned_file = "cleaned_university_paragraphs.txt"
    with open(output_cleaned_file, "w", encoding="utf-8") as f:
        for p in cleaned_paragraphs:
            f.write(p + "\n")
    print(f"\nتم حفظ الفقرات النظيفة في الملف: {output_cleaned_file}")