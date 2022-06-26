from pyodbc import threadsafety
import requests, json, time, socket 
from datetime  import datetime as dt
import connectionFactory as cf



clientId = ''
clientSecret = ''
token = '1f0e6494-aa97-4cab-93c5-25ae63deb736'
rtoken = ''


def getToken():

    global clientId, clientSecret, token, rtoken
    dados = cf.getAll("select client_id, client_secret, access_token, refresh_token from token where crm = 'RD' ")
    clientId = dados[0][0] 
    clientSecret = dados[0][1]
    token = dados[0][2]
    rtoken = dados[0][3]



def connectExact(url):

    try:
        headers = {'content-type': 'application/json', 'token_exact': f'{token}'}
        
        z = 0
        while (z == 0):
            r = requests.get(url, headers=headers)
            dados = json.loads(r.text)
            if ('errors' in dados):
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




