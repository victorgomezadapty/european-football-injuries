# Discusión: carga de lesiones registrada y disponibilidad del jugador

Esta discusión relaciona los resultados descriptivos del proyecto con doce publicaciones seleccionadas. La literatura aporta contexto y criterios metodológicos; no valida clínicamente el archivo de Kaggle. El [registro de búsqueda](literature_search.md) describe una búsqueda narrativa dirigida, no una revisión sistemática. La numeración coincide con el [registro de referencias](../references/references.json).

## 1. La unidad de observación determina la afirmación

El archivo contiene 15.603 registros, 4.081 nombres de jugadores y 276 etiquetas de ausencia. Incluye lesiones, enfermedad, cuarentena, estado físico y descanso. El recuento principal representa, por tanto, frecuencia de ausencias registradas. El consenso de fútbol distingue definición de lesión, recurrencia, gravedad y exposición: una tabla sin celdas vacías no demuestra que cumpla esas definiciones. [Fuller et al., 2006 [1]](https://doi.org/10.1136/bjsm.2005.025270)

La extensión específica de fútbol actualiza la nomenclatura y el registro de lesiones y enfermedades. Apoya conservar esas distinciones y dejar sin resolver las etiquetas sintomáticas vagas, en lugar de asignarles un diagnóstico tisular sin evidencia. La taxonomía propuesta facilita la revisión, pero no constituye una clasificación clínicamente validada. [Waldén et al., 2023 [3]](https://doi.org/10.1136/bjsports-2022-106405)

## 2. Las ausencias frecuentes y las costosas plantean preguntas diferentes

**Hamstring injury** es la etiqueta más frecuente: 1.256 registros, 52.483 días-episodio reportados y 8.534 partidos perdidos, sumados entre registros. **Cruciate ligament tear** aparece en 226 registros, pero acumula 56.768 días-episodio y una mediana de 230,5 días. Son resúmenes de etiquetas originales, no grupos diagnósticos verificados ni pronósticos individuales.

El enfoque de carga de Bahr y colaboradores justifica presentar consecuencias junto a frecuencia. La matriz del proyecto aplica esta idea de forma descriptiva. Recuento, duración y partidos perdidos permiten formular distintas preguntas de planificación; su eje de frecuencia no representa incidencia y las líneas de mediana no son umbrales clínicos. [Bahr et al., 2018 [4]](https://doi.org/10.1136/bjsports-2017-098160)

## 3. La importancia de los isquiotibiales tiene un contexto clínico relevante

La cohorte UEFA de 21 temporadas utilizó registros del personal médico y exposición individual. Documentó un aumento de la proporción de lesiones de isquiotibiales y de sus días de ausencia. Esto respalda la relevancia del tema, pero no equipara la proporción de una etiqueta de este archivo con las categorías clínicas o las tendencias ajustadas por exposición de aquella cohorte. [Ekstrand et al., 2023 [6]](https://doi.org/10.1136/bjsports-2021-105407)

Una cohorte médica anterior también identificó consecuencias importantes de las lesiones musculares y ausencias más prolongadas en recurrencias definidas clínicamente. Justifica conservar historiales, a la vez que muestra por qué repetir una etiqueta de texto aquí no confirma ese mismo desenlace clínico. [Ekstrand et al., 2011 [11]](https://doi.org/10.1177/0363546510395879)

Estos datos no demuestran una epidemia, un mecanismo de carga de entrenamiento ni un cambio en la incidencia.

## 4. La visibilidad pública es selectiva

Krutsch y colaboradores contrastaron datos de medios con médicos de equipos y encontraron diagnósticos incorrectos y lesiones ausentes del registro público, con mayor concordancia en algunos tipos graves. La visibilidad y la validez diagnóstica pueden variar según la lesión; sus resultados no son un factor universal de corrección para este archivo. [Krutsch et al., 2020 [7]](https://doi.org/10.2147/OAJSM.S251081)

Hoenig y colaboradores observaron menor registro de lesiones y una proporción mayor de lesiones graves en un archivo extenso de Transfermarkt frente a otras fuentes. Un conjunto público grande no es necesariamente representativo. La verificación médica y la cadena de procedencia de esta versión de Kaggle no se han establecido independientemente: la comparación es pertinente, pero no demuestra errores idénticos. [Hoenig et al., 2022 [8]](https://doi.org/10.1016/j.jsams.2021.11.038)

La vigilancia mediante medios puede ser útil con procedimientos definidos. Aus der Fünten y colaboradores aplicaron un protocolo prospectivo con varias fuentes, reconociendo dificultades para precisar diagnósticos de lesiones menores. Descargar un archivo no reproduce ese protocolo ni su construcción de exposición. [Aus der Fünten et al., 2023 [9]](https://doi.org/10.1186/s40798-023-00563-x)

La ausencia de celdas vacías solo describe los registros incluidos; no demuestra cobertura de todas las lesiones, jugadores elegibles o diagnósticos correctos.

## 5. Los intervalos repetidos afectan a los totales

La suma principal alcanza **563.314 días-episodio** y **85.928 partidos perdidos**. No se detectaron duplicados exactos de fila completa, pero 1.973 filas comparten identificador provisional por nombre, etiqueta normalizada y fechas con otra fila. Las diferencias de club u otro contexto impiden eliminar automáticamente todos esos intervalos coincidentes.

El escenario de sensibilidad que colapsa candidatos conserva 14.611 registros y produce 532.422 días-episodio y 81.226 partidos: reducciones aproximadas del 5,48 % y del 5,47 %. Conserva la primera fila de cada clave completa, sin determinar cuál es el club correcto. Publicar ambas vistas permite evaluar ese supuesto.

La unión de intervalos inclusivos evita contar dos veces una fecha dentro de un nombre, pero no confirma un historial completo de ausencia. Traspasos, homónimos y partidos de distintas competiciones siguen requiriendo verificación.

## 6. La disponibilidad necesita denominador

Hägglund y colaboradores observaron asociaciones entre menor carga de lesión, mayor disponibilidad para partidos y mejor rendimiento colectivo en una cohorte prospectiva. Explica la relevancia de estudiar disponibilidad, pero no establece causalidad ni demuestra un efecto sobre resultados deportivos en este archivo. [Hägglund et al., 2013 [5]](https://doi.org/10.1136/bjsports-2013-092215)

Los **perfiles de carga de disponibilidad registrada** de este proyecto resumen consecuencias documentadas. Un porcentaje real de disponibilidad requiere además partidos o días elegibles, periodos de inscripción y estados de ausencia completos. La incidencia exige exposición apropiada. El consenso del COI explica por qué denominadores y consecuencias deben corresponder a la pregunta; el periodo entre primera y última lesión no sustituye esa información. [Bahr et al., 2020 [2]](https://doi.org/10.1136/bjsports-2019-101969)

## 7. Una fecha final no equivale a autorización médica

Todas las duraciones reportadas equivalen a la diferencia de fechas más un día. Conservar esta convención inclusiva verifica la aritmética, pero no el significado clínico ni su equivalencia con días de ausencia estandarizados. Los retornos de cero días y la definición de participación plena requieren el protocolo de origen.

El consenso sobre retorno al deporte distingue progresión por participación, deporte y rendimiento, mediante decisiones compartidas y multifactoriales. El final de un intervalo no aporta esas evaluaciones. [Ardern et al., 2016 [10]](https://doi.org/10.1136/bjsports-2016-096278)

Por ello, las etiquetas posteriores a un intervalo se describen como repeticiones registradas, no como recaídas confirmadas. Modelar recuperación exigiría verificar primero desenlace, observación y censura.

## 8. El calendario genera preguntas

El gráfico mensual cuenta inicios registrados y asigna toda la carga de un episodio al mes de inicio. No distribuye las fechas de ausencia entre meses ni identifica efectos de entrenamiento.

Un subanálisis UEFA con exposición no encontró un cambio global importante en incidencia durante la temporada del Mundial 2022/23 frente a su comparación histórica, con matices según contexto. Ilustra que un calendario inusual no establece por sí mismo causalidad; tampoco demuestra que la congestión sea inocua en todos los entornos. [Bengtsson et al., 2025 [12]](https://doi.org/10.1136/bmjsem-2025-002772)

## 9. Aportación del proyecto

La capa reproducible permite explorar composición de ausencias, duraciones largas, historiales solapados y sensibilidad a episodios repetidos. Sirve para revisar fuentes y formular preguntas sobre recursos; no selecciona tratamientos, autoriza retornos ni predice lesiones futuras. Las prioridades son verificar identidades y episodios, validar taxonomía y desenlaces y obtener inscripción, elegibilidad y exposición completas. Un modelo posterior al inicio debe excluir resultados futuros y totales calculados con todo el historial.

Las cifras propias proceden de `reports/dataset_summary.json` y las tablas de carga y sensibilidad. La fuente, atribuida por separado, es el dataset de Kaggle de Sanan Muzaffarov. Cada afirmación externa incluye enlace. No se reproducen figuras, tablas, resúmenes completos ni citas extensas de las publicaciones.
