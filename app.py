import os
from flask import Flask, render_template, request, jsonify, send_file
import google.generativeai as genai
from dotenv import load_dotenv
import pandas as pd
import json
from datetime import datetime
import time

# تحميل المتغيرات البيئية
load_dotenv()

# إعداد تطبيق Flask
app = Flask(__name__)

# إعداد Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
genai.configure(api_key=GOOGLE_API_KEY)

# مجلد للبيانات المؤقتة
os.makedirs("temp_data", exist_ok=True)

# استيراد مكون استخراج النصوص
from web_scraper import extract_text_from_url

# استيراد نظام RAG
from rag_system import RAGSystem, create_rag_system

# إنشاء نظام RAG
rag_system = create_rag_system()

# المسارات
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract():
    try:
        url = request.form.get('url')
        if not url:
            return jsonify({'error': 'الرجاء إدخال رابط صحيح'}), 400
        
        # استخراج النص من الرابط
        text = extract_text_from_url(url)
        
        if not text:
            return jsonify({'error': 'لم يتم العثور على نص في الرابط المحدد'}), 400
        
        return jsonify({'text': text})
    except Exception as e:
        app.logger.error(f"خطأ في استخراج النص: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/save_text', methods=['POST'])
def save_text():
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'لا يوجد نص للحفظ'}), 400
        
        # إنشاء اسم ملف فريد
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"extracted_text_{timestamp}.txt"
        filepath = os.path.join('temp_data', filename)
        
        # حفظ النص في ملف
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        
        return jsonify({'filename': filename})
    except Exception as e:
        app.logger.error(f"خطأ في حفظ النص: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/answer', methods=['POST'])
def answer():
    try:
        data = request.get_json()
        questions = data.get('questions', [])
        text = data.get('text', '')
        
        if not questions:
            return jsonify({'error': 'الرجاء إدخال سؤال واحد على الأقل'}), 400
            
        if not text:
            return jsonify({'error': 'لا يوجد نص للتحليل'}), 400
        
        # الإجابة على الأسئلة باستخدام نظام RAG
        answers = []
        for question in questions:
            answer = rag_system.answer_question(question, text)
            answers.append({'question': question, 'answer': answer})
        
        return jsonify({'answers': answers})
    except Exception as e:
        app.logger.error(f"خطأ في معالجة الأسئلة: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/export_results', methods=['POST'])
def export_results():
    try:
        data = request.get_json()
        results = data.get('results', [])
        format_type = data.get('format', 'txt')
        
        if not results:
            return jsonify({'error': 'لا توجد نتائج للتصدير'}), 400
        
        # إنشاء اسم ملف فريد
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"research_results_{timestamp}.{format_type}"
        filepath = os.path.join('temp_data', filename)
        
        # تصدير النتائج حسب التنسيق المطلوب
        if format_type == 'txt':
            with open(filepath, 'w', encoding='utf-8') as f:
                for i, result in enumerate(results):
                    f.write(f"سؤال {i+1}: {result['question']}\n\n")
                    f.write(f"الإجابة: {result['answer']}\n\n")
                    f.write("="*50 + "\n\n")
        
        elif format_type == 'csv':
            df = pd.DataFrame(results)
            df.to_csv(filepath, index=False, encoding='utf-8')
        
        elif format_type == 'json':
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=4)
        
        else:
            return jsonify({'error': 'تنسيق غير مدعوم'}), 400
        
        return jsonify({'filename': filename})
    except Exception as e:
        app.logger.error(f"خطأ في تصدير النتائج: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    try:
        return send_file(os.path.join('temp_data', filename), as_attachment=True)
    except Exception as e:
        app.logger.error(f"خطأ في تنزيل الملف: {str(e)}")
        return jsonify({'error': str(e)}), 500

# تشغيل التطبيق
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
