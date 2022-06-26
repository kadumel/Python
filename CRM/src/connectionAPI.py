from pyodbc import threadsafety
import requests, json, time, socket 
from datetime  import datetime as dt
import connectionFactory as cf



clientId = ''
clientSecret = ''
token = ''
rtoken = ''


def getToken():

    global clientId, clientSecret, token, rtoken
    dados = cf.getAll("select client_id, client_secret, access_token, refresh_token from token where crm = 'RD' ")
    clientId = dados[0][0] 
    clientSecret = dados[0][1]
    token = dados[0][2]
    rtoken = dados[0][3]



def connectRD(url, uuid = None, origem = None, page = None, pageS = None):

    global token
    try:
        getToken()
        headers = {'content-type': 'application/json', 'Authorization': f'Bearer {token}'}
        
        if page == None: 
            param = {}
        else:
            param = {'page':page,'page_size':pageS}

        z = 0

        # print(url)
        while (z == 0):
            r = requests.get(url, headers=headers, params=param)
            dados = json.loads(r.text)
            if ('errors' in dados):
                print(dados)
                if type(dados['errors']) is list:
                    if  dados['errors'][0]['error_type'] == 'SERVICE_UNAVAILABLE':
                        print('Serviço Indisponivel!!!')
                        z = 1
                    # elif dados['errors']['error_type'] == 'RESOURCE_NOT_FOUND':
                elif 'RESOURCE_NOT_FOUND' in  dados['errors']['error_type']:
                    if origem == "Contato":
                        cf.insert(f"set dateformat ymd update DimcontadoRD set tags = 'RESOURCE_NOT_FOUND', dtimportacao = '{str(dt.now())[:19]}' where uuid = '{uuid}'")
                    print('Recurso não encontrado!!!')
                    z = 1
                # elif dados['errors']['error_type'] == 'UNAUTHORIZED':
                elif 'UNAUTHORIZED' in dados['errors']['error_type']:
                    print('Atualizar token!!!')
                    refreshConnectRD()
                else: 
                    print('Aguarde 10 segundos...')
                    time.sleep(5)
            else:
                z = 1

        return dados
    except ValueError:
        print('Erro ao conectar na API!!!', dados)



def refreshConnectRD():
    global token, rtoken
    try:
        url = 'https://api.rd.services/auth/token'
        headers = {'content-type': 'application/json'}
        param = {'client_id':f'{clientId}', 'client_secret': f'{clientSecret}','refresh_token':f'{rtoken}'}

        r = requests.post(url, headers=headers, params=param)
        dados = json.loads(r.text)
        data = str(dt.now())[:19]
        print(data)
        cf.query(f"set dateformat ymd update token set access_token = '{dados['access_token']}', expires_in = '{dados['expires_in']}', refresh_token = '{dados['refresh_token']}', updateDate = '{data}' where crm = 'RD'")
        token = dados['access_token']
        rtoken = dados['refresh_token']

    except ValueError:
        print('Erro ao atualizar token RD!!!', dados)




