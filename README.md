# Automatización: Seguro Vida Ley (Altas/Bajas)

## Descripción:

Este bot se encargará de registrar trabajadores y a cada beneficiario por cada trabajador en el sistema de Seguros Vida Ley. Así también se encarga de dar de baja a los trabajadores que se especifiquen. Funciona con un webdriver que se encarga de realizar acciones en el navegador para realizar los 2 procesos mencionados de forma automática y procedural.

## Estructura:

Código del bot en la carpeta scripts.

Carpeta SHARED-REGS es para el uso único del bot, solo se guardan archivos intermedios a partir de los datos de entrada y los logs.

El script principal es start.py, solo recibe como único argumento la ruta al archivo "auth.json" (no necesariamente debe tener ese nombre pero debe seguir la estructura de "test/auth-template.json"). Este archivo de código se encarga de ejecutar el resto de scripts del bot para que funcione todo en la siguiente secuencia:

- Preprocesar la entrada principal (excel con los datos de los trabajadores y beneficiarios).
  > Genera archivos intermedios CSV para que el bot interactúe cómodamente. En caso de cambiar de medio de entrada, solo se debe configurar este paso y que devuelva la misma salida.

- Ejecución del bot con los archivos CSV intermedios para dar de alta a trabajadores y sus beneficiarios indicados en la entrada.
  > Genera la trazabilidad para el archivo de salida de los trabajadores y beneficiarios registrados.
- Cierre de sesión y reingreso para la ejecución del bot con los archivos CSV intermedios para dar de baja a los trabajadores indicados en la entrada.
  > Genera la trazabilidad para el archivo de salida de los trabajadores cesados.
  > Genera el archivo de salida que se especifica en auth.json.

### Requisitos:

- Tener instalado un webdriver (Edge, Chrome, Firefox o Safari).
- Tener conexión a internet.
- Instalar python>=3.12 y pip 24.0.
- Instalar las librerías especificadas en el archivo "requirements.txt":
  - selenium: Para poder realizar acciones en el navegador.
  - pandas: Para manejar datos ordenados en tablas.

### Ejecución:
El bot no requiere instalación, solo clonar este repositorio y proceder con la ejecución:
+ El comando de ejecución del bot:

  ```python start.py -r "PATH/TO/AUTH.JSON"```

+ El comando para generar una plantilla del archivo de configuración:

  ```python start.py -t "PATH/TO/AUTH.JSON"```

⚠️ Se debe asegurar que auth.json existe y la dirección otorgada es correcta. 

## Archivo de configuración del usuario

Dado que hay argumentos para el bot que se desconocen desde un inicio o pueden cambiar con el tiempo, se usa un archivo JSON que contenga estos argumentos. Este archivo es editable en todo momento mientras el bot no se está ejecutando. A continuación se muestra los campos que acepta este archivo:
+ "url": El URL de la página de login para realizar registros del Seguro Vida Ley. 
+ "webdriver": Campo del webdriver que cargará Selenium.
  + "browser": El webdriver ya instalado que usará el bot ("edge","chrome", "firefox", "safari").
  + "headless": **true** si no se quiere visualizar el navegador en pantalla, sino **false**.
+ "login": Credenciales de la empresa/empleador para el inicio de sesión.
  + "ruc": Los dígitos del RUC de la empresa/empleador.
  + "user": Nombre de usuario de la empresa/empleador.
  + "password": Contraseña de la empresa/empleador.
+ "svl": Campo de datos que solo se refieren al Seguro Vida Ley.
  + "insurance date": La fecha de aseguramiento para registrarlo junto al trabajador. Si este campo es nulo, se considerará como fecha de aseguramiento a la fecha de inicio mostrada en la página de registro de trabajador. El formato es "dd/mm/Y".
  + "insurance salary": El monto del seguro que se asigna a todos por igual en soles. El tipo es INT.
+ "notifications": Campo referido a métodos de entrada y salida del bot.
  + "file io": Configuración para la entrada/salida del bot para archivos.
    + "input": Campo de la entrada.
      + "active": **true** si se quiere usar este medio como entrada del bot, sino **false**.
      + "path": Dirección al archivo que será usado como entrada para el bot.
    + "output": Campo de la salida.
      + "active": **true** si se quiere usar este medio como salida del bot, sino **false**.
      + "path": Dirección al archivo donde se quiere colocar el registro de seguimiento de las operaciones realizadas y las que no pudo realizar el bot.

