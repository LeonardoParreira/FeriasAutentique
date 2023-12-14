import requests
import pyodbc
from Documento import Documento


def create_document_mutation(token_api: str, documento: Documento, teste: str):
    url = "https://api.autentique.com.br/v2/graphql"
    headers = {'Authorization': 'Bearer ' + token_api}
    payload = {
        'operations': '{"query":"mutation CreateDocumentMutation('
                      ' $document: DocumentInput!'
                      ' ,$signers: [SignerInput!]!'
                      ' ,$file: Upload!'
                      ' ) {'
                      '     createDocument('
                      '         document: $document'
                      '         ,signers: $signers'
                      '         ,file: $file'
                      '     ) {'
                      '         id '
                      '         name '
                      '         refusable '
                      '         sortable '
                      '         created_at '
                      '         signatures { '
                      '             public_id '
                      '             name '
                      '             email '
                      '             created_at '
                      '             action { name } '
                      '             link { short_link } '
                      '             user { id name email }'
                      '         }'
                      '     }'
                      ' }"'
                      ' ,"variables":{'
                      '     "document": {'
                      '         "name": "' + documento.nome_arquivo.replace(".pdf", "") + '"'
                      '     }'
                      '     ,"signers": ['
                      '         {'
                      '             "name": "' + documento.signatario + '"'
                      '             ,"action": "SIGN"'
                      '             ,"positions": ['
                      '                 {"x": "70.0", "y": "59.0", "z": 1, "element": "NAME"}'
                      '                 ,{"x": "68.0", "y": "59.0", "z": 2, "element": "NAME"}'
                      '             ]'
                      '         }'
                      '         ,{'
                      '             "email": "' + busca_superior_imediato(documento.matricula[0:2], documento.matricula[2:8]) + '"'
                      '             ,"action": "SIGN"'
                      '             ,"positions": [{"x": "42.0", "y": "59.0", "z": 1, "element": "NAME"}]'
                      '         }'
                      '         ,{'
                      '             "email": "renata@realcafe.com.br"'
                      '             ,"action": "SIGN"'
                      '             ,"positions": [{"x": "13.0", "y": "59.0", "z": 1, "element": "NAME"}]'
                      '         }'
                      '     ]'
                      '     ,"file":null'
                      ' }'
                      '}',
        'map': '{"file": ["variables.file"]}'
    }
    files = [('file', open(documento.caminho+"/"+documento.nome_arquivo, 'rb'))]

    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    print(response.text)
    response_json = response.json()

    id_documento = response_json['data']['createDocument']['id']
    try:
        link = response_json['data']['createDocument']['signatures'][0]['link']['short_link']
        superior = response_json['data']['createDocument']['signatures'][1]['email']
    except:
        link = response_json['data']['createDocument']['signatures'][1]['link']['short_link']
        superior = response_json['data']['createDocument']['signatures'][2]['email']

    print("id:" + id_documento)
    print("link:" + link)
    print("superior:" + superior)
    #print("superior:" + response_json['data']['createDocument']['signatures'][1]['email'])
    salva_link(documento.signatario, link, id_documento, documento.nome_arquivo, superior)


def busca_superior_imediato(filial: str, matricula: str):
    con = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                         "Server=10.0.73.209;"
                         "Database=Folha12;"
                         "Uid=sa;"
                         "Pwd=TceRkf1935")

    query = "SELECT SRASUP.RA_MAT " \
            "   ,SRASUP.RA_NOME " \
            "   ,TRIM(SRASUP.RA_EMAIL) AS RA_EMAIL " \
            "FROM SRA010 SRA " \
            "LEFT JOIN SQB010 SQB ON ( " \
            "   QB_FILRESP = RA_FILIAL " \
            "   AND QB_DEPTO = RA_DEPTO " \
            "   AND SQB.D_E_L_E_T_ = '' ) " \
            "LEFT JOIN SRA010 SRASUP ON( " \
            "   SRASUP.RA_FILIAL = QB_FILRESP " \
            "   AND SRASUP.RA_MAT = QB_MATRESP " \
            "   AND SRASUP.RA_DEMISSA = '' " \
            "   AND SRASUP.D_E_L_E_T_ = '' ) " \
            "WHERE SRA.RA_FILIAL = '" + filial + "' " \
            "   AND SRA.RA_MAT = '" + matricula + "' " \
            "   AND SRA.RA_DEMISSA = '' " \
            "   AND SRA.D_E_L_E_T_ = ''"
    print(query)

    cursor = con.cursor()

    cursor.execute(query)
    row = cursor.fetchone()
    nome_superior = row.RA_NOME
    email_superior = row.RA_EMAIL
    print(row.RA_EMAIL)

    con.close()

    return email_superior


def salva_link(signatario: str, link: str, id_documento: str, titulo: str, superior: str):
    con = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                         "Server=10.0.73.209;"
                         "Database=DADOSRKF;"
                         "Uid=sa;"
                         "Pwd=TceRkf1935")

    cursor = con.cursor()
    query = "INSERT INTO RKF_AUTENTIQUE_FERIAS VALUES(" \
            "'" + link + "'" \
            ",'" + signatario + "'" \
            ",'" + titulo + "'" \
            ",'" + superior + "'" \
            ",'" + id_documento + "'" \
            ",''" \
            ")"
    print(query)

    cursor.execute(query)
    con.commit()
    con.close()
