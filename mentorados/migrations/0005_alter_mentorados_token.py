# Generated by Django 5.1.7 on 2025-04-02 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentorados', '0004_alter_mentorados_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mentorados',
            name='token',
            field=models.CharField(blank=True, default='', max_length=16),
        ),
    ]
