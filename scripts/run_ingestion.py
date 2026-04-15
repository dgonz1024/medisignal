import argparse

from app.core.db import SessionLocal, initialize_database
from app.ingestion.fetch_studies import ingest_study_pages


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch study records from ClinicalTrials.gov into the raw schema."
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=5,
        help="Maximum number of result pages to ingest in one run.",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=100,
        help="Number of studies to request per page.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    initialize_database()

    with SessionLocal() as session:
        response = ingest_study_pages(
            session=session,
            max_pages=args.max_pages,
            page_size=args.page_size,
        )

    print(response)


if __name__ == "__main__":
    main()
