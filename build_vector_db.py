# import os
# from langchain_community.vectorstores import FAISS
# from langchain_cohere import CohereEmbeddings
# from langchain.text_splitter import RecursiveCharacterTextSplitter

# # 1. تأكد من أن مفتاح API الخاص بـ Cohere موجود كمتغير بيئة
# # إذا لم يكن موجودًا، سيتم رفع خطأ
# if "COHERE_API_KEY" not in os.environ:
#     print("خطأ: متغير البيئة 'COHERE_API_KEY' غير موجود.")
#     print("يرجى تعيينه قبل تشغيل الكود (مثال: $env:COHERE_API_KEY = 'Your_Key' في PowerShell).")
#     exit()

# # 2. تحميل الفقرات النظيفة من الملف
# cleaned_file_path = "cleaned_university_paragraphs.txt"
# try:
#     with open(cleaned_file_path, "r", encoding="utf-8") as f:
#         # قراءة كل سطر كفقرة منفصلة
#         text_content = f.read().splitlines()
#     # تصفية أي أسطر فارغة قد تكون موجودة بعد القراءة
#     documents = [doc.strip() for doc in text_content if doc.strip()]
#     print(f"تم قراءة {len(documents)} فقرة نظيفة من الملف '{cleaned_file_path}'.")
# except FileNotFoundError:
#     print(f"خطأ: ملف '{cleaned_file_path}' غير موجود. يرجى التأكد من تشغيل كود التنظيف أولاً.")
#     documents = []

# if not documents:
#     print("لا توجد بيانات لمعالجتها. يرجى التأكد من أن ملف الفقرات النظيفة غير فارغ.")
#     exit()

# # 3. تقسيم النصوص إلى أجزاء (Chunks)
# # هذا مهم لأن نماذج اللغة الكبيرة لها حدود لعدد الرموز التي يمكن معالجتها.
# # سنقوم بتقسيم النصوص الكبيرة إلى أجزاء أصغر.
# # chunk_size: أقصى عدد من الأحرف في كل جزء.
# # chunk_overlap: عدد الأحرف المتداخلة بين الأجزاء المتتالية للمساعدة في الحفاظ على السياق.
# text_splitter = RecursiveCharacterTextSplitter(
#     chunk_size=500,  # يمكن تعديل هذا الرقم بناءً على طول الفقرات لديك
#     chunk_overlap=50, # يمكن تعديل هذا الرقم
#     length_function=len,
# )

# # يمكن استخدام `create_documents` إذا كانت الفقرات طويلة جداً وتفضل تقسيمها
# # في هذه الحالة، الفقرات لدينا هي بالفعل "مستندات" فردية
# # chunks = text_splitter.create_documents(documents)
# # بما أن فقراتنا قد تكون قصيرة بما يكفي، يمكننا معالجتها مباشرة كـ "مستندات"
# # أو التأكد من أنها ليست قصيرة جداً (نصفي الشرط على len(text)>5 في التنظيف)

# # إذا كانت documents هي قائمة سلاسل نصية مباشرة (فقرات)، نحتاج إلى تحويلها إلى كائنات Document لـ LangChain
# from langchain_core.documents import Document
# langchain_documents = [Document(page_content=d) for d in documents]

# # الآن نقسم هذه المستندات إلى أجزاء
# chunks = text_splitter.split_documents(langchain_documents)

# print(f"تم تقسيم النصوص إلى {len(chunks)} جزءًا (chunk).")

# # 4. إنشاء تضمينات (Embeddings) باستخدام Cohere
# # ستقوم CohereEmbeddings بتحويل كل جزء نصي إلى متجه رقمي (قائمة من الأرقام)
# # يمثل المعنى الدلالي للنص.
# print("جاري إنشاء تضمينات (embeddings) للنصوص باستخدام Cohere. قد يستغرق هذا بعض الوقت...")
# # embeddings = CohereEmbeddings(model="embed-multilingual-v3.0")
# embeddings = CohereEmbeddings(model="embed-english-v2.0")



# # 5. بناء قاعدة بيانات المتجهات (Vector Database) باستخدام FAISS
# # FAISS هي مكتبة كفاءة للبحث عن التشابه في المتجهات.
# # DocArrayInMemorySearch هي قاعدة بيانات متجهات بسيطة تعيش في الذاكرة ومفيدة للاختبار.
# # FAISS.from_documents() تقوم بإنشاء التضمينات وتخزينها في قاعدة البيانات.
# try:
#     # يمكننا استخدام FAISS.from_documents مباشرة إذا كانت chunks هي قائمة بكائنات Document
#     vector_db = FAISS.from_documents(chunks, embeddings)
#     print("تم بناء قاعدة بيانات المتجهات بنجاح!")

#     # 6. حفظ قاعدة بيانات المتجهات (اختياري ولكن موصى به لتجنب إعادة البناء في كل مرة)
#     # هذا يحفظ قاعدة البيانات إلى القرص، بحيث يمكنك تحميلها لاحقاً دون الحاجة لإعادة إنشاء التضمينات.
#     vector_db_path = "faiss_university_db"
#     vector_db.save_local(vector_db_path)
#     print(f"تم حفظ قاعدة بيانات المتجهات محلياً في: {vector_db_path}")

#     print("\nأصبحت قاعدة بيانات المتجهات جاهزة للاستعلامات!")

# except Exception as e:
#     print(f"حدث خطأ أثناء بناء قاعدة بيانات المتجهات: {e}")
#     print("الرجاء التأكد من أن مفتاح API الخاص بـ Cohere صحيح ويعمل.")






##################################################################################
# import os
# from langchain_community.vectorstores import FAISS
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_core.documents import Document

