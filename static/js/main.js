// متغيرات عالمية
let extractedText = "";
let results = [];
const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));

// عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    // نموذج استخراج النص
    const extractForm = document.getElementById('extractForm');
    extractForm.addEventListener('submit', handleExtractSubmit);
    
    // زر استخدام النص المباشر
    const useDirectTextBtn = document.getElementById('useDirectTextBtn');
    useDirectTextBtn.addEventListener('click', handleDirectTextSubmit);
    
    // زر تحميل الملف النصي
    const loadFileBtn = document.getElementById('loadFileBtn');
    loadFileBtn.addEventListener('click', handleFileUpload);
    
    // زر حفظ النص
    const saveTextBtn = document.getElementById('saveTextBtn');
    saveTextBtn.addEventListener('click', handleSaveText);
    
    // زر إضافة سؤال
    const addQuestionBtn = document.getElementById('addQuestionBtn');
    addQuestionBtn.addEventListener('click', addQuestion);
    
    // زر إرسال الأسئلة
    const submitQuestionsBtn = document.getElementById('submitQuestionsBtn');
    submitQuestionsBtn.addEventListener('click', handleSubmitQuestions);
    
    // أزرار التصدير
    const exportBtns = document.querySelectorAll('.export-btn');
    exportBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const format = this.getAttribute('data-format');
            exportResults(format);
        });
    });
    
    // إضافة سؤال أول افتراضي
    addQuestion();
});

// معالجة استخراج النص من رابط
async function handleExtractSubmit(e) {
    e.preventDefault();
    
    const urlInput = document.getElementById('urlInput');
    const url = urlInput.value.trim();
    
    if (!url) {
        showAlert('يرجى إدخال رابط صحيح', 'danger');
        return;
    }
    
    // عرض مؤشر التحميل
    document.getElementById('loadingMessage').textContent = 'جاري استخراج النص من الرابط...';
    loadingModal.show();
    
    try {
        const formData = new FormData();
        formData.append('url', url);
        
        const response = await fetch('/extract', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            extractedText = data.text;
            displayExtractedText(extractedText);
            document.getElementById('questionSection').style.display = 'block';
        } else {
            showAlert(data.error || 'حدث خطأ أثناء استخراج النص', 'danger');
        }
    } catch (error) {
        showAlert('حدث خطأ في الاتصال بالخادم', 'danger');
        console.error(error);
    } finally {
        loadingModal.hide();
    }
}

// معالجة إدخال النص المباشر
function handleDirectTextSubmit() {
    const directTextInput = document.getElementById('directTextInput');
    const text = directTextInput.value.trim();
    
    if (!text) {
        showAlert('يرجى إدخال نص', 'danger');
        return;
    }
    
    extractedText = text;
    displayExtractedText(extractedText);
    document.getElementById('questionSection').style.display = 'block';
    showAlert('تم استخدام النص بنجاح', 'success');
}

// معالجة تحميل ملف نصي
function handleFileUpload() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    
    if (!file) {
        showAlert('يرجى اختيار ملف', 'danger');
        return;
    }
    
    // عرض مؤشر التحميل
    document.getElementById('loadingMessage').textContent = 'جاري قراءة الملف...';
    loadingModal.show();
    
    const reader = new FileReader();
    
    reader.onload = function(e) {
        extractedText = e.target.result;
        displayExtractedText(extractedText);
        document.getElementById('questionSection').style.display = 'block';
        loadingModal.hide();
        showAlert('تم تحميل الملف بنجاح', 'success');
    };
    
    reader.onerror = function() {
        loadingModal.hide();
        showAlert('حدث خطأ أثناء قراءة الملف', 'danger');
    };
    
    reader.readAsText(file);
}

// عرض النص المستخرج
function displayExtractedText(text) {
    const extractedTextArea = document.getElementById('extractedText');
    extractedTextArea.value = text;
    document.getElementById('extractedTextSection').style.display = 'block';
}

// حفظ النص المستخرج
async function handleSaveText() {
    if (!extractedText) {
        showAlert('لا يوجد نص لحفظه', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/save_text', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: extractedText })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // تنزيل الملف
            window.location.href = `/download/${data.filename}`;
            showAlert('تم حفظ النص بنجاح', 'success');
        } else {
            showAlert(data.error || 'حدث خطأ أثناء حفظ النص', 'danger');
        }
    } catch (error) {
        showAlert('حدث خطأ في الاتصال بالخادم', 'danger');
        console.error(error);
    }
}

