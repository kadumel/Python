from django.shortcuts import render, get_object_or_404
from .models import Acesso, Tipomovimento, Grupo, Subgrupo, Loja, Produto, Movimentacao, Itemmovimentado, Status
from .forms import LojaForm, TipoMovientoForm, GrupoForm, SubGrupoForm, ProdutoForm
from django.http import HttpResponse, Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import json
from datetime import datetime as dt
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

        print('Conteudo da request: ', request.POST.get('loja'))
        print('Fim Ajax')

        prod = request.POST.get('produto')
        cdsbgp = request.POST.get('subgrupo')
        cdgp = request.POST.get('grupo')

        

        if prod != '':
            produtos = Produto.objects.filter(nmproduto=prod, ativo='A').values('cdproduto','nmproduto', 'cdunidade__nmUnidade')
            dados = JsonResponse(list(produtos), safe=False)
        elif  cdsbgp != '':
            produtos = Produto.objects.filter(cdsubgrupo__nmsubgrupo=cdsbgp, ativo='A').values('cdproduto','nmproduto', 'cdunidade__nmUnidade')
            dados = JsonResponse(list(produtos), safe=False)
        else:
            print(cdgp)
            produtos = Produto.objects.filter(cdsubgrupo__cdGrupo__nmgrupo=cdgp, ativo='A').values('cdproduto','nmproduto', 'cdunidade__nmUnidade')
            dados = JsonResponse(list(produtos), safe=False)
        
        return HttpResponse(dados)

    else:
        raise Http404

    pass


@login_required
def movimento(request):

    if request.is_ajax() and request.method == "POST":

        cab = json.loads(request.POST.get('cab'))
        prod = request.POST.getlist('prod[]')
        flag = int(request.POST.getlist('flag')[0])

        mov = None
        idMov = None

        # date = dt.strptime(cab['data'], '%d/%m/%Y').date()
        # print(date)

        if flag == 0:

            
            mov = Movimentacao.objects.create(
                        cdtipomovimento_id = pkModels('tpMov', cab['movimento']),
                        user_id = User.objects.filter(username=request.user).values('id'),
                        cdloja_id = pkModels('loja', cab['loja']),
                        # dtmovimentacao = date,
                        status_id = 2).pk

            idMov = mov
        else:
            idMov = flag

        conversao = list(Tipomovimento.objects.filter(nmtipomovimento=cab['movimento']).values('conversao'))[0]['conversao']
        print(conversao)
        for i in prod:
            d = json.loads(i)

            try:
                if d['valor']:
                    print('1', d['valor'])
                    pesq = Itemmovimentado.objects.filter(cdproduto_id= d['cdProduto'], cdmovimentacao_id=idMov)

                    produto = list(Produto.objects.filter(cdproduto=d['cdProduto']).values('cdunidade', 'cduniconv', 'vlconv' ))

                    print(produto[0]['cdunidade'])

                    unidade = produto[0]['cdunidade']
                    unidadeConv = produto[0]['cduniconv']
                    valorConv = float(d['valor']) * produto[0]['vlconv']

                    print('2', pesq)
                    if pesq:
                        
                        if conversao == 'I':
                            print('3', d, idMov)
                            Itemmovimentado.objects.filter(cdproduto_id= d['cdProduto'], cdmovimentacao_id=idMov).update(valor=d['valor'])
                            print('3 Finalizado')
                        else:
                            
                            Itemmovimentado.objects.filter(cdproduto_id= d['cdProduto'], cdmovimentacao_id=idMov).update(valor=valorConv)

                    else:
                        print('4', d, idMov)
                        if conversao == 'I':
                            Itemmovimentado.objects.update_or_create(
                                cdmovimentacao_id=idMov,
                                cdproduto_id=d['cdProduto'],
                                valor=d['valor'],
                                cdunidade_id=unidade
                            )
                        else:
                            Itemmovimentado.objects.update_or_create(
                                cdmovimentacao_id=idMov,
                                cdproduto_id=d['cdProduto'],
                                valor=valorConv,
                                cdunidade_id=unidadeConv
                            )
                        print('4 - FIM')
                    print('fim do IF d[valor]')
            except KeyError:
                pass

        print('5', idMov)
        dados = Itemmovimentado.objects.filter(cdmovimentacao_id=idMov).values('cdmovimentacao_id','cdproduto__nmproduto','cdunidade__nmUnidade', 'valor').order_by('cdproduto__nmproduto')

        dados = json.dumps(list(dados))
        print(dados)



        return HttpResponse(dados)

    else:
        raise Http404

    pass



