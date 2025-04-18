from PIL import Image
from screeninfo import get_monitors
from colorama import init, Fore, Style
from tqdm import tqdm

def resize(paths):
    init()
    for monitor in get_monitors():
        height = monitor.height -140
        width = monitor.width
    
    for path in tqdm(paths):
        try:
            img = Image.open(path)
            # изменяем размер
            new_image = img.resize((width, height))
            # сохранение картинки
            new_image.save(path+'resized')
            print(Fore.GREEN + f'successfully resized {path}')
        except:
            print(Fore.RED + f'failed resize {path}')

if __name__ == '__main__':
    while True:
        paths = input('Путь к файлy: ')
        resize(paths)
