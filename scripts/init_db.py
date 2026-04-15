from app.core.db import initialize_database


def main() -> None:
    initialize_database()
    print("Database schemas and tables created.")


if __name__ == "__main__":
    main()
