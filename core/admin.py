from django.contrib import admin
from .models import Acesso, Grupo, Itemmovimentado, Loja,Movimentacao, Perfil, Produto, Subgrupo, Tipomovimento, Status
# Register your models here.

admin.site.register(Acesso)
admin.site.register(Grupo)
admin.site.register(Itemmovimentado)
admin.site.register(Loja)
admin.site.register(Movimentacao)
admin.site.register(Produto)
admin.site.register(Subgrupo)
admin.site.register(Tipomovimento)
admin.site.register(Status)