from datetime import date

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from conexao_supabase import obter_conexao

app = FastAPI()


class AlunoCriar(BaseModel):
    nome: str
    email: str
    data_nascimento: date


@app.get("/")
def raiz():
    """A lista de alunos está em /alunos — a raiz não tem outro conteúdo."""
    return RedirectResponse(url="/alunos", status_code=307)


@app.get("/alunos")
def listar_alunos():
    """
    Retorna todos os registros da tabela "ALUNOS" em JSON.

    Se sua tabela tiver outro nome (ex: 'alunos' em vez de 'ALUNOS'),
    ajuste a query no SELECT.
    """
    conn = obter_conexao()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM "ALUNOS";')
            colunas = [desc[0] for desc in cur.description]
            rows = cur.fetchall()

            # Converte cada linha (tupla) em dicionário usando os nomes das colunas.
            return [dict(zip(colunas, row)) for row in rows]
    finally:
        conn.close()


@app.post("/alunos", status_code=status.HTTP_201_CREATED)
def criar_aluno(aluno: AlunoCriar):
    """Insere um aluno com nome, email e data_nascimento."""
    conn = obter_conexao()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO "ALUNOS" (nome, email, data_nascimento) '
                "VALUES (%s, %s, %s) RETURNING *;",
                (aluno.nome, aluno.email, aluno.data_nascimento),
            )
            colunas = [desc[0] for desc in cur.description]
            row = cur.fetchone()
            conn.commit()
            return dict(zip(colunas, row))
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@app.put("/alunos/{aluno_id}")
def atualizar_aluno(aluno_id: int, aluno: AlunoCriar):
    """Atualiza nome, email e data_nascimento do aluno pelo id."""
    conn = obter_conexao()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'UPDATE "ALUNOS" SET nome = %s, email = %s, data_nascimento = %s '
                "WHERE id = %s RETURNING *;",
                (aluno.nome, aluno.email, aluno.data_nascimento, aluno_id),
            )
            row = cur.fetchone()
            if row is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Aluno não encontrado",
                )
            colunas = [desc[0] for desc in cur.description]
            conn.commit()
            return dict(zip(colunas, row))
    except HTTPException:
        conn.rollback()
        raise
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@app.delete("/alunos/{aluno_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_aluno(aluno_id: int) -> None:
    """Remove o aluno pelo identificador (coluna id)."""
    conn = obter_conexao()
    try:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM "ALUNOS" WHERE id = %s;', (aluno_id,))
            if cur.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Aluno não encontrado",
                )
            conn.commit()
    except HTTPException:
        conn.rollback()
        raise
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

