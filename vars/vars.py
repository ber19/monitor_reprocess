import string

## VARS PARA schedulingScraping
PATH_DRIVER = "C:\\Users\\mi11878\\chromedriver.exe"

selenium_driver = None

URL_EJECUCIONES  = "http://150.100.216.64:8080/scheduling/ejecucionesStatus"

UUAAS_ESTADO = {
    "dco": "MDCO%",
    "rig": "MRIG%",
    "ctk": "MCTK%",
    "ras": "MRAS%",
    "deo": "MDEO%",
    "alm": "MMALM%"
}

## VARS PARA GOOGLE SHEETS
    
VALUE_INPUT_OPTION = "USER_ENTERED"

COLUMNS = {
    "estado": [[
        "No.", "JOBNAME", "SCHEDTABLE", "APPLICATION", "SUB-APPLICATION", "RUN AS",
        "ORDER ID", "ODATE", "START TIME", "END TIME", "RUN TIME", "RUN COUNTER", "ENDED STATUS",
        "HOST", "CPUTIME"
    ]]
}

COLUMNS_MONITOR = [[
    "JOB", "Responsable","DESCRIPCION", "Persistencia Ctrl-M", "SubAplicativo", "Origen",
    "Periodicidad BUI 2.0", "Periodicidad Sofia", "Skynet", "Tipo", "Tabla Master", "Tabla Raw",
    "ESTATUS", "COMENTARIO", "Malla", "JobName", "Periodicidad", "Orden Ejecucion", "Campos Sensibles",
    "Tokenizada", "Mig-Nex-Art", "Fecha de aceptacion", "TIPO", "Entradas CdU", "Salidas CdU", 
    "Dependencia de Salida", "Insumos desde Legacy", "Modulo Legacy", "Tabla Delegada?", "Particion",
    "Ruta Master", "IDC", "#", "TAG", "Contacto origen", "Contacto Destino", "Link documentacion"
]]

COLUMNS_CANCELACIONES = [[
    "OrderId", "BEX", "UUAA", "MALLA", "SUBAPLICATIVO", "JOBNAME", "STATUS", "odate", "Fecha Cancelacion",
    "Delegado?", "TIPO JOB", "MES", "Tabla", "PERIODICIDAD", "ERROR", "SOLUCION TACTICA", "SOLUCION ESTRATEGICA",
    "ESTATUS", "FECHA ATENCION", "Registrado PIBEX?", "MOTIVO", "DESCRIPCION JOB"
]]

NOTOKS_OPTIONS = ["NOTOK"]

def columns_index():
    cols = []
    for letra0 in string.ascii_uppercase:
        cols.append(letra0)
    for letra1 in string.ascii_uppercase:
            for letra2 in string.ascii_uppercase:
                cols.append(letra1+letra2)
    return cols