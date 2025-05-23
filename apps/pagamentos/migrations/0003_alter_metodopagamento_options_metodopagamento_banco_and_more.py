# Generated by Django 5.1.5 on 2025-04-02 18:07

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pagamentos', '0002_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='metodopagamento',
            options={'ordering': ['ordem', 'nome'], 'verbose_name': 'Método de Pagamento', 'verbose_name_plural': 'Métodos de Pagamento'},
        ),
        migrations.AddField(
            model_name='metodopagamento',
            name='banco',
            field=models.CharField(blank=True, choices=[('', '-- Selecione um Banco --'), ('bai', 'Banco Angolano de Investimentos (BAI)'), ('bfa', 'Banco de Fomento Angola (BFA)'), ('bic', 'Banco BIC'), ('bpc', 'Banco de Poupança e Crédito (BPC)'), ('atlantico', 'Banco Atlântico'), ('bda', 'Banco de Desenvolvimento de Angola (BDA)'), ('bni', 'Banco de Negócios Internacional (BNI)'), ('keve', 'Banco Keve'), ('sol', 'Banco Sol'), ('millennium', 'Millennium Atlântico'), ('outro', 'Outro')], help_text='Selecione o banco para métodos de pagamento bancário', max_length=30, null=True, verbose_name='Banco'),
        ),
        migrations.AddField(
            model_name='metodopagamento',
            name='data_atualizacao',
            field=models.DateTimeField(auto_now=True, verbose_name='Última Atualização'),
        ),
        migrations.AddField(
            model_name='metodopagamento',
            name='data_criacao',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Data de Criação'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='metodopagamento',
            name='iban',
            field=models.CharField(blank=True, help_text='IBAN para transferências bancárias internacionais', max_length=50, null=True, verbose_name='IBAN'),
        ),
        migrations.AddField(
            model_name='metodopagamento',
            name='imagem',
            field=models.ImageField(blank=True, help_text='Logo ou imagem do método de pagamento', null=True, upload_to='metodos_pagamento/', verbose_name='Imagem/Logo'),
        ),
        migrations.AddField(
            model_name='metodopagamento',
            name='instrucoes',
            field=models.TextField(blank=True, help_text='Instruções detalhadas sobre como utilizar este método de pagamento', null=True, verbose_name='Instruções de Pagamento'),
        ),
        migrations.AddField(
            model_name='metodopagamento',
            name='mostrar_na_loja',
            field=models.BooleanField(default=True, help_text='Se este método deve aparecer como opção para clientes durante o checkout', verbose_name='Mostrar na Loja'),
        ),
        migrations.AddField(
            model_name='metodopagamento',
            name='numero_conta',
            field=models.CharField(blank=True, help_text='Número da conta para transferências bancárias', max_length=30, null=True, verbose_name='Número da Conta'),
        ),
        migrations.AddField(
            model_name='metodopagamento',
            name='ordem',
            field=models.PositiveSmallIntegerField(default=0, help_text='Ordem em que este método aparece na loja (menor = primeiro)', verbose_name='Ordem de Exibição'),
        ),
        migrations.AddField(
            model_name='metodopagamento',
            name='taxa_fixa',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Valor fixo (AOA) cobrado por este método de pagamento', max_digits=10, verbose_name='Taxa Fixa'),
        ),
        migrations.AddField(
            model_name='metodopagamento',
            name='tipo',
            field=models.CharField(choices=[('transferencia_bancaria', 'Transferência Bancária'), ('multicaixa_express', 'Multicaixa Express'), ('dinheiro', 'Dinheiro na Entrega'), ('paypal', 'PayPal'), ('referencia', 'Referência Bancária'), ('outro', 'Outro')], default='transferencia_bancaria', max_length=50, verbose_name='Tipo de Pagamento'),
        ),
        migrations.AddField(
            model_name='metodopagamento',
            name='titular_conta',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Titular da Conta'),
        ),
        migrations.AddField(
            model_name='metodopagamento',
            name='valor_maximo',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Valor máximo (AOA) para aceitar este método de pagamento (0 = sem limite)', max_digits=10, verbose_name='Valor Máximo'),
        ),
        migrations.AddField(
            model_name='metodopagamento',
            name='valor_minimo',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Valor mínimo (AOA) para aceitar este método de pagamento', max_digits=10, verbose_name='Valor Mínimo'),
        ),
        migrations.AlterField(
            model_name='metodopagamento',
            name='taxa',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Taxa em percentagem (%) cobrada por este método de pagamento', max_digits=5, verbose_name='Taxa'),
        ),
    ]
