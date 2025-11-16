// Кольорова схема для типів вузлів
const NODE_COLORS = {
    'EmotionalState': '#4A90E2',
    'TestCategory': '#7B68EE',
    'Resource': '#50C878',
    'Theme': '#FF6B6B',
    'ResourceType': '#FFA500',
    'default': '#95A5A6'
};

let network = null;
let graphData = null;
let nodesDataSet = null;
let edgesDataSet = null;
let schema = null; // Схема онтології
let selectedNodes = []; // Для створення зв'язків

console.log("graph.js start");

// Завантажити дані графа
async function loadGraph() {
    try {
        // Завантажити схему
        const schemaResponse = await fetch('/api/schema');
        if (schemaResponse.ok) {
            schema = await schemaResponse.json();
            console.log('✓ Схема завантажена:', schema);
        }
        
        // Завантажити граф
        const response = await fetch('/api/graph');
        console.log(response);
        if (!response.ok) throw new Error('Failed to load graph');
        
        graphData = await response.json();
        
        // Показати попередження якщо є
        if (graphData.warnings && graphData.warnings.length > 0) {
            console.warn('⚠️ Graph loading warnings:', graphData.warnings);
            showWarningToast(graphData.warnings, graphData.warning_count);
        }
        
        renderGraph(graphData);
        
    } catch (error) {
        console.error('❌ Graph loading error:', error);
        document.getElementById('graph').innerHTML = 
            `<div class="error">❌ Помилка завантаження: ${error.message}</div>`;
    }
}

