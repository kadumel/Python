import datetime
from django.core.exceptions import TooManyFieldsSent
from django.db.models.fields import NullBooleanField
from django.shortcuts import render, get_object_or_404, redirect
from .models import Acesso, Tipomovimento, Grupo, Subgrupo, Loja, Produto, Movimentacao, Itemmovimentado, Status
from .forms import LojaForm, TipoMovientoForm, GrupoForm, SubGrupoForm, ProdutoForm
from django.http import HttpResponse, Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
import json
from datetime import datetime as dt
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

        print('Conteudo da request: ', request.POST.get('loja'))
        print('Fim Ajax')

        prod = request.POST.get('produto')
        cdsbgp = request.POST.get('subgrupo')
        cdgp = request.POST.get('grupo')
        idMov = request.POST.get('idMov')
        tpMovimento = request.POST.get('movimento')

        conversao = list(Tipomovimento.objects.filter(nmtipomovimento=tpMovimento).values('conversao'))[0]['conversao']

        print(tpMovimento)
        
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
        if flag == 0:
            mov = Movimentacao.objects.create(
                        cdtipomovimento_id = pkModels('tpMov', cab['movimento']),
                        user_id = User.objects.filter(username=request.user).values('id'),
                        cdloja_id = pkModels('loja', cab['loja']),
                        dtmovimentacao = date,
                        status_id = 2).pk

            idMov = mov
        else:
            idMov = flag

        conversao = list(Tipomovimento.objects.filter(nmtipomovimento=cab['movimento']).values('conversao'))[0]['conversao']


        print(prod)
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
            
        dados = Itemmovimentado.objects.filter(cdmovimentacao_id=idMov).values('cdmovimentacao_id','cditemmovimentado', 'cdproduto__nmproduto','cdunidade__nmUnidade', 'valor', 'valorLiquido').order_by('cditemmovimentado')
       

        dados = json.dumps(list(dados))

        return HttpResponse(dados)

    else:
        raise Http404

    pass



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
            print("teste:" , i['cdmovimentacao'])
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
        print(lista)
        return HttpResponse(json.dumps(lista))

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




@login_required
def excluirItem(request):

    if request.is_ajax() and request.method == "POST":

        try:
            idMov = request.POST.get('idMov')
            idItem = request.POST.get('idItem')

            print(idMov, '-', idItem)

            Itemmovimentado.objects.filter(cditemmovimentado=idItem).delete()

            lista = getItens(idMov)
            return HttpResponse(json.dumps(lista))

        except ValueError as e:
            print(e)
            return HttpResponse("Erro ao exculir registro.")


    else:
        raise Http404



@login_required
def importData(request):

    if request.method == 'POST':

        dataset = Dataset()
        new_mov = request.FILES['myfile']
        imported_data = dataset.load(new_mov.read())

        listDate = []
        cliente = None
        listProdutos = []
        listProdutoErro = []

        for i in imported_data:

            # Agrupamento das datas
            if not i[4] in listDate:
                listDate.append(i[4])

             # Agrupamento dos produtos
            if not i[2] in listProdutos:
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
            print(v)
            idProduto = list(Produto.objects.filter(nmproduto=v).values("cdproduto", "nmproduto"))
            listAllProduct.append(idProduto)

            print(idProduto)
            if not idProduto:
                listProdutoErro.append(v)

        
        print(listProdutoErro   )  
        if not listProdutoErro and cliente != None:

            for x in listDate:

                print('inserindo cabeçalho')
                # Preenchimento do cabeçalho da movimentação
                data = dt.strptime(x, "%d/%m/%Y")
                print
                idMovimentacao = Movimentacao.objects.create(cdtipomovimento_id = 3,
                                                            user_id = User.objects.filter(username=request.user).values('id'),
                                                            cdloja_id = cliente,
                                                            dtmovimentacao = data,
                                                            status_id = 3).pk


                for j in imported_data:

                    if j[4] == x:

                        idProduto = list(Produto.objects.filter(nmproduto=j[2]).values("cdproduto", "cduniconv"))

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
            
            return HttpResponse(json.dumps(listProdutoErro))
            

    # return render(request, 'core/importaDados.html') 
    return render(request, 'core/importaDados.html') 