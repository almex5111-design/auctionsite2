from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
# Импортируем все модели, включая созданную ItemImage
from .models import Category, AuctionItem, Bid, Watchlist, ItemImage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'items_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    
    def items_count(self, obj):
        return obj.items.count()
    
    items_count.short_description = 'Кол-во лотов'


# НАСТРОЙКА INLINE ДЛЯ СТАВОК (внутри лота)
class BidInline(admin.TabularInline):
    model = Bid
    extra = 0
    fields = ['bidder', 'amount', 'created_at', 'is_winning_bid']
    readonly_fields = ['created_at']


# НАСТРОЙКА INLINE ДЛЯ ДОПОЛНИТЕЛЬНЫХ ФОТОГРАФИЙ (внутри лота)
class ItemImageInline(admin.TabularInline):
    model = ItemImage
    extra = 3  # Показывает 3 пустых поля для загрузки новых фото по умолчанию
    fields = ['image']


# НАСТРОЙКА АДМИНКИ ДЛЯ ЛОТОВ
@admin.register(AuctionItem)
class AuctionItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'current_price', 'status', 'start_time', 'end_time']
    list_filter = ['status', 'category']
    # Исправлено: seller__username (двойное подчеркивание для поиска по связанной модели User)
    search_fields = ['title', 'description', 'seller__username']
    readonly_fields = ['current_price', 'created_at', 'updated_at']
    
    # Подключаем оба inline-блока: и ставки, и дополнительные фотографии
    inlines = [BidInline, ItemImageInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'category', 'seller', 'main_image')
        }),
        ('Цена и ставки', {
            'fields': ('start_price', 'current_price', 'min_bid_step')
        }),
        ('Время', {
            'fields': ('start_time', 'end_time')
        }),
        ('Статус', {
            'fields': ('status', 'winner')
        }),
    )


# НАСТРОЙКА АДМИНКИ ДЛЯ СТАВОК
@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ['item', 'bidder', 'amount', 'created_at', 'is_winning_bid']
    list_filter = ['is_winning_bid', 'created_at']
    # Исправлено: item__title и bidder__username (двойное подчеркивание)
    search_fields = ['item__title', 'bidder__username']


# НАСТРОЙКА АДМИНКИ ДЛЯ СПИСКОВ ОТСЛЕЖИВАНИЯ
@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'item', 'added_at']
    # Исправлено: user__username и item__title (двойное подчеркивание)
    search_fields = ['user__username', 'item__title']