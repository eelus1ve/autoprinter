import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import ctypes
from ctypes.wintypes import MAX_PATH
from PIL import Image, ImageWin, ImageOps
import json
import win32print
import win32con
import win32ui
import datetime
import os
clear = lambda: os.system('cls')

path = ""
path_cach = ""
printer = ""

rgb_mode = False
save_size_mode = False
test_mode = False
global_area = (768, 1024)
worked_area = (56, 363)
sizes = (378, 268)


def work_with_printer(img, file):
    hDC = win32ui.CreateDC ()
    hDC.CreatePrinterDC (win32print.GetDefaultPrinter ())
    printable_area = hDC.GetDeviceCaps(win32con.HORZRES), hDC.GetDeviceCaps(win32con.VERTRES)
    printer_size = hDC.GetDeviceCaps(win32con.HORZRES), hDC.GetDeviceCaps(win32con.VERTRES)
    bmp = img
    if bmp.size[0] > bmp.size[1]:
        bmp = bmp.rotate (90)

    ratios = [1.0 * printable_area[0] / bmp.size[0], 1.0 * printable_area[1] / bmp.size[1]]
    scale = min (ratios)

    hDC.StartDoc (file)
    hDC.StartPage ()

    dib = ImageWin.Dib (bmp)
    scaled_width, scaled_height = [int (scale * i) for i in bmp.size]
    x1 = int ((printer_size[0] - scaled_width) / 2)
    y1 = int ((printer_size[1] - scaled_height) / 2)
    x2 = x1 + scaled_width
    y2 = y1 + scaled_height
    dib.draw (hDC.GetHandleOutput (), (x1, y1, x2, y2))
    hDC.EndPage ()
    hDC.EndDoc ()
    hDC.DeleteDC ()

