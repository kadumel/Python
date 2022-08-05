import datetime
from django.db import connection
from distutils.log import error
from urllib import request
from django.utils import datastructures
from re import L
from statistics import quantiles
import django
from django.core.exceptions import TooManyFieldsSent
from django.db.models.fields import NullBooleanField
from django.shortcuts import render, get_object_or_404, redirect
from .models import Acesso, Tipomovimento, Grupo, Subgrupo, Loja, Produto, Movimentacao, Itemmovimentado, Status, importa_de_para
from .forms import LojaForm, TipoMovientoForm, GrupoForm, SubGrupoForm, ProdutoForm
from django.http import HttpResponse, Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
import json
from datetime import datetime as dt, timedelta
from tablib import Dataset
from .resources import MovimentacaoResource
# Create your views here.


tp_mv = Tipomovimento.objects.all()
grupos = Grupo.objects.all()
subgrupos = Subgrupo.objects.all()
user = User.objects.all()
status = Status.objects.all()
listProdutos = Produto.objects.all()

@login_required
def index(request):
    print("View Index")
    tp_mvform = TipoMovientoForm()
    ljform = LojaForm
    gp_form = GrupoForm
    sbgp_form = SubGrupoForm

    lojas = adminORnormal(request)

    return render(request, 'core/index.html', {  'ljForm': ljform,
                                            'tp_mvform': tp_mvform,
                                            'gp_form': gp_form,
                                            'sbgp_form': sbgp_form,
                                            'tipo_movimento': tp_mv,
                                            'result_lojas': lojas,
                                            'result_grupos': grupos,
                                            'result_subGrupos': subgrupos,
                                            'result_produtos': listProdutos,
                                        })

@login_required
def filtroConsulta(request):

    lojas = adminORnormal(request)

    return render(request, 'core/filtro.html', {'lojas': lojas, "tipoMovimento":tp_mv, "usuario": user, "status": status })


@login_required
def filtroMovimento(request):

    print('Testando o Ajax')

    if request.is_ajax() and request.method == "POST":

        prod = request.POST.get('produto')
        cdsbgp = request.POST.get('subgrupo')
        cdgp = request.POST.get('grupo')
        idMov = request.POST.get('idMov')
        tpMovimento = request.POST.get('movimento')

        conversao = list(Tipomovimento.objects.filter(nmtipomovimento=tpMovimento).values('conversao'))[0]['conversao']
        
        if conversao == 'A':
            if prod != '':
                produtos = Produto.objects.filter(cdproduto=prod, ativo='A').values('cdproduto','nmproduto', 'cdunidade__nmUnidade', 'percPerda')
            elif  cdsbgp != '':
                produtos = Produto.objects.filter(cdsubgrupo=cdsbgp, ativo='A').values('cdproduto','nmproduto', 'cdunidade__nmUnidade', 'percPerda')
            else:
                produtos = Produto.objects.filter(cdsubgrupo__cdGrupo=cdgp, ativo='A').values('cdproduto','nmproduto', 'cdunidade__nmUnidade', 'percPerda')
        else:
            if prod != '':
                produtos = Produto.objects.filter(cdproduto=prod, ativo='A').values('cdproduto','nmproduto', 'cdunipadrao__nmUnidade', 'percPerda')
            elif  cdsbgp != '':
                produtos = Produto.objects.filter(cdsubgrupo=cdsbgp, ativo='A').values('cdproduto','nmproduto', 'cdunipadrao__nmUnidade', 'percPerda')
            else:
                produtos = Produto.objects.filter(cdsubgrupo__cdGrupo=cdgp, ativo='A').values('cdproduto','nmproduto', 'cdunipadrao__nmUnidade', 'percPerda')
            

            
        if idMov != 0:
            lista = []
            for i in produtos:


                print(i)
                valores = Itemmovimentado.objects.filter(cdmovimentacao=idMov, cdproduto=i['cdproduto']).values('valor', 'valorLiquido')

                valor = valores[0]['valor'] if valores else None
                valorLiquido = valores[0]['valorLiquido'] if valores else None

                print(valores, '-', valor, '-', valorLiquido)
                uni = i['cdunidade__nmUnidade'] if conversao == 'A' else i['cdunipadrao__nmUnidade']
                dados = {
                    "cdProduto" : i['cdproduto'],
                    "nmProduto" : i['nmproduto'],
                    "unidade"   : uni ,
                    "percPerda" : i['percPerda'],
                    "valor" : valor,
                    "valorLiquido" : valorLiquido 
                }
                lista.append(dados)
            dados = JsonResponse(lista, safe=False)
        else:
            dados = JsonResponse(list(produtos), safe=False)
        
        return HttpResponse(dados)

    else:
        raise Http404

    pass


