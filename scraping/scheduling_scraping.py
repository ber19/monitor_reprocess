from selenium import webdriver
import requests
from bs4 import BeautifulSoup
from selenium.common.exceptions import WebDriverException
import vars.vars as vars
import datos.datos as datos


def main_estado(fechas):
    try:
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument("--headless")
        options.add_argument("--window-size=1280x720")
        vars.selenium_driver = webdriver.Chrome(executable_path=vars.PATH_DRIVER, options=options)
        vars.selenium_driver.get(vars.URL_EJECUCIONES)
        # vars.selenium_driver.minimize_window()
        for uuaa, str_uuaa in vars.UUAAS_ESTADO.items():
            if fechas["flag1"] == 0:   # Mismo mes
                datos.data_estado[uuaa] = estado(vars.selenium_driver, str_uuaa,
                    fechas["ayer"], fechas["hoy"].strftime("%d"))
                print("- {0} de consulta con estado OK".format(uuaa))
            if fechas["flag1"] == 1:  # Diferente mes
                datos.data_estado[uuaa] = estado(vars.selenium_driver, str_uuaa,
                    fechas["ayer"], fechas["hoy"].strftime("%d-%m"))
                print("- {0} de consulta con estado OK".format(uuaa))
            if fechas["flag1"] == 2:  # Diferente año
                datos.data_estado[uuaa] = estado(vars.selenium_driver, str_uuaa,
                    fechas["ayer"], fechas["hoy"].strftime("%d-%m-%Y"))
                print("- {0} de consulta con estado OK".format(uuaa))
            vars.selenium_driver.refresh()
        vars.selenium_driver.quit()
        vars.selenium_driver = None
    except WebDriverException:
        print("- Se cerro el proceso del navegador\n"\
            "- Intentando de nuevo\n"\
                "\tPor favor no cierre el proceso")
        vars.selenium_driver.quit()
        vars.selenium_driver = None
        main_estado(fechas)

def estado(driver, uuaa, f_date, t_date):
    data = []
    jobname = driver.find_element_by_id("jobname")
    jobname.clear()
    jobname.send_keys(uuaa)
    from_date = driver.find_element_by_id("txtFromDate")
    from_date.send_keys(f_date)
    to_date = driver.find_element_by_id("txtToDate")
    to_date.send_keys(t_date)
    submit = driver.find_element_by_id("Consultar")
    submit.click()
    driver.implicitly_wait(3)
    if driver.find_elements_by_xpath("//div[text()='No hay registros']"):
        return data
    driver.implicitly_wait(177)
    if driver.find_elements_by_xpath("//table[@id='tblEjec']/tbody/tr"):  
        soup = BeautifulSoup(driver.page_source, "html.parser")
        table = soup.find("table", attrs={"id":"tblEjec"})
        for row in table.find_all("tr")[1:]:
            data.append([value.getText() for value in row.find_all("td")])
        return data