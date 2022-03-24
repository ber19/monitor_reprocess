import datos.dates as dates

fechas = dates.fechas()

def main():
    print("- La FECHA DE HOY es: ({1}) {0}"\
        .format(fechas["hoy"].strftime("%d-%m-%Y"), 
        dates.dias[fechas["hoy"].weekday()]))
    print("- La FECHA INICIAL para la consulta de estado sera: {0}"\
    .format(fechas["ayer"]))
    r1 = input("- ¿Esta de acuerdo?: (n/s)\n").strip().lower()
    if r1 == "s" or r1 == "si" or r1 == "sí" or r1 == "S" \
        or r1 == "SI" or r1 == "SÍ":
        print("- Obteniendo datos (de consulta con estado)...")
        a_day, a_month, a_year = fechas["ayer"].split('-')
        flag1 = 0
        if int(a_month) != dates.m_actual: flag1 = 1
        if int(a_year) != dates.y_actual: flag1 = 2
        return {
            "ayer": fechas["ayer"],
            "hoy": fechas["hoy"],
            "flag1": flag1
        }
    elif r1 == "n" or r1 == "no" or r1 == "N" or r1 == "NO":
        fechas_custom = sel_fechas()
        return fechas_custom
    else:
        print("- Entrada invalida")
        return main()

def sel_fechas():
    year = dates.sel_y_final()
    mes = dates.sel_m_final(year)
    range_month = dates.range_month(int(year), int(mes))
    dia = dates.sel_d_final(range_month, int(mes), int(year))
    fecha_f = dates.set_date(int(dia), int(mes), int(year))
    print("- FECHA FINAL de la consulta de estado: "\
        + fecha_f.strftime("%d-%m-%Y"))
    fecha_i = dates.dias_atras(fecha_f)
    print("- La consulta se hara de {0} a {1}".format(
        fecha_i.strftime("%d-%m-%Y"),
        fecha_f.strftime("%d-%m-%Y")
    ))
    def conf_fechas():
        fi_ff = input("- ¿Esta de acuerdo con las fechas de consulta de estado?: (n/s) \n")
        if fi_ff == "s" or fi_ff == "si" or fi_ff == "sí" \
            or fi_ff == "S" or fi_ff == "SI" or fi_ff == "SÍ":
            flag1 = 0
            if fecha_i.month != dates.m_actual: flag1 = 1
            if fecha_i.year != dates.y_actual: flag1 = 2
            print("- Obteniendo datos (de consulta con estado)...") 
            return {
                "ayer": fecha_i.strftime("%d-%m-%Y"),
                "hoy": fecha_f,
                "flag1": flag1
            }
        elif fi_ff == "n" or fi_ff == "no" \
            or fi_ff == "N" or fi_ff == "NO":
            return sel_fechas()
        else:
            print("- Entrada invalida")
            return conf_fechas()
    return conf_fechas()


