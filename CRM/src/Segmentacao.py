import connectionFactory as db
import connectionAPI as api
from datetime import datetime as dt

def getSegmentacao():

    url = 'https://api.rd.services/platform/segmentations'
    insert = 'set dateformat ymd insert into DimSegmentacaoRD values (?,?,?,?,?,?,?,?,?,?,?)'

    hash = True
    page = 1
    pageS = 125
    while hash == True: 

        listaDados = []
        dados = api.connectRD(url, page, pageS)
        if 'erros' in dados:
            hash = False
        else:
            for i in dados['segmentations']:
                for j in i.get['links']:

                    d = [
                        i.get('id'),
                        i.get('name'), 
                        i.get('standard'),
                        str(i.get('created_at'))[:19] ,
                        str(i.get('updated_at'))[:19] ,
                        i.get('process_status') ,
                        j['rel'],
                        j['href'],
                        j['media'],
                        j['type'],
                        str(dt.now())[:19]  
                    ]
                    listaDados.append(d)

            print(listaDados)
            db.query('truncate table DimSegmentacaoRD')
            db.insertLote(insert, listaDados)
            page = page + 1




def getContatos():

    # db.query('truncate table DimContatoRD')
    url = db.getAll('select id, href from DimSegmentacaoRD where id = 145858 ')
    insert = 'set dateformat ymd insert into DimContatoRD (segmentacao, uuid, email, name, last_conversion_date, created_at, href, dtimportacao) values (?,?,?,left(?,100),?,?,?,?)'

    for x in url:
        
        hash = True
        page = 2044
        pageS = 125

        while hash == True: 

            print(x , str(page), str(pageS))
            listaDados = []
            dados = api.connectRD(x[1], page, pageS)
            if 'erros' in dados:
                hash = False
            else:
                for i in dados['contacts']:
                    for j in i.get('links'):
                        dados = [
                            x[0],
                            i.get('uuid'),
                            i.get('email'), 
                            i.get('name'),
                            str(i.get('last_conversion_date'))[:19] ,
                            str(i.get('created_at'))[:19],
                            j['href'],
                            str(dt.now())[:19]  
                        ]
                        listaDados.append(dados)
                db.insertLote(insert, listaDados)
                page = page + 1





def updateContatos():

    
    # db.query('truncate table DimContatoRD')
    url = db.getAll('select uuid from DimContatoRD where tags is null')
    insert = """set dateformat ymd 
                    update DimContatoRD set 
                        state = ?,                     
                        city = ?,
                        personal_phone = ?,
                        tags = ?,
                        nmEstado = ?,
                        cf_nome_do_embaixador = ?,
                        cf_conteudo_de_interesse_leads = ?,
                        cf_assuntos_preferidos = ?,
                        cf_de_0_a_10_quanto_voce_recomendaria_a_fortes_tecnologia = ?,
                        cf_para_qual_sistema_deseja_demonstracao = ?,
                        cf_seu_cargo = ?,
                        cf_solucao_solicitada_site = ?,
                        cf_trilha_de_interesse_fortes_summit = ?,
                        cf_trilha_de_interesse_summit_2021 = ?,
                        cf_trilha_de_interesse_2 = ?,
                        cf_cnpj = ?,
                        cf_cargo_atualizado = ?,
                        cf_setor = ?,
                        cf_numero_de_funcionarios = ?,
                        cf_possui_empresa = ?,
                        cf_segmento_da_empresa = ?,
                        cf_produtos_recompra = ?,
                        cf_observacoes = ?,
                        cf_redes_sociais_segmento = ?,
                        cf_redes_sociais_cadastro_de_leads = ?,
                        cf_qual_sistema_deseja_orcamento = ?,
                        dtImportacao = ?
                    where 
                        uuid = ?    

            """
    k = 0
    for x in url:

        print(k, x[0])
        i = api.connectRD(f"https://api.rd.services/platform/contacts/{x[0]}",x[0])
        d = [
            i.get('state'),
            i.get('city'),
            i.get('personal_phone'),
            str(i.get('tags',None)).replace(",","|") ,
            i.get('cf_e9b63c61'),
            i.get('cf_nome_do_embaixador'),
            str(i.get('cf_conteudo_de_interesse_leads')).replace(",","|"),
            str(i.get('cf_assuntos_preferidos')).replace(",","|"),
            str(i.get('cf_de_0_a_10_quanto_voce_recomendaria_a_fortes_tecnologia')).replace(",","|"),
            str(i.get('cf_para_qual_sistema_deseja_demonstracao')).replace(",","|"),
            str(i.get('cf_seu_cargo')).replace(",","|"),
            str(i.get('cf_solucao_solicitada_site')).replace(",","|"),
            str(i.get('cf_trilha_de_interesse_fortes_summit')).replace(",","|"),
            str(i.get('cf_trilha_de_interesse_summit_2021')).replace(",","|") ,
            str(i.get('cf_trilha_de_interesse_2')).replace(",","|") ,
            i.get('cf_cnpj'),
            i.get('cf_cargo_atualizado'),
            i.get('cf_setor'),
            i.get('cf_numero_de_funcionarios'),
            i.get('cf_possui_empresa'),
            i.get('cf_segmento_da_empresa'),
            str(i.get('cf_produtos_recompra')).replace(",","|"),
            i.get('cf_observacoes'),
            i.get('cf_redes_sociais_segmento'),
            i.get('cf_redes_sociais_cadastro_de_leads'),
            str(i.get('cf_qual_sistema_deseja_orcamento')).replace(",","|"),
            str(dt.now())[:19],
            x[0]
        ]
        db.insert(insert, d, x[0], 'Contato')
        k = k + 1



