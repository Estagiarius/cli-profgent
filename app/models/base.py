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
# Importa a função declarative_base do SQLAlchemy ORM.
# Esta função é usada para criar uma classe base da qual todos os modelos ORM (tabelas) irão herdar.
from sqlalchemy.orm import declarative_base

# Cria a instância da classe Base.
# Qualquer classe de modelo que herdar de 'Base' será automaticamente registrada
# nos metadados do SQLAlchemy, permitindo que o ORM mapeie a classe para uma tabela no banco de dados.
Base = declarative_base()
