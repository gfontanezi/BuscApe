
def gerar_json(imoveis_encontrados, tipo_venda):
    if not imoveis_encontrados:
        print("A lista de imóveis está vazia. Nenhum arquivo foi criado.")
        return
    print(f"\n--- DADOS EXTRAÍDOS DE {len(imoveis_encontrados)} IMÓVEIS ---\n")
        
        # Exemplo de como salvar em um arquivo JSON para ver o resultado
    import json
    with open(f"ApêsEncontrados\imoveis_{tipo_venda}.json", 'w', encoding='utf-8') as f:
        json.dump(imoveis_encontrados, f, indent=4, ensure_ascii=False)
    print(f"Resultados salvos em 'imoveis_{tipo_venda}.json'")


def gerar_mapa(imoveis_encontrados):
    if not imoveis_encontrados:
        print("A lista de imóveis está vazia. Nenhum arquivo foi criado.")
        return
    import folium
    import time
    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent="meu_scraper_de_imoveis_v4")
    mapa = folium.Map(location=[-23.5505, -46.6333], zoom_start=12)

    print(f"\nIniciando a geração do mapa para {len(imoveis_encontrados)} imóveis...")
    
    imoveis_plotados = 0
    for imovel in imoveis_encontrados:
        try:
            # --- LÓGICA FINAL DE LIMPEZA: EXTRAIR APENAS A RUA ---
            endereco_bruto = imovel.get('endereco', 'N/A')
            rua = ""
            
            # rsplit(',', 1) divide a string a partir da DIREITA na primeira vírgula que encontrar.
            # Isso isola a rua de forma eficaz.
            if ',' in endereco_bruto:
                partes = endereco_bruto.rsplit(',', 1)
                if len(partes) > 1:
                    rua = partes[1].strip() # Pega o que veio depois da última vírgula
            else:
                rua = endereco_bruto # Se não houver vírgula, usa o texto todo

            # Se a extração da rua falhar, pulamos este imóvel.
            if not rua:
                print(f"Não foi possível extrair um nome de rua válido de: '{endereco_bruto}'")
                continue

            # Criamos a busca mais limpa possível: "Nome da Rua, Cidade, País"
            endereco_a_buscar = f"{rua}, São Paulo, Brasil"
            
            time.sleep(1)

            print(f"Geocodificando: '{endereco_a_buscar}'...")
            location = geolocator.geocode(endereco_a_buscar, timeout=10)

            if location:
                imoveis_plotados += 1
                print(f"-> SUCESSO! Localização encontrada.")

                preco = (imovel.get('preco_venda_rs') or 
                         imovel.get('preco_aluguel_rs') or 
                         imovel.get('preco') or 'N/A')

                popup_html = (f"<b>R$ {preco}</b><br>"
                              f"<b>{imovel.get('area_m2', 'N/A')} m²</b><br>"
                              f"<a href='{imovel.get('url_anuncio', '#')}' target='_blank'>Ver anúncio</a>")

                folium.Marker(
                    [location.latitude, location.longitude], 
                    popup=popup_html
                ).add_to(mapa)
            else:
                print("-> Endereço não encontrado pelo geolocator.")

        except Exception as e:
            print(f"!!! Ocorreu um erro ao processar o imóvel: {e}")
            continue

    mapa.save("ApêsEncontrados\mapa_imoveis.html")


