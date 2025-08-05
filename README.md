## 🧬 Análisis de perfiles transcriptómicos inducidos por compuestos químicos en líneas celulares humanas (LINCS L1000)

Las células humanas modifican su expresión génica en respuesta a estímulos externos, como compuestos químicos, fármacos o agentes tóxicos. El proyecto LINCS (Library of Integrated Network-based Cellular Signatures) desarrolló una colección masiva de estos perfiles transcriptómicos, conocidos como L1000, que permiten estudiar cómo distintas drogas alteran la expresión de un subconjunto representativo de genes en líneas celulares humanas.

Este proyecto tiene como objetivo analizar un subconjunto de datos del consorcio LINCS para explorar la respuesta transcriptómica a diferentes compuestos químicos. Nos enfocamos en determinar si existen patrones comunes o distintivos que permitan agrupar o clasificar compuestos según su efecto molecular.

La hipótesis de trabajo es que los compuestos con mecanismos de acción similares inducen firmas transcriptómicas comparables, y que estas firmas pueden ser utilizadas tanto para visualizar relaciones entre drogas como para entrenar modelos de machine learning capaces de predecir el compuesto aplicado a partir del perfil de expresión génica.

A lo largo del proyecto se realizarán las siguientes tareas:
- Selección y preprocesamiento de un subconjunto de datos L1000 representativo.
- Análisis exploratorio de perfiles transcriptómicos pre y post tratamiento.
- Identificación de genes diferencialmente expresados por compuesto.
- Visualización de agrupamientos y patrones mediante clustering y reducción de dimensionalidad.
- Entrenamiento de modelos de clasificación supervisada para predecir el compuesto aplicado.

Este análisis combina herramientas de bioinformática, ciencia de datos y aprendizaje automático con el objetivo de aportar conocimiento sobre los mecanismos de acción de fármacos y posibles aplicaciones en investigación biomédica.





---
## 🔁 Reproducibility: setting up the environment

This project uses a virtual environment to ensure reproducibility and avoid dependency issues.

### 1. Clone the repository

```bash
git clone https://github.com/your-username/vitD-transcriptomic-profiling.git
cd vitD-transcriptomic-profiling
```

### 2. Create and activate the virtual environment

```bash
# Create environment (only once)
python -m venv env

# Activate it
# On Windows (PowerShell)
.\env\Scripts\Activate

# On Linux/Mac
source env/bin/activate

```


### 3. Install the required packages

```bash
pip install -r requirements.txt
```

You can now run the notebooks safely and reproducibly!

### 4. To deactivate the environment

```bash
deactivate
```

---


