import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import urllib3
import pytesseract # لاستخدام Tesseract OCR
from PIL import Image # لمعالجة الصور
import io # للمساعدة في قراءة بيانات الصورة من الذاكرة
import os # لتعيين مسار Tesseract إذا لزم الأمر

# --- إعداد Tesseract OCR في بايثون (قد يكون ضرورياً إذا لم يتم اكتشافه تلقائياً) ---
# إذا واجهت مشاكل في العثور على Tesseract، قم بإلغاء التعليق عن السطر التالي
# وقم بتعيين المسار الصحيح لمجلد Tesseract-OCR الذي يحتوي على tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\ALWAFER\AppData\Local\Programs\Tesseract-OCR\tesseract.exe' # تأكد من تعديل هذا المسار حسب تثبيتك

# إخفاء تحذير InsecureRequestWarning عند تعطيل التحقق من SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# قائمة لتخزين جميع الفقرات النصية المستخلصة (من HTML و الصور)
all_extracted_text = []
# مجموعة لتتبع الروابط التي تمت زيارتها لتجنب التكرار
visited_urls = set()

def extract_text_from_image(image_url):
    """
    يقوم بتحميل صورة من عنوان URL ويستخلص النص منها باستخدام Tesseract OCR.
    """
    try:
        # تحميل الصورة
        img_response = requests.get(image_url, stream=True, timeout=10, verify=False)
        img_response.raise_for_status()

        # قراءة محتوى الصورة في الذاكرة وتحويلها إلى كائن Image
        image = Image.open(io.BytesIO(img_response.content))
        
        # تحويل الصورة إلى وضع أبيض وأسود أو تدرج رمادي لتحسين OCR إذا لزم الأمر
        # image = image.convert('L') # تدرج رمادي
        # image = image.convert('1') # أبيض وأسود

        # استخلاص النص باستخدام Tesseract OCR
        # lang='ara+eng' يخبر Tesseract بالبحث عن النص العربي والإنجليزي
        text = pytesseract.image_to_string(image, lang='ara+eng')
        
        # تنظيف النص المستخلص (إزالة المسافات الزائدة)
        text = text.strip()
        return text

    except requests.exceptions.RequestException as e:
        print(f"خطأ في تحميل الصورة {image_url}: {e}")
        return ""
    except pytesseract.TesseractNotFoundError:
        print("خطأ: Tesseract OCR غير موجود. تأكد من تثبيته وإضافته إلى PATH.")
        return ""
    except Exception as e:
        print(f"حدث خطأ أثناء معالجة الصورة {image_url}: {e}")
        return ""

