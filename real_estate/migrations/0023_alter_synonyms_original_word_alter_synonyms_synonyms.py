# Generated by Django 5.0.3 on 2024-06-17 23:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('real_estate', '0022_alter_synonyms_original_word_alter_synonyms_synonyms'),
    ]

    operations = [
        migrations.AlterField(
            model_name='synonyms',
            name='original_word',
            field=models.CharField(db_collation='utf8mb4_unicode_ci', max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='synonyms',
            name='synonyms',
            field=models.TextField(blank=True, db_collation='utf8mb4_unicode_ci', null=True),
        ),
    ]
