import streamlit as st
import pandas as pd
import numpy as np
import io
import math
import plotly.express as px
import plotly.figure_factory as ff

df = pd.read_csv('Datos/seguros.csv')

# Obtener las metricas generales

# Costo medio de la poliza
si_fumadores = df[df['fumador'] == 'Si']
si_fumadores_media = si_fumadores['costo'].mean()

no_fumadores = df[df['fumador'] == 'No']
no_fumadores_media = no_fumadores['costo'].mean()

# Cantidad de fumadores
fumadores = df['fumador'].value_counts()
no_fuma = fumadores[0]
si_fuma = fumadores[1]

def intervalos(var):
    import math

    n = len(var)
    x_max = var.max()
    x_min = var.min()
    recorrido = x_max - x_min
    intervalos = round(1 + (3.3 * (math.log10(n))))
    amplitud = recorrido / intervalos

    return x_min, x_max, amplitud

def tablaFrecuencia(tabla, col, nomCol):
    tabla1 = pd.DataFrame(tabla)
    lista = []

    for reg in tabla:
        cont = 0
        for i in col:
            if reg == i:
                cont += 1
        lista.append(cont)

    tabla2 = pd.DataFrame(lista)
    total = tabla2.sum()
    tabla3 = pd.concat([tabla1, tabla2], axis=1)
    tabla3.columns = [nomCol, 'frecAbs']

    def calcula(frecAbs):
        fRel = frecAbs / total
        return fRel

    tabla3['frecRel'] = tabla3['frecAbs'].apply(calcula)
    tabla3['frecAcum'] = tabla3['frecAbs'].cumsum()

    return tabla3

# Funcion para tabla de frecuencias agrupadas

# global intervalos

def tabla_Hist(varCol, nomCol):
    global intervalos
    # Paso 1: Determinar el tamaño de la muestra
    print('Variable: ', nomCol, '\n')
    n = len(varCol)
    print('Paso 1: Tamaño de la muestra: ', n, '\n')

    # Paso 2: Determinar el maximo y mínimo
    x_max = varCol.max()
    x_min = varCol.min()
    print('Paso 2: Valor máximo: ', x_max, 'Valor mínimo: ', x_min, '\n')

    # Paso 3: Determinar el recorrido
    recorrido = x_max - x_min
    print('Paso 3: Recorrido: ', recorrido, '\n')

    # Paso 4: Calcular intervalos (clases)
    # Formula de Sturges (1 + 3.3 log10(n))
    intervalos = round(1 + (3.3 * (math.log10(n))))
    print('Paso 4: Intervalos: ', intervalos, '\n')

    # Paso 5: Calcular la amplitud de cada intervalo
    amplitud = recorrido / intervalos
    print('Paso 5: Amplitud: ', '%0.2f' %amplitud, '\n')

    # Paso 6: construir la tabla de frecuencias
    df_tf = pd.DataFrame()
    df_tf['Clase'] = list(range(1, intervalos + 1))
    df_tf['limInf'] = np.full(shape = intervalos, fill_value=np.nan)

    for i in range(intervalos):
        df_tf.loc[i, 'limInf'] = round(x_min + (i * amplitud), 3)
    
    df_tf['limSup'] = round(df_tf['limInf'] + amplitud, 3)
    df_tf['x'] = (df_tf['limSup'] + df_tf['limInf']) / 2
    df_tf['f'] = np.full(shape= intervalos, fill_value=np.nan)

    for i in range(intervalos):
        k = 0
        if i == 0:
            for j in range(n):
                if varCol[j] <= df_tf['limSup'][i]:
                    k += 1
                df_tf.loc[i, 'f'] = k
            else:
                for j in range(n):
                    if (varCol[j] > df_tf['limInf'][i]) and (varCol[j] <= df_tf['limSup'][i]):
                        k += 1
                    df_tf.loc[i, 'f'] = k

    df_tf['Fa'] = df_tf['f'].cumsum()
    df_tf['fr'] = round(df_tf['f'] / n, 4)
    df_tf['Fra'] = df_tf['fr'].cumsum()

    return df_tf

# Funcion para actualizar el layout de las graficas

def actualiza_layout(grafica, x_title, y_title):

    grafica.update_layout(
        xaxis_title = x_title,
        yaxis_title = y_title,
        paper_bgcolor = 'white',
        plot_bgcolor = 'white',
        title_pad_l = 20,
        title_font_family = 'verdana',
        title_font_color = 'black',
        title_font_size = 16,
        font_size = 15,
        height = 400
    )

