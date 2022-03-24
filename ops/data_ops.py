# from datetime import date
from dateutil.relativedelta import relativedelta
from datos import datos
from datos.dates import today
import pandas as pd
from vars import vars

###
def get_notoks():
    for uuaa_dfs in datos.dfs_estado.values():
        local_notoks = uuaa_dfs[uuaa_dfs["ENDED STATUS"].isin(vars.NOTOKS_OPTIONS)]
        datos.total_not_oks = datos.total_not_oks.append(local_notoks)
    datos.total_not_oks["ODATE"] = datos.total_not_oks["ODATE"].astype("int64")
    datos.total_not_oks["END TIME"] = pd.to_datetime(datos.total_not_oks["END TIME"])
    datos.total_not_oks.sort_values(by=["ODATE","END TIME"], inplace=True)

def get_delegated_notoks(sheets):
    for index in range(len(datos.total_not_oks)):
        job_not_ok = datos.total_not_oks.iloc[index]
        row_monitor = datos.df_monitor.loc[datos.df_monitor["JOB"] == job_not_ok["JOBNAME"]]
        if not row_monitor.empty:
            var1 = row_monitor.iloc[0]
            if var1["Tabla Delegada?"] == "DELEGADA" or var1["Tabla Delegada?"] == "EN PROCESO":
                datos.notoks = datos.notoks.append(job_not_ok)
                if not check_cancelado_exists(job_not_ok):
                    job_estado = pd.DataFrame().append(job_not_ok)
                    sheets.insert_empty_row()
                    cancelados_sheet_insert(sheets, row_monitor, job_estado)
###
def cancelados_sheet_insert(sheets, r_monitor, r_estado):
    row_monitor = r_monitor.iloc[0]
    row_estado = r_estado.iloc[0]
    sheets.insert_data_cancelados(
        [row_estado["ORDER ID"], "Riesgos",
        row_estado["JOBNAME"][:4], row_monitor["Malla"],
        row_monitor["SubAplicativo"], row_estado["JOBNAME"],
        row_estado["ENDED STATUS"], row_estado["ODATE"], row_estado["END TIME"].strftime("%Y%m%d%H%M%S"),  ## (1) Aqui si se quiere cambiar el formato
        row_monitor["Tabla Delegada?"], row_monitor["TIPO"], datos.meses[row_estado["END TIME"].month],
        row_monitor["Tabla Master"], datos.get_per(row_monitor["Malla"][8:11]), "", "", "", "", "",
        "", ""
        ]
    )

def check_cancelado_exists(job_not_ok):
    job_s = datos.df_sheet_cancelaciones.loc[
        (datos.df_sheet_cancelaciones["JOBNAME"] == str(job_not_ok["JOBNAME"])) &
        (datos.df_sheet_cancelaciones["Fecha Cancelacion"] == job_not_ok["END TIME"].strftime("%Y%m%d%H%M%S"))  ## (1) tambien aqui, para que lo reconozca 
    ]
    if job_s.empty:
        return False
    else: 
        return True

###########
def estado_get_delegated_jobs():
    for uuaa_dfs in datos.dfs_estado.values():
        for index in range(len(uuaa_dfs)):
            dele_job = uuaa_dfs.iloc[index]
            row_monitor = datos.df_monitor.loc[datos.df_monitor["JOB"] == dele_job.JOBNAME]
            if row_monitor.empty == False:
                var1 = row_monitor.iloc[0]
                if var1["Tabla Delegada?"] == "DELEGADA" or var1["Tabla Delegada?"] == "EN PROCESO":
                    datos.jobs_estado = datos.jobs_estado.append(dele_job)
    datos.jobs_estado["JOBNAME"] = datos.jobs_estado["JOBNAME"].str.strip()
    datos.jobs_estado["ENDED STATUS"] = datos.jobs_estado["ENDED STATUS"].str.strip()
    datos.jobs_estado["ODATE"] = datos.jobs_estado["ODATE"].str.strip()
    datos.jobs_estado["END TIME"] = datos.jobs_estado["END TIME"].str.strip()
    datos.jobs_estado["END TIME"] = pd.to_datetime(datos.jobs_estado["END TIME"])
    datos.jobs_estado.sort_values(by=["ODATE", "END TIME"], inplace=True, ascending=False)

