import subprocess
import time
import csv
import os
from datetime import datetime

# ============================================================================
# CONFIGURACIÓN GENERAL
# ============================================================================
INTERFAZ_WIFI = "Wi-Fi"      # Nombre del adaptador, puede ser "Wi-Fi" o "WLAN"
HOST_PRUEBA = "8.8.8.8"      # Dirección para medir latencia
ARCHIVO_CSV = "monitoreo_red.csv"
INTERVALO_SEGUNDOS = 5       # Tiempo entre mediciones


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def ejecutar_comando(cmd):
    """Ejecuta un comando en PowerShell o CMD y devuelve su salida."""
    try:
        resultado = subprocess.check_output(cmd, shell=True, text=True, encoding="utf-8", errors="ignore")
        return resultado
    except:
        return ""


def obtener_informacion_wifi():
    """Obtiene información sobre la red WiFi utilizando netsh."""
    salida = ejecutar_comando("netsh wlan show interfaces")

    datos = {
        "ssid": "--",
        "bssid": "--",
        "senal": "--",
        "radio": "--",
        "canal": "--",
        "velocidad_rx": "--",
        "velocidad_tx": "--"
    }

    for linea in salida.splitlines():
        linea = linea.strip()

        if "SSID" in linea and "BSSID" not in linea:
            datos["ssid"] = linea.split(":", 1)[1].strip()

        elif "BSSID" in linea:
            datos["bssid"] = linea.split(":", 1)[1].strip()

        elif "Señal" in linea or "Signal" in linea:
            datos["senal"] = linea.split(":", 1)[1].strip()

        elif "Tipo de radio" in linea or "Radio type" in linea:
            datos["radio"] = linea.split(":", 1)[1].strip()

        elif "Canal" in linea or "Channel" in linea:
            datos["canal"] = linea.split(":", 1)[1].strip()

        elif "Velocidad de recepción" in linea or "Receive rate" in linea:
            datos["velocidad_rx"] = linea.split(":", 1)[1].strip()

        elif "Velocidad de transmisión" in linea or "Transmit rate" in linea:
            datos["velocidad_tx"] = linea.split(":", 1)[1].strip()

    return datos


def medir_latencia():
    """Mide la latencia con ping."""
    salida = ejecutar_comando(f"ping -n 1 {HOST_PRUEBA}")

    if "Tiempo" in salida or "time" in salida:
        try:
            for linea in salida.splitlines():
                if "Tiempo" in linea or "time" in linea:
                    valor = linea.split("=", 1)[1].replace("ms", "").strip()
                    return float(valor)
        except:
            pass

    return None


# ============================================================================
# FORMATO BONITO EN PANTALLA
# ============================================================================
def imprimir_registro(registro):
    os.system("cls")  # Limpia la terminal

    print("=" * 80)
    print("                   MONITOREO DE RED - INFORME EN TIEMPO REAL")
    print("=" * 80)

    print(f"Fecha y hora:              {registro['fecha_hora']}")
    print("-" * 80)

    print("      MÉTRICAS DE RED")
    print(f"  Latencia (ms):           {registro['latencia']}")
    print("-" * 80)

    print("      TRÁFICO")
    print(f"  Bytes enviados/s:        {registro['bytes_tx']}")
    print(f"  Bytes recibidos/s:       {registro['bytes_rx']}")
    print("-" * 80)

    print("      INFORMACIÓN WIFI")
    print(f"  SSID:                    {registro['ssid']}")
    print(f"  BSSID:                   {registro['bssid']}")
    print(f"  Señal (%):               {registro['senal']}")
    print(f"  Tipo de radio:           {registro['radio']}")
    print(f"  Canal:                   {registro['canal']}")
    print(f"  Velocidad Rx (Mbps):     {registro['velocidad_rx']}")
    print(f"  Velocidad Tx (Mbps):     {registro['velocidad_tx']}")
    print("-" * 80)

    print("      OTROS")
    print(f"  Dispositivos detectados: No disponible en Windows")
    print("=" * 80)
    print()


# ============================================================================
# INICIALIZAR ARCHIVO CSV (si no existe)
# ============================================================================
if not os.path.exists(ARCHIVO_CSV):
    with open(ARCHIVO_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "fecha_hora", "latencia_ms",
            "bytes_tx_s", "bytes_rx_s",
            "ssid", "bssid", "senal", "radio", "canal",
            "velocidad_rx_mbps", "velocidad_tx_mbps"
        ])


# ============================================================================
# LÓGICA PRINCIPAL DE MONITOREO
# ============================================================================
print("Iniciando monitoreo de red...")

# Obtención inicial de bytes
bytes_prev_tx = 0
bytes_prev_rx = 0

# Intentar leer contador inicial
try:
    salida = ejecutar_comando(f'netsh interface ipv4 show interfaces')
except:
    salida = ""

while True:
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Latencia
    latencia = medir_latencia()
    if latencia is None:
        latencia = "--"

    # Información WiFi
    wifi = obtener_informacion_wifi()

    # Tráfico de red
    salida_estad = ejecutar_comando(f'netsh interface ipv4 show interfaces')

    bytes_tx = 0
    bytes_rx = 0

    for linea in salida_estad.splitlines():
        if INTERFAZ_WIFI in linea:
            partes = linea.split()
            try:
                bytes_tx = int(partes[-2])
                bytes_rx = int(partes[-1])
            except:
                pass

    # Calcular diferencia
    velocidad_tx = max(0, bytes_tx - bytes_prev_tx)
    velocidad_rx = max(0, bytes_rx - bytes_prev_rx)

    bytes_prev_tx = bytes_tx
    bytes_prev_rx = bytes_rx

    # Registro final
    registro = {
        "fecha_hora": fecha_hora,
        "latencia": latencia,
        "bytes_tx": velocidad_tx,
        "bytes_rx": velocidad_rx,
        "ssid": wifi["ssid"],
        "bssid": wifi["bssid"],
        "senal": wifi["senal"],
        "radio": wifi["radio"],
        "canal": wifi["canal"],
        "velocidad_rx": wifi["velocidad_rx"],
        "velocidad_tx": wifi["velocidad_tx"]
    }

    imprimir_registro(registro)

    # Guardar en CSV
    with open(ARCHIVO_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            fecha_hora, latencia,
            velocidad_tx, velocidad_rx,
            wifi["ssid"], wifi["bssid"], wifi["senal"], wifi["radio"], wifi["canal"],
            wifi["velocidad_rx"], wifi["velocidad_tx"]
        ])

    time.sleep(INTERVALO_SEGUNDOS)
