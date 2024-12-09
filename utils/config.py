try:
    DATABASE_URL = "oracle+cx_oracle://C##DEEZER:oracle@192.168.0.17:1521/?service_name=xe"
except:
    try:
        DATABASE_URL = "oracle+cx_oracle://C##DEEZER:oracle@localhost:1521/?service_name=xe"
    except:
        print("Error Database_url incorrecta, verificar archivo utils.config.py")