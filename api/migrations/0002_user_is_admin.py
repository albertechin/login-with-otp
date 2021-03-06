# Generated by Django 3.2.7 on 2021-09-18 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_admin',
            field=models.BooleanField(default=False, help_text='Designates whether the user is admin/superuser.', verbose_name='admin status'),
        ),
    ]