@login_required
def movimento(request):

    if request.is_ajax() and request.method == "POST":

        print('cheguei aqui')
        cab = json.loads(request.POST.get('cab'))
        prod = request.POST.getlist('prod[]')
        flag = int(request.POST.getlist('flag')[0])

        mov = None
        idMov = None
        date = cab['data'] +' '+ str(dt.today().time())

        dtInicial = cab['data']
        dtFinal = cab['data']+' 23:59:59'

        idCadatro = None
        dados = 'Error'
        global flagCadastro
        flagCadastro = 0

        
        idCadastro = Movimentacao.objects.filter(
                                                cdtipomovimento_id = pkModels('tpMov', cab['movimento']),
                                                cdloja_id = pkModels('loja', cab['loja']),
                                                dtmovimentacao__gte=dtInicial,
                                                dtmovimentacao__lte=dtFinal,
                                                )

        print("IDCadastro - "+ str(idCadastro.values()))

        if flag == 0:
            if not idCadatro:
                mov = Movimentacao.objects.create(
                            cdtipomovimento_id = pkModels('tpMov', cab['movimento']),
                            user_id = User.objects.filter(username=request.user).values('id'),
                            cdloja_id = pkModels('loja', cab['loja']),
                            dtmovimentacao = date,
                            status_id = 2).pk

                idMov = mov
                print(f"Inserindo codigo da movimentacao - {idMov}")
            else:
                 flagCadastro = 1

        else:
            idMov = flag

        conversao = list(Tipomovimento.objects.filter(nmtipomovimento=cab['movimento']).values('conversao'))[0]['conversao']


        # print(prod)
        if flagCadastro == 0:
            for i in prod:
                d = json.loads(i)
                try:
                    if d['valor'] and ['valor'] != '0':
                        pesq = Itemmovimentado.objects.filter(cdproduto_id= d['cdProduto'], cdmovimentacao_id=idMov)
                        produto = list(Produto.objects.filter(cdproduto=d['cdProduto']).values('cdunidade', 'cduniconv','cdunipadrao', 'vlconv', 'percPerda' ))

                        unidade = produto[0]['cdunidade']
                        unidadeConv = produto[0]['cduniconv']
                        unidadePadrao = produto[0]['cdunipadrao']
                        valorConv = float(d['valor']) * produto[0]['vlconv']

                        valorLiq = None

                        
                        if produto[0]['percPerda'] != 0 and produto[0]['percPerda'] != None and d['valorLiquido'] != 0 and d['valorLiquido'] != None:

                            vlAtual = Itemmovimentado.objects.filter(cdproduto_id= d['cdProduto'], cdmovimentacao_id=idMov).values('valorLiquido')
                            # print(vlAtual)
                            if vlAtual:
                                if vlAtual[0]['valorLiquido'] != float(d['valorLiquido']):
                                    valorLiq = float(d['valorLiquido']) #* float( 1 - (produto[0]['percPerda'] / 100))
                                else:
                                    valorLiq = vlAtual[0]['valorLiquido'] 
                            else:
                                if d['valorLiquido']:
                                    valorLiq = float(d['valorLiquido']) #* float( 1 - (produto[0]['percPerda'] / 100)) 
                                else:
                                    valorLiq = 0                                     
            

                        # Verifica se o produto já foi inserido e atualiza os valores
                        if pesq:
                            # Verifica se a conversão está inativa ou não
                            if conversao == 'I':
                                Itemmovimentado.objects.filter(cdproduto_id= d['cdProduto'], cdmovimentacao_id=idMov).update(valor=d['valor'], cdunidade_id=unidadePadrao , valorLiquido=valorLiq)
                            else:
                                Itemmovimentado.objects.filter(cdproduto_id= d['cdProduto'], cdmovimentacao_id=idMov).update(valor=valorConv, cdunidade_id=unidadeConv, valorLiquido=valorLiq)

                        #  Insere o produto na movimentação 
                        else:
                            # Verifica se a conversão está inativa ou não 
                            if conversao == 'I':
                                Itemmovimentado.objects.update_or_create(
                                    cdmovimentacao_id=idMov,
                                    cdproduto_id=d['cdProduto'],
                                    valor=d['valor'],
                                    valorLiquido=valorLiq,
                                    cdunidade_id=unidadePadrao
                                )
                            else:
                                Itemmovimentado.objects.update_or_create(
                                    cdmovimentacao_id=idMov,
                                    cdproduto_id=d['cdProduto'],
                                    valor=valorConv,
                                    valorLiquido=valorLiq,
                                    cdunidade_id=unidadeConv
                                )
                except ValueError as e:
                    print(e)

            print(idMov)
            dados = Itemmovimentado.objects.filter(cdmovimentacao_id=idMov).values('cdmovimentacao_id','cditemmovimentado', 'cdproduto__nmproduto','cdunidade__nmUnidade', 'valor', 'valorLiquido').order_by('cditemmovimentado')
            dados = json.dumps(list(dados))
        
            
            

        return HttpResponse(dados)

    else:
        raise Http404




