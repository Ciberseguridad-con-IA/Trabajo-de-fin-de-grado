# -*- coding: utf-8 -*-
"""Generacion dataset definciones.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1AcdeTsmm7zLeDyleeGt9pdkYCCPX8u3i
"""

!pip install requests python-dotenv --quiet

import os
import re
import requests
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import json

from google.colab import drive
drive.mount('/content/drive')

# Carga las variables desde el archivo
load_dotenv("/content/drive/My Drive/TFG/.env")
#load_dotenv("/content/drive/Shareddrives/TFG/.env") #usad esto si no sois yo :D

DEEPINFRA_API_KEY = os.getenv("DEEPINFRA_API_KEY")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

"""https://api.together.ai/?_gl=1*xpc3i2*_gcl_au*NzMzMjA0ODc1LjE3NDMwOTk3NTk.*_ga*OTcwMzk4ODUwLjE3NDMwOTk3NTg.*_ga_BS43X21GZ2*MTc0MzA5OTc1Ny4xLjAuMTc0MzA5OTc1Ny4wLjAuMA..*_ga_BBHKJ5V8S0*MTc0MzA5OTc1Ny4xLjAuMTc0MzA5OTc1Ny4wLjAuMA.."""

def extract_json(text):
    """Extrae y limpia el bloque JSON de la respuesta del modelo."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        extracted = match.group(0)
        try:
            return json.loads(extracted)  # Intentar cargarlo directamente
        except json.JSONDecodeError:
            # Si falla, intentar limpiar caracteres no válidos
            cleaned_text = extracted.replace("\\_", "_")  # Corrige backslashes no deseados
            try:
                return json.loads(cleaned_text)
            except json.JSONDecodeError:
                return None
    return None

"""1. Recibir la pregunta
2. Identificar si la pregunta es sobre una definición
3. Si es una definicion responder y cortar el razonamiento
4. Si no es script hacer RAG
"""

def clean_possible_json(raw: str) -> str:
    # Reemplazar comillas dobles no escapadas dentro de strings
    # Sustituir comillas dobles dentro del cuerpo del valor
    return raw.replace('\n', '\\n').replace('\"', '\\"')

def generate_qa_structure(topic: str, model: str = "mistralai/Mixtral-8x7B-Instruct-v0.1") -> dict:
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    # Construcción del prompt que se enviará al modelo
    prompt = f"""
    Vas a recibir un tema en forma de una breve descripción. Tienes que identificar que se trata de una explicación sobre un comando Linux.

    El objetivo es crear un JSON con la siguiente estructura:
    - "Question": Una pregunta clara que un usuario podría preguntar sobre el tema.
    - "Complex_CoT": Un proceso de razonamiento que identifique qué clase de información es solicitada (definición, explicación de un comando, etc). Basado en su conocimiento debe conocer la respuesta.
    - "Response": La respuesta final y concisa.

    Ejemplo:

    input: 'uname -r → mostrar la versión del kernel usado.'

    output:
    {{
        "Question": "¿Qué hace el comando 'uname -r' en Linux?",
        "Complex_CoT": "El usuario está preguntando por la funcionalidad de un comando en Linux. Por tanto, basado en mis conocimientos, todo lo que tengo que hacer es aportar una respuesta que sea capaz de resolver la consulta de forma correcta, asegurándome de que el usuario lo entienda bien",
        "Response": "El comando 'uname -r' sirve para mostrar el número de versión del kernel que se está ejecutando actualmente. Esto puede ser especialmente útil para comprobar la compatibilidad con drivers, módulos o para solucionar problemas del sistema. Por ejemplo, al ejecutarlo podría devolver algo como '5.15.0-84-generic'"
    }}

    Es importante traducir todo al inglés.

    Tema: '{topic}'
    """

    data = {
        "model": model,
        "messages": [{"role": "system", "content": "You are a cybersecurity expert with advanced knowledge in penetration testing, vulnerability analysis, and exploit development. You specialize in guiding and explaining the process of solving VulnHub machines, focusing on practical methodologies, critical thinking, and step-by-step problem-solving strategies."},
                     {"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1000
    }

    text_output = ""

    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        # Por si hay error más adelante, definimos text_output desde ya
        text_output = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

        if "choices" not in result:
            print(f"❌ Error en la API: {result}")
            return {
                "Question": topic,
                "Complex_CoT": "Error: Respuesta no válida de la API.",
                "Response": str(result)
            }

        text_output = result["choices"][0]["message"]["content"].strip()

        # Primer intento: extract_json
        json_response = extract_json(text_output)

        if json_response is None:
            # Segundo intento: json.loads directo con escape de comillas internas
            try:
                escaped_text_output = text_output.replace('\\"', '"')  # normalizar escapes previos
                escaped_text_output = re.sub(r'(?<!\\)"', r'\"', escaped_text_output)  # escapa comillas dobles que no están escapadas
                json_response = json.loads(escaped_text_output)
                print("✅ JSON cargado directamente desde texto plano (tras escapado).")
            except json.JSONDecodeError:
                pass  # Pasamos al tercer intento

        if json_response:
          # Si la respuesta es una lista (multiple questions), procesar cada pregunta
            if isinstance(json_response.get("Questions"), list):
                processed_questions = []
                for item in json_response["Questions"]:
                    question_data = {
                        "Question": item.get("Question"),
                        "Complex_CoT": item.get("Complex_CoT"),
                        "Response": item.get("Response")
                    }
                    processed_questions.append(question_data)

                print("✅ JSON extraído correctamente con múltiples preguntas.")
                return {"Questions": processed_questions}
            if isinstance(json_response.get("Complex_CoT"), dict):
                steps = [f"{i+1}. {v}" for i, (k, v) in enumerate(json_response["Complex_CoT"].items())]
                json_response["Complex_CoT"] = "\n".join(steps)

            print("✅ JSON extraído correctamente.")
            return json_response

        # Tercer intento: buscar JSON embebido con regex
        raw_content = result["choices"][0]["message"]["content"]
        embedded_json_match = re.search(r"\{.*\}", raw_content, re.DOTALL)
        if embedded_json_match:
          possible_json = embedded_json_match.group(0)
          cleaned = clean_possible_json(possible_json)
          try:
              parsed = json.loads(cleaned)
              print("✅ JSON recuperado del contenido embebido (con limpieza).")
              return parsed
          except Exception as e:
            pass

    except Exception as e:
        pass  # Silencioso hasta fallo total

    # Si llegamos aquí, fallaron todos los intentos
    print(f"⚠️ Fallo total al procesar:\n{text_output}\n")
    return {
        "Question": topic,
        "Complex_CoT": "Error: No se pudo procesar correctamente la respuesta.",
        "Response": "El modelo devolvió una estructura anidada no válida. Revisa logs."
    }

def process_file(input_filepath: str, output_filepath: str):
    results = []

    with open(input_filepath, "r", encoding="utf-8") as file:
        topics = [line.strip() for line in file if line.strip()]

    for topic in topics:
        result = generate_qa_structure(topic)

        # Si viene en formato {"Questions": [ ... ]}
        if isinstance(result, dict) and "Questions" in result:
            results.extend(result["Questions"])  # Añade todas las preguntas
        else:
            results.append(result)  # Añade el resultado normal

    with open(output_filepath, "w", encoding="utf-8") as outfile:
        json.dump(results, outfile, indent=2, ensure_ascii=False)

    print(f"Se han guardado los resultados en {output_filepath}")

# Definir rutas de los archivos
input_file = "/content/drive/My Drive/TFG/topics.txt"  # Archivo de entrada
output_file = "/content/drive/My Drive/TFG/definiciones.json"  # Archivo de salida

# Ejecutar el procesamiento
test_run = False  # Cambiar a False para ejecutar en todo el archivo

if test_run:
    with open(input_file, "r", encoding="utf-8") as file:
        first_line = file.readline().strip()
    print(generate_qa_structure(first_line))
else:
    process_file(input_file, output_file)