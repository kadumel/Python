# Generated by Django 3.2.2 on 2021-07-20 21:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20210720_1833'),
    ]

    operations = [
        
        migrations.AlterField(
            model_name='ocorrencia',
            name='dsOcorrencia',
            field=models.CharField(blank=True, db_column='dsOcorrencia', max_length=255, null=True),
        ),
      
    ]
