# Generated by Django 4.2.7 on 2023-11-23 18:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_rename_noune_block_nonce_alter_transaction_amount_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='block',
            name='hash',
        ),
    ]
