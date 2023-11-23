# Generated by Django 4.2.7 on 2023-11-23 17:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_block_hash_block_noune'),
    ]

    operations = [
        migrations.RenameField(
            model_name='block',
            old_name='noune',
            new_name='nonce',
        ),
        migrations.AlterField(
            model_name='transaction',
            name='amount',
            field=models.DecimalField(decimal_places=5, max_digits=20),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='recipient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='recipient_account', to='app.account'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sender_account', to='app.account'),
        ),
    ]
