// static/admin/js/drag_and_drop.js
document.addEventListener('DOMContentLoaded', () => {
    const containers = document.querySelectorAll('.drag-drop-container');
    containers.forEach(container => {
        const input = container.querySelector('input[type="file"]');
        const dropArea = container.querySelector('.drag-drop-area');

        dropArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropArea.style.backgroundColor = '#3a3f4a'; /* Чуть светлее при перетаскивании */
            dropArea.style.borderColor = '#2c44b6'; /* Цвет выделения */
        });

        dropArea.addEventListener('dragleave', () => {
            dropArea.style.backgroundColor = '#2a2d37';
            dropArea.style.borderColor = '#2a2d37';
        });

        dropArea.addEventListener('drop', (e) => {
            e.preventDefault();
            dropArea.style.backgroundColor = '#2a2d37';
            dropArea.style.borderColor = '#2a2d37';
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                input.files = files;
            }
        });

        dropArea.addEventListener('click', () => {
            input.click();
        });
    });
});