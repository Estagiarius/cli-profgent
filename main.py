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
import logging
from sqlalchemy import inspect
from app.tui.app import TuiApp # Import TUI App instead of MainApp
from app.data.database import engine, Base
# Importa o DataService singleton (instância compartilhada) para garantir consistência com as ferramentas da IA
from app.services import data_service
# Importa o AssistantService
from app.services.assistant_service import AssistantService
from app.data.migrations import migrate_database
import sys
from pathlib import Path
from app.core.config import CONFIG_DIR

# Determina o arquivo de log baseado no modo de execução (Frozen vs Dev)
if getattr(sys, 'frozen', False):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = CONFIG_DIR / "app.log"
else:
    log_file = "app.log"

# Configuração básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(log_file)),
        logging.StreamHandler()  # Também exibe no console para debug durante o desenvolvimento
    ]
)

def initialize_database():
    """
    Verifica e inicializa o banco de dados de forma robusta.
    Usa 'inspect' para verificar tabelas em vez de apenas a existência do arquivo.
    Isso previne erros quando o arquivo existe mas está vazio ou corrompido.
    """
    try:
        inspector = inspect(engine)
        # Obtém as tabelas existentes no banco
        existing_tables = inspector.get_table_names()

        if not existing_tables:
            logging.info("Banco de dados vazio ou inexistente. Criando nova estrutura de tabelas...")
            Base.metadata.create_all(bind=engine)
            logging.info("Banco de dados inicializado com sucesso.")
        else:
            logging.info(f"Banco de dados encontrado com as seguintes tabelas: {', '.join(existing_tables)}")
            # Executa create_all mesmo assim para garantir que qualquer nova tabela definida no código seja criada.
            # O create_all do SQLAlchemy é inteligente e ignora tabelas que já existem.
            Base.metadata.create_all(bind=engine)

    except Exception as e:
        logging.critical(f"Falha crítica na inicialização do banco de dados: {e}")
        # Relança a exceção para ser capturada no bloco principal e encerrar o programa
        raise

def main():
    try:
        logging.info("Iniciando o Profgent TUI...")

        # 1. Inicializa a camada de dados
        initialize_database()
        migrate_database(engine)

        # 2. Inicializa os serviços
        # O data_service já foi importado como singleton.
        # Inicializa o serviço do assistente (que carrega configurações e ferramentas)
        assistant_service = AssistantService()

        # 3. Inicializa a Interface Gráfica (TUI)
        logging.info("Inicializando interface TUI...")
        app = TuiApp(data_service=data_service, assistant_service=assistant_service)

        # 4. Inicia o loop principal
        app.run()

        logging.info("Aplicação encerrada pelo usuário.")

    except Exception as e:
        logging.critical(f"A aplicação encontrou um erro fatal e não pôde iniciar: {e}", exc_info=True)
        print(f"\nERRO FATAL: A aplicação falhou. Verifique o arquivo 'app.log' para detalhes.\nErro: {e}")

if __name__ == "__main__":
    main()
