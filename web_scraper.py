"""
وحدة استخراج النصوص من الويب
هذا الملف يحتوي على وظائف متقدمة لاستخراج النصوص من صفحات الويب
"""

import requests
from bs4 import BeautifulSoup, Comment
import re
import logging
from urllib.parse import urlparse

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebScraper:
    """فئة لاستخراج النصوص من صفحات الويب"""
    
    def __init__(self, user_agent=None):
        """تهيئة المستخرج مع إعدادات اختيارية"""
        self.headers = {
            'User-Agent': user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.unwanted_tags = [
            "script", "style", "meta", "noscript", "header", "footer", 
            "aside", "nav", "iframe", "svg", "button", "form", "input"
        ]
        self.content_tags = ["p", "h1", "h2", "h3", "h4", "h5", "h6", "article", "section", "main", "div.content", "div.article"]
    
    def extract_text(self, url):
        """استخراج النص من رابط URL"""
        try:
            logger.info(f"بدء استخراج النص من: {url}")
            
            # التحقق من صحة الرابط
            if not self._validate_url(url):
                return "رابط URL غير صالح. يرجى التأكد من إدخال رابط كامل يبدأ بـ http:// أو https://"
            
            # الحصول على محتوى الصفحة
            response = self._get_page_content(url)
            if isinstance(response, str):  # إذا كانت هناك رسالة خطأ
                return response
            
            # تحليل المحتوى
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # إزالة العناصر غير المرغوب فيها
            self._remove_unwanted_elements(soup)
            
            # استخراج النص
            text = self._extract_clean_text(soup)
            
            logger.info(f"تم استخراج {len(text)} حرف من النص")
            return text
            
        except Exception as e:
            error_msg = f"حدث خطأ أثناء استخراج النص: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def _validate_url(self, url):
        """التحقق من صحة رابط URL"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
        except:
            return False
    
    def _get_page_content(self, url):
        """الحصول على محتوى الصفحة مع معالجة الأخطاء"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            return f"خطأ HTTP: {e}"
        except requests.exceptions.ConnectionError:
            return "خطأ في الاتصال: تعذر الاتصال بالخادم"
        except requests.exceptions.Timeout:
            return "انتهت مهلة الاتصال: استغرق الخادم وقتًا طويلاً للرد"
        except requests.exceptions.RequestException as e:
            return f"خطأ في الطلب: {e}"
    
    def _remove_unwanted_elements(self, soup):
        """إزالة العناصر غير المرغوب فيها من المحتوى"""
        # إزالة التعليقات
        for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
            comment.extract()
        
        # إزالة العناصر غير المرغوب فيها
        for tag in self.unwanted_tags:
            for element in soup.select(tag):
                element.extract()
    
    def _extract_clean_text(self, soup):
        """استخراج وتنظيف النص من المحتوى"""
        # محاولة استخراج المحتوى الرئيسي أولاً
        main_content = None
        for selector in ["article", "main", ".content", ".article", "#content", "#main"]:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        # إذا لم يتم العثور على محتوى رئيسي، استخدم كامل المستند
        content_soup = main_content if main_content else soup
        
        # استخراج النص
        text = content_soup.get_text(separator=' ', strip=True)
        
        # تنظيف النص
        text = self._clean_text(text)
        
        return text
    
    def _clean_text(self, text):
        """تنظيف النص المستخرج"""
        # إزالة المسافات المتعددة
        text = re.sub(r'\s+', ' ', text)
        
        # إزالة الأسطر الفارغة المتعددة
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # إزالة الأحرف الخاصة غير المرغوب فيها
        text = re.sub(r'[^\w\s\.,;:!?()\[\]{}«»""\'\-]', '', text)
        
        # تنظيم علامات الترقيم
        text = re.sub(r'\s([.,;:!?])', r'\1', text)
        
        return text.strip()

# استخدام الفئة
def extract_text_from_url(url):
    """دالة مساعدة لاستخراج النص من رابط URL"""
    scraper = WebScraper()
    return scraper.extract_text(url)

# اختبار الوحدة إذا تم تشغيل الملف مباشرة
if __name__ == "__main__":
    test_url = "https://ar.wikipedia.org/wiki/الذكاء_الاصطناعي"
    print(extract_text_from_url(test_url))
