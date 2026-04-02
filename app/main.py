from db import get_connection
from monitor import ping_host
from incidents import get_last_status, get_open_incident, open_incident, close_incident

def run_monitor():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, address FROM hosts WHERE is_active = TRUE;")
    hosts = cursor.fetchall()

    for host in hosts:
        host_id, name, address = host

        status, latency, error = ping_host(address)

        print(f"{name} ({address}) -> {status}")

        cursor.execute("""
            INSERT INTO checks (host_id, status, latency_ms, error_message)
            VALUES (%s, %s, %s, %s)
        """, (host_id, status, latency, error))

        previous_status = get_last_status(cursor, host_id)

        if previous_status == "UP" and status == "DOWN":
            if not get_open_incident(cursor, host_id):
                open_incident(cursor, host_id)
                print(f"Incidente ABIERTO para {name}")

        elif previous_status == "DOWN" and status == "UP":
            incident_id = get_open_incident(cursor, host_id)
            if incident_id:
                close_incident(cursor, incident_id)
                print(f"Incidente CERRADO para {name}")

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    run_monitor()