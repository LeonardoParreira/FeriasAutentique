import PyPDF2
from PyPDF2 import PdfWriter


class Documento:
    def __init__(self, caminho: str = None, signatario: str = None, matricula: str = None, nome_arquivo: str = None
                 , page_aviso: PyPDF2.PageObject = None, page_recibo: PyPDF2.PageObject = None):
        self.caminho = caminho
        self.signatario = signatario
        self.matricula = matricula
        self.nome_arquivo = nome_arquivo
        self.page_aviso = page_aviso
        self.page_recibo = page_recibo

    def criar_documento(self):
        pdf_writer = PdfWriter()
        recibo_lines = self.page_recibo.extract_text().splitlines()
        self.signatario = recibo_lines[5].split("Nome do Empregado.......: ")[1].replace("|", "").strip(" ")

        self.matricula = recibo_lines[6].split('Registro: ')[1].split(' ')[0].replace('|', '').strip(' ') + recibo_lines[6].split('Registro: ')[1].split(' ')[1].replace('|', '').strip(' ')
        print(self.matricula)

        try:
            data = self.page_aviso.extract_text().splitlines()[28].split("|")[4].strip().replace("/", "_")
        except:
            data = self.page_aviso.extract_text().splitlines()[29].split("|")[4].strip().replace("/", "_")

        self.nome_arquivo = "RECIBO DE FERIAS_" + data + "_" + self.signatario + "_" + self.matricula

        pdf_writer.add_page(self.page_aviso)
        pdf_writer.add_page(self.page_recibo)
        pdf_writer.write(self.caminho + "/" + self.nome_arquivo + ".pdf")

        print(self.nome_arquivo)

        return