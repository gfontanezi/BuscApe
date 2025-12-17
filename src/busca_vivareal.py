import time
import json
import re
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Constante para limitar a busca
LIMITE_IMOVEIS = 250

def buscar_imoveis_vivareal(transacao, cidade, bairro, rua="", tipo_imovel="ambos", quartos=0, preco_min=0, preco_max=0, perto_metro=False):
    
    # --- CONFIGURAÇÃO ---
    if transacao.lower() == 'alugar':
        url_base = "https://www.vivareal.com.br/aluguel/sp/"
        chave_preco = 'preco_aluguel_rs'
        seletor_min = "input[data-cy='rp-rentalMinPrice-inp']"
        seletor_max = "input[data-cy='rp-rentalMaxPrice-inp']"
    else:
        url_base = "https://www.vivareal.com.br/venda/sp/"
        chave_preco = 'preco_venda_rs'
        seletor_min = "input[data-cy='rp-saleMinPrice-inp']"
        seletor_max = "input[data-cy='rp-saleMaxPrice-inp']"

    termo_busca = ""
    if rua: termo_busca = f"{rua}"
    elif bairro: termo_busca = f"{bairro}"
    else: termo_busca = f"{cidade}"
    
    termo_busca = termo_busca.replace("-", " ").strip()

    print(f"INFO: Iniciando busca no VivaReal por: '{termo_busca}'")
    
    # --- DRIVER ---
    print("Iniciando driver em modo anti-bloqueio...")
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    driver = uc.Chrome(options=options, use_subprocess=True)
    wait = WebDriverWait(driver, 20)
    dados_imoveis = []

    try:
        driver.get(url_base)
        
        try:
            btn_cookie = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "cookie-notifier-cta")))
            btn_cookie.click()
        except: pass

        # --- 1. LOCALIZAÇÃO ---
        print("\n--- 1. Localizando imóvel ---")
        try:
            seletor_input = (By.CSS_SELECTOR, "input[data-cy='autocomplete-input']")
            campo_busca = wait.until(EC.element_to_be_clickable(seletor_input))
            campo_busca.click()
            time.sleep(1)
            campo_busca.send_keys(Keys.CONTROL + "a")
            campo_busca.send_keys(Keys.DELETE)
            time.sleep(0.5)
            
            for letra in termo_busca:
                campo_busca.send_keys(letra)
                time.sleep(random.uniform(0.05, 0.15))
            
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-cy='autocomplete-item']")))
            time.sleep(1.5)

            sugestoes = driver.find_elements(By.CSS_SELECTOR, "button[data-cy='autocomplete-item']")
            if sugestoes:
                print(f"Selecionando: {sugestoes[0].text}")
                sugestoes[0].click()
            else:
                campo_busca.send_keys(Keys.ENTER)
            
            time.sleep(5) 

        except Exception as e:
            print(f"ERRO na busca de local: {e}")

        # --- 2. FILTROS ---
        print("\n--- 2. Aplicando Filtros ---")

        if tipo_imovel:
            tipo_limpo = tipo_imovel.lower().replace('/', '')
            try:
                if 'apartamento' in tipo_limpo:
                    xpath = "//label[@data-testid='multiselect-item-apartamento']"
                    elem = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                    elem.click()
                elif 'casa' in tipo_limpo:
                    xpath = "//label[@data-testid='multiselect-item-casa']"
                    elem = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                    elem.click()
                time.sleep(1)
            except: pass

        if quartos and int(str(quartos)[0]) > 0:
            qtd = int(str(quartos)[0])
            texto_botao = f"{qtd}+" if qtd < 4 else "4+"
            try:
                xpath = f"//div[@data-cy='rp-bedroomQuantity-cb']//button[contains(text(), '{texto_botao}')]"
                btn = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                btn.click()
                time.sleep(1)
            except: pass

        if perto_metro:
            print("Tentando ativar filtro: Próximo ao Metrô...")
            try:
                driver.execute_script("document.getElementById('nearsubway-tgl').click();")
                time.sleep(2)
            except: pass

        if int(preco_min) > 0:
            try:
                inp = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, seletor_min)))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", inp)
                inp.click(); inp.send_keys(Keys.CONTROL + "a"); inp.send_keys(Keys.DELETE)
                inp.send_keys(str(preco_min))
            except: pass

        if int(preco_max) > 0:
            try:
                inp = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, seletor_max)))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", inp)
                inp.click(); inp.send_keys(Keys.CONTROL + "a"); inp.send_keys(Keys.DELETE)
                inp.send_keys(str(preco_max))
                inp.send_keys(Keys.ENTER) 
                time.sleep(5)
            except: pass

        # --- 3. ORDENAÇÃO ---
        print("\n--- 3. Ordenando por Menor Preço ---")
        current_url = driver.current_url
        if "ordem=LOWEST_PRICE" not in current_url:
            separator = "&" if "?" in current_url else "?"
            nova_url = f"{current_url}{separator}ordem=LOWEST_PRICE"
            driver.get(nova_url)
            print("Página recarregada para ordenar.")
            time.sleep(6)

        # --- 4. RASPAGEM ---
        dados_imoveis = raspar_resultados_regex(driver, wait, chave_preco)
        
        if dados_imoveis:
             import os
             caminho = os.path.join("output", "imoveis_vivareal.json")
             if not os.path.exists("output"): os.makedirs("output")
             with open(caminho, 'w', encoding='utf-8') as f:
                 json.dump(dados_imoveis, f, indent=4, ensure_ascii=False)

    except Exception as e:
        print(f"Erro crítico: {e}")
    finally:
        driver.quit()
        return dados_imoveis

