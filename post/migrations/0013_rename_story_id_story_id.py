# Generated by Django 4.2 on 2023-05-24 14:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0012_story'),
    ]

    operations = [
        migrations.RenameField(
            model_name='story',
            old_name='story_id',
            new_name='id',
        ),
    ]
