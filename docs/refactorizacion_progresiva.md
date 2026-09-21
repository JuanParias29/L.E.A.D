# Refactorizacion progresiva

## Etapa 1: datos e ingestion

### Cambios realizados

- Se creo `src/lead/data/loaders.py` para cargar el dataset transaccional desde una ruta configurable.
- Se creo `src/lead/data/schema.py` con las columnas documentadas en `notebooks/01_eda_general.py`.
- Se creo `src/lead/data/validation.py` con una validacion basica de existencia del archivo.
- Se agregaron pruebas focalizadas en `tests/test_data_ingestion.py`.
- Los notebooks originales no fueron modificados.

### Logica trasladada

La funcion `load_sales_transactions()` conserva la lectura con separador `;` y `on_bad_lines='skip'` del notebook. No realiza conversion de fechas, tipos numericos, categorias ni limpieza de registros; esas operaciones pertenecen a la etapa 2.

### Clasificacion de problemas

- **[REFACTORIZACION TECNICA]** Las rutas de Google Drive y el montaje de Colab quedaron fuera del modulo. La ruta ahora se recibe como argumento.
- **[REFACTORIZACION TECNICA]** La carga y el contrato estructural del dataset quedaron separados de la limpieza.
- **[REQUIERE DECISION METODOLOGICA]** Se conserva `on_bad_lines='skip'`, aunque descartar registros puede ocultar problemas de calidad. Se debe decidir posteriormente si el pipeline productivo debe fallar, advertir o registrar esas filas.
- **[REQUIERE VALIDACION CON EL NEGOCIO]** El contrato usa las columnas documentadas en el notebook. Debe confirmarse que siguen siendo obligatorias para todos los archivos operativos.

### Pendientes

- Extraer la conversion de tipos y reglas de limpieza.
- Definir configuracion centralizada de rutas y formatos.
- Agregar reporte de filas descartadas cuando se tome una decision sobre `on_bad_lines`.
