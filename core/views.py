from django.shortcuts import render, get_object_or_404
from .models import Acesso, Tipomovimento, Grupo, Subgrupo, Loja, Produto, Movimentacao, Itemmovimentado, Status
from .forms import LojaForm, TipoMovientoForm, GrupoForm, SubGrupoForm, ProdutoForm, MovimentacaoForm
from . import connectionFactory as cf
from django.http import HttpResponse, Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import json, datetime
# Create your views here.


tp_mv = Tipomovimento.objects.all()
grupos = Grupo.objects.all()
subgrupos = Subgrupo.objects.all()
user = User.objects.all()
status = Status.objects.all()

@login_required
def index(request):

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

        cdgp = request.POST.get('grupo')
        cdsbgp = request.POST.get('subgrupo')

        if  cdsbgp != '':
            pd_form = ProdutoForm
            produtos = Produto.objects.filter(cdsubgrupo__nmsubgrupo=cdsbgp).values()
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

        global mov
        mov = None

        print(cab['movimento'])
        print(pkModels('tpMov', cab['movimento']))

        if flag == 0:
           print('teste CAB')
           mov = Movimentacao.objects.create(
                        cdtipomovimento_id = pkModels('tpMov', cab['movimento']),
                        user_id = User.objects.filter(username=request.user).values('id'),
                        cdloja_id = pkModels('loja', cab['loja']),
                        status_id = 2).pk
        if flag == 0:
            idMov = mov
        else:
            idMov = flag

        for i in prod:
            d = json.loads(i)
            if d['valor']:

                pesq = Itemmovimentado.objects.filter(cdproduto_id= d['cdProduto'], cdmovimentacao_id=idMov)

                if (pesq):
                    print(pesq)
                    Itemmovimentado.objects.filter(cdproduto_id= d['cdProduto'], cdmovimentacao_id=idMov).update(valor=d['valor'])
                else:
                    print('Inserir Dados')
                    insertProduto = Itemmovimentado.objects.update_or_create(
                        cdmovimentacao_id=idMov,
                        cdproduto_id=d['cdProduto'],
                        valor=d['valor']
                    )





        # if dados != '':
        #     pd_form = ProdutoForm
        #     produtos = Produto.objects.filter(cdsubgrupo__nmsubgrupo=cdsbgp).values()
        #     dados = JsonResponse(list(produtos), safe=False)
        return HttpResponse(mov)

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

    return id




def adminORnormal(request):

    x = User.objects.filter(username=request.user).values_list('is_superuser', flat=True)

    if x[0] == False:
        i = Acesso.objects.filter(user_id=request.user).values_list('cdloja_id', flat=True)
        lojas = Loja.objects.filter(cdloja__in=i)
    else:
        lojas = Loja.objects.all()


    return lojas