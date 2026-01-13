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
# Importa as bibliotecas necessárias para os testes.
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pytest_mock import MockerFixture
from contextlib import contextmanager

# Importa a Base e os serviços/modelos da aplicação.
from app.models.base import Base
from app.services.data_service import DataService
# É crucial importar todos os modelos aqui para garantir que a Base.metadata
# conheça todas as tabelas antes de `create_all` ser chamado.
from app.models.student import Student  # noqa: F401
from app.models.course import Course  # noqa: F401
from app.models.grade import Grade  # noqa: F401
from app.models.class_ import Class  # noqa: F401
from app.models.class_enrollment import ClassEnrollment  # noqa: F401
from app.models.assessment import Assessment  # noqa: F401
from app.models.lesson import Lesson  # noqa: F401
from app.models.incident import Incident  # noqa: F401

# Define uma 'fixture' do pytest. Fixtures são funções que fornecem um ambiente ou dados
# consistentes para os testes. `scope="function"` significa que esta fixture será
# executada uma vez para cada função de teste.
@pytest.fixture(scope="function")
def db_session() -> Session:
    """
    Fixture do Pytest que cria uma nova sessão de banco de dados SQLite em memória
    para cada função de teste. Isso garante que os testes sejam isolados uns dos outros.
    """
    # Cria uma 'engine' do SQLAlchemy para um banco de dados SQLite que existe apenas na memória RAM.
    engine = create_engine("sqlite:///:memory:")
    # Cria todas as tabelas definidas nos modelos importados neste banco de dados em memória.
    Base.metadata.create_all(engine)
    # Cria uma fábrica de sessões ligada a este banco de dados.
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = session_factory()
    # 'yield' entrega a sessão para a função de teste que a solicitou.
    # O código após o 'yield' é executado após o término do teste.
    yield session
    # Fecha a sessão para liberar recursos.
    session.close()
    # Remove todas as tabelas do banco de dados em memória, limpando o ambiente para o próximo teste.
    Base.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def data_service(db_session: Session, mocker: MockerFixture) -> DataService:
    """
    Fixture do Pytest que cria uma instância do DataService onde todas as interações
    com o banco de dados são 'mockadas' (simuladas) para usar a sessão de teste
    isolada e em memória.
    """
    # Cria um gerenciador de contexto falso que, em vez de criar uma nova sessão,
    # simplesmente fornece a sessão de teste (`db_session`) que já foi criada.
    @contextmanager
    def mock_get_db_session():
        yield db_session

    # Usa o `mocker` do pytest-mock para substituir a função `get_db_session` real.
    # Com a refatoração para serviços dedicados, o patch deve ser aplicado no BaseDataService.
    mocker.patch("app.services.data.base_service.get_db_session", new=mock_get_db_session)

    # Cria uma instância do DataService. Agora, sempre que este serviço tentar
    # obter uma sessão de banco de dados, ele receberá a sessão de teste em memória.
    service = DataService()
    return service

@pytest.fixture(scope="function")
def assistant_service(mocker: MockerFixture) -> "AssistantService":
    """
    Fixture do Pytest que cria uma nova instância do AssistantService para cada teste,
    com a inicialização do provedor de IA 'mockada' para evitar o carregamento pesado
    e chamadas de rede reais.
    """
    # Importamos o AssistantService aqui dentro para evitar problemas de dependência circular.
    from app.services.assistant_service import AssistantService

    # 'Mocka' o método que inicializa o provedor de LLM, que pode ser pesado
    # (carregar modelos, fazer chamadas de rede, etc.).
    mocker.patch("app.services.assistant_service.AssistantService._initialize_provider")

    service = AssistantService()
    # Como a inicialização foi 'mockada', precisamos definir manualmente um provedor falso
    # para quaisquer testes que possam precisar dele. `MagicMock` é um objeto flexível
    # que simula qualquer atributo ou método que for acessado nele.
    service.provider = mocker.MagicMock()

    return service

# Fixture com escopo de 'session' (executada apenas uma vez por sessão de teste).
@pytest.fixture(scope="session")
def anyio_backend():
    # Força o pytest-anyio a usar o backend 'asyncio', evitando erros se outros
    # backends como 'trio' não estiverem instalados.
    return "asyncio"
