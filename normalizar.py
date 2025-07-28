import pandas as pd
from geopy.geocoders import Nominatim
from thefuzz import process, fuzz
import unicodedata

def encontrar_endereco_por_coordenadas(nome_da_estacao, arquivo_stops):
    
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
            location = geolocator.reverse((lat, lon), exactly_one=True, language='pt-br')

            if location:
                address = location.raw['address']
                chaves_bairro = ['suburb', 'neighbourhood', 'quarter', 'city_district', 'district']
                bairro = ''
                for chave in chaves_bairro:
                    if chave in address:
                        bairro = address[chave]
                        break
                cidade = address.get('city', '') or address.get('town', '')
                rua = address.get('road', '')
                numero = address.get('house_number', '')
                print(address)
                print(f"{rua}, {numero} - {bairro}, {cidade}")
                return bairro, cidade
            else:
                print("Endereço não encontrado para as coordenadas.")
                return
        else:
            print("Estação não encontrada no arquivo GTFS.")
            return

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return 



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
                print(f"Pesquisando por '{nome_encontrado}'...")
                return nome_encontrado
            else:
                print(f"Nenhuma estação suficientemente parecida encontrada. Melhor palpite: '{nome_encontrado}' (Pontuação: {pontuacao}).")
                return nome_encontrado
    else:
        return "Estação não encontrada."