# Grafica de scatter

def sct(varX, varY, co, cocs, x_titulo, y_titulo, tam, titulo, marg_x = None, marg_y = None, facetCol = None):

    grafica_sc = px.scatter(df, x = varX, y = varY,
                            color = co,
                            color_continuous_scale=cocs,
                            size = tam,
                            marginal_x=marg_x,
                            marginal_y=marg_y,
                            facet_col=facetCol,
                            title = titulo
                            )
    
    actualiza_layout(grafica_sc, x_titulo, y_titulo)

    return grafica_sc

# Grafica de Histograma
def histograma(var, tit, subtit, col, cods, textoA, x_titulo, y_titulo, agrupados, x_min = 0, x_max = 0, amplitud = 0,
               varY = None, pshape = None):

    if agrupados == True:
        grafica_hist = px.histogram(df, x = var,title = tit,subtitle = subtit,text_auto = textoA)
        grafica_hist.update_traces(marker_line_width = 1, xbins = dict(start = x_min, end = x_max, size = amplitud))

    elif agrupados == False:
        grafica_hist = px.histogram(df, x = var, y = varY, pattern_shape = pshape, title = tit, subtitle = subtit, color = col,
                                    color_discrete_sequence = cods, text_auto = textoA)

    actualiza_layout(grafica_hist, x_titulo, y_titulo)

    return grafica_hist

def grafica_densidad(var, etiqueta, color):

    _, _, amplitudA = intervalos(var)
    amplitud = amplitudA

    graf_dens = ff.create_distplot([var], [etiqueta],
                                   show_hist = 'True',
                                   show_curve= 'True',
                                   curve_type= 'kde',
                                   show_rug= False,
                                   bin_size= amplitud,
                                   colors = [color]
                                   )
    graf_dens.update_traces(marker_line_width = 1)

    graf_dens.update_layout(
        title = 'Grafica de densidad: ' + etiqueta,
        xaxis_title = 'Rango de ' + etiqueta,
        yaxis_title = 'Frecuencia - Densidad',
        paper_bgcolor = 'white',
        plot_bgcolor = 'white',
        title_pad_l = 20,
        title_font_family = 'verdana',
        title_font_color = 'black',
        title_font_size = 16,
        font_size = 15,
        height = 400
        )
    
    return graf_dens

# Grafica de BoxPlot

def boxplt1(yvar, cds, titulo, x_titulo, y_titulo, col = None, xvar = None, puntos = None):

    grafica_box = px.box(df, x = xvar, y = yvar,
                         points= puntos,
                         color = col,
                         color_discrete_sequence= cds,
                         title= titulo
                         )
    
    actualiza_layout(grafica_box, x_titulo, y_titulo)

    return grafica_box

# Grafica Sunburst

grafica_sunb = px.sunburst(df, path= ['region', 'fumador', 'sexo'],
                           values= 'costo', color= 'costo',
                           color_continuous_scale= px.colors.cyclical.IceFire)

grafica_sunb.update_traces(marker = dict(line = dict(color = 'purple', width = 1)))

grafica_sunb.update_layout(
    title = 'Costos de la polizaa por region',
    font = dict(family = 'Courier New, monospace',
                size = 14,
                color = 'purple'),
    paper_bgcolor = 'white',#'hsl(50, 20%, 50%)',
    height = 400
)

st.set_page_config(page_title = 'Tablero de control',
                   layout= 'wide', page_icon='Imagenes/imagenIco.ico')

st.markdown(
    """
        <style>
        .block-container {
            padding-top:1rem;
            padding-bottom:0rem;
            padding-left:5rem;
            padding-right:5rem;
        }
        </style>
        """, unsafe_allow_html= True
)
st.title('Tablero de visualizacion de variables')
st.text('Indicadores generales para el DataSet Poliza de seguro para gastos medicos')

colm1, colm2, colm3, colm4 = st.columns(4, vertical_alignment= "center", border = True)

with colm1:
    st.metric('Costo promedio para fumadores',
              '$ %0.2f' %si_fumadores_media,
              delta = '9382 mediana',
              delta_color= 'inverse')
with colm2:
    st.metric('Costo promedio para no fumadores',
              '$ %0.2f' %no_fumadores_media,
              delta = '1200 mediana')
