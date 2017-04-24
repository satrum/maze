import asyncio
import functools


def event_handler(loop, stop=False):
    print('Вызван обработчик события')
    if stop:
        print('Цикл останавливается')
        loop.stop()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.call_soon(event_handler, loop)
        loop.call_later(1,event_handler, loop)
        loop.call_later(1,event_handler, loop)
        print('Цикл событий запускается')
        current_time = loop.time()
        loop.call_at(current_time+5,functools.partial(event_handler, loop, stop=True))

        loop.run_forever()
    finally:
        print('Завершаю цикл событий')
        loop.close()

