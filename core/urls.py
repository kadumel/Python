from django.urls import path
from .views import index, filtroConsulta, filtroMovimento, movimento, finalizarMov, acompanhamentoMov,filtroSubgrupo


urlpatterns = [
    path('insert', index, name="index"),
    path('', filtroConsulta, name="filtro_consulta"),
    path('movimento', movimento),
    path('filtroMovimento', filtroMovimento, name="filtro_teste"),
    path('fimMovimento', finalizarMov),
    path('listaMov', acompanhamentoMov),
    path('filtroSubgrupo', filtroSubgrupo),

]
