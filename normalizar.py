import pandas as pd
from geopy.geocoders import Nominatim
from thefuzz import process, fuzz
import unicodedata

""" def encontrar_endereco_por_coordenadas(nome_da_estacao, arquivo_stops):
    
    try:
        # Carrega o arquivo de paradas
        df_stops = pd.read_csv(arquivo_stops)

        # Busca pela estação (pode ser necessário ajustar a busca ao nome exato)
        # O campo 'stop_name' geralmente contém o nome da parada/estação
        estacao = df_stops[df_stops['stop_name'].str.contains(nome_da_estacao, case=False, na=False)]

        if not estacao.empty:
            # Pega a primeira correspondência
            lat = estacao.iloc[0]['stop_lat']
            lon = estacao.iloc[0]['stop_lon']

            # Utiliza o geopy para obter o endereço
            geolocator = Nominatim(user_agent="BuscApe") 
            location = geolocator.reverse((lat, lon), exactly_one=True)

            if location:
                address = location.raw['address']
                bairro = address.get('suburb', '') or address.get('quarter', '')
                cidade = address.get('city', '') or address.get('town', '')
                rua = address.get('road', '')
                numero = address.get('house_number', '')

                return f"{rua}, {numero} - {bairro}, {cidade}"
            else:
                return "Endereço não encontrado para as coordenadas."
        else:
            return "Estação não encontrada no arquivo GTFS."

    except Exception as e:
        return f"Ocorreu um erro: {e}"

# Exemplo de uso
# Certifique-se de que o arquivo 'stops.txt' está no mesmo diretório ou forneça o caminho completo
arquivo_gtfs_stops = 'stops.txt'
nome_estacao = 'bras' # Exemplo de estação

endereco = encontrar_endereco_por_coordenadas(nome_estacao, arquivo_gtfs_stops)
print(f"O endereço da estação {nome_estacao} é: {endereco}") """



def normalizar_texto(texto):
    if not isinstance(texto, str):
        return ""
    texto_normalizado = unicodedata.normalize('NFD', texto)
    return "".join(c for c in texto_normalizado if unicodedata.category(c) != 'Mn').lower()

def encontrar_estacao(nome_digitado):
    arquivo_estacoes = 'lista_estacoes_normalizadas.txt'
    df_stops = pd.read_csv(arquivo_estacoes)
    lista_estacoes = df_stops.iloc[:,0].tolist()
    melhor_correspondencia = process.extractOne(nome_digitado, lista_estacoes)
    if melhor_correspondencia:
            nome_encontrado, pontuacao = melhor_correspondencia
            if pontuacao >= 80:
                
                return print(f"Pesquisando por '{nome_encontrado}'...")
            else:
                return print(f"Nenhuma estação suficientemente parecida encontrada. Melhor palpite: '{nome_encontrado}' (Pontuação: {pontuacao}).")
    else:
        return "Estação não encontrada."


