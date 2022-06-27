# Generated by Django 3.2.2 on 2022-05-21 00:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_importadepara_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='importadepara',
            old_name='cdLoja',
            new_name='cdloja',
        ),
        migrations.RenameField(
            model_name='importadepara',
            old_name='cdProduto',
            new_name='cdproduto',
        ),
        migrations.RenameField(
            model_name='importadepara',
            old_name='dataImportacao',
            new_name='data_importacao',
        ),
        migrations.RenameField(
            model_name='importadepara',
            old_name='produtoLoja',
            new_name='produtoloja',
        ),
        migrations.AlterField(
            model_name='importadepara',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterModelTable(
            name='importadepara',
            table=None,
        ),
    ]