@login_required
def finalizarMov(request):

    if request.is_ajax() and request.method == "POST":

        flag = int(request.POST.getlist('flag')[0])

        Movimentacao.objects.filter(cdmovimentacao=flag).update(status_id=3)

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


        print('tipo de dadps -', id, superUser)
        if superUser  == True:
            usuario = pkModels('user', dados['usuario'])
        else:
            usuario = id


        # Apenas Um Filtro
        if loja != None and usuario == None and tipoMov ==None and status == None:
            x = Movimentacao.objects.filter(dtmovimentacao__gte=dtInicial,dtmovimentacao__lte=dtFinal, cdloja_id=loja ).order_by('dtmovimentacao')
        elif loja == None and usuario != None and tipoMov ==None and status == None:
            x = Movimentacao.objects.filter(dtmovimentacao__gte=dtInicial,dtmovimentacao__lte=dtFinal, user_id= usuario ).order_by('dtmovimentacao')
        elif loja == None and usuario == None and tipoMov !=None and status == None:
            x = Movimentacao.objects.filter(dtmovimentacao__gte=dtInicial,dtmovimentacao__lte=dtFinal, cdtipomovimento_id=tipoMov ).order_by('dtmovimentacao')
        elif loja == None and usuario == None and tipoMov ==None and status != None:
            x = Movimentacao.objects.filter(dtmovimentacao__gte=dtInicial,dtmovimentacao__lte=dtFinal, status_id=status ).order_by('dtmovimentacao')

        # Dois Filtros
        #  Loja
        elif loja != None and usuario != None and tipoMov ==None and status == None:
            x = Movimentacao.objects.filter(dtmovimentacao__gte=dtInicial,dtmovimentacao__lte=dtFinal, cdloja_id=loja, user_id= usuario ).order_by('dtmovimentacao')
        elif loja != None and usuario == None and tipoMov !=None and status == None:
            x = Movimentacao.objects.filter(dtmovimentacao__gte=dtInicial,dtmovimentacao__lte=dtFinal, cdloja_id=loja, cdtipomovimento_id=tipoMov ).order_by('dtmovimentacao')
        elif loja != None and usuario == None and tipoMov ==None and status != None:
            x = Movimentacao.objects.filter(dtmovimentacao__gte=dtInicial,dtmovimentacao__lte=dtFinal, cdloja_id=loja, status_id=status ).order_by('dtmovimentacao')
        elif loja == None and usuario != None and tipoMov != None and status == None:
            x = Movimentacao.objects.filter(dtmovimentacao__gte=dtInicial, dtmovimentacao__lte=dtFinal, user_id= usuario, cdtipomovimento_id=tipoMov).order_by('dtmovimentacao')
        elif loja == None and usuario != None and tipoMov == None and status != None:
            x = Movimentacao.objects.filter(dtmovimentacao__gte=dtInicial, dtmovimentacao__lte=dtFinal, user_id= usuario, status_id=status).order_by('dtmovimentacao')
        elif loja == None and usuario == None and tipoMov != None and status != None:
            x = Movimentacao.objects.filter(dtmovimentacao__gte=dtInicial, dtmovimentacao__lte=dtFinal, cdtipomovimento_id=tipoMov, status_id=status).order_by('dtmovimentacao')

        # Tres FIltros
        elif loja != None and usuario != None and tipoMov != None and status == None:
            x = Movimentacao.objects.filter(dtmovimentacao__gte=dtInicial, dtmovimentacao__lte=dtFinal, cdloja_id=loja, user_id= usuario, cdtipomovimento_id=tipoMov).order_by('dtmovimentacao')
        elif loja != None and usuario != None and tipoMov == None and status != None:
            x = Movimentacao.objects.filter(dtmovimentacao__gte=dtInicial, dtmovimentacao__lte=dtFinal, cdloja_id=loja, user_id= usuario, status_id=status).order_by('dtmovimentacao')
        elif loja == None and usuario != None and tipoMov != None and status != None:
            x = Movimentacao.objects.filter(dtmovimentacao__gte=dtInicial, dtmovimentacao__lte=dtFinal, user_id= usuario, cdtipomovimento_id=tipoMov,  status_id=status).order_by('dtmovimentacao')
        elif loja != None and usuario == None and tipoMov != None and status != None:
            x = Movimentacao.objects.filter(dtmovimentacao__gte=dtInicial, dtmovimentacao__lte=dtFinal, cdloja_id=loja, cdtipomovimento_id=tipoMov, status_id=status ).order_by('dtmovimentacao')

        # Quatro Filtros
        elif loja != None and usuario != None and tipoMov != None and status != None:
            x = Movimentacao.objects.filter(dtmovimentacao__gte=dtInicial, dtmovimentacao__lte=dtFinal,cdloja_id=loja, user_id= usuario, cdtipomovimento_id=tipoMov, status_id=status ).order_by('dtmovimentacao')

        # Somente com o filtro de data
        else:
            x = Movimentacao.objects.filter(dtmovimentacao__gte=dtInicial, dtmovimentacao__lte=dtFinal).order_by('dtmovimentacao')


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



