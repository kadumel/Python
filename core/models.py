# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import User



class Grupo(models.Model):
    cdgrupo = models.AutoField(db_column='cdGrupo', primary_key=True)  # Field name made lowercase.
    nmgrupo = models.CharField(db_column='nmGrupo', max_length=70, blank=True, null=True)  # Field name made lowercase.


    class Meta:
        managed = True
        db_table = 'Grupo'

    def __str__(self):
        return self.nmgrupo

class Loja(models.Model):
    cdloja = models.AutoField(db_column='cdLoja', primary_key=True)  # Field name made lowercase.
    cnpj = models.CharField(max_length=18, blank=True, null=True)
    nmloja = models.CharField(db_column='nmLoja', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Loja'

    def __str__(self):
        return self.nmloja

class Tipomovimento(models.Model):
    cdtipomovimento = models.AutoField(db_column='cdTipoMovimento', primary_key=True)  # Field name made lowercase.
    nmtipomovimento = models.CharField(db_column='nmTipoMovimento', max_length=70, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'TipoMovimento'

    def __str__(self):
        return self.nmtipomovimento

class Movimentacao(models.Model):
    cdmovimentacao = models.AutoField(db_column='cdMovimentacao', primary_key=True)  # Field name made lowercase.
    cdtipomovimento = models.ForeignKey("Tipomovimento",models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    cdloja = models.ForeignKey("Loja",models.PROTECT)
    dtmovimentacao = models.DateTimeField(auto_now_add=True)  # Field name made lowercase.
    dtAlteracao = models.DateTimeField(auto_now=True)  # Field name made lowercase.
    status = models.ForeignKey("Status",models.PROTECT)

    class Meta:
        managed = True
        db_table = 'Movimentacao'


class Itemmovimentado(models.Model):
    cditemmovimentado = models.AutoField(db_column='cdItemMovimentado', primary_key=True)  # Field name made lowercase.
    cdmovimentacao = models.ForeignKey("Movimentacao",models.PROTECT)
    cdproduto = models.ForeignKey("Produto",models.PROTECT)
    valor = models.FloatField()

    class Meta:
        managed = True
        db_table = 'ItemMovimentado'


class Perfil(models.Model):
    cdperfil = models.AutoField(db_column='cdPerfil', primary_key=True)  # Field name made lowercase.
    nmperfil = models.CharField(db_column='nmPerfil', max_length=30, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Perfil'

    def __str__(self):
        return  self.nmperfil

class Acesso(models.Model):
    cdacesso = models.AutoField(db_column='cdAcesso',primary_key=True)  # Field name made lowercase.
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    cdloja = models.ForeignKey('Loja',on_delete=models.PROTECT)

    class Meta:
        managed = True
        db_table = 'Acesso'

    # def __str__(self):
    #     return '({}) {}'.format(', '.join(self.user.all().values_list('code', flat=True)), self.username[:20])
    #     # return self.username

class Produto(models.Model):
    cdproduto = models.AutoField(db_column='cdProduto', primary_key=True)  # Field name made lowercase.
    idproduto = models.IntegerField(db_column='idProduto', blank=True, null=True)  # Field name made lowercase.
    # cdgrupo = models.IntegerField(db_column='cdGrupo', blank=True, null=True)  # Field name made lowercase.
    cdsubgrupo = models.ForeignKey("Subgrupo", on_delete=models.PROTECT)
    nmproduto = models.CharField(db_column='nmProduto', max_length=70, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Produto'

    def __str__(self):
        return self.cdsubgrupo_id, self.nmproduto


class Subgrupo(models.Model):
    cdsubgrupo = models.AutoField(db_column='cdSubGrupo', primary_key=True)  # Field name made lowercase.
    nmsubgrupo = models.CharField(db_column='nmSubGrupo', max_length=70, blank=True, null=True)  # Field name made lowercase.
    cdGrupo = models.ForeignKey("Grupo",on_delete=models.PROTECT)

    class Meta:
        managed = True
        db_table = 'SubGrupo'

    def __str__(self):
        return self.nmsubgrupo


class Usuario(models.Model):
    cdusuario = models.AutoField(db_column='cdUsuario', primary_key=True)  # Field name made lowercase.
    cdperfil = models.ForeignKey("Perfil",on_delete=models.PROTECT)
    nmusuario = models.CharField(db_column='nmUsuario', max_length=30, blank=True, null=True)  # Field name made lowercase.
    senha = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Usuario'


class Status(models.Model):
    cdStatus = models.AutoField(db_column='cdStatus', primary_key=True)  # Field name made lowercase.
    nmStatus = models.CharField(db_column='nmStatus', max_length=30, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Status'