@login_required
def finalizarMov(request):

    if request.is_ajax() and request.method == "POST":

        flag = int(request.POST.getlist('flag')[0])
        cab = json.loads(request.POST.getlist('cab')[0])
        
        date = cab['data'] +' '+ str(dt.today().time())

        print(date)

        dataAtual = list(Movimentacao.objects.filter(cdmovimentacao=flag).values('dtmovimentacao'))
        dataAtual = dataAtual[0]['dtmovimentacao'].date().strftime('%Y-%m-%d')

        if cab['data'] != dataAtual:
             Movimentacao.objects.filter(cdmovimentacao=flag).update(status_id=3, dtmovimentacao=date )
        else:
            Movimentacao.objects.filter(cdmovimentacao=flag).update(status_id=3 )



        return HttpResponse("OK")

    else:
        raise Http404



@login_required
def acompanhamentoMov(request):

    if request.is_ajax() and request.method == "POST":

        dados = json.loads(request.body)['data']

        dtInicial = dados['dataInicial']
        dtFinal = dados['dataFinal']+' 23:59:59'
        loja = pkModels('loja', dados['loja'])
        tipoMov = pkModels('tpMov', dados['tipoMov'])
        status = pkModels('status', dados['status'])

        userLogin = User.objects.filter(username=request.user).values()
        for i in userLogin:
            id = i['id']
            superUser = i['is_superuser']

        if loja == None:
            lojasID = adminORnormal_ID(request)
        else:
            lojasID = [loja]

        usuario = None
        if dados['usuario']:
            usuario = pkModels('user', dados['usuario'])


        # Apenas Um Filtro
        if loja != None and usuario == None and tipoMov ==None and status == None:
            print('1 - Filtro')
            x = Movimentacao.objects.filter(dtmovimentacao__gte=dtInicial,dtmovimentacao__lte=dtFinal, cdloja_id__in=lojasID ).order_by('dtmovimentacao')
        elif loja == None and usuario != None and tipoMov ==None and status == None:
            print('2 - Filtro')
            x = Movimentacao.objects.filter(dtmovimentacao__gte=dtInicial,dtmovimentacao__lte=dtFinal, user_id= usuario, cdloja_id__in=lojasID  ).order_by('dtmovimentacao')
        elif loja == None and usuario == None and tipoMov !=None and status == None:
            print('3 - Filtro')
            x = Movimentacao.objects.filter(dtmovimentacao__gte=dtInicial,dtmovimentacao__lte=dtFinal, cdtipomovimento_id=tipoMov, cdloja_id__in=lojasID  ).order_by('dtmovimentacao')
        elif loja == None and usuario == None and tipoMov ==None and status != None:
            print('4 - Filtro')
            x = Movimentacao.objects.filter(dtmovimentacao__gte=dtInicial,dtmovimentacao__lte=dtFinal, status_id=status, cdloja_id__in=lojasID  ).order_by('dtmovimentacao')

        # Dois Filtros
        #  Loja
        elif loja != None and usuario != None and tipoMov ==None and status == None:
            print('5 - Filtro - ID Usuário = ', usuario, f"ID Loja = {loja} ")
            x = Movimentacao.objects.filter(dtmovimentacao__gte=dtInicial,dtmovimentacao__lte=dtFinal, cdloja_id__in=lojasID, user_id= usuario ).order_by('dtmovimentacao')
        elif loja != None and usuario == None and tipoMov !=None and status == None:
            print('6 - Filtro')
            x = Movimentacao.objects.filter(dtmovimentacao__gte=dtInicial,dtmovimentacao__lte=dtFinal, cdloja_id__in=lojasID, cdtipomovimento_id=tipoMov ).order_by('dtmovimentacao')
        elif loja != None and usuario == None and tipoMov ==None and status != None:
            print('7 - Filtro')
            x = Movimentacao.objects.filter(dtmovimentacao__gte=dtInicial,dtmovimentacao__lte=dtFinal, cdloja_id__in=lojasID, status_id=status ).order_by('dtmovimentacao')
        elif loja == None and usuario != None and tipoMov != None and status == None:
            print('8 - Filtro')
            x = Movimentacao.objects.filter(dtmovimentacao__gte=dtInicial, dtmovimentacao__lte=dtFinal, user_id= usuario, cdtipomovimento_id=tipoMov, cdloja_id__in=lojasID ).order_by('dtmovimentacao')
        elif loja == None and usuario != None and tipoMov == None and status != None:
            print('9 - Filtro')
            x = Movimentacao.objects.filter(dtmovimentacao__gte=dtInicial, dtmovimentacao__lte=dtFinal, user_id= usuario, status_id=status, cdloja_id__in=lojasID ).order_by('dtmovimentacao')
        elif loja == None and usuario == None and tipoMov != None and status != None:
            print('10 - Filtro')
            x = Movimentacao.objects.filter(dtmovimentacao__gte=dtInicial, dtmovimentacao__lte=dtFinal, cdtipomovimento_id=tipoMov, status_id=status, cdloja_id__in=lojasID ).order_by('dtmovimentacao')

        # Tres FIltros
        elif loja != None and usuario != None and tipoMov != None and status == None:
            print('11 - Filtro')
            x = Movimentacao.objects.filter(dtmovimentacao__gte=dtInicial, dtmovimentacao__lte=dtFinal, cdloja_id__in=lojasID, user_id= usuario, cdtipomovimento_id=tipoMov).order_by('dtmovimentacao')
        elif loja != None and usuario != None and tipoMov == None and status != None:
            print('12 - Filtro')
            x = Movimentacao.objects.filter(dtmovimentacao__gte=dtInicial, dtmovimentacao__lte=dtFinal, cdloja_id__in=lojasID, user_id= usuario, status_id=status).order_by('dtmovimentacao')
        elif loja == None and usuario != None and tipoMov != None and status != None:
            print('13 - Filtro')
            x = Movimentacao.objects.filter(dtmovimentacao__gte=dtInicial, dtmovimentacao__lte=dtFinal, user_id= usuario, cdtipomovimento_id=tipoMov,  status_id=status, cdloja_id__in=lojasID ).order_by('dtmovimentacao')
        elif loja != None and usuario == None and tipoMov != None and status != None:
            print('14 - Filtro')
            x = Movimentacao.objects.filter(dtmovimentacao__gte=dtInicial, dtmovimentacao__lte=dtFinal, cdtipomovimento_id=tipoMov, status_id=status, cdloja_id__in=lojasID  ).order_by('dtmovimentacao')

        # Quatro Filtros
        elif loja != None and usuario != None and tipoMov != None and status != None:
            print('15 - Filtro')
            x = Movimentacao.objects.filter(dtmovimentacao__gte=dtInicial, dtmovimentacao_lte=dtFinal,cdloja_id=lojasID, user_id= usuario, cdtipomovimento_id=tipoMov, status_id=status ).order_by('dtmovimentacao')

        # Somente com o filtro de data
        else:
            print('16 - Filtro')
            x = Movimentacao.objects.filter(dtmovimentacao__gte=dtInicial, dtmovimentacao__lte=dtFinal, cdloja_id__in=lojasID ).order_by('dtmovimentacao')


        lista = []
        for i in x:

            dados = {
                "codigo" : i.cdmovimentacao,
                "loja" : str(i.cdloja.nmloja).upper(),
                "usuario": str(i.user.username).upper(),
                "tipo" : str(i.cdtipomovimento.nmtipomovimento).upper(),
                "status" : str(i.status.nmStatus).upper(),
                "data" : i.dtmovimentacao.date().strftime('%d/%m/%Y')
            }
            lista.append(dados)

        # print(json.dumps(lista))
        return HttpResponse(json.dumps(lista))

    else:
        raise Http404



