# Generated by Django 5.1.2 on 2024-11-08 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0004_alter_bank_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.IntegerField(choices=[(1, 'Deposit'), (2, 'Withdraw'), (3, 'Loan'), (4, 'Loan Paid'), (5, 'Money Transfer')], null=True),
        ),
    ]
