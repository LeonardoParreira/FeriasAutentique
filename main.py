import threading
from tkinter import Tk
import tkinter.filedialog as fd
import tkinter.messagebox as mb
import PySimpleGUI as Sg
import os
from PyPDF2 import PdfReader
import Documento
import AutentiqueAPI
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

import SeleniumAPI


def select_pdf():
    select_pdf_path = fd.askopenfilename(filetypes=[('pdf file', '*.pdf')])
    print(select_pdf_path)
    return select_pdf_path


def select_folder():
    select_folder_path = fd.askdirectory()
    print(select_folder_path)
    return select_folder_path


def menu_enviar_autentique():
    folder_path = ""
    layout_enviar_autentique = [
        [Sg.Text("Pasta Documentos: "), Sg.InputText("", key="folder_path", disabled=True),
         Sg.Button('Selecionar Pasta')]
        , [Sg.Button('Cancelar'), Sg.Button('Confirmar')]
    ]

    window_enviar_autentique = Sg.Window('FÉRIAS - ENVIAR PARA AUTENTIQUE', layout_enviar_autentique)

    while True:
        event, values = window_enviar_autentique.read()
        if event == 'Selecionar Pasta':
            folder_path = select_folder()
            window_enviar_autentique['folder_path'].update(folder_path)
        elif event == 'Confirmar':
            if folder_path != "":
                continua = True
                break
            elif pdf_path == "":
                mb.showwarning("ATENÇÃO", "Escolha a pasta com os arquivos de férias!")
        else:
            continua = False
            break

    window_enviar_autentique.close()
    return [continua, folder_path]


def menu_gerar_pdf():
    pdf_path = ""
    pasta_dest = ""

    layout = [
        [Sg.Text("Arquivo PDF: "), Sg.InputText("", key="pdf_path", disabled=True), Sg.Button('Selecionar Arquivo')]
        , [Sg.Text("Pasta Destino: "), Sg.InputText("", key="pasta_dest", disabled=True), Sg.Button('Selecionar Pasta')]
        , [Sg.Button('Cancelar'), Sg.Button('Confirmar')]
    ]
    window = Sg.Window('FÉRIAS - GERAR PDF', layout)

    while True:
        event, values = window.read()
        if event == 'Selecionar Arquivo':
            pdf_path = select_pdf()
            window['pdf_path'].update(pdf_path)
        elif event == 'Selecionar Pasta':
            pasta_dest = select_folder()
            window['pasta_dest'].update(pasta_dest)
        elif event == 'Confirmar':
            if pdf_path != "" and pasta_dest != "":
                continua = True
                break
            elif pdf_path == "":
                mb.showwarning("ATENÇÃO", "Escolha o arquivo PDF de férias!")
            elif pasta_dest == "":
                mb.showwarning("ATENÇÃO", "Escolha a pasta destino dos documentos!")
        else:
            continua = False
            break

    window.close()
    return [continua, pdf_path, pasta_dest]


def gerar_pdf(pdf_path, pasta_dest, pb_window: Sg.Window):
    pdf_pages = PdfReader(pdf_path).pages
    documentos: Documento = []

    pb_window.write_event_value('update_max_value', len(pdf_pages))
    for page in range(len(pdf_pages)):
        page_text = pdf_pages[page].extract_text()
        lines = page_text.splitlines()

        line1 = lines[1].replace("|", "").strip(" ")
        line2 = lines[2].replace("|", "").strip(" ")

        if line1 == "RECIBO DE FERIAS" and line2 == "================":
            documentos.append(
                Documento.Documento(caminho=pasta_dest, page_aviso=pdf_pages[page - 1],
                                    page_recibo=pdf_pages[page]))

        pb_window.write_event_value('update_pb', page)

    print(len(pdf_pages))
    print(len(documentos))
    # documentos[1].criar_documento()
    pb_window.write_event_value('update_max_value', len(documentos))
    for idx, documento in enumerate(documentos):
        documento.criar_documento()
        pb_window.write_event_value('update_pb', idx)

    pb_window.write_event_value('Exit', '')
    mb.showinfo("SUCESSO", "PDFs Gerados!")


def documentos_pasta(folder_path, pb_window: Sg.Window):
    documentos: Documento = []
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    pb_window.write_event_value('update_max_value', len(files))
    for idx, file in enumerate(files):
        matricula = file.split("_")[5].replace(".pdf", "")
        signatario = file.split("_")[4]
        documentos.append(
            Documento.Documento(caminho=folder_path, nome_arquivo=file, matricula=matricula, signatario=signatario)
        )
        pb_window.write_event_value('update_pb', idx + 1)

    print(documentos)
    pb_window.write_event_value('update_max_value', len(documentos))
    for idx, documento in enumerate(documentos):
        AutentiqueAPI.create_document_mutation("64db2a1a3085c4da4a776bbe19b8f54c3c2fee3c1443c00b99a19b21f5f18381"
                                               , documento
                                               , 'false')
        pb_window.write_event_value('update_pb', idx + 1)

    pb_window.write_event_value('Exit', '')


