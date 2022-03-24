import pandas as pd

data_estado = {
    "dco": None,
    "rig": None,
    "ctk": None,
    "ras": None,
    "deo": None,
    "alm": None
}

###############################################################

dfs_estado = {
    "dco": None,
    "rig": None,
    "ctk": None,
    "ras": None,
    "deo": None,
    "alm": None
}

meses = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre"
}
periodicidad = {
    "DIA" : "DIARIA",
    "MEN" : "MENSUAL",
    "SEM" : "SEMANAL"
}
def get_per(per):
    if per in periodicidad.keys():
        return periodicidad[per]
    else: return ""


data_monitor = None
df_monitor = None

data_monitor_p = None
df_monitor_p = None

####
spreadsheet_dict = None
sheets_id = {}
####
###############################
jobs_estado = pd.DataFrame()
days_ejec = set()
ejec_by_day = {}

days_monitor = None
days_monitor_p = None
################################
days_values = None
days_values_p = None
################################
total_not_oks = pd.DataFrame()
notoks = pd.DataFrame()
delegated_notoks = pd.DataFrame()

data_sheet_cancelaciones = None
df_sheet_cancelaciones = None