def pkModels(tipo, valor):

    id = None

    if(tipo == 'tpMov'):
        mov = Tipomovimento.objects.filter(nmtipomovimento=valor).values()
        for i in mov:
            id = i['cdtipomovimento']


    if (tipo == 'loja'):
        mov = Loja.objects.filter(nmloja=valor).values()
        for i in mov:
            id = i['cdloja']


    if (tipo == 'status'):
        mov = Status.objects.filter(nmStatus=valor).values()
        for i in mov:
            id = i['cdStatus']


    if (tipo == 'user'):
        mov = User.objects.filter(username=valor).values('id')
        for i in mov:
            id = i['id']

    if (tipo == 'data'):
        print(valor)
        for i in valor:
            id = i['id']


    return id



def adminORnormal(request):

    x = User.objects.filter(username=request.user).values_list('is_superuser', flat=True)

    if x[0] == False:
        i = Acesso.objects.filter(user_id=request.user).values_list('cdloja_id', flat=True)
        lojas = Loja.objects.filter(cdloja__in=i)
    else:
        lojas = Loja.objects.all()
    return lojas


def adminORnormal_ID(request):

    x = User.objects.filter(username=request.user).values_list('is_superuser', flat=True)

    if x[0] == False:
        lojas = Acesso.objects.filter(user_id=request.user).values_list('cdloja_id', flat=True)
    else:
        lojas = Loja.objects.all().values_list('cdloja', flat=True)
    return lojas


