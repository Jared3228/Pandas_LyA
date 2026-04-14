import streamlit as st
import pandas as pd
import numpy as np
import io
import math
import plotly.express as px
import plotly.figure_factory as ff

df = pd.read_csv('Datos/plantacion_datiles_v4.csv')

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