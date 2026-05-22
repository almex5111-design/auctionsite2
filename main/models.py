from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils.text import slugify






class Category(models.Model):
    """Категори товаров"""
    name = models.CharField('Название', max_length=100, unique=True) #ИМЯ
    slug = models.SlugField(max_length=100, unique=True) #это поле для короткого текста в URL
    description = models.TextField('Описание', blank=True)
    image = models.ImageField('Изображение', upload_to='categories/', blank=True, null=True)


    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name'] #Классы идут от А до Я

        


    def __str__(self):
        return self.name #Определяет, как объект будет отображаться как текст
    
       
class AuctionItem(models.Model):
            """Лот (товар) на аукционе"""
            STATUS_CHOICES = [
                ('active', 'Активен'),
                ('closed', 'Завершен'),
                ('cancelled', 'Отменен'), #Это список вариантов (выбора) для поля в Django
            ]

            title = models.CharField('Название лота', max_length=200) #название товара
            description = models.TextField('Описание') #описание товара
            category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='items')#категория товара  если категорию удалят станет null
            seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')#кто продаёт товар CASVADE= если пользователь удалён  товар удаляется


            main_image = models.ImageField('Главное фото', upload_to='auction_items') #Создаёт поле для загрузки главного изображения лота


            start_price = models.DecimalField('Начальная цена', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])#Создаёт поле для цены с проверками
            current_price = models.DecimalField('Текущая цена', max_digits=10, decimal_places=2, editable=False, default=0)#editable=False = поле нельзя редактировать вручную
            min_bid_step = models.DecimalField('Минимальный шаг ставки', max_digits=10, decimal_places=2, default=Decimal('1.00'))

            start_time = models.DateTimeField('Время начала')
            end_time = models.DateTimeField('Время окончания')


            status = models.CharField('Статус', max_length=10, choices=STATUS_CHOICES, default='active')
            winner = models.ForeignKey(User, on_delete= models.SET_NULL, null=True, blank=True, related_name='won_items', verbose_name='Победитель') #хранит победителя может быть пустым

            created_at = models.DateTimeField('Создан' , auto_now_add=True)#Создаёт поле даты и времени создания объекта
            updated_at = models.DateTimeField('Обновлен' , auto_now=True)#поле хранит дату последнего обновления объекта

            class Meta:
                verbose_name = 'Лот'
                verbose_name_plural = 'Лоты'
                ordering = ['-created_at']#сортировка от нового к старому

            def save(self, *args, **kwargs):
                if not self.pk:
                    self.current_price = self.start_price
                super().save(*args, **kwargs)#if not self.pk  новый объект #save()  переопределение сохранения


            def is_active(self):
                """Проверка, идут ли торги прямо сейчас"""
                now = timezone.now()
                return self.status == 'active' and self.start_time <= now <= self.end_time
            
            def place_bid(self, user, amount):
                """Поставить новую ставку"""
                from .models import Bid #проверить,  создать ставку,  обновить цену

                if not self.is_active():
                    raise ValueError("Аукцион не активен")
                if amount <= self.current_price:
                    raise ValueError(f"Ставка должна быть выше текущей цены({self.current_price})")
                
                min_required =self.current_price + self.min_bid_step
                if amount < min_required:
                    raise ValueError(f"Минимальная ставка: {min_required}") #минимальна ставка
                
                if user == self.seller:
                    raise ValueError("Продавец не может ставить на свой лот")
                

                bid = Bid.objects.create(
                    item=self,
                    bidder=user,
                    amount=amount
                )#создаёт новую запись в базе

                self.current_price = amount 
                self.save (update_fields=['current_price'])

                return bid #обновляет цену 
            
            def close_auction(self):
                """Завершить аукцион и определить победителя"""
                if self.status != 'active':
                    return
                last_bid = self.bids.filter(is_winning_bid=False).order_by('-amount', '-created_at').first() #находит последнюю (лучшую) ставку


                if last_bid:
                    self.winner = last_bid.bidder
                    self.status = 'closed'
                    last_bid.is_winning_bid = True      #назначает победителя, закрывает аукцион, помечает выигрышную ставку
                    last_bid.save()
                else:
                    self.status = 'cancelled'

                self.save()

            def __str__(self):
                return f"{self.title} - {self.current_price}с"#Определяет, как объект будет отображаться как текст
            
class Bid(models.Model):
            """Ставка пользователя"""
            item = models.ForeignKey(AuctionItem, on_delete=models.CASCADE, related_name='bids') 
            bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
            amount = models.DecimalField('Сумма ставки', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal(0.01))])
            created_at = models.DateTimeField('Время ставки', auto_now_add=True)
            is_winning_bid = models.BooleanField('Выигрышная ставка', default=False)#хранит все ставки пользователей

            class Meta:
                verbose_name = 'Ставка'
                verbose_name_plural = 'Ставки'
                ordering = ['-amount', '-created_at']
                unique_together = ['item', 'bidder', 'amount']#Один пользователь не может сделать две однаковые ставки подряд


            def save(self, *args, **kwargs):
                if self.amount < self.item.current_price + self.item.min_bid_step: 
                    raise ValueError(f"Сумма ставки слишком мала. Минимум: {self.item.current_price + self.item.min_bid_step}")
                super().save(*args, **kwargs)#проверяет минимальную ставку

            def __str__(self):
                return f"{self.bidder.username} ставит {self.amount} на {self.item.title}"#Определяет, как ставка будет отображаться как текст
            
class Watchlist(models.Model):
                """Список отслеживаемых лотов пользователя"""
                user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
                item = models.ForeignKey(AuctionItem, on_delete=models.CASCADE, related_name='watched_by')
                added_at = models.DateTimeField('Добавлен', auto_now_add=True)#хранит избранные лоты пользователя

                class Meta:
                    unique_together = ['user', 'item']
                    verbose_name = 'Отслеживаемый лот'
                    verbose_name_plural = 'Отслеживаемые лоты'

                def __str__(self):
                    return f"{self.user.username} следит за {self.item.title}"
class ItemImage(models.Model):
    """Дополнительные фотографии для лота"""
    item = models.ForeignKey(AuctionItem, on_delete=models.CASCADE, related_name='images', verbose_name='Лот')
    image = models.ImageField('Фотография', upload_to='auction_items/extra/')

    class Meta:
        verbose_name = 'Дополнительное фото'
        verbose_name_plural = 'Дополнительные фото'

    def __str__(self):
        return f"Фото для {self.item.title}"    