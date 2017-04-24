import asyncio
import os
import urllib.request

async def download_coroutine(url):
    """
    Сопрограмма для загрузки данных по указанному url
    """
    request = urllib.request.urlopen(url)
    filename = os.path.basename(url)

    with open(filename, 'wb') as file_handle:
        while True:
            chunk = request.read(1024)
            if not chunk:
                break
            file_handle.write(chunk)
    msg = 'Завершена загрузка {filename}'.format(filename=filename)
    return msg

async def main(urls):
    """
    Создет группу сопрограмм и ожидает их завершения
    """
    print('1')
    coroutines = [download_coroutine(url) for url in urls]
    print('2')
    completed, pending = await asyncio.wait(coroutines)
    print('3')
    for item in pending:
        print(item.result())
    for item in completed:
        print(item.result())


if __name__ == '__main__':
    urls = ["http://www.irs.gov/pub/irs-pdf/f1040.pdf",
            "http://www.irs.gov/pub/irs-pdf/f1040a.pdf",
            "http://www.irs.gov/pub/irs-pdf/f1040ez.pdf",
            "http://www.irs.gov/pub/irs-pdf/f1040es.pdf",
            "http://www.irs.gov/pub/irs-pdf/f1040sb.pdf"]

    event_loop = asyncio.get_event_loop()
    try:
        event_loop.run_until_complete(main(urls))
        print('completed')
    finally:
        event_loop.close()