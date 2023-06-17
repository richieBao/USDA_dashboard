# -*- coding: utf-8 -*-
"""
Created on Sat Jun 17 09:04:04 2023

@author: richie bao
"""
import webbrowser
from threading import Timer
from ._dash_fossil_CO2_emissions_2022 import app

def dash_fossil_CO2_emissions_2022():
    """ Run the app from an entry point defined in setup.cfg
    TODO: need to check port is available
    """

    # set up the url and a threading Timer
    host ='127.0.0.1'#"localhost"
    port =8050 #8080
    folder = "dash-nba"
    url = f"http://{host}:{port}/{folder}/"
    Timer(10, webbrowser.open_new(url))

    # run app
    app.run(host=host, port=port, debug=False)
    
if __name__=="__main__":
    dash_fossil_CO2_emissions_2022()
