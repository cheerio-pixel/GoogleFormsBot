
# Sin la API de Google
Los scripts esenciales para esto son los de `forms_scrapper.py` y
`responses_processor.py` y la entrada principal es el segundo de estos.

Antes de usar estos debes de descargar el documento que guarda las
respuestas ya sea desde el Google Spreadsheet o desde el forms. Lo
importante es que este sea en formato de csv y que los titulos de los
headers no sean modificados.

Despues de descargarlos, en donde esta la constante TEST_FILE
sustituyes la string con el camino de tu archivo csv.
NOTA: El camino que pongas es relativo a desde donde estas ejecutando
el script (El directorio donde estas en la terminal).

Lo siguiente es sustituir la variable `view_form_id` con el id del
forms en vista. Uno lo puede encontrar en el link completo que uno
manda para que llenen. Ejemplo:
"https://docs.google.com/forms/d/e/{view_form_id}/viewform"

Una vez configurado esto, solo necesitas correr el script y configurar
la ultima linea, la cual es la que ejecuta la funcion
