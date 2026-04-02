from datetime import datetime
from db import get_connection
import csv

def get_active_hosts():
    """
    Obtiene todos los hosts activos desde la base de datos.

    Retorna:
        list[dict]: Lista de hosts con id, name y address.
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT id, name, address
        FROM hosts
        WHERE is_active = TRUE
        ORDER BY id;
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    hosts = []
    for row in rows:
        hosts.append({
            "id": row[0],
            "name": row[1],
            "address": row[2]
        })

    return hosts


def get_checks_for_host(host_id):
    """
    Obtiene todos los checks de un host específico.

    Parámetros:
        host_id (int): ID del host.

    Retorna:
        list[dict]: Lista de checks del host.
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT check_time, status, latency_ms, error_message
        FROM checks
        WHERE host_id = %s
        ORDER BY check_time;
    """
    cursor.execute(query, (host_id,))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    checks = []
    for row in rows:
        checks.append({
            "check_time": row[0],
            "status": row[1],
            "latency_ms": float(row[2]) if row[2] is not None else None,
            "error_message": row[3]
        })
        

    return checks


def get_incidents_for_host(host_id):
    """
    Obtiene todos los incidentes de un host específico.

    Parámetros:
        host_id (int): ID del host.

    Retorna:
        list[dict]: Lista de incidentes del host.
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT start_time, end_time, status
        FROM incidents
        WHERE host_id = %s
        ORDER BY start_time;
    """
    cursor.execute(query, (host_id,))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    incidents = []
    for row in rows:
        incidents.append({
            "start_time": row[0],
            "end_time": row[1],
            "status": row[2]
        })

    return incidents


def calculate_check_metrics(checks):
    """
    Calcula métricas basadas en la tabla checks.

    Parámetros:
        checks (list[dict]): Lista de checks de un host.

    Retorna:
        dict: Métricas calculadas:
            - total_checks
            - up_checks
            - down_checks
            - availability_pct
            - avg_latency_ms
    """
    total_checks = len(checks)

    up_checks = 0
    down_checks = 0
    latencies = []

    for check in checks:
        status = check["status"]

        if status == "UP":
            up_checks += 1

            # Solo agregamos latencia si existe
            if check["latency_ms"] is not None:
                latencies.append(check["latency_ms"])

        elif status == "DOWN":
            down_checks += 1

    # Disponibilidad
    if total_checks > 0:
        availability_pct = (up_checks / total_checks) * 100
    else:
        availability_pct = None

    # Latencia promedio
    if len(latencies) > 0:
        avg_latency_ms = sum(latencies) / len(latencies)
    else:
        avg_latency_ms = None

    return {
        "total_checks": total_checks,
        "up_checks": up_checks,
        "down_checks": down_checks,
        "availability_pct": availability_pct,
        "avg_latency_ms": avg_latency_ms
    }


def calculate_incident_metrics(incidents):
    """
    Calcula métricas basadas en la tabla incidents.

    Parámetros:
        incidents (list[dict]): Lista de incidentes de un host.

    Retorna:
        dict: Métricas calculadas:
            - fall_count
            - downtime_seconds
    """
    fall_count = len(incidents)
    downtime_seconds = 0

    now = datetime.now()

    for incident in incidents:
        start_time = incident["start_time"]
        end_time = incident["end_time"]

        # Si el incidente sigue abierto, calculamos hasta ahora
        if end_time is None:
            duration = now - start_time
        else:
            duration = end_time - start_time

        downtime_seconds += duration.total_seconds()

    return {
        "fall_count": fall_count,
        "downtime_seconds": int(downtime_seconds)
    }


def build_host_report(host):
    """
    Construye el reporte completo de un host.
    """
    host_id = host["id"]

    # 1. Obtener datos
    checks = get_checks_for_host(host_id)
    incidents = get_incidents_for_host(host_id)

    # 2. Determinar estado actual (IMPORTANTE: aquí va)
    if len(checks) > 0:
        current_status = checks[-1]["status"]
    else:
        current_status = "UNKNOWN"

    # 3. Calcular métricas
    check_metrics = calculate_check_metrics(checks)
    incident_metrics = calculate_incident_metrics(incidents)

    # 4. Construir reporte
    report = {
        "host_id": host["id"],
        "name": host["name"],
        "address": host["address"],
        "total_checks": check_metrics["total_checks"],
        "up_checks": check_metrics["up_checks"],
        "down_checks": check_metrics["down_checks"],
        "availability_pct": check_metrics["availability_pct"],
        "avg_latency_ms": check_metrics["avg_latency_ms"],
        "fall_count": incident_metrics["fall_count"],
        "downtime_seconds": incident_metrics["downtime_seconds"],
        "current_status": current_status
    }

    return report
    """
    Construye el reporte completo de un host.

    Parámetros:
        host (dict): Diccionario con información del host.

    Retorna:
        dict: Reporte consolidado del host.
    """
    host_id = host["id"]

    # 1. Obtener datos del host
    checks = get_checks_for_host(host_id)
    incidents = get_incidents_for_host(host_id)

    # 2. Calcular métricas por separado
    check_metrics = calculate_check_metrics(checks)
    incident_metrics = calculate_incident_metrics(incidents)

    # 3. Combinar toda la información en un solo diccionario
    report = {
        "host_id": host["id"],
        "name": host["name"],
        "address": host["address"],
        "total_checks": check_metrics["total_checks"],
        "up_checks": check_metrics["up_checks"],
        "down_checks": check_metrics["down_checks"],
        "availability_pct": check_metrics["availability_pct"],
        "avg_latency_ms": check_metrics["avg_latency_ms"],
        "fall_count": incident_metrics["fall_count"],
        "downtime_seconds": incident_metrics["downtime_seconds"]
    }

    return report


def build_report():
    """
    Construye el reporte de todos los hosts activos.

    Retorna:
        list[dict]: Lista con reportes por host.
    """
    hosts = get_active_hosts()
    report_data = []

    for host in hosts:
        host_report = build_host_report(host)
        report_data.append(host_report)

    return report_data


def format_duration(seconds):
    """
    Convierte segundos a formato HH:MM:SS.

    Parámetros:
        seconds (int): Cantidad de segundos.

    Retorna:
        str: Tiempo formateado.
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    return f"{hours:02}:{minutes:02}:{secs:02}"


