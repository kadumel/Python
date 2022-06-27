from pyexpat import model
from django.db import models
from django.contrib.auth.models import User
from django.db.models.expressions import OrderBy

GENDER_CHOICES = (
    ('A', 'Ativo'),
    ('I', 'Inativo'),
)

class Grupo(models.Model):
    cdgrupo = models.AutoField(db_column='cdGrupo', primary_key=True)  # Field name made lowercase.
    nmgrupo = models.CharField(db_column='nmGrupo', max_length=70, blank=True, null=True)  # Field name made lowercase.


    class Meta:
        managed = False
        db_table = 'Grupo'

    def __str__(self):
        return self.nmgrupo


class Subgrupo(models.Model):
    cdsubgrupo = models.AutoField(db_column='cdSubGrupo', primary_key=True)  # Field name made lowercase.
    nmsubgrupo = models.CharField(db_column='nmSubGrupo', max_length=70, blank=True, null=True)  # Field name made lowercase.
    cdGrupo = models.ForeignKey("Grupo",on_delete=models.PROTECT)

    class Meta:
        managed = False
        db_table = 'SubGrupo'

    def __str__(self):
        return self.nmsubgrupo



class Loja(models.Model):
    cdloja = models.AutoField(db_column='cdLoja', primary_key=True)  # Field name made lowercase.
    cnpj = models.CharField(max_length=18, blank=True, null=True)
    nmloja = models.CharField(db_column='nmLoja', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Loja'

    def __str__(self):
        return self.nmloja

class Tipomovimento(models.Model):
    cdtipomovimento = models.AutoField(db_column='cdTipoMovimento', primary_key=True)  # Field name made lowercase.
    nmtipomovimento = models.CharField(db_column='nmTipoMovimento', max_length=70, blank=True, null=True)  # Field name made lowercase.
    conversao = models.CharField(max_length=1, choices=GENDER_CHOICES)
    class Meta:
        managed = False
        db_table = 'TipoMovimento'

    def __str__(self):
        return '{} - {}'.format(self.nmtipomovimento, self.conversao)

class Movimentacao(models.Model):
    cdmovimentacao = models.AutoField(db_column='cdMovimentacao', primary_key=True)  # Field name made lowercase.
    cdtipomovimento = models.ForeignKey("Tipomovimento",models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    cdloja = models.ForeignKey("Loja",models.PROTECT)
    dtmovimentacao = models.DateTimeField(auto_now_add=False)  # Field name made lowercase.
    dtAlteracao = models.DateTimeField(auto_now=True)  # Field name made lowercase.
    status = models.ForeignKey("Status",models.PROTECT)
    class Meta:
        managed = False
        db_table = 'Movimentacao'

    def __str__(self):
        return '{} - {}  -  {} - {}  -  {}'.format(self.cdmovimentacao, self.user.username, self.dtmovimentacao, self.status, self.cdloja.nmloja)

class Itemmovimentado(models.Model):
    cditemmovimentado = models.AutoField(db_column='cdItemMovimentado', primary_key=True)  # Field name made lowercase.
    cdmovimentacao = models.ForeignKey("Movimentacao",models.PROTECT)
    cdproduto = models.ForeignKey("Produto",models.PROTECT)
    valor = models.FloatField()
    cdunidade = models.ForeignKey("TipoUnidade", on_delete=models.PROTECT)
    valorLiquido = models.FloatField()

    class Meta:
        managed = False
        db_table = 'ItemMovimentado'


class Acesso(models.Model):
    cdacesso = models.AutoField(db_column='cdAcesso',primary_key=True)  # Field name made lowercase.
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    cdloja = models.ForeignKey('Loja',on_delete=models.PROTECT)

    class Meta:
        managed = False
        ordering = ['user__username']
        db_table = 'Acesso'

    def __str__(self):
        return '{} - {}'.format(self.user.username, self.cdloja.nmloja)

class Produto(models.Model):
    cdproduto = models.AutoField(db_column='cdProduto', primary_key=True)  # Field name made lowercase.
    idproduto = models.IntegerField(db_column='idProduto', blank=True, null=True)  # Field name made lowercase.
    # cdgrupo = models.IntegerField(db_column='cdGrupo', blank=True, null=True)  # Field name made lowercase.
    cdsubgrupo = models.ForeignKey("Subgrupo", on_delete=models.PROTECT)
    nmproduto = models.CharField(db_column='nmProduto', max_length=70, blank=True, null=True)
    cdunidade = models.ForeignKey("TipoUnidade", on_delete=models.PROTECT)
    ativo = models.CharField(max_length=1, choices=GENDER_CHOICES)
    cduniconv = models.ForeignKey("TipoUnidade", on_delete=models.PROTECT, related_name='Conversao')
    vlconv = models.FloatField()
    percPerda = models.FloatField(db_column='percPerdaDesc', blank=True, null=True)
    cdunipadrao = models.ForeignKey("TipoUnidade", on_delete=models.PROTECT, related_name='Padrao')
    class Meta:
        managed = False
        ordering = ['nmproduto']
        db_table = 'Produto'

    def __str__(self):
        return '{}  -  {}  -  {}'.format(self.nmproduto, self.cdsubgrupo.cdGrupo.nmgrupo, self.cdsubgrupo.nmsubgrupo )


class TipoUnidade(models.Model):
    cdUnidade = models.AutoField(db_column='cdUnidade', primary_key=True)  # Field name made lowercase.
    nmUnidade = models.CharField(db_column='nmUnidade', max_length=5, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TipoUnidade'

    def __str__(self):
        return self.nmUnidade



class Status(models.Model):
    cdStatus = models.AutoField(db_column='cdStatus', primary_key=True)  # Field name made lowercase.
    nmStatus = models.CharField(db_column='nmStatus', max_length=30, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Status'

    def __str__(self):
        return self.nmStatus

class Ocorrencia(models.Model):
    cdOcorrencia = models.AutoField(db_column='cdOcorrencia', primary_key=True)
    cdMovimentacao = models.ForeignKey("Movimentacao", on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    dtOcorrencia = models.DateTimeField(auto_now_add=True)
    dsOcorrencia = models.CharField(db_column='dsOcorrencia', max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Ocorrencia'

    def __str__(self):
         return '{}  -  {}  -  {}  -  {}'.format(self.cdMovimentacao.cdmovimentacao, self.user.username, self.dtOcorrencia, self.dsOcorrencia )


class importa_de_para(models.Model):
    dtimportacao = models.DateField(auto_now_add=False)
    cdloja = models.IntegerField()
    nmprodutocliente = models.CharField(max_length=255)
    cdproduto = models.IntegerField()

    class Meta:
        managed = False
        db_table = "importa_de_para"