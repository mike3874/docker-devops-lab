import psycopg
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


def get_connection():
    return psycopg.connect(
        host="db",
        dbname="mikeapp",
        user="mike",
        password="devpassword",
    )


class Note(BaseModel):
    title: str
    content: str


@app.on_event("startup")
def startup():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL
                )
            """)
        conn.commit()


app.get("/")
def home():
    return {
        "project": "Mike Docker DevOps Lab",
        "version": "v2",
        "status": "running"
    }

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/db-health")
def db_health():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()

    return {
        "database": "ok",
        "result": result[0]
    }


@app.post("/notes")
def create_note(note: Note):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO notes (title, content)
                VALUES (%s, %s)
                RETURNING id
                """,
                (note.title, note.content),
            )
            note_id = cur.fetchone()[0]

        conn.commit()

    return {
        "id": note_id,
        "title": note.title,
        "content": note.content
    }


@app.get("/notes")
def get_notes():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, title, content
                FROM notes
                ORDER BY id
            """)
            rows = cur.fetchall()

    return [
        {
            "id": row[0],
            "title": row[1],
            "content": row[2]
        }
        for row in rows
    ]