@login_required
def filtroSubgrupo(request):
    if request.is_ajax() and request.method == "POST":
        paramGrupo = request.POST.get('grupo')

        print(paramGrupo)

        if paramGrupo != '':
            print('estou aqui!!!')
            x = list(Subgrupo.objects.filter(cdGrupo__nmgrupo=paramGrupo).values('cdsubgrupo','nmsubgrupo'))
            print(x)

        return HttpResponse(json.dumps(x))
    else:
        raise Http404

@login_required
def getAll(request):

    if request.is_ajax() and request.method == "POST":

        dados = request.POST.get('data')

        print( 'teste visualizar', dados)

        lista = getItens(dados)

        return HttpResponse(json.dumps(lista))
    else:
        raise Http404


def getItens(cd):

    x = Itemmovimentado.objects.filter(cdmovimentacao=cd).order_by('cditemmovimentado')
        
    lista = []
    for i in x:

        dados = {
            "cdItem"    : i.cditemmovimentado,
            "cdProduto" : i.cdproduto.cdproduto,
            "nmProduto" : i.cdproduto.nmproduto,
            "unidade"   : i.cdunidade.nmUnidade,
            "valor" : i.valor,
            "valorLiquido": i.valorLiquido
        }
        lista.append(dados)

    return lista


@login_required
def getEditar(request):

    if request.is_ajax() and request.method == "POST":


        idMov = request.POST.get('dados')
        print("id da movimentação: ", idMov)
        dados = Itemmovimentado.objects.filter(cdmovimentacao=idMov).values('cdmovimentacao',
                                                                            'cdmovimentacao__cdloja__nmloja', 
                                                                            'cdmovimentacao__dtmovimentacao', 
                                                                            'cdmovimentacao__cdtipomovimento__nmtipomovimento', 
                                                                            'cdmovimentacao__cdtipomovimento__conversao', 
                                                                            'cdproduto', 
                                                                            'cdproduto__nmproduto', 
                                                                            'valor', 
                                                                            'valorLiquido',
                                                                            'cdunidade__nmUnidade',
                                                                            'cditemmovimentado' ).order_by('cditemmovimentado')

        
        lista = []
        
        for i in dados:
            # print("teste:" , i['cdmovimentacao'])
            dados = {
                "cditemmovimentado" : i["cditemmovimentado"],
                "cdmovimentacao" : i['cdmovimentacao'],
                "cdmovimentacao__cdloja__nmloja" : i['cdmovimentacao__cdloja__nmloja'],
                'cdmovimentacao__dtmovimentacao' : i['cdmovimentacao__dtmovimentacao'].date().strftime('%Y-%m-%d'), 
                'cdmovimentacao__cdtipomovimento__nmtipomovimento' :i['cdmovimentacao__cdtipomovimento__nmtipomovimento'], 
                'cdmovimentacao__cdtipomovimento__conversao' : i['cdmovimentacao__cdtipomovimento__conversao'], 
                "cdProduto" : i['cdproduto'],
                "cdproduto__nmproduto" : i['cdproduto__nmproduto'],
                "cdunidade__nmUnidade"  : i['cdunidade__nmUnidade'],
                "valor" : i['valor'],
                "valorLiquido" : i["valorLiquido"]
            }
            lista.append(dados)
        # print(lista)
        return HttpResponse(json.dumps(lista))

    else:
        raise Http404

 

