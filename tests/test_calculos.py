"""Pruebas sencillas de coincidencia entre src/, verificacion/ y las muestras."""

import re
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from src.distribuciones import gumbel_momentos
from src.eda import resumen_numerico
from src.regresion import calculo_manual
from src.series import concurso_referencia, indices_estacionales, promedio_movil


RAIZ = Path(__file__).resolve().parent.parent


def ejecutar_verificacion(nombre: str) -> str:
    """Ejecuta un script independiente y devuelve su salida de texto."""
    proceso = subprocess.run(
        ["./.venv/bin/python", f"verificacion/{nombre}"],
        cwd=RAIZ,
        capture_output=True,
        text=True,
        check=True,
    )
    return proceso.stdout


def test_eda_app_src_y_verificacion():
    muestra = pd.read_csv(RAIZ / "datos/muestra_eda10.csv")
    salida = ejecutar_verificacion("verificar_eda.py")
    resumen = resumen_numerico(muestra["rendimiento"])

    esperado_media = float(re.search(r"Media = ([0-9.]+)", salida).group(1))
    esperado_mediana = float(re.search(r"Mediana = ([0-9.]+)", salida).group(1))
    esperado_varianza = float(re.search(r"Varianza muestral = ([0-9.]+)", salida).group(1))
    esperado_desviacion = float(re.search(r"Desviación estándar muestral = ([0-9.]+)", salida).group(1))

    assert abs(resumen["media"] - esperado_media) < 0.0001
    assert abs(resumen["mediana"] - esperado_mediana) < 0.0001
    assert abs(resumen["varianza"] - esperado_varianza) < 0.0001
    assert abs(resumen["desviacion_estandar"] - esperado_desviacion) < 0.0001
    assert resumen["n"] == 10


def test_distribuciones_src_y_verificacion():
    muestra = pd.read_csv(RAIZ / "datos/muestra_dist10.csv")
    salida = ejecutar_verificacion("verificar_distribuciones.py")
    momentos = gumbel_momentos(muestra["pmax24h_mm"])

    beta_verificacion = float(re.search(r"Beta \(Gumbel, momentos\) = ([0-9.]+)", salida).group(1))
    mu_verificacion = float(re.search(r"Mu \(Gumbel, momentos\) = ([0-9.]+)", salida).group(1))
    assert abs(momentos["beta"] - beta_verificacion) < 0.0001
    assert abs(momentos["mu"] - mu_verificacion) < 0.0001


def test_regresion_src_y_verificacion():
    muestra = pd.read_csv(RAIZ / "datos/muestra_reg8.csv")
    salida = ejecutar_verificacion("verificar_regresion.py")
    resultado = calculo_manual(
        muestra["lamina_riego"].to_numpy(dtype=float),
        muestra["rendimiento"].to_numpy(dtype=float),
    )

    sxx = float(re.search(r"Sxx = ([0-9.]+)", salida).group(1))
    sxy = float(re.search(r"Sxy = ([0-9.]+)", salida).group(1))
    b1 = float(re.search(r"b1 = ([0-9.]+)", salida).group(1))
    r2 = float(re.search(r"R² = ([0-9.]+)", salida).group(1))
    assert abs(resultado["Sxx"] - sxx) < 0.0001
    assert abs(resultado["Sxy"] - sxy) < 0.0001
    assert abs(resultado["b1"] - b1) < 0.0001
    assert abs(resultado["R2"] - r2) < 0.0001


def test_series_src_y_verificacion():
    muestra = pd.read_csv(RAIZ / "datos/muestra_series24.csv")
    muestra["fecha"] = pd.to_datetime(muestra["fecha"])
    serie = muestra.set_index("fecha")["precipitacion_mm"].asfreq("MS")
    salida = ejecutar_verificacion("verificar_series.py")

    pm3 = promedio_movil(serie, 3)
    assert abs(float(pm3.iloc[-1]) - 172.59666666666666) < 0.0001

    indices = indices_estacionales(serie)
    assert abs(float(indices.sum()) - 0.0) < 1e-8

    concurso = concurso_referencia(muestra)
    ganador_verificacion = "Estacional ingenuo" in salida
    assert not concurso.empty
    assert concurso.iloc[0]["metodo"] == "Estacional ingenuo"
    assert ganador_verificacion
