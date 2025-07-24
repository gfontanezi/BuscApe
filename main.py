from busca_quintoAndar import buscar_imoveis_quinto_andar
import folium 
from geopy.geocoders import Nominatim

tipo_venda = str(input("Alugar ou Comprar? ")).strip().lower()

bairro = str(input("Bairro: ")).strip().lower().replace(' ', '-')
bairro = f"{bairro}-" if bairro else ""

cidade = str(input("Cidade: ")).strip().lower().replace(' ', '-')

estado = str(input("Estado (sigla): ")).strip().lower()


tipo_imovel = str(input("Casa, Apartamento ou Ambos? ")).strip().lower()
if tipo_imovel == "ambos":
    tipo_imovel = ""
elif tipo_imovel in "casa apartamento":
    tipo_imovel = f"{tipo_imovel}/"


quartos = str(input("Quantos quartos: ")).strip().lower()
quartos = f"{quartos}-quartos/" if quartos else ""

if tipo_venda == "alugar":
    preco_min = input("Preço mínimo do aluguel (mínimo de R$500,00): R$")
    if preco_min == "" or not preco_min.isdigit():
        preco_min = 500
    else:
        preco_min = int(preco_min)
        if preco_min < 500:
            print("O preço mínimo do aluguel deve ser pelo menos R$500,00.")
            preco_min = 500
    while True:
        preco_max = input("Preço máximo do aluguel: R$")
        if preco_max.isdigit():
            preco_max = int(preco_max)
            if preco_max >= preco_min:
                break
            else:
                print(f"O preço máximo deve ser maior ou igual a R${preco_min},00.")
        else:
            print("Por favor, insira um valor numérico válido para o preço máximo do aluguel.")


elif tipo_venda == "comprar":
    preco_min = input("Preço mínimo da compra (mínimo de R$150.000,00): R$")
    if preco_min == "" or not preco_min.isdigit():
        preco_min = 150000
    else:
        preco_min = int(preco_min)
        if preco_min < 150000:
            print("O preço mínimo do imóvel deve ser pelo menos R$150.000,00.")
            preco_min = 150000
    while True:
        preco_max = input("Preço máximo do imóvel: R$")
        if preco_max.isdigit():
            preco_max = int(preco_max)
            if preco_max >= preco_min:
                break
            else:
                print(f"O preço máximo deve ser maior ou igual a R${preco_min},00.")
        else:
            print("Por favor, insira um valor numérico válido para o preço máximo do imóvel.")


def url_quintoAndar(tipo_venda, tipo_imovel, cidade, estado, bairro, quartos, preco_min, preco_max):
    if tipo_venda == "alugar":
        url = f'https://www.quintoandar.com.br/alugar/imovel/{bairro}{cidade}-{estado}-brasil/{tipo_imovel}{quartos}proximo-ao-metro/de-{preco_min}-a-{preco_max}-reais'
    elif tipo_venda == "comprar":
        url = f'https://www.quintoandar.com.br/comprar/imovel/{bairro}{cidade}-{estado}-brasil/{tipo_imovel}{quartos}proximo-ao-metro/de-{preco_min}-a-{preco_max}-venda'
    return url

url = url_quintoAndar(tipo_venda, tipo_imovel, cidade, estado, bairro, quartos, preco_min, preco_max)
imoveis_encontrados_quintoAndar = buscar_imoveis_quinto_andar(url, criterio_de_ordenacao="Mais próximos")

if imoveis_encontrados_quintoAndar:
    print(f"\n--- DADOS EXTRAÍDOS DE {len(imoveis_encontrados_quintoAndar)} IMÓVEIS ---\n")
        
        # Exemplo de como salvar em um arquivo JSON para ver o resultado
    import json
    with open(f"imoveis_{tipo_venda}.json", 'w', encoding='utf-8') as f:
        json.dump(imoveis_encontrados_quintoAndar, f, indent=4, ensure_ascii=False)
    print(f"Resultados salvos em 'imoveis_{tipo_venda}.json'")
        
else:
    print("\nNenhum imóvel foi extraído.")

mapa = folium.Map(location=[-23.5505, -46.6333], zoom_start=12) # Centro de SP
geolocator = Nominatim(user_agent="meu_scraper_de_imoveis")

for imovel in imoveis_encontrados_quintoAndar:
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
        continue # Ignora erros de geocodificação

mapa.save("mapa_imoveis.html")




def salvar_em_html(lista_de_imoveis, nome_do_arquivo="galeria_imoveis.html"):
    if not lista_de_imoveis:
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

    for imovel in lista_de_imoveis:
        # ***** A LÓGICA INTELIGENTE ESTÁ AQUI *****
        # Usamos .get() para procurar as chaves. Ele retorna o valor se a chave existe,
        # ou None se não existe. O 'or' continua para a próxima tentativa.
        # Isso torna a função à prova de falhas e flexível.
        preco = (imovel.get('preco_venda_rs') or 
                 imovel.get('preco_aluguel_rs') or 
                 imovel.get('preco') or  # Adicionamos uma terceira verificação por segurança
                 'N/A') # Valor padrão se nenhuma chave for encontrada

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

    with open(nome_do_arquivo, 'w', encoding='utf-8') as arquivo_html:
        arquivo_html.write(html)
    
    print(f"Dados salvos com sucesso no arquivo '{nome_do_arquivo}'! Abra-o no seu navegador.")

salvar_em_html(imoveis_encontrados_quintoAndar, nome_do_arquivo="galeria_imoveis_quintoAndar.html")