// Показати тост з попередженнями
function showWarningToast(warnings, count) {
    const warningDiv = document.createElement('div');
    warningDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 4px;
        padding: 15px;
        max-width: 300px;
        z-index: 1000;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    `;
    warningDiv.innerHTML = `
        <strong>⚠️ Попередження (${count})</strong>
        <div style="font-size: 12px; margin-top: 5px; max-height: 100px; overflow-y: auto;">
            ${warnings.slice(0, 3).map(w => `<div>• ${w}</div>`).join('')}
            ${warnings.length > 3 ? `<div>... та ще ${warnings.length - 3}</div>` : ''}
        </div>
        <button onclick="this.parentElement.remove()" style="margin-top: 10px; padding: 5px 10px; cursor: pointer;">
            Закрити
        </button>
    `;
    document.body.appendChild(warningDiv);
    setTimeout(() => warningDiv.remove(), 10000);
}

// Відобразити граф
function renderGraph(data) {
    try {
        // Підготовка даних для vis.js
        nodesDataSet = new vis.DataSet(
            data.nodes.map(node => ({
                id: node.id,
                label: truncateLabel(node.label),
                title: node.label,
                color: NODE_COLORS[node.type] || NODE_COLORS.default,
                shape: 'dot',
                size: 20,
                font: {
                    size: 12,
                    color: '#333'
                },
                nodeData: node
            }))
        );
        
        edgesDataSet = new vis.DataSet(
            data.edges.map((edge, index) => ({
                id: `edge_${index}`,
                from: edge.from,
                to: edge.to,
                label: edge.label,
                arrows: 'to',
                font: {
                    size: 10,
                    align: 'middle'
                },
                color: {
                    color: '#999',
                    highlight: '#333'
                },
                smooth: {
                    type: 'continuous'
                },
                edgeData: edge
            }))
        );
        
        // Оновити статистику
        document.getElementById('node-count').textContent = nodesDataSet.length;
        document.getElementById('edge-count').textContent = edgesDataSet.length;
        
        // Налаштування візуалізації
        const container = document.getElementById('graph');
        const graphDataVis = { nodes: nodesDataSet, edges: edgesDataSet };
        
        const options = {
            physics: {
                enabled: true,
                barnesHut: {
                    gravitationalConstant: -8000,
                    centralGravity: 0.3,
                    springLength: 150,
                    springConstant: 0.04,
                    damping: 0.09
                },
                stabilization: {
                    iterations: 150,
                    fit: false
                }
            },
            interaction: {
                hover: true,
                tooltipDelay: 100,
                zoomView: true,
                dragView: true,
                hideEdgesOnDrag: true,
                hideEdgesOnZoom: true
            },
            nodes: {
                borderWidth: 2,
                borderWidthSelected: 4,
                color: {
                    border: '#333',
                    highlight: {
                        border: '#000',
                        background: '#FFD700'
                    }
                }
            },
            edges: {
                smooth: {
                    type: 'continuous',
                    forceDirection: 'none'
                }
            },
            layout: {
                improvedLayout: true,
                randomSeed: 42
            }
        };
        
        // Створити мережу
        network = new vis.Network(container, graphDataVis, options);
        
        // Вимкнути фізику після стабілізації
        network.once('stabilizationIterationsDone', function() {
            console.log('✓ Граф стабілізовано, вимикаю фізику');
            network.setOptions({ physics: false });
            network.moveTo({
                scale: 0.5,
                animation: false
            });
        });
        
        // Фолбек: вимкнути фізику через 10 секунд
        setTimeout(() => {
            if (network) {
                console.log('⏱ Timeout: примусово вимикаю фізику');
                network.setOptions({ physics: false });
            }
        }, 10000);
        
        // Обробник кліку на вузол
        network.on('click', function(params) {
            if (params.nodes.length > 0) {
                const nodeId = params.nodes[0];
                const node = nodesDataSet.get(nodeId);
                showNodeDetails(node.nodeData);
                
                // Додати до вибраних для створення зв'язку
                toggleNodeSelection(nodeId);
            } else if (params.edges.length > 0) {
                // Клік на зв'язок
                const edgeId = params.edges[0];
                const edge = edgesDataSet.get(edgeId);
                showEdgeDetails(edge.edgeData, edgeId);
                clearNodeSelection();
            } else {
                // Клік в порожнє місце
                clearNodeSelection();
            }
        });
        
        // Обробник подвійного кліку
        network.on('doubleClick', function(params) {
            if (params.nodes.length > 0) {
                network.focus(params.nodes[0], {
                    scale: 1.5,
                    animation: true
                });
            }
        });
        
    } catch (error) {
        console.error('❌ Render error:', error);
        document.getElementById('graph').innerHTML = 
            `<div class="error">❌ Помилка рендерингу: ${error.message}</div>`;
    }
}

// Показати деталі вузла
function showNodeDetails(node) {
    const detailsDiv = document.getElementById('node-details');
    const noSelection = document.getElementById('no-selection');
    
    noSelection.style.display = 'none';
    detailsDiv.classList.add('active');
    
    const badgeColor = NODE_COLORS[node.type] || NODE_COLORS.default;
    
    let html = `
        <div class="node-type-badge" style="background: ${badgeColor}; color: white;">
            ${node.type}
        </div>
        
        <h3 style="margin: 0 0 20px 0; color: #333;">${escapeHtml(node.label)}</h3>
        
        <div class="property-group">
            <h4>Властивості</h4>
    `;
    
    for (const [key, value] of Object.entries(node.properties)) {
        if (key === 'id' || key === 'name' || key === 'title') continue;
        html += `
            <div class="property">
                <span class="property-label">${escapeHtml(key)}:</span>
                <span class="property-value">${escapeHtml(String(value))}</span>
            </div>
        `;
    }
    
    html += `</div>`;
    
    html += `
        <div class="property-group">
            <h4>Дії</h4>
            <button onclick="editNode(${node.id})" style="width: 100%; padding: 10px; margin: 5px 0; cursor: pointer; border: 1px solid #ddd; background: white; border-radius: 4px;">
                ✏️ Редагувати
            </button>
            <button onclick="deleteNode(${node.id})" style="width: 100%; padding: 10px; margin: 5px 0; cursor: pointer; border: 1px solid #d32f2f; color: #d32f2f; background: white; border-radius: 4px;">
                🗑️ Видалити
            </button>
        </div>
    `;
    
    detailsDiv.innerHTML = html;
}

// Показати деталі зв'язку
function showEdgeDetails(edge, visEdgeId) {
    const detailsDiv = document.getElementById('node-details');
    const noSelection = document.getElementById('no-selection');
    
    noSelection.style.display = 'none';
    detailsDiv.classList.add('active');
    
    // Отримати назви вузлів
    const fromNode = nodesDataSet.get(edge.from);
    const toNode = nodesDataSet.get(edge.to);
    
    let html = `
        <div class="node-type-badge" style="background: #666; color: white;">
            Зв'язок
        </div>
        
        <h3 style="margin: 0 0 20px 0; color: #333;">${escapeHtml(edge.label)}</h3>
        
        <div class="property-group">
            <h4>Напрямок</h4>
            <div style="padding: 10px; background: #f8f9fa; border-radius: 4px; font-size: 13px;">
                <strong>${escapeHtml(fromNode.nodeData.label)}</strong>
                <div style="text-align: center; margin: 5px 0;">↓</div>
                <strong>${escapeHtml(toNode.nodeData.label)}</strong>
            </div>
        </div>
    `;
    
    if (edge.properties && Object.keys(edge.properties).length > 0) {
        html += `<div class="property-group"><h4>Властивості зв'язку</h4>`;
        for (const [key, value] of Object.entries(edge.properties)) {
            html += `
                <div class="property">
                    <span class="property-label">${escapeHtml(key)}:</span>
                    <span class="property-value">${escapeHtml(String(value))}</span>
                </div>
            `;
        }
        html += `</div>`;
    }
    
    html += `
        <div class="property-group">
            <h4>Дії</h4>
            <button onclick="editEdge('${visEdgeId}', ${edge.id})" style="width: 100%; padding: 10px; margin: 5px 0; cursor: pointer; border: 1px solid #ddd; background: white; border-radius: 4px;">
                ✏️ Змінити тип зв'язку
            </button>
            <button onclick="deleteEdge('${visEdgeId}', ${edge.id})" style="width: 100%; padding: 10px; margin: 5px 0; cursor: pointer; border: 1px solid #d32f2f; color: #d32f2f; background: white; border-radius: 4px;">
                🗑️ Видалити зв'язок
            </button>
        </div>
    `;
    
    detailsDiv.innerHTML = html;
}