@login_required
def excluirMovi(request):

    if request.is_ajax() and request.method == "POST":

        try:
            idMov = request.POST.get('data')

            # print(idMov)

            Itemmovimentado.objects.filter(cdmovimentacao=idMov).delete()
            Movimentacao.objects.filter(cdmovimentacao=idMov).delete()

            return HttpResponse("Registro excluido com sucesso!!!")
        except ValueError as e:
            print(e)
            return HttpResponse("Erro ao exculir registro.")


    else:
        raise Http404




@login_required
def excluirItem(request):
        
    if request.is_ajax() and request.method == "POST":
        try:
            idMov = request.POST.get('idMov')
            idItem = request.POST.get('idItem')
            Itemmovimentado.objects.filter(cditemmovimentado=idItem).delete()
            lista = getItens(idMov)
            return HttpResponse(json.dumps(lista))
        except ValueError as e:
            print(e)
            return HttpResponse("Erro ao exculir registro.")


    else:
        raise Http404

def importaVenda(request):
    dataset = Dataset()
    new_mov = request.FILES['myfile']
    #verifica se o arquivo é xlsx
    if not new_mov.name.endswith('xlsx'):
        messages.error(request, 'Erro ao importar - Verifique o tipo do arquivo.  ')
        return redirect('/importData')

    imported_data = dataset.load(new_mov.read())
    data_importa = request.POST.get('data_importacao')
    lista_pd_nao_correspondentes = []
    nome_loja = request.POST.get('loja')
    qr_loja = Loja.objects.filter(nmloja=f'{nome_loja}').values('cdloja')
    cd_loja = qr_loja[0].get('cdloja')
        
    for i in imported_data:
        #verificar se tem no de para
        produto = i[0]
        de_para = importa_de_para.objects.filter(nmprodutocliente=f"{produto}")
        if de_para:
            print(f"tem - {produto}")
        else:
            print(f"Não tem - {produto}")
            lista_pd_nao_correspondentes.append(produto)

    if len(lista_pd_nao_correspondentes):
        messages.error(request, "AVISO IMPORTANTE! - IMPORTAÇÃO NÃO REALIZADA")
        messages.warning(request, "LISTA DE PRODUTOS NÃO ENCONTRADOS NO DE PARA.")
        for i in lista_pd_nao_correspondentes:
            messages.info(request, f"{i}")
        messages.warning(request, f"Total: {len(lista_pd_nao_correspondentes)}")
        return render(request, 'core/importaDados.html')
    
    else:
        print("Tudo certo para importar")
        
        data_atual = datetime.datetime.strptime(f"{data_importa} 00:00:00", '%Y-%m-%d %H:%M:%S')
        print(data_atual)
        usuario_logado = User.objects.filter(username=request.user).values('id')
        id_mov = 0
        for i in imported_data:
            produto = i[0]
            valor = i[1]
            quantidade = i[2]
            cd_produto = importa_de_para.objects.filter(nmprodutocliente=f"{produto}").values('cdproduto').get()
            cd = cd_produto["cdproduto"]
            cdunidade_produto = Produto.objects.filter(cdproduto=cd).values("cdunidade_id").get()
            cd_uni = cdunidade_produto["cdunidade_id"]
            
            if id_mov == 0:
                id_mov = Movimentacao.objects.create(cdtipomovimento_id=5,
                                                        user_id = usuario_logado,
                                                        cdloja_id=cd_loja,
                                                        dtmovimentacao=data_atual,
                                                        status_id=4,
                                                        obs='Importacao').pk

            base_item = Itemmovimentado(
                cdmovimentacao_id=id_mov,
                cdproduto_id=cd,
                valor=quantidade,
                valorLiquido=valor,
                cdunidade_id=cd_uni,
            )
            base_item.save()
        messages.success(request, "Importação de vendas realizada com sucesso.") 