with colm3:
    porcentajeSi = ('%0.0f' %((si_fuma/1338) * 100))
    st.metric('Numero de fumadores',
              si_fuma,
              delta= f'{porcentajeSi} %',
              delta_color= 'inverse')
with colm4:
    porcentajeNo = ('%0.0f' %((no_fuma/1338) * 100))
    st.metric('Numero de no fumadores',
              no_fuma,
              delta= f'{porcentajeNo} %')
    
st.markdown('---')

#Seccion logo de la empresa
st.sidebar.header('Logo Empresa')
st.sidebar.image('Imagenes/imagenG.png')

# Selector de variables
st.sidebar.markdown('---')
st.sidebar.header('Analisis exploratorio de DataSet')
op = st.sidebar.radio('Selecciona:', ['Estadistica', 'Visualizacion'])

if op == 'Visualizacion':
    st.sidebar.markdown('---')

    st.sidebar.header('Visualizacion exploratoria')
    opcion = st.sidebar.radio('Selecciona:',
                              ['Una variable', 'Dos variables'])
    
    if opcion == 'Una variable':
        opcionUni = st.sidebar.selectbox('Selecciona una variable',
                                         ['Hijos', 'Region', 'IMC', 'Costo', 'Fumador'])
        col1, col2 = st.columns([0.98, 0.02])
        if opcionUni == 'Hijos':
            with col1:
                var = 'hijos'
                tit = 'Frecuencia de numero de hijos'
                subtit = 'por contratante'
                col = 'hijos'
                cods = [['Red'], ['Olive'], ['Yellow'], ['Purple'], ['Blue'], ['Green']]
                textoA = True
                x_titulo = 'Numero de hijos'
                y_tituto = 'Frecuencia'
                agrupados = False
                hist_hijos = histograma(var, tit, subtit, col, cods, textoA, x_titulo, y_tituto, agrupados)

                st.plotly_chart(hist_hijos, use_container_width= True)

        elif opcionUni == 'Region':
            with col1:
                coll_1, coll_2 = st.columns(2)
                
            with coll_1:
                var = 'region'
                tit = 'Frecuencia de variable region'
                subtit = 'Cantidad por cada región'
                col = 'region'
                cods = [['Red'], ['Olive'], ['Yellow'], ['Purple']]
                textoA = True
                x_titulo = 'Regiones'
                y_titulo = 'Frecuencia'
                agrupados = False
                hist_region = histograma(var, tit, subtit, col, cods, textoA,
                                         x_titulo, y_titulo, agrupados)
                
                st.plotly_chart(hist_region, use_container_width = True)
                
            with coll_2:
                st.plotly_chart(grafica_sunb, use_container_width = True)

        elif opcionUni == 'IMC':
            with col1:
                coll_1, coll_2 = st.columns(2)
                col_imc = df['imc']
                with coll_1:
                    x_min, x_max, amplitudA = intervalos(col_imc)
                    amplitud = '%0.2f' %amplitudA
                    var = 'imc'
                    tit = 'Frecuencia de variable imc'
                    subtit = 'IMC'
                    col = 'imc'
                    cods = ['Olive']
                    textoA = True
                    x_titulo = 'Rango de IMC'
                    y_titulo = 'Frecuencia'
                    agrupados = True
                    hist_imc = histograma(var, tit, subtit, col, cods,
                                          textoA, x_titulo, y_titulo,
                                          agrupados, x_min, x_max, amplitud)
                    
                    st.plotly_chart(hist_imc, use_container_width = True)
                    
                with coll_2:
                    etiq = 'imc'
                    color = 'red'
                    densidad_imc = grafica_densidad(col_imc, etiq, color)
                    st.plotly_chart(densidad_imc, use_container_width = True)
        
        elif opcionUni == 'Costo':
            with col1:
                coll_1, coll_2, coll_3 = st.columns(3)
                col_costo = df['costo']
                
                with coll_1:
                    x_min, x_max, amplitudA = intervalos(col_costo)
                    amplitud = '%0.2f' %amplitudA
                    var = 'costo'
                    tit = 'Frecuencia de variable costo'
                    subtit = 'Costo'
                    col = 'costo'
                    cods = ['Olive']
                    textoA = True
                    x_titulo = 'Rango de costo de la póliza'
                    y_titulo = 'Frecuencia'
                    agrupados = True
                    hist_costo = histograma(var, tit, subtit, col, cods,
                                            textoA, x_titulo, y_titulo,
                                            agrupados, x_min, x_max, amplitud)
                    
                    st.plotly_chart(hist_costo, use_container_width = True)
                
                with coll_2:
                    etiq = 'costo'
                    color = 'red'
                    densidad_costo = grafica_densidad(col_costo, etiq, color)
                    st.plotly_chart(densidad_costo, use_container_width = True)
                
                with coll_3:
                    yvar = 'costo'
                    cds = ['Olive']
                    titulo = 'Costo de la póliza'
                    x_titulo = 'Variable costo'
                    y_titulo = 'Costo póliza'
                    box_costo = boxplt1(yvar, cds, titulo, x_titulo, y_titulo)
                    
                    st.plotly_chart(box_costo, use_container_width = True)

        
        elif opcionUni == 'Fumador':
            with col1:
                coll_1, coll_2 = st.columns(2)
                
                with coll_1:
                    var = 'fumador'
                    tit = 'Frecuencia de variable fumador'
                    subtit = 'Clasificado por fumador y no fumador'
                    col = 'fumador'
                    cods = [['Magenta'], ['Olive']]
                    textoA = True
                    x_titulo = 'Fumador'
                    y_titulo = 'Cantidad'
                    agrupados = False
                    hist_fumador = histograma(var, tit, subtit, col, cods,
                                              textoA, x_titulo, y_titulo, 
                                              agrupados)
                    
                    st.plotly_chart(hist_fumador, use_container_width = True)
                
                with coll_2:
                    var = 'fumador'
                    tit = 'Frecuencia de variable fumador'
                    subtit = 'Clasificado por fumador y no fumador por sexo'
                    col = 'sexo'
                    cods = ['Magenta', 'Magenta', 'Olive', 'Olive']
                    textoA = True
                    x_titulo = 'Fumador'
                    y_titulo = 'Cantidad'
                    agrupados = False
                    hist_fumador2 = histograma(var, tit, subtit, col, cods,
                                               textoA, x_titulo, y_titulo, 
                                               agrupados)
                    
                    st.plotly_chart(hist_fumador2, use_container_width = True)
    elif opcion == 'Dos variables':
            opcionBi = st.sidebar.multiselect('Selecciona dos variables',
                                              ['Edad', 'Costo', 'Fumador'])
            
            lista1 = ['Edad', 'Costo']
            lista2 = ['Costo', 'Fumador']
            
            if set(opcionBi) == set(lista1):
                varX = df['edad']
                varY = df['costo']
                
                coll, col2 = st.columns(2)
                
                with coll:
                    col = 'edad'
                    cocs = 'delta'
                    x_title = 'Edad'
                    y_title = 'Costo'
                    tamano = 'edad'
                    titulo = 'Edad-costo'
                    
                    sct_EC_1 = sct(varX, varY, col, cocs, x_title, y_title, 
                                   tamano, titulo)
                    
                    st.plotly_chart(sct_EC_1, use_container_width = True)
                
                with col2:
                    col = 'fumador'
                    cocs = 'delta'
                    tamano = 'costo'
                    x_title = 'Edad'
                    y_title = 'Costo'
                    titulo = 'Edad-Costo por Fumador'
                    sct_EC_2 = sct(varX, varY, col, cocs, x_title, y_title,
                        tamano, titulo)
    
                    st.plotly_chart(sct_EC_2, use_container_width = True)

                col3, col4 = st.columns(2)
                with col3:
                    col = 'fumador'
                    cocs = 'Jet'
                    x_title = 'Edad'
                    y_title = 'Costo'
                    titulo = 'Edad-Costo con graficas al márgen'
                    tamano = 'costo'
                    marg_x = 'histogram'
                    marg_y = 'box'
                    sct_EC_3 = sct(varX, varY, col, cocs, x_title, y_title,
                                tamano, titulo, marg_x, marg_y)

                    st.plotly_chart(sct_EC_3, use_container_width = True)

                with col4:
                    col = 'fumador'
                    cocs = 'Darkmint'
                    x_title = 'Edad'
                    y_title = 'Costo'
                    titulo = 'Edad-Costo por fumador y sexo'
                    tamano = 'costo'
                    marg_x = None
                    marg_y = None
                    facetCol = 'sexo'
                    sct_EC_4 = sct(varX, varY, col, cocs, x_title, y_title,
                                tamano, titulo, marg_x, marg_y, facetCol)
                    
                    st.plotly_chart(sct_EC_4, use_container_width = True)

            elif set(opcionBi) == set(lista2):
                coll, col2 = st.columns(2)
                with coll:
                    varX = df['fumador']
                    varY = df['costo']
                    col = 'costo'
                    cocs = 'Darkmint'
                    x_title = 'Fumador'
                    y_title = 'Costo'
                    titulo = 'Fumador-Costo'
                    tamano = 'costo'
                    marg_x = None
                    marg_y = None
                    facetCol = 'sexo'
                    sct_FC_1 = sct(varX, varY, col, cocs, x_title, y_title,
                                tamano, titulo, marg_x, marg_y, facetCol)
                    
                    st.plotly_chart(sct_FC_1, use_container_width = True)
                
                with col2:
                    varX = 'sexo'
                    varY = 'costo'
                    col = 'sexo'
                    pshape = 'fumador'
                    tit = 'Variable fumador - costo - sexo'
                    subtit = 'por costo acumulado -millones'
                    cods = ['Magenta', 'Olive']
                    textoA = True
                    x_titulo = 'Fumador'
                    y_titulo = 'Costo'
                    agrupados = False
                    x_min = 0
                    x_max = 0
                    amplitud = 0
                    hist_FCS_1 = histograma(varX, tit, subtit, col, cods,
                                            textoA, x_titulo, y_titulo,
                                            agrupados, x_min, x_max, 
                                            amplitud, varY, pshape)

                    st.plotly_chart(hist_FCS_1, use_container_width = True)
                
                col3, col4, col5 = st.columns(3)
                xvar = 'fumador'
                yvar = 'costo'

                with col3:
                    col = 'fumador'
                    cds = ['Olive', 'red']
                    titulo = 'Costo de la póliza'
                    x_titulo = 'Fumador'
                    y_titulo = 'Costo póliza'
                    box_CF_1 = boxplt1(yvar, cds, titulo, x_titulo, y_titulo,
                                        col, xvar)
                    
                    st.plotly_chart(box_CF_1, use_container_width = True)
                
                with col4:
                    col = 'fumador'
                    puntos = 'all'
                    cds = ['Olive', 'Magenta']
                    titulo = 'Costo de la póliza -todos los puntos'
                    x_titulo = 'Fumador'
                    y_titulo = 'Costo póliza'
                    box_CF_2 = boxplt1(yvar, cds, titulo, x_titulo, y_titulo,
                                        col, xvar, puntos)
                    
                    st.plotly_chart(box_CF_2, use_container_width = True)

                with col5:
                    col = 'sexo'
                    puntos = 'outliers'
                    cds = ['Yellow', 'Green']
                    titulo = 'Costo de la póliza - fumador por sexo'
                    x_titulo = 'Fumador'
                    y_titulo = 'Costo póliza'
                    box_CF_3 = boxplt1(yvar, cds, titulo, x_titulo, y_titulo,
                                        col, xvar, puntos)
                    
                    st.plotly_chart(box_CF_3, use_container_width = True)

                col6, col7 = st.columns([0.98, 0.02])
                with col6:
                    col = 'region'
                    puntos = 'outliers'
                    cds = ['Yellow', 'Green', 'Blue', 'Magenta']
                    titulo = 'Costo de la póliza - fumador por regiones'
                    x_titulo = 'Fumador'
                    y_titulo = 'Costo póliza'
                    box_CF_4 = boxplt1(yvar, cds, titulo, x_titulo, y_titulo,
                                        col, xvar, puntos)
                    
                    st.plotly_chart(box_CF_4, use_container_width = True)

