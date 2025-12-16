import os
import json
import folium
from geopy.geocoders import Nominatim

def garantir_diretorio(caminho):
    pasta = os.path.dirname(caminho)
    if pasta and not os.path.exists(pasta):
        os.makedirs(pasta)

def gerar_json(imoveis_encontrados, tipo_venda):
    if not imoveis_encontrados:
        print("A lista de imóveis está vazia. Nenhum arquivo foi criado.")
        return
    print(f"\n--- DADOS EXTRAÍDOS DE {len(imoveis_encontrados)} IMÓVEIS ---\n")

    nome_arquivo = f"imoveis_{tipo_venda}.json"
    caminho_arquivo = os.path.join("ApêsEncontrados", nome_arquivo)
    
    garantir_diretorio(caminho_arquivo)

    with open(caminho_arquivo, 'w', encoding='utf-8') as f:
        json.dump(imoveis_encontrados, f, indent=4, ensure_ascii=False)
    print(f"Resultados salvos em '{caminho_arquivo}'")


def gerar_mapa(imoveis_encontrados):
    if not imoveis_encontrados:
        print("A lista de imóveis está vazia. Nenhum arquivo foi criado.")
        return
    
    geolocator = Nominatim(user_agent="meu_scraper_de_imoveis_v4")
    mapa = folium.Map(location=[-23.5505, -46.6333], zoom_start=12)

    print(f"\nIniciando a geração do mapa para {len(imoveis_encontrados)} imóveis...")
    
    imoveis_plotados = 0
    for imovel in imoveis_encontrados:
        try:
            endereco_bruto = imovel.get('endereco', 'N/A')
            rua = ""
            
            if ',' in endereco_bruto:
                partes = endereco_bruto.rsplit(',', 1)
                if len(partes) > 1:
                    rua = partes[1].strip()
            else:
                rua = endereco_bruto

            if not rua:
                continue

            endereco_a_buscar = f"{rua}, São Paulo, Brasil"
            location = geolocator.geocode(endereco_a_buscar, timeout=10)

            if location:
                imoveis_plotados += 1
                
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

        except Exception as e:
            print(f"!!! Erro ao processar imóvel: {e}")
            continue

    caminho_mapa = os.path.join("ApêsEncontrados", "mapa_imoveis.html")
    garantir_diretorio(caminho_mapa)
    
    mapa.save(caminho_mapa)
    print(f"Mapa salvo em: {caminho_mapa}")