// Редагувати вузол
function editNode(nodeId) {
    alert(`TODO: Редагування вузла ${nodeId}`);
}

// Видалити вузол
function deleteNode(nodeId) {
    if (confirm('Видалити цей вузол? Це також видалить всі зв\'язки з ним.')) {
        alert(`TODO: Видалення вузла ${nodeId}`);
    }
}

// Редагувати зв'язок
async function editEdge(visEdgeId, neo4jEdgeId) {
    const edge = edgesDataSet.get(visEdgeId);
    const newType = prompt('Введіть новий тип зв\'язку:', edge.label);
    
    if (newType && newType.trim() !== '') {
        try {
            const response = await fetch(`/api/edge/${neo4jEdgeId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ type: newType.trim() })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to update edge');
            }
            
            // Оновити локально
            edgesDataSet.update({
                id: visEdgeId,
                label: newType.trim()
            });
            
            alert('✓ Тип зв\'язку успішно змінено');
            
            // Оновити деталі
            showEdgeDetails(edge.edgeData, visEdgeId);
            
        } catch (error) {
            alert(`❌ Помилка: ${error.message}`);
        }
    }
}

// Видалити зв'язок
async function deleteEdge(visEdgeId, neo4jEdgeId) {
    if (confirm('Видалити цей зв\'язок?')) {
        try {
            const response = await fetch(`/api/edge/${neo4jEdgeId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to delete edge');
            }
            
            // Видалити локально
            edgesDataSet.remove(visEdgeId);
            
            // Оновити статистику
            document.getElementById('edge-count').textContent = edgesDataSet.length;
            
            // Закрити деталі
            const detailsDiv = document.getElementById('node-details');
            const noSelection = document.getElementById('no-selection');
            detailsDiv.classList.remove('active');
            noSelection.style.display = 'block';
            
            alert('✓ Зв\'язок успішно видалено');
            
        } catch (error) {
            alert(`❌ Помилка: ${error.message}`);
        }
    }
}

// Допоміжні функції
function truncateLabel(label, maxLength = 25) {
    return label.length > maxLength ? label.substring(0, maxLength) + '...' : label;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Завантажити граф при завантаженні сторінки
window.addEventListener("load", () => {
    loadGraph();
});

// ============= ВИБІР ВУЗЛІВ ДЛЯ ЗВ'ЯЗКІВ =============

function toggleNodeSelection(nodeId) {
    const index = selectedNodes.indexOf(nodeId);
    
    if (index > -1) {
        selectedNodes.splice(index, 1);
    } else {
        selectedNodes.push(nodeId);
        if (selectedNodes.length > 2) {
            selectedNodes.shift(); // Залишаємо тільки 2 останніх
        }
    }
    
    updateNodeSelectionVisual();
    updateConnectionPanel();
}

function clearNodeSelection() {
    selectedNodes = [];
    updateNodeSelectionVisual();
    updateConnectionPanel();
}

function updateNodeSelectionVisual() {
    // Оновити візуальне виділення
    nodesDataSet.forEach(node => {
        if (selectedNodes.includes(node.id)) {
            nodesDataSet.update({
                id: node.id,
                borderWidth: 4,
                borderWidthSelected: 6,
                shapeProperties: {
                    borderDashes: [5, 5]
                }
            });
        } else {
            nodesDataSet.update({
                id: node.id,
                borderWidth: 2,
                borderWidthSelected: 4,
                shapeProperties: {
                    borderDashes: false
                }
            });
        }
    });
}

function updateConnectionPanel() {
    const panel = document.getElementById('connection-panel');
    if (!panel) return;
    
    if (selectedNodes.length === 2) {
        const node1 = nodesDataSet.get(selectedNodes[0]);
        const node2 = nodesDataSet.get(selectedNodes[1]);
        
        panel.innerHTML = `
            <div style="background: #e3f2fd; padding: 15px; border-radius: 4px; margin-bottom: 10px;">
                <strong>🔗 Створити зв'язок</strong>
                <div style="margin-top: 10px; font-size: 13px;">
                    <div>${escapeHtml(node1.label)}</div>
                    <div style="text-align: center; margin: 5px 0;">↓</div>
                    <div>${escapeHtml(node2.label)}</div>
                </div>
                <button onclick="showCreateEdgeModal()" style="width: 100%; padding: 10px; margin-top: 10px; cursor: pointer; background: #2196F3; color: white; border: none; border-radius: 4px;">
                    Створити зв'язок
                </button>
                <button onclick="clearNodeSelection()" style="width: 100%; padding: 8px; margin-top: 5px; cursor: pointer; background: white; border: 1px solid #ccc; border-radius: 4px;">
                    Скасувати
                </button>
            </div>
        `;
        panel.style.display = 'block';
    } else if (selectedNodes.length === 1) {
        const node = nodesDataSet.get(selectedNodes[0]);
        panel.innerHTML = `
            <div style="background: #fff3cd; padding: 15px; border-radius: 4px;">
                <strong>1 вузол обрано</strong>
                <div style="margin-top: 5px; font-size: 13px;">
                    ${escapeHtml(node.label)}
                </div>
                <div style="margin-top: 10px; font-size: 12px; color: #666;">
                    Оберіть ще один вузол для створення зв'язку
                </div>
            </div>
        `;
        panel.style.display = 'block';
    } else {
        panel.style.display = 'none';
    }
}

// ============= МОДАЛЬНІ ВІКНА =============

function showModal(content) {
    const modal = document.createElement('div');
    modal.id = 'modal-overlay';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
    `;
    
    modal.innerHTML = `
        <div style="background: white; border-radius: 8px; padding: 30px; max-width: 500px; width: 90%; max-height: 80vh; overflow-y: auto; position: relative;">
            <button onclick="closeModal()" style="position: absolute; top: 10px; right: 10px; background: none; border: none; font-size: 24px; cursor: pointer; color: #999;">×</button>
            ${content}
        </div>
    `;
    
    document.body.appendChild(modal);
}

function closeModal() {
    const modal = document.getElementById('modal-overlay');
    if (modal) modal.remove();
}

// ============= СТВОРЕННЯ ВУЗЛА =============

function showCreateNodeModal() {
    if (!schema) {
        alert('Схема ще не завантажена');
        return;
    }
    
    const content = `
        <h2 style="margin: 0 0 20px 0;">Створити новий вузол</h2>
        
        <div style="margin-bottom: 15px;">
            <label style="display: block; margin-bottom: 5px; font-weight: 600;">Тип вузла:</label>
            <select id="new-node-type" onchange="updateNodePropertyFields()" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
                <option value="">-- Оберіть тип --</option>
                ${schema.node_types.map(type => `<option value="${type}">${type}</option>`).join('')}
            </select>
        </div>
        
        <div id="node-properties-fields"></div>
        
        <div style="display: flex; gap: 10px; margin-top: 20px;">
            <button onclick="createNode()" style="flex: 1; padding: 10px; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">
                Створити
            </button>
            <button onclick="closeModal()" style="flex: 1; padding: 10px; background: #999; color: white; border: none; border-radius: 4px; cursor: pointer;">
                Скасувати
            </button>
        </div>
    `;
    
    showModal(content);
}

function updateNodePropertyFields() {
    const typeSelect = document.getElementById('new-node-type');
    const fieldsDiv = document.getElementById('node-properties-fields');
    const selectedType = typeSelect.value;
    
    if (!selectedType || !schema.node_properties[selectedType]) {
        fieldsDiv.innerHTML = '';
        return;
    }
    
    const properties = schema.node_properties[selectedType];
    
    fieldsDiv.innerHTML = properties.map(prop => `
        <div style="margin-bottom: 15px;">
            <label style="display: block; margin-bottom: 5px; font-weight: 600;">${prop}:</label>
            <input type="text" id="prop-${prop}" placeholder="${prop}" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
        </div>
    `).join('');
}

async function createNode() {
    const typeSelect = document.getElementById('new-node-type');
    const nodeType = typeSelect.value;
    
    if (!nodeType) {
        alert('Оберіть тип вузла');
        return;
    }
    
    const properties = {};
    const propInputs = document.querySelectorAll('[id^="prop-"]');
    propInputs.forEach(input => {
        const propName = input.id.replace('prop-', '');
        if (input.value.trim()) {
            // Спроба конвертувати в число
            const numValue = Number(input.value);
            properties[propName] = isNaN(numValue) ? input.value.trim() : numValue;
        }
    });
    
    try {
        const response = await fetch('/api/node', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: nodeType, properties })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to create node');
        }
        
        const result = await response.json();
        
        // Додати вузол до графа
        const newNode = result.node;
        nodesDataSet.add({
            id: newNode.id,
            label: truncateLabel(newNode.properties.name || newNode.properties.title || newNode.properties.id || 'New Node'),
            title: newNode.properties.name || newNode.properties.title || newNode.properties.id || 'New Node',
            color: NODE_COLORS[newNode.type] || NODE_COLORS.default,
            shape: 'dot',
            size: 20,
            font: { size: 12, color: '#333' },
            nodeData: {
                id: newNode.id,
                type: newNode.type,
                label: newNode.properties.name || newNode.properties.title || newNode.properties.id || 'New Node',
                properties: newNode.properties
            }
        });
        
        // Оновити статистику
        document.getElementById('node-count').textContent = nodesDataSet.length;
        
        closeModal();
        alert('✓ Вузол успішно створено');
        
    } catch (error) {
        alert(`❌ Помилка: ${error.message}`);
    }
}

// ============= СТВОРЕННЯ ЗВ'ЯЗКУ =============

function showCreateEdgeModal() {
    if (!schema || selectedNodes.length !== 2) {
        alert('Оберіть два вузли для створення зв\'язку');
        return;
    }
    
    const node1 = nodesDataSet.get(selectedNodes[0]);
    const node2 = nodesDataSet.get(selectedNodes[1]);
    
    const content = `
        <h2 style="margin: 0 0 20px 0;">Створити зв'язок</h2>
        
        <div style="background: #f8f9fa; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
            <div><strong>Від:</strong> ${escapeHtml(node1.label)}</div>
            <div style="text-align: center; margin: 10px 0;">↓</div>
            <div><strong>До:</strong> ${escapeHtml(node2.label)}</div>
        </div>
        
        <div style="margin-bottom: 15px;">
            <label style="display: block; margin-bottom: 5px; font-weight: 600;">Тип зв'язку:</label>
            <select id="new-edge-type" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
                <option value="">-- Оберіть тип --</option>
                ${schema.edge_types.map(type => `<option value="${type}">${type}</option>`).join('')}
                <option value="__custom__">+ Власний тип</option>
            </select>
        </div>
        
        <div id="custom-edge-type" style="display: none; margin-bottom: 15px;">
            <input type="text" id="custom-edge-type-input" placeholder="Введіть назву типу" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
        </div>
        
        <div style="margin-bottom: 15px;">
            <label style="display: block; margin-bottom: 5px; font-weight: 600;">Властивості (опціонально):</label>
            <div id="edge-properties-container">
                <button onclick="addEdgeProperty()" style="padding: 6px 12px; background: #f0f0f0; border: 1px solid #ddd; border-radius: 4px; cursor: pointer;">
                    + Додати властивість
                </button>
            </div>
        </div>
        
        <div style="display: flex; gap: 10px; margin-top: 20px;">
            <button onclick="createEdge()" style="flex: 1; padding: 10px; background: #2196F3; color: white; border: none; border-radius: 4px; cursor: pointer;">
                Створити
            </button>
            <button onclick="closeModal()" style="flex: 1; padding: 10px; background: #999; color: white; border: none; border-radius: 4px; cursor: pointer;">
                Скасувати
            </button>
        </div>
    `;
    
    showModal(content);
    
    // Обробник для показу поля власного типу
    document.getElementById('new-edge-type').addEventListener('change', function() {
        const customDiv = document.getElementById('custom-edge-type');
        customDiv.style.display = this.value === '__custom__' ? 'block' : 'none';
    });
}

function addEdgeProperty() {
    const container = document.getElementById('edge-properties-container');
    const propDiv = document.createElement('div');
    propDiv.style.cssText = 'display: flex; gap: 10px; margin-top: 10px;';
    propDiv.innerHTML = `
        <input type="text" placeholder="Назва" class="edge-prop-key" style="flex: 1; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
        <input type="text" placeholder="Значення" class="edge-prop-value" style="flex: 1; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
        <button onclick="this.parentElement.remove()" style="padding: 8px 12px; background: #f44336; color: white; border: none; border-radius: 4px; cursor: pointer;">×</button>
    `;
    container.appendChild(propDiv);
}

async function createEdge() {
    const typeSelect = document.getElementById('new-edge-type');
    let edgeType = typeSelect.value;
    
    if (edgeType === '__custom__') {
        edgeType = document.getElementById('custom-edge-type-input').value.trim();
    }
    
    if (!edgeType) {
        alert('Оберіть або введіть тип зв\'язку');
        return;
    }
    
    // Зібрати властивості
    const properties = {};
    const propKeys = document.querySelectorAll('.edge-prop-key');
    const propValues = document.querySelectorAll('.edge-prop-value');
    
    propKeys.forEach((keyInput, index) => {
        const key = keyInput.value.trim();
        const value = propValues[index].value.trim();
        if (key && value) {
            const numValue = Number(value);
            properties[key] = isNaN(numValue) ? value : numValue;
        }
    });
    
    try {
        const response = await fetch('/api/edge', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                from: selectedNodes[0],
                to: selectedNodes[1],
                type: edgeType,
                properties
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to create edge');
        }
        
        const result = await response.json();
        
        // Додати зв'язок до графа
        const newEdge = result.edge;
        edgesDataSet.add({
            id: `edge_${edgesDataSet.length}`,
            from: newEdge.from,
            to: newEdge.to,
            label: newEdge.type,
            arrows: 'to',
            font: { size: 10, align: 'middle' },
            color: { color: '#999', highlight: '#333' },
            smooth: { type: 'continuous' },
            edgeData: newEdge
        });
        
        // Оновити статистику
        document.getElementById('edge-count').textContent = edgesDataSet.length;
        
        clearNodeSelection();
        closeModal();
        alert('✓ Зв\'язок успішно створено');
        
    } catch (error) {
        alert(`❌ Помилка: ${error.message}`);
    }
}

// ============= РЕДАГУВАННЯ ЗВ'ЯЗКУ =============