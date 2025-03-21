from PIL import Image
from screeninfo import get_monitors
from colorama import init, Fore, Style

def resize(path):
    init()
    for monitor in get_monitors():
        height = monitor.height -140
        width = monitor.width

    try:
        img = Image.open(path)
        # изменяем размер
        new_image = img.resize((width, height))
        # сохранение картинки
        new_image.save(path)
        print(Fore.GREEN + f'successfully resized {path}')
    except:
        print(Fore.RED + f'failed resize {path}')

if __name__ == '__main__':
    while True:
        path = input('Путь к файлy: ')
        resize(path)
