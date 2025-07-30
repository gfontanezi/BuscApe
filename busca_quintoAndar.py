import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc

def buscar_imoveis_quinto_andar(url, pesquisa, estacao, criterio_de_ordenacao=None):
    
    print("Iniciando o driver com undetected-chromedriver em modo headless...")
    driver = None
    try:
        # A configuração de opções pode ser feita aqui se necessário, mas 
        # o 'uc' já faz o principal trabalho de se manter indetectável.
        # headless=True ativa o modo headless.
        driver = uc.Chrome(headless=True, use_subprocess=True)
        # Definimos o tamanho da janela aqui, que é importante para o headless.
        driver.set_window_size(1920, 1080)
        driver.get(url)
    except Exception as e:
        print(f"ERRO: Falha ao iniciar o undetected-chromedriver. Verifique a instalação.")
        print(f"Erro original: {e}")
        return []
    print(f"Acessando a URL: {url} (em modo headless)")

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
    
    time.sleep(1)

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

    # Procurar pela estação, se foi selecionada
    if pesquisa == 2:
        try:
            wait = WebDriverWait(driver, 15) # Tempo de espera maior para segurança
            
            # Etapa 1: Clicar para ativar (seu código aqui já é bom)
            search_container_locator = (By.XPATH, "//div[@data-testid='cockpit-location-input']")
            search_container = wait.until(EC.element_to_be_clickable(search_container_locator))
            search_container.click()

            # Etapa 2: Digitar no campo
            active_input_locator = (By.XPATH, "//div[@data-testid='cockpit-location-input']//input")
            active_input_field = wait.until(EC.visibility_of_element_located(active_input_locator))
            active_input_field.send_keys("estacao " + estacao)
            
            # Etapa 3: Espera Inteligente (SUBSTITUI O time.sleep(4))
            print("Aguardando o campo de busca se expandir (aria-expanded='true')...")
            wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@aria-expanded='true']")))

            # Etapa 4: Navegação por Teclado com Pausas Mínimas
            print("Campo expandido! Navegando com o teclado...")
            time.sleep(0.5) # Pausa mínima para o JS do site "respirar".
            active_input_field.send_keys(Keys.ARROW_DOWN)
            time.sleep(0.5)
            active_input_field.send_keys(Keys.ENTER)
            time.sleep(2) # Pausa para a página recarregar após o Enter.
        except Exception as e:
             print(f"Ocorreu um erro na busca por estação: {e}")
        

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
        time.sleep(0.5)
        print(f"\nIniciando processo de ordenação por: '{criterio_de_ordenacao}'...")
        try:
            seletor_botao_ordenar = '#SORT_BUTTON'
            botao_ordenar = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR,seletor_botao_ordenar)))
            driver.execute_script("arguments[0].click();", botao_ordenar)
            print("Botão 'Ordenar' clicado com sucesso via JavaScript.")
            
            xpath_opcao = f"//li[contains(., '{criterio_de_ordenacao}')]"
            opcao = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath_opcao)))
            # Clicar na opção
            driver.execute_script("arguments[0].click();", opcao)
            print(f"Opção '{criterio_de_ordenacao}' clicada com sucesso via JavaScript.")
            time.sleep(2) # Pausa para reordenação
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
            "url_imagem": "N/A",
            "quartos": "0",
            "preco_condominio_rs": "0"
        }

        condo_tag = card.find(string=re.compile(r'Condo\.'))
        if condo_tag:
            # O texto completo é algo como "R$ 1.000 Condo. + IPTU"
            # Usamos Regex para pegar apenas os números
            valor_match = re.search(r'([\d\.]+)', condo_tag)
            if valor_match:
                imovel_data['preco_condominio_rs'] = valor_match.group(1).replace('.', '')
        
        quartos_tag = card.find(string=re.compile(r'quarto', re.IGNORECASE))
        if quartos_tag:
            # O texto é algo como "18 m² · 1 quarto"
            # O Regex (\d+)\s*quarto pega o número antes da palavra "quarto"
            valor_match = re.search(r'(\d+)\s*quarto', quartos_tag.lower())
            if valor_match:
                imovel_data['quartos'] = valor_match.group(1)
        
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

