# L.E.A.D.
## Logiser Evaluation of Analytics & Demand

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

Cada fase genera artefactos reutilizables que alimentan la siguiente etapa, garantizando trazabilidad, modularidad y reproducibilidad del pipeline completo.

| # | Fase | Carpeta | Inputs | Outputs |
|---|------|---------|--------|---------|
| 1 | Entendimiento y exploración de datos | `01_entendimiento_datos/` | Datos históricos | Dataset analizado + reporte EDA |
| 2 | Preprocesamiento de datos | `02_preprocesamiento_datos/` | Datos crudos | Datos limpios y transformados |
| 3 | Exploración y entrenamiento de modelos | `03_modelado/` | Series temporales | Modelos candidatos + métricas |
| 4 | Selección y ajuste de modelos | `04_seleccion_ajuste/` | Modelos candidatos | Modelo final serializado |
| 5 | Cálculo de stock de seguridad | `05_stock_seguridad/` | Forecasts + incertidumbre | Stock recomendado |
| 6 | Evaluación y validación | `06_evaluacion_real/` | Modelo final | Backtesting + métricas |
| 7 | MVP Streamlit | `07_app/` | Modelo entrenado | Aplicación interactiva |

---

# Estructura del Proyecto

```text
LEAD/
│
├── 01_entendimiento_datos/
│   ├── eda_general.ipynb
│   ├── analisis_series_temporales.ipynb
│   ├── data/
│   │   ├── raw/
│   │   └── interim/
│   └── reports/
│       └── eda_summary.html
│
├── 02_procesamiento_datos/
│   ├── limpieza.ipynb
│   ├── transformaciones.ipynb
│   └── outputs/
│       └── dataset_clean.csv
│
├── 03_modelado/
│   ├── exploracion_modelos.ipynb
│   ├── evaluacion_comparativa.ipynb
│   ├── src/
│   │   ├── train.py
│   │   ├── evaluate.py
│   │   └── utils_metricas.py
│   └── outputs/
│       ├── metricas/
│       └── modelos_candidatos.csv
│
├── 04_seleccion_ajuste/
│   ├── seleccion_modelo.ipynb
│   ├── hyperparameter_tuning.ipynb
│   ├── src/
│   │   └── tuning.py
│   └── models/
│       └── modelo_final.pkl
│
├── 05_stock_seguridad/
│   ├── calculo_stock.ipynb
│   ├── analisis_incertidumbre.ipynb
│   ├── src/
│   │   └── stock_utils.py
│   └── outputs/
│       └── stock_seguridad.csv
│
├── 06_evaluacion_real/
│   ├── backtest.ipynb
│   ├── evaluacion_operacional.ipynb
│   └── outputs/
│       └── metricas_reales/
│
├── 07_app/
│   ├── app.py
│   ├── pages/
│   ├── components/
│   └── assets/
│
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── requirements.txt
├── README.md
├── .gitignore
└── LICENSE
```

---

# Flujo General del Pipeline

```text
Datos históricos
        ↓
Exploración y análisis
        ↓
Preprocesamiento
        ↓
Entrenamiento de modelos
        ↓
Evaluación comparativa
        ↓
Selección y tuning
        ↓
Forecasting de demanda
        ↓
Estimación de incertidumbre
        ↓
Cálculo de stock de seguridad
        ↓
Aplicación Streamlit
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
