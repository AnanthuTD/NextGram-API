# Generated by Django 4.2 on 2024-02-27 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_interest'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='interests',
            field=models.ManyToManyField(related_name='profiles', to='accounts.interest'),
        ),
    ]