/**
 * Widget для збереження ресурсів
 * Додай цей файл в static/js/save_resource.js
 * Підключи на сторінках де показуються ресурси
 */

// Глобальний кеш статусів збереження
const savedResourcesCache = new Set();

/**
 * Ініціалізувати всі кнопки збереження на сторінці
 */
async function initSaveButtons() {
    const buttons = document.querySelectorAll('.save-resource-btn');
    
    // Отримати статуси для всіх ресурсів одним запитом (опціонально)
    const resourceIds = Array.from(buttons).map(btn => btn.dataset.resourceId);
    
    if (resourceIds.length > 0) {
        await checkSavedStatusBatch(resourceIds);
    }
    
    // Оновити UI кнопок
    buttons.forEach(btn => {
        const resourceId = btn.dataset.resourceId;
        updateButtonState(btn, savedResourcesCache.has(resourceId));
    });
}

/**
 * Перевірити статус збереження кількох ресурсів одночасно (BATCH)
 * Це швидше ніж робити окремий запит для кожного ресурсу
 */
async function checkSavedStatusBatch(resourceIds) {
    try {
        const response = await fetch('/api/saved-resources/check-batch', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ resource_ids: resourceIds })
        });
        
        if (!response.ok) {
            console.warn('Batch check failed, falling back to individual checks');
            // Fallback до індивідуальних перевірок
            const promises = resourceIds.map(id => checkSavedStatus(id));
            await Promise.all(promises);
            return;
        }
        
        const data = await response.json();
        
        // Оновити кеш
        Object.entries(data.saved).forEach(([resourceId, isSaved]) => {
            if (isSaved) {
                savedResourcesCache.add(resourceId);
            } else {
                savedResourcesCache.delete(resourceId);
            }
        });
        
    } catch (error) {
        console.error('Error in batch check:', error);
        // Fallback до індивідуальних перевірок
        const promises = resourceIds.map(id => checkSavedStatus(id));
        await Promise.all(promises);
    }
}

/**
 * Перевірити чи збережений ресурс
 */
async function checkSavedStatus(resourceId) {
    try {
        const response = await fetch(`/api/saved-resources/check/${resourceId}`);
        if (!response.ok) return false;
        
        const data = await response.json();
        if (data.is_saved) {
            savedResourcesCache.add(resourceId);
        } else {
            savedResourcesCache.delete(resourceId);
        }
        return data.is_saved;
    } catch (error) {
        console.error('Error checking saved status:', error);
        return false;
    }
}

/**
 * Toggle збереження ресурсу
 */
async function toggleSaveResource(resourceId) {
    const button = document.querySelector(`.save-resource-btn[data-resource-id="${resourceId}"]`);
    if (!button) return;
    
    const isSaved = savedResourcesCache.has(resourceId);
    
    // Показати індикатор завантаження
    button.disabled = true;
    const originalContent = button.innerHTML;
    button.innerHTML = '<span>⏳</span> <span>Збереження...</span>';
    
    try {
        if (isSaved) {
            // Видалити зі збережених
            const response = await fetch(`/api/saved-resources/${resourceId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) throw new Error('Failed to unsave resource');
            
            savedResourcesCache.delete(resourceId);
            updateButtonState(button, false);
            showToast('✓ Ресурс видалено зі збережених', 'success');
            
        } else {
            // Зберегти
            const response = await fetch(`/api/saved-resources/${resourceId}`, {
                method: 'POST'
            });
            
            if (!response.ok) throw new Error('Failed to save resource');
            
            const data = await response.json();
            
            if (data.already_saved) {
                showToast('ℹ️ Ресурс вже збережено', 'info');
            } else {
                showToast('✓ Ресурс збережено', 'success');
            }
            
            savedResourcesCache.add(resourceId);
            updateButtonState(button, true);
        }
        
    } catch (error) {
        console.error('Error toggling save:', error);
        showToast(`❌ Помилка: ${error.message}`, 'error');
        button.innerHTML = originalContent;
    } finally {
        button.disabled = false;
    }
}

/**
 * Оновити стан кнопки
 */
function updateButtonState(button, isSaved) {
    if (isSaved) {
        button.classList.add('saved');
        button.innerHTML = '<span class="save-icon">✅</span> <span class="save-text">Збережено</span>';
        button.style.background = '#FFC107';
        button.style.color = '#333';
    } else {
        button.classList.remove('saved');
        button.innerHTML = '<span class="save-icon">💾</span> <span class="save-text">Зберегти</span>';
        button.style.background = '#4CAF50';
        button.style.color = 'white';
    }
}

/**
 * Показати toast повідомлення
 */
function showToast(message, type = 'info') {
    // Видалити попередній toast якщо є
    const existingToast = document.getElementById('save-resource-toast');
    if (existingToast) existingToast.remove();
    
    // Створити новий toast
    const toast = document.createElement('div');
    toast.id = 'save-resource-toast';
    toast.textContent = message;
    
    // Стилі
    const colors = {
        success: '#4CAF50',
        error: '#f44336',
        info: '#2196F3'
    };
    
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${colors[type] || colors.info};
        color: white;
        padding: 15px 20px;
        border-radius: 4px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 10000;
        font-size: 14px;
        font-weight: 500;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    // Автоматично видалити через 3 секунди
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/**
 * Створити кнопку збереження програматично
 */
function createSaveButton(resourceId, options = {}) {
    const button = document.createElement('button');
    button.className = 'save-resource-btn';
    button.dataset.resourceId = resourceId;
    button.onclick = () => toggleSaveResource(resourceId);
    
    // Застосувати опції
    const defaultStyle = {
        cursor: 'pointer',
        padding: '8px 16px',
        border: 'none',
        borderRadius: '4px',
        background: '#4CAF50',
        color: 'white',
        fontSize: '14px',
        fontWeight: '600',
        transition: 'all 0.2s',
        ...options.style
    };
    
    Object.assign(button.style, defaultStyle);
    
    button.innerHTML = '<span class="save-icon">💾</span> <span class="save-text">Зберегти</span>';
    
    // Перевірити статус та оновити
    checkSavedStatus(resourceId).then(isSaved => {
        updateButtonState(button, isSaved);
    });
    
    return button;
}

// Додати CSS анімації
if (!document.getElementById('save-resource-styles')) {
    const style = document.createElement('style');
    style.id = 'save-resource-styles';
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }
        
        .save-resource-btn:hover {
            opacity: 0.9;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        .save-resource-btn:active {
            transform: translateY(0);
        }
        
        .save-resource-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
    `;
    document.head.appendChild(style);
}

// Автоматично ініціалізувати при завантаженні
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSaveButtons);
} else {
    initSaveButtons();
}

// Експортувати для використання з інших скриптів
window.toggleSaveResource = toggleSaveResource;
window.createSaveButton = createSaveButton;
window.checkSavedStatus = checkSavedStatus;