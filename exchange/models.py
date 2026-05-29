from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=150, blank=True)
    profile_picture = models.URLField(max_length=500, blank=True)

    # Google OAuth fields
    google_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    google_access_token = models.TextField(blank=True)
    google_refresh_token = models.TextField(blank=True)

    # User status
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.display_name or self.email

    def get_short_name(self):
        return self.display_name or self.email.split('@')[0]


class UserDevice(models.Model):
    """Track user devices for single device login enforcement"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    device_id = models.CharField(max_length=255, help_text='Unique device identifier')
    device_name = models.CharField(max_length=255, blank=True, help_text='e.g., iPhone 12, Samsung Galaxy')
    device_type = models.CharField(max_length=50, blank=True, help_text='e.g., ios, android, web')
    fcm_token = models.TextField(blank=True, help_text='Firebase Cloud Messaging token for push notifications')

    # Session management
    is_active = models.BooleanField(default=True, help_text='Only one device can be active at a time')
    access_token = models.TextField(blank=True, help_text='JWT access token for this device')
    refresh_token = models.TextField(blank=True, help_text='JWT refresh token for this device')

    # Timestamps
    last_login = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_login']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'device_id'],
                name='unique_user_device',
            )
        ]

    def __str__(self):
        return f'{self.user.email} - {self.device_name or self.device_id}'


class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=80)
    symbol = models.CharField(max_length=8)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'code']
        verbose_name_plural = 'Currencies'

    def __str__(self):
        return f'{self.code} - {self.name}'


class ExchangeRate(models.Model):
    currency = models.OneToOneField(
        Currency,
        on_delete=models.CASCADE,
        related_name='exchange_rate',
    )
    buy_rate = models.DecimalField(
        max_digits=16,
        decimal_places=4,
        help_text='MMK amount needed to buy 1 unit of this currency.',
    )
    sell_rate = models.DecimalField(
        max_digits=16,
        decimal_places=4,
        help_text='MMK amount paid when selling 1 unit of this currency.',
    )
    change_percentage = models.DecimalField(
        max_digits=7,
        decimal_places=3,
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['currency__sort_order', 'currency__code']

    def __str__(self):
        return f'{self.currency.code}: buy {self.buy_rate} / sell {self.sell_rate}'

    def save(self, *args, **kwargs):
        self.last_updated = timezone.now()
        super().save(*args, **kwargs)

    def to_api_dict(self):
        return {
            'currency_code': self.currency.code,
            'currency_name': self.currency.name,
            'currency_symbol': self.currency.symbol,
            'buy_rate': float(self.buy_rate),
            'sell_rate': float(self.sell_rate),
            'buy_tiers': [
                tier.to_api_dict()
                for tier in self.tiers.filter(
                    direction=ExchangeRateTier.DIRECTION_BUY,
                    is_active=True,
                )
            ],
            'sell_tiers': [
                tier.to_api_dict()
                for tier in self.tiers.filter(
                    direction=ExchangeRateTier.DIRECTION_SELL,
                    is_active=True,
                )
            ],
            'last_updated': self.last_updated.isoformat(),
            'change_percentage': (
                float(self.change_percentage)
                if self.change_percentage is not None
                else None
            ),
        }

    def rate_for_amount(self, direction, amount):
        tier = (
            self.tiers.filter(
                direction=direction,
                is_active=True,
                min_amount__lte=amount,
            )
            .filter(models.Q(max_amount__isnull=True) | models.Q(max_amount__gte=amount))
            .order_by('-min_amount')
            .first()
        )
        if tier:
            return tier.rate
        if direction == ExchangeRateTier.DIRECTION_BUY:
            return self.buy_rate
        return self.sell_rate


class ExchangeRateTier(models.Model):
    DIRECTION_BUY = 'buy'
    DIRECTION_SELL = 'sell'
    DIRECTION_CHOICES = [
        (DIRECTION_BUY, 'Buy foreign currency with MMK'),
        (DIRECTION_SELL, 'Sell foreign currency for MMK'),
    ]

    exchange_rate = models.ForeignKey(
        ExchangeRate,
        on_delete=models.CASCADE,
        related_name='tiers',
    )
    direction = models.CharField(max_length=8, choices=DIRECTION_CHOICES)
    min_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        help_text='Buy tiers use MMK amount. Sell tiers use foreign currency amount.',
    )
    max_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Leave empty for no upper limit.',
    )
    rate = models.DecimalField(max_digits=16, decimal_places=4)
    label = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'direction', 'min_amount']
        constraints = [
            models.UniqueConstraint(
                fields=['exchange_rate', 'direction', 'min_amount', 'max_amount'],
                name='unique_exchange_rate_tier_range',
            )
        ]

    def __str__(self):
        return f'{self.exchange_rate.currency.code} {self.direction}: {self.range_label}'

    @property
    def range_label(self):
        if self.max_amount is None:
            return f'{self.min_amount}+'
        return f'{self.min_amount} - {self.max_amount}'

    def to_api_dict(self):
        return {
            'direction': self.direction,
            'min_amount': float(self.min_amount),
            'max_amount': float(self.max_amount) if self.max_amount is not None else None,
            'rate': float(self.rate),
            'label': self.label or self.range_label,
        }


class ExchangeOrder(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    DIRECTION_BUY = 'buy'
    DIRECTION_SELL = 'sell'
    DIRECTION_CHOICES = [
        (DIRECTION_BUY, 'Customer buys foreign currency with MMK'),
        (DIRECTION_SELL, 'Customer sells foreign currency for MMK'),
    ]

    customer_name = models.CharField(max_length=120)
    customer_phone = models.CharField(max_length=40)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    direction = models.CharField(max_length=8, choices=DIRECTION_CHOICES)
    foreign_amount = models.DecimalField(max_digits=16, decimal_places=4)
    mmk_amount = models.DecimalField(max_digits=18, decimal_places=2)
    rate_used = models.DecimalField(max_digits=16, decimal_places=4)
    status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.customer_name} {self.direction} {self.currency.code}'


class LotteryDraw(models.Model):
    name = models.CharField(max_length=120)
    draw_date = models.DateField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-draw_date']

    def __str__(self):
        return f'{self.name} ({self.draw_date})'


class LotteryTicket(models.Model):
    STATUS_AVAILABLE = 'available'
    STATUS_RESERVED = 'reserved'
    STATUS_SOLD = 'sold'
    STATUS_INACTIVE = 'inactive'
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, 'Available'),
        (STATUS_RESERVED, 'Reserved'),
        (STATUS_SOLD, 'Sold'),
        (STATUS_INACTIVE, 'Inactive'),
    ]

    BUNDLE_SIZE_CHOICES = [
        (1, '1 ticket'),
        (2, '2 ticket bundle'),
        (5, '5 ticket bundle'),
        (10, '10 ticket bundle'),
    ]

    draw = models.ForeignKey(
        LotteryDraw,
        on_delete=models.CASCADE,
        related_name='tickets',
    )
    number = models.CharField(max_length=6)
    bundle_size = models.PositiveSmallIntegerField(choices=BUNDLE_SIZE_CHOICES)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default=STATUS_AVAILABLE,
    )
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['draw', 'number', 'bundle_size']
        constraints = [
            models.UniqueConstraint(
                fields=['draw', 'number', 'bundle_size'],
                name='unique_lottery_ticket_bundle_per_draw',
            )
        ]

    def __str__(self):
        return f'{self.draw.draw_date} - {self.number} ({self.bundle_size})'


class CommunicationChannel(models.Model):
    """
    Communication channels for customer support and exchange inquiries.
    Examples: Facebook, Telegram, Viber, WhatsApp, etc.
    """
    PLATFORM_FACEBOOK = 'facebook'
    PLATFORM_MESSENGER = 'messenger'
    PLATFORM_TELEGRAM = 'telegram'
    PLATFORM_VIBER = 'viber'
    PLATFORM_WHATSAPP = 'whatsapp'
    PLATFORM_LINE = 'line'
    PLATFORM_WECHAT = 'wechat'
    PLATFORM_OTHER = 'other'

    PLATFORM_CHOICES = [
        (PLATFORM_FACEBOOK, 'Facebook'),
        (PLATFORM_MESSENGER, 'Facebook Messenger'),
        (PLATFORM_TELEGRAM, 'Telegram'),
        (PLATFORM_VIBER, 'Viber'),
        (PLATFORM_WHATSAPP, 'WhatsApp'),
        (PLATFORM_LINE, 'LINE'),
        (PLATFORM_WECHAT, 'WeChat'),
        (PLATFORM_OTHER, 'Other'),
    ]

    name = models.CharField(
        max_length=100,
        help_text='Display name for the channel (e.g., "Facebook Group", "Telegram Support")'
    )
    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES,
        default=PLATFORM_OTHER,
        help_text='Platform type'
    )
    url = models.URLField(
        max_length=500,
        help_text='URL to redirect users (e.g., Facebook group link, Telegram bot link)'
    )
    icon_url = models.URLField(
        max_length=500,
        blank=True,
        help_text='URL to channel icon/logo (optional, can use default platform icons)'
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        help_text='Short description (e.g., "Chat with us on Facebook")'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Show this channel to users'
    )
    sort_order = models.PositiveSmallIntegerField(
        default=0,
        help_text='Display order (lower numbers appear first)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = 'Communication Channel'
        verbose_name_plural = 'Communication Channels'

    def __str__(self):
        return f'{self.name} ({self.get_platform_display()})'

    def to_api_dict(self):
        """Serialize for API response"""
        return {
            'id': self.id,
            'name': self.name,
            'platform': self.platform,
            'platform_display': self.get_platform_display(),
            'url': self.url,
            'icon_url': self.icon_url or self.get_default_icon_url(),
            'description': self.description,
            'sort_order': self.sort_order,
        }

    def get_default_icon_url(self):
        """Return default icon URL based on platform"""
        # These are placeholder URLs - you can replace with actual CDN URLs later
        icons = {
            self.PLATFORM_FACEBOOK: 'https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg',
            self.PLATFORM_MESSENGER: 'https://upload.wikimedia.org/wikipedia/commons/b/be/Facebook_Messenger_logo_2020.svg',
            self.PLATFORM_TELEGRAM: 'https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg',
            self.PLATFORM_VIBER: 'https://upload.wikimedia.org/wikipedia/commons/7/7a/Viber_logo.svg',
            self.PLATFORM_WHATSAPP: 'https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg',
            self.PLATFORM_LINE: 'https://upload.wikimedia.org/wikipedia/commons/4/41/LINE_logo.svg',
            self.PLATFORM_WECHAT: 'https://upload.wikimedia.org/wikipedia/commons/1/12/WeChat_logo.svg',
        }
        return icons.get(self.platform, '')
