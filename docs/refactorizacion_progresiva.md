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

## Etapa 2: limpieza y transformacion

### Cambios realizados

- Se creo `src/lead/data/cleaning.py`.
- Se extrajeron las conversiones de fechas, categorias y cantidades enteras.
- Se extrajeron los filtros actuales de clientes atipicos y vendedores no validos.
- Se extrajo la eliminacion de registros sin `VlrUnitario`.
- Se centralizo el calculo de `VentaTotal`, `VentaReal` y `BackOrderValue`.
- Se agregaron pruebas en `tests/test_cleaning.py`.
- Los notebooks originales no fueron modificados.

### Funciones nuevas

- `convert_sales_types()`
- `drop_missing_unit_prices()`
- `remove_atypical_clients()`
- `remove_logistica_ferretera_clients()`
- `add_sales_amounts()`
- `remove_invalid_sellers()`
- `clean_sales_transactions()`

### Logica conservada

Se conservaron las reglas de texto, los patrones de exclusion, la conversion de cantidades con coma decimal, la conversion de `FECHA` con `errors='coerce'` y el calculo de importes del notebook. Las categorias documentadas como excluidas no se filtran porque el notebook no ejecutaba ese filtro.

### Clasificacion de problemas

- **[REFACTORIZACION TECNICA]** La limpieza estaba mezclada con visualizaciones y analisis exploratorio. Ahora puede ejecutarse desde notebooks o futuros modulos de aplicacion.
- **[REQUIERE VALIDACION CON EL NEGOCIO]** Los patrones de clientes y vendedores se conservan, pero deben confirmarse con Logistica Ferretera antes de cambiarlos.
- **[REQUIERE DECISION METODOLOGICA]** Las fechas invalidas se convierten en `NaT` y no se eliminan automaticamente, porque ese es el comportamiento actual. Se debe decidir posteriormente si el pipeline productivo debe rechazarlas o reportarlas.
- **[REQUIERE DECISION METODOLOGICA]** Las cantidades numericas se convierten a enteros, truncando cualquier decimal despues de la conversion a `float`, tal como hace el notebook. Debe confirmarse que las cantidades nunca requieren fracciones.

### Pendientes

- Definir reportes de filas eliminadas y valores convertidos.
- Confirmar reglas de clientes y vendedores con el negocio.
- Confirmar el tratamiento de fechas invalidas y cantidades decimales.
- Extraer posteriormente la seleccion de productos sin mezclarla con la limpieza.

## Etapa 3: seleccion de productos

### Cambios realizados

- Se creo `src/lead/data/product_selection.py`.
- Se extrajeron el filtro por origen, Pareto, ABC-XYZ y seleccion `AX`.
- Se extrajo la clasificacion textual de productos por marca.
- Se agregaron pruebas en `tests/test_product_selection.py`.
- Los notebooks originales no fueron modificados.

### Funciones nuevas

- `filter_product_origin()`
- `calculate_pareto()`
- `add_observed_demand()`
- `classify_abc()`
- `classify_xyz()`
- `classify_abc_xyz()`
- `select_ax_pareto()`
- `assign_brand()`
- `brand_proportions()`

### Logica conservada

Se mantienen los umbrales ABC de 80/95 %, los umbrales XYZ de CV 0.5/1.0, la frecuencia semanal `W`, la inclusion de semanas sin ventas entre las fechas extremas, el filtro `FlagImportado` y la seleccion de los primeros 20 productos `AX` pertenecientes al Pareto.

### Clasificacion de problemas

- **[REFACTORIZACION TECNICA]** La misma logica de Pareto y ABC-XYZ estaba duplicada para productos importados y nacionales. Ahora se parametriza mediante funciones reutilizables.
- **[REFACTORIZACION TECNICA]** La asignacion de marca por coincidencia textual se centralizo y puede ser reutilizada por notebooks y futuros servicios.
- **[REQUIERE DECISION METODOLOGICA]** Se conserva el coeficiente de variacion con la desviacion estandar de pandas y la clasificacion de CV nulo como `Z`.
- **[REQUIERE VALIDACION CON EL NEGOCIO]** Las listas de marcas y el criterio de seleccionar solo productos `AX` deben confirmarse antes de convertirlos en configuracion productiva.
- **[REQUIERE DECISION METODOLOGICA]** El producto queda incluido en Pareto solo cuando el acumulado es `<= 80`, por lo que un salto que cruza el 80 % puede dejar fuera el siguiente producto. Se conserva esta regla actual.