## Formato de entrada

Para esta versión del bot, la entrada para el programa es un archivo excel 'xlsx'. Este archivo debe contener 2 hojas: Ingresos y Ceses. A continuación se muestra que columnas debe contener cada hoja y el tipo de dato de cada columna (es importante considerar el orden de las columnas como se presentan en este caso ya que el nombre de las columnas no importa).
1. La hoja de "Ingresos" debe contener las siguientes columnas:
    + Tipo de documento del trabajador: STRING (DNI, CEX, PP, CSRF, PTP, CPTP)
    + Número de documento del trabajador: STRING
    + Tipo de documento del beneficiario: STRING (DNI, CEX, PP, CSRF, PTP, CPTP)
    + Número de documento del beneficiario: STRING
    + Apellido paterno: STRING
    + Apellido materno: STRING
    + Nombres: STRING (separado por espacio si son 2 nombres)
    + Fecha de nacimiento: DATETIME (no importa el formato)
    + Dirección: STRING
    + Departamento: STRING
    + Provincia: STRING
    + Distrito: STRING
    + Sexo: STRING (Masculino - Femenino)
    + Vínculo familiar: INT (66, 69, 71, 91)
2. La hoja de "Ceses" debe contar con las siguientes columnas:
    + Tipo de documento del trabajador: STRING
    + Número de documento del trabajador: STRING
    + Motivo: STRING (debe coincidir en lo posible con el listado de opciones presentes en la página de ceses)
    + Fecha de baja: DATETIME (no importa el formato)

## Carpeta "scripts/"

- constants.py contiene todas las variables constantes ajustadas a la página web objetivo.

- bot_step1.py es el script temporal que procesa la información de entrada para retornar los archivos intermedios que bot_step2.py usará.

- bot_step2.py es el script del bot que corresponde al código del bot para altas y bajas en la secuencia correspondiente.

## Script "bot_step2.py"

### Variables Globales

- **`emp_registered_out`**: Lista para almacenar información sobre los trabajadors registrados. Contiene las siguientes columnas:
  - Documento
  - Número de beneficiados
  - Registrado (Sí/No)
  - Motivo

- **`ben_registered_out`**: Lista para almacenar información sobre los beneficiarios registrados. Contiene las siguientes columnas:
  - Trabajador
  - Documento
  - Registrado (Sí/No)
  - Motivo

- **`emp_terminated_out`**: Lista para almacenar información sobre los trabajadors dados de baja. Contiene las siguientes columnas:
  - Documento
  - Cesado (Sí/No)
  - Motivo

### Funciones

#### `yesno(val: bool) -> str`
Convierte un valor booleano en una cadena que representa 'Sí' o 'No'.
- **Parámetros**:
  - `val` (bool): Valor booleano a convertir.
- **Retorno**: Cadena ('Sí' o 'No').

#### `format_document(doc_n, doc_t) -> str`
Formatea el número de documento con ceros a la izquierda según el tipo de documento.
- **Parámetros**:
  - `doc_n`: Número de documento.
  - `doc_t`: Tipo de documento.
- **Retorno**: Cadena con el número de documento formateado.

#### `fdevinfo(msg: str, max_length: int = 50, padding: str = '*') -> str`
Imprime un mensaje con relleno a los lados para formatear la salida en los logs.
- **Parámetros**:
  - `msg` (str): Mensaje a formatear.
  - `max_length` (int): Longitud máxima del mensaje formateado.
  - `padding` (str): Carácter de relleno.
- **Retorno**: Mensaje formateado.

#### `emp_registered_log(emp, bens, registered, reason)`
Registra la información de alta de un trabajador en los logs y actualiza `emp_registered_out`.
- **Parámetros**:
  - `emp`: Información del trabajador.
  - `bens`: Beneficiarios asociados.
  - `registered` (bool): Indica si el trabajador fue registrado.
  - `reason` (str): Motivo del registro.

#### `ben_registered_log(emp, ben, registered, reason)`
Registra la información de alta de un beneficiario en los logs y actualiza `ben_registered_out`.
- **Parámetros**:
  - `emp`: Información del trabajador.
  - `ben`: Información del beneficiario.
  - `registered` (bool): Indica si el beneficiario fue registrado.
  - `reason` (str): Motivo del registro.

