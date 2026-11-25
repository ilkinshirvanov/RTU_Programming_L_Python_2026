"""Reading CSV files into flight records and error messages."""

import csv
import os

from validator import validate_row, to_record


def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    """Process CSV files and return valid records and error messages."""

    records = []
    errors = []
    seen_flights = set()

    for path in paths:
        filename = os.path.basename(path)

        try:
            with open(path, "r", encoding="utf-8", newline="") as file:
                reader = csv.reader(file)

                # Skip the first physical line as the header.
                first_line = True

                for line_number, line in enumerate(file, start=1):
                    if first_line:
                        first_line = False
                        continue

                    stripped_line = line.strip()

                    # Skip blank lines.
                    if not stripped_line:
                        continue

                    # Skip comment lines.
                    if stripped_line.startswith("#"):
                        continue

                    try:
                        fields = next(csv.reader([line]))
                    except csv.Error:
                        errors.append(
                            f"{filename}:{line_number}: WRONG_FIELD_COUNT | Malformed CSV row"
                        )
                        continue

                    fields = [field.strip() for field in fields]

                    error_code = validate_row(fields, airports)

                    if error_code is not None:
                        errors.append(
                            f"{filename}:{line_number}: {error_code} | Invalid flight data"
                        )
                        continue

                    record = to_record(fields)

                    # Duplicate check: flight ID + departure datetime.
                    duplicate_key = (
                        record["flight_id"],
                        record["departure_datetime"],
                    )

                    if duplicate_key in seen_flights:
                        errors.append(
                            f"{filename}:{line_number}: DUPLICATE_FLIGHT | Duplicate flight"
                        )
                        continue

                    seen_flights.add(duplicate_key)
                    records.append(record)

        except (OSError, UnicodeError):
            errors.append(f"{filename}:0: FILE_ERROR | Unable to read file")

    return records, errors
