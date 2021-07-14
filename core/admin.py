from django.contrib import admin
from .models import Acesso, Grupo, Itemmovimentado, Loja,Movimentacao, Produto, Subgrupo, Tipomovimento, Status, TipoUnidade
# Register your models here.





admin.site.register(Acesso)
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


