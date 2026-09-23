#!/usr/bin/env python3
"""
Nova Hub Publisher — ModernoTech
Script para publicar Nova 2B (archivo GGUF, Modelfile y Model Card)
directamente en el Hugging Face Hub bajo la cuenta de Breacorp.
"""

import os
import sys

def print_instructions():
    print("=" * 70)
    print("  🚀 PUBLICACIÓN UNIVERSAL DE NOVA 2B EN HUGGING FACE / OLLAMA")
    print("  Autor: ModernoTech | Repositorio: Breacorp/nova-2b")
    print("=" * 70)
    print("""
Para que cualquier cliente tuyo pueda ejecutar Nova 2B directamente con:
  • LM Studio: buscando 'Breacorp/nova-2b'
  • Ollama: corriendo 'ollama run hf.co/Breacorp/nova-2b'
  • llama.cpp: descargando con '-hf Breacorp/nova-2b'

Sigue estos 3 pasos sencillos:

1. Instalar la herramienta oficial de Hugging Face (si no la tienes):
   pip install huggingface_hub

2. Iniciar sesión con tu Hugging Face Token (con permisos de Write):
   huggingface-cli login

3. Subir el archivo GGUF y el Modelfile ejecutando:
   huggingface-cli upload Breacorp/nova-2b ./nova-2b.gguf nova-2b.gguf
   huggingface-cli upload Breacorp/nova-2b ./Modelfile Modelfile
   huggingface-cli upload Breacorp/nova-2b ./README.md README.md

Una vez subido, cualquier cliente en el mundo podrá cargar 'Breacorp/nova-2b'
en su LM Studio u Ollama con todo el comportamiento experto preconfigurado.
""")
    print("=" * 70)

if __name__ == "__main__":
    print_instructions()
