# Generated by Django 4.2 on 2023-04-22 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0002_transaction_currency_user_groups_user_is_active_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='balance',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]