def gerar_pagina_html(imoveis_encontrados):
    if not imoveis_encontrados:
        print("A lista de imóveis está vazia. Nenhum arquivo foi criado.")
        return

    html = """
    <html>
    <head>
        <title>Galeria de Imóveis - QuintoAndar</title>
        <style>
            body { font-family: sans-serif; background-color: #f4f4f4; margin: 0; }
            h1 { text-align: center; color: #333; padding: 20px; }
            .container { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 25px; padding: 25px; }
            .card { border: 1px solid #ddd; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 8px rgba(0,0,0,0.1); background-color: white; transition: transform 0.2s, box-shadow 0.2s; }
            .card:hover { transform: translateY(-5px); box-shadow: 0 8px 16px rgba(0,0,0,0.2); }
            .card img { width: 100%; height: 220px; object-fit: cover; }
            .card-info { padding: 15px; }
            .card-info h3 { margin: 0 0 10px 0; color: #005c99; font-size: 1.4em; }
            .card-info p { margin: 5px 0; color: #555; font-size: 0.95em; }
            a { text-decoration: none; color: inherit; }
        </style>
    </head>
    <body>
        <h1>Galeria de Imóveis Encontrados</h1>
        <div class="container">
    """

    for imovel in imoveis_encontrados:
        preco = (imovel.get('preco_venda_rs') or 
                 imovel.get('preco_aluguel_rs') or 
                 imovel.get('preco') or 
                 'N/A') 

        html += f"""
            <a href="{imovel['url_anuncio']}" target="_blank">
                <div class="card">
                    <img src="{imovel['url_imagem']}" alt="Foto do imóvel">
                    <div class="card-info">
                        <h3>R$ {preco}</h3>
                        <p>{imovel['endereco']}</p>
                        <p>{imovel['area_m2']} m²</p>
                    </div>
                </div>
            </a>
        """

    html += """
        </div>
    </body>
    </html>
    """

    with open("ApêsEncontrados\galeria_imoveis.html", 'w', encoding='utf-8') as arquivo_html:
        arquivo_html.write(html)
    
    print(f"Dados salvos com sucesso no arquivo 'galeria_imoveis.html'! Abra-o no seu navegador.")

def gerar_ghtml(imoveis_encontrados, tipo_venda):
    if not imoveis_encontrados:
        print("A lista de imóveis está vazia. Nenhum arquivo de galeria foi criado.")
        return

    # Pega a chave do preço correta
    chave_preco = 'preco_aluguel_rs' if tipo_venda == 'alugar' else 'preco_venda_rs'

    # Começamos a criar o conteúdo HTML
    html_content = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Imóveis Encontrados</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; }
            h1 { text-align: center; color: #333; }
            .gallery-container { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
            .card { background-color: white; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); overflow: hidden; transition: transform 0.2s; }
            .card:hover { transform: translateY(-5px); }
            .card img { width: 100%; height: 200px; object-fit: cover; }
            .card-info { padding: 15px; }
            .card-info h3 { margin: 0; font-size: 1.1em; color: #1a1a1a; }
            .card-info p { margin: 5px 0; color: #555; }
            .card-info .price { font-size: 1.2em; font-weight: bold; color: #007A7C; }
            .card-info a { display: block; background-color: #007A7C; color: white; text-align: center; padding: 10px; border-radius: 5px; text-decoration: none; margin-top: 10px; }
            .card-info a:hover { background-color: #005f5f; }
        </style>
    </head>
    <body>
        <h1>Imóveis Encontrados</h1>
        <div class="gallery-container">
    """

    # Loop para criar um card para cada imóvel
    for imovel in imoveis_encontrados:
        preco = imovel.get(chave_preco, 'N/A')
        
        # Formata o preço com pontos
        try:
            preco_formatado = f"{int(preco):,}".replace(",", ".")
        except (ValueError, TypeError):
            preco_formatado = preco

        card_html = f"""
            <div class="card">
                <img src="{imovel.get('url_imagem', 'https://via.placeholder.com/300x200?text=Sem+Imagem')}" alt="Foto do imóvel">
                <div class="card-info">
                    <h3>{imovel.get('endereco', 'Endereço não disponível')}</h3>
                    <p class="price">R$ {preco_formatado}</p>
                    <p>{imovel.get('area_m2', 'N/A')} m²</p>
                    <a href="{imovel.get('url_anuncio', '#')}" target="_blank">Ver Anúncio</a>
                </div>
            </div>
        """
        html_content += card_html

    html_content += """
        </div>
    </body>
    </html>
    """

    # Salva o arquivo HTML
    with open("ApêsEncontrados\imveis.html", 'w', encoding='utf-8') as arquivo_html:
        arquivo_html.write(html_content)