### Pendientes

- Definir si los nombres de marca deben mantenerse como reglas de texto o provenir de un catalogo.
- Confirmar si la seleccion importada y nacional debe compartir los mismos umbrales.
- Extraer el preprocesamiento temporal del notebook `03_preprocesamiento.py`.

## Etapa 4: preprocesamiento temporal

### Cambios realizados

- Se creo `src/lead/data/temporal.py`.
- Se centralizo la creacion de `demanda_observada`.
- Se extrajeron las agregaciones semanales por columnas y por grupo.
- Se extrajo la deteccion de periodos continuos con demanda observada cero.
- Se extrajo la agrupacion de departamentos usada en el notebook.
- Se agregaron pruebas en `tests/test_temporal.py`.
- Los notebooks originales no fueron modificados.

### Funciones nuevas

- `prepare_temporal_frame()`
- `add_observed_demand()`
- `aggregate_weekly_demand()`
- `aggregate_weekly_by_group()`
- `find_zero_demand_periods()`
- `group_department()`

### Logica conservada

Se conserva la frecuencia semanal `W`, la suma de `Facturado` y `BackOrder`, la reindexacion diaria entre la primera y ultima fecha de cada producto y la salida con las columnas `Producto`, `Fecha_Inicio_Sin_Inventario` y `Fecha_Fin_Sin_Inventario`.

Se reemplazo `Series.append()` por `pd.concat()` y se corrigio la indexacion de la serie acolchada. Ambos cambios son tecnicos y necesarios para ejecutar la logica actual con pandas moderno.

### Clasificacion de problemas

- **[REFACTORIZACION TECNICA]** La deteccion original dependia de `Series.append()`, eliminado en versiones actuales de pandas.
- **[REFACTORIZACION TECNICA]** La demanda observada estaba duplicada entre etapas; ahora vive en `temporal.py`.
- **[REQUIERE DECISION METODOLOGICA]** El notebook llama periodos de demanda cero "sin inventario", aunque el dato solo demuestra ausencia de demanda observada.
- **[REQUIERE VALIDACION CON EL NEGOCIO]** Debe confirmarse si un dia sin `Facturado + BackOrder` representa realmente un quiebre, cierre operativo o ausencia de pedidos.
- **[REQUIERE VALIDACION CON EL NEGOCIO]** La agrupacion de departamentos conserva las reglas textuales de Bogotá, Cundinamarca y resto.

### Pendientes

- Definir una fuente operacional confiable para identificar quiebres.
- Separar formalmente demanda cero, ausencia de registros y falta de inventario.

## Etapa 5: preparación de series para forecasting

### Cambios realizados

- Se creo `src/lead/forecasting/series.py`.
- Se extrajo la agregacion semanal por producto con frecuencia `W-MON`.
- Se centralizaron `demanda_observada`, eventos comerciales, quiebres de inventario y precio rezagado.
- Se extrajo la separacion temporal de entrenamiento y prueba con seleccion de eventos variables.
- Se extrajo la estandarizacion del precio rezagado usando solo estadisticas de entrenamiento.
- Se extrajo la comparacion de variantes SARIMAX con y sin precio.
- Se agregaron pruebas en `tests/test_forecasting_series.py`.
- La ejecucion por producto y la imputacion SARIMAX permanecen pendientes para unidades posteriores.

### Logica conservada

Se mantienen la suma de `Facturado` y `BackOrder`, la interpolacion y relleno del precio, la exclusion de semanas 52 y 53 para marcar quiebres, la ventana de solapamiento de fechas y el requisito minimo de 70 semanas del notebook.

## Etapa 6: consolidación del dataset AX

**Fecha:** 2026-09-22

### Objetivo

Construir un dataset local con las ventas nacionales e importadas pertenecientes al universo AX definido por las selecciones existentes, conservando las variables originales e incorporando evidencia explícita de stockouts.

### Datasets de entrada

