# TP Sistemas Distribuidos I - 1C 2025

## Integrantes

| Nombre                     | Padrón |
|----------------------------|--------|
| Victor Manuel Bravo Arroyo | 98882  |
| Adrian Leandro Re          | 105025 |


## Descripción 

El siguiente repositorio contiene los archivos fuentes del TP de Sistemas Distribuidos I - 1C 2025 

## Como correr el proyecto

Tenemos los pasos
1. Descargaremos el set de datos: Peliculas, ratings y creditos
2. Establecer la arquitectura del sistema: ¿Cuantos nodos de filtros, joiners, selectors vamos a tener? 
3. Correr el docker compose: Levantamos el sistema y corremos!
4. Tolerancia a fallos: Demos de bajas algunos nodos y veamos como responde el sistema
5. Extra: Archivos de prueba

### Descarga del set de datos

Ejecturando el comando a continuación, descargaremos los archivos de kaggle en `./data` y serán descomprimidos

```sh
make download-dataset 
```
Y ser verá en el terminal como
```sh
Archive:  ./data/the-movies-dataset.zip
  inflating: ./data/credits.csv      
  inflating: ./data/keywords.csv     
  inflating: ./data/links.csv      
```


### Arquitectura

El archivo `/dockerize/config.yml` contiene la cantidad de nodos para cada servicio. Por ejemplo:

```yaml
average_ratio: 2
client: 3
contains_country_ar: 2
contains_country_es: 2
creditdispatcher: 2
...
```

Donde el primer campo es el nombre del servicio y el segundo la cantidad de nodos.
Una vez establecida correr en la raiz 

```sh
$ make compose
```
Que creará (o sobrescribirá) nuestro `compose.yml` similar a

```yaml
services:
  average_ratio_0:
    container_name: average_ratio_0
    depends_on:
      mom:
        condition: service_healthy
    entrypoint: ./main
```

### Levantar con docker

Necesitaremos construir las imagenes y luego correrlas. Ambos se puede realizar con 

```sh
make docker-compose-up 
```

Una vez terminado, los archivos de resultado podrán ser encontrados en `./data`. Por ejemplo: 

```sh
data/1-cdd07d2c-e3bd-4640-bcb6-d632e8dd6e8d.csv
data/2-cdd07d2c-e3bd-4640-bcb6-d632e8dd6e8d.csv
data/3-cdd07d2c-e3bd-4640-bcb6-d632e8dd6e8d.csv
data/4-cdd07d2c-e3bd-4640-bcb6-d632e8dd6e8d.csv
data/5-cdd07d2c-e3bd-4640-bcb6-d632e8dd6e8d.csv
```
Donde el primer digito indica el resultado de la query y el resto el ID asignado al usuario. 
Este es dado al azar en cada ejecución.

### Tolerancia a fallos

Primero, reiniciaremos el sistema con 

```sh
make reboot
```

Esto eliminará los archivos de resultados de `./data` y los estados de cada nodo en `./state`.
Una vez corriendo, podremos dar de baja un servicio como

```sh
docker compose kill ratingselector_0
```
O matandolo desde Docker Desktop.


Si esperamos unos segundos, veremos como los `health_checkers` lo revivirán, a menos que sean los clientes o sentimentanalyzer.


### Extra: Archivos de prueba

En el archivo `./configs/configs.yml` veremos algunas configuración tales como 

```yaml
client:
  credits: data/credits.csv
  movies: data/movies_metadata.csv
  ratings: data/ratings.csv-sample
  batchSize: 1000
```

Que indican de donde tomaremos los datos y el tamaño del BatchSize (cuantos registros hay en un mensaje).
Cambiando la ruta, cambiará el dataset tomado.  Luego, basta con `make reboot` para volver a correr. 

Otra opción es correr nuestro creador de archivos de prueba

```sh
make sample-all n=1000
```
Donde `n` es la cantidad de registros. 
Esto genera tres archivos 

```sh
./data/credits.csv-1000
./data/movies_metadata.csv-1000
./data/ratings.csv-1000
```
Y podemos modificar nuestro `./configs/configs.yml` para que tome alguno de ellos. Tal como:

```yaml
client:
  ratings: data/ratings.csv-1000
```


