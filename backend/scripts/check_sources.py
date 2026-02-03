from sqlalchemy import text
from sqlmodel import Session

from app.database import engine


def check_sources():
    with Session(engine) as session:
        # Count by source
        query = text("SELECT source, COUNT(*), SUM(tokens) FROM token_usage GROUP BY source")
        result = session.execute(query).fetchall()

        print("--- Token Usage by Source ---")
        for row in result:
            print(f"Source: {row[0]}, Count: {row[1]}, Total Tokens: {row[2]}")


if __name__ == "__main__":
    check_sources()
