# Generated by Django 4.2 on 2023-04-29 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickers', '0003_alter_statsaggregation_average_and_more'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='statsaggregation',
            index_together=set(),
        ),
        migrations.AddField(
            model_name='statsaggregation',
            name='is_final',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='statsaggregation',
            unique_together={('full_name', 'type', 'time')},
        ),
        migrations.AlterIndexTogether(
            name='statsaggregation',
            index_together={('full_name', 'type', 'time', 'is_final')},
        ),
    ]
