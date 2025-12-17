import time
import re
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains # Adicione esta também para garantir
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
import undetected_chromedriver as uc

def buscar_imoveis_quinto_andar(url, pesquisa, estacao, criterio_de_ordenacao=None):
    
    print("Iniciando o driver com undetected-chromedriver em modo headless...")
    driver = None
    try:
        driver = uc.Chrome(headless=False, use_subprocess=True)
        driver.set_window_size(1920, 1080)
        driver.get(url)
    except Exception as e:
        print(f"ERRO: Falha ao iniciar o undetected-chromedriver. Verifique a instalação.")
        print(f"Erro original: {e}")
        return []
    print(f"Acessando a URL: {url}")

    if "alugar" in url:
        chave_preco = "preco_aluguel_rs"
        tipo_negocio = "aluguel"
    elif "comprar" in url:
        chave_preco = "preco_venda_rs"
        tipo_negocio = "venda"
    else:
        chave_preco = "preco_rs"
        tipo_negocio = "venda|aluguel" 

    print(f"Tipo de negociação detectado: {tipo_negocio.split('|')[0]}")
    
    time.sleep(1)

    try:
        textos_aceitar = ["Aceitar todos", "Aceitar", "Concordo", "Entendi"]
        for texto in textos_aceitar:
            xpath_botao_cookie = f"//button[contains(., '{texto}')]"
            botoes_cookie = driver.find_elements(By.XPATH, xpath_botao_cookie)
            if botoes_cookie:
                print(f"Pop-up com texto '{texto}' encontrado. Tentando clicar...")
                botoes_cookie[0].click()
                print("Pop-up clicado com sucesso.")
                time.sleep(0.5)
                break
    except Exception as e:
        print(f"Não foi possível clicar no pop-up de cookie, ou ele não foi encontrado. Erro: {e}")

    if pesquisa == 2:
        try:
            print(f"Pesquisando pela estação: {estacao}")
            wait = WebDriverWait(driver, 15) 

            search_container_locator = (By.XPATH, "//div[@data-testid='cockpit-location-input']")
            search_container = wait.until(EC.element_to_be_clickable(search_container_locator))
            search_container.click()

            active_input_locator = (By.XPATH, "//div[@data-testid='cockpit-location-input']//input")
            active_input_field = wait.until(EC.visibility_of_element_located(active_input_locator))
            
            active_input_field.send_keys(Keys.CONTROL + "a")
            active_input_field.send_keys(Keys.DELETE)
            time.sleep(0.5)

            texto_busca = "Estação " + estacao
            for letra in texto_busca:
                active_input_field.send_keys(letra)
                time.sleep(0.01) 
            
            print(f"Texto '{texto_busca}' digitado. Aguardando 3 segundos para o site carregar a lista...")
            time.sleep(3) 

            xpath_primeira_opcao = "(//li[@role='option'])[1]"
            primeira_opcao = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_primeira_opcao)))
            
            texto_da_opcao = primeira_opcao.text
            print(f"Opção carregada e encontrada: '{texto_da_opcao}'. Clicando...")
            
            primeira_opcao.click()
            time.sleep(4) 

        except Exception as e:
             print(f"ERRO ao selecionar a estação: {e}")
             print("Tentando fallback com ENTER...")
             try:
                 ActionChains(driver).send_keys(Keys.ENTER).perform()
                 time.sleep(4)
             except Exception as e_fallback: 
                 print(f"Fallback falhou: {e_fallback}")
        

    seletor_card_imovel = '[data-testid="house-card-container"]'
    print("Aguardando o carregamento inicial dos imóveis...")
    try:
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, seletor_card_imovel)))
        print("Imóveis iniciais carregados com sucesso.")
    except Exception as e:
        print(f"ERRO: A página inicial não carregou os imóveis a tempo.")
        driver.quit()
        return []

    if criterio_de_ordenacao:
        time.sleep(0.5)
        print(f"\nIniciando processo de ordenação por: '{criterio_de_ordenacao}'...")
        try:
            seletor_botao_ordenar = '#SORT_BUTTON'
            botao_ordenar = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR,seletor_botao_ordenar)))
            driver.execute_script("arguments[0].click();", botao_ordenar)
            print("Botão 'Ordenar' clicado com sucesso via JavaScript.")
            
            xpath_opcao = f"//li[contains(., '{criterio_de_ordenacao}')]"
            opcao = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath_opcao)))
            driver.execute_script("arguments[0].click();", opcao)
            print(f"Opção '{criterio_de_ordenacao}' clicada com sucesso via JavaScript.")
            time.sleep(2)
        except Exception as e:
            print(f"ERRO durante a ordenação: {e}")

    seletor_botao_ver_mais = '[data-testid="load-more-button"]'
    while True:
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.6)

            load_more_button = driver.find_element(By.CSS_SELECTOR, seletor_botao_ver_mais)
            
            if load_more_button.is_enabled():
                print("Botão 'Ver mais' está habilitado. Clicando...")
                driver.execute_script("arguments[0].click();", load_more_button)
                time.sleep(0.6)
            else:
                print("Botão 'Ver mais' encontrado, mas está desabilitado. Fim do carregamento.")
                break

        except NoSuchElementException:
            print("Botão 'Ver mais' não foi encontrado no HTML. Todos os imóveis foram carregados.")
            break
        except Exception as e:
            print(f"Ocorreu um erro inesperado ao clicar no botão 'Ver mais': {e}")
            break

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
        imovel_data = {
            "endereco": "N/A",
            "area_m2": "N/A",
            chave_preco: "N/A",
            "url_anuncio": "N/A",
            "url_imagem": "N/A",
            "quartos": "0",
            "preco_condominio_rs": "0"
        }

        condo_tag = card.find(string=re.compile(r'Condo\.'))
        if condo_tag:
            valor_match = re.search(r'([\d\.]+)', condo_tag)
            if valor_match:
                imovel_data['preco_condominio_rs'] = valor_match.group(1).replace('.', '')
        
        quartos_tag = card.find(string=re.compile(r'quarto', re.IGNORECASE))
        if quartos_tag:
            valor_match = re.search(r'(\d+)\s*quarto', quartos_tag.lower())
            if valor_match:
                imovel_data['quartos'] = valor_match.group(1)
        
        link_tag = card.find('a')
        if link_tag and 'href' in link_tag.attrs:
            imovel_data['url_anuncio'] = base_url + link_tag['href']

        image_tag = card.find('img')
        if image_tag and 'src' in image_tag.attrs:
            if image_tag['src'].startswith('http'):
                imovel_data['url_imagem'] = image_tag['src']
            else:
                imovel_data['url_imagem'] = base_url + image_tag['src']

        info_div = card.find('div', {'aria-label': True})
        if info_div:
            info_completa = info_div['aria-label']
            area_match = re.search(r'(\d+)\s+metros\s+quadrados', info_completa)
            endereco_match = re.search(r'\.\s+(.*?)\.\s+\d+\s+metros', info_completa)
            if area_match:
                imovel_data['area_m2'] = area_match.group(1)
            if endereco_match:
                imovel_data['endereco'] = endereco_match.group(1)

        todos_paragrafos = card.find_all('p')
        for p in todos_paragrafos:
            texto_paragrafo = p.get_text(strip=True)
            if texto_paragrafo.startswith("R$"):
                valor_match = re.search(r'([\d\.]+)', texto_paragrafo)
                if valor_match:
                    imovel_data[chave_preco] = valor_match.group(1).replace('.', '')
                    break 
        
        lista_de_imoveis.append(imovel_data)
            
    return lista_de_imoveis

