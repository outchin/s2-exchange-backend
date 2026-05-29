from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path
from adminsortable2.admin import SortableAdminMixin

from .forms import LotteryTicketCsvImportForm
from .lottery_import import import_lottery_tickets_from_csv
from .models import (
    Currency,
    ExchangeOrder,
    ExchangeRate,
    ExchangeRateTier,
    LotteryDraw,
    LotteryTicket,
    User,
    UserDevice,
)


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'symbol', 'trading_status', 'is_active', 'sort_order', 'updated_at')
    list_editable = ('is_active', 'sort_order')
    search_fields = ('code', 'name')
    ordering = ('sort_order', 'code')
    actions = ('mark_online', 'mark_offline')

    @admin.display(description='Trading')
    def trading_status(self, obj):
        return 'Online' if obj.is_active else 'Offline'

    @admin.action(description='Mark selected currencies online')
    def mark_online(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Mark selected currencies offline')
    def mark_offline(self, request, queryset):
        queryset.update(is_active=False)


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = (
        'currency',
        'buy_rate',
        'sell_rate',
        'change_percentage',
        'trading_status',
        'is_active',
        'last_updated',
    )
    list_editable = ('buy_rate', 'sell_rate', 'change_percentage', 'is_active')
    list_filter = ('is_active', 'currency')
    search_fields = ('currency__code', 'currency__name')
    readonly_fields = ('last_updated', 'created_at', 'updated_at')
    actions = ('mark_online', 'mark_offline')
    inlines = []

    @admin.display(description='Trading')
    def trading_status(self, obj):
        return 'Online' if obj.is_active and obj.currency.is_active else 'Offline'

    @admin.action(description='Mark selected rates online')
    def mark_online(self, request, queryset):
        queryset.update(is_active=True)
        self._broadcast_rate_changes()

    @admin.action(description='Mark selected rates offline')
    def mark_offline(self, request, queryset):
        queryset.update(is_active=False)
        self._broadcast_rate_changes()

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        self._broadcast_rate_changes()

    def _broadcast_rate_changes(self):
        """Broadcast rate changes to all connected WebSocket clients"""
        from .websocket_utils import broadcast_rate_update
        rates = ExchangeRate.objects.filter(is_active=True).order_by('order')
        rates_data = [
            {
                'id': rate.id,
                'currency': rate.currency.code,
                'buy_rate': float(rate.buy_rate),
                'sell_rate': float(rate.sell_rate),
                'last_updated': rate.last_updated.isoformat() if rate.last_updated else None,
                'buy_tiers': rate.buy_tiers or [],
                'sell_tiers': rate.sell_tiers or [],
            }
            for rate in rates
        ]
        broadcast_rate_update(rates_data)


class ExchangeRateTierInline(admin.TabularInline):
    model = ExchangeRateTier
    extra = 1
    fields = (
        'direction',
        'min_amount',
        'max_amount',
        'rate',
        'label',
        'is_active',
    )


ExchangeRateAdmin.inlines = [ExchangeRateTierInline]


@admin.register(ExchangeRateTier)
class ExchangeRateTierAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = (
        'exchange_rate',
        'direction',
        'min_amount',
        'max_amount',
        'rate',
        'label',
        'is_active',
    )
    list_editable = ('rate', 'label', 'is_active')
    list_filter = ('direction', 'is_active', 'exchange_rate__currency')
    search_fields = ('exchange_rate__currency__code', 'label')


@admin.register(ExchangeOrder)
class ExchangeOrderAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'customer_name',
        'customer_phone',
        'currency',
        'direction',
        'foreign_amount',
        'mmk_amount',
        'status',
    )
    list_filter = ('status', 'direction', 'currency')
    search_fields = ('customer_name', 'customer_phone', 'note')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'


@admin.register(LotteryDraw)
class LotteryDrawAdmin(admin.ModelAdmin):
    list_display = ('draw_date', 'name', 'is_active', 'ticket_count', 'updated_at')
    list_editable = ('is_active',)
    search_fields = ('name',)
    ordering = ('-draw_date',)

    @admin.display(description='Tickets')
    def ticket_count(self, obj):
        return obj.tickets.count()


@admin.register(LotteryTicket)
class LotteryTicketAdmin(admin.ModelAdmin):
    change_list_template = 'admin/exchange/lotteryticket/change_list.html'
    list_display = (
        'draw',
        'number',
        'bundle_size',
        'quantity',
        'price',
        'status',
        'updated_at',
    )
    list_editable = ('quantity', 'price', 'status')
    list_filter = ('draw', 'bundle_size', 'status')
    search_fields = ('number', 'draw__name')
    ordering = ('-draw__draw_date', 'number', 'bundle_size')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'import-csv/',
                self.admin_site.admin_view(self.import_csv),
                name='exchange_lotteryticket_import_csv',
            ),
        ]
        return custom_urls + urls

    def import_csv(self, request):
        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'title': 'Import lottery tickets from CSV',
            'required_columns': 'draw_date, number, bundle_size, quantity, price',
            'optional_columns': 'draw_name, status, note',
            'sample_csv': (
                'draw_date,draw_name,number,bundle_size,quantity,price,status,note\n'
                '2026-06-01,Thai Lottery - 2026-06-01,001234,1,10,120,available,\n'
                '2026-06-01,Thai Lottery - 2026-06-01,123456,2,5,240,available,2 ticket bundle\n'
                '2026-06-01,Thai Lottery - 2026-06-01,234567,5,2,600,available,5 ticket bundle\n'
                '2026-06-01,Thai Lottery - 2026-06-01,345678,10,1,1200,available,10 ticket bundle'
            ),
        }

        if request.method == 'POST':
            form = LotteryTicketCsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                summary = import_lottery_tickets_from_csv(
                    form.cleaned_data['csv_file']
                )
                context['summary'] = summary
                if summary.total_errors:
                    messages.warning(
                        request,
                        (
                            'CSV import finished with '
                            f'{summary.total_errors} validation error(s).'
                        ),
                    )
                else:
                    messages.success(request, 'CSV import completed successfully.')
                    return redirect('..')
        else:
            form = LotteryTicketCsvImportForm()

        context['form'] = form
        return TemplateResponse(
            request,
            'admin/exchange/lotteryticket/import_csv.html',
            context,
        )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'email',
        'display_name',
        'is_staff',
        'is_active',
        'date_joined',
        'last_login',
    )
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('email', 'display_name', 'google_id')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login', 'google_id')

    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        ('Personal Info', {
            'fields': ('display_name', 'profile_picture')
        }),
        ('Google OAuth', {
            'fields': ('google_id', 'google_access_token', 'google_refresh_token'),
            'classes': ('collapse',),
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'display_name', 'is_staff', 'is_active'),
        }),
    )


@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'device_name',
        'device_type',
        'is_active',
        'last_login',
        'created_at',
    )
    list_filter = ('is_active', 'device_type', 'created_at')
    search_fields = ('user__email', 'device_id', 'device_name')
    readonly_fields = ('device_id', 'last_login', 'created_at', 'updated_at')
    ordering = ('-last_login',)

    fieldsets = (
        (None, {
            'fields': ('user', 'device_id', 'device_name', 'device_type')
        }),
        ('Session', {
            'fields': ('is_active', 'fcm_token'),
        }),
        ('Tokens', {
            'fields': ('access_token', 'refresh_token'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('last_login', 'created_at', 'updated_at')
        }),
    )
