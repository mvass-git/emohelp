document.addEventListener('DOMContentLoaded', function() {
    initEventListeners();
});

function initEventListeners() {
    const form = document.querySelector('form');
    const btnBack = document.getElementById('btnBack');
    const btnSkip = document.getElementById('btnSkip');
    
    // Видаляємо старі обробники (якщо є)
    const newForm = form.cloneNode(true);
    form.parentNode.replaceChild(newForm, form);
    
    // Обробка сабміту форми (кнопки Next/Submit)
    newForm.addEventListener('submit', handleSubmit);
    
    // Обробка кнопки Back
    const newBtnBack = document.getElementById('btnBack');
    if (newBtnBack) {
        newBtnBack.addEventListener('click', handleBack);
    }
    
    // Обробка кнопки Skip
    const newBtnSkip = document.getElementById('btnSkip');
    if (newBtnSkip) {
        newBtnSkip.addEventListener('click', handleSkip);
    }
}

function handleSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    const questionId = form.querySelector('input[name="question_id"]').value;
    const selectedAnswer = form.querySelector('input[name="answer"]:checked');
    
    if (selectedAnswer) {
        formData.set('answer', selectedAnswer.value);
    }
    formData.set('question_id', questionId);
    
    const submitter = e.submitter;
    if (submitter && submitter.name === 'action') {
        formData.set('action', submitter.value);
    } else {
        formData.set('action', 'next');
    }
    
    sendRequest(formData);
}

function handleBack() {
    const form = document.querySelector('form');
    const formData = new FormData(form);
    const questionId = form.querySelector('input[name="question_id"]').value;
    const selectedAnswer = form.querySelector('input[name="answer"]:checked');
    
    if (selectedAnswer) {
        formData.set('answer', selectedAnswer.value);
    }
    formData.set('question_id', questionId);
    formData.set('action', 'back');
    
    sendRequest(formData);
}

function handleSkip() {
    const form = document.querySelector('form');
    const formData = new FormData(form);
    const questionId = form.querySelector('input[name="question_id"]').value;
    
    formData.set('question_id', questionId);
    formData.set('action', 'skip');
    
    sendRequest(formData);
}

function sendRequest(formData) {
    fetch(window.location.href, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.redirect) {
            window.location.href = data.redirect;
        } else if (data.success && data.html) {
            const questionContainer = document.querySelector('.question-container').parentElement;
            questionContainer.innerHTML = data.html;
            // Повторно ініціалізуємо обробники після оновлення HTML
            initEventListeners();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Виникла помилка. Спробуйте ще раз.');
    });
}