from datetime import date, timedelta, datetime
import calendar

'''weekday()'''
dias = {
    0: "Lunes",
    1: "Martes",
    2: "Miercoles",
    3: "Jueves",
    4: "Viernes",
    5: "Sabado",
    6: "Domingo"
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
rango_y = tuple([y for y in range(2020,2030,1)])
today = date.today()
y_actual = today.year
m_actual = today.month
d_actual = today.day
now = datetime.now()

def fechas():
    if today.weekday() == 0:
        yesterday = today - timedelta(days=3)
    else:
        yesterday = today - timedelta(days=1)
    return {
        "ayer": yesterday.strftime("%d-%m-%Y"),
        "hoy": today,
        "flag1": 0
    }

def sel_y_final():
    year = input("- Indique el AÑO de la FECHA FINAL: (2020 a 2022)\n")
    if year.isnumeric() and int(year) in rango_y and int(year) <= y_actual:
        return year
    else:
        print("- Entrada invalida")
        return sel_y_final()

def sel_m_final(year):
    mes = input("- Indique el MES de la FECHA FINAL: (1 a 12)\n")
    if mes.isnumeric() and int(mes) in meses:
        if int(year) == y_actual and int(mes) <= m_actual:
            return mes
        elif int(year) < y_actual:
            return mes
        else:
            print("- Entrada invalida")
            return sel_m_final(year)
    else:
        print("- Entrada invalida")
        return sel_m_final(year)

def range_month(year, month):
    weekday, t_days = calendar.monthrange(year, month)
    return [i for i in range(1, t_days+1)]

def sel_d_final(rango, mes, year):
    def in_actual(mes, year):
        if mes == m_actual and year == y_actual:
            return True
        else: return False

    dia = input("- Indique el DÍA de la FECHA FINAL: ({0} a {1})\n".format(
        rango[0], rango[-1]
    ))
    if in_actual(mes, year):
        if dia.isnumeric() and int(dia) in rango and int(dia) <= d_actual:
            return dia
        else:
            print("- Entrada invalida")
            return sel_d_final(rango, mes, year)
    elif not in_actual(mes, year):
        if dia.isnumeric() and int(dia) in rango:
            return dia
        else:
            print("- Entrada invalida")
            return sel_d_final(rango, mes, year)
    else:
        print("- Entrada invalida")
        return sel_d_final(rango, mes, year)

def set_date(day, mes, year):
    return date(year, mes, day)

def dias_atras(fecha_f):
    dias = input("- ¿Desde cuantos dias atras quiere hacer la consulta?\n"\
                    "(ejemplo: 1 para ayer, 2 para antier) (recomendable no mas de 10 dias)\n")
    # if dias.isnumeric() and int(dias) < 10: # Limitador
    if dias.isnumeric():
        return fecha_f - timedelta(days=int(dias))
    else:
        print("- Entrada invalida")
        return dias_atras(fecha_f)

        