def importaPedido(request):
    
    print("Entrou no pedido...")
    dataset = Dataset()
    new_mov = request.FILES['myfile']
    #verifica se o arquivo é xlsx
    if not new_mov.name.endswith('xlsx'):
        messages.error(request, 'Erro ao importar - Verifique o tipo do arquivo.  ')
        return redirect('/importData')

    imported_data = dataset.load(new_mov.read())
        

    listDate = []
    cliente = None
    listProdutos = []
    listProdutoErro = []
    listProdutoErroUnicos = []
    
    for i in imported_data:
            # Agrupamento das datas
            if not i[4] in listDate:
                listDate.append(i[4])

            # Agrupamento dos produtos
            if not i[2] in listProdutos:
                print(i[2])
                listProdutos.append(i[2])

            # Codigo da empresa
            if cliente == None:
                cliente = Loja.objects.filter(nmloja=i[3]).values("cdloja")
                if cliente:
                    cliente = cliente[0]['cdloja']
                else:
                    listProdutoErro.append(i[3])
                

            # Verifica se o produto existe no cadastro
            listAllProduct = []
            for v in listProdutos:
                # print(v)
                idProduto = list(Produto.objects.filter(nmproduto=v).values("cdproduto", "nmproduto"))
                listAllProduct.append(idProduto)

                # print(idProduto)
                if not idProduto:
                    listProdutoErro.append(v)

            for r in listProdutoErro:
                if not r in listProdutoErroUnicos:
                    listProdutoErroUnicos.append(r)

            
    # print(listProdutoErro   )  
    if not listProdutoErro and cliente != None:

        for x in listDate:
            # print('inserindo cabeçalho')
            # Preenchimento do cabeçalho da movimentação
            data = dt.strptime(x, "%d/%m/%Y")
            idMovimentacao = Movimentacao.objects.create(cdtipomovimento_id = 3,
                                                        user_id = User.objects.filter(username=request.user).values('id'),
                                                        cdloja_id = cliente,
                                                        dtmovimentacao = data,
                                                        status_id = 4).pk
            for j in imported_data:
                if j[4] == x:
                    # print(j)
                    idProduto = list(Produto.objects.filter(nmproduto=j[2]).values("cdproduto", "cduniconv"))
                    # print("teste - ", idProduto)
                    Itemmovimentado.objects.update_or_create(
                                cdmovimentacao_id=idMovimentacao,
                                cdproduto_id= idProduto[0]['cdproduto'],
                                valor=j[6],
                                valorLiquido=0,
                                cdunidade_id=idProduto[0]['cduniconv']
                            )

        messages.info(request, 'Importação realizada com sucesso!!!')
        return redirect('/importData')
    else:
        messages.error(request, "AVISO IMPORTANTE! - IMPORTAÇÃO NÃO REALIZADA")
        messages.warning(request, "LISTA DE PRODUTOS NÃO ENCONTRADOS.")
        for i in listProdutoErroUnicos:
            messages.info(request, f"{i}")
        messages.warning(request, f"Total: {len(listProdutoErroUnicos)}")
        return redirect('/importData')
        # return HttpResponse(json.dumps(listProdutoErro))

    # return render(request, 'core/importaDados.html')
    #return render(request, 'core/importaDados.html') 
def desfazerImportacao(request):   
    if request.method == "POST":
        opcao = request.POST.get('opcao')
        loja = request.POST.get('loja')
        data_importacao = request.POST.get('data_importacao')
        qr_loja = Loja.objects.filter(nmloja=f'{loja}').values('cdloja')
        cd_loja = qr_loja[0].get('cdloja')
        date_temp = datetime.datetime.strptime(f"{data_importacao} 00:00:00", "%Y-%m-%d %H:%M:%S")
        new_date = date_temp + datetime.timedelta(days=1)
        
        print(date_temp, new_date)
        if opcao == "depara":
            print(data_importacao, cd_loja,)
            base = importa_de_para.objects.filter(
                # dtimportacao=data_importacao,
                cdloja=cd_loja
            )
            if len(base) > 0:
                base.delete()
                messages.success(request, "Importação desfeita com sucesso.")
            else:
                messages.warning(request, "Não foi encontrado nenhuma informação referente.")

        elif opcao == "vendas":
                base = Movimentacao.objects.filter(
                    dtmovimentacao__gte=f"{data_importacao} 00:00:00",
                    dtmovimentacao__lt=new_date,
                    cdloja=cd_loja,
                    cdtipomovimento_id=5,
                    status_id = 4).values('cdmovimentacao')
                
                if base:
                    Itemmovimentado.objects.filter(cdmovimentacao__in=base).delete()
                    Movimentacao.objects.filter(cdmovimentacao__in=base).delete()
                    messages.success(request, "Importação desfeita com sucesso.")
                else:
                    messages.warning(request, "Não foi encontrado nenhuma informação referente.")
            
