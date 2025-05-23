# Generated by Django 5.1.5 on 2025-03-27 12:34

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imagemproduto',
            name='ordem',
            field=models.IntegerField(blank=True, null=True, verbose_name='Ordem'),
        ),
        migrations.CreateModel(
            name='MovimentoEstoque',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade', models.IntegerField(verbose_name='Quantidade')),
                ('tipo', models.CharField(choices=[('entrada', 'Entrada'), ('saida', 'Saída'), ('ajuste', 'Ajuste')], max_length=10, verbose_name='Tipo de Movimento')),
                ('data', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Data do Movimento')),
                ('observacao', models.TextField(blank=True, null=True, verbose_name='Observação')),
                ('produto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='movimentos_estoque', to='produtos.produto')),
            ],
            options={
                'verbose_name': 'Movimento de Estoque',
                'verbose_name_plural': 'Movimentos de Estoque',
                'ordering': ['-data'],
            },
        ),
    ]
