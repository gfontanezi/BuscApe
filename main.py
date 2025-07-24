import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from busca_quintoAndar import buscar_imoveis_quinto_andar


tipo_venda = str(input("Alugar ou Comprar? ")).strip().lower()

bairro = str(input("Bairro: ")).strip().lower().replace(' ', '-')
bairro = f"{bairro}-" if bairro else ""

cidade = str(input("Cidade: ")).strip().lower().replace(' ', '-')

estado = str(input("Estado (sigla): ")).strip().lower()


tipo_imovel = str(input("Casa, Apartamento ou Ambos? ")).strip().lower()
if tipo_imovel == "ambos":
    tipo_imovel = ""
elif tipo_imovel in "casa apartamento":
    tipo_imovel = f"{tipo_imovel}/"


quartos = str(input("Quantos quartos: ")).strip().lower()
quartos = f"{quartos}-quartos/" if quartos else ""

if tipo_venda == "alugar":
    preco_min = int(input("Preço mínimo do aluguel (mínimo de R$500,00): R$"))
    if preco_min < 500:
        print("O preço mínimo do aluguel deve ser pelo menos R$500,00.")
        preco_min = 500
    else:
        print(f"Preço mínimo do aluguel definido para R${preco_min},00.")
    preco_max = int(input("Preço máximo do aluguel: R$"))

elif tipo_venda == "comprar":
    preco_min = int(input("Preço mínimo da compra (mínimo de R$150.000,00): R$"))
    if preco_min < 150000:
        print("O preço mínimo da compra deve ser pelo menos R$150.000,00.")
        preco_min = 150000
    else:
        print(f"Preço mínimo da compra definido para R${preco_min},00.")
    preco_max = int(input("Preço máximo da compra: R$"))


def url_quintoAndar(tipo_venda, tipo_imovel, cidade, estado, bairro, quartos, preco_min, preco_max):
    if tipo_venda == "alugar":
        url = f'https://www.quintoandar.com.br/alugar/imovel/{bairro}{cidade}-{estado}-brasil/{tipo_imovel}{quartos}proximo-ao-metro/de-{preco_min}-a-{preco_max}-reais'
    elif tipo_venda == "comprar":
        url = f'https://www.quintoandar.com.br/comprar/imovel/{bairro}{cidade}-{estado}-brasil/{tipo_imovel}{quartos}proximo-ao-metro/de-{preco_min}-a-{preco_max}-venda'
    return url

url = url_quintoAndar(tipo_venda, tipo_imovel, cidade, estado, bairro, quartos, preco_min, preco_max)
imoveis_encontrados_quintoAndar = buscar_imoveis_quinto_andar(url, criterio_de_ordenacao="Mais próximos")

