
import ConnectionExact as exa
from datetime import datetime as dt

def getListLead():

    url = 'https://api.exactsales.com.br/v3/Leads'
    insert = 'set dateformat ymd insert into DimLeadExact values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'

    dados = exa.connectExact(url)

    lista = []
    for i in dados['value']:
        d = [
            i.get('lead'),
            i.get('registerDate'),
            i.get('updateDate'),
            i.get('mktLink'),
            i.get('phone1'),
            i.get('phone2'),
            i.get('website'),
            i.get('leadProduct'),
            i.get('description'),
            i.get('stage'),
            i.get('cnpj'),
            i.get('city'),
            i.get('state'),
            i.get('country'),
            i.get('integrationId'),
            i.get('id'),
            i.get('industry')['id'],
            i.get('industry_value'),
            i.get('source_id'),
            i.get('source_value'),
            i.get('subSource_id'),
            i.get('subSource_value'),
            i.get('sdr_id'),
            i.get('sdr_name'),
            i.get('sdr_lastName'),
            i.get('sdr_email'),
            i.get('salesRep_id'),
            i.get('salesRep_name'),
            i.get('salesRep_lastName'),
            i.get('salesRep_email')
        ]
        lista.append(d)
        print(d)
    


getListLead()