def work_with_image(file, t=2):
    global save_size_mode, worked_area, global_area, test_mode, rgb_mode, sizes
    time.sleep(t)
    with Image.open(path+f"\{file}") as cropped_img:
        cropped_img.load()
    if test_mode:
        with Image.open(path+"\\test_back.jpg") as img:
            img.load()
    else:
        img = Image.new('RGB', global_area, color = (255,255,255))
    if save_size_mode:
        a = img.size[0]
        b = img.size[1]
        i = 1
        while (a/i > 504) or (b/i > 264):
            i+=0.25
        low_res_img = cropped_img.resize((a//i, b//i))
    else:
        low_res_img = cropped_img.resize(sizes)
    if not rgb_mode:
        low_res_img = ImageOps.grayscale(low_res_img)
        img = ImageOps.grayscale(img)
    else:
        pass
    img.paste(low_res_img, worked_area)
    if test_mode:
        img.show()
    else:
        work_with_printer(img, file) 

def work_with_file(file):
    # with open(path_cach+"\worked_files.txt", "a") as f:
        # f.write(f"{datetime.datetime.now()} - {file}"+"\n")
    work_with_image(file)

def add_log(log):
    with open(path_cach+"\logs.txt", "a") as f:
        f.write(f"{datetime.datetime.now()} - {log}"+"\n")

class EventHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.event_type == "created" and not event.is_directory:
            global path
            l = len(path) if path[-1] == "\\" else len(path)+1
            if event.src_path[l:].split(".")[-1].upper() in ["JPG", "JPEG", "PNG", "WEBP", "GIF", "RAW", "TIFF", "PSD", "SVG", "EPS", "PDF", "AI", "CDR"]:
                work_with_file(event.src_path[l:])

def on_folder_update():
    global path
    event_handler = EventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt as e:
        print(e)
        add_log(e)
        observer.stop()
    observer.join()

def create_cach_dir():
    global path_cach
    CSIDL_PERSONAL = 5
    shell32 = ctypes.windll.shell32
    buf = ctypes.create_unicode_buffer(MAX_PATH + 1)
    shell32.SHGetSpecialFolderPathW(None, buf, CSIDL_PERSONAL, False)
    path_cach = f"{buf.value}\\Autoprinter"
    if not "Autoprinter" in os.listdir(buf.value):
        os.mkdir(path_cach)
    open(path_cach+"\\logs.txt", "a").close()
    if not os.path.exists(path_cach+"\\config.json"):
        with open(path_cach+"\\config.json", "w") as file:
            file.write('{}')
    else:
        with open(path_cach+"\\config.json", "r") as file:
            if not file.read():
                with open(path_cach+"\\config.json", "w") as file:
                    file.write('{}')

    with open(path_cach+"\\config.json", "r") as file:
        data: dict = json.load(file)
    if data == {}:
        data =  {
                        "device": {
                            "printer": printer,
                            "path": path
                        }, 
                        "image": {
                            "mode": {
                                "rgb": rgb_mode, 
                                "save_size": save_size_mode,
                                "test": test_mode
                            }, 
                            "global_area": global_area,
                            "worked_area": worked_area, 
                            "sizes": sizes
                        }
                    }
    with open(path_cach+"\\config.json", "w") as file:
        json.dump(data, file, indent=4)
    open(path_cach+"\\worked_files.txt", "a").close()

class Checkers:
    def check_printer():
        global printer
        try:
            if printer in [i[2] for i in win32print.EnumPrinters(3)]:
                return True
            return False
        except Exception as e:
            print(e)
            add_log(e)
            return False

    def check_path():
        global path
        try:
            if os.path.exists(path):
                return True
            return False
        except Exception as e:
            print(e)
            add_log(e)
            return False

    def check_test_image():
        global path, test_mode
        try:
            if os.path.exists(path+"\\test_back.jpg") or not test_mode:
                return True
            return False
        except Exception as e:
            print(e)
            add_log(e)
            return False
        
    def check_global_area():
        global global_area, worked_area, sizes
        try:
            if global_area[0] >= worked_area[0] and global_area[0] >= sizes[0] and global_area[1] >= worked_area[1] and global_area[1] >= sizes[1]:
                return True
            return False
        except Exception as e:
            print(e)
            add_log(e)
            return False
    
    def check_worked_area():
        global global_area, worked_area, sizes
        try:
            if worked_area[0] >= 0 and worked_area[0] <= global_area[0] and worked_area[0] <= global_area[1] and worked_area[1] >= 0 and worked_area[1] <= global_area[0] and worked_area[1] <= global_area[1]:
                return True
            return False
        except Exception as e:
            print(e)
            add_log(e)
            return False
        
    def check_sizes():
        global global_area, worked_area, sizes
        try:
            if sizes[0] <= global_area[0] and sizes[1] <= global_area[1]:
                return True
            return False
        except Exception as e:
            print(e)
            add_log(e)
            return False

    def main():
        global path, path_cach, printer, rgb_mode, save_size_mode, test_mode, global_area, worked_area, sizes
        while not Checkers.check_printer():
            print(f"Принтер {printer} не обнаружен попробуйте другой или переподключить принтер.")
            Settings.set_printer()
        while not Checkers.check_path():
            print(f"Путь {path} не существует")
            Settings.set_path()
        while not Checkers.check_test_image():
            print(f"Неизвестная ошибка")
            Settings.set_test_image()
        while not Checkers.check_global_area() or not Checkers.check_worked_area() or not Checkers.check_sizes():
            try:
                print("Укажите правильные настройки областей")
                a = int(input(f"Ваши настройки: \n\n1. Размер шаблона {global_area}\n2. Рабочая область {worked_area}\n3. Стороны изображения {sizes}\n4. Сохранить\n\nВведите номер настройки которую хотите изменить: \n"))
                if a == 1:
                    Settings.set_global_area()
                    clear()
                elif a == 2:
                    Settings.set_worked_area()
                    clear()
                elif a == 3:
                    Settings.set_sizes()
                    clear()
                else:
                    raise NameError
            except Exception as e:
                clear()
                print("Некоректный ввод попробуйте ещё раз.\n\n")

class Settings:
    def set_printer():
        global printer
        while True:
            try:
                printers = [i for i in win32print.EnumPrinters(3)] + [("", "", "Принтера нет в списке")]
                printer = printers[int(input("Выберете принтер для дальнейшей работы: \n" + "\n".join([f"{i+1}. "+printers[i][2] for i in range(len(printers))]) + "\n"))-1][2]
                if printer == "Принтера нет в списке":
                    raise NameError("normal_er")
                clear()
                break
            except Exception as e:
                clear()
                if str(e) != "normal_er":
                    print("Некоректный ввод попробуйте ещё раз.\n\n")

    def set_path():
        global path
        while True:
            try:
                path = input(f"Введите путь до рабочей папки (при пропуске будет выбрана текущая папка: {os.getcwd()})\n")
                path = path if path else os.getcwd()
                if Checkers.check_path():
                    clear()
                    break
                else:
                    raise NameError
            except Exception as e:
                clear()
                print("Некоректный ввод попробуйте ещё раз.\n\n")

    def set_rgb_mode():
        global rgb_mode
        rgb_mode = not rgb_mode

    def set_save_size_mode():
        global save_size_mode
        save_size_mode = not save_size_mode

    def set_test_image():
        global path
        if not Checkers.check_test_image():
            print(f"Положите в папку (путь до папки: {path}) изображение с названием test_back.jpg")
            while not Checkers.check_test_image():
                time.sleep(1)

    def set_test_mode():
        global test_mode
        test_mode = not test_mode
        if test_mode:
            Settings.set_test_image()
        
    def set_global_area():
        global global_area
        while True:
            try:
                a = input(f"Введите размер вашего шаблона в px\n Пример ввода: 768, 1024\n")
                global_area = list(map(int, a.split(", ")))
                break
            except Exception as e:
                clear()
                print("Некоректный ввод попробуйте ещё раз.\n\n")

    def set_worked_area():
        global worked_area
        while True:
            try:
                a = input(f"Введите параметр рабочей области\n Пример ввода: 768, 1024\n")
                worked_area = list(map(int, a.split(", ")))
                break
            except Exception as e:
                clear()
                print("Некоректный ввод попробуйте ещё раз.\n\n")

    def set_sizes():
        global sizes
        while True:
            try:
                a = input(f"Введите стороны вашего изображения в px\n Пример ввода: 768, 1024\n")
                sizes = list(map(int, a.split(", ")))
                break
            except Exception as e:
                clear()
                print("Некоректный ввод попробуйте ещё раз.\n\n")

    def main():
        global path, path_cach, printer, rgb_mode, save_size_mode, test_mode, global_area, worked_area, sizes
        clear()
        while True:
            try:
                a = int(input(f"Ваши настройки: \n\n1. Принтер {printer}\n2. Путь {path}\n3. RGB мод {py_to_ru(rgb_mode)}\n4. Мод сохранения сторон {py_to_ru(save_size_mode)}\n5. Тест режим {py_to_ru(test_mode)}\n6. Размер шаблона {global_area}\n7. Рабочая область {worked_area}\n8. Стороны изображения {sizes}\n9. Выйти\n\nВведите номер настройки которую хотите изменить: \n"))
                if a == 1:
                    clear()
                    Settings.set_printer()
                    clear()
                elif a == 2:
                    clear()
                    Settings.set_path()
                    clear()
                elif a == 3:
                    clear()
                    Settings.set_rgb_mode()
                    clear()
                elif a == 4:
                    clear()
                    Settings.set_save_size_mode()
                    clear()
                elif a == 5:
                    clear()
                    Settings.set_test_mode()
                    clear()
                elif a == 6:
                    clear()
                    Settings.set_global_area()
                    clear()
                elif a == 7:
                    clear()
                    Settings.set_worked_area()
                    clear()
                elif a == 8:
                    clear()
                    Settings.set_sizes()
                    clear()
                elif a == 9:
                    clear()
                    break
                else: 
                    raise NameError
            except Exception as e:
                clear()
                print("Некоректный ввод попробуйте ещё раз.\n\n")

def py_to_ru(_bool):
    if _bool:
        return "Вкл"
    return "Выкл"

def save():
    global path, path_cach, printer, rgb_mode, save_size_mode, test_mode, global_area, worked_area, sizes
    clear()
    while True:
        try:
            a = (int(input(f"Сохранить ваши настройки? \n\n1. Принтер {printer}\n2. Путь {path}\n3. RGB мод {py_to_ru(rgb_mode)}\n4. Мод сохранения сторон {py_to_ru(save_size_mode)}\n5. Тест режим {py_to_ru(test_mode)}\n6. Размер шаблона {global_area}\n7. Рабочая область {worked_area}\n8. Стороны изображения {sizes}\n\n1. Сохранить    2. Редактировать    3. Не сохранять \n"))-1)
            if not a:
                with open(path_cach+"\\config.json", "w") as file:
                    data = {
                        "device": {
                            "printer": printer,
                            "path": path
                        }, 
                        "image": {
                            "mode": {
                                "rgb": rgb_mode, 
                                "save_size": save_size_mode,
                                "test": test_mode
                            }, 
                            "global_area": global_area,
                            "worked_area": worked_area, 
                            "sizes": sizes
                        }
                    }
                    json.dump(data, file, indent=4)
                clear()
                break
            elif a == 1:
                Settings.main()
                clear()
            elif a == 2:
                clear()
                break
            else:
                raise NameError
        except Exception as e:
            clear()
            print("Некоректный ввод попробуйте ещё раз.\n\n")

def new_presets():
    Settings.set_printer()
    Settings.set_path()
    save()
        
def start_settings():
    global path, path_cach, printer, rgb_mode, save_size_mode, test_mode, global_area, worked_area, sizes
    create_cach_dir()
    while True:
        with open(path_cach+"\\config.json", "r") as file:
            data = json.load(file)
        clear()
        if data != {'device': {'printer': '', 'path': ''}, 'image': {'mode': {'rgb': False, 'save_size': False, 'test': False}, 'global_area': [768, 1024], 'worked_area': [56, 363], 'sizes': [378, 268]}}:
            printer = data['device']['printer']
            path = data['device']['path']

            rgb_mode = data['image']['mode']['rgb']
            save_size_mode = data['image']['mode']['save_size']
            test_mode = data['image']['mode']['test']
            global_area = data['image']['global_area']
            worked_area = data['image']['worked_area']
            sizes = data['image']['sizes']
            if not int(input(f"Хотите загрузиться с этими настройками?\n\n1. Принтер {data['device']['printer']}\n2. Путь {data['device']['path']}\n3. RGB мод {py_to_ru(data['image']['mode']['rgb'])}\n4. Мод сохранения сторон {py_to_ru(data['image']['mode']['save_size'])}\n5. Тест режим {py_to_ru(data['image']['mode']['test'])}\n6. Размер шаблона {data['image']['global_area']}\n7. Рабочая область {data['image']['worked_area']}\n8. Стороны изображения {data['image']['sizes']}\n\n1. Да    2. Нет \n"))-1:
                clear()
                print("Программа запущена!")
                break
            else:
                save()
        else:
            new_presets()
    with open(path_cach+"\\worked_files.txt", "r") as f:
        f = f.read()
    try:
        win32print.SetDefaultPrinterW(printer)
        win32print.SetDefaultPrinter(printer)
    finally:
        printer = win32print.GetDefaultPrinter()

def run():
    start_settings()
    Checkers.main()
    on_folder_update()


if __name__ == "__main__":
    run()
    # path = "C:\\Users\\Admin\\AppData\\Roaming\\BetterDiscord\\themes\\321.jpg"
    # with Image.open(path) as img:
    #     img.load()
    # img = ImageOps.grayscale(img)
    # img.show()