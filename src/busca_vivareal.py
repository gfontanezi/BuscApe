import time
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException

def clique_robusto(driver, wait, seletor):
    elemento = wait.until(EC.presence_of_element_located(seletor))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", elemento)
    time.sleep(0.5); wait.until(EC.element_to_be_clickable(seletor)); driver.execute_script("arguments[0].click();", elemento)

def digitar_robusto(driver, wait, seletor, texto_para_digitar):
    elemento = wait.until(EC.presence_of_element_located(seletor)); driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", elemento)
    time.sleep(0.5); wait.until(EC.element_to_be_clickable(seletor)); elemento.click(); elemento.clear(); elemento.send_keys(texto_para_digitar)

def raspar_resultados_final(driver, wait, chave_preco):

    print("\n[RASPAGEM] Iniciando a extração dos dados de todas as páginas...")

    resultados_completos = []
    pagina_atual = 1

    while True:
        print(f"[RASPAGEM] Analisando a página {pagina_atual}...")

        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li[data-cy='rp-property-cd']")))
            time.sleep(2)
        except TimeoutException:
            print(f"AVISO: Nenhum imóvel encontrado na página {pagina_atual}. Finalizando raspagem.")
            break

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        cards_de_imoveis = soup.select("li[data-cy='rp-property-cd']")

        if not cards_de_imoveis: break

        print(f"INFO: {len(cards_de_imoveis)} imóveis encontrados na página {pagina_atual}. Extraindo...")

        for card in cards_de_imoveis:
            imovel_info = {
                'endereco': "Não informado",
                'area_m2': "Não informado",
                chave_preco: "Não informado",
                'url_anuncio': "Não informado",
                'url_imagem': "Não informada",
                'quartos': "Não informado",
                'preco_condominio_rs': "Não informado"
            }

            try:
                bairro_cidade = card.select_one("h2[data-cy='rp-cardProperty-location-txt']").get_text(strip=True)

                partes = re.split(r'\s*em\s*', bairro_cidade, 1, flags=re.IGNORECASE)
                if len(partes) > 1:
                    bairro_cidade = partes[1]
                try:
                    rua = card.select_one("p[data-cy='rp-cardProperty-street-txt']").get_text(strip=True)
                    imovel_info['endereco'] = f"{bairro_cidade}, {rua}"
                except AttributeError: imovel_info['endereco'] = bairro_cidade
            except AttributeError: pass

            
            try:
                area_tag = card.select_one("div[data-cy='rp-card-area']")
                    
                imovel_info['area_m2'] = re.sub(r'[^\d]', '', area_tag.get_text(strip=True))

            except (AttributeError, TypeError):
                try:
                    area_h3 = card.find(lambda tag: tag.name == 'h3' and 'Tamanho do imóvel' in tag.get_text())
                        
                    imovel_info['area_m2'] = re.sub(r'[^\d]', '', area_h3.get_text(strip=True))

                except (AttributeError, TypeError):
                    pass

            try:
                price_tag = card.select_one("div[data-cy='rp-cardProperty-price-txt'] p.font-semibold")
                imovel_info[chave_preco] = re.sub(r'[^\d]', '', price_tag.get_text(strip=True))
            except (AttributeError, TypeError): pass

            link_tag = card.select_one("a[href*='/imovel/']")
            if link_tag and link_tag.has_attr('href'):
                href = link_tag['href']
                if href.startswith('/'): imovel_info['url_anuncio'] = 'https://www.vivareal.com.br' + href
                else: imovel_info['url_anuncio'] = href

            image_tag = card.find('img')
            if image_tag and image_tag.has_attr('src'):
                imovel_info['url_imagem'] = image_tag['src']

            try:
                quartos_tag = card.select_one("div[data-cy='rp-card-bedrooms']")
                match = re.search(r'\d+', quartos_tag.get_text(strip=True))
                imovel_info['quartos'] = match.group(0)
            except (AttributeError, TypeError):
                try:
                    quartos_h3 = card.find(lambda tag: tag.name == 'h3' and 'Quantidade de quartos' in tag.get_text())
                    match = re.search(r'\d+', quartos_h3.get_text(strip=True))
                    imovel_info['quartos'] = match.group(0)
                except (AttributeError, TypeError): pass

            try:
                condo_tag_text = card.find(string=re.compile(r'Condomínio|Cond\.', re.IGNORECASE))
                valor_match = re.search(r'R\$\s*([\d\.]+)', condo_tag_text)
                imovel_info['preco_condominio_rs'] = valor_match.group(1).replace('.', '')
            except (AttributeError, TypeError): pass

            resultados_completos.append(imovel_info)

        try:
            seletor_proxima_pagina = (By.CSS_SELECTOR, "button[data-testid='next-page']")
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable(seletor_proxima_pagina))
            clique_robusto(driver, wait, seletor_proxima_pagina)
            pagina_atual += 1
        except TimeoutException:
            print("\n[RASPAGEM] Fim da paginação. Botão 'Próxima página' não está mais ativo.")
            break

    return resultados_completos, pagina_atual

