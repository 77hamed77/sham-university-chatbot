# import requests
# from bs4 import BeautifulSoup

# def scrape_university_website(url):
#     """
#     يقوم بجمع الروابط والفقرات النصية من صفحة ويب معينة.

#     المعلمات:
#     url (str): عنوان URL للصفحة التي سيتم جمع المعلومات منها.

#     النتائج:
#     tuple: يحتوي على قائمتين (list) - الأولى للروابط المستخرجة والثانية للفقرات النصية.
#     """
#     print(f"جاري جمع المعلومات من: {url}")
#     try:
#         # إرسال طلب للحصول على محتوى الصفحة
#         response = requests.get(url)
#         # التأكد من أن الطلب كان ناجحاً (رمز الحالة 200)
#         response.raise_for_status()

#         # تحليل محتوى الصفحة باستخدام BeautifulSoup
#         soup = BeautifulSoup(response.text, 'html.parser')

#         # قائمة لتخزين الروابط
#         extracted_links = []
#         # البحث عن جميع وسوم 'a' (الروابط)
#         for link in soup.find_all('a', href=True):
#             href = link['href']
#             # التأكد من أن الرابط ليس فارغاً
#             if href:
#                 # إذا كان الرابط نسبياً، اجعله كاملاً
#                 if not href.startswith(('http://', 'https://', 'mailto:')):
#                     href = requests.compat.urljoin(url, href)
#                 extracted_links.append(href)

#         # قائمة لتخزين الفقرات النصية
#         extracted_paragraphs = []
#         # البحث عن جميع وسوم 'p' (الفقرات)
#         for paragraph in soup.find_all('p'):
#             text = paragraph.get_text(strip=True)
#             if text:
#                 extracted_paragraphs.append(text)

#         print("تم جمع المعلومات بنجاح!")
#         return extracted_links, extracted_paragraphs

#     except requests.exceptions.RequestException as e:
#         print(f"حدث خطأ أثناء الاتصال بالخادم: {e}")
#         return [], []
#     except Exception as e:
#         print(f"حدث خطأ غير متوقع: {e}")
#         return [], []

# # عنوان URL لموقع جامعة الشام
# university_url = "https://shamuniversity.com/"

# # استدعاء الدالة لجمع المعلومات
# links, paragraphs = scrape_university_website(university_url)

# # طباعة الروابط والفقرات المستخرجة
# print("\n--- الروابط المستخرجة ---")
# for i, link in enumerate(links[:20]): # نطبع أول 20 رابط لتجنب الإطالة
#     print(f"{i+1}. {link}")

# print("\n--- الفقرات النصية المستخرجة ---")
# for i, paragraph in enumerate(paragraphs[:10]): # نطبع أول 10 فقرات لتجنب الإطالة
#     print(f"{i+1}. {paragraph}")

# # ملاحظة: يمكنك حفظ هذه البيانات في ملف لاحقاً
# # مثال: حفظ الفقرات في ملف نصي
# # with open("university_paragraphs.txt", "w", encoding="utf-8") as f:
# #     for p in paragraphs:
# #         f.write(p + "\n")

###########################################################################################################

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import urllib3 # لإخفاء تحذير عدم التحقق من SSL

# إخفاء تحذير InsecureRequestWarning عند تعطيل التحقق من SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# قائمة لتخزين جميع الفقرات النصية من جميع الصفحات
all_extracted_paragraphs = []
# مجموعة لتتبع الروابط التي تمت زيارتها لتجنب التكرار
visited_urls = set()