// إضافة سؤال جديد
function addQuestion() {
    const questionsContainer = document.getElementById('questionsContainer');
    const questionCount = questionsContainer.children.length;
    
    // إنشاء عنصر سؤال جديد
    const questionDiv = document.createElement('div');
    questionDiv.className = 'input-group mb-2';
    questionDiv.innerHTML = `
        <input type="text" class="form-control question-input" placeholder="أدخل سؤالك البحثي هنا..." required>
        <button type="button" class="btn btn-danger remove-question">
            <i class="bi bi-trash"></i>
        </button>
    `;
    
    // إضافة السؤال إلى الحاوية
    questionsContainer.appendChild(questionDiv);
    
    // إضافة مستمع حدث لزر الحذف
    const removeBtn = questionDiv.querySelector('.remove-question');
    removeBtn.addEventListener('click', function() {
        questionDiv.remove();
        updateRemoveButtons();
    });
    
    // تحديث أزرار الحذف
    updateRemoveButtons();
    
    // التركيز على حقل الإدخال الجديد
    const newInput = questionDiv.querySelector('.question-input');
    newInput.focus();
}

// تحديث أزرار الحذف (إخفاء زر الحذف إذا كان هناك سؤال واحد فقط)
function updateRemoveButtons() {
    const questionsContainer = document.getElementById('questionsContainer');
    const removeButtons = questionsContainer.querySelectorAll('.remove-question');
    
    if (removeButtons.length === 1) {
        removeButtons[0].style.display = 'none';
    } else {
        removeButtons.forEach(btn => {
            btn.style.display = 'block';
        });
    }
}

// معالجة إرسال الأسئلة
async function handleSubmitQuestions() {
    const questionInputs = document.querySelectorAll('.question-input');
    const questions = [];
    
    // جمع الأسئلة
    questionInputs.forEach(input => {
        const question = input.value.trim();
        if (question) {
            questions.push(question);
        }
    });
    
    if (questions.length === 0) {
        showAlert('يرجى إدخال سؤال واحد على الأقل', 'warning');
        return;
    }
    
    // عرض مؤشر التحميل
    document.getElementById('loadingMessage').textContent = 'جاري معالجة الأسئلة...';
    loadingModal.show();
    
    try {
        const response = await fetch('/answer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                questions: questions,
                text: extractedText
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            results = data.answers;
            displayResults(results);
        } else {
            showAlert(data.error || 'حدث خطأ أثناء معالجة الأسئلة', 'danger');
        }
    } catch (error) {
        showAlert('حدث خطأ في الاتصال بالخادم', 'danger');
        console.error(error);
    } finally {
        loadingModal.hide();
    }
}

// عرض النتائج
function displayResults(results) {
    const resultsContainer = document.getElementById('resultsContainer');
    resultsContainer.innerHTML = '';
    
    results.forEach((result, index) => {
        const resultDiv = document.createElement('div');
        resultDiv.className = 'result-card';
        resultDiv.innerHTML = `
            <div class="question-text">
                <i class="bi bi-question-circle me-2"></i>السؤال ${index + 1}: ${result.question}
            </div>
            <div class="answer-text">
                <i class="bi bi-chat-left-text me-2"></i>الإجابة: ${result.answer}
            </div>
        `;
        
        resultsContainer.appendChild(resultDiv);
    });
    
    document.getElementById('resultsSection').style.display = 'block';
}

// تصدير النتائج
async function exportResults(format) {
    if (results.length === 0) {
        showAlert('لا توجد نتائج للتصدير', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/export_results', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                results: results,
                format: format
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // تنزيل الملف
            window.location.href = `/download/${data.filename}`;
            showAlert(`تم تصدير النتائج بنجاح بصيغة ${format.toUpperCase()}`, 'success');
        } else {
            showAlert(data.error || 'حدث خطأ أثناء تصدير النتائج', 'danger');
        }
    } catch (error) {
        showAlert('حدث خطأ في الاتصال بالخادم', 'danger');
        console.error(error);
    }
}

// عرض رسالة تنبيه
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // إضافة التنبيه في أعلى الصفحة
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // إزالة التنبيه تلقائيًا بعد 5 ثوانٍ
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}