def buscar_imoveis_vivareal(transacao, cidade, bairro, rua="", tipo_imovel="ambos", quartos=0, preco_min=0, preco_max=0, perto_metro=False):
    
    tipo_imovel = tipo_imovel[:len(tipo_imovel)-1]
    quartos = str(quartos)[0] 

    if transacao.lower() == 'aluguel':
        url_vivaReal = "https://www.vivareal.com.br/aluguel/sp/"
        chave_preco = 'preco_aluguel_rs'
        seletor_min = "input[data-cy='rp-rentalMinPrice-inp']"; seletor_max = "input[data-cy='rp-rentalMaxPrice-inp']"
    else:
        url_vivaReal = "https://www.vivareal.com.br/venda/sp/"
        chave_preco = 'preco_venda_rs'
        seletor_min = "input[data-cy='rp-saleMinPrice-inp']"; seletor_max = "input[data-cy='rp-saleMaxPrice-inp']"

    print(f"INFO: Buscando imóveis para '{transacao.upper()}'")

    print("Iniciando o navegador...")
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled") 
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    
    dados_dos_imoveis = []

    try:
        quartos, preco_min, preco_max = int(quartos), int(preco_min), int(preco_max)
        driver.get(url_vivaReal); wait = WebDriverWait(driver, 20)
        try: WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))).click()
        except: pass
        campo_de_busca = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cy="rp-locations-ddl-trigger"]')))
        actions = ActionChains(driver); actions.click(campo_de_busca).send_keys(f"{rua}, {bairro}, {cidade}").perform(); time.sleep(1.5)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//label[.//span[text()='São Paulo']]"))).click(); time.sleep(0.5)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[data-cy="locations-item-input"]'))).click()
        try: wait.until(EC.element_to_be_clickable((By.ID, "cookie-banner-content"))).click()
        except: pass
        print("\n--- Localização definida. Aplicando filtros... ---\n"); time.sleep(2)

        if tipo_imovel == 'apartamento':
            print("[FILTRO] Selecionando tipo: Apartamento"); clique_robusto(driver, wait, (By.XPATH, "//label[contains(., 'Apartamento')]")); time.sleep(0.5)
        if quartos > 0:
            quartos_str = "4+" if quartos >= 4 else str(quartos); print(f"[FILTRO] Selecionando quartos: {quartos_str}")
            clique_robusto(driver, wait, (By.XPATH, f"//div[@data-cy='rp-bedroomQuantity-cb']//button[text()='{quartos_str}']")); time.sleep(0.5)
        if preco_min > 0:
            print(f"[FILTRO] Digitando preço mínimo: R$ {preco_min}"); digitar_robusto(driver, wait, (By.CSS_SELECTOR, seletor_min), str(preco_min))
        if preco_max > 0:
            print(f"[FILTRO] Digitando preço máximo: R$ {preco_max}"); digitar_robusto(driver, wait, (By.CSS_SELECTOR, seletor_max), str(preco_max)); time.sleep(0.5)
        if perto_metro:
            print("[FILTRO] Selecionando: Próximo ao metrô/trem"); clique_robusto(driver, wait, (By.CSS_SELECTOR, "label[for='nearsubway-tgl']")); time.sleep(0.5)
        print("\n[AÇÃO FINAL] Clicando em 'Buscar Imóveis'..."); clique_robusto(driver, wait, (By.CSS_SELECTOR, "button[data-cy='rp-search-btn']")); time.sleep(3)

        dados_dos_imoveis, total_de_paginas = raspar_resultados_final(driver, wait, chave_preco)
        
        if dados_dos_imoveis:
            import os
            caminho_arquivo = os.path.join("output", "imoveis_vivareal.json")
            pasta = os.path.dirname(caminho_arquivo)
            if not os.path.exists(pasta):
                os.makedirs(pasta)
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados_dos_imoveis, f, ensure_ascii=False, indent=4)
            print(f"\n✅ VivaReal: {len(dados_dos_imoveis)} imóveis salvos em '{caminho_arquivo}'.")
        else:
            print("\nAVISO: A automação foi concluída, mas nenhum dado foi raspado dos cards encontrados.")

    except Exception as e:
        print(f"\nOCORREU UM ERRO DURANTE A EXECUÇÃO: {e}")
        return [] 
    finally:
        print("Fechando o navegador.")
        driver.quit()
        return dados_dos_imoveis