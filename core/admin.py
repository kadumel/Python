from django.contrib import admin
from django.utils.html import format_html

from .models import Acesso, Grupo, Itemmovimentado, Loja,Movimentacao, Ocorrencia, Produto, Subgrupo, Tipomovimento, Status, TipoUnidade
# Register your models here.




class AcessoAdmin(admin.ModelAdmin):
    list_filter = ['user__username']

admin.site.register(Acesso, AcessoAdmin)
admin.site.register(Grupo)
admin.site.register(Itemmovimentado)
admin.site.register(Loja)
admin.site.register(Movimentacao)

class ProdutoAdmin(admin.ModelAdmin):
    search_fields = ['nmproduto']
    list_filter = ['cdsubgrupo__cdGrupo__nmgrupo', 'cdsubgrupo__nmsubgrupo']


admin.site.register(Produto, ProdutoAdmin)
admin.site.register(Subgrupo)
admin.site.register(Tipomovimento)
admin.site.register(Status)
admin.site.register(TipoUnidade)
admin.site.register(Ocorrencia)


