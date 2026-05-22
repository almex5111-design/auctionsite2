from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import AuctionItem, Bid
from .forms import UserRegisterForm   # Импортируем нашу форму из файла
# чтобы неавторизованные гости не могли зайти в профиль:
from django.contrib.auth.decorators import login_required

@login_required # Этот декоратор автоматически перенаправит на вход, если пользователь не авторизован
def profile(request):
    """Страница личного профиля пользователя"""
    # Находим все ставки текущего пользователя.
    # select_related('item') загрузит информацию о товарах сразу, чтобы база данных не перегружалась.
    user_bids = Bid.objects.filter(bidder=request.user).select_related('item').order_by('-created_at')
    
    # Передаем ставки в шаблон
    return render(request, 'main/profile.html', {
        'user_bids': user_bids
    })

def index(request):
    """Главная страница - список активных лотов"""
    items = AuctionItem.objects.filter(status='active')
    return render(request, 'main/index.html', {'items': items})

def item_detail(request, pk):
    """Детальная страница лота"""
    item = get_object_or_404(AuctionItem, pk=pk)
    
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            amount = float(request.POST.get('amount'))
            
            # Проверка минимальной ставки
            if amount < item.current_price + item.min_bid_step:
                messages.error(request, f'Минимальная ставка: {item.current_price + item.min_bid_step} ₽')
            elif amount <= item.current_price:
                messages.error(request, f'Ставка должна быть выше {item.current_price} ₽')
            else:
                # Создаём ставку
                Bid.objects.create(
                    item=item,
                    bidder=request.user,
                    amount=amount
                )
                # Обновляем текущую цену
                item.current_price = amount
                item.save()
                messages.success(request, 'Ставка принята!')
                
        except Exception as e:
            messages.error(request, f'Ошибка: {e}')
        
        return redirect('item_detail', pk=pk)
    
    return render(request, 'main/item_detail.html', {'item': item})


def register(request):
    # ПРОВЕРКА: Если пользователь УЖЕ залогинен, ему не нужно регистрироваться снова
    if request.user.is_authenticated:
        return redirect('/')  # Робот сразу перенаправляет его на главную страницу

    # СЛУЧАЙ 1: Пользователь нажал кнопку отправки формы (метод POST)
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)  # Наполняем форму данными, которые ввел человек
        
        # Проверяем, правильно ли заполнены поля (совпадают ли пароли, уникален ли логин)
        if form.is_valid():
            form.save()  # Физически создаем и сохраняем нового пользователя в базу данных PostgreSQL
            
            # Достаем очищенное (проверенное) имя пользователя для красивого уведомления
            username = form.cleaned_data.get('username')
            
            # Создаем зеленое сообщение об успехе, которое отобразится на следующей странице
            messages.success(request, f'Аккаунт для {username} успешно создан! Теперь вы можете войти.')
            
            # Перенаправляем пользователя на страницу входа (логина)
            return redirect('login')
            
    # СЛУЧАЙ 2: Пользователь просто первый раз открыл страницу регистрации (метод GET)
    else:
        form = UserRegisterForm()  # Создаем пустую форму без данных

    # Отдаем пользователю HTML-страницу и передаем туда объект формы
    return render(request, 'main/register.html', {'form': form})

