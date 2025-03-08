# dictionary/widgets.py
from django.forms.widgets import ClearableFileInput
from django.utils.safestring import mark_safe

class DragAndDropFileInput(ClearableFileInput):
    def render(self, name, value, attrs=None, renderer=None):
        # Получаем HTML для стандартного поля загрузки файла
        input_html = super().render(name, value, attrs=attrs, renderer=renderer)

        # Добавляем контейнер для Drag-and-Drop
        html = f"""
        <div class="drag-drop-container" style="border: 2px dashed #d1d4d7; padding: 20px; text-align: center; border-radius: 10px; margin: 10px 0; background-color: #fafafa;">
            {input_html}
            <div class="drag-drop-area">
                <p style="color: #6c757d;">Перетащите изображение сюда или нажмите, чтобы выбрать файл</p>
            </div>
        </div>
        """

        return mark_safe(html)