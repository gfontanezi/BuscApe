import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


tipo_venda = str(input("Alugar ou Comprar? ")).strip().lower()

bairro = str(input("Bairro: ")).strip().lower()
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
        url = f'https://www.quintoandar.com.br/alugar/imovel/{bairro}{cidade}-{estado}-brasil/{tipo_imovel}{quartos}de-{preco_min}-a-{preco_max}-reais'
    elif tipo_venda == "comprar":
        url = f'https://www.quintoandar.com.br/comprar/imovel/{cidade}-{estado}-brasil/{tipo_imovel}{quartos}de-{preco_min}-a-{preco_max}-venda'


def buscar_imoveis_quintoAndar(url):
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    print(f"Acessando a URL: {url}")
    driver.get(url)
    wait = WebDriverWait(driver, 30)
    print("Aguardando os imóveis carregarem...")
    try:
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-testid="property-card"]')))
        print("Imóveis carregados com sucesso!")
        # Adicionar uma pequena espera extra para garantir que tudo renderizou
        time.sleep(5) 
    except Exception as e:
        print(f"Não foi possível carregar os imóveis ou o seletor está incorreto: {e}")
        driver.quit()
        exit()

    html_content = driver.page_source

    driver.quit()

    soup = BeautifulSoup(html_content, 'html.parser')

    imoveis = soup.select('[data-testid="property-card"]')
    print(f"Encontrados {len(imoveis)} imóveis na página.")

    lista_de_imoveis = []

    for imovel in imoveis:
        try:
            # Use .find() ou .select_one() com os seletores corretos para cada informação.
            # Estes seletores SÃO APENAS EXEMPLOS. Você DEVE encontrá-los inspecionando o site.
            preco_element = imovel.select_one('[data-testid="property-card__price-value"]')
            endereco_element = imovel.select_one('[data-testid="property-card__address"]')
            area_element = imovel.select_one('[data-testid="property-card__area"]')

            # Extrair o texto e limpar (remover espaços em branco extras)
            preco = preco_element.get_text(strip=True) if preco_element else "N/A"
            endereco = endereco_element.get_text(strip=True) if endereco_element else "N/A"
            area = area_element.get_text(strip=True) if area_element else "N/A"

            # Adicionar os dados extraídos à nossa lista
            lista_de_imoveis.append({
                "preco_aluguel": preco,
                "endereco": endereco,
                "area": area
            })
        except Exception as e:
            print(f"Erro ao extrair dados de um imóvel: {e}")
            continue # Pula para o próximo imóvel em caso de erro

    # Imprimir os resultados de forma organizada
    for item in lista_de_imoveis:
        print(item)
