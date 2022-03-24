from googleapiclient.errors import HttpError
from scraping.scheduling_scraping import main_estado
from vars import vars
from datos import datos
from interface.cli_user import main as cli
from ops.sheets_services import set_spreadsheet
from ops import set_dfs, data_ops
import traceback
import json
from ops.clean_scrap import clean_mei, clean_scoped, clean_drag
from datos import dates


def main():
    try:
        '''Limpia la basura que puediera dejar el programa'''
        clean_mei()
        clean_drag()
        try:
            clean_scoped()
        except PermissionError as err:
            pass
        '''Ejecuta la interfaz de usuario para seleccionar las fechas'''
        fechas = cli()
        '''Obtiene los datos de la consulta de estado'''
        main_estado(fechas)
        '''Convierte los datos de la consulta de estado a Dataframes'''
        set_dfs.set_dfs_e()
        print("- Datos recolectados\n")
        '''Establece los servicios con las Google Spredsheet'''
        sheets = set_spreadsheet()              
        '''Verifica si la hoja negra (la del monitor) y la de cancelaciones existen'''
        sheets.check_sheet_monitor()
        sheets.check_sheet_cancelados()
        '''Obtiene los valores de la hoja negra y lo convierte a un DataFrame'''
        set_dfs.set_df_monitor()
        set_dfs.set_df_monitor_p()
        '''Obtiene los valores de la hoja de cancelaciones y lo convierte a un DataFrame'''
        sheets.get_sheet_cancelados()
        set_dfs.set_df_cancelaciones()
        '''Obtiene los cancelados de la consulta de estado'''
        data_ops.get_notoks()
        '''Obtiene los cancelados que son nuestros y
            los coloca en la hoja de cancelaciones'''
        data_ops.get_delegated_notoks(sheets)
        '''Obtiene los jobs que son nuestros'''
        data_ops.estado_get_delegated_jobs()
        '''Establece los dias segun la consulta'''
        data_ops.set_days()
        '''Reconoce las columnas del calendario (los dias)'''
        sheets.get_days_monitor()
        sheets.get_days_monitor_p()
        '''Obtiene los valores anteriores de los dias'''
        sheets.get_vals_cal()
        sheets.get_vals_cal_p()
        '''Establece los valores de las ejecuciones de los jobs
           para que funcionen con la hoja negra'''
        data_ops.ejec_by_day()
        '''Inserta las ejecuciones del dia (por dia) (columna) en la hoja negra'''
        for m, n_day in datos.days_ejec:
            if m == "a":
                col_index = datos.days_monitor[n_day]
                sheets.set_ejec_by_days(
                    col_index=col_index,
                    n_day=n_day,
                    mes = m
                )
            if m == "p":
                col_index = datos.days_monitor_p[n_day]
                sheets.set_ejec_by_days(
                    col_index = col_index,
                    n_day = n_day,
                    mes = m
                )
        """Coloca la fecha y hora de la ejecucion"""
        sheets.set_datetime_ejec()
        '''Finaliza la ejecucion del programa'''
        print("\nProceso finalizado! :D")
    except HttpError as err:
        if vars.selenium_driver:
            vars.selenium_driver.quit()
        print(json.loads(err.content.decode("utf-8"))["error"]["message"])
    except Exception as err:
        if vars.selenium_driver:
            vars.selenium_driver.quit()
        print("- Error inesperado.\n- Info:\n", err,
            "\n- Cerrando ...")       
        traceback.print_exc()
    except KeyboardInterrupt:
        if vars.selenium_driver:
            vars.selenium_driver.quit()
        print("- Ejecucion interrumpida")

if __name__ == "__main__":
    main()