@login_required
def filtroSubgrupo(request):
    if request.is_ajax() and request.method == "POST":
        paramGrupo = request.POST.get('grupo')

        print(paramGrupo)

        if paramGrupo != '':
            print('estou aqui!!!')
            x = list(Subgrupo.objects.filter(cdGrupo__nmgrupo=paramGrupo).values('nmsubgrupo'))
            print(x)

        return HttpResponse(json.dumps(x))
    else:
        raise Http404





@login_required
def getAll(request):

    if request.is_ajax() and request.method == "POST":

 
        dados = request.POST.get('data')

        print( 'teste visualizar', dados)

        x = Itemmovimentado.objects.filter(cdmovimentacao=dados).order_by('cdproduto__nmproduto')
        print(x)

        
        lista = []
        for i in x:

            dados = {
               
                "cdProduto" : i.cdproduto.cdproduto,
                "nmProduto" : i.cdproduto.nmproduto,
                "unidade"   : i.cdunidade.nmUnidade,
                "valor" : i.valor
            }
            lista.append(dados)
        
        print(lista)

        return HttpResponse(json.dumps(lista))
    else:
        raise Http404




@login_required
def getEditar(request):

    if request.is_ajax() and request.method == "POST":


        idMov = request.POST.get('dados')

        dados = Itemmovimentado.objects.filter(cdmovimentacao=idMov).values('cdmovimentacao','cdmovimentacao__cdloja__nmloja', 'cdmovimentacao__cdtipomovimento__nmtipomovimento', 'cdmovimentacao__cdtipomovimento__conversao', 'cdproduto', 'cdproduto__nmproduto', 'valor' )



        dados = json.dumps(list(dados))


        print(dados)

        return HttpResponse(dados)

    else:
        raise Http404



@login_required
def excluirMovi(request):

    if request.is_ajax() and request.method == "POST":

        try:
            idMov = request.POST.get('data')

            print(idMov)

            Itemmovimentado.objects.filter(cdmovimentacao=idMov).delete()
            Movimentacao.objects.filter(cdmovimentacao=idMov).delete()

            return HttpResponse("Registro excluido com sucesso!!!")
        except ValueError as e:
            print(e)
            return HttpResponse("Erro ao exculir registro.")


    else:
        raise Http404