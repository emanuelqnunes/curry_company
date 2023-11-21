
#  =============================
#  Limpeza do DF e importação de bibliotecas
#  =============================
# Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image
import folium as fl
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Restaurante', page_icon='', layout='wide')

## Importar arquivo csv
df = pd.read_csv( 'dataset/FTC_Aula34.1.csv' )

##  =============================
##  Funções
##  =============================
### Limpeza de dados
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
    # Convertendo a coluna 'Order_Date' para datetime
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%Y-%m-%d' )
    ## Excluindo coluna Unnamed: 0
    df1 = df1.drop(['Unnamed: 0'], axis=1).reset_index()
    ## Remover NaN da coluna Festival
    nan_festival = (df1['Festival'] != 'NaN ' )
    df1 = df1.loc[nan_festival, :].copy()
    ## Remover espaços da coluna Festival
    df1.loc[: ,'Festival'] = df1.loc[ : ,'Festival'].str.strip()
    ## Criando a coluna 'week_of_year
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U' )
    ## Convertendo coluna 'week_of_year'
    df1['week_of_year'] = df1['week_of_year'].astype(int)
    ## Limpando a coluna 'Time_taken(min)'
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1] )
    ## convertendo a coluna 'Time_taken(min)' para número
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )
    return df1

## Copiando / limpando dataframe
df1 = clean_code(df)

def distance(df1, fig):
    if fig == False:
        cols = ['Delivery_location_latitude', 'Delivery_location_longitude',
                'Restaurant_latitude', 'Restaurant_longitude']
        df1['distance'] = df1.loc[:, cols].apply(lambda x: haversine(
                                        (x['Restaurant_latitude'],
                                             x['Restaurant_longitude']),
                                        (x['Delivery_location_latitude'],
                                                x['Delivery_location_longitude']) ), axis=1)
        avg_distance = np.round( df1['distance'].mean(),2)
        return avg_distance

    else:
        cols = ['Delivery_location_latitude', 'Delivery_location_longitude',
               'Restaurant_latitude', 'Restaurant_longitude']
        df1['distance'] = (df1.loc[:, cols].apply(lambda x:
                                        haversine((x['Restaurant_latitude'],
                                        x['Restaurant_longitude']),
                                    (x['Delivery_location_latitude'],
                                            x['Delivery_location_longitude'])), axis=1))
        avg_distance = (df1.loc[:, ['City', 'distance']].groupby('City')
                                                        .mean().reset_index() )
        fig = go.Figure(data=[go.Pie(labels=avg_distance['City'],
                                    values=avg_distance['distance'],
                                    pull=[0, 0.1,0]) ])
        return fig


#     """
#     Esta função calcula o tempo médio e o desvio padrão do tempo de entrega.
#     Parâmetros:
#         Input:
#             - df: dataframe com os dados necessários para o cálculo
#             - op: tipo de operação que pode ser calculado
#                 'avg_time': Calcula o tempo médio
#                 'std-time': calcula o desvio padrão do tempo
#         Output:
#             - dataframe com duas colunas e uma linha
#     """

def avg_std_time_delivery(df1, festival, op):
    df_aux = ( df1.loc[:, ['Time_taken(min)', 'Festival']]
               .groupby('Festival').agg( {'Time_taken(min)' : ['mean', 'std']} ) )
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round( df_aux.loc[df_aux['Festival'] == festival, op], 2)
    return df_aux



def avg_std_time_graph(df1):
    df_aux = (df1.loc[:, ['City', 'Time_taken(min)']]
              .groupby('City').agg( {'Time_taken(min)': ['mean', 'std']} ) )
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = go.Figure()
    fig.add_trace( go.Bar( name='Control', x=df_aux['City'], y=df_aux['avg_time'],
                           error_y=dict(type='data', array=df_aux['std_time'])) )
    fig.update_layout(barmode='group')
    return fig


def avg_std_time_on_traffic(df1):
    df_aux = (df1.loc[:, ['City', 'Time_taken(min)', 'Road_traffic_density']]
              .groupby(['City', 'Road_traffic_density'])
              .agg({'Time_taken(min)': ['mean', 'std']}))
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                                  color='std_time', color_continuous_scale='RdBu',
                                  color_continuous_midpoint=np.average(df_aux['std_time']))
    return fig



#  =============================
#  Barra Lateral
#  =============================

st.header('Marketplace - Visão Restaurantes')

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
#  layout visao_restaurante
#  =============================
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '_', '_'] )

with tab1:
    #  Primeiro container
    with st.container():
        st.title( 'Overall Metrics' )

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            # st.markdown('###### Entregadores Únicos')
            delivery_unique = len( df1.loc[:, 'Delivery_person_ID'].unique() )
            # print( 'O número de entregadores únicos é: {}'.format(delivery_unique))
            col1.metric('Entregadores Únicos',delivery_unique)

        with col2:
            avg_distance = distance(df1, fig=False)
            col2.metric('A distancia media', avg_distance)

        with col3:
            df_aux = avg_std_time_delivery(df1, 'Yes', 'avg_time')
            col3.metric('Tempo médio', df_aux)

        with col4:
            df_aux = avg_std_time_delivery(df1, 'Yes', 'std_time')
            col4.metric('STD Entrega', df_aux)

        with col5:
            df_aux = avg_std_time_delivery(df1, 'No', 'avg_time')
            col5.metric('Tempo médio', df_aux)

        with col6:
            df_aux = avg_std_time_delivery(df1, 'No', 'std_time')
            col6.metric('STD Entrega', df_aux)

    st.markdown("""___""")

    #  Segundo container
    with st.container():
        st.title('Tempo Médio de entrega por cidade')
        col1, col2 = st.columns( 2 )
        # st.markdown('#### Tempo médio e STD') / Grafico de Barras

        with col1:
            fig = avg_std_time_graph(df1)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("""___""")

        with col2:
            st.markdown('##### Tempo médio por cidade e tráfego')
            mean_std4 = (df1.loc[:, ['Time_taken(min)', 'City', 'Type_of_order']]
                         .groupby(['City', 'Type_of_order'])
                         .agg({'Time_taken(min)': ['mean', 'std']}))

            mean_std4.columns = ['avg_time', 'std_time']
            mean_std4 = mean_std4.reset_index()
            st.dataframe(mean_std4)


    #  Terceiro Container ----- Já corrigido
    with st.container():
        st.title(' Distribuição do tempo ')
        col1, col2 = st.columns(2)
        with col1:
            # Gráfico de Pizza
            # Tempo médio de entrega por cidade
            fig = distance(df1, fig=True)
            st.plotly_chart( fig, use_container_width=True )



        with col2:
            # st.title(' 2 ')
            fig = avg_std_time_on_traffic(df1)
            st.plotly_chart( fig, use_container_width=True )
            # fig = avg_std_time_on_traffic(df1)
            # st.plotly_chart(fig)

