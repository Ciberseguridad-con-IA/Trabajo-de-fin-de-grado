Este proyecto en Python permite generar un dataset en formato JSON a partir de archivos PDF sin estructura fija, utilizando una IA de Hugging Face para:

  -Leer y segmentar contenido de PDFs.
  -Generar preguntas relevantes basadas en el contenido.
  -Producir cadenas de razonamiento (chain of thought) para cada pregunta.
  -Generar respuestas finales.
  -Guardar los resultados en un archivo .json estructurado.

⚙️ Requisitos
  -Python 3.8+
  -pip
  -transformers
  -PyMuPDF o pdfplumber (para leer PDFs)
  -datasets
