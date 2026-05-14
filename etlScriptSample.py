import sqlite3, json, logging
import retry

logging.basicConfig(filename="etl.log", level=logging.INFO)

@retry(max_attempts=3, delay=2)
def ingest_events(file):
    try:
        with open(file) as f:
            events = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"File error: {e}")
        return []

    try:
        with sqlite3.connect("supply_chain.db") as conn:
            cur = conn.cursor()
            cur.executemany("INSERT INTO rfid VALUES (:item_id, :location, :timestamp)", events)
            conn.commit()
    except sqlite3.Error as e:
        logging.error(f"DB error: {e}")
    return events

if __name__ == "__main__":
    events = ingest_events("rfid_events.json")
    logging.info(f"Ingested {len(events)} events")
