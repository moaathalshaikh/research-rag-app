# نظام البحث باستخدام RAG

نظام بحثي متقدم يستخدم تقنية RAG (Retrieval Augmented Generation) للإجابة على الأسئلة البحثية بناءً على محتوى مستخرج من روابط الإنترنت.

## الميزات الرئيسية

- استخراج النص من روابط الإنترنت بشكل آلي
- تقسيم النص إلى أجزاء وإنشاء قاعدة معرفة
- الإجابة على الأسئلة البحثية باستخدام تقنية RAG مع Gemini API
- دعم إضافة عدد غير محدود من الأسئلة البحثية
- تصدير النتائج بتنسيقات متعددة (TXT، CSV، JSON)
- واجهة مستخدم سهلة الاستخدام وتدعم اللغة العربية بالكامل

## متطلبات النظام

- Python 3.8+
- Flask
- Google Generative AI API
- LangChain
- BeautifulSoup4
- متطلبات أخرى موجودة في ملف `requirements.txt`

## التثبيت

1. استنساخ المستودع:
```bash
git clone https://github.com/moaathalshaikh/research-rag-app.git
cd research-rag-app
```

2. إنشاء بيئة افتراضية وتفعيلها:
```bash
python -m venv venv
source venv/bin/activate  # لينكس/ماك
# أو
venv\Scripts\activate  # ويندوز
```

3. تثبيت المتطلبات:
```bash
pip install -r requirements.txt
```

4. إعداد ملف `.env` مع مفتاح API الخاص بـ Google Gemini:
```
GOOGLE_API_KEY=your_api_key_here
```

## طريقة الاستخدام

1. تشغيل التطبيق:
```bash
python app.py
```

2. فتح المتصفح على العنوان: `http://localhost:5000`

3. استخدام النظام:
   - أدخل رابط الإنترنت لاستخراج النص منه
   - أضف أسئلتك البحثية
   - احصل على إجابات مستندة إلى النص المستخرج
   - صدّر النتائج بالتنسيق المطلوب

## الهيكل العام للمشروع

```
research-rag-app/
├── app.py                  # تطبيق Flask الرئيسي
├── web_scraper.py          # مكون استخراج النصوص من الويب
├── rag_system.py           # نظام RAG للإجابة على الأسئلة
├── requirements.txt        # متطلبات المشروع
├── .env                    # ملف المتغيرات البيئية
├── static/                 # الملفات الثابتة
│   ├── css/                # ملفات CSS
│   │   └── style.css       # أنماط التطبيق
│   └── js/                 # ملفات JavaScript
│       └── main.js         # سكربت التطبيق الرئيسي
├── templates/              # قوالب HTML
│   └── index.html          # الصفحة الرئيسية
└── temp_data/              # مجلد للبيانات المؤقتة
```

## كيفية المساهمة

1. قم بعمل Fork للمشروع
2. أنشئ فرع جديد للميزة التي تريد إضافتها (`git checkout -b feature/amazing-feature`)
3. قم بإجراء التغييرات وحفظها (`git commit -m 'إضافة ميزة رائعة'`)
4. ارفع التغييرات إلى الفرع الخاص بك (`git push origin feature/amazing-feature`)
5. افتح طلب سحب (Pull Request)

## الترخيص

هذا المشروع مرخص تحت رخصة MIT - انظر ملف [LICENSE](LICENSE) للتفاصيل.

## المطور

- [معاذ الشيخ](https://github.com/moaathalshaikh)
