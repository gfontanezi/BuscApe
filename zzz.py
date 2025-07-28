import googlemaps

def obter_endereco_google(nome_da_estacao, api_key):
    """
    Obtém o endereço de uma estação usando a Google Maps Places API.

    Argumentos:
        nome_da_estacao (str): O nome da estação.
        api_key (str): Sua chave da API do Google Maps.

    Retorna:
        str: O endereço da estação ou uma mensagem de erro.
    """
    gmaps = googlemaps.Client(key=api_key)
    try:
        # Busca por "text search"
        places_result = gmaps.places(query=f"estação {nome_da_estacao}")

        if places_result['status'] == 'OK' and places_result['results']:
            # Pega o primeiro resultado, que geralmente é o mais relevante
            primeiro_resultado = places_result['results'][0]
            return primeiro_resultado.get('formatted_address', 'Endereço não disponível.')
        else:
            return "Endereço não encontrado."
    except Exception as e:
        return f"Ocorreu um erro: {e}"

# Exemplo de uso
# Substitua 'SUA_CHAVE_DE_API' pela sua chave real
chave_api = "SUA_CHAVE_DE_API"
nome_estacao = input("Digite o nome da estação: ")
endereco = obter_endereco_google(nome_estacao, chave_api)
print(f"O endereço da estação '{nome_estacao}' é: {endereco}")