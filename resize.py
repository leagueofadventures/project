from PIL import Image
from screeninfo import get_monitors

def resize(path):
    for monitor in get_monitors():
        height = monitor.height
        width = monitor.width

    img = Image.open(path)
    # изменяем размер
    new_image = img.resize((width, height))
    # сохранение картинки
    new_image.save(path)
    print('successfully resized')