#### `terminated_log(emp, terminated, reason)`
Registra la información de baja de un trabajador en los logs y actualiza `emp_terminated_out`.
- **Parámetros**:
  - `emp`: Información del trabajador.
  - `terminated` (bool): Indica si el trabajador fue dado de baja.
  - `reason` (str): Motivo de la baja.

#### `click_newest_insurance(self, xpath)`
Selecciona el seguro más reciente basado en la fecha de inicio desde una tabla.
- **Parámetros**:
  - `xpath` (str): Ruta XPath del elemento de la tabla.
- **Retorno**: Ninguno.

#### `send_doc_by_type(self, xpath_t, xpath_n, doc_t, doc_n, enter=True)`
Envía el documento a RENIEC con la longitud adecuada para el tipo de documento, opcionalmente presionando la tecla Enter.
- **Parámetros**:
  - `xpath_t` (str): Ruta XPath del campo de tipo de documento.
  - `xpath_n` (str): Ruta XPath del campo del número de documento.
  - `doc_t`: Tipo de documento.
  - `doc_n`: Número de documento.
  - `enter` (bool): Indica si se debe presionar la tecla Enter (predeterminado: True).

#### `closest_match_from_element(self, xpath: str, to_match: str, bias=0.8)`
Selecciona el elemento más cercano en una lista de opciones basado en el texto dado usando la función difflib.get_close_matches.
- **Parámetros**:
  - `xpath` (str): Ruta XPath del elemento de selección.
  - `to_match` (str): Texto para comparar.
  - `bias` (float): Umbral de similitud (predeterminado: 0.8).
- **Retorno**: Ninguno.

#### `employee_is_already_registered(driver: w3auto.WebDriverExtended, doc_n, doc_t) -> bool`
Verifica si un trabajador ya está registrado basado en su documento.
- **Parámetros**:
  - `driver`: Instancia del controlador web extendido.
  - `doc_n`: Número de documento.
  - `doc_t`: Tipo de documento.
- **Proceso**:
  - Se ingresa el documento del trabajador, por ende aparecería la opción de registrar beneficiarios al presionar el elemento con el símbolo de una lupa en el navegador.
  - Se obtiene la tabla que contendría una única fila.
  - En el caso de que la única fila esté vacía significa que el trabajador no esta registrado.
  - También puede darse el caso de que la única fila obtenida tenga el aspecto de que el trabajador ya fue cesado anteriomente.
  - Caso contrario a los mencionados, el trabajador si está registrado.
- **Retorno**: `True` si el trabajador está registrado, `False` en caso contrario.

#### `from_login2update_revenue_insurance(driver: w3auto.WebDriverExtended, auth, emps, bens=None, old_ins=None)`
Gestiona la transición del inicio de sesión a la actualización de seguros de ingresos.
- **Parámetros**:
  - `driver`: Instancia del controlador web extendido.
  - `auth`: Información de autenticación.
  - `emps`: Datos de trabajadors.
  - `bens` (opcional): Datos de beneficiarios.
  - `old_ins` (opcional): Seguros antiguos.
- **Proceso**:
  - **Inicialización**:
     - Se establece una bandera (`flag`) en `True` para manejar posibles reintentos en caso de fallos.
     - Los trabajadors se agregan a una cola (`deque`) para procesarlos uno a uno.

  - **Inicio de Sesión**:
     - Navega a la URL especificada en `auth[AUTH_URL]`.
     - Introduce las credenciales (`RUC`, `Usuario`, `Contraseña`).
     - Hace clic en el botón de inicio de sesión.
     - Accede a la sección de seguros seleccionando la opción adecuada.

  - **Actualización de Seguros**:
     - Dependiendo del valor de `register_mode`:
       - **Modo de Registro (`register_mode=True`)**:
         - Procesa cada trabajador en la cola.
         - Obtiene los beneficiarios asociados y llama a `sign_up_employee` para registrarlos.
       - **Modo de Terminación (`register_mode=False`)**:
         - Procesa cada trabajador en la cola.
         - Llama a `terminate_employee` para dar de baja al trabajador.
- **Retorno**: Ninguno.

