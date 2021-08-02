from django.urls import path
from .views import excluirMovi, getAll, getEditar, index, filtroConsulta, filtroMovimento, movimento, finalizarMov, acompanhamentoMov,filtroSubgrupo


urlpatterns = [
    path('insert', index, name="index"),
    path('', filtroConsulta, name="filtro_consulta"),
    path('movimento', movimento),
    path('filtroMovimento', filtroMovimento, name="filtro_teste"),
    path('fimMovimento', finalizarMov),
    path('listaMov', acompanhamentoMov),
    path('filtroSubgrupo', filtroSubgrupo),
    path('visualizarMov', getAll), # Pega todos os produtos lançados para um movimento
    path('getEditar', getEditar), # Pega os dados do cabeçalho da movimentação para inclusão ou alteração dos dados
    path('excluirMovi', excluirMovi), # Ecluir os itens e o cabeçalho da movimentação 

]
