"""
Conexão simples ao PostgreSQL do Supabase via URL.

A URL fica no arquivo .env (não versionado) na variável DATABASE_URL.
"""

import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise SystemExit(
        "Defina DATABASE_URL no arquivo .env (veja .env.example)."
    )


def obter_conexao():
    """Abre uma conexão usando a string do Supabase."""
    return psycopg2.connect(DATABASE_URL)


def main():
    conn = obter_conexao()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            versao = cur.fetchone()[0]
            print("Conectado com sucesso.")
            print(versao[:80] + "...")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