def getFunnel():

    #db.query('truncate table DimFunil')
    uuid = db.getAll("""select distinct  uuid
                        from DimContatoRD c
                        where not exists (select * from dimfunil f where f.uuid = c.uuid)""")
    insert = 'set dateformat ymd insert into DimFunil  values (?,?,?,?,?,?,?,?)'

    for x in uuid:
        url = f"https://api.rd.services/platform/contacts/{x[0]}/funnels/default"
        dados = api.connectRD(url)
        print(str(dados) +' - '+ x[0])
        if not 'errors' in dados:
            d = [
                x[0],
                dados['lifecycle_stage'],
                dados['opportunity'], 
                dados['contact_owner_email'],
                dados['interest'] ,
                dados['fit'],
                dados['origin'],
                str(dt.now())[:19]  
            ]
            db.insert(insert, d)
        


def getEvents():

    # db.query('truncate table dimeventos')
    uuid = db.getAll('select distinct uuid from DimContatoRD where hreffunnel is null order by 1')
    insert = 'set dateformat ymd insert into dimeventos  values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'

    
    for x in uuid:
        url = f"https://api.rd.services/platform/contacts/{x[0]}/events?event_type=CONVERSION"  #funnels/default"
        dados = api.connectRD(url)
        print(x[0])
        
        listaDados = []
        if not 'errors' in dados:
            for j in dados :
            
                d = [
                    x[0],
                    j.get('event_type'),
                    j.get('event_family'),
                    str(j.get('event_identifier')),
                    str(j.get('event_timestamp'))[:19] ,
                    str(j['payload'].get('name')),
                    str(j['payload'].get('email')),
                    str(j['payload'].get('job_title')),
                    str(j['payload'].get('state')),
                    str(j['payload'].get('city')),
                    str(j['payload'].get('country')),
                    str(j['payload'].get('personal_phone')),
                    str(j['payload'].get('mobile_phone')),
                    str(j['payload'].get('twitter')),
                    str(j['payload'].get('facebook')),
                    str(j['payload'].get('linkedin')),
                    str(j['payload'].get('website')),
                    str(j['payload'].get('company_name')),
                    str(j['payload'].get('company_site')),
                    str(j['payload'].get('company_address')),
                    str(j['payload'].get('client_tracking_id')),
                    None,
                    str(j['payload'].get('traffic_medium')),
                    str(j['payload'].get('traffic_campaign')),
                    str(j['payload'].get('traffic_value')),
                    str(j['payload'].get('tags')),
                    str(j['payload'].get('available_for_mailing')),
                    str(j['payload'].get('cf_nome_do_embaixador')),
                    str(j['payload'].get('cf_conteudo_de_interesse_leads')),
                    str(j['payload'].get('cf_assuntos_preferidos')),
                    str(j['payload'].get('cf_de_0_a_10_quanto_voce_recomendaria_a_fortes_tecnologia')),
                    str(j['payload'].get('cf_para_qual_sistema_deseja_demonstracao')),
                    str(j['payload'].get('cf_seu_cargo')),
                    str(j['payload'].get('cf_solucao_solicitada_site')),
                    str(j['payload'].get('cf_trilha_de_interesse_fortes_summit')),
                    str(j['payload'].get('cf_trilha_de_interesse_summit_2021')),
                    str(j['payload'].get('cf_trilha_de_interesse_2')),
                    str(j['payload'].get('cf_cnpj')),
                    str(j['payload'].get('cf_cargo_atualizado')),
                    str(j['payload'].get('cf_setor')),
                    str(j['payload'].get('cf_numero_de_funcionarios')),
                    str(j['payload'].get('cf_possui_empresa')),
                    str(j['payload'].get('cf_segmento_da_empresa')),
                    str(j['payload'].get('cf_produtos_recompra')),
                    str(j['payload'].get('cf_observacoes')),
                    str(j['payload'].get('cf_redes_sociais_segmento')),
                    str(j['payload'].get('cf_redes_sociais_cadastro_de_leads')),
                    str(j['payload'].get('cf_qual_sistema_deseja_orcamento')),
                    str(dt.now())[:19]  
                ]
                listaDados.append(d)
            db.insertLote(insert, listaDados)
            db.query(f"update dimcontatord set hreffunnel = '1' where uuid = '{x[0]}'")

getEvents()