- `data/inputs/Dataset_Nacionales.csv`: 68.889 registros, 20 columnas efectivas, sin encabezado. Fechas entre 2026-01-01 y 2026-09-22.
- `data/inputs/Dataset_Importados.csv`: 48.033 registros, 20 columnas efectivas, sin encabezado. Fechas entre 2026-01-01 y 2026-09-22.
- `data/inputs/Stockout_productos.csv`: 157.054 intervalos, con `IDProductos`, `FechaInicial` y `FechaFinal`. Fechas entre 2024-01-02 y 2026-05-12.
- `data/outputs/productos_nacionales_AX.csv`: fuente de verdad de 30 productos AX nacionales.
- `data/outputs/productos_importados_AX.csv`: fuente de verdad de 20 productos AX importados.

Las fuentes de ventas llegaron como `Dataset_Nacionales.csv` y `Dataset_Importados.csv`, no como los nombres inicialmente propuestos en minúsculas. Se mantuvieron intactas y el script usa sus nombres reales.

### Clave y combinación

La identificación de producto utiliza `IDProducto`. El origen se conserva en `tipo_producto`, con valores `nacional` e `importado`. La clave temporal de integración es el producto y la fecha de transacción; el stockout se marca cuando `FECHA` cae dentro de `[FechaInicial, FechaFinal]`.

La información de ventas es transaccional y contiene `Semana`, pero el número de semana original se conserva sin usarlo como clave única. La convención definitiva deriva el período desde `FECHA`: lunes a domingo, con `semana_inicio` como fecha clave, `semana_fin` como límite inclusivo y `semana_calendario` en formato `AAAA-W##`.

### Implementación

- `src/lead/data/dataset_ax.py`: carga fuentes con o sin encabezado, obtiene IDs AX, filtra ventas, valida intervalos y marca stockouts sin duplicar filas ni imputar demanda.
- `scripts/build_dataset_ax.py`: ejecución reproducible desde la raíz del repositorio.
- `tests/test_dataset_ax.py`: prueba focalizada de filtrado, origen y marcado temporal.

### Artefacto generado

- `data/processed/dataset_ax.csv`
- Propósito: dataset local consolidado para la preparación posterior del modelado.
- Origen: datasets nacionales/importados, selecciones AX y stockouts.
- Método: concatenación de ventas, filtrado por `IDProducto`, adición de `tipo_producto` y marcado por solapamiento de fechas.
- Estructura: 116.922 registros y 27 columnas.
- Productos representados: 20 nacionales y 20 importados, 40 totales.
- Período: 2026-01-01 a 2026-09-22.
- Nombre definitivo: `dataset_ax` (`data/processed/dataset_ax.csv`).

### Stockouts

Se marcaron 2.750 registros de ventas y 40 productos tienen al menos un registro marcado. Los 411 intervalos de stockout que corresponden al universo AX se evaluaron contra las ventas disponibles. No se inventaron filas para períodos sin ventas y no se realizó imputación.

### Verificación

- No hay productos adicionales fuera del universo AX.
- Se excluyeron del universo final los 10 productos AX nacionales sin registros en la fuente recibida: `64`, `230`, `1585`, `3971`, `5425`, `6340`, `7027`, `7118`, `7119` y `7162`. No se generaron filas artificiales.
- No hay duplicados completos ni duplicados por `tipo_producto`, `FECHA`, `IDFactura`, `IDProducto`.
- No hay registros sin `IDProducto` ni sin `FECHA`.
- Las columnas `Facturado` y `BackOrder` se conservaron; no se corrigieron ni imputaron.
- El test focalizado `python -m unittest tests.test_dataset_ax -v` pasó.

### Git y decisiones pendientes

Se actualizaron las reglas de `.gitignore` para los nombres solicitados y los nombres reales recibidos, además de `data/processed/dataset_ax.csv`. Los datasets privados permanecen locales y no se hizo commit.

- La exclusión de los 10 productos nacionales sin ventas fue aprobada para esta etapa.
- La convención semanal lunes-domingo basada en `FECHA` fue aprobada.
- El nombre final aprobado es `dataset_ax`.
- El solapamiento inclusivo de fechas para stockouts fue validado por negocio.

### Estado

COMPLETADO CON OBSERVACIONES
