
#  =============================
#  Limpeza do DF e importação de bibliotecas
#  =============================
# Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from PIL import Image
import folium as fl
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Entregadores', page_icon='', layout='wide')

# Importar arquivo csv
df = pd.read_csv( 'FTC_Aula34.1.csv' )


##  =============================
##  Funções
##  =============================

### função Limpeza de dados
def clean_code( df1 ):
    """ Esta função tem a responsabilidade de limpar o dataframe
     Tipos de limpeza:
     1. Remoção dos dados NaN
     2. mudança do tipo da coluna de dados
     3. Remoção dos espaços das variáveis de texto
     4. Formatação da coluna de datas
     5. Limpeza da coluna de tempo (remoção do texto da variável numérica)
     Input: dataframe
     Output: dataframe
    """

    ## Convertendo a coluna 'Order_Date' para datetime
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%Y-%m-%d' )
    # # Excluindo coluna Unnamed: 0
    df1 = df1.drop(['Unnamed: 0'], axis=1).reset_index()
    # Remover NaN da coluna Festival
    nan_festival = (df1['Festival'] != 'NaN ' )
    df1 = df1.loc[nan_festival, :].copy()
    # Remover espaços da coluna Festival
    df1.loc[: ,'Festival'] = df1.loc[ : ,'Festival'].str.strip()
    # Criando a coluna 'week_of_year
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U' )
    # Convertendo coluna 'week_of_year'
    df1['week_of_year'] = df1['week_of_year'].astype(int)
    # Limpando a coluna 'Time_taken(min)'
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1] )
    # convertendo a coluna 'Time_taken(min)' para número
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )
    return df1


# # Copiando dataframe
df1 = clean_code(df)


def top_delivers( df1, top_asc):
    df2 = (df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
           .groupby(['City', 'Delivery_person_ID'])
           .max().sort_values(['City', 'Delivery_person_ID'], ascending=top_asc).reset_index())
    #  Filtros
    df_aux1 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux2 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux3 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
    df3 = pd.concat([df_aux1, df_aux2, df_aux3]).reset_index(drop=True)
    # st.dataframe( df3 )
    return df3



#  =============================
#  Barra Lateral
#  =============================

st.header('Marketplace - Visão Entregadores')

# image_path = 'C:/users/Dell/Desktop/260623/Comunidade_DS/FTC_Python/curry_delivery.jpg'
image = Image.open( 'curry_delivery.jpg' )
st.sidebar.image( image, width=120 )

st.sidebar.markdown( '# Cury Company')
st.sidebar.markdown( '## Fastest Delivery in Town' )
# Cria linha horizontal para separar
st.sidebar.markdown( """___""")


from datetime import datetime
st.sidebar.markdown( '## Selecione uma data limite' )
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime(2022, 4, 13 ),
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 6),
    format='DD-MM-YYYY')

# st.header( date_slider )
st.sidebar.markdown( """___""")


traffic_options = st.sidebar.multiselect(
    'Quaisas condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'] )

st.sidebar.markdown( """___""")
st.sidebar.markdown( '### Powered by Comunidade DS')

# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]


#  =============================
#  Layout visao_entregadores
#  =============================
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '_', '_'] )

with ((tab1)):
    with st.container():
        st.title( 'Overhall Metrics' )

        col1, col2, col3, col4 = st.columns( 4, gap='large')
        with col1:
            # st.subheader( 'Maior Idade' )
            columns = df1.loc[:, 'Delivery_person_Age']
            aux_maximo = columns.max()
            col1.metric( 'Maior idade', aux_maximo )

        with col2:
            # st.subheader( 'Menor Idade' )
            aux_minimo = columns.min()
            # print(f'A menor idade é {aux_minimo}')
            col2.metric( 'Menor idade', aux_minimo)

        with col3:
            # st.subheader( 'Condição de Veículos' )
            melhor_veiculo = df1.loc[:, 'Vehicle_condition'].max()
            # print(f'A pior condição é {pior_veiculo} e, a melhor condição é {melhor_veiculo}')
            col3.metric('Melhor Veículo', melhor_veiculo)

        with col4:
            # st.subheader( 'Condição de Veículos' )
            pior_veiculo = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior Veículo', pior_veiculo)

    with st.container():
        st.markdown( """___""")
        st.title( 'Avaliações' )

        col1, col2 = st.columns ( 2 )
        with col1:
            st.markdown( '##### Avaliação media por Entregador')
            avaliacao = (df1.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']].
                         groupby('Delivery_person_ID').
                         mean().reset_index() )
            st.dataframe( avaliacao )

        with col2:
            st.markdown( '##### Avaliação media por transito' )
            df_result = (df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                         .groupby('Road_traffic_density').agg({'Delivery_person_Ratings': ['mean', 'std']}))
            # Mudança de nome das colunas
            df_result.columns = ['delivery_mean', 'delivery_std']
            # reset do index
            df_result = df_result.reset_index()
            st.dataframe(df_result)

            st.markdown( '##### Avaliação media por clima' )
            result5 = ( df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                       .groupby('Weatherconditions')
                       .agg({'Delivery_person_Ratings': ['mean', 'std']}) )
            # Criando novas colunas / resetando index
            result5.columns = ['delivery_mean', 'delivery_std']
            result5.reset_index()
            st.dataframe(result5)


    with st.container():
        st.markdown( """___""")
        st.title( 'Velocidade de Entrega' )
        col1, col2 = st.columns( 2 )

        with col1:
            st.markdown( '##### Top entregadores mais rápidos' )
            df3 = top_delivers(df1, top_asc=True)
            st.dataframe(df3)


        with col2:
            st.markdown( '##### Top entregadores mais lentos' )
            df3 = top_delivers(df1, top_asc=False)
            st.dataframe( df3 )