def menu_login_vivaintra():
    usuario = ""
    senha = ""
    mensagem = ""

    layout_vivaintra = [[Sg.Text('Usuario:'), Sg.InputText('comunicacaointerna@realcafe.com.br', key='user')]
        , [Sg.Text('Senha:'), Sg.InputText('', key='password', password_char='*')]
        , [Sg.Text('Mensagem:'), Sg.InputText('', key='message')]
        , [Sg.Button('Login'), Sg.Button('Cancel')]]

    window_vivaintra = Sg.Window('FÉRIAS - LOGIN VIVA INTRA', layout_vivaintra)

    while True:
        event, values = window_vivaintra.read()
        if event == 'Login':
            usuario = values['user']
            senha = values['password']
            mensagem = values['message']
            if usuario != "" and senha != "":
                continua = True
                break
            elif usuario == "":
                mb.showwarning("ATENÇÃO", "Informe o usuário!")
            else:
                mb.showwarning("ATENÇÃO", "Informe a senha!")
        else:
            continua = False
            break

    window_vivaintra.close()
    return [continua, usuario, senha, mensagem]


if __name__ == '__main__':

    Tk().withdraw()

    # Sg.theme("black")

    layout = [
        [Sg.Button('GERAR PDF')]
        , [Sg.Button('ENVIAR PARA AUTENTIQUE')]
        , [Sg.Button('ENVIAR CHAT VIVA INTRA')]
        , [Sg.Button('CANCELAR')]
    ]
    main_menu_window = Sg.Window('FÉRIAS', layout)

    while True:
        event, values = main_menu_window.read()
        if event == 'GERAR PDF':
            main_menu_window.disable()
            gerar_pdf_ret = menu_gerar_pdf()
            continua = gerar_pdf_ret[0]
            pdf_path = gerar_pdf_ret[1]
            pasta_dest = gerar_pdf_ret[2]
            if continua:

                layout_pb = [[Sg.ProgressBar(max_value=100, orientation='h', size=(20, 20), key='progress_pb')]]
                pb_window = Sg.Window("GERAR PDF", layout_pb, finalize=True)
                pb_window['progress_pb'].update(current_count=0)

                threading.Thread(target=gerar_pdf, args=(pdf_path, pasta_dest, pb_window), daemon=True).start()

                while True:
                    window, event, values = Sg.read_all_windows()
                    if event == 'Exit':
                        break
                    if event == 'update_max_value':
                        window['progress_pb'].update(current_count=0, max=values[event])
                        window.refresh()
                        continue
                    if event == 'update_pb':
                        window['progress_pb'].update(current_count=values[event])
                        window.refresh()
                        continue
                    else:
                        break
                pb_window.close()

                # gerar_pdf(pdf_path, pasta_dest)

            main_menu_window.enable()
            main_menu_window.force_focus()
        elif event == 'ENVIAR PARA AUTENTIQUE':
            main_menu_window.disable()
            enviar_autentique_ret = menu_enviar_autentique()
            continua = enviar_autentique_ret[0]
            folder_path = enviar_autentique_ret[1]
            print(folder_path)
            if continua:
                layout_pb = [[Sg.ProgressBar(max_value=100, orientation='h', size=(20, 20), key='progress_pb')]]
                pb_window = Sg.Window("ENVIAR PARA AUTENTIQUE", layout_pb, finalize=True)
                pb_window['progress_pb'].update(current_count=0)

                threading.Thread(target=documentos_pasta, args=(folder_path, pb_window), daemon=True).start()

                while True:
                    window, event, values = Sg.read_all_windows()
                    if event == 'Exit':
                        break
                    if event == 'update_max_value':
                        window['progress_pb'].update(current_count=0, max=values[event])
                        window.refresh()
                        continue
                    if event == 'update_pb':
                        window['progress_pb'].update(current_count=values[event])
                        window.refresh()
                        continue
                    else:
                        break
                pb_window.close()

            main_menu_window.enable()
            main_menu_window.force_focus()
        elif event == 'ENVIAR CHAT VIVA INTRA':
            main_menu_window.disable()

            login_vivaintra_ret = menu_login_vivaintra()
            continua = login_vivaintra_ret[0]
            usuario = login_vivaintra_ret[1]
            senha = login_vivaintra_ret[2]
            mensagem = login_vivaintra_ret[3]

            if continua:
                df = SeleniumAPI.busca_assinaturas()

                if df.empty:
                    mb.showwarning("ATENÇÃO", "Sem link para enviar!")
                else:
                    browser = None
                    try:
                        browser = SeleniumAPI.login_intranet(usuario, senha)
                        browser.refresh()
                    except:
                        mb.showwarning("ATENÇÃO", "Usuário ou senha inválido!")

                    if browser is not None:
                        for idx, row in df.iterrows():
                            try:
                                envia_link_ret = SeleniumAPI.envia_link(row, browser, mensagem)
                                SeleniumAPI.atualiza_status(envia_link_ret, row)
                            except:
                                SeleniumAPI.atualiza_status("E", row)
                        browser.close()

            main_menu_window.enable()
            main_menu_window.force_focus()
        else:
            break