def scrape_single_page_with_ocr(url):
    """
    يقوم بجمع الفقرات النصية من HTML والنصوص من الصور من صفحة ويب واحدة.
    """
    if url in visited_urls:
        return [] # تم زيارة هذه الصفحة من قبل

    print(f"جاري جمع المعلومات (بما في ذلك الصور) من: {url}")
    visited_urls.add(url)

    page_texts = []
    try:
        response = requests.get(url, timeout=15, verify=False) # زيادة المهلة قليلاً
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # استخلاص الفقرات النصية العادية
        for paragraph in soup.find_all('p'):
            text = paragraph.get_text(strip=True)
            if text:
                page_texts.append(text)

        # استخلاص النصوص من الصور
        for img_tag in soup.find_all('img'):
            img_src = img_tag.get('src')
            if img_src:
                full_img_url = urljoin(url, img_src)
                # يمكننا إضافة بعض المنطق هنا لتصفية الصور (مثلاً، تجاهل الأيقونات الصغيرة)
                # مثال: if not img_src.endswith(('.gif', '.ico')) and img_tag.get('width', 0) > 50:
                
                # يمكنك إضافة فحص إذا كانت الصورة تحتوي على نص مهم بناءً على السياق
                # مثلاً: إذا كانت الصورة داخل <div class="info-block">
                extracted_img_text = extract_text_from_image(full_img_url)
                if extracted_img_text:
                    page_texts.append(extracted_img_text)
                    print(f"  - تم استخلاص نص من صورة: {full_img_url[:60]}...") # لطباعة جزء من الرابط

        print(f"تم جمع معلومات من: {url} بنجاح!")
        return page_texts

    except requests.exceptions.Timeout:
        print(f"انتهت مهلة الاتصال عند {url}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"حدث خطأ أثناء الاتصال بالخادم عند {url}: {e}")
        return []
    except Exception as e:
        print(f"حدث خطأ غير متوقع عند {url}: {e}")
        return []

def crawl_university_website_with_ocr(start_urls, max_depth=1):
    """
    يزحف على صفحات موقع الجامعة ويستخلص النص من HTML والصور.
    """
    queue = [(url, 0) for url in start_urls]
    
    while queue:
        current_url, current_depth = queue.pop(0)

        if current_depth > max_depth:
            continue

        texts_from_page = scrape_single_page_with_ocr(current_url)
        all_extracted_text.extend(texts_from_page)

        # متابعة الروابط الداخلية لاستكشاف المزيد من الصفحات
        # (يمكنك تعديل هذا الجزء ليكون أكثر ذكاءً ويتبع فقط الروابط المهمة)
        if current_depth < max_depth:
            try:
                response = requests.get(current_url, timeout=5, verify=False)
                soup = BeautifulSoup(response.text, 'html.parser')
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if href and not href.startswith('#'):
                        full_url = urljoin(current_url, href)
                        if urlparse(full_url).netloc == urlparse(current_url).netloc and full_url not in visited_urls:
                            queue.append((full_url, current_depth + 1))
            except Exception as e:
                # print(f"خطأ في متابعة الروابط من {current_url}: {e}")
                pass # تجاهل أخطاء الروابط الثانوية هنا

# قائمة الروابط التي قدمتها سابقاً
initial_urls = [
    "https://shamuniversity.com",
    "https://shamuniversity.com/nav14", # كلية العلوم الصحية
    "https://shamuniversity.com/nav21", # كلية الاقتصاد والإدارة
    "https://shamuniversity.com/nav28", # كلية الهندسة
    "https://shamuniversity.com/nav29", # كلية التربية
    "https://shamuniversity.com/nav24", # كلية الشريعة والقانون
    "https://shamuniversity.com/nav25", # كلية العلوم السياسية
    "https://shamuniversity.com/nav15", # الهندسة الكيميائية
    "https://shamuniversity.com/nav36", # الهندسة الزراعية
    "https://shamuniversity.com/nav41", # عن الجامعة
    "https://shamuniversity.com/nav67", # مركز شام
    # يمكنك إضافة المزيد من الروابط الهامة هنا
    "https://shamuniversity.com/nav52",
    "https://shamuniversity.com/navnone",
    "https://shamuniversity.com/nav64"


]

print("بدء عملية الزحف واستخلاص النصوص من HTML والصور...")
# ابدأ بعمق 1 لزيارة الروابط الأولية فقط، ثم يمكنك زيادة العمق
crawl_university_website_with_ocr(initial_urls, max_depth=1) 

# تنظيف شامل للنصوص المجمعة (مثلما فعلنا سابقاً)
# (يمكنك نسخ دالة clean_text_data() من ملف clean_data.py هنا أو استيرادها)
def clean_text_data(texts):
    cleaned_unique_texts = set()
    unwanted_phrases = [
        "نهتم دوما بالاستماع إلى مقترحاتكم وآرائكم.",
        "Copyright ©جميع الحقوق محفوظة لجامعة الشام",
        "جامعة الشام",
        "Sham university",
        "المزيد",
        "Copyright ©جميع الحقوق محفوظة لمركز شام للدراسات والبحث العلمي",
        "Sham university"
    ]
    for text in texts:
        text = text.strip()
        for phrase in unwanted_phrases:
            text = text.replace(phrase, "")
        text = re.sub(r'[^\u0600-\u06FF\sA-Za-z0-9\.\,]', '', text) # الاحتفاظ بالأرقام وعلامات الترقيم الأساسية
        text = re.sub(r'\s+', ' ', text).strip()
        if text and len(text) > 10: # زيادة الطول الأدنى للفقرة
            cleaned_unique_texts.add(text)
    return list(cleaned_unique_texts)

import re # استيراد re لدالة التنظيف

final_cleaned_texts = clean_text_data(all_extracted_text)

# حفظ النصوص المستخلصة في ملف جديد
output_file_with_ocr = "university_texts_with_ocr.txt"
with open(output_file_with_ocr, "w", encoding="utf-8") as f:
    for text_item in final_cleaned_texts:
        f.write(text_item + "\n")
print(f"\nتم جمع وحفظ النصوص المستخلصة (بما في ذلك من الصور) في الملف: {output_file_with_ocr}")

# ملاحظة: بعد هذه الخطوة، ستحتاج إلى إعادة بناء قاعدة بيانات المتجهات
# باستخدام النصوص الجديدة من 'university_texts_with_ocr.txt'
# ثم ستحتاج إلى تحديث ملف الـ FAQ 'university_faq_qa.txt' يدوياً بمساعدة Gemini
# ثم إعادة بناء قاعدة بيانات المتجهات لـ FAQ
# ثم تشغيل الشات بوت.