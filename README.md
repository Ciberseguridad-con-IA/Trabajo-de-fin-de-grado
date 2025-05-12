## 📘 Trabajo de fin de grado

Este proyecto en **Python** permite generar un dataset en formato **JSON** a partir de archivos **PDF sin estructura fija**, utilizando **LLM`s** para automatizar el siguiente flujo:

---

### ⚙️ Funcionalidades del Sistema de Generación de Dataset desde PDFs
✅ Lectura y segmentación de contenido en PDF
El sistema es capaz de procesar archivos PDF sin estructura fija, extrayendo texto de manera eficiente y dividiéndolo en fragmentos coherentes que representen pasos, instrucciones o secciones de interés para su posterior análisis.

✅ Generación automática de preguntas relevantes
A partir de los fragmentos de texto extraídos, se generan automáticamente preguntas pertinentes que permiten evaluar la comprensión del contenido o la resolución de retos presentes en el documento.

✅ Producción de cadenas de razonamiento ("Chain of Thought")
Para cada pregunta generada, el sistema produce una cadena de pensamiento lógica que representa el proceso mental paso a paso para llegar a la respuesta, mejorando la explicabilidad del modelo.

✅ Generación de respuestas finales con contexto
Se genera una respuesta final fundamentada, basada en el contenido original del documento y en la cadena de pensamiento previa, asegurando precisión y coherencia con el material fuente.

✅ Exportación de resultados a archivo JSON
Todo el contenido generado (pregunta, pensamiento y respuesta) se guarda en un archivo .json.

---

### ⚙️ Funcionalidades del Sistema de Fine-Tuning con Datos de Ciberseguridad

✅ Carga eficiente del modelo LLM con Unsloth
Utiliza la librería Unsloth para cargar y preparar el modelo DeepSeek-R1-Distill-Qwen-7B, reduciendo el consumo de memoria y acelerando el entrenamiento mediante el uso de técnicas optimizadas (como el uso de Flash Attention y carga en 4 bits).

✅ Integración de LoRA para Fine-Tuning Acelerado
Se aplica LoRA (Low-Rank Adaptation) con configuración personalizada (r=16, alpha=16) para modificar selectivamente capas del modelo, permitiendo un entrenamiento eficiente y económico sin necesidad de ajustar todos los parámetros del modelo base.

✅ Personalización del estilo de prompt
El sistema adapta el formato de los datos al estilo típico de chat (question, thought, answer)

✅ Entrenamiento supervisado con SFTTrainer
Utiliza SFTTrainer de Hugging Face con técnicas avanzadas:

  - Mezcla del modelo base y adaptado
  
  - Logging en Weights & Biases para visualización de métricas
  
  - Early stopping y evaluación con warm-up
  
  - Tokenización eficiente con padding dinámico

✅ Evaluación con ejemplos personalizados
Permite evaluar fácilmente el rendimiento del modelo usando un conjunto de preguntas nuevas, generando predicciones paso a paso desde el modelo afinado.

✅ Exportación y carga del modelo. El modelo puede guardarse en dos formatos:

  - LoRA adaptado: útil si se quiere seguir entrenando o aplicar sobre el modelo base
  
  - Modelo fusionado (merge_and_unload()): para despliegue directo sin dependencia de LoRA


✅ Soporte para datasets personalizados
Admite la carga de datasets en Hugging Face (NachoRedNav/Def-All-2) que contienen preguntas reales extraídas de procedimientos de pentesting, permitiendo un entrenamiento centrado en contextos de ciberseguridad realistas.

---

### 📦 Apunte

En este repositorio solo se muestran los scripts, para una correcta ejecución se deberan usar en el entorno de **Google Colab**, con las claves API's necesarias, y la configuración pertinente.
