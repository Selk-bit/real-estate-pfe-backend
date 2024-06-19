# Generated by Django 5.0.3 on 2024-05-07 20:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authtoken', '0004_alter_tokenproxy_options'),
        ('real_estate', '0018_alter_userprofile_profile_picture'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpirableToken',
            fields=[
                ('token_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='authtoken.token')),
            ],
            bases=('authtoken.token',),
        ),
    ]