def scrape_single_page(url):
    """
    يقوم بجمع الروابط والفقرات النصية من صفحة ويب واحدة.

    المعلمات:
    url (str): عنوان URL للصفحة التي سيتم جمع المعلومات منها.

    النتائج:
    tuple: يحتوي على قائمتين (list) - الأولى للروابط المستخرجة من هذه الصفحة والثانية للفقرات النصية.
    """
    if url in visited_urls:
        return [], [] # تم زيارة هذه الصفحة من قبل

    print(f"جاري جمع المعلومات من: {url}")
    visited_urls.add(url) # إضافة URL إلى قائمة الصفحات التي تمت زيارتها

    try:
        # !!! التعديل هنا: إضافة verify=False لتجاهل مشاكل شهادة SSL !!!
        response = requests.get(url, timeout=10, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        page_links = []
        # البحث عن جميع وسوم 'a' (الروابط)
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href:
                # التأكد من أن الرابط كامل وليس مجرد #anchor
                if not href.startswith('#'):
                    # تحويل الروابط النسبية إلى روابط مطلقة
                    full_url = urljoin(url, href)
                    # التأكد من أن الرابط ينتمي إلى نفس النطاق (domain)
                    if urlparse(full_url).netloc == urlparse(url).netloc:
                        page_links.append(full_url)

        page_paragraphs = []
        # البحث عن جميع وسوم 'p' (الفقرات)
        for paragraph in soup.find_all('p'):
            text = paragraph.get_text(strip=True)
            if text:
                page_paragraphs.append(text)

        print(f"تم جمع معلومات من: {url} بنجاح!")
        return page_links, page_paragraphs

    except requests.exceptions.Timeout:
        print(f"انتهت مهلة الاتصال عند {url}")
        return [], []
    except requests.exceptions.RequestException as e:
        print(f"حدث خطأ أثناء الاتصال بالخادم عند {url}: {e}")
        return [], []
    except Exception as e:
        print(f"حدث خطأ غير متوقع عند {url}: {e}")
        return [], []

def crawl_university_website(start_urls, max_depth=1):
    """
    يزحف على صفحات موقع الجامعة بدءًا من قائمة عناوين URL محددة.

    المعلمات:
    start_urls (list): قائمة بعناوين URL التي سيتم البدء بالزحف منها.
    max_depth (int): أقصى عمق للزحف (كم عدد طبقات الروابط التي يجب متابعتها).
                     قيمة 1 تعني فقط الصفحات الأولية المقدمة.
                     قيمة 2 تعني الصفحات الأولية والروابط الموجودة فيها.
    """
    queue = [(url, 0) for url in start_urls] # قائمة انتظار (URL, depth)
    
    while queue:
        current_url, current_depth = queue.pop(0) # استخراج أول عنصر

        # إذا تجاوزنا أقصى عمق، نتخطى هذه الصفحة
        if current_depth > max_depth:
            continue

        # جمع المعلومات من الصفحة الحالية
        links_from_page, paragraphs_from_page = scrape_single_page(current_url)
        all_extracted_paragraphs.extend(paragraphs_from_page)

        # إضافة الروابط الجديدة التي لم تتم زيارتها بعد إلى قائمة الانتظار
        if current_depth < max_depth:
            for link in links_from_page:
                if link not in visited_urls:
                    queue.append((link, current_depth + 1))

# قائمة الروابط التي قدمتها
initial_urls = [
    "https://shamuniversity.com",
    "https://shamuniversity.com/nav14",
    "https://shamuniversity.com/nav21",
    "https://shamuniversity.com/nav28",
    "https://shamuniversity.com/nav29",
    "https://shamuniversity.com/nav24",
    "https://shamuniversity.com/nav25",
    "https://shamuniversity.com/nav15",
    "https://shamuniversity.com/nav36",
    "https://shamuniversity.com/nav41",
    "https://shamuniversity.com/nav67"
]

# بدء عملية الزحف بعمق 1 (يزور فقط الروابط الأولية التي قدمتها)
crawl_university_website(initial_urls, max_depth=1)

# طباعة جميع الفقرات النصية التي تم جمعها من كل الصفحات
print("\n--- جميع الفقرات النصية المستخرجة من جميع الصفحات ---")
for i, paragraph in enumerate(all_extracted_paragraphs):
    print(f"{i+1}. {paragraph}")

# ملاحظة: لحفظ هذه البيانات في ملف، يمكنك استخدام الكود التالي:
output_file = "all_university_paragraphs.txt"
with open(output_file, "w", encoding="utf-8") as f:
    for p in all_extracted_paragraphs:
        f.write(p + "\n")
print(f"\nتم حفظ جميع الفقرات في الملف: {output_file}")
