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
# Importa a classe DataService do arquivo data_service.py, que está no mesmo diretório.
from .data_service import DataService

# Cria uma instância única e compartilhada do DataService.
# Esta instância será importada por outras partes da aplicação (por exemplo, as 'tools' da IA)
# para garantir que todos usem o mesmo objeto de serviço.
# Isso ajuda a manter um estado consistente e a gerenciar as conexões com o banco de dados de forma centralizada.
data_service = DataService()
