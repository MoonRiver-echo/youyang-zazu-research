/**
 * csv-upload.js — CSV 文件上传、预览与解析
 */

const CSVUpload = (function() {
    let parsedData = [];
    let columns = [];
    const listeners = [];

    function init() {
        const dropZone = document.getElementById('drop-zone');
        const fileInput = document.getElementById('file-input');
        const uploadTrigger = document.getElementById('upload-trigger');
        const modal = document.getElementById('upload-modal');
        const modalClose = document.getElementById('modal-close');
        const modalBackdrop = modal.querySelector('.modal-backdrop');
        const btnCancel = document.getElementById('btn-cancel');
        const btnImport = document.getElementById('btn-import');

        // Open modal
        uploadTrigger.addEventListener('click', () => {
            modal.classList.add('visible');
            resetModal();
        });

        // Close modal handlers
        [modalClose, modalBackdrop, btnCancel].forEach(el => {
            el.addEventListener('click', () => modal.classList.remove('visible'));
        });

        // Drag & drop
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
        });

        dropZone.addEventListener('drop', handleDrop, false);
        fileInput.addEventListener('change', handleFiles, false);

        btnImport.addEventListener('click', () => {
            if (parsedData.length > 0) {
                notifyListeners(parsedData);
                App.showToast(I18n.t('toast.importSuccess', { count: parsedData.length }), 'success');
                modal.classList.remove('visible');
            }
        });
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles({ target: { files } });
    }

    function handleFiles(e) {
        const files = e.target.files;
        if (!files || files.length === 0) return;

        const file = files[0];
        if (!file.name.toLowerCase().endsWith('.csv')) {
            App.showToast(I18n.t('toast.fileTypeError'), 'error');
            return;
        }

        Papa.parse(file, {
            header: true,
            skipEmptyLines: true,
            encoding: 'UTF-8',
            complete: function(results) {
                parsedData = results.data || [];
                columns = results.meta.fields || [];
                showPreview(parsedData, columns);
            },
            error: function(err) {
                console.error('CSV parse error:', err);
                App.showToast(I18n.t('toast.importError'), 'error');
            }
        });
    }

    function showPreview(data, cols) {
        const previewArea = document.getElementById('preview-area');
        const previewTable = document.getElementById('preview-table');
        const previewRows = document.getElementById('preview-rows');
        const previewCols = document.getElementById('preview-cols');
        const detectionInfo = document.getElementById('detection-info');
        const btnImport = document.getElementById('btn-import');

        previewArea.classList.remove('hidden');
        btnImport.classList.remove('hidden');

        previewRows.textContent = data.length;
        previewCols.textContent = cols.length;

        // Build preview table (first 5 rows)
        const previewLimit = Math.min(data.length, 5);
        let thead = '<tr>' + cols.map(c => `<th>${escapeHtml(c)}</th>`).join('') + '</tr>';
        let tbody = '';
        for (let i = 0; i < previewLimit; i++) {
            tbody += '<tr>' + cols.map(c => {
                const val = data[i][c] || '';
                return `<td>${escapeHtml(String(val).substring(0, 60))}</td>`;
            }).join('') + '</tr>';
        }
        previewTable.innerHTML = `<thead>${thead}</thead><tbody>${tbody}</tbody>`;

        // Detection info
        const expectedCols = ['name', 'title', 'category', 'description', 'lat', 'lng', 'latitude', 'longitude', 'source', 'culture_type', 'period'];
        const lowerCols = cols.map(c => c.toLowerCase());
        const detected = expectedCols.filter(c => lowerCols.includes(c));
        const missing = expectedCols.filter(c => !lowerCols.includes(c));

        let detHtml = `<div><strong>检测到列：</strong> `;
        if (detected.length > 0) {
            detHtml += detected.map(c => `<span class="detected">${c}</span>`).join('、');
        } else {
            detHtml += '<span class="missing">无匹配列</span>';
        }
        detHtml += `</div><div style="margin-top:6px"><strong>未检测到列：</strong> `;
        detHtml += missing.map(c => `<span class="missing">${c}</span>`).join('、');
        detHtml += '</div>';
        detectionInfo.innerHTML = detHtml;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function resetModal() {
        document.getElementById('preview-area').classList.add('hidden');
        document.getElementById('btn-import').classList.add('hidden');
        document.getElementById('preview-table').innerHTML = '';
        document.getElementById('detection-info').innerHTML = '';
        parsedData = [];
        columns = [];
    }

    function onDataLoaded(callback) {
        listeners.push(callback);
    }

    function notifyListeners(data) {
        listeners.forEach(cb => cb(data));
    }

    return { init, onDataLoaded };
})();