def raspar_resultados_regex(driver, wait, chave_preco):
    print("\n[RASPAGEM] Extraindo dados (Filtrando sem URL)...")
    resultados = []
    pagina = 1
    total_coletado = 0
    
    while True:
        if total_coletado >= LIMITE_IMOVEIS:
            print(f"🛑 Limite de {LIMITE_IMOVEIS} imóveis atingido.")
            break

        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li[data-cy='rp-property-cd']")))
        except:
            print("Fim da listagem ou erro de carregamento.")
            break
            
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        cards = soup.select("li[data-cy='rp-property-cd']")
        
        if not cards: break
        
        novos_nesta_pagina = 0
        
        for card in cards:
            if total_coletado >= LIMITE_IMOVEIS: break

            imovel_data = {
                "endereco": "N/A",
                "area_m2": "0",
                chave_preco: "0",
                "url_anuncio": "N/A",
                "url_imagem": "N/A",
                "quartos": "0",
                "preco_condominio_rs": "0"
            }

            # 1. ENDEREÇO
            try: 
                loc_text = card.select_one("h2[data-cy='rp-cardProperty-location-txt']").get_text(strip=True)
                if " - " in loc_text:
                    imovel_data['endereco'] = loc_text.split(" - ")[0].strip()
                else:
                    imovel_data['endereco'] = loc_text
            except: 
                imovel_data['endereco'] = "Endereço não informado"

            # 2. PREÇO
            try:
                preco_container = card.select_one("div[data-cy='rp-cardProperty-price-txt']").get_text()
                match = re.search(r'R\$\s*(\d{1,3}(?:\.\d{3})*)', preco_container)
                if match:
                    imovel_data[chave_preco] = match.group(1).replace('.', '')
            except: pass
            
            # 3. CONDOMÍNIO
            try:
                condo_text = card.find(string=re.compile(r'Condomínio', re.IGNORECASE))
                if condo_text:
                    match = re.search(r'R\$\s*(\d{1,3}(?:\.\d{3})*)', condo_text)
                    if match:
                        imovel_data['preco_condominio_rs'] = match.group(1).replace('.', '')
            except: pass

            # 4. ÁREA E QUARTOS
            try:
                features_elements = card.select("ul li") + card.select("span")
                features_text = " ".join([f.get_text(strip=True) for f in features_elements]).lower()

                match_area = re.search(r'(\d+)\s*m²', features_text)
                if match_area: imovel_data['area_m2'] = match_area.group(1)

                match_quartos = re.search(r'(\d+)\s*quarto', features_text)
                if match_quartos: imovel_data['quartos'] = match_quartos.group(1)
            except: pass

            # 5. LINKS E IMAGEM
            try:
                link = card.select_one("a[href*='/imovel/']")['href']
                imovel_data['url_anuncio'] = "https://www.vivareal.com.br" + link if link.startswith('/') else link
            except: pass
            
            try: 
                img = card.find('img')
                if img and 'src' in img.attrs:
                    imovel_data['url_imagem'] = img['src']
            except: pass

            # === FILTRO DE SEGURANÇA ===
            # Se a URL continuou como "N/A" (não foi encontrada), ignoramos este imóvel
            if imovel_data['url_anuncio'] == "N/A":
                continue # Pula para o próximo card sem adicionar este
            
            resultados.append(imovel_data)
            total_coletado += 1
            novos_nesta_pagina += 1
            
        print(f"Página {pagina}: {novos_nesta_pagina} coletados. Total: {total_coletado}")
        
        # Paginação
        if total_coletado < LIMITE_IMOVEIS:
            try:
                xpath_prox = "//a[@aria-label='próxima página'] | //a[contains(@class, 'pagination') and contains(., '>')]"
                btn_next = driver.find_elements(By.XPATH, xpath_prox)
                
                if btn_next and "disabled" not in btn_next[0].get_attribute("class"):
                    print("➡️ Indo para próxima página...")
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", btn_next[0])
                    pagina += 1
                    time.sleep(5)
                else:
                    print("Fim das páginas.")
                    break
            except:
                break
        else:
            break

    return resultados