elif op == 'Estadistica':

    # Segunda sección de interacción
    st.sidebar.markdown('---')
    st.sidebar.header('Análisis exploratorio')
    opcion_explora = st.sidebar.selectbox('Selecciona:',
                                          ['Visualizar DataFrame', 'Descripcion por Variable',
                                           'Cuartiles', 'T Frecuencias No Agrupados',
                                           'T Frecuencias Agrupados', 'Medidas Centrales',
                                           'Medidas de Dispersion']
                                          )

    if opcion_explora == 'Visualizar DataFrame':
        with st.expander('Data Set: Póliza médica', expanded = False):
            st.markdown('''
            El Data Set es un conjunto de datos de 1,338 registros descargado de Kaggle
            Incluye información sobre la póliza médica de un grupo de personas, que incluye:
            * **Edad**. Edad del beneficiario principal.
            * **Sexo**. Sexo del contratante del seguro.
            * **IMC**. Índice de masa corporal del contratante.
            * **Hijos**. Número de hijos cubiertos por el seguro médico.
            * **Fumador**. Si el contratante del seguro es fumador o no.
            * **Región**. Área residencial del asegurado.
            * **Costo**. Costos médicos individuales facturados por el seguro médico.
            * **Educación**. Nivel académico del contratante del seguro.
            ''')
        st.dataframe(df, use_container_width = True)

        col1, col2, col3 = st.columns(3, border = True)
        with col1:
            st.text('Tipos de datos')
            tipos_df = df.dtypes
            st.write(tipos_df)
        with col2:
            info = io.StringIO()
            df.info(buf = info)
            info_df = info.getvalue()
            st.text('Información general')
            st.text(info_df)
        with col3:
            st.text('Describe df')
            describ = df.describe()
            st.write(describ)

    elif opcion_explora == 'Descripcion por Variable':
        coll1, col2, col3 = st.columns([0.3, 0.2, 0.5], border = False)
        with coll1:
            var_col = list(df.columns)
            opcion_col = st.selectbox('Selecciona la variable (describe()): ', var_col)

        with col2:
            describe_col = df[opcion_col].describe()
            st.write(describe_col)
    
    elif opcion_explora == 'Cuartiles':
        coll1, col2, col3 = st.columns([0.3, 0.2, 0.5], border = False)
        with coll1:
            opcion_col = st.selectbox('Selecciona la variable (cuartiles): ',
                                    ['edad', 'imc', 'hijos', 'costo'])
            
        with col2:
            cuartiles = df[opcion_col].quantile([0.25, 0.50, 0.75])
            st.write(cuartiles)

    elif opcion_explora == 'T Frecuencias No Agrupados':
        coll1, col2, col3 = st.columns([0.2, 0.6, 0.2], border = False)
        with coll1:
            opcion_col = st.selectbox('Selecciona la variable (Tabla Frecuencias): ', 
                                    ['region', 'hijos'])
            
        with col2:
            tablaF = sorted(df[opcion_col].unique())
            colF = df[opcion_col]
            nomColF = opcion_col
            t_f = tablaFrecuencia(tablaF, colF, nomColF)
            st.write(t_f)
    

    elif opcion_explora == 'T Frecuencias Agrupados':
        coll1, col2, col3 = st.columns([0.2, 0.6, 0.2], border = False)
        with coll1:
            opcion_col = st.selectbox('Selecciona la variable (Tabla Frecuencias): ', 
                                    ['imc', 'costo'])
            
        with col2:
            nomCol = opcion_col
            var_col = df[opcion_col]
            t_fA = tabla_Hist(var_col, nomCol)
            st.write(t_fA)
    
    elif opcion_explora == 'Medidas Centrales':
        coll1, col2, col3, col4 = st.columns(4, border = False)
        with coll1:
            opcion_col = st.selectbox('Selecciona la variable (Medidas Centrales): ',
                                    ['edad', 'imc', 'hijos', 'costo'])

        with col2:
            media_v = df[opcion_col].mean()
            st.metric('Media', '%0.2f' %media_v)
            
        with col3:
            mediana_v = df[opcion_col].median()
            st.metric('Mediana', '%0.2f' %mediana_v)
            
        with col4:
            moda_v = df[opcion_col].mode()
            st.metric('Moda', '%0.2f' %moda_v)
    
    elif opcion_explora == 'Medidas de Dispersion':
        coll1, col2, col3, col4, col5, col6 = st.columns(6, border = False)
        with coll1:
            opcion_col = st.selectbox('Selecciona la variable (Medidas Dispersion): ',
                                    ['edad', 'imc', 'hijos', 'costo'])
        
        with col2:
            rango_v = df[opcion_col].max() - df[opcion_col].min()
            st.metric('Rango', '%0.2f' %rango_v)
            
        with col3:
            varianza_v = df[opcion_col].var()
            st.metric('Varianza', '%0.2f' %varianza_v)
            
        with col4:
            std_v = df[opcion_col].std()
            st.metric('Desviación estándar', '%0.2f' %std_v)
            
        with col5:
            asimetria_v = df[opcion_col].skew()
            st.metric('Asimetría', '%0.3f' %asimetria_v)
            
        with col6:
            curtosis_v = df[opcion_col].kurt()
            st.metric('Curtosis', '%0.3f' %curtosis_v)


st.sidebar.markdown('---')
st.sidebar.header('Acerca de')
st.sidebar.info('Dashboard diseñado con fines académicos para la materia')