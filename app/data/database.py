# Author: Victor Hugo Garcia de Oliveira
# Date: 2025-12-21
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Este arquivo de código-fonte está sujeito aos termos da Mozilla Public
# License, v. 2.0. Se uma cópia da MPL não foi distribuída com este
# arquivo, você pode obter uma em https://mozilla.org/MPL/2.0/.
# Importa a função create_engine do SQLAlchemy para criar a conexão com o banco de dados.
from sqlalchemy import create_engine
# Importa a função sessionmaker para criar sessões de banco de dados.
from sqlalchemy.orm import sessionmaker
# Importa o contextmanager para criar gerenciadores de contexto (para a sessão do banco).
from contextlib import contextmanager
# Importa a classe Base declarativa da qual todos os modelos herdam.
from app.models.base import Base

import sys
from pathlib import Path
from app.core.config import CONFIG_DIR

# Define a URL de conexão para o banco de dados SQLite.
# Se estiver rodando como executável (frozen), usa o diretório de configuração do usuário.
# Caso contrário (desenvolvimento), usa o diretório atual.
if getattr(sys, 'frozen', False):
    # Garante que o diretório existe
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    db_path = CONFIG_DIR / "academic_management.db"
    DATABASE_URL = f"sqlite:///{db_path}"
else:
    DATABASE_URL = "sqlite:///academic_management.db"

# Cria a 'engine' do SQLAlchemy, que gerencia a conexão com o banco de dados.
# connect_args={"check_same_thread": False} é necessário para o SQLite permitir conexões de múltiplas threads,
# o que é comum em aplicações com interface gráfica.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# Cria uma classe 'SessionLocal' que será usada para criar novas sessões de banco de dados.
# autocommit=False e autoflush=False garantem que as transações sejam controladas manualmente.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define uma função para inicializar o banco de dados.
def init_db():
    """Cria as tabelas do banco de dados a partir dos modelos."""
    # O método create_all usa os metadados da classe Base para criar todas as tabelas definidas nos modelos.
    Base.metadata.create_all(bind=engine)

# Usa o decorador @contextmanager para transformar a função em um gerenciador de contexto.
@contextmanager
# Define uma função para obter uma sessão de banco de dados de forma segura.
def get_db_session():
    """Fornece um escopo transacional para uma série de operações."""
    # Cria uma nova instância de sessão a partir da classe SessionLocal.
    db = SessionLocal()
    try:
        # 'yield' entrega a sessão para o código que está dentro do bloco 'with'.
        yield db
        # Se o bloco 'with' for concluído sem erros, as alterações são 'comitadas' (salvas).
        db.commit()
    # Se ocorrer qualquer exceção dentro do bloco 'with'.
    except Exception:
        # As alterações são revertidas ('rollback') para manter a consistência dos dados.
        db.rollback()
        # A exceção é relançada para que possa ser tratada em outro lugar, se necessário.
        raise
    # O bloco 'finally' é executado sempre, independentemente de ter havido erro ou não.
    finally:
        # A sessão é fechada para liberar os recursos do banco de dados.
        db.close()