def set_days():   ####### AQUI SE IDENTIFICAN LOS JOB QUE PUEDEN SER DEL MES ANTERIOR
    for index in range(len(datos.jobs_estado)):
        job = datos.jobs_estado.iloc[index]
        if job["ODATE"][4:6][0] == "0":
            if job["ODATE"][5:6] == str(today.month):
                datos.days_ejec.add(("a", int(job["ODATE"][6:8])))
            elif job["ODATE"][5:6] == str((today - relativedelta(months=1)).month):
                datos.days_ejec.add(("p", int(job["ODATE"][6:8])))
        if job["ODATE"].strip()[4:6] == str(today.month):
            datos.days_ejec.add(("a", int(job["ODATE"][6:8])))
        elif job["ODATE"].strip()[4:6] == str((today - relativedelta(months=1)).month):
            datos.days_ejec.add(("p", int(job["ODATE"][6:8])))
    for m, day in datos.days_ejec:
        datos.ejec_by_day[(m, day)] = []

def ejec_by_day():
    def get_day(str_day):
        if len(str_day) == 1: return "0" + str_day
        else: return str_day
    for m, day in datos.ejec_by_day:
        if m == "a":
            for index in range(len(datos.df_monitor)):
                row_monitor = datos.df_monitor.iloc[index]
                job = datos.jobs_estado.loc[
                    (datos.jobs_estado["JOBNAME"] == row_monitor["JOB"]) &
                    (datos.jobs_estado["ODATE"].str.slice(6,8) == get_day(str(day)))
                ]
                if job.empty:
                    datos.ejec_by_day[(m, day)].append([])
                    continue
                else:
                    var1 = job.iloc[0]
                    col_index = day - 1
                    if datos.days_values:
                        # if datos.days_values[index]:
                        try:
                            row_ejec_prev = datos.days_values[index]
                            if len(row_ejec_prev) <= col_index:
                                dif = (col_index - len(row_ejec_prev)) + 1
                                for i in range(0, dif):
                                    row_ejec_prev.append("")                
                            prev_status = row_ejec_prev[col_index]
                            curr_status = var1["ENDED STATUS"]
                            ## m servira para que despues se vayan colocando los valores en las hojas correspondientes (mes pasado o mes actual) 
                            if (prev_status == "C" and curr_status == "OK") or \
                                (prev_status == "REX" and curr_status == "OK") or \
                                    (prev_status == "ROK"): datos.ejec_by_day[(m, day)].append(["ROK"])
                            elif prev_status == "C" and curr_status == "Executing": datos.ejec_by_day[(m, day)].append(["REX"])
                            elif (prev_status == "BAC" and curr_status == "OK") or \
                                (prev_status == "BA" and curr_status == "OK"):
                                    datos.ejec_by_day[(m, day)].append(["EVEOK"])
                            elif curr_status == "OK": datos.ejec_by_day[(m, day)].append(["O"])
                            elif curr_status == "Ended OK/En Hold": datos.ejec_by_day[(m, day)].append(["O"])
                            elif curr_status == "Wait Condition ¿Que espera para ejecutar?": datos.ejec_by_day[(m, day)].append(["WAIT"])
                            elif curr_status == "Executing": datos.ejec_by_day[(m, day)].append(["EX"])
                            elif curr_status == "NOTOK": datos.ejec_by_day[(m, day)].append(["C"])
                            elif curr_status == "Wait Workload/En Hold ¿Que espera para ejecutar?": datos.ejec_by_day[(m, day)].append(["WWH"])
                            elif curr_status == "Wait Condition/Eliminado del Activo": datos.ejec_by_day[(m, day)].append(["BA"])
                            elif curr_status == "Ended Not OK/Eliminado del Activo": datos.ejec_by_day[(m, day)].append(["BAC"])
                            elif curr_status == "Wait Condition/En Hold ¿Que espera para ejecutar?": datos.ejec_by_day[(m, day)].append(["WH"])
                            elif curr_status == "Executing/En Hold": datos.ejec_by_day[(m, day)].append(["EH"])
                            elif curr_status == "Ended Not OK/En Hold": datos.ejec_by_day[(m, day)].append(["CH"])
                            else: datos.ejec_by_day[(m, day)].append([])
                        # else:
                        except IndexError:
                            curr_status = var1["ENDED STATUS"]
                            if curr_status == "OK": datos.ejec_by_day[(m, day)].append(["O"])
                            elif curr_status == "Ended OK/En Hold": datos.ejec_by_day[(m, day)].append(["O"])
                            elif curr_status == "Wait Condition ¿Que espera para ejecutar?": datos.ejec_by_day[(m, day)].append(["WAIT"])
                            elif curr_status == "Executing": datos.ejec_by_day[(m, day)].append(["EX"])
                            elif curr_status == "NOTOK": datos.ejec_by_day[(m, day)].append(["C"])
                            elif curr_status == "Wait Workload/En Hold ¿Que espera para ejecutar?": datos.ejec_by_day[(m, day)].append(["WWH"])
                            elif curr_status == "Wait Condition/Eliminado del Activo": datos.ejec_by_day[(m, day)].append(["BA"])
                            elif curr_status == "Ended Not OK/Eliminado del Activo": datos.ejec_by_day[(m, day)].append(["BAC"])
                            elif curr_status == "Wait Condition/En Hold ¿Que espera para ejecutar?": datos.ejec_by_day[(m, day)].append(["WH"])
                            elif curr_status == "Executing/En Hold": datos.ejec_by_day[(m, day)].append(["EH"])
                            elif curr_status == "Ended Not OK/En Hold": datos.ejec_by_day[(m, day)].append(["CH"])
                            else: datos.ejec_by_day[(m, day)].append([])
                    else:
                        curr_status = var1["ENDED STATUS"]
                        if curr_status == "OK": datos.ejec_by_day[(m, day)].append(["O"])
                        elif curr_status == "Ended OK/En Hold": datos.ejec_by_day[(m, day)].append(["O"])
                        elif curr_status == "Wait Condition ¿Que espera para ejecutar?": datos.ejec_by_day[(m, day)].append(["WAIT"])
                        elif curr_status == "Executing": datos.ejec_by_day[(m, day)].append(["EX"])
                        elif curr_status == "NOTOK": datos.ejec_by_day[(m, day)].append(["C"])
                        elif curr_status == "Wait Workload/En Hold ¿Que espera para ejecutar?": datos.ejec_by_day[(m, day)].append(["WWH"])
                        elif curr_status == "Wait Condition/Eliminado del Activo": datos.ejec_by_day[(m, day)].append(["BA"])
                        elif curr_status == "Ended Not OK/Eliminado del Activo": datos.ejec_by_day[(m, day)].append(["BAC"])
                        elif curr_status == "Wait Condition/En Hold ¿Que espera para ejecutar?": datos.ejec_by_day[(m, day)].append(["WH"])
                        elif curr_status == "Executing/En Hold": datos.ejec_by_day[(m, day)].append(["EH"])
                        elif curr_status == "Ended Not OK/En Hold": datos.ejec_by_day[(m, day)].append(["CH"])
                        else: datos.ejec_by_day[(m, day)].append([])
        elif m == "p":
            for index in range(len(datos.df_monitor_p)):
                row_monitor = datos.df_monitor_p.iloc[index]     # Va iterando en la hoja del monitor
                job = datos.jobs_estado.loc[
                    (datos.jobs_estado["JOBNAME"] == row_monitor["JOB"]) &
                    (datos.jobs_estado["ODATE"].str.slice(6,8) == get_day(str(day)))
                ]
                if job.empty:
                    datos.ejec_by_day[(m, day)].append([])
                    continue
                else:
                    var1 = job.iloc[0]
                    col_index = day - 1
                    if datos.days_values_p:   ## No tiene datos aun
                        # if datos.days_values_p[index]:  ## Comentado por error de Google Sheets (err1) -> sheets_services.py
                        try:
                            row_ejec_prev = datos.days_values_p[index]
                            if len(row_ejec_prev) <= col_index: 
                                dif = (col_index - len(row_ejec_prev)) + 1
                                for i in range(0, dif):
                                    row_ejec_prev.append("")  ## Se llenan los espacios vacios que puedan haber hasta la fecha actual
                            prev_status = row_ejec_prev[col_index]  ## Se obtiene la ejecucion del dia (columna)
                            curr_status = var1["ENDED STATUS"]
                            ## m servira para que despues se vayan colocando los valores en las hojas correspondientes (mes pasado o mes actual) 
                            if (prev_status == "C" and curr_status == "OK") or \
                                (prev_status == "REX" and curr_status == "OK") or \
                                    (prev_status == "ROK"): datos.ejec_by_day[(m, day)].append(["ROK"])
                            elif prev_status == "C" and curr_status == "Executing": datos.ejec_by_day[(m, day)].append(["REX"])
                            elif (prev_status == "BAC" and curr_status == "OK") or \
                                (prev_status == "BA" and curr_status == "OK"):
                                    datos.ejec_by_day[(m, day)].append(["EVEOK"])
                            elif curr_status == "OK": datos.ejec_by_day[(m, day)].append(["O"])
                            elif curr_status == "Ended OK/En Hold": datos.ejec_by_day[(m, day)].append(["O"])
                            elif curr_status == "Wait Condition ¿Que espera para ejecutar?": datos.ejec_by_day[(m, day)].append(["WAIT"])
                            elif curr_status == "Executing": datos.ejec_by_day[(m, day)].append(["EX"])
                            elif curr_status == "NOTOK": datos.ejec_by_day[(m, day)].append(["C"])
                            elif curr_status == "Wait Workload/En Hold ¿Que espera para ejecutar?": datos.ejec_by_day[(m, day)].append(["WWH"])
                            elif curr_status == "Wait Condition/Eliminado del Activo": datos.ejec_by_day[(m, day)].append(["BA"])
                            elif curr_status == "Ended Not OK/Eliminado del Activo": datos.ejec_by_day[(m, day)].append(["BAC"])
                            elif curr_status == "Wait Condition/En Hold ¿Que espera para ejecutar?": datos.ejec_by_day[(m, day)].append(["WH"])
                            elif curr_status == "Executing/En Hold": datos.ejec_by_day[(m, day)].append(["EH"])
                            elif curr_status == "Ended Not OK/En Hold": datos.ejec_by_day[(m, day)].append(["CH"])
                            else: datos.ejec_by_day[(m, day)].append([])
                        # else:
                        except IndexError:
                            curr_status = var1["ENDED STATUS"]
                            if curr_status == "OK": datos.ejec_by_day[(m, day)].append(["O"])
                            elif curr_status == "Ended OK/En Hold": datos.ejec_by_day[(m, day)].append(["O"])
                            elif curr_status == "Wait Condition ¿Que espera para ejecutar?": datos.ejec_by_day[(m, day)].append(["WAIT"])
                            elif curr_status == "Executing": datos.ejec_by_day[(m, day)].append(["EX"])
                            elif curr_status == "NOTOK": datos.ejec_by_day[(m, day)].append(["C"])
                            elif curr_status == "Wait Workload/En Hold ¿Que espera para ejecutar?": datos.ejec_by_day[(m, day)].append(["WWH"])
                            elif curr_status == "Wait Condition/Eliminado del Activo": datos.ejec_by_day[(m, day)].append(["BA"])
                            elif curr_status == "Ended Not OK/Eliminado del Activo": datos.ejec_by_day[(m, day)].append(["BAC"])
                            elif curr_status == "Wait Condition/En Hold ¿Que espera para ejecutar?": datos.ejec_by_day[(m, day)].append(["WH"])
                            elif curr_status == "Executing/En Hold": datos.ejec_by_day[(m, day)].append(["EH"])
                            elif curr_status == "Ended Not OK/En Hold": datos.ejec_by_day[(m, day)].append(["CH"])
                            else: datos.ejec_by_day[(m, day)].append([])
                    else:
                        curr_status = var1["ENDED STATUS"]
                        if curr_status == "OK": datos.ejec_by_day[(m, day)].append(["O"])
                        elif curr_status == "Ended OK/En Hold": datos.ejec_by_day[(m, day)].append(["O"])
                        elif curr_status == "Wait Condition ¿Que espera para ejecutar?": datos.ejec_by_day[(m, day)].append(["WAIT"])
                        elif curr_status == "Executing": datos.ejec_by_day[(m, day)].append(["EX"])
                        elif curr_status == "NOTOK": datos.ejec_by_day[(m, day)].append(["C"])
                        elif curr_status == "Wait Workload/En Hold ¿Que espera para ejecutar?": datos.ejec_by_day[(m, day)].append(["WWH"])
                        elif curr_status == "Wait Condition/Eliminado del Activo": datos.ejec_by_day[(m, day)].append(["BA"])
                        elif curr_status == "Ended Not OK/Eliminado del Activo": datos.ejec_by_day[(m, day)].append(["BAC"])
                        elif curr_status == "Wait Condition/En Hold ¿Que espera para ejecutar?": datos.ejec_by_day[(m, day)].append(["WH"])
                        elif curr_status == "Executing/En Hold": datos.ejec_by_day[(m, day)].append(["EH"])
                        elif curr_status == "Ended Not OK/En Hold": datos.ejec_by_day[(m, day)].append(["CH"])
                        else: datos.ejec_by_day[(m, day)].append([])
        else: raise LookupError
                