def gerar_galeria_html(imoveis_encontrados, tipo_venda):
    if not imoveis_encontrados:
        print("A lista de imóveis está vazia. Nenhum arquivo de galeria foi criado.")
        return

    chave_preco = 'preco_aluguel_rs' if tipo_venda == 'alugar' else 'preco_venda_rs'

    
    html_template = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Imóveis Encontrados</title>
    <style>
        :root {{
            --primary-color: #007A7C;
            --background-color: #f0f2f5;
            --card-background: #ffffff;
            --text-color: #333;
            --light-text-color: #666;
            --border-color: #e0e0e0;
        }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
            background-color: var(--background-color); 
            margin: 0; 
            padding: 0; 
        }}
        .header {{
            background-color: var(--card-background);
            padding: 20px 40px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            position: sticky; top: 0; z-index: 1000;
        }}
        .header h1 {{ text-align: center; color: var(--text-color); margin: 0 0 20px 0; }}
        .controls {{ display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 15px; }}
        #search-input {{ flex-grow: 1; padding: 12px 15px; border: 1px solid var(--border-color); border-radius: 8px; font-size: 16px; min-width: 250px; }}
        .sort-buttons {{ display: flex; flex-wrap: wrap; gap: 10px; }}
        .sort-buttons button {{ padding: 10px 15px; border: 1px solid var(--border-color); background-color: transparent; border-radius: 8px; cursor: pointer; font-size: 14px; transition: background-color 0.2s, color 0.2s; }}
        .sort-buttons button.active {{ background-color: var(--primary-color); color: white; border-color: var(--primary-color); }}
        .main-container {{ max-width: 1600px; margin: 20px auto; padding: 0 20px; }}
        #results-counter {{ text-align: center; color: var(--light-text-color); margin-bottom: 20px; }}
        .gallery-container {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 25px; }}
        .card {{ background-color: var(--card-background); border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); overflow: hidden; transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out; display: flex; flex-direction: column; }}
        .card:hover {{ transform: translateY(-8px); box-shadow: 0 8px 20px rgba(0,0,0,0.12); }}
        .card img {{ width: 100%; height: 220px; object-fit: cover; background-color: #eee; }}
        .card-info {{ padding: 20px; display: flex; flex-direction: column; flex-grow: 1; }}
        .card-info .address {{ margin: 0 0 5px 0; font-size: 1em; color: var(--text-color); font-weight: 500; }}
        .card-info .price {{ font-size: 1.5em; font-weight: bold; color: var(--primary-color); margin: 5px 0; }}
        .condo-price {{ font-size: 0.9em; color: var(--light-text-color); margin: -5px 0 15px 2px; }}
        .features {{ display: flex; justify-content: space-around; align-items: center; color: var(--light-text-color); margin: 10px 0 5px 0; padding: 10px 0; border-top: 1px solid var(--border-color); border-bottom: 1px solid var(--border-color); }}
        .features span {{ display: flex; align-items: center; gap: 6px; font-size: 0.95em; }}
        .area-price {{ text-align: center; color: #333; font-size: 0.9em; margin: 10px 0 15px 0; }}
        .card-info .link-button {{ display: block; background-color: var(--primary-color); color: white; text-align: center; padding: 12px; border-radius: 8px; text-decoration: none; margin-top: auto; transition: background-color 0.2s; }}
        .card-info .link-button:hover {{ background-color: #005f5f; }}
        #not-found-message {{ display: none; width: 100%; text-align: center; padding: 50px; font-size: 1.2em; color: var(--light-text-color); }}
    </style>
</head>
<body>
    <header class="header">
        <h1>Imóveis Encontrados</h1>
        <div class="controls">
            <input type="text" id="search-input" placeholder="Buscar por endereço...">
            <div class="sort-buttons">
                <button data-sort="price" data-order="desc">Preço Maior</button>
                <button data-sort="price" data-order="asc">Preço Menor</button>
                <button data-sort="area" data-order="desc">Área Maior</button>
                <button data-sort="area" data-order="asc">Área Menor</button>
            </div>
        </div>
    </header>
    <main class="main-container">
        <div id="results-counter"></div>
        <div class="gallery-container">{cards_html}</div>
        <div id="not-found-message">Nenhum imóvel encontrado com os critérios de busca.</div>
    </main>
    <script>
        {js_script}
    </script>
</body>
</html>
    """

    cards_list = []
    for imovel in imoveis_encontrados:
        # Pega todos os dados com valores padrão seguros
        preco_str = imovel.get(chave_preco, '0')
        area_str = imovel.get('area_m2', '0')
        quartos_str = imovel.get('quartos', '0')
        condominio_str = imovel.get('preco_condominio_rs', '0')

        # Cálculo do preço por m²
        preco_m2_formatado = "N/A"
        preco_m2_num = 0
        try:
            preco_num = float(preco_str)
            area_num = float(area_str)
            if area_num > 0:
                preco_m2_num = round(preco_num / area_num)
                preco_m2_formatado = f"{preco_m2_num:,}".replace(",", ".")
        except (ValueError, TypeError): pass

        preco_formatado = f"{int(preco_str):,}".replace(",", ".") if preco_str.isdigit() else preco_str
        
        condominio_html = ''
        if condominio_str == 'Não informado':
            condominio_html = '<p class="condo-price">Condomínio não informado</p>'
            condominio_str = '0'
        elif condominio_str and int(condominio_str) > 0:
            condominio_formatado = f"{int(condominio_str):,}".replace(",", ".")
            condominio_html = f'<p class="condo-price">+ R$ {condominio_formatado} Condomínio</p>'

        # Montagem do card final
        card_html = f"""
        <div class="card" data-price="{preco_str}" data-area="{area_str}" data-preco-m2="{preco_m2_num}">
            <img src="{imovel.get('url_imagem', '')}" alt="Foto do imóvel" loading="lazy">
            <div class="card-info">
                <h3 class="address">{imovel.get('endereco', 'Endereço não disponível')}</h3>
                <p class="price">R$ {preco_formatado}</p>
                {condominio_html}
                
                <!-- SEÇÃO 'FEATURES' CORRIGIDA PARA INCLUIR QUARTOS -->
                <div class="features">
                    <span><strong>{area_str}</strong> m²</span>
                    <span>
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="18px" height="18px"><path d="M20 9.55V3.5c0-.83-.67-1.5-1.5-1.5H5.5C4.67 2 4 2.67 4 3.5v6.05c-1.69.88-2.85 2.63-3 4.7V19.5c0 .83.67 1.5 1.5 1.5H5v-2h14v2h2.5c.83 0 1.5-.67 1.5-1.5v-5.25c-.15-2.07-1.31-3.82-3-4.7zM18 8H6V4h12v4z"/></svg>
                        {quartos_str} quarto(s)
                    </span>
                    <!-- Removi as outras informações, como solicitado -->
                </div>
                
                <p class="area-price"><b>R$ {preco_m2_formatado} / m²</b></p>
                <a class="link-button" href="{imovel.get('url_anuncio', '#')}" target="_blank">Ver Anúncio no QuintoAndar</a>
            </div>
        </div>
        """
        cards_list.append(card_html)
    
    js_script = """
        document.addEventListener('DOMContentLoaded', () => {
            const searchInput = document.getElementById('search-input');
            const gallery = document.querySelector('.gallery-container');
            const allCards = Array.from(gallery.querySelectorAll('.card'));
            const sortButtons = document.querySelectorAll('.sort-buttons button');
            const counter = document.getElementById('results-counter');
            const notFoundMessage = document.getElementById('not-found-message');
            const totalCards = allCards.length;

            function updateCounter(visibleCount) {
                counter.textContent = `Exibindo ${visibleCount} de ${totalCards} imóveis`;
            }

            function filterAndSort() {
                const searchTerm = searchInput.value.toLowerCase();
                let visibleCards = 0;

                allCards.forEach(card => {
                    const address = card.querySelector('.address').textContent.toLowerCase();
                    const matches = address.includes(searchTerm);
                    card.style.display = matches ? 'flex' : 'none';
                    if(matches) visibleCards++;
                });

                if (visibleCards === 0) {
                    notFoundMessage.style.display = 'block';
                } else {
                    notFoundMessage.style.display = 'none';
                }
                updateCounter(visibleCards);
            }

            function sortCards(sortBy, sortOrder) {
                const sortedCards = allCards.sort((a, b) => {
                    const valA = parseFloat(a.dataset[sortBy]);
                    const valB = parseFloat(b.dataset[sortBy]);
                    if (isNaN(valA) || isNaN(valB)) return 0;
                    return sortOrder === 'asc' ? valA - valB : valB - valA;
                });

                gallery.innerHTML = '';
                sortedCards.forEach(card => gallery.appendChild(card));
                filterAndSort();
            }
            
            searchInput.addEventListener('input', filterAndSort);

            sortButtons.forEach(button => {
                button.addEventListener('click', () => {
                    sortButtons.forEach(btn => btn.classList.remove('active'));
                    button.classList.add('active');
                    const sortBy = button.dataset.sort;
                    const sortOrder = button.dataset.order;
                    sortCards(sortBy, sortOrder);
                });
            });
            
            updateCounter(totalCards);
        });
    """

    final_html = html_template.format(cards_html="".join(cards_list), js_script=js_script)

    caminho_galeria = os.path.join("ApêsEncontrados", "galeria_imoveis.html")
    garantir_diretorio(caminho_galeria)
    with open(caminho_galeria, 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    print(f"\nGaleria de imóveis salva em: {caminho_galeria}")