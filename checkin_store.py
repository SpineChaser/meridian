import sqlite3

DATABASE = "stock.db"

def initialize_database():
    connection = sqlite3.connect(DATABASE)


    connection.execute("""
        CREATE TABLE IF NOT EXISTS checkins (
            attendee_id TEXT PRIMARY KEY,
            job_id TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    connection.commit()
    connection.close()

def create_pending_checkin(attendee_id, job_id, timestamp):
    connection = sqlite3.connect(DATABASE)

    try:
        connection.execute(
            """
            INSERT INTO checkins (
                attendee_id,
                job_id,
                status,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (attendee_id, job_id, "PENDING", timestamp, timestamp),
        )
        connection.commit()
        return True
    except sqlite3.IntegrityError:
        connection.rollback()
        return False
    finally:
        connection.close()

def get_checkin(attendee_id):
    connection = sqlite3.connect(DATABASE)

    row = connection.execute(
        """
        SELECT attendee_id, job_id, status, created_at, updated_at
        FROM checkins
        WHERE attendee_id = ?
        """,
        (attendee_id,),
    ).fetchone()

    connection.close()

    if row is None:
        return None

    return {
        "attendee_id": row[0],
        "job_id": row[1],
        "status": row[2],
        "created_at": row[3],
        "updated_at": row[4],
    }

def mark_printed(attendee_id, job_id, timestamp):
    connection = sqlite3.connect(DATABASE)

    cursor = connection.execute(
        """
        UPDATE checkins
        SET status = ?, updated_at = ?
        WHERE attendee_id = ?
          AND job_id = ?
          AND status = ?
        """,
        ("PRINTED", timestamp, attendee_id, job_id, "PENDING"),
    )

    connection.commit()
    updated = cursor.rowcount
    connection.close()

    return updated == 1