#### `sign_up_employee(driver: w3auto.WebDriverExtended, auth, emp, bens)`
Registra un nuevo trabajador en el sistema.
- **Parámetros**:
  - `driver`: Instancia del controlador web extendido.
  - `auth`: Información de autenticación.
  - `emp`: Datos del trabajador a registrar.
  - `bens`: Datos de beneficiarios asociados.
- **Proceso**:
  - Envía el tipo y número de documento del trabajador.
  - Si el documento no es aceptado, se registra el error y se finaliza.
  - Completa la información de ingreso del trabajador y los datos de la póliza.
  - Guarda los datos del trabajador.
  - Dado que el mensaje puede dar la alerta de que el trabajador ya se encontraba registrado, se debe aceptar dicha alerta.
  - Registra el trabajador y busca sus beneficiarios asociados.
- **Retorno**: Llama a `search_beneficier_by_doc`.

#### `search_beneficier_by_doc(driver: w3auto.WebDriverExtended, auth, emp, bens)`
Busca y registra beneficiarios asociados al trabajador.
- **Parámetros**:
  - `driver`: Instancia del controlador web extendido.
  - `auth`: Información de autenticación.
  - `emp`: Datos del trabajador.
  - `bens`: Datos de los beneficiarios a registrar.
- **Proceso**:
  - Verifica si el trabajador ya está registrado.
  - Si es así, procede a registrar los beneficiarios.
- **Retorno**: Llama a `close_beneficier_page`.

#### `is_adult_question(driver: w3auto.WebDriverExtended, auth, emp, ben) -> bool`
Determina si un beneficiario es adulto y decide el método de registro adecuado.
- **Parámetros**:
  - `driver`: Instancia del controlador web extendido.
  - `auth`: Información de autenticación.
  - `emp`: Datos del trabajador.
  - `ben`: Datos del beneficiario.
- **Retorno**: `True` si el beneficiario es adulto, `False` si es menor de edad. Llama a `insert_just_doc` o `insert_full_form` respectivamente.

#### `insert_just_doc(driver: w3auto.WebDriverExtended, auth, emp, ben) -> bool`
Registra a un beneficiario adulto utilizando solo el documento.
- **Parámetros**:
  - `driver`: Instancia del controlador web extendido.
  - `auth`: Información de autenticación.
  - `emp`: Datos del trabajador.
  - `ben`: Datos del beneficiario.
- **Retorno**: `True` si el registro es exitoso, `False` si no se encuentra el beneficiario. Llama a `save_beneficier_data`.

#### `insert_full_form(driver: w3auto.WebDriverExtended, auth, emp, ben) -> bool`
Registra a un beneficiario menor de edad con información completa.
- **Parámetros**:
  - `driver`: Instancia del controlador web extendido.
  - `auth`: Información de autenticación.
  - `emp`: Datos del trabajador.
  - `ben`: Datos del beneficiario.
- **Retorno**: `True` si el registro es exitoso, `False` en caso de errores. Llama a `save_beneficier_data`.

#### `save_beneficier_data(driver: w3auto.WebDriverExtended, auth, emp, ben) -> bool`
Guarda los datos del beneficiario y confirma la operación.
- **Parámetros**:
  - `driver`: Instancia del controlador web extendido.
  - `auth`: Información de autenticación.
  - `emp`: Datos del trabajador.
  - `ben`: Datos del beneficiario.
- **Retorno**: `True` si el guardado es exitoso, `False` en caso contrario.

#### `close_beneficier_page(driver: w3auto.WebDriverExtended, auth, emp, ben)`
Cierra la página de registro de beneficiarios y regresa a la página anterior.
- **Parámetros**:
  - `driver`: Instancia del controlador web extendido.
  - `auth`: Información de autenticación.
  - `emp`: Datos del trabajador.
  - `ben`: Datos del beneficiario.
- **Retorno**: Ninguno.

#### `terminate_employee(driver: w3auto.WebDriverExtended, auth, temp)`
Registra la baja de un trabajador en el sistema.
- **Parámetros**:
  - `driver`: Instancia del controlador web extendido.
  - `auth`: Información de autenticación.
  - `temp`: Datos del trabajador a dar de baja.
- **Proceso**:
  - Verifica si el trabajador está registrado.
  - Si está registrado, procede a registrar la baja.
- **Retorno**: Llama a `terminated_log` pero no devuelve nada.