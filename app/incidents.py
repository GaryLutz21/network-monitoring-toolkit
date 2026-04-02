def get_last_status(cursor, host_id):
    cursor.execute("""
        SELECT status
        FROM checks
        WHERE host_id = %s
        ORDER BY check_time DESC, id DESC
        LIMIT 1 OFFSET 1
    """, (host_id,))
    
    row = cursor.fetchone()
    return row[0] if row else None


def get_open_incident(cursor, host_id):
    cursor.execute("""
        SELECT id
        FROM incidents
        WHERE host_id = %s AND status = 'OPEN'
        ORDER BY start_time DESC
        LIMIT 1
    """, (host_id,))
    
    row = cursor.fetchone()
    return row[0] if row else None


def open_incident(cursor, host_id):
    cursor.execute("""
        INSERT INTO incidents (host_id, start_time, status)
        VALUES (%s, CURRENT_TIMESTAMP, 'OPEN')
    """, (host_id,))


def close_incident(cursor, incident_id):
    cursor.execute("""
        UPDATE incidents
        SET end_time = CURRENT_TIMESTAMP,
            status = 'CLOSED'
        WHERE id = %s
    """, (incident_id,))