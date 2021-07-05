import pyodbc

def conexao():
    conn = pyodbc.connect('Driver={sql server};'
                          'Server=localhost\SQLEXPRESS;'
                          'Database=Pannemix;'
                          'Trusted_Connection=True;')
    return conn


def truncateTable(sql):
    cursor = conexao()
    cursor.execute(sql)
    cursor.commit()
    cursor.close()

def query(sql):
    cursor = conexao()
    cursor.execute(sql)
    cursor.commit()
    cursor.close()


def insert(sql, *args):
    cursor = conexao()
    cursor.execute(sql, *args)
    cursor.commit()
    cursor.close()


def insertLote(sql, args):
    cursor = conexao()
    lista = args
    for i in lista:
        cursor.execute(sql, i)
    cursor.commit()
    cursor.close()


def getId(sql):
    cursor = conexao()
    row = cursor.execute(sql)
    id = 0
    for i in row:
        if i.id != None:
            id = i.id

    cursor.close()
    return id


def getAll(sql):
    cursor = conexao()
    row = cursor.execute(sql)
    List = []
    for i in row:   
        List.append(i)
    cursor.close()
    return List
