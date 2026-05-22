from django import forms
from django.contrib.auth.models import User
# Импортируем готовую встроенную форму Django для создания пользователя
from django.contrib.auth.forms import UserCreationForm

# Создаем свой класс формы, который наследуется от базовой формы Django
class UserRegisterForm(UserCreationForm):
    # Добавляем обязательное поле для Email (в базовой форме его по умолчанию нет)
    email = forms.EmailField(required=True, label="Email")

    # Вложенный класс Meta говорит Django, какую модель использовать и какие поля выводить
    class Meta:
        model = User  # Работаем со встроенной моделью пользователя Django
        fields = ['username', 'email']  # Поля, которые пользователь увидит на странице

    # Конструктор класса: срабатывает в момент создания формы на странице
    def init(self, *args, **kwargs):
        super().init(*args, **kwargs)  # Запускаем стандартную настройку Django
        
        # Перебираем все поля формы (username, email, password1, password2) в цикле,
        # чтобы автоматически добавить к ним CSS-классы Tailwind.
        # Это избавляет от необходимости прописывать стили вручную для каждого инпута.
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            })