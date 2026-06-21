# TuVino - API REST

Cuando se inicia el proyecto de `Docker Compose`, estas son las URLs:

*   Documentación y endpoints $\rightarrow$ `http://localhost:8000/docs`

## Comandos para correr la aplicación

1.  Copiar el archivo `.env.example` a un archivo `.env`:
    ```shell
    cp .env.example .env
    ```

2.  Modificar el archivo `.env` según tus preferencias.

3.  Buildear e inicia los contenedores:
    ```shell
    make docker-compose-up
    ```

4.  Para ver los logs de los contenedores mientras el proyecto está en ejecución, ejecutar:
    ```shell
    make docker-compose-logs
    ```

5.  Ejecuta este comando para correr la suite de tests de la aplicación:
    ```shell
    make test
    ```

6.  Cuando hayas terminado de ejecutar el proyecto, puedes usar este comando para detener los contenedores:
    ```shell
    make docker-compose-down
    ```

7.  A medida que crees/modifiques modelos, debes ejecutar este comando para crear migraciones de base de datos y aplicarlas:
    ```shell
    make create-migration MESSAGE="tu_mensaje_de_migración"
    ```

8.  Si simplemente queres migrar la base de datos a la última version creada, debes ejecutar:
    ```shell
    make upgrade
    ```

9.  Para volver a una versión determinada, buscar el hash de la misma ejecutar:
    ```shell
    make downgrade VERSION="hash"
    ```

10.  Para reiniciar todos los contenedores y empezar de cero, debes ejecutar:
    ```shell
    make restart
    ```
    ADVERTENCIA: Se perderán todos los datos.
