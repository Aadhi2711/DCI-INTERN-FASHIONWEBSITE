# Generated by Django 5.0 on 2023-12-28 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fashionapp', '0009_alter_usercart_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercart',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
    ]
