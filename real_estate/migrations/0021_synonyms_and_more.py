# Generated by Django 5.0.3 on 2024-06-17 05:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('real_estate', '0020_remove_userprofile_id_alter_userprofile_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Synonyms',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_word', models.CharField(max_length=255, unique=True)),
                ('synonyms', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.AddConstraint(
            model_name='synonyms',
            constraint=models.UniqueConstraint(fields=('original_word',), name='unique_original_word_case_insensitive'),
        ),
    ]