def importaDePara(request):
    dataset = Dataset()
    new_mov = request.FILES['myfile']
    
    #verifica se o arquivo é xlsx
    if not new_mov.name.endswith('xlsx'):
        messages.error(request, 'Erro ao importar - Verifique o tipo do arquivo.  ')
        return redirect('/importData')
    
    imported_data = dataset.load(new_mov.read())
    data_importa = request.POST.get('data_importacao')
    nome_loja = request.POST.get('loja')
    qr_loja = Loja.objects.filter(nmloja=f'{nome_loja}').values('cdloja')
    cd_loja = qr_loja[0].get('cdloja')
    verificar_importacao = importa_de_para.objects.filter(cdloja=cd_loja)

    divergentes = []
    lista_cdprodutos_nao_encontrados = []
    dados_importados = []
    
    if verificar_importacao:
        ultima_data = importa_de_para.objects.filter(cdloja=cd_loja).latest('dtimportacao')
        messages.warning(request, f"Essa loja já foi importada no dia: {ultima_data.dtimportacao}")
        return

    for i in imported_data:
        #cd_produto = qr_produto[0].get('cdproduto')
        if i[0] == None or i[1] == None:
            print(i[0], i[1], "contem valor vazio.")
            divergentes.append(i[0])
        else:

            qr_produto = Produto.objects.filter(nmproduto=f'{i[1]}').values('cdproduto')
            if len(qr_produto) == 0:
                print(i[1], "Não encontrado o cdproduto")
                lista_cdprodutos_nao_encontrados.append(i[1])
            else:
                cd_produto = qr_produto[0].get('cdproduto')
                data_importa
                des_loja = i[0]
                des_bi = i[1]
                cd_loja
                dados_importados.append(i[1])
                
                p = importa_de_para.objects.create(dtimportacao=data_importa,
                    cdloja=cd_loja,
                    nmprodutocliente=des_loja, 
                    cdproduto=cd_produto,
                    )
                print(data_importa,cd_loja, des_loja, des_bi, cd_produto)
                
    qnt_div = len(divergentes)
    qnt_cdpd_ne = len(lista_cdprodutos_nao_encontrados)
    qnt_importados = len(dados_importados)
    total = qnt_div + qnt_cdpd_ne + qnt_importados
    messages.success(request, f'Dados Importados: {qnt_importados}')
    messages.warning(request, f'Dados divergentes: {qnt_div}')
    messages.error(request, f'Codigos não encontrados: {qnt_cdpd_ne}')
    messages.info(request, f'Total: {total}')
            
@login_required
def filtroVenda(request):
    cd_loja = importa_de_para.objects.all().values("cdloja").distinct()
    lojas = list(Loja.objects.filter(cdloja__in=cd_loja).values("nmloja"))
    print(lojas)
    lj = json.dumps(lojas)
    return HttpResponse(lj)
    
@login_required
def filtroDePara(request):
    lojas = list(Loja.objects.all().values("nmloja"))
    lj = json.dumps(lojas)
    return HttpResponse(lj)
        
@login_required
def importData(request):
    lojas = adminORnormal(request)

    if request.method == 'POST':   
        opcao = request.POST.get('opcao')
        loja = request.POST.get('loja')
        data_importacao = request.POST.get('data_importacao')
        desfazer_importacao = request.POST.get('btn-desfazer', False)
        btn_importar = request.POST.get('btn-importar', False)
        #print(tipo_arq, loja, data_importacao)
        print(desfazer_importacao)
        print(btn_importar)
        print(opcao)
        
        if btn_importar == "importar" and opcao == "depara":
            try:
                importaDePara(request)
            except datastructures.MultiValueDictKeyError as e:
                messages.error(request, f"Ocorreu um erro em - {e}")
        elif btn_importar == "importar" and opcao == "vendas":
            try:
                importaVenda(request)
            except datastructures.MultiValueDictKeyError as e:
                messages.error(request, f"Ocorreu um erro em - {e}")
        elif btn_importar == "importar" and opcao == "pedido":
            try:
                importaPedido(request)
            except datastructures.MultiValueDictKeyError as e:
                messages.error(request, f"Ocorreu um erro em {e}")
        
        if (desfazer_importacao == "desfazer"):
            desfazerImportacao(request)
        
    return render(request, 'core/importaDados.html', {'result_lojas':lojas})
