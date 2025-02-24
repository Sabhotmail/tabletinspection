# Generated by Django 5.1.3 on 2025-01-27 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inspection', '0002_alter_deviceinspection_sn_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deviceinspection',
            name='bag_status',
            field=models.CharField(blank=True, choices=[('ปกติ', 'ปกติ'), ('ชำรุด', 'ชำรุด'), ('ศูนย์หาย', 'ศูนย์หาย')], default='ปกติ', max_length=10, null=True, verbose_name='Bag Status'),
        ),
        migrations.AlterField(
            model_name='deviceinspection',
            name='charger_status_printer',
            field=models.CharField(choices=[('ปกติ', 'ปกติ'), ('ชำรุด', 'ชำรุด'), ('ศูนย์หาย', 'ศูนย์หาย')], default='ปกติ', max_length=10, verbose_name='Printer Charger Status'),
        ),
        migrations.AlterField(
            model_name='deviceinspection',
            name='charger_status_tablet',
            field=models.CharField(choices=[('ปกติ', 'ปกติ'), ('ชำรุด', 'ชำรุด'), ('ศูนย์หาย', 'ศูนย์หาย')], default='ปกติ', max_length=10, verbose_name='Tablet Charger Status'),
        ),
        migrations.AlterField(
            model_name='deviceinspection',
            name='condition',
            field=models.CharField(choices=[('ปกติ', 'ปกติ'), ('ชำรุด', 'ชำรุด'), ('ศูนย์หาย', 'ศูนย์หาย')], max_length=10),
        ),
    ]
