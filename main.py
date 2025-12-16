from src.busca_quinto_andar import buscar_imoveis_quinto_andar
from src.busca_vivareal import buscar_imoveis_vivareal
from src.visualizar_dados import gerar_json, gerar_galeria_html
from src.normalizar import encontrar_estacao, normalizar_texto, encontrar_endereco_por_coordenadas
import webbrowser
import os

os.system('cls' if os.name == 'nt' else 'clear')

print("=== 🏢 BUSCAPE - Buscador Profissional ===")

while True:
    tipo_venda = str(input("Alugar ou Comprar? ")).strip().lower()
    if tipo_venda in ["alugar", "comprar"]:
        break

while True:
    pesquisa = int(input("Pesquisar por \n[1] endereço\n[2] estação de metrô \nOpção: "))
    if pesquisa in [1, 2]:
        break

bairro = ""
cidade = ""
rua = ""
if pesquisa == 1:
    rua = str(input("Rua: ")).strip().lower().replace(' ', '-')
    bairro = str(input("Bairro: ")).strip().lower().replace(' ', '-')
    bairro = f"{bairro}-" if bairro else ""
    cidade = str(input("Cidade: ")).strip().lower().replace(' ', '-')

elif pesquisa == 2:
    estacao = str(input("Estação de metrô: ")).strip().lower().replace(' ', '-')
    estacao = normalizar_texto(estacao)
    estacao_encontrada = encontrar_estacao(estacao)
    bairro, cidade = encontrar_endereco_por_coordenadas(estacao_encontrada, 'lat_lon_estacoes.csv')
    

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



if tipo_venda == "alugar":
    url_quintoAndar = f'https://www.quintoandar.com.br/alugar/imovel/{bairro}{cidade}-sp-brasil/{tipo_imovel}{quartos}proximo-ao-metro/de-{preco_min}-a-{preco_max}-reais'
elif tipo_venda == "comprar":
    url_quintoAndar = f'https://www.quintoandar.com.br/comprar/imovel/{bairro}{cidade}-sp-brasil/{tipo_imovel}{quartos}proximo-ao-metro/de-{preco_min}-a-{preco_max}-venda'

imoveis_encontrados_quintoAndar = buscar_imoveis_quinto_andar(url_quintoAndar, pesquisa, estacao_encontrada, criterio_de_ordenacao="Menor valor")


if tipo_venda == "alugar":
    url_vivaReal = f'https://www.vivareal.com.br/aluguel/sp/'
if tipo_venda == "comprar":
    url_vivaReal = f'https://www.vivareal.com.br/venda/sp/'

imoveis_encontrados_vivaReal = buscar_imoveis_vivareal(url_vivaReal, cidade, bairro, rua, tipo_imovel, quartos, preco_min, preco_max, perto_metro=True)

todos_imoveis = imoveis_encontrados_quintoAndar + imoveis_encontrados_vivaReal
if todos_imoveis:
    gerar_json(todos_imoveis, tipo_venda)
    gerar_galeria_html(todos_imoveis, tipo_venda)

    # Abre usando a pasta output
    caminho_arquivo = os.path.join(os.getcwd(), "output", "galeria_imoveis.html")
    if os.path.exists(caminho_arquivo):
        print(f"\n🌐 Abrindo galeria...")
        webbrowser.open("file://" + caminho_arquivo)
    else:
        print(f"Arquivo não encontrado: {caminho_arquivo}")
else:
    print("\n❌ Nenhum imóvel encontrado.")