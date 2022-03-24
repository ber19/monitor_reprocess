from googleapiclient.discovery import build
from sheets_auth.sheets_autorization import autentication
from googleapiclient.errors import HttpError
import vars.vars as vars
import vars.spreadsheets_reqs as srqsts
from datos.dates import today, now
from datos import datos
from dateutil.relativedelta import relativedelta


class Services:
    def __init__(self, spreadsheet_id):
        self.spreadsheet_id = spreadsheet_id
        self.service = build("sheets", "v4", credentials=autentication())

    def get_spreadsheet(self):
        spreadsheet_dict = self.service.spreadsheets()\
            .get(spreadsheetId=self.spreadsheet_id).execute()
        datos.spreadsheet_dict = spreadsheet_dict
    
    def check_sheet_monitor(self):
        sheets = datos.spreadsheet_dict["sheets"]
        sheets_names = []
        for sheet in sheets:
            sheets_names.append(sheet["properties"]["title"])
        if "Calendario Ejec " + today.strftime("%Y%m") in sheets_names and \
            "Calendario Ejec " + ((today - relativedelta(months=1)).strftime("%Y%m")) in sheets_names:
            self.get_sheet_monitor()
            self.get_sheet_monitor_p()     #############
            return True
        else:
            print("\n- Deben existir dos hoja con nombres:\n" +\
                "Calendario Ejec {}\n".format(today.strftime("%Y%m")) +\
                "Calendario Ejec {}\n".format((today - relativedelta(months=1)).strftime("%Y%m")) +\
                "- Asegurese de que el nombre de las hoja no tenga espacios en blanco de más\n" +\
                "- *DE QUE TENGAN EL FORMATO (COLUMNAS) NECESARIO*\n" +\
                "- *QUE SUS DATOS (DELEGACIONES) ESTEN AL CORRIENTE*\n")
            input("- Esperando la hoja...\n(Enter para volver a intentarlo)\n")
            set_spreadsheet()
            self.check_sheet_monitor()

    def check_sheet_cancelados(self):
        sheets = datos.spreadsheet_dict["sheets"]
        sheets_names = []
        for sheet in sheets:
            sheets_names.append(sheet["properties"]["title"])
        if "CANCELACIONES RIESGOS" in sheets_names:
            return True
        else:
            print("\n- La hoja de cancelaciones no existe\n" +\
                    "- Debe existir una hoja con nombre:\n" +\
                    "CANCELACIONES RIESGOS\n" +\
                    "- Asegurese de que el nombre de la hoja no tenga espacios en blanco de más\n"
                    "- ASEGURESE DE QUE TENGA EL FORMATO (COLUMNAS) NECESARIO\n")
            input("- Esperando la hoja...\n(Enter para volver a intentarlo)\n")
            set_spreadsheet()
            self.check_sheet_cancelados()

    def get_sheet_monitor(self):
        res = self.service.spreadsheets().values().get(
            spreadsheetId = self.spreadsheet_id,
            range = "Calendario Ejec {}!B4:AL".format(
                today.strftime("%Y%m")
            )
        ).execute()
        datos.data_monitor = res["values"]
        
    def get_sheet_monitor_p(self):
        res = self.service.spreadsheets().values().get(
            spreadsheetId = self.spreadsheet_id,
            range = "Calendario Ejec {}!B4:AL".format(
                (today - relativedelta(months=1)).strftime("%Y%m")
            )
        ).execute()
        datos.data_monitor_p = res["values"]

    def set_sheets_id_dict(self):
        sheets = datos.spreadsheet_dict["sheets"]
        for sheet in sheets:
            datos.sheets_id[sheet["properties"]["title"]] = sheet["properties"]["sheetId"]
    
    def set_datetime_ejec(self):
        res = self.service.spreadsheets().values().batchUpdate(
            spreadsheetId = self.spreadsheet_id,
            body = srqsts.set_datetime_ejec(now)
        ).execute()
        flag1 = False
        # print(datos.ejec_by_day.keys()) ### Para poder ver los dias y su mes que se van a actualizar
        for m, day in datos.ejec_by_day.keys():
            if m == "p": flag1 = True
        if flag1: 
            res1 = self.service.spreadsheets().values().batchUpdate(
                spreadsheetId = self.spreadsheet_id,
                body = srqsts.set_datetime_ejec(
                    now - relativedelta(months=1)
                )
            ).execute()

    def get_days_monitor(self):
        res = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id, 
            range="Calendario Ejec {}!A2:BV2".format(
                today.strftime("%Y%m")
            )).execute()
        comienzo_fechas = 0
        for val in res["values"][0]:
            comienzo_fechas += 1
            if val[:2].isnumeric(): break
        cols = zip(
            [int(fecha[:2]) for fecha in res["values"][0][comienzo_fechas-1:] if fecha[:2].isnumeric()],
            [i_col for i_col in vars.columns_index()[comienzo_fechas-1:]]
        )
        datos.days_monitor = dict(cols)

    def get_days_monitor_p(self):
        res = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id, 
            range="Calendario Ejec {}!A2:BV2".format(
                (today - relativedelta(months=1)).strftime("%Y%m")
            )).execute()
        comienzo_fechas = 0
        for val in res["values"][0]:
            comienzo_fechas += 1
            if val[:2].isnumeric(): break
        cols = zip(
            [int(fecha[:2]) for fecha in res["values"][0][comienzo_fechas-1:] if fecha[:2].isnumeric()],
            [i_col for i_col in vars.columns_index()[comienzo_fechas-1:]]
        )
        datos.days_monitor_p = dict(cols)

    def get_vals_cal(self):
        l_days_monitor = list(datos.days_monitor.values())
        res = self.service.spreadsheets().values().get(
            spreadsheetId = self.spreadsheet_id,
            range = "Calendario Ejec {}!{}4:{}".format(
                today.strftime("%Y%m"),
                l_days_monitor[0],
                l_days_monitor[-1]
            )).execute()
        if "values" in res.keys():
            datos.days_values = res["values"]

    def get_vals_cal_p(self):
        l_days_monitor = list(datos.days_monitor_p.values())
        res = self.service.spreadsheets().values().get(
            spreadsheetId = self.spreadsheet_id,
            range = "Calendario Ejec {}!{}4:{}".format(
                (today - relativedelta(months=1)).strftime("%Y%m"),
                l_days_monitor[0],
                l_days_monitor[-1]
            )).execute()
        if "values" in res.keys():
            datos.days_values_p = res["values"]  #### A veces google sheets no regresa todos los datos (err1) -> data_ops.py
                                                 ### Lista de lista, cada lista es una fila de ejecuciones (dias)

    def set_ejec_by_days(self, col_index, n_day, mes):
        body_req = srqsts.set_ejec_day(today, col_index, datos.ejec_by_day, n_day, mes)
        res = self.service.spreadsheets().values().batchUpdate(
            spreadsheetId = self.spreadsheet_id,
            body=body_req
        ).execute()

    def get_sheet_cancelados(self):
        res = self.service.spreadsheets().values().get(
            spreadsheetId = self.spreadsheet_id,
            range = "CANCELACIONES RIESGOS!A2:V"
        ).execute()
        datos.data_sheet_cancelaciones = res["values"]

    def insert_empty_row(self):
        srqsts.reqs.append(srqsts.insert_empty_row(datos.sheets_id["CANCELACIONES RIESGOS"]))
        res = self.service.spreadsheets().batchUpdate(
            spreadsheetId = self.spreadsheet_id,
            body = srqsts.body_reqs(srqsts.reqs)
        ).execute()
        srqsts.reqs = []

    def insert_data_cancelados(self, data):
        res = self.service.spreadsheets().values().batchUpdate(
            spreadsheetId = self.spreadsheet_id,
            body = srqsts.insert_data(data)
        ).execute()
        return res


def set_spreadsheet():
    # vars.SPREADSHEET_ID = input("- Ingrese el spreadsheetID:\n")
    vars.SPREADSHEET_ID = "1aoE1ruBKwATdW-KQrzyE_jl4Pzi3i8mukBtO1Qzh3qc"
    try:
        sheets = Services(vars.SPREADSHEET_ID)
        sheets.get_spreadsheet()
        sheets.set_sheets_id_dict()
        return sheets
    except HttpError as err:
        if err.resp["status"] == "404":
            print("- No se encontro el spreadsheet")
        return set_spreadsheet()
    
