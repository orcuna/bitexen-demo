# Generated by Django 4.2 on 2023-04-29 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickers', '0002_alter_statsaggregation_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statsaggregation',
            name='average',
            field=models.DecimalField(blank=True, decimal_places=10, max_digits=100, null=True),
        ),
        migrations.AlterField(
            model_name='statsaggregation',
            name='high',
            field=models.DecimalField(blank=True, decimal_places=10, max_digits=100, null=True),
        ),
        migrations.AlterField(
            model_name='statsaggregation',
            name='low',
            field=models.DecimalField(blank=True, decimal_places=10, max_digits=100, null=True),
        ),
        migrations.AlterField(
            model_name='statsaggregation',
            name='volume',
            field=models.DecimalField(blank=True, decimal_places=10, max_digits=100, null=True),
        ),
    ]
