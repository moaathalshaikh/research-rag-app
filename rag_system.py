"""
وحدة نظام RAG (Retrieval Augmented Generation)
هذا الملف يحتوي على وظائف متقدمة لتنفيذ نظام RAG مع Gemini API
"""

import os
import google.generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging
from dotenv import load_dotenv

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# تحميل المتغيرات البيئية
load_dotenv()

# الحصول على مفتاح API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# تهيئة Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

class RAGSystem:
    """فئة لتنفيذ نظام RAG مع Gemini API"""
    
    def __init__(self, api_key=None):
        """تهيئة نظام RAG مع إعدادات اختيارية"""
        self.api_key = api_key or GOOGLE_API_KEY
        self.chunks = []
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # التحقق من وجود مفتاح API
        if not self.api_key:
            logger.warning("لم يتم تعيين مفتاح API لـ Google Gemini. يرجى تعيينه في ملف .env")
    
    def create_knowledge_base(self, text):
        """إنشاء قاعدة معرفة من النص"""
        try:
            logger.info("بدء إنشاء قاعدة المعرفة")
            
            # التحقق من النص
            if not text or len(text.strip()) < 100:
                logger.warning("النص قصير جدًا أو فارغ")
                return False
            
            # تقسيم النص إلى أجزاء
            self.chunks = self.text_splitter.split_text(text)
            logger.info(f"تم تقسيم النص إلى {len(self.chunks)} جزء")
            
            # تخزين الأجزاء مباشرة بدلاً من استخدام قاعدة معرفة متجهية
            logger.info("تم تخزين أجزاء النص بنجاح")
            
            return True
        except Exception as e:
            logger.error(f"حدث خطأ أثناء إنشاء قاعدة المعرفة: {str(e)}")
            return False
    
    def answer_question(self, question):
        """الإجابة على سؤال باستخدام RAG"""
        try:
            # التحقق من وجود قاعدة المعرفة
            if not hasattr(self, 'chunks') or not self.chunks:
                return "يرجى إنشاء قاعدة المعرفة أولاً باستخدام النص المستخرج."
            
            # التحقق من وجود مفتاح API
            if not self.api_key:
                return "يرجى تعيين مفتاح API لـ Google Gemini في ملف .env"
            
            # التحقق من السؤال
            if not question or len(question.strip()) < 3:
                return "يرجى إدخال سؤال صحيح."
            
            logger.info(f"معالجة السؤال: {question}")
            
            # استخدام Gemini API مباشرة
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            # بدلاً من البحث المتجهي، نستخدم جميع الأجزاء كسياق
            # يمكن تحسين هذا لاحقًا باستخدام بحث نصي بسيط
            context = "\n\n".join(self.chunks[:5])  # استخدام أول 5 أجزاء فقط لتجنب تجاوز حدود السياق
            
            # إنشاء سلسلة الاستعلام باستخدام Gemini مباشرة
            prompt = f"""
            أنت مساعد بحثي ذكي. استخدم المعلومات المقدمة فقط للإجابة على السؤال.
            إذا لم تكن المعلومات كافية للإجابة، قل "لا أستطيع الإجابة على هذا السؤال بناءً على المعلومات المتاحة."
            لا تختلق معلومات أو تستخدم معرفتك الخارجية.
            
            المعلومات المتاحة:
            {context}
            
            السؤال: {question}
            
            الإجابة:
            """
            
            # استدعاء النموذج
            response = model.generate_content(prompt)
            
            logger.info("تم الحصول على الإجابة بنجاح")
            
            return response.text
        except Exception as e:
            error_msg = f"حدث خطأ أثناء الإجابة على السؤال: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def batch_answer_questions(self, questions):
        """الإجابة على مجموعة من الأسئلة"""
        answers = []
        for question in questions:
            answer = self.answer_question(question)
            answers.append({"question": question, "answer": answer})
        return answers

# استخدام الفئة
def create_rag_system():
    """دالة مساعدة لإنشاء نظام RAG"""
    return RAGSystem()

# اختبار الوحدة إذا تم تشغيل الملف مباشرة
if __name__ == "__main__":
    # إنشاء نظام RAG
    rag_system = create_rag_system()
    
    # نص اختبار
    test_text = """
    الذكاء الاصطناعي هو فرع من فروع علوم الحاسوب يهتم بأتمتة السلوك الذكي. 
    يشير الذكاء الاصطناعي إلى الأنظمة أو الآلات التي تحاكي الذكاء البشري لأداء المهام، 
    ويمكن أن تحسن نفسها تدريجيًا بناءً على المعلومات التي تجمعها.
    
    يتضمن الذكاء الاصطناعي العديد من التقنيات مثل التعلم الآلي والتعلم العميق ومعالجة اللغة الطبيعية.
    تستخدم هذه التقنيات في العديد من التطبيقات مثل الروبوتات والسيارات ذاتية القيادة والمساعدين الافتراضيين.
    """
    
    # إنشاء قاعدة المعرفة
    rag_system.create_knowledge_base(test_text)
    
    # اختبار الإجابة على سؤال
    question = "ما هو الذكاء الاصطناعي؟"
    answer = rag_system.answer_question(question)
    
    print(f"السؤال: {question}")
    print(f"الإجابة: {answer}")
