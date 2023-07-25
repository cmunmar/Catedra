import os
import requests
from bs4 import BeautifulSoup
import json

with open('enlaces.txt', 'r') as file:
    lines = file.readlines()

apartado = '03 - Extensión Universitaria.'
enlaces_apartado = []

for line in lines:
    line = line.strip()
    if line.startswith('Apartado:'):
        apartado_actual = line.replace('Apartado: ', '')
    elif apartado_actual == apartado and line.startswith("{"):
        enlace = eval(line)
        enlaces_apartado.append(enlace)

if not enlaces_apartado:
    print(f"No se encontraron enlaces para el apartado '{apartado}'.")
    exit()

carpeta = apartado.replace(' ', '_')
if not os.path.exists(carpeta):
    os.mkdir(carpeta)

enlace = enlaces_apartado[5]

url = enlace['enlace']
titulo = enlace['titulo']
titulo_archivo = titulo.replace(' ', '_')

response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    content = soup.find('div', id='main-content')

    if content:
        diccionario = {
            'apartado': apartado,
            'titulo': titulo,
            'enlace': url
        }
        
        h1_element = content.find('ol')
        if h1_element:
            h1_element.extract()
        """   
        h1_element = content.find('h2')
        if h1_element:
            h1_element.extract()
        """
        h1_element = content.find('p')
        if h1_element:
            h1_element.extract()

        
        elementos = content.find_all(['h1', 'h2', 'p', 'ul', 'ol', 'h3'])
        
        subtitulo_num = 0
        seccion_num = 0
        subseccion_num = 0
        texto_acumulado = ""

        for i, elemento in enumerate(elementos, start=1):
            etiqueta = elemento.name
            texto = elemento.get_text()
            
            if etiqueta == 'h1':
                subtitulo_num += 1
                seccion_num = 0
                subseccion_num = 0
                clave = f'subtitulo-{subtitulo_num}'
                diccionario[clave] = texto.strip()
                etiqueta_anterior = 'h1'
                texto_acumulado = ""

            elif etiqueta in ('h2'):
                seccion_num += 1
                subseccion_num = 0
                clave = f'seccion-{subtitulo_num}.{seccion_num}'
                diccionario[clave] = texto.strip()
                etiqueta_anterior = 'h2'
                texto_acumulado = ""
                
            elif etiqueta in ('h3'):
                subseccion_num += 1
                clave = f'subseccion-{subtitulo_num}.{seccion_num}.{subseccion_num}'
                diccionario[clave] = texto.strip()
                etiqueta_anterior = 'h3'
                texto_acumulado = ""
                
            elif etiqueta in ('p', 'ul', 'ol'):
                if etiqueta_anterior in ('h1', 'h2', 'h3'):
                    texto_acumulado = texto.strip()
                    if etiqueta_anterior == 'h1':
                        clave = f'contenido-{subtitulo_num}'
                    if etiqueta_anterior == 'h2':
                        clave = f'contenido-{subtitulo_num}.{seccion_num}'
                    elif etiqueta_anterior == 'h3':
                        clave = f'contenido-{subtitulo_num}.{seccion_num}.{subseccion_num}'
                    etiqueta_anterior = etiqueta
                else:
                    texto_acumulado += " " + texto.strip()
                if i < len(elementos) - 1:
                    if elementos[i].name in ('h1', 'h2', 'h3'):
                        diccionario[clave] = texto_acumulado
                        texto_acumulado = ""
                else:
                    diccionario[clave] = texto_acumulado
                
            """
            elif etiqueta in ('h4'):
                subseccion_num += 1
                clave = f'subseccion-{subtitulo_num}.{seccion_num}.{subseccion_num}'
                diccionario[clave] = texto.strip()
                etiqueta_anterior = 'h4'
                texto_acumulado = ""
            """


            nombre_archivo = f"{carpeta}/{titulo_archivo}.json"
            with open(nombre_archivo, 'w') as file:
                json.dump(diccionario, file)

        print(f"Se ha creado exitosamente el archivo {nombre_archivo}")
    else:
        print(f"No se encontró el elemento <div id='main-content'> en la página web del enlace {i}.")
else:
    print(f"No se pudo acceder a la página web del enlace {i}. Código de estado:", response.status_code)
