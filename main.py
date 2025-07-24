from busca_quintoAndar import buscar_imoveis_quinto_andar
from vizualizar_dados import gerar_json, gerar_mapa, gerar_pagina_html


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

gerar_json(imoveis_encontrados_quintoAndar, tipo_venda)
gerar_mapa(imoveis_encontrados_quintoAndar)
gerar_pagina_html(imoveis_encontrados_quintoAndar, nome_do_arquivo="galeria_imoveis_quintoAndar.html")