def print_report(report_data):
    """
    Imprime el reporte en consola en formato tabular.
    """

    print("\n" + "=" * 120)
    print("NETWORK MONITORING REPORT")
    print("=" * 120)

    print(
        f"{'HOST':20} {'ADDRESS':18} {'CHK':5} {'UP':5} {'DOWN':6} "
        f"{'AVAIL(%)':10} {'STATUS':8} {'FALLS':7} {'DOWNTIME':12} {'AVG LAT(ms)':12}"
    )

    print("-" * 120)

    for item in report_data:
        availability = (
            f"{item['availability_pct']:.2f}"
            if item["availability_pct"] is not None
            else "N/A"
        )

        avg_latency = (
            f"{item['avg_latency_ms']:.2f}"
            if item["avg_latency_ms"] is not None
            else "N/A"
        )

        downtime = format_duration(item["downtime_seconds"])

        print(
            f"{item['name'][:20]:20} "
            f"{item['address'][:18]:18} "
            f"{item['total_checks']:<5} "
            f"{item['up_checks']:<5} "
            f"{item['down_checks']:<6} "
            f"{availability:10} "
            f"{item['current_status']:<8} "
            f"{item['fall_count']:<7} "
            f"{downtime:12} "
            f"{avg_latency:12}"
        )

    print("=" * 120)




def export_to_csv(report_data, filename="report.csv"):
    """
    Exporta el reporte a un archivo CSV.
    """

    fieldnames = [
        "host_id",
        "name",
        "address",
        "total_checks",
        "up_checks",
        "down_checks",
        "availability_pct",
        "current_status",
        "fall_count",
        "downtime_seconds",
        "avg_latency_ms"
    ]

    with open(filename, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()

        for row in report_data:
            writer.writerow(row)

    print(f"\nReporte exportado a {filename}")

def export_checks_to_csv(filename="checks_report.csv"):
    """
    Exporta los checks con información temporal para análisis.
    """

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT h.name, h.address, c.check_time, c.status, c.latency_ms
        FROM checks c
        JOIN hosts h ON h.id = c.host_id
        ORDER BY c.check_time;
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    import csv

    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "host",
            "address",
            "check_time",
            "status",
            "latency_ms"
        ])

        for row in rows:
            writer.writerow(row)

    print(f"Checks exportados a {filename}")

if __name__ == "__main__":
    report = build_report()
    print_report(report)
    export_to_csv(report)
    export_checks_to_csv()