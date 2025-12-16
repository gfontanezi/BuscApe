# 🏢 BuscApe - Automação de Busca Imobiliária

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Status](https://img.shields.io/badge/Status-Concluído-success)
![License](https://img.shields.io/badge/License-MIT-green)

> **BuscApe** é uma ferramenta inteligente de *Web Scraping* e automação que unifica a busca de imóveis em São Paulo, coletando dados do **QuintoAndar** e **VivaReal** simultaneamente. Seu diferencial é a busca baseada em proximidade de estações de metrô e trem, gerando visualizações interativas.

---

## 📸 Demonstração

| Galeria de Imóveis | Mapa de Localização |
|:------------------:|:-------------------:|
| *[Insira um print da sua Galeria HTML aqui]* | *[Insira um print do seu Mapa Folium aqui]* |
| *Visualização limpa dos anúncios* | *Plotagem geográfica dos imóveis* |

---

## 🚀 Funcionalidades

- **🕵️ Buscador Híbrido**: Realiza raspagem de dados (scraping) em múltiplos portais imobiliários simultaneamente.
- **🚇 Busca por Geolocalização**: 
    - Integração com dados de **transporte público**.
    - Converte nomes de estações de metrô em coordenadas geográficas reais.
    - Utiliza *Fuzzy Matching* para entender nomes de estações digitados incorretamente.
- **📊 Visualização de Dados**:
    - Gera uma **Galeria HTML** moderna para navegar pelos imóveis encontrados.
    - Cria um **Mapa Interativo (Folium)** mostrando a localização exata dos apartamentos.
    - Exporta dados brutos em **JSON** para análise posterior.
- **🧹 Tratamento de Dados**: Normalização de textos, limpeza de strings de preços e cálculo automático de preço por m².

---

## 🛠️ Tecnologias Utilizadas

O projeto foi desenvolvido utilizando as seguintes bibliotecas e ferramentas:

| Categoria | Tecnologias |
|-----------|-------------|
| **Linguagem** | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) |
| **Web Scraping** | `Selenium` `Undetected Chromedriver` `BeautifulSoup4` |
| **Dados & Análise** | `Pandas` `JSON` `TheFuzz` (Fuzzy Logic) |
| **Geolocalização** | `Geopy` (Nominatim API) `Folium` (Mapas) |
| **Automação** | `Webbrowser` `OS` |

---

## 📂 Estrutura do Projeto

```text
BuscApe/
│
├── main.py                     # Arquivo principal de execução
├── requirements.txt            # Dependências do projeto
│
├── src/                        # Código fonte modularizado
│   ├── __init__.py
│   ├── busca_quinto_andar.py   # Lógica de scraping do QuintoAndar
│   ├── busca_vivareal.py       # Lógica de scraping do VivaReal
│   ├── normalizar.py           # Funções de tratamento de texto e geocoding
│   └── visualizar_dados.py     # Geração de HTML, JSON e Mapas
│
├── data/                       # Bases de dados estáticas
│   ├── lat_lon_estacoes.csv    # Coordenadas das estações de SP
│   └── lista_estacoes.txt      # Lista para fuzzy matching
│
└── ApêsEncontrados/            # (Gerado automaticamente) Resultados da busca
    ├── galeria_imoveis.html
    ├── mapa_imoveis.html
    └── imoveis_venda.json