# import urllib3
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# # 2. تحميل الفقرات النظيفة من الملف
# cleaned_file_path = "cleaned_university_paragraphs.txt"
# try:
#     with open(cleaned_file_path, "r", encoding="utf-8") as f:
#         text_content = f.read().splitlines()
#     documents = [doc.strip() for doc in text_content if doc.strip()]
#     print(f"تم قراءة {len(documents)} فقرة نظيفة من الملف '{cleaned_file_path}'.")
# except FileNotFoundError:
#     print(f"خطأ: ملف '{cleaned_file_path}' غير موجود. يرجى التأكد من تشغيل كود التنظيف أولاً.")
#     documents = []

# if not documents:
#     print("لا توجد بيانات لمعالجتها. يرجى التأكد من أن ملف الفقرات النظيفة غير فارغ.")
#     exit()

# # 3. تقسيم النصوص إلى أجزاء (Chunks)
# text_splitter = RecursiveCharacterTextSplitter(
#     chunk_size=500,
#     chunk_overlap=50,
#     length_function=len,
# )

# langchain_documents = [Document(page_content=d) for d in documents]
# chunks = text_splitter.split_documents(langchain_documents)

# print(f"تم تقسيم النصوص إلى {len(chunks)} جزءًا (chunk).")

# # 4. إنشاء تضمينات (Embeddings) باستخدام Hugging Face Model
# print("جاري إنشاء تضمينات (embeddings) للنصوص باستخدام نموذج Hugging Face. قد يستغرق هذا بعض الوقت...")
# # تم تغيير اسم النموذج هنا
# model_name = "sentence-transformers/distiluse-base-multilingual-cased-v1"
# embeddings = HuggingFaceEmbeddings(model_name=model_name)

# # 5. بناء قاعدة بيانات المتجهات (Vector Database) باستخدام FAISS
# try:
#     vector_db = FAISS.from_documents(chunks, embeddings)
#     print("تم بناء قاعدة بيانات المتجهات بنجاح!")

#     # 6. حفظ قاعدة بيانات المتجهات (اختياري ولكن موصى به لتجنب إعادة البناء في كل مرة)
#     vector_db_path = "faiss_university_db"
#     vector_db.save_local(vector_db_path)
#     print(f"تم حفظ قاعدة بيانات المتجهات محلياً في: {vector_db_path}")

#     print("\nأصبحت قاعدة بيانات المتجهات جاهزة للاستعلامات!")

# except Exception as e:
#     print(f"حدث خطأ أثناء بناء قاعدة بيانات المتجهات: {e}")
#     print("الرجاء التأكد من أن نموذج التضمين يمكن تحميله ويعمل بشكل صحيح.")


######################################
import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 1. تحميل أزواج الأسئلة والأجوبة من ملف الـ FAQ الجديد
faq_file_path = "university_faq_qa.txt" # اسم ملف الـ FAQ الجديد
qa_documents = []
try:
    with open(faq_file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
        # تقسيم المحتوى إلى أزواج سؤال-جواب باستخدام الفاصل "---"
        entries = content.split("---")
        for entry in entries:
            entry = entry.strip()
            if entry:
                lines = entry.split('\n')
                if len(lines) >= 2:
                    question = lines[0].strip().replace("س:", "").strip()
                    answer = lines[1].strip().replace("ج:", "").strip()
                    if question and answer:
                        # ننشئ Document حيث الـ page_content هو السؤال (ليتم تضمينه)
                        # ونخزن الإجابة في metadata لسهولة الاسترجاع
                        qa_documents.append(Document(page_content=question, metadata={"answer": answer, "type": "qa_pair"}))
    print(f"تم قراءة {len(qa_documents)} زوج سؤال-جواب من الملف '{faq_file_path}'.")
except FileNotFoundError:
    print(f"خطأ: ملف '{faq_file_path}' غير موجود. يرجى إنشاءه أولاً.")
    qa_documents = []

if not qa_documents:
    print("لا توجد بيانات أسئلة وأجوبة لمعالجتها. يرجى التأكد من أن ملف الـ FAQ غير فارغ.")
    exit()

# 2. تقسيم النصوص إلى أجزاء (Chunks)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,  # حجم صغير لأننا نتعامل مع أسئلة
    chunk_overlap=10,
    length_function=len,
)

chunks = text_splitter.split_documents(qa_documents)

print(f"تم تقسيم النصوص إلى {len(chunks)} جزءًا (chunk).")

# 3. إنشاء تضمينات (Embeddings) باستخدام Hugging Face Model
print("جاري إنشاء تضمينات (embeddings) للنصوص باستخدام نموذج Hugging Face. قد يستغرق هذا بعض الوقت...")
model_name = "sentence-transformers/distiluse-base-multilingual-cased-v1"
embeddings = HuggingFaceEmbeddings(model_name=model_name)

# 4. بناء قاعدة بيانات المتجهات (Vector Database) باستخدام FAISS
try:
    vector_db = FAISS.from_documents(chunks, embeddings)
    print("تم بناء قاعدة بيانات المتجهات بنجاح!")

    # 5. حفظ قاعدة بيانات المتجهات (في مسار جديد لتمييزها)
    vector_db_path_qa = "faiss_university_qa_db" 
    vector_db.save_local(vector_db_path_qa)
    print(f"تم حفظ قاعدة بيانات المتجهات محلياً في: {vector_db_path_qa}")

    print("\nأصبحت قاعدة بيانات المتجهات للأسئلة والأجوبة جاهزة للاستعلامات!")

except Exception as e:
    print(f"حدث خطأ أثناء بناء قاعدة بيانات المتجهات: {e}")
    print("الرجاء التأكد من أن نموذج التضمين يمكن تحميله ويعمل بشكل صحيح.")