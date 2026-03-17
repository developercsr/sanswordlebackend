# Generated manually for Word Upload feature

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('words', '0005_remove_word_chapter_name_remove_word_class_name_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='word',
            name='class_name',
            field=models.TextField(blank=True, default='[]'),
        ),
        migrations.AddField(
            model_name='word',
            name='chapter',
            field=models.TextField(blank=True, default='[]'),
        ),
        migrations.AddField(
            model_name='word',
            name='is_rejected',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='word',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='word',
            name='approved_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='approved_words',
                to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
