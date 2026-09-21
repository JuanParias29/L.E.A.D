# L.E.A.D.
## Logistica Evaluation of Analytics & Demand

Herramienta basada en técnicas de series de tiempo y aprendizaje automático para el pronóstico de la demanda y la estimación de su incertidumbre, orientada al cálculo del stock de seguridad para la gestión de inventarios. La metodología implementada documenta un pipeline técnico, reproducible y modular que abarca desde el análisis exploratorio de datos hasta el despliegue de un MVP funcional en Streamlit.

---

# Stack Tecnológico

## Lenguaje y Entorno

- Python 3.10+
- Google Colab

## Análisis y Procesamiento

- pandas
- numpy
- matplotlib
- seaborn
- plotly

## Forecasting y Machine Learning

- statsforecast
- sktime
- Prophet
- scikit-learn

## Aplicación MVP

- Streamlit
- Plotly

## Infraestructura y Despliegue

- Docker
- Git + GitHub

---

# Arquitectura Metodológica

La herramienta adopta una aproximación técnica inspirada en CRISP-DM, enfocándose exclusivamente en las etapas relacionadas con procesamiento, modelado, evaluación y despliegue analítico.

La metodología implementada permite:

- Analizar el comportamiento histórico de la demanda y su variabilidad temporal.
- Explorar y comparar modelos estadísticos y de aprendizaje automático para forecasting.
- Evaluar precisión predictiva e incertidumbre asociada al pronóstico.
- Integrar la estimación de incertidumbre dentro del cálculo de stock de seguridad.
- Implementar un MVP funcional orientado al apoyo en decisiones de inventario.
---

# Estructura del Proyecto

```text
LEAD/
│
├── data/
│   ├── sample/
│   │   └── demanda_demo.csv
│   │
│   ├── processed/
│   │   └── series_modelado.csv
│   │
│   └── outputs/
│       ├── forecasts.csv
│       └── stock_seguridad.csv
│
├── notebooks/
│   │
│   ├── 01_eda_general.ipynb
│   ├── 02_seleccion_productos.ipynb
│   ├── 03_preprocesamiento.ipynb
│   ├── 04_analisis_demanda.ipynb
│   ├── 05_modelado.ipynb
│   ├── 06_stock_seguridad.ipynb
│   └── 07_validacion.ipynb
│
├── src/
│   │
│   ├── forecasting/
│   │   ├── train.py
│   │   ├── predict.py
│   │   └── evaluate.py
│   │
│   ├── inventory/
│   │   ├── uncertainty.py
│   │   └── stock_safety.py
│   │
│   ├── visualization/
│   │   └── plots.py
│   │
│   └── utils/
│       ├── metrics.py
│       └── helpers.py
│
├── models/
│   ├── candidatos/
│   └── modelo_final.pkl
│
├── reports/
│   ├── eda/
│   ├── metricas/
│   └── figuras/
│
├── app/
│   ├── app.py
│   ├── pages/
│   ├── components/
│   └── assets/
│
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── docs/
│   ├── metodologia.md
│   └── arquitectura.md
│
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```
---

# Instalación y Ejecución con Docker

## Construir contenedores

```bash
docker compose build
```

## Levantar servicios

```bash
docker compose up
```

---

# Licencia

Este proyecto se distribuye bajo la licencia MIT.

El desarrollo tiene fines académicos y de investigación aplicada. Su utilización está orientada exclusivamente a actividades internas de análisis y apoyo operacional dentro de la organización.

No está destinado para distribución comercial externa.
