## 📘 Trabajo de fin de grado

Este proyecto en **Python** permite generar un dataset en formato **JSON** a partir de archivos **PDF sin estructura fija**, utilizando un modelo de **IA de Hugging Face** para automatizar el siguiente flujo:

---

### ⚙️ Funcionalidades

✅ Leer y segmentar contenido de PDFs  
✅ Generar preguntas relevantes basadas en el contenido  
✅ Producir cadenas de razonamiento (_chain of thought_) para cada pregunta  
✅ Generar respuestas finales con contexto  
✅ Guardar los resultados en un archivo `.json` estructurado

---

### 📦 Requisitos

- 🐍 Python **3.8+**  
- 📦 `pip`  
- 🤗 `transformers`  
- 📄 `PyMuPDF` o `pdfplumber` (para leer PDFs)  
- 📚 `datasets` (opcional, para compatibilidad con Hugging Face)

Instalación rápida:

```bash
pip install transformers pymupdf pdfplumber datasets
