""" import requests
from bs4 import BeautifulSoup


response = requests.get('https://www.geonames.org/search.html?q=santo+andre&country=')
if response.status_code == 200:
    print("Sucesso! A requisição foi bem-sucedida.")
    print(response.text)
elif response.status_code == 404:
    print("Não encontrado. A URL pode estar errada.")
else:
    print(f"Algo deu errado. Código: {response.status_code}")
 """


import time
import re # Importamos a biblioteca de Expressões Regulares
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def buscar_imoveis_quinto_andar(url):
    # --- CONFIGURAÇÃO DO SELENIUM (igual ao anterior) ---
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('log-level=3')
    driver = webdriver.Chrome(service=service, options=options)

    print(f"Acessando a URL: {url}")
    driver.get(url)

    # --- ESPERAR CARREGAR COM O SELETOR CORRETO ---
    seletor_card_imovel = '[data-testid="house-card-container-rent"]'
    print("Aguardando os imóveis carregarem...")
    try:
        WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, seletor_card_imovel)))
        print("Imóveis carregados com sucesso!")
        time.sleep(5)
    except Exception as e:
        print(f"ERRO: Não foi possível carregar os imóveis. Seletor '{seletor_card_imovel}' pode estar incorreto.")
        driver.quit()
        return []
    
    
    # --- EXTRAÇÃO E ANÁLISE ---
    seletor_botao_ver_mais = '[data-testid="load-more-button"]'
    while True:
        try:
            # Procura pelo botão
            load_more_button = driver.find_element(By.CSS_SELECTOR, seletor_botao_ver_mais)
            
            # Rola a página para garantir que o botão esteja visível e clica nele via JavaScript
            driver.execute_script("arguments[0].click();", load_more_button)
            
            print("Clicando em 'Ver mais' para carregar mais imóveis...")
            # Espera um pouco para o conteúdo novo carregar
            time.sleep(3) 

        except NoSuchElementException:
            # Se o botão não for encontrado, significa que todos os imóveis foram carregados.
            print("Botão 'Ver mais' não encontrado. Todos os imóveis foram carregados.")
            break # Sai do loop
        except Exception as e:
            print(f"Ocorreu um erro ao tentar clicar no botão 'Ver mais': {e}")
            break # Sai do loop em caso de outros erros
    

    html_content = driver.page_source
    print("Página carregada. Fechando o navegador e iniciando a análise do HTML.")
    driver.quit()

    soup = BeautifulSoup(html_content, 'html.parser')
    cards_de_imoveis = soup.select(seletor_card_imovel)
    print(f"Encontrados {len(cards_de_imoveis)} imóveis na página.")

    # --- LOOP ÚNICO E CORRIGIDO ---
    lista_de_imoveis = []
    base_url = "https://www.quintoandar.com.br"

    for card in cards_de_imoveis:
        # 1. Encontrar o link (href)
        link_tag = card.find('a')
        url_completa = base_url + link_tag['href'] if link_tag and link_tag.has_attr('href') else "URL não encontrada"

        # 2. Encontrar a div com o aria-label
        info_div = card.find('div', {'aria-label': True})
        
        # 3. Extrair e processar os dados do aria-label
        if info_div:
            info_completa = info_div['aria-label']
            
            # Usando Expressões Regulares (Regex) para extrair os dados do texto
            aluguel_match = re.search(r'(\d+\.?\d*)\s+aluguel', info_completa)
            area_match = re.search(r'(\d+)\s+metros\s+quadrados', info_completa)
            endereco_match = re.search(r'\.\s+(.*?)\.\s+\d+\s+metros', info_completa)
            
            # Atribuir os valores ou "N/A" se não encontrados
            aluguel = aluguel_match.group(1).replace('.', '') if aluguel_match else "N/A"
            area = area_match.group(1) if area_match else "N/A"
            endereco = endereco_match.group(1) if endereco_match else "N/A"
            
            # 4. Adicionar tudo a um único dicionário
            lista_de_imoveis.append({
                "endereco": endereco,
                "area_m2": area,
                "preco_aluguel_rs": aluguel,
                "url_anuncio": url_completa
            })
        else:
            # Caso não encontre o aria-label por algum motivo
             lista_de_imoveis.append({
                "endereco": "N/A",
                "area_m2": "N/A",
                "preco_aluguel_rs": "N/A",
                "url_anuncio": url_completa
            })
    return lista_de_imoveis

# --- EXECUÇÃO DO SCRIPT ---
if __name__ == "__main__":
    url_alvo = 'https://www.quintoandar.com.br/alugar/imovel/morumbi-sao-paulo-sp-brasil/apartamento/2-quartos/de-1000-a-30000-reais'
    
    # Chama a função e guarda o resultado
    imoveis_encontrados = buscar_imoveis_quinto_andar(url_alvo)

    if imoveis_encontrados:
        print("\n--- DADOS EXTRAÍDOS COM SUCESSO ---\n")
        # Imprime cada imóvel de forma organizada
        for imovel in imoveis_encontrados:
            print(imovel)
    else:
        print("\nNenhum imóvel foi extraído. Verifique os logs de erro acima.")

