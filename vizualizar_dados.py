
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
    from geopy.geocoders import Nominatim
    mapa = folium.Map(location=[-23.5505, -46.6333], zoom_start=12) # Centro de SP
    geolocator = Nominatim(user_agent="meu_scraper_de_imoveis")

    for imovel in imoveis_encontrados:
        preco = (imovel.get('preco_venda_rs') or 
                    imovel.get('preco_aluguel_rs') or 
                    imovel.get('preco') or  # Adicionamos uma terceira verificação por segurança
                    'N/A') # Valor padrão se nenhuma chave for encontrada
        try:
            # Transforma o endereço em coordenadas
            location = geolocator.geocode(imovel['endereco'])
            if location:
                # Adiciona um marcador no mapa
                popup_html = f"<b>R$ {imovel[preco]}</b><br>{imovel['area_m2']} m²<br><a href='{imovel['url_anuncio']}' target='_blank'>Ver anúncio</a>"
                folium.Marker([location.latitude, location.longitude], popup=popup_html).add_to(mapa)
        except:
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