# Generated by Django 4.2 on 2023-05-08 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_profile_gender_profile_website'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='following',
            field=models.ManyToManyField(related_name='followers', to='accounts.profile'),
        ),
    ]