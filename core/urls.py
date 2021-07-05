from django.urls import path
from .views import index, filtroConsulta, filtroMovimento, movimento, finalizarMov, acompanhamentoMov

urlpatterns = [
    path('', index, name="index"),
    path('filtro', filtroConsulta, name="filtro_consulta"),
    path('filtroMovimento', filtroMovimento, name="filtro_teste"),
    path('movimento', movimento),
    path('fimMovimento', finalizarMov),
    path('listaMov', acompanhamentoMov),

]