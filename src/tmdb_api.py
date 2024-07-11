# %%
import requests
import pandas as pd
from urllib.parse import quote

#%%
df_cert = pd.read_csv('https://raw.githubusercontent.com/bert-bruno/LH_CD_BRUNOBERTHOLDI/main/data/cert_null.csv').set_index('Unnamed: 0')
df_cert.head()

# %%
## movie_list = df_cert['Series_Title'].values.tolist()
## year_list = df_cert['Released_Year'].values.tolist()

# %%
def buscar_filme(titulo, ano):
    
    url = f'https://api.themoviedb.org/3/search/movie?query={quote(titulo)}&include_adult=true&language=en-US&primary_release_year={ano}&page=1'
    
    headers = {
              'accept': 'application/json',
              'Authorization': "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwMmMzZjJiNjU0ODk1ZDlkZTI3M2RkNzhjNmU2Yzk1MyIsIm5iZiI6MTcyMDUzNTY0OS43MTcxNjksInN1YiI6IjY2OGQ0OWMxNWM2YmRkMDgwODVjMDhlOSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.JDt-IhbPdxthB0yC_uBhtx_4wRJB0hAImSmu5k_RaaY"
              }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

#%%
def obter_id_filme(row):
    
    response = buscar_filme(row['Series_Title'], row['Released_Year'])

    if response and 'results' in response and len(response['results']) > 0:
        return response['results'][0]['id']
    else:
        return 000000

# Adicionar a coluna 'id' ao DataFrame
df_cert['id'] = df_cert.apply(obter_id_filme, axis=1)

# %%
df_cert['id'].value_counts()
df_cert[df_cert['id'] == 0]['Series_Title']

# %%
# Vamos coletar os dois valores faltantes manualmente: 'Arsenic and Old Lace' -> 212; 'This is England' -> 11798
df_cert.loc[df_cert['Series_Title'] == 'Arsenic and Old Lace', 'id'] = 212
df_cert.loc[df_cert['Series_Title'] == 'This is England', 'id'] = 11798

# %%
def busca_certificate(movie_id):
    url = f'https://api.themoviedb.org/3/movie/{quote(str(movie_id))}/release_dates'

    headers = {
              "accept": "application/json",
              "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwMmMzZjJiNjU0ODk1ZDlkZTI3M2RkNzhjNmU2Yzk1MyIsIm5iZiI6MTcyMDUzNTY0OS43MTcxNjksInN1YiI6IjY2OGQ0OWMxNWM2YmRkMDgwODVjMDhlOSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.JDt-IhbPdxthB0yC_uBhtx_4wRJB0hAImSmu5k_RaaY"
              }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def obter_certificado(row):
    
    if row['id'] == 'não encontrado':
        return 'não encontrado'
    
    response = busca_certificate(row['id'])
    if response and 'results' in response:
        for result in response['results']:
            if 'release_dates' in result and len(result['release_dates']) > 0:
                for release in result['release_dates']:
                    if 'certification' in release and release['certification']:
                        return release['certification']
    return 'não encontrado'

# %%
df_cert['certificate'] = df_cert.apply(obter_certificado, axis=1)

# %%
df_cert['certificate'].value_counts()
 
# %%
translation_dict = {'12': 12,
                     '16': 16,
                     'M': 12,
                     'PG': 7,
                     '6': 6,
                     'G': 0,
                     '14': 14,
                     '18': 18,
                     '18+': 18,
                     '15+': 15,
                     'U': 0,
                     'não encontrado': 0,
                     'MA15+': 15,
                     '15': 15,
                     '13': 13,
                     '+18': 18,
                     '12 anos': 12,
                     '12+': 12,
                     'e 14': 14,
                     '14A': 14,
                     'AA': 14,
                     '16 anos': 16,
                     'MA 15+': 15,
                     'R 18+': 18
                     }

# %%
df_cert['certificate'] = df_cert['certificate'].map(translation_dict)

# %%
# Exporta DataFrame com certificados já traduzidos para arquivo csv
df_cert.drop(columns='id', axis=1).to_csv('certificates.csv')

# %%
# Importa DataFrame com títulos de filmes que não possuem meta_score alocado
meta_null = pd.read_csv('https://raw.githubusercontent.com/bert-bruno/LH_CD_BRUNOBERTHOLDI/main/data/meta_null.csv')
meta_null.head()

# %%
# Define função de obtenção de meta_score
def obter_meta_score(row):
    
    response = buscar_filme(row['Series_Title'], row['Released_Year'])

    if response and 'results' in response and len(response['results']) > 0:
        return response['results'][0]['vote_average']
    else:
        return 000000
    
# %%
# Adiciona a coluna 'meta_score' ao DataFrame meta_null
meta_null['meta_score'] = meta_null.apply(obter_meta_score, axis=1)

# %%
# Multiplica meta_score por 10 para manter a consistência com o dataset original
meta_null['meta_score'] = meta_null['meta_score'].apply(lambda x: x*10)

# %%
# Exporta DataFrame com meta_scores já alocados para arquivo csv
meta_null.to_csv('meta_scores.csv')