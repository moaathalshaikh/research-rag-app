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
        
        # محددات خاصة لمواقع مختلفة
        self.site_specific_selectors = {
            "stackexchange.com": [".question-page #question .post-text", ".question-page .answer .post-text"],
            "stackoverflow.com": [".question-page #question .post-text", ".question-page .answer .post-text"],
            "serverfault.com": [".question-page #question .post-text", ".question-page .answer .post-text"],
            "superuser.com": [".question-page #question .post-text", ".question-page .answer .post-text"],
            "askubuntu.com": [".question-page #question .post-text", ".question-page .answer .post-text"],
            "pm.stackexchange.com": [".question .s-prose", ".answer .s-prose", ".postcell", ".answercell .post-text", "#question .post-text", "#answers .post-text"]
        }
    
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
            text = self._extract_clean_text(soup, url)
            
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
            response = requests.get(url, headers=self.headers, timeout=15)
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
    
    def _is_stack_exchange(self, url):
        """التحقق مما إذا كان الرابط ينتمي إلى مواقع Stack Exchange"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        # التحقق من النطاقات المعروفة لـ Stack Exchange
        stack_domains = list(self.site_specific_selectors.keys())
        
        for stack_domain in stack_domains:
            if stack_domain in domain:
                return True, stack_domain
                
        # التحقق من النطاقات الفرعية لـ stackexchange.com
        if domain.endswith('stackexchange.com'):
            return True, 'stackexchange.com'
            
        return False, None
    
    def _extract_clean_text(self, soup, url):
        """استخراج وتنظيف النص من المحتوى"""
        # التحقق مما إذا كان الموقع من مواقع Stack Exchange
        is_stack, stack_domain = self._is_stack_exchange(url)
        
        if is_stack:
            return self._extract_stack_exchange_text(soup, stack_domain)
        
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
    
    def _extract_stack_exchange_text(self, soup, domain):
        """استخراج النص من مواقع Stack Exchange"""
        logger.info(f"استخراج النص من موقع Stack Exchange: {domain}")
        
        # الحصول على المحددات الخاصة بالموقع
        selectors = self.site_specific_selectors.get(domain, self.site_specific_selectors['stackexchange.com'])
        
        # جمع النص من جميع المحددات
        text_parts = []
        
        # إضافة عنوان السؤال
        title = soup.select_one('h1')
        if title:
            text_parts.append(f"العنوان: {title.get_text(strip=True)}\n\n")
        
        # استخراج نص السؤال والإجابات
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                for element in elements:
                    # تنظيف العنصر من الأكواد البرمجية والمكونات غير النصية
                    for code in element.select('pre, code'):
                        code.extract()
                    
                    text = element.get_text(separator=' ', strip=True)
                    if text:
                        text_parts.append(text)
        
        # دمج النصوص المستخرجة
        combined_text = "\n\n".join(text_parts)
        
        # تنظيف النص
        clean_text = self._clean_text(combined_text)
        
        return clean_text
    
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
    test_url = "https://pm.stackexchange.com/questions/11144/constantly-under-estimating-user-stories"
    print(extract_text_from_url(test_url))
