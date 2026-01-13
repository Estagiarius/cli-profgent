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
# Importa a biblioteca 'asyncio' para trabalhar com programação assíncrona (coroutines).
import asyncio
# Importa a biblioteca 'threading' para executar operações em threads separadas, em segundo plano.
import threading

# Define a função que executa uma tarefa assíncrona a partir de um contexto síncrono (como a UI).
def run_async_task(coro, loop, queue, callback):
    """
    Executa uma tarefa assíncrona em segundo plano utilizando uma thread separada. Este método é útil
    para integrar loops de eventos asyncio com aplicações que utilizam arquiteturas baseadas em threads.
    O resultado ou a exceção correspondente será enfileirado para processamento em outra thread,
    normalmente a thread principal.

    :param coro: Coroutine assíncrona a ser executada no loop de eventos.
    :type coro: Coroutine
    :param loop: Loop de eventos asyncio onde a coroutine será executada.
    :type loop: asyncio.AbstractEventLoop
    :param queue: Fila thread-safe que armazena o callback e o resultado (ou exceção) da coroutine.
    :type queue: queue.Queue
    :param callback: Função a ser chamada na thread principal com o resultado ou a exceção
        da execução da coroutine.
    :type callback: Callable
    :return: Nenhum valor é retornado diretamente pela função. O resultado do processamento
        é passado ao callback por meio da queue.
    """
    # Define uma função interna (wrapper) que será o alvo da nossa thread de segundo plano.
    def task_wrapper():
        # Esta função é executada em uma thread separada.
        # Ela submete a coroutine ao loop de eventos principal e aguarda pelo resultado.
        # `run_coroutine_threadsafe` é a forma segura de interagir com um loop asyncio de outra thread.
        future = asyncio.run_coroutine_threadsafe(coro, loop)
        try:
            # `future.result()` é uma chamada bloqueante, mas bloqueia APENAS esta thread de segundo plano,
            # não a thread principal da UI, que continua responsiva.
            result = future.result()
            # Assim que o resultado estiver pronto, coloca ele e a função de callback na fila thread-safe.
            # A thread principal irá ler desta fila para executar o callback.
            queue.put((callback, (result,)))
        except Exception as e:
            # Se a tarefa assíncrona levantar uma exceção, a exceção é enfileirada
            # para que o callback na thread principal possa tratá-la (ex: mostrar uma mensagem de erro).
            queue.put((callback, (e,)))

    # Cria a thread de segundo plano para gerenciar a tarefa assíncrona.
    thread = threading.Thread(target=task_wrapper)
    # Define a thread como 'daemon', o que significa que ela não impedirá o programa de fechar.
    thread.daemon = True
    # Inicia a execução da thread.
    thread.start()
