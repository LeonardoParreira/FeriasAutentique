import time
import pyodbc
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By


def busca_assinaturas():
    con = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                         "Server=10.0.73.209;"
                         "Database=DADOSRKF;"
                         "Uid=sa;"
                         "Pwd=TceRkf1935")
    df = pd.read_sql_query("SELECT * FROM RKF_AUTENTIQUE_FERIAS WHERE ENVIADO = ''", con)

    con.close()

    return df


def atualiza_status(status, line):
    con = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                         "Server=10.0.73.209;"
                         "Database=DADOSRKF;"
                         "Uid=sa;"
                         "Pwd=TceRkf1935")

    query = "UPDATE RKF_AUTENTIQUE_FERIAS SET ENVIADO = '" + status + "' WHERE ID = '" + str(line["ID"]) + "'"

    con.cursor().execute(query)
    con.commit()

    con.close()

    return


def login_intranet(usuario: str, senha: str):

    browser = webdriver.Chrome()
    browser.get("https://intranet.grupotristao.com/chat")

    username_input = browser.find_element(By.ID, "username")
    username_input.send_keys(usuario)

    browser.find_element(By.NAME, "user-login").submit()

    username_input = browser.find_element(By.ID, "password")
    username_input.send_keys(senha)

    browser.find_element(By.NAME, "user-login").submit()

    return browser


def envia_link(row, browser, mensagem):
    browser.refresh()
    chat_search = browser.find_element(By.ID, "search-input")
    chat_search.send_keys(row["SIGNATARIO"])
    # chat_search.send_keys("MIGUEL GOMES FERREIRA")

    browser.implicitly_wait(5)
    chat_contacts = browser.find_element(By.ID, "chat-contacts")
    browser.implicitly_wait(5)
    chat_contacts.find_element(By.CSS_SELECTOR, "li.talkToUser").click()
    browser.implicitly_wait(5)
    time.sleep(2)

    msg = "Olá, " + row["SIGNATARIO"] + "! " + mensagem + " Segue link: " + row["LINK"]

    browser.implicitly_wait(50)
    conversation_title = browser.find_element(By.CSS_SELECTOR, "div.conversation-title")
    browser.implicitly_wait(50)
    conversation_title_text = conversation_title.get_attribute("innerText")
    print(conversation_title_text, row["SIGNATARIO"])
    browser.implicitly_wait(50)
    if conversation_title_text == row["SIGNATARIO"]:
        chat_textarea = browser.find_element(By.ID, "chat-textarea")
        browser.implicitly_wait(5)
        chat_textarea.send_keys(msg)
        browser.implicitly_wait(5)
        browser.find_element(By.ID, "conversation-form-input").submit()
        browser.implicitly_wait(5)
        retorno = "S"
    else:
        retorno = "E"

    time.sleep(5)

    return retorno
