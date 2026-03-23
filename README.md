# Random Fox and The Cat

Código que muestra como hacer una interfaz con Python a un par de APIs sencillas.

## Sobre el repositorio

Una interfaz en Python para obtener imágenes aleatorias de zorros y gatos desde las APIs de RandomFox y TheCat.
Este proyecto fue desarrollado inicialmente como una ayuda personal para un amigo, pero como ya pasaron varios años ahora está disponible para que cualquiera pueda disfrutar de una dosis diaria de ternura animal.

## Guía de configuración del proyecto

Siga estos pasos para configurar el entorno de desarrollo:

### Crear el entorno virtual

Dentro del directorio del repositorio

* Para Linux 

```bash
python -m venv prj
```

* Para Windows 

```bash
py -m venv prj
```

### Activar el entorno virtual

* Para Linux 

```bash
source ./prj/bin/activate
```

* Para Windows 

```bash
.\prj\Scripts\activate
```

### Instalar dependencias

* Para Linux

```bash
pip install -r requirements.txt
```

* Para Windows

```bash
py -m pip install -r requirements.txt
```

### Desactivar el entorno (cuando haya terminado)

```
deactivate
```

## Guía de instalación 

Siga estos pasos para instalar alguno de los dos paquetes:

### Crear el entorno virtual

Dentro del directorio del repositorio

* Para Linux 

```bash
python -m venv prj
```

* Para Windows 

```bash
py -m venv prj
```

### Activar el entorno virtual

* Para Linux 

```bash
source ./prj/bin/activate
```

* Para Windows 

```bash
.\prj\Scripts\activate
```

### Instalación de paquetes

* Para instalar `randomfox`

```bash
pip install git+https://github.com/stefano-sosa/random-fox-and-the-cat.git#subdirectory=random-fox-api
```


* Para instalar `thecat`

```bash
pip install git+https://github.com/stefano-sosa/random-fox-and-the-cat.git#subdirectory=the-cat-api
```

### Prueba local desde CLI

* Para probar `randomfox`:

```bash
python -c "from randomfox import RandomFoxAPI; fox = RandomFoxAPI(); fox.fetch_image(); print(fox.imgsize); fox.save_image(path='.')"
```

Debería observar una imagen llamada `test.jpg` en el directorio en el que ejecutó el comando.

* Para probar `thecat`:

```bash
python -c "from thecat import CatAPI; cat = CatAPI(); cat.fetch_images(limit=3); cat.download_images(); cat.save_image(0, path='.'); cat.create_collage(); cat.save_collage(path='.')"
```

Debería observar un mensaje parecido a `The Cat API 1.4.6` en la consola.

### Desactivar el entorno (cuando haya terminado)

```
deactivate
```

## Descargo de responsabilidad

Las imágenes en los cuadernos son resultados de las APIs y están publicadas como demostración del funcionamiento de la interfaz. No soy el propietario de estos archivos, ni de las API, ni reclamo derechos sobre ellos. Si eres el propietario del contenido y deseas que lo retire, por favor contacta conmigo.
