
# Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from PIL import Image
import folium as fl
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Empresa', page_icon='', layout='wide')

#Importar arquivo csv
df = pd.read_csv( 'FTC_Aula34.1.csv' )

##  =============================
####Funções
##  =============================

###Limpeza de dados
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

# #Copiando dataframe
df1 = clean_code(df)

def order_metric(df1):
    # Order Metric
    cols = ['ID', 'Order_Date']
    # Seleção de linhas
    df_aux1 = df1.loc[:, cols].groupby('Order_Date').count().reset_index()
    fig = px.bar(df_aux1, x='Order_Date', y='ID')
    return fig

def traffic_order_share(df1):
    # Gráfico pizza
    df_aux3 = (df1.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density')
               .count().reset_index() )
    df_aux3['entregas_%'] = df_aux3['ID'] / df_aux3['ID'].sum()
    # Criando o gráfico
    fig = px.pie(df_aux3, values='entregas_%', names='Road_traffic_density')
    return fig

def traffic_order_city(df1):
    # st.markdown( '#Coluna2' )
    df_aux4 = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(
        ['City', 'Road_traffic_density']).count().reset_index()
    # Criando o gráfico
    fig = px.scatter(df_aux4, x='City', y='Road_traffic_density', size='ID', color='City')
    return fig

def order_by_week(df1):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux2 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    # Criando o Gráfico
    fig = px.line(df_aux2, x='week_of_year', y='ID')
    return fig

def order_share_by_week(df1):
    df_aux01 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux02 = (df1.loc[:, ['Delivery_person_ID', 'week_of_year']]
                .groupby('week_of_year').nunique().reset_index() )
    # Junção de dois dataframes
    df_aux = pd.merge(df_aux01, df_aux02, how='inner')
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    # Criação do Gráfico
    fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')
    return fig

def country_maps(df1):
    #
    df_aux6 = (df1.loc[:,
    ['City', 'Road_traffic_density',
    'Delivery_location_latitude', 'Delivery_location_longitude']]
    .groupby(['City', 'Road_traffic_density'])
    .median().reset_index() )
    # df_aux6
    map = fl.Map()
    for index, location_info in df_aux6.iterrows():
        fl.Marker([location_info['Delivery_location_latitude'],
                      location_info['Delivery_location_longitude']],
                      popup=location_info[['City', 'Road_traffic_density']]).add_to(map)
    folium_static( map, width=800, height=600)


### Operação com dados
# Colunas
cols = ['ID', 'Order_Date']

# Seleção de linhas
df_aux = df1.loc[:, cols].groupby( 'Order_Date' ).count().reset_index()

# Desenhar o gráfico de linhas
# Plotly
px.bar( df_aux, x='Order_Date', y='ID')


##  =============================
##  Barra Lateral
##  =============================

st.header('Marketplace - Visão Cliente')

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
linhas_selecionadas = (df1['Order_Date'] < date_slider)
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

st.dataframe( df1 )

#  =============================
#  Layout do streamlit
#  =============================
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'] )

with tab1:
    with st.container():
        st.markdown('# Orders by Day')
        fig = order_metric(df1)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        col1, col2 = st.columns( 2 )
        with col1:
            fig = traffic_order_share( df1 )
            st.header( "Traffic Order Share" )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.header('Traffic Order City')
            fig = traffic_order_city(df1)
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    with st.container():
        st.header('# Order by Week')
        fig = order_by_week(df1)
        st.plotly_chart(fig, user_container_width=True)

    with st.container():
        st.header('#Order Share by Week')
        fig = order_share_by_week(df1)
        st.plotly_chart(fig, user_container_width=True)


with tab3:
    st.header('# Country Maps')
    country_maps(df1)
    # Importando biblioteca folium p/ criar o mapa



