import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def buscar_imoveis_quinto_andar(url, criterio_de_ordenacao=None):
    # --- 1. CONFIGURAÇÃO DO SELENIUM ---
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    
    # ***** CORREÇÕES PARA HEADLESS AQUI *****
    options.add_argument('--headless') 
    # 1. Definimos um tamanho de janela grande para o modo headless
    options.add_argument("--window-size=1920,1080") 
    
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('log-level=3')
    driver = webdriver.Chrome(service=service, options=options)
    # A linha abaixo não tem efeito no headless, mas não custa manter
    # driver.maximize_window() 
    actions = ActionChains(driver)

    print(f"Acessando a URL: {url} (em modo headless)")
    driver.get(url)

    # --- 2. ESPERAR CARREGAMENTO INICIAL ---
    seletor_card_imovel = '[data-testid="house-card-container-rent"]'
    print("Aguardando o carregamento inicial dos imóveis...")
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, seletor_card_imovel)))
        print("Imóveis iniciais carregados.")
    except Exception as e:
        print(f"ERRO: A página inicial não carregou nenhum imóvel.")
        driver.quit()
        return []

    # --- 3. ORDENAR A PÁGINA ---
    if criterio_de_ordenacao:
        print(f"\nIniciando processo de ordenação por: '{criterio_de_ordenacao}'...")
        try:
            seletor_botao_ordenar = '#SORT_BUTTON'
            botao_ordenar = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, seletor_botao_ordenar)))
            actions.move_to_element(botao_ordenar).click().perform()
            print(f"Botão 'Ordenar' clicado com sucesso.")
            time.sleep(2)

            xpath_opcao = f"//li[contains(., '{criterio_de_ordenacao}')]"
            
            print(f"Aguardando a opção '{criterio_de_ordenacao}' aparecer no menu...")
            opcao = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath_opcao)))
            actions.move_to_element(opcao).click().perform()
            print(f"Opção '{criterio_de_ordenacao}' clicada com sucesso.")

            print("Aguardando a página reordenar os imóveis...")
            time.sleep(5)
        except Exception as e:
            print(f"ERRO durante a ordenação: {e}")

    # --- 4. LOOP PARA CLICAR EM "VER MAIS" ---
    seletor_botao_ver_mais = '[data-testid="load-more-button"]'
    while True:
        try:
            # 2. Forçamos a rolagem da página para o final ANTES de procurar o botão
            print("Rolando para o final da página para encontrar o botão 'Ver mais'...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1) # Pequena pausa para a página reagir à rolagem

            load_more_button = driver.find_element(By.CSS_SELECTOR, seletor_botao_ver_mais)
            driver.execute_script("arguments[0].click();", load_more_button)
            print("Clicando em 'Ver mais'...")
            time.sleep(3)
        except NoSuchElementException:
            print("Botão 'Ver mais' não encontrado. Todos os imóveis foram carregados.")
            break
        except Exception as e:
            print(f"Ocorreu um erro ao clicar no botão 'Ver mais': {e}")
            break

    # --- 5. EXTRAÇÃO FINAL ---
    print("\nIniciando a extração de dados de TODOS os imóveis carregados...")
    html_content = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html_content, 'html.parser')
    cards_de_imoveis = soup.select(seletor_card_imovel)
    print(f"Analisando um total de {len(cards_de_imoveis)} imóveis.")

    lista_de_imoveis = []
    base_url = "https://www.quintoandar.com.br"
    for card in cards_de_imoveis:
        link_tag = card.find('a')
        url_completa = base_url + link_tag['href'] if link_tag and 'href' in link_tag.attrs else "URL não encontrada"

        info_div = card.find('div', {'aria-label': True})
        if info_div:
            info_completa = info_div['aria-label']
            aluguel_match = re.search(r'(\d+\.?\d*)\s+aluguel', info_completa)
            area_match = re.search(r'(\d+)\s+metros\s+quadrados', info_completa)
            endereco_match = re.search(r'\.\s+(.*?)\.\s+\d+\s+metros', info_completa)
            
            aluguel = aluguel_match.group(1).replace('.', '') if aluguel_match else "N/A"
            area = area_match.group(1) if area_match else "N/A"
            endereco = endereco_match.group(1) if endereco_match else "N/A"
            
            lista_de_imoveis.append({
                "endereco": endereco,
                "area_m2": area,
                "preco_aluguel_rs": aluguel,
                "url_anuncio": url_completa
            })
            
    return lista_de_imoveis


url_alvo = 'https://www.quintoandar.com.br/alugar/imovel/morumbi-sao-paulo-sp-brasil/apartamento/2-quartos/de-1000-a-30000-reais/proximos-ao-metro'
    
imoveis_encontrados = buscar_imoveis_quinto_andar(url_alvo, criterio_de_ordenacao="Mais próximos")

if imoveis_encontrados:
    print(f"\n--- DADOS EXTRAÍDOS DE {len(imoveis_encontrados)} IMÓVEIS ---\n")
    for imovel in imoveis_encontrados:
        print(imovel)
else:
    print("\nNenhum imóvel foi extraído.")