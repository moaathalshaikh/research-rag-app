import os
from flask import Flask, render_template, request, jsonify, send_file
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pandas as pd
import json
import time
from datetime import datetime

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
from rag_system import RAGSystem

# إنشاء تطبيق Flask
app = Flask(__name__)

# إنشاء نظام RAG
rag_system = RAGSystem()

# المسارات
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract():
    try:
        url = request.form.get('url')
        if not url:
            return jsonify({'success': False, 'error': 'الرجاء إدخال رابط صحيح'}), 400
        
        # استخراج النص من الرابط
        text = extract_text_from_url(url)
        
        if not text:
            return jsonify({'success': False, 'error': 'لم يتم العثور على نص في الرابط المحدد'}), 400
        
        return jsonify({'success': True, 'text': text})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/save_text', methods=['POST'])
def save_text():
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'success': False, 'error': 'لا يوجد نص للحفظ'}), 400
        
        # إنشاء اسم ملف فريد
        filename = f"extracted_text_{int(time.time())}.txt"
        filepath = os.path.join('temp_data', filename)
        
        # حفظ النص في ملف
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        
        return jsonify({'success': True, 'filename': filename})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/answer', methods=['POST'])
def answer():
    try:
        data = request.get_json()
        questions = data.get('questions', [])
        
        if not questions:
            return jsonify({'success': False, 'error': 'الرجاء إدخال سؤال واحد على الأقل'}), 400
        
        # الإجابة على الأسئلة باستخدام نظام RAG
        answers = []
        for question in questions:
            answer = rag_system.answer_question(question)
            answers.append({'question': question, 'answer': answer})
        
        return jsonify({'success': True, 'answers': answers})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/export_results', methods=['POST'])
def export_results():
    try:
        data = request.get_json()
        results = data.get('results', [])
        format_type = data.get('format', 'txt')
        
        if not results:
            return jsonify({'success': False, 'error': 'لا توجد نتائج للتصدير'}), 400
        
        # إنشاء اسم ملف فريد
        timestamp = int(time.time())
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
            return jsonify({'success': False, 'error': 'تنسيق غير مدعوم'}), 400
        
        return jsonify({'success': True, 'filename': filename})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    try:
        return send_file(os.path.join('temp_data', filename), as_attachment=True)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# تشغيل التطبيق
if __name__ == '__main__':
    # التأكد من وجود مجلد البيانات المؤقتة
    os.makedirs('temp_data', exist_ok=True)
    app.run(debug=True, host='0.0.0.0')

# استيراد نظام RAG
from rag_system import RAGSystem

# إنشاء نظام RAG
rag_system = RAGSystem()

# إنشاء قاعدة المعرفة باستخدام RAG
def create_knowledge_base(text):
    global rag_system
    success = rag_system.create_knowledge_base(text)
    return success

# الإجابة على سؤال باستخدام RAG
def answer_question_with_rag(question):
    global rag_system
    return rag_system.answer_question(question)

# المسارات
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract():
    global extracted_text
    
    url = request.form.get('url')
    if not url:
        return jsonify({"error": "يرجى إدخال رابط URL"}), 400
    
    extracted_text = extract_text_from_url(url)
    
    # إنشاء قاعدة المعرفة
    create_knowledge_base(extracted_text)
    
    return jsonify({"text": extracted_text})

@app.route('/answer', methods=['POST'])
def answer():
    data = request.get_json()
    questions = data.get('questions', [])
    
    if not questions:
        return jsonify({"error": "يرجى إدخال سؤال واحد على الأقل"}), 400
    
    answers = []
    for question in questions:
        answer = answer_question_with_rag(question)
        answers.append({"question": question, "answer": answer})
    
    return jsonify({"answers": answers})

@app.route('/save_text', methods=['POST'])
def save_text():
    global extracted_text
    
    if not extracted_text:
        return jsonify({"error": "لا يوجد نص لحفظه"}), 400
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"temp_data/extracted_text_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(extracted_text)
    
    return jsonify({"filename": filename})

@app.route('/export_results', methods=['POST'])
def export_results():
    data = request.get_json()
    format_type = data.get('format', 'txt')
    results = data.get('results', [])
    
    if not results:
        return jsonify({"error": "لا توجد نتائج للتصدير"}), 400
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format_type == 'txt':
        filename = f"temp_data/results_{timestamp}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            for item in results:
                f.write(f"السؤال: {item['question']}\n")
                f.write(f"الإجابة: {item['answer']}\n\n")
    
    elif format_type == 'csv':
        filename = f"temp_data/results_{timestamp}.csv"
        df = pd.DataFrame(results)
        df.to_csv(filename, index=False, encoding='utf-8')
    
    elif format_type == 'json':
        filename = f"temp_data/results_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
    
    else:
        return jsonify({"error": "صيغة غير مدعومة"}), 400
    
    return jsonify({"filename": filename})

@app.route('/download/<path:filename>', methods=['GET'])
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
