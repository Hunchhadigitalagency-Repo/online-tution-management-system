# Generated by Django 5.0.3 on 2024-04-02 07:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tution', '0011_paymentdetails'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PaymentDetails',
            new_name='PaymentDetail',
        ),
    ]