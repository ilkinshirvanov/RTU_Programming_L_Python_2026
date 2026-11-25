"""Flight Schedule Parser and Query Tool - command-line entry point."""

import sys
import argparse
import json
import os
import logging
from datetime import datetime

from validator import load_airports
from csv_loader import parse_files
from query import run_queries


STUDENT_ID = "251ADB133"
FIRST_NAME = "ILKIN"
LAST_NAME = "SHIRVANOV"


def write_errors(error_file: str, errors: list[str]) -> None:
    """Write parsing errors using the logging module."""
    logger = logging.getLogger("flight_parser")
    logger.setLevel(logging.WARNING)
    logger.propagate = False

    # Remove old handlers to avoid duplicate log entries.
    for old_handler in logger.handlers[:]:
        logger.removeHandler(old_handler)
        old_handler.close()

    handler = logging.FileHandler(
        error_file,
        mode="w",
        encoding="utf-8"
    )

    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    )

    logger.addHandler(handler)

    try:
        for error in errors:
            logger.warning(error)
    finally:
        logger.removeHandler(handler)
        handler.close()


def write_query_response(
    db: list[dict],
    query_file: str,
    response_folder: str
) -> None:
    """Execute queries and save the response JSON file."""

    with open(query_file, "r", encoding="utf-8") as file:
        queries = json.load(file)

    responses = run_queries(db, queries)

    os.makedirs(response_folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    response_filename = (
        f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{timestamp}.json"
    )

    response_path = os.path.join(response_folder, response_filename)

    with open(response_path, "w", encoding="utf-8") as file:
        json.dump(responses, file, indent=2, ensure_ascii=False)

    print(f"Query response created: {response_path}")


def main(argv: list[str] | None = None) -> int:
    """Run the program and return an exit code."""

    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description="Flight Schedule Parser and Query Tool"
    )

    source = parser.add_mutually_exclusive_group(required=True)

    source.add_argument(
        "-i",
        metavar="FILE",
        help="Input CSV file"
    )

    source.add_argument(
        "-d",
        metavar="FOLDER",
        help="Input folder containing CSV files"
    )

    source.add_argument(
        "-j",
        metavar="FILE",
        help="Input JSON database"
    )

    parser.add_argument(
        "-a",
        metavar="FILE",
        help="Airport codes file"
    )

    parser.add_argument(
        "-o",
        metavar="FILE",
        default="db.json",
        help="Output database file"
    )

    parser.add_argument(
        "-q",
        metavar="FILE",
        help="Query file"
    )

    parser.add_argument(
        "-r",
        metavar="FOLDER",
        default=".",
        help="Response output folder"
    )

    args = parser.parse_args(argv)

    # -o is not allowed with JSON input mode.
    if args.j and "-o" in argv:
        parser.error("-o cannot be used with -j")

    # --------------------------------------------------
    # Single CSV file mode
    # --------------------------------------------------

    if args.i:

        if not args.a:
            parser.error("-a FILE is required with -i")

        if not os.path.isfile(args.i):
            print(f"Error: Input file not found: {args.i}", file=sys.stderr)
            return 1

        if not os.path.isfile(args.a):
            print(f"Error: Airport file not found: {args.a}", file=sys.stderr)
            return 1

        try:
            airports = load_airports(args.a)

            records, errors = parse_files(
                [args.i],
                airports
            )

            with open(args.o, "w", encoding="utf-8") as file:
                json.dump(records, file, indent=2, ensure_ascii=False)

            output_directory = os.path.dirname(
                os.path.abspath(args.o)
            )

            error_file = os.path.join(
                output_directory,
                "errors.log"
            )

            write_errors(error_file, errors)

            print(f"Database created: {args.o}")
            print(f"Valid flights: {len(records)}")
            print(f"Errors: {len(errors)}")

            if args.q:
                write_query_response(
                    records,
                    args.q,
                    args.r
                )

        except (OSError, ValueError, json.JSONDecodeError) as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1

        return 0

    # --------------------------------------------------
    # Folder mode
    # --------------------------------------------------

    if args.d:

        if not args.a:
            parser.error("-a FILE is required with -d")

        if not os.path.isdir(args.d):
            print(f"Error: Folder not found: {args.d}", file=sys.stderr)
            return 1

        if not os.path.isfile(args.a):
            print(f"Error: Airport file not found: {args.a}", file=sys.stderr)
            return 1

        try:
            airports = load_airports(args.a)

            # Only CSV files directly inside the folder.
            # Do not process subdirectories.
            csv_files = []

            for filename in sorted(os.listdir(args.d)):
                full_path = os.path.join(args.d, filename)

                if (
                    os.path.isfile(full_path)
                    and filename.lower().endswith(".csv")
                ):
                    csv_files.append(full_path)

            if not csv_files:
                print(
                    f"Error: No CSV files found in folder: {args.d}",
                    file=sys.stderr
                )
                return 1

            records, errors = parse_files(
                csv_files,
                airports
            )

            with open(args.o, "w", encoding="utf-8") as file:
                json.dump(records, file, indent=2, ensure_ascii=False)

            output_directory = os.path.dirname(
                os.path.abspath(args.o)
            )

            error_file = os.path.join(
                output_directory,
                "errors.log"
            )

            write_errors(error_file, errors)

            print(f"Database created: {args.o}")
            print(f"CSV files found: {len(csv_files)}")
            print(f"Valid flights: {len(records)}")
            print(f"Errors: {len(errors)}")

            if args.q:
                write_query_response(
                    records,
                    args.q,
                    args.r
                )

        except (OSError, ValueError, json.JSONDecodeError) as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1

        return 0

    # --------------------------------------------------
    # JSON database mode
    # --------------------------------------------------

    if args.j:

        if not os.path.isfile(args.j):
            print(f"Error: JSON file not found: {args.j}", file=sys.stderr)
            return 1

        try:
            with open(args.j, "r", encoding="utf-8") as file:
                records = json.load(file)

            if not isinstance(records, list):
                raise ValueError(
                    "JSON database must contain a list"
                )

            print(f"Database loaded: {args.j}")
            print(f"Flights: {len(records)}")

            if args.q:
                write_query_response(
                    records,
                    args.q,
                    args.r
                )

        except (OSError, json.JSONDecodeError, ValueError) as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1

        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())




















