import random
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path


DB_PATH = Path(__file__).with_name("detective.db")
MIN_ROWS = 30


def create_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_tables(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE suspects (
            suspect_id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER,
            city TEXT,
            occupation TEXT,
            risk_level TEXT
        );

        CREATE TABLE employees (
            employee_id INTEGER PRIMARY KEY,
            name TEXT,
            department TEXT,
            clearance_level INTEGER,
            hire_date TEXT
        );

        CREATE TABLE locations (
            location_id INTEGER PRIMARY KEY,
            location_name TEXT,
            city TEXT,
            security_level INTEGER
        );

        CREATE TABLE detectives (
            detective_id INTEGER PRIMARY KEY,
            name TEXT,
            rank TEXT,
            years_experience INTEGER
        );

        CREATE TABLE access_logs (
            log_id INTEGER PRIMARY KEY,
            suspect_id INTEGER,
            location_id INTEGER,
            access_time TEXT,
            access_date TEXT,
            FOREIGN KEY (suspect_id) REFERENCES suspects(suspect_id),
            FOREIGN KEY (location_id) REFERENCES locations(location_id)
        );

        CREATE TABLE vehicles (
            vehicle_id INTEGER PRIMARY KEY,
            owner_suspect_id INTEGER,
            plate_number TEXT,
            vehicle_type TEXT,
            color TEXT,
            registered_city TEXT,
            FOREIGN KEY (owner_suspect_id) REFERENCES suspects(suspect_id)
        );

        CREATE TABLE bank_transactions (
            transaction_id INTEGER PRIMARY KEY,
            suspect_id INTEGER,
            amount REAL,
            transaction_date TEXT,
            location TEXT,
            FOREIGN KEY (suspect_id) REFERENCES suspects(suspect_id)
        );

        CREATE TABLE incidents (
            incident_id INTEGER PRIMARY KEY,
            location_id INTEGER,
            incident_type TEXT,
            incident_date TEXT,
            severity INTEGER,
            FOREIGN KEY (location_id) REFERENCES locations(location_id)
        );

        CREATE TABLE phone_records (
            record_id INTEGER PRIMARY KEY,
            caller_id INTEGER,
            receiver_id INTEGER,
            call_time TEXT,
            duration_seconds INTEGER,
            FOREIGN KEY (caller_id) REFERENCES suspects(suspect_id),
            FOREIGN KEY (receiver_id) REFERENCES suspects(suspect_id)
        );

        CREATE TABLE evidence_inventory (
            evidence_id INTEGER PRIMARY KEY,
            evidence_type TEXT,
            found_location_id INTEGER,
            linked_suspect_id INTEGER,
            FOREIGN KEY (found_location_id) REFERENCES locations(location_id),
            FOREIGN KEY (linked_suspect_id) REFERENCES suspects(suspect_id)
        );

        CREATE TABLE case_assignments (
            case_id INTEGER PRIMARY KEY,
            suspect_id INTEGER,
            detective_id INTEGER,
            status TEXT,
            priority INTEGER,
            FOREIGN KEY (suspect_id) REFERENCES suspects(suspect_id),
            FOREIGN KEY (detective_id) REFERENCES detectives(detective_id)
        );

        CREATE TABLE crime_scene_reports (
            report_id INTEGER PRIMARY KEY,
            location_id INTEGER,
            report_text TEXT,
            report_date TEXT,
            FOREIGN KEY (location_id) REFERENCES locations(location_id)
        );

        CREATE TABLE interviews (
            interview_id INTEGER PRIMARY KEY,
            suspect_id INTEGER,
            detective_id INTEGER,
            interview_text TEXT,
            interview_date TEXT,
            FOREIGN KEY (suspect_id) REFERENCES suspects(suspect_id),
            FOREIGN KEY (detective_id) REFERENCES detectives(detective_id)
        );
        """
    )


def daterange(start: date, end: date) -> list[date]:
    days = (end - start).days
    return [start + timedelta(days=offset) for offset in range(days + 1)]


def random_date_string(rng: random.Random, start: date, end: date) -> str:
    return rng.choice(daterange(start, end)).isoformat()


def random_datetime_parts(
    rng: random.Random, start: date, end: date
) -> tuple[str, str]:
    chosen_date = rng.choice(daterange(start, end))
    chosen_time = datetime.combine(chosen_date, datetime.min.time()) + timedelta(
        seconds=rng.randint(0, 86399)
    )
    return chosen_date.isoformat(), chosen_time.strftime("%H:%M:%S")


def populate_tables(connection: sqlite3.Connection) -> None:
    rng = random.Random(1847)
    cities = [
        "Brookhaven",
        "Riverton",
        "Ashford",
        "Fairview",
        "Oakridge",
        "Stonebridge",
        "Redwater",
        "Kingsport",
    ]
    first_names = [
        "Ava",
        "Noah",
        "Mila",
        "Ethan",
        "Iris",
        "Liam",
        "Sofia",
        "Mason",
        "Nora",
        "Julian",
        "Leah",
        "Caleb",
        "Zoe",
        "Owen",
        "Clara",
        "Isaac",
    ]
    last_names = [
        "Cross",
        "Bennett",
        "Vale",
        "Mercer",
        "Doyle",
        "Shaw",
        "Reed",
        "Foster",
        "Hayes",
        "Quinn",
        "Parker",
        "Sloan",
        "Price",
        "Hart",
        "Mills",
        "Drake",
    ]
    occupations = [
        "Accountant",
        "Mechanic",
        "Warehouse Supervisor",
        "Night Manager",
        "Courier",
        "Bartender",
        "Consultant",
        "Security Guard",
        "Bookkeeper",
        "Freelance Driver",
    ]
    risk_levels = ["LOW", "MEDIUM", "HIGH"]
    departments = [
        "Operations",
        "Finance",
        "Security",
        "Logistics",
        "Archives",
        "Facilities",
    ]
    location_types = [
        "Warehouse",
        "Office",
        "Harbor",
        "Garage",
        "Storage Unit",
        "Safe House",
        "Night Club",
        "Train Depot",
    ]
    vehicle_types = ["Sedan", "SUV", "Van", "Motorcycle", "Pickup", "Coupe"]
    colors = ["Black", "White", "Gray", "Blue", "Red", "Silver", "Green"]
    incident_types = [
        "Burglary",
        "Unauthorized Access",
        "Fraud Alert",
        "Arson Attempt",
        "Smuggling Tip",
        "Assault Report",
        "Data Theft",
        "Suspicious Meeting",
    ]
    evidence_types = [
        "Fingerprint",
        "USB Drive",
        "Ledger Page",
        "Keycard",
        "Photograph",
        "Fabric Sample",
        "Cash Bundle",
        "Burner Phone",
    ]
    statuses = ["OPEN", "ACTIVE", "CLOSED"]
    ranks = ["Junior", "Senior", "Inspector", "Chief"]
    report_fragments = [
        "Entry point showed signs of forced access.",
        "Witnesses reported a dark vehicle leaving quickly.",
        "Security cameras were partially disabled.",
        "Multiple prints were recovered near the rear exit.",
        "Receipts and coded notes were collected on site.",
        "Evidence suggests coordinated movement before midnight.",
    ]
    interview_fragments = [
        "Subject denied knowledge of the transfer.",
        "Witness placed the suspect near the location.",
        "Timeline shifted after reviewing phone activity.",
        "Detective noted evasive answers about recent travel.",
        "Interview revealed a connection to a warehouse lease.",
        "Statement partially matched access log records.",
    ]

    def full_name(index: int) -> str:
        return f"{first_names[index % len(first_names)]} {last_names[(index * 3) % len(last_names)]}"

    suspects = [
        (
            suspect_id,
            full_name(suspect_id),
            24 + (suspect_id % 29),
            cities[suspect_id % len(cities)],
            occupations[suspect_id % len(occupations)],
            risk_levels[suspect_id % len(risk_levels)],
        )
        for suspect_id in range(1, MIN_ROWS + 1)
    ]
    connection.executemany(
        "INSERT INTO suspects VALUES (?, ?, ?, ?, ?, ?)",
        suspects,
    )

    employees = [
        (
            employee_id,
            full_name(employee_id + 40),
            departments[employee_id % len(departments)],
            (employee_id % 5) + 1,
            random_date_string(rng, date(2015, 1, 1), date(2024, 12, 31)),
        )
        for employee_id in range(1, MIN_ROWS + 1)
    ]
    connection.executemany(
        "INSERT INTO employees VALUES (?, ?, ?, ?, ?)",
        employees,
    )

    locations = [
        (
            location_id,
            f"{cities[location_id % len(cities)]} {location_types[location_id % len(location_types)]}",
            cities[location_id % len(cities)],
            (location_id % 5) + 1,
        )
        for location_id in range(1, MIN_ROWS + 1)
    ]
    connection.executemany(
        "INSERT INTO locations VALUES (?, ?, ?, ?)",
        locations,
    )

    detectives = [
        (
            detective_id,
            full_name(detective_id + 90),
            ranks[(detective_id - 1) % len(ranks)],
            2 + (detective_id % 24),
        )
        for detective_id in range(1, MIN_ROWS + 1)
    ]
    connection.executemany(
        "INSERT INTO detectives VALUES (?, ?, ?, ?)",
        detectives,
    )

    access_logs = []
    for log_id in range(1, MIN_ROWS + 11):
        access_date, access_time = random_datetime_parts(
            rng, date(2025, 1, 1), date(2026, 3, 1)
        )
        access_logs.append(
            (
                log_id,
                ((log_id - 1) % MIN_ROWS) + 1,
                ((log_id * 2 - 1) % MIN_ROWS) + 1,
                access_time,
                access_date,
            )
        )
    connection.executemany(
        "INSERT INTO access_logs VALUES (?, ?, ?, ?, ?)",
        access_logs,
    )

    vehicles = []
    for vehicle_id in range(1, MIN_ROWS + 9):
        owner_id = ((vehicle_id * 3 - 1) % MIN_ROWS) + 1
        plate_number = (
            f"{chr(65 + (vehicle_id % 26))}{chr(65 + ((vehicle_id + 7) % 26))}"
            f"-{1000 + vehicle_id}"
        )
        vehicles.append(
            (
                vehicle_id,
                owner_id,
                plate_number,
                vehicle_types[vehicle_id % len(vehicle_types)],
                colors[vehicle_id % len(colors)],
                cities[owner_id % len(cities)],
            )
        )
    connection.executemany(
        "INSERT INTO vehicles VALUES (?, ?, ?, ?, ?, ?)",
        vehicles,
    )

    bank_transactions = []
    for transaction_id in range(1, MIN_ROWS + 13):
        suspect_id = ((transaction_id * 5 - 1) % MIN_ROWS) + 1
        amount = round(75 + (transaction_id * 43.27), 2)
        bank_transactions.append(
            (
                transaction_id,
                suspect_id,
                amount,
                random_date_string(rng, date(2024, 6, 1), date(2026, 2, 28)),
                f"{cities[transaction_id % len(cities)]} Financial Center",
            )
        )
    connection.executemany(
        "INSERT INTO bank_transactions VALUES (?, ?, ?, ?, ?)",
        bank_transactions,
    )

    incidents = []
    for incident_id in range(1, MIN_ROWS + 7):
        incidents.append(
            (
                incident_id,
                ((incident_id * 4 - 1) % MIN_ROWS) + 1,
                incident_types[incident_id % len(incident_types)],
                random_date_string(rng, date(2024, 8, 1), date(2026, 3, 15)),
                (incident_id % 5) + 1,
            )
        )
    connection.executemany(
        "INSERT INTO incidents VALUES (?, ?, ?, ?, ?)",
        incidents,
    )

    phone_records = []
    for record_id in range(1, MIN_ROWS + 16):
        caller_id = ((record_id * 2 - 1) % MIN_ROWS) + 1
        receiver_id = ((record_id * 7 + 3) % MIN_ROWS) + 1
        if receiver_id == caller_id:
            receiver_id = (receiver_id % MIN_ROWS) + 1
        phone_date, phone_time = random_datetime_parts(
            rng, date(2025, 1, 1), date(2026, 3, 18)
        )
        phone_records.append(
            (
                record_id,
                caller_id,
                receiver_id,
                f"{phone_date} {phone_time}",
                45 + (record_id * 37 % 1200),
            )
        )
    connection.executemany(
        "INSERT INTO phone_records VALUES (?, ?, ?, ?, ?)",
        phone_records,
    )

    evidence_inventory = []
    for evidence_id in range(1, MIN_ROWS + 8):
        evidence_inventory.append(
            (
                evidence_id,
                evidence_types[evidence_id % len(evidence_types)],
                ((evidence_id * 6 - 1) % MIN_ROWS) + 1,
                ((evidence_id * 5 + 2) % MIN_ROWS) + 1,
            )
        )
    connection.executemany(
        "INSERT INTO evidence_inventory VALUES (?, ?, ?, ?)",
        evidence_inventory,
    )

    case_assignments = []
    for case_id in range(1, MIN_ROWS + 1):
        case_assignments.append(
            (
                case_id,
                case_id,
                ((case_id * 3 - 1) % MIN_ROWS) + 1,
                statuses[case_id % len(statuses)],
                (case_id % 5) + 1,
            )
        )
    connection.executemany(
        "INSERT INTO case_assignments VALUES (?, ?, ?, ?, ?)",
        case_assignments,
    )

    crime_scene_reports = []
    for report_id in range(1, MIN_ROWS + 6):
        location_id = ((report_id * 3 - 1) % MIN_ROWS) + 1
        crime_scene_reports.append(
            (
                report_id,
                location_id,
                f"{report_fragments[report_id % len(report_fragments)]} "
                f"Scene linked to {cities[location_id % len(cities)]}.",
                random_date_string(rng, date(2024, 8, 1), date(2026, 3, 15)),
            )
        )
    connection.executemany(
        "INSERT INTO crime_scene_reports VALUES (?, ?, ?, ?)",
        crime_scene_reports,
    )

    interviews = []
    for interview_id in range(1, MIN_ROWS + 10):
        suspect_id = ((interview_id * 4 - 1) % MIN_ROWS) + 1
        detective_id = ((interview_id * 5 - 1) % MIN_ROWS) + 1
        interviews.append(
            (
                interview_id,
                suspect_id,
                detective_id,
                f"{interview_fragments[interview_id % len(interview_fragments)]} "
                f"Follow-up concerned suspect #{suspect_id}.",
                random_date_string(rng, date(2024, 9, 1), date(2026, 3, 20)),
            )
        )
    connection.executemany(
        "INSERT INTO interviews VALUES (?, ?, ?, ?, ?)",
        interviews,
    )

    connection.commit()


def validate_database(connection: sqlite3.Connection) -> None:
    expected_tables = [
        "suspects",
        "employees",
        "locations",
        "access_logs",
        "vehicles",
        "bank_transactions",
        "incidents",
        "phone_records",
        "evidence_inventory",
        "case_assignments",
        "crime_scene_reports",
        "interviews",
        "detectives",
    ]
    for table_name in expected_tables:
        row_count = connection.execute(
            f"SELECT COUNT(*) FROM {table_name}"
        ).fetchone()[0]
        if row_count < MIN_ROWS:
            raise ValueError(f"Table {table_name} has fewer than {MIN_ROWS} rows")

    join_checks = [
        (
            "suspects_access_logs",
            """
            SELECT COUNT(*)
            FROM suspects s
            JOIN access_logs a ON a.suspect_id = s.suspect_id
            """,
        ),
        (
            "suspects_vehicles",
            """
            SELECT COUNT(*)
            FROM suspects s
            JOIN vehicles v ON v.owner_suspect_id = s.suspect_id
            """,
        ),
        (
            "suspects_bank_transactions",
            """
            SELECT COUNT(*)
            FROM suspects s
            JOIN bank_transactions b ON b.suspect_id = s.suspect_id
            """,
        ),
        (
            "suspects_phone_records",
            """
            SELECT COUNT(*)
            FROM suspects s
            JOIN phone_records p ON p.caller_id = s.suspect_id
            """,
        ),
        (
            "suspects_evidence_inventory",
            """
            SELECT COUNT(*)
            FROM suspects s
            JOIN evidence_inventory e ON e.linked_suspect_id = s.suspect_id
            """,
        ),
        (
            "locations_incidents",
            """
            SELECT COUNT(*)
            FROM locations l
            JOIN incidents i ON i.location_id = l.location_id
            """,
        ),
        (
            "locations_crime_scene_reports",
            """
            SELECT COUNT(*)
            FROM locations l
            JOIN crime_scene_reports c ON c.location_id = l.location_id
            """,
        ),
        (
            "detectives_interviews",
            """
            SELECT COUNT(*)
            FROM detectives d
            JOIN interviews i ON i.detective_id = d.detective_id
            """,
        ),
        (
            "detectives_case_assignments",
            """
            SELECT COUNT(*)
            FROM detectives d
            JOIN case_assignments c ON c.detective_id = d.detective_id
            """,
        ),
    ]
    for check_name, query in join_checks:
        result = connection.execute(query).fetchone()[0]
        if result == 0:
            raise ValueError(f"Join check failed: {check_name}")

    fk_errors = connection.execute("PRAGMA foreign_key_check").fetchall()
    if fk_errors:
        raise ValueError(f"Foreign key validation failed: {fk_errors}")


def initialize_database() -> None:
    if DB_PATH.exists():
        return

    connection = create_connection()
    try:
        create_tables(connection)
        populate_tables(connection)
        validate_database(connection)
    except Exception:
        connection.close()
        if DB_PATH.exists():
            DB_PATH.unlink()
        raise
    else:
        connection.close()


initialize_database()


if __name__ == "__main__":
    initialize_database()
