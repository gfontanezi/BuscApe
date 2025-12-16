import pandas as pd
from geopy.geocoders import Nominatim
from thefuzz import process, fuzz
import unicodedata
import os

def get_data_path(filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, '..', 'data', filename)
    return os.path.abspath(data_path)

def encontrar_endereco_por_coordenadas(nome_da_estacao, arquivo_stops):
    
    try:
        caminho_arquivo = get_data_path(arquivo_stops)
        
        if not os.path.exists(caminho_arquivo):
            print(f"❌ Erro: Arquivo '{arquivo_stops}' não encontrado em: {caminho_arquivo}")
            return "", ""

        df_stops = pd.read_csv(caminho_arquivo)

        estacao = df_stops[df_stops['stop_name'].str.contains(nome_da_estacao, case=False, na=False)]

        if not estacao.empty:
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
                print(f"📍 Endereço base: {rua}, {bairro} - {cidade}")
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
    nome_arquivo = 'lista_estacoes_normalizadas.txt'
    caminho_arquivo = get_data_path(nome_arquivo)
    
    if not os.path.exists(caminho_arquivo):
        print(f"❌ Erro Crítico: '{nome_arquivo}' não encontrado na pasta 'data'.")
        return "Estação não encontrada."

    try:
        df_stops = pd.read_csv(caminho_arquivo, header=None)
        lista_estacoes = df_stops.iloc[:,0].tolist()
        
        melhor_correspondencia = process.extractOne(nome_digitado, lista_estacoes)
        if melhor_correspondencia:
            nome_encontrado, pontuacao = melhor_correspondencia
            if pontuacao >= 80:
                print(f"✅ Estação identificada: '{nome_encontrado}'")
                return nome_encontrado
            else:
                print(f"⚠️ Nenhuma correspondência exata. Usando: '{nome_encontrado}' (Pontuação: {pontuacao})")
                return nome_encontrado
    except Exception as e:
        print(f"Erro ao ler lista de estações: {e}")
        return "Estação não encontrada."


