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
    # Configuração do Selenium com o Chrome
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    
    options.add_argument('--headless') 
    options.add_argument("--window-size=1920,1080") 
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('log-level=3')
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window() 
    actions = ActionChains(driver)

    print(f"Acessando a URL: {url} (em modo headless)")
    driver.get(url)

    if "alugar" in url:
        chave_preco = "preco_aluguel_rs"
        tipo_negocio = "aluguel"
    elif "comprar" in url:
        chave_preco = "preco_venda_rs"
        tipo_negocio = "venda"
    else:
        # Padrão, caso não encontre nenhum dos dois
        chave_preco = "preco_rs"
        tipo_negocio = "venda|aluguel" # Regex para procurar qualquer um dos dois
    
    print(f"Tipo de negociação detectado: {tipo_negocio.split('|')[0]}")
    
    time.sleep(0.5)

    try:
        textos_aceitar = ["Aceitar todos", "Aceitar", "Concordo", "Entendi"]
        for texto in textos_aceitar:
            xpath_botao_cookie = f"//button[contains(., '{texto}')]"
            # Usamos find_elements para não quebrar o script se o botão não existir
            botoes_cookie = driver.find_elements(By.XPATH, xpath_botao_cookie)
            if botoes_cookie:
                print(f"Pop-up com texto '{texto}' encontrado. Tentando clicar...")
                botoes_cookie[0].click()
                print("Pop-up clicado com sucesso.")
                time.sleep(0.5)
                break
    except Exception as e:
        print(f"Não foi possível clicar no pop-up de cookie, ou ele não foi encontrado. Erro: {e}")

    # Carregamento inicial
    seletor_card_imovel = '[data-testid="house-card-container"]'
    print("Aguardando o carregamento inicial dos imóveis...")
    try:
        # Procura o card do imóvel para garantir que a página carregou corretamente
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, seletor_card_imovel)))
        print("Imóveis iniciais carregados com sucesso.")
    except Exception as e:
        print(f"ERRO: A página inicial não carregou os imóveis a tempo.")
        driver.quit()
        return []

    # Ordena a página pela proximidade do metrô
    if criterio_de_ordenacao:
        print(f"\nIniciando processo de ordenação por: '{criterio_de_ordenacao}'...")
        try:
            seletor_botao_ordenar = '#SORT_BUTTON'
            botao_ordenar = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR,seletor_botao_ordenar)))
            actions.move_to_element(botao_ordenar).click().perform()
            print(f"Botão 'Ordenar' clicado com sucesso.")
            time.sleep(0.3)

            xpath_opcao = f"//li[contains(., '{criterio_de_ordenacao}')]"
            
            print(f"Aguardando a opção '{criterio_de_ordenacao}' aparecer no menu...")
            opcao = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath_opcao)))
            actions.move_to_element(opcao).click().perform()
            print(f"Opção '{criterio_de_ordenacao}' clicada com sucesso.")

            print("Aguardando a página reordenar os imóveis...")
            time.sleep(0.3)
        except Exception as e:
            print(f"ERRO durante a ordenação: {e}")

    # Loop clicar em "Ver mais"
    seletor_botao_ver_mais = '[data-testid="load-more-button"]'
    while True:
        try:
            # Rola a página para garantir que o botão esteja visível
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.6)

            # Encontra o botão
            load_more_button = driver.find_element(By.CSS_SELECTOR, seletor_botao_ver_mais)
            
            # Apenas clica no botão se ele estiver habilitado
            if load_more_button.is_enabled():
                print("Botão 'Ver mais' está habilitado. Clicando...")
                driver.execute_script("arguments[0].click();", load_more_button)
                time.sleep(0.6)
            else:
                # Se o botão for encontrado mas não estiver habilitado, paramos.
                print("Botão 'Ver mais' encontrado, mas está desabilitado. Fim do carregamento.")
                break

        except NoSuchElementException:
            # Se o botão não for mais encontrado no HTML, paramos.
            print("Botão 'Ver mais' não foi encontrado no HTML. Todos os imóveis foram carregados.")
            break
        except Exception as e:
            print(f"Ocorreu um erro inesperado ao clicar no botão 'Ver mais': {e}")
            break

    # Extração dos dados dos imóveis
    time.sleep(0.5)
    print("\nIniciando a extração de dados de TODOS os imóveis carregados...")
    html_content = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html_content, 'html.parser')
    cards_de_imoveis = soup.select('[data-testid^="house-card-container"]')
    print(f"Analisando um total de {len(cards_de_imoveis)} imóveis.")

    lista_de_imoveis = []
    base_url = "https://www.quintoandar.com.br"

    for card in cards_de_imoveis:
        # 1. Cria um dicionário com valores padrão
        imovel_data = {
            "endereco": "N/A",
            "area_m2": "N/A",
            chave_preco: "N/A",
            "url_anuncio": "N/A",
            "url_imagem": "N/A"
        }

        # 2. Tenta extrair cada informação de forma independente
        
        # --- LINK DO ANÚNCIO ---
        link_tag = card.find('a')
        if link_tag and 'href' in link_tag.attrs:
            imovel_data['url_anuncio'] = base_url + link_tag['href']

        # --- URL DA IMAGEM ---
        image_tag = card.find('img')
        if image_tag and 'src' in image_tag.attrs:
            if image_tag['src'].startswith('http'):
                imovel_data['url_imagem'] = image_tag['src']
            else:
                imovel_data['url_imagem'] = base_url + image_tag['src']

        # --- ENDEREÇO E ÁREA (pelo aria-label, que é bom para isso) ---
        info_div = card.find('div', {'aria-label': True})
        if info_div:
            info_completa = info_div['aria-label']
            area_match = re.search(r'(\d+)\s+metros\s+quadrados', info_completa)
            endereco_match = re.search(r'\.\s+(.*?)\.\s+\d+\s+metros', info_completa)
            if area_match:
                imovel_data['area_m2'] = area_match.group(1)
            if endereco_match:
                imovel_data['endereco'] = endereco_match.group(1)

        # --- PREÇO (LÓGICA FINAL E MAIS ROBUSTA) ---
        # Encontra todas as tags <p> dentro do card
        todos_paragrafos = card.find_all('p')
        for p in todos_paragrafos:
            texto_paragrafo = p.get_text(strip=True)
            # O primeiro parágrafo que começar com R$ é o preço principal
            if texto_paragrafo.startswith("R$"):
                valor_match = re.search(r'([\d\.]+)', texto_paragrafo)
                if valor_match:
                    imovel_data[chave_preco] = valor_match.group(1).replace('.', '')
                    # Uma vez que encontramos, paramos o loop para não pegar outros valores (ex: condomínio)
                    break 
        
        # 3. Adiciona o dicionário à lista final
        lista_de_imoveis.append(imovel_data)
            
    return lista_de_imoveis