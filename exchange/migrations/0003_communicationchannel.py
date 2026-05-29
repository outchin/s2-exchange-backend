# Generated manually for CommunicationChannel model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0002_alter_exchangeratetier_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommunicationChannel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Display name for the channel (e.g., "Facebook Group", "Telegram Support")', max_length=100)),
                ('platform', models.CharField(choices=[('facebook', 'Facebook'), ('messenger', 'Facebook Messenger'), ('telegram', 'Telegram'), ('viber', 'Viber'), ('whatsapp', 'WhatsApp'), ('line', 'LINE'), ('wechat', 'WeChat'), ('other', 'Other')], default='other', help_text='Platform type', max_length=20)),
                ('url', models.URLField(help_text='URL to redirect users (e.g., Facebook group link, Telegram bot link)', max_length=500)),
                ('icon_url', models.URLField(blank=True, help_text='URL to channel icon/logo (optional, can use default platform icons)', max_length=500)),
                ('description', models.CharField(blank=True, help_text='Short description (e.g., "Chat with us on Facebook")', max_length=255)),
                ('is_active', models.BooleanField(default=True, help_text='Show this channel to users')),
                ('sort_order', models.PositiveSmallIntegerField(default=0, help_text='Display order (lower numbers appear first)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Communication Channel',
                'verbose_name_plural': 'Communication Channels',
                'ordering': ['sort_order', 'name'],
            },
        ),
    ]
