#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import whoosh
from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser
import argparse
import nltk
import os
import json

def load_json(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

def preprocess_query(query):
    stemmer = nltk.stem.SnowballStemmer('spanish')
    query_tokens = nltk.word_tokenize(query)
    stemmed_tokens = [stemmer.stem(token) for token in query_tokens]
    processed_query = ' '.join(stemmed_tokens)
    return processed_query

def print_query(result, original_data, input_query):
    print(f"-> ({original_data['apartado']}) {original_data['titulo']}")
    print(f"   {original_data['enlace']}")
    res = set()
    for key, value in result.items():
        if isinstance(value, str) and input_query in value:
            if key.startswith('contenido-') and key not in res:
                parts = key.split('-')
                p = parts[1].split('.')
                if len(p) == 1:
                    subtitulo_key = f"subtitulo-{p[0]}"
                    if subtitulo_key not in res:
                        print(f"     - {original_data[subtitulo_key]}")
                        res.add(subtitulo_key)
                elif len(p) == 2:
                    subtitulo_key = f"subtitulo-{p[0]}"
                    seccion_key = f"seccion-{p[0]}.{p[1]}"
                    if seccion_key not in res:
                        print(f"     - {original_data[subtitulo_key]} --> {original_data[seccion_key]}")
                        res.add(seccion_key)
                elif len(p) == 3:
                    subtitulo_key = f"subtitulo-{p[0]}"
                    seccion_key = f"seccion-{p[0]}.{p[1]}"
                    subseccion_key = f"subseccion-{p[0]}.{p[1]}.{p[2]}"
                    if subseccion_key not in res:
                        print(f"     - {original_data[subtitulo_key]} --> {original_data[seccion_key]} --> {original_data[subseccion_key]}")
                        res.add(subseccion_key)
            elif key.startswith('subseccion-'):
                parts = key.split('-')
                p = parts[1].split('.')
                subtitulo_key = f"subtitulo-{p[0]}"
                seccion_key = f"seccion-{p[0]}.{p[1]}"
                subseccion_key = f"subseccion-{p[0]}.{p[1]}.{p[2]}"
                if subseccion_key not in res:
                    print(f"     - {original_data[subtitulo_key]} --> {original_data[seccion_key]} --> {original_data[subseccion_key]}")
                    res.add(subseccion_key)
            elif key.startswith('seccion-'):
                parts = key.split('-')
                p = parts[1].split('.')
                subtitulo_key = f"subtitulo-{p[0]}"
                seccion_key = f"seccion-{p[0]}.{p[1]}"
                if seccion_key not in res:
                    print(f"     - {original_data[subtitulo_key]} --> {original_data[seccion_key]}")
                    res.add(seccion_key)
            elif key.startswith('subtitulo-'):
                parts = key.split('-')
                p = parts[1].split('.')
                subtitulo_key = f"subtitulo-{p[0]}"
                if subtitulo_key not in res:
                    print(f"     - {original_data[subtitulo_key]}")
                    res.add(subtitulo_key)

def load_original_data(directory):
    original_data = {}
    for dirname, subdirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith(".json"):
                fullname = os.path.join(dirname, filename)
                data = load_json(fullname)
                original_data[filename] = data  # Agregar docid sin cambios
    return original_data

parser = argparse.ArgumentParser()
parser.add_argument("dir_ind", help='Index directory')
args = parser.parse_args()

dir_ind = args.dir_ind
ix = open_dir(dir_ind)
fields = [field_name for field_name, field_type in ix.schema.items() if isinstance(field_type, whoosh.fields.TEXT)]
original_data = load_original_data("Archivos")

with ix.searcher() as searcher:
    while True:
        input_query = input('Query: ')
        if input_query == '':
            break
        processed_query = preprocess_query(input_query)
        query_parser = MultifieldParser(fields, schema=ix.schema)
        query = query_parser.parse(processed_query)
        results = searcher.search(query)
        for x in results:
            doc_id = x['docid']
            if doc_id in original_data:
                print_query(x, original_data[doc_id], processed_query)
        print('=================')
        print(f'{len(results)} documentos')
        
