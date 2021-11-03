from import_export import resources
from .models import Movimentacao, Itemmovimentado

class MovimentacaoResource(resources.ModelResource):
    class Meta:
        model = Movimentacao