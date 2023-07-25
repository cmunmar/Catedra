#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from glob import glob
import os
import json
from whoosh.fields import *
from whoosh.index import create_in
import argparse
import nltk

def load_json(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

def preprocess_text(text):
    stemmer = nltk.stem.SnowballStemmer('spanish')
    words = nltk.word_tokenize(text)
    stemmed_words = [stemmer.stem(word) for word in words]
    return ' '.join(stemmed_words)

parser = argparse.ArgumentParser()
parser.add_argument("dir_doc", help='Document directory')
parser.add_argument("dir_ind", help='Index directory')
args = parser.parse_args()

dir_doc = args.dir_doc
dir_ind = args.dir_ind

schema = Schema(docid=KEYWORD(stored=True), 
                apartado=TEXT(stored=True),
                titulo=TEXT(stored=True),
                enlace=ID(stored=True),
                **{f'subtitulo-{i}': TEXT(stored=True) for i in range(1, 20)},
                **{f'contenido-{i}': TEXT(stored=True) for i in range(1, 20)},
                **{f'seccion-{i}.{j}': TEXT(stored=True) for i in range(1, 20) for j in range(1, 20)},
                **{f'contenido-{i}.{j}': TEXT(stored=True) for i in range(1, 20) for j in range(1, 20)},
                **{f'subseccion-{i}.{j}.{k}': TEXT(stored=True) for i in range(1, 20) for j in range(1, 20) for k in range(1, 20)},
                **{f'contenido-{i}.{j}.{k}': TEXT(stored=True) for i in range(1, 20) for j in range(1, 20) for k in range(1, 20)}
                )

if not os.path.exists(dir_ind):
    os.mkdir(dir_ind)
        
ix = create_in(dir_ind, schema)
writer = ix.writer()

for dirname, subdirs, files in os.walk(dir_doc):
    for filename in files:
        if filename.startswith("."):
            continue
        fullname = os.path.join(dirname, filename)
        data = load_json(fullname)
        data['docid'] = filename
        for key in data:
            if key == 'docid':
                continue
            if isinstance(data[key], str):
                data[key] = preprocess_text(data[key])
        writer.add_document(**data)
        
print('Writing index...')
writer.commit()
print('Indexing complete.')
