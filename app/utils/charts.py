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
import matplotlib
# Configura o backend 'Agg' antes de importar pyplot para evitar problemas com threads e GUI
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import tempfile
from typing import List, Dict, Any, Union

def create_grade_distribution_chart(data: Union[List[Dict[str, Any]], List[float]], course_name: str) -> str:
    """
    Gera e salva um gráfico da distribuição de notas (ou médias) de um curso específico.
    O gráfico é salvo em um arquivo temporário e retorna o caminho para o arquivo salvo.
    Caso não haja dados disponíveis, uma mensagem de aviso será exibida no gráfico.

    :param data: Lista de notas. Pode ser uma lista de dicionários (legado) contendo 'score',
                 ou uma lista direta de valores float (médias finais).
    :param course_name: Nome do curso cujas notas serão analisadas.
    :return: Caminho do arquivo temporário onde o gráfico gerado foi salvo.
    """
    # Create a temporary file path
    temp_dir = tempfile.gettempdir()
    output_path = os.path.join(temp_dir, "academic_app_chart.png")

    fig, ax = plt.subplots()

    if not data:
        ax.text(0.5, 0.5, 'Nenhum dado disponível para este curso.', horizontalalignment='center', verticalalignment='center')
    else:
        # Extrai os scores. Se for lista de dicts, extrai 'score'. Se for lista de floats, usa direto.
        scores = []
        if isinstance(data[0], dict):
             scores = [min(d['score'], 10) for d in data]
        else:
             scores = [min(v, 10) for v in data]

        ax.hist(scores, bins=10, range=(0, 10), edgecolor='black')
        ax.set_xlabel('Média Final')
        ax.set_ylabel('Número de Alunos')
        # Set ticks from 0 to 10
        ax.set_xticks(range(0, 11, 1))

    ax.set_title(f'Distribuição de Médias para {course_name}')

    plt.savefig(output_path)
    plt.close(fig)

    return output_path

def create_approval_pie_chart(approved: int, failed: int) -> str:
    """
    Gera um gráfico de pizza mostrando a proporção de aprovados vs reprovados.

    :param approved: Número de aprovações.
    :param failed: Número de reprovações.
    :return: Caminho do arquivo temporário com a imagem.
    """
    temp_dir = tempfile.gettempdir()
    output_path = os.path.join(temp_dir, "academic_app_pie_chart.png")

    fig, ax = plt.subplots(figsize=(5, 4))

    total = approved + failed
    if total == 0:
        ax.text(0.5, 0.5, 'Sem dados suficientes', horizontalalignment='center', verticalalignment='center')
        ax.axis('off')
    else:
        labels = ['Aprovados', 'Abaixo da Média']
        sizes = [approved, failed]
        colors = ['#66bb6a', '#ef5350'] # Green and Red compatible with dark mode

        # Only show labels if slice > 0
        labels = [l if s > 0 else '' for l, s in zip(labels, sizes)]

        ax.pie(sizes, labels=labels, colors=colors, autopct=lambda p: f'{p:.1f}%' if p > 0 else '',
               startangle=90, textprops={'color':"white" if plt.rcParams['figure.facecolor'] == 'black' else 'black'})
        ax.axis('equal')

    # Set transparent background to blend with CustomTkinter dark theme
    fig.patch.set_alpha(0.0)

    plt.savefig(output_path, transparent=True)
    plt.close(fig)
    return output_path
