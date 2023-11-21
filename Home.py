import pandas as pd
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Home",layout='wide')

image = Image.open( 'curry_delivery.jpg' )
st.sidebar.image( image, width=120)

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest Delivery in Town')
st.sidebar.markdown( """___""")

st.write( "# Curry Company Growth Dashboard" )

st.markdown(
    """
    ### Como utilizar esse Growtd Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visão Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes
    ### Ask for Help
    - Time de Data Sciense no Discord
        
    """ )
