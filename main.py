import flet as ft
import base64
from io import BytesIO
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
from PIL import Image, ImageWin, ImageOps
import json
import win32print
import win32con
import win32ui
import asyncio
from typing import Literal, Callable


def main(page: ft.Page):
	global global_area, save_size_mode, worked_area, sizes, path_template, rgb_mode, printers, printer, config_name, log_path, language, theme, select_file, select_floader, image_holder_settings, image_holder_floader, set_image, conf_open, start_b, rg_pr, sl_wa_wh, sl_wa_hg, sl_sz_wh, sl_sz_hg, sl_tr, end_tb, cb_rgb, dd_ss, dd_lang, dd_conf, w_path, sl_ss_mod, progress, floader, file_img, tf_wa_wh, tf_wa_hg, tf_sz_wh, tf_sz_hg, tf_ss_mod, tf_tr, tr, welc_row, zow
 
	printers = [i for i in win32print.EnumPrinters(3)]

	start_b = False
	w_path = ""
	printer = ""
	log_path = ""
	path_template = ""
	config_name = ""
	conf_open = False
	language = ""
	theme = "dark"

	rgb_mode = True
	save_size_mode = "16:9"

	progress = [False, False, False, False]
	dd_lang = None
	dd_conf = None
	dd_ss = None
	cb_rgb = None
	file_img = None
	floader = None
	set_image = None
	sl_wa_wh = None
	sl_wa_hg = None
	sl_sz_wh = None
	sl_sz_hg = None
	sl_ss_mod = None
	sl_tr = None
	end_tb = None
	rg_pr = None
	tf_wa_wh = None
	tf_wa_hg = None
	tf_sz_wh = None
	tf_sz_hg = None
	tf_tr = None
	tr=0
	zow = False

	page.title = "Autoprinter"
	page.vertical_alignment = ft.MainAxisAlignment.CENTER
	page.theme_mode = theme
	page.window.min_wight = 1053
	page.window.min_height = 590
	page.window.width = 1124
	page.window.height = 720

	progress = [False, False, False, False]


	welc = {"dark": "#a0cafd", "light": "#001d36"}
	welc_row = ft.Row([ft.Text("WELCOME", color=welc[page.theme_mode], size=50), ], alignment=ft.MainAxisAlignment.CENTER)

	select_file = ft.Text()
	select_floader = ft.Text()
	image_holder_settings = ft.Image(width=400, height=400, visible=False, fit=ft.ImageFit.CONTAIN)
	image_holder_floader = ft.Image(width=100, height=100, visible=False, fit=ft.ImageFit.CONTAIN)


	global_area = (768, 1024)
	worked_area = (2, 2)
	sizes = (1, 1)

	class NumberField(ft.TextField):
		def __init__(self,
					on_change: Callable[[ft.ControlEvent], None] = None,
					input_type: Literal["int", "float"] = "int",
					**kwargs):
			super().__init__(**kwargs)

			if input_type not in ("int", "float"):
				raise ValueError("Input must be 'int' or 'float'")

			self.input_type = input_type
			self.keyboard_type = ft.KeyboardType.NUMBER

			self.custom_on_change = self._custom_on_change
			self.user_on_change = on_change
			self.last_value = self.value

		def _custom_on_change(self, e):
			try:
				e.control.value = int(e.control.value) if self.input_type == "int" else float(e.control.value)
			except ValueError as er:
				e.control.value = (0 if er.args == ("invalid literal for int() with base 10: ''", ) else self.last_value)
				e.control.update()
				if self.user_on_change:
					self.user_on_change(e)
			else:
				self.last_value = e.control.value
				if self.user_on_change:
					self.user_on_change(e)

		def build(self):
			self.on_change = self.custom_on_change
			return super().build()

	class TextIntoSlider(NumberField):
		def __init__(self, value=None, **kwargs):
			super().__init__(width=50, text_size=10, height=40, text_align=ft.MainAxisAlignment.START, value=value, on_change=tf_update, **kwargs)

	class Lang:
		def __init__(self, lang: str):
			self.lang = lang
	
			self.on = "Вкл"
			self.off = "Выкл"

			self.nav_1 = "Приветствуем!"
			self.nav_2 = "Выбор принтера"
			self.nav_3 = "Выбор путей"
			self.nav_4 = "Настройки печати"
			self.nav_5 = "Готово!"

			self.welcome = "WELCOME"
			self.fp_lang = "Выберите язык"
			self.fp_config = "Выберите конфиг"
			self.fp_dark_mode = "Тёмная тема"
			self.fp_zow = "Сохранять размеры окна"
			self.fp_no_conf = "Продолжить без конфига"
			
			self.printer = "Принтера нет в списке"


			self.pf_template_button = "Выберите файл с шаблоном"
			self.pf_no_template = "Файл не выбран!"
			self.pf_template_file = "Файл: "
			self.pf_template_path = "Путь: "

			self.pf_work_button = "Выберите рабочую папку"
			self.pf_no_work = "Директория не выбрана!"
			self.pf_work_file = "Папка: "
			self.pf_work_path = "Путь: "


			self.set_left = "Отступ слева"
			self.set_up = "Отступ сверху"
			self.set_wight = "Ширина изображения"
			self.set_height = "Высота изображения"
			self.set_trans = "Цвет"
			self.set_rgb = "RGB мод"
			self.set_ssm = "Режим сохранения сторон"
			self.set_button = "Открыть изображение"
			self.set_sl_ssmod = "Размер картинки"

			self.endp_config = "Конфиг: "
			self.endp_printer = "Принтер: "
			self.endp_path_work = "Путь к рабочей папке: "
			self.endp_path_template = "Путь к шаблону: "
			self.endp_rgb_mod = "RGB мод: "
			self.endp_save_size_mod = "Сохренение сторон: "
			self.endp_global_size = "Размер шаблона: "
			self.endp_left = "Отступ слева "
			self.endp_up = "Отступ сверху "
			self.endp_size = "Размер изображения: "
			self.endp_config_input = "Введите название конфига"
			self.endp_button = "Сохранить"
	
			if self.lang == "ua":
		
				self.on = "Вкл"
				self.off = "Вимкнено"
				
				self.nav_1 = "Вітаємо!"
				self.nav_2 = "Вибір принтера"
				self.nav_3 = "Вибір шляхів"
				self.nav_4 = "Налаштування друку"
				self.nav_5 = "Готово!"

				self.welcome = "WELCOME"
				self.fp_lang = "Виберіть мову"
				self.fp_config = "Виберіть конфігурацію"
				self.fp_dark_mode = "Темна тема"
				self.fp_zow = "Зберігати розміри вікна"
				self.fp_no_conf = "Продовжити без конфігурації"
				
				self.printer = "Принтера немає в списку"


				self.pf_template_button = "Виберіть файл із шаблоном"
				self .pf_no_template = " Файл не вибрано!"
				self .pf_template_file = "Файл: "
				self .pf_template_path = "Шлях: "

				self.pf_work_button = "Виберіть робочу папку"
				self .pf_no_work = " Директорія не вибрана!"
				self .pf_work_file = "Папка: "
				self .pf_work_path = "Шлях: "


				self.set_left = "Відступ зліва"
				self.set_up = "Відступ зверху"
				self.set_wight = "Ширина зображення"
				self.set_height = "Висота зображення"
				self.set_trans = "Колір"
				self.set_rgb = "RGB мод"
				self.set_ssm = "Режим збереження сторін"
				self.set_button = "Відкрити зображення"
				self.set_sl_ssmod = "Розмір зображення"


				self.endp_config = "Конфігурація: "
				self.endp_printer = "Принтер: "
				self.endp_path_work = "Шлях до робочої папки: "
				self.endp_path_template = "Шлях до шаблону: "
				self.endp_rgb_mod = "RGB мод: "
				self.endp_save_size_mod = "Збереження сторін: "
				self.endp_global_size = "Розмір шаблону: "
				self.endp_left = "Відступ зліва: "
				self.endp_up = "Відступ зверху: "
				self.endp_size = "Розмір зображення: "
				self.endp_config_input = "Введіть назву конфігурації"
				self.endp_button = "Зберегти"

			elif self.lang == "uk":
		
				self.on = "On"
				self.off = "Off"
		
				self.nav_1 = "Welcome!"
				self.nav_2 = "Printer selection"
				self.nav_3 = "Path selection"
				self.nav_4 = "Print settings"
				self.nav_5 = "Done!"

				self.welcome = "WELCOME"
				self.fp_lang = "Select language"
				self.fp_config = "Select a config"
				self.fp_dark_mode = "Dark Theme"
				self.fp_zow = "Save window sizes"
				self.fp_no_conf = "Continue without config"

				self.printer = "The printer is not in the list"


				self.pf_template_button = "Select the template file"
				self.pf_no_template = "No file selected!"
				self.pf_template_file = "File: "
				self.pf_template_path = "Path: "

				self.pf_work_button = "Select a working folder"
				self.pf_no_work = "Directory not selected!"
				self.pf_work_file = "Folder: "
				self.pf_work_path = "Path: "


				self.set_left = "Left indentation"
				self.set_up = "Top indentation"
				self.set_wight = "Image width"
				self.set_height = "Image height"
				self.set_trans = "Color"
				self.set_rgb = "RGB mode"
				self.set_ssm = "Side saving mode"
				self.set_button = "Open Image"
				self.set_sl_ssmod = "Image size"

				self.endp_config = "Config: "
				self.endp_printer = "Printer: "
				self.endp_path_work = "Path to the working folder: "
				self.endp_path_template = "Template path: "
				self.endp_rgb_mod = "RGB mod: "
				self.endp_save_size_mod = "Saving sides: "
				self.endp_global_size = "Template size: "
				self.endp_left = "Left indentation: "
				self.endp_up = "Top margin: "
				self.endp_size = "Image size: "
				self.endp_config_input = "Enter the name of the config"
				self.endp_button = "Save"

		def py_to_lang(self, _bool):
			return (self.on if _bool else self.off)

	class EventHandler(FileSystemEventHandler):
		def on_any_event(self, event):
			if event.event_type == "created" and not event.is_directory:
				global w_path
				l = len(w_path) if w_path[-1] == "\\" else len(w_path)+1
				if event.src_path[l:].split(".")[-1].upper() in ["JPG", "JPEG", "PNG", "WEBP", "GIF", "RAW", "TIFF", "PSD", "SVG", "EPS", "PDF", "AI", "CDR"]:
					work_with_image(event.src_path)

	async def on_folder_update():
		global w_path, start_b
		event_handler = EventHandler()
		observer = Observer()
		observer.schedule(event_handler, w_path, recursive=True)
		observer.start()
		try:
			while True:
				if not start_b:
					observer.stop()
					break
				await asyncio.sleep(1)
		except KeyboardInterrupt as e:
			# add_log(e)
			observer.stop()
		observer.join()

	def start_log_func():
		global log_path, language, theme, zow
		log_path = os.getenv('APPDATA')
		if not "WaveTeam" in os.listdir(log_path):
			os.mkdir(f"{log_path}/WaveTeam")
		log_path = f"{log_path}/WaveTeam"
		if not "AutoPrinter" in os.listdir(log_path):
			os.mkdir(f"{log_path}/AutoPrinter")
		log_path = f"{log_path}/AutoPrinter"
		if not os.path.exists(log_path+"/presets.json"):
			with open(log_path+"/presets.json", "w") as file:
				file.write('{}')
		else:
			with open(log_path+"/presets.json", "r") as file:
				if not file.read():
					with open(log_path+"/presets.json", "w") as file:
						file.write('{}')
		with open(log_path+"/presets.json", "r") as file:
			data: dict = json.load(file)
			if data == {}:
				data = {
					"lang": "ru",
					"theme": "dark",
					"zow": ((1124, 720), False)
				}
				with open(log_path+"/presets.json", "w") as file:
					json.dump(data, file, indent=4)
			language = Lang(data["lang"])
			theme = data["theme"]
			zow = data["zow"][1]
			if zow:
				page.window.width = data["zow"][0][0]
				page.window.height = data["zow"][0][1]

	def work_with_test_image():
		global global_area, save_size_mode, worked_area, sizes, path_template, rgb_mode, tr
		sizes = tuple(map(int, sizes))
		worked_area = tuple(map(int, worked_area))
		ssmn = True
		if save_size_mode == "OFF":
			ssmn = False
		cropped_img = Image.new('RGB', sizes, "#"+"0"*(6-len(hex(tr)[2:]))+str(hex(tr)[2:]))
		cropped_img.load()
		with Image.open(path_template) as img:
			width, height = img.size
			img.load()
		global_area = (width, height)
		if ssmn:
			ssmn = tuple(map(int, save_size_mode.split(":")))
			a = ssmn[0]*1000
			b = ssmn[1]*1000
			i = 1
			while (a/i > sizes[0]) or (b/i > sizes[1]):
				i+=0.25
			if 0 not in ((int(a//i), int(b//i))):
				low_res_img = cropped_img.resize((int(a//i), int(b//i)))
			else:
				low_res_img = cropped_img.resize(sizes)
		else:
			low_res_img = cropped_img.resize(sizes)
		if not rgb_mode:
			low_res_img = ImageOps.grayscale(low_res_img)
			img = ImageOps.grayscale(img)
		img.paste(low_res_img, worked_area)
		return img

	def work_with_image(path_file, t=2):
		global global_area, save_size_mode, worked_area, sizes, rgb_mode
		sizes = tuple(map(int, sizes))
		worked_area = tuple(map(int, worked_area))
		ssmn = True
		if save_size_mode == "OFF":
			ssmn = False
		time.sleep(t)
		with Image.open(path_file) as cropped_img:
			cropped_img.load()
		img = Image.new('RGB', global_area, color = (255,255,255))
		if ssmn:
			ssmn = tuple(map(int, save_size_mode.split(":")))
			a = ssmn[0]*1000
			b = ssmn[1]*1000
			i = 1
			while (a/i > 504) or (b/i > 264):
				i+=0.25
			if 0 not in ((int(a//i), int(b//i))):
				low_res_img = cropped_img.resize((int(a//i), int(b//i)))
			else:
				low_res_img = cropped_img.resize(sizes)
		else:
			low_res_img = cropped_img.resize(sizes)
		if not rgb_mode:
			low_res_img = ImageOps.grayscale(low_res_img)
			img = ImageOps.grayscale(img)
		img.paste(low_res_img, worked_area)
		work_with_printer(img, path_file) 
	
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

	def json_load(conf_name):
		global global_area, save_size_mode, worked_area, sizes, path_template, rgb_mode, printers, printer, config_name, log_path, select_file, select_floader, image_holder_settings, image_holder_floader, set_image, conf_open, w_path, progress, tr
		with open(log_path+f"/{conf_name}config.json", "r") as file:
			data: dict = json.load(file)
		config_name = conf_name
		w_path = data["device"]["path"]
		printer = data["device"]["printer"]
		path_template = data["device"]["template"]
		rgb_mode = data["image"]["mode"]["rgb"]
		save_size_mode = data["image"]["mode"]["save_size"]
		tr = data["image"]["color"]
		global_area = data["image"]["global_area"]
		worked_area = data["image"]["worked_area"]
		sizes = data["image"]["sizes"]
		k1= path_template.split('\\')[-1]
		k2 = w_path.split('\\')[-1]
		select_file.value = f"{language.pf_template_file}{k1}\n{language.pf_template_path}{path_template}"
		select_floader.value = f"{language.pf_work_file}{k2}\n{language.pf_work_path}{w_path}"
		with open(path_template, 'rb') as r:
			image_holder_floader.src_base64= base64.b64encode(r.read()).decode("utf-8")
			image_holder_floader.visible=True
		set_image = work_with_test_image()
		buffered = BytesIO()
		set_image.save(buffered, format="JPEG")
		image_holder_settings.src_base64= base64.b64encode(buffered.getvalue()).decode("utf-8")
		image_holder_settings.visible=True
		# progress = [True, True, True, True]
		
	def full_page_update(e):
		page.clean()
		sl_update()
		tf_update()
		page.add(gen_set_page())
		page.update()

	def sl_update(e=None):
		global worked_area, sizes, save_size_mode, tr
  
		tf_wa_wh.value = int(sl_wa_wh.value)
		tf_wa_hg.value = int(sl_wa_hg.value)
		tf_sz_wh.value = int(sl_sz_wh.value)
		tf_sz_hg.value = int(sl_sz_hg.value)
		tf_ss_mod.value = int(sl_ss_mod.value)
		tr = int(sl_tr.value)
  
		worked_area = (sl_wa_wh.value, sl_wa_hg.value)
		if save_size_mode == "OFF":
			sizes = (sl_sz_wh.value, sl_sz_hg.value)
		else:
			sizes = (sl_ss_mod.value, sl_ss_mod.value)
		img_update(set_image)
  
	def tf_update(e=None):
		global worked_area, sizes, save_size_mode, tr

		sl_wa_wh.value = tf_wa_wh.value
		sl_wa_hg.value = tf_wa_hg.value
		sl_sz_wh.value = tf_sz_wh.value
		sl_sz_hg.value = tf_sz_hg.value
		sl_ss_mod.value = tf_ss_mod.value
  
		worked_area = (tf_wa_wh.value, tf_wa_hg.value)
		if save_size_mode == "OFF":
			sizes = (tf_sz_wh.value, tf_sz_hg.value)
		else:
			sizes = (tf_ss_mod.value, tf_ss_mod.value)
		img_update(set_image)
	
	def change_progress(count):
		progress = [True]*(count)+[False]*(4-count)
		
	def change_printer(e):
		global printer
		printer = e.data
		if printer != "":
			page.floating_action_button.disabled = False
		page.update()

	def change_button(name, ic, func):
		if page.theme_mode == "dark":
			page.floating_action_button = ft.FloatingActionButton(text=name, icon=ic, bgcolor="#111418", on_click=func)
			page.floating_action_button_location = ft.FloatingActionButtonLocation.CENTER_FLOAT
		else:
			page.floating_action_button = ft.FloatingActionButton(text=name, icon=ic, bgcolor="#f8f9ff", on_click=func)
			page.floating_action_button_location = ft.FloatingActionButtonLocation.CENTER_FLOAT

	def start_func(e=None, swap=True):
		global start_b
		if swap:
			start_b = not start_b
		if not start_b:
			if page.theme_mode == "dark":
				page.floating_action_button = ft.FloatingActionButton(text="START", bgcolor="#111418", on_click=start_func)
			else:
				page.floating_action_button = ft.FloatingActionButton(text="START", bgcolor="#f8f9ff", on_click=start_func)
			page.floating_action_button_location = ft.FloatingActionButtonLocation.CENTER_FLOAT

		else:
			if page.theme_mode == "dark":
				page.floating_action_button = ft.FloatingActionButton(text="STOP", bgcolor="#b00000", foreground_color="#babbc1", on_click=start_func)
			else:
				page.floating_action_button = ft.FloatingActionButton(text="STOP", bgcolor="#f80000", foreground_color="#f8f9ff", on_click=start_func)
			page.floating_action_button_location = ft.FloatingActionButtonLocation.CENTER_FLOAT
			page.run_task(on_folder_update)
		page.update()

	def navigate(e=None):
		index = page.navigation_bar.selected_index
		page.clean()

		if index == 0:
			page.add(gen_fp_page())
			change_button("NEXT", ft.icons.ARROW_FORWARD, new_progress)
		elif index == 1:
			page.add(gen_printer_page())
			change_button("NEXT", ft.icons.ARROW_FORWARD, new_progress)
			page.floating_action_button.disabled = True
			if printer != "":
				page.floating_action_button.disabled = False
		elif index == 2:
			change_button("NEXT", ft.icons.ARROW_FORWARD, new_progress)
			page.floating_action_button.disabled = True
			page.add(gen_floader_page())
			if (select_file.value != None and select_file.value != language.pf_no_template) and (select_floader.value != language.pf_no_work and select_floader.value != None and "None" not in select_floader.value):
				page.floating_action_button.disabled = False
			else:
				change_progress(2)
				page.navigation_bar = change_nav(2, 2)
		elif index == 3:
			page.add(gen_set_page())
			change_button("NEXT", ft.icons.ARROW_FORWARD, new_progress)
		else: 
			page.add(gen_start_page())
			start_func(swap=False)
		page.update()

	def change_nav(count=0, start_pos=0)-> ft.NavigationBar:
		nav_list = [
			ft.NavigationBarDestination(icon=ft.icons.WAVING_HAND, label=language.nav_1),
			ft.NavigationBarDestination(icon=ft.icons.LOCAL_PRINT_SHOP, label=language.nav_2),
			ft.NavigationBarDestination(icon=ft.icons.FOLDER, label=language.nav_3),
			ft.NavigationBarDestination(icon=ft.icons.SETTINGS , label=language.nav_4),
			ft.NavigationBarDestination(icon=ft.icons.CHECK_CIRCLE, label=language.nav_5)
		]
		return ft.NavigationBar(destinations=nav_list[:1+count], selected_index=start_pos, on_change=navigate)

	def new_progress(e):
		global progress
		page.clean()

		
		index = page.navigation_bar.selected_index
		if config_name:
			regen_set_page()
			progress = [True, True, True, True]
		elif not progress[index]:
			progress[index] = True
		counter = progress.count(True)
		page.navigation_bar = change_nav(count=counter, start_pos=counter)
		if counter == 0:
			page.add(gen_fp_page())
			change_button("NEXT", ft.icons.ARROW_FORWARD, new_progress)
		elif counter == 1:
			page.add(gen_printer_page())
			change_button("NEXT", ft.icons.ARROW_FORWARD, new_progress)
			page.floating_action_button.disabled = True
			if printer != "":
				page.floating_action_button.disabled = False
		elif counter == 2:
			change_button("NEXT", ft.icons.ARROW_FORWARD, new_progress)
			page.floating_action_button.disabled = True
			page.add(gen_floader_page())
			if (select_file.value != None and select_file.value != language.pf_no_template) and (select_floader.value != language.pf_no_work and select_floader.value != None and "None" not in select_floader.value):
				page.floating_action_button.disabled = False
			else:
				change_progress(2)
				page.navigation_bar = change_nav(2, 2)
		elif counter == 3:
			page.add(gen_set_page())
			change_button("NEXT", ft.icons.ARROW_FORWARD, new_progress)
		else: 
			page.add(gen_start_page())
			start_func(swap=False)
		page.update()

	def swap_lang(e):
		global language, select_file, select_floader
		l1 = ("", )
		l2 = ("", )
		if select_file.value != None:
			if language.pf_no_template == select_file.value:
				l1 = (language.pf_no_template, )
			if language.pf_template_file in select_file.value:
				l1 = (language.pf_template_file, language.pf_template_path)
		if select_floader.value != None:
			if language.pf_no_work == select_floader.value:
				l2 = (language.pf_no_work, )
			if language.pf_work_file in select_floader.value:
				l2 = (language.pf_work_file, language.pf_work_path)
		language = Lang(e.data)
		if select_file.value != None:
			if len(l1) == 1:
				select_file.value = select_file.value.replace(l1[0], language.pf_no_template)
			else:
				select_file.value = select_file.value.replace(l1[0], language.pf_template_file).replace(l1[1], language.pf_template_path)
		if select_floader.value != None:
			if len(l2) == 1:
				select_floader.value = select_floader.value.replace(l2[0], language.pf_no_work)
			else:
				select_floader.value = select_floader.value.replace(l2[0], language.pf_work_file).replace(l2[1], language.pf_work_path)
		page.clean()
		page.add(gen_fp_page())
		des = page.navigation_bar.destinations
		sel = page.navigation_bar.selected_index
		page.navigation_bar = change_nav(len(des)-1, sel)
		change_button("NEXT", ft.icons.ARROW_FORWARD, new_progress)
		page.update()
		with open(log_path+"/presets.json", "r") as file:
			data: dict = json.load(file)
		data["lang"] = e.data
		with open(log_path+"/presets.json", "w") as file:
				json.dump(data, file, indent=4)

	def change_conf(e):
		global config_name
		if dd_conf.value != language.fp_no_conf:
			json_load(dd_conf.value)
		else:
			config_name = False

	def change_fp_page():
		global dd_lang, dd_conf, welc_row
		op = [ft.dropdown.Option(i.split("config.json")[0]) for i in os.listdir(log_path) if "config.json" in i] + [ft.dropdown.Option(language.fp_no_conf)]
		dd_lang = ft.Dropdown(width=400, options=[ft.dropdown.Option("ru"), ft.dropdown.Option("uk"), ft.dropdown.Option("ua")], on_change=swap_lang, value=language.lang)
		dd_conf = (ft.Dropdown(width=400, options=op, on_change=change_conf, value=config_name) if config_name else ft.Dropdown(width=400, options=op, on_change=change_conf, value=language.fp_no_conf))
		welc_row = welc_row = ft.Row([ft.Text("WELCOME", color=welc[page.theme_mode], size=50), ], alignment=ft.MainAxisAlignment.CENTER)

	def change_theme_mode(e):
		global welc_row
		if page.theme_mode == "dark":
			page.theme_mode = "light"
		else:
			page.theme_mode = "dark"
		change_button("NEXT", ft.icons.ARROW_FORWARD, new_progress)
		welc_row = ft.Row([ft.Text("WELCOME", color=welc[page.theme_mode], size=50), ], alignment=ft.MainAxisAlignment.CENTER)
		page.clean()
		page.add(gen_fp_page())
		page.update()
		with open(log_path+"/presets.json", "r") as file:
			data: dict = json.load(file)
		data["theme"] = page.theme_mode
		with open(log_path+"/presets.json", "w") as file:
				json.dump(data, file, indent=4)

	def change_zow_mod(e):
		global zow
		with open(log_path+"/presets.json", "r") as file:
			data: dict = json.load(file)
		data["zow"] = ((page.window.width, page.window.height), (False if e.data == "false" else True))
		with open(log_path+"/presets.json", "w") as file:
				json.dump(data, file, indent=4)
		zow = (False if e.data == "false" else True)
  
	def page_close(e):
		global zow
		if e.data=='hide':
			if zow:
				with open(log_path+"/presets.json", "r") as file:
					data: dict = json.load(file)
				data["zow"] = ((page.window.width, page.window.height), zow)
				with open(log_path+"/presets.json", "w") as file:
						json.dump(data, file, indent=4)

	def gen_fp_page():
		change_fp_page()
		if [i for i in os.listdir(log_path) if "config.json" in i] != []:
			return ft.Column(
				[
					welc_row,
					ft.Row([ft.Text(language.fp_lang), ], alignment=ft.MainAxisAlignment.CENTER),
					ft.Row([dd_lang], alignment=ft.MainAxisAlignment.CENTER),
					ft.Row([ft.Text(language.fp_config), ], alignment=ft.MainAxisAlignment.CENTER),
					ft.Row([dd_conf, ], alignment=ft.MainAxisAlignment.CENTER),
					ft.Row([ft.Checkbox(label=language.fp_zow, on_change=change_zow_mod, value=zow), ft.Checkbox(label=language.fp_dark_mode, on_change=change_theme_mode, value=(True if page.theme_mode == "dark" else False)), ], alignment=ft.MainAxisAlignment.CENTER)
					
				],
				alignment=ft.MainAxisAlignment.CENTER,
			)
		return ft.Column(
			[
				welc_row,
				ft.Row([ft.Text(language.fp_lang), ], alignment=ft.MainAxisAlignment.CENTER),
				ft.Row([dd_lang], alignment=ft.MainAxisAlignment.CENTER),
				ft.Row([ft.Checkbox(label=language.fp_zow, on_change=change_zow_mod, value=zow), ft.Checkbox(label=language.fp_dark_mode, on_change=change_theme_mode, value=(True if page.theme_mode == "dark" else False)), ], alignment=ft.MainAxisAlignment.CENTER)
			],
			alignment=ft.MainAxisAlignment.CENTER,
		)

	def img_update(set_image: Image, show = False):
		global global_area, save_size_mode, worked_area, sizes, path_template, rgb_mode
		rgb_mode = cb_rgb.value
		path_template = select_file.value.split(language.pf_template_path)[1]
		save_size_mode = dd_ss.value
		set_image = work_with_test_image()
		buffered = BytesIO()
		set_image.save(buffered, format="JPEG")
		image_holder_settings.src_base64= base64.b64encode(buffered.getvalue()).decode("utf-8")
		page.update()
		if show:
			set_image.show()

	def checkbox_changed_rgb(e):
		img_update(set_image)
		
	def checkbox_changed_ssm(e):
		img_update(set_image)	

	def open_img_button(e):
		img_update(set_image, show=True)

	def pick_img(e):
		global global_area, save_size_mode, worked_area, sizes, path_template, rgb_mode
		if not e.files:
			select_file.value = language.pf_no_template
			image_holder_floader.visible=False
			page.floating_action_button.disabled = True
			change_progress(2)
			page.navigation_bar = change_nav(2, 2)
			page.update()
		else:
			select_file.value = "\n\n".join([f"{language.pf_template_file}{i.name}\n{language.pf_template_path}{i.path}" for i in e.files])
			if (select_file.value != None and select_file.value != language.pf_no_template) and (select_floader.value != language.pf_no_work and select_floader.value != None and "None" not in select_floader.value):
				page.floating_action_button.disabled = False
			else:
				page.floating_action_button.disabled = True
				change_progress(2)
				page.navigation_bar = change_nav(2, 2)
			with open(e.files[0].path, 'rb') as r:
				image_holder_floader.src_base64= base64.b64encode(r.read()).decode("utf-8")
				image_holder_floader.visible=True
				page.update()
			rgb_mode = (cb_rgb.value if cb_rgb != None else rgb_mode)
			path_template = select_file.value.split(language.pf_template_path)[1]
			save_size_mode = (dd_ss.value if dd_ss != None else save_size_mode)
			set_image = work_with_test_image()
			buffered = BytesIO()
			set_image.save(buffered, format="JPEG")
			image_holder_settings.src_base64= base64.b64encode(buffered.getvalue()).decode("utf-8")
			image_holder_settings.visible=True

	def pick_folder(e):
		global w_path
		if not e.path:
			select_floader.value = language.pf_no_work
			page.floating_action_button.disabled = True
			change_progress(2)
			page.navigation_bar = change_nav(2, 2)
		else:
			name = e.path.split("\\")[-1]
			select_floader.value = f"{language.pf_work_file}{name}\n{language.pf_work_path}{e.path}"
			w_path = select_floader.value.split(language.pf_work_path)[1]
			if (select_file.value != None and select_file.value != language.pf_no_template) and (select_floader.value != language.pf_no_work and select_floader.value != None and "None" not in select_floader.value):
				page.floating_action_button.disabled = False
			else:
				page.floating_action_button.disabled = True
				change_progress(2)
				page.navigation_bar = change_nav(2, 2)
		page.update()

	file_img = ft.FilePicker(on_result=pick_img)
	floader = ft.FilePicker(on_result=pick_folder)
	page.overlay.append(file_img)
	page.overlay.append(floader)

	def gen_floader_page():
		global file_img, floader
		return ft.Row(
			[
				ft.Column(
					[
						ft.Column(
							[
								ft.Row([ft.ElevatedButton(language.pf_template_button, icon=ft.icons.UPLOAD_FILE, on_click= lambda _: file_img.pick_files(allow_multiple=False, allowed_extensions=["jpeg", "png", "jpg"]))], alignment=ft.MainAxisAlignment.CENTER),
								ft.Row([select_file], alignment=ft.MainAxisAlignment.CENTER)
							]
						),
						ft.Column(
							[
								image_holder_floader
							]
						)
					]
				),
				ft.Column(
					[
						ft.Row([ft.ElevatedButton(language.pf_work_button, icon=ft.icons.UPLOAD_FILE, on_click= lambda _: floader.get_directory_path())], alignment=ft.MainAxisAlignment.CENTER),
						ft.Row([select_floader], alignment=ft.MainAxisAlignment.CENTER)
					]
				)
			],
			alignment=ft.MainAxisAlignment.CENTER,
			spacing=100
		)

	def gen_rg_pr():
		global printer, printers, rg_pr
		if printer and printer in [i[2] for i in printers]:
			return ft.RadioGroup(content=ft.Column([ft.Radio(value=i[2], label=i[2]) for i in printers]), on_change=change_printer, value=printer)
		return ft.RadioGroup(content=ft.Column([ft.Radio(value=i[2], label=i[2]) for i in printers]), on_change=change_printer)

	def col(arg: str):
		return '#'+'0'*(6-len(hex(int('{value}')))[2:])+str(hex(int('{value}'))[2:])

	def regen_set_page():
		global sl_wa_wh, sl_wa_hg, sl_sz_wh, sl_sz_hg, sl_tr, end_tb, cb_rgb, dd_ss, sl_ss_mod, tf_wa_wh, tf_wa_hg, tf_sz_wh, tf_sz_hg, tf_ss_mod, tf_tr
		dd_ss = ft.Dropdown(width=200, options=[ft.dropdown.Option("16:9"), ft.dropdown.Option("4:3"), ft.dropdown.Option("16:10"), ft.dropdown.Option("OFF")], value=save_size_mode, on_change=full_page_update)
		cb_rgb = ft.Checkbox(label=language.set_rgb, on_change=checkbox_changed_rgb, value=rgb_mode)
		sl_wa_wh = ft.Slider(min=0, max=global_area[0], divisions=global_area[0], label="{value}", on_change=sl_update, value=worked_area[0])
		sl_wa_hg = ft.Slider(min=0, max=global_area[1], divisions=global_area[1], label="{value}", on_change=sl_update, value=worked_area[1])
		sl_sz_wh = ft.Slider(min=0, max=(global_area[0]), divisions=(global_area[0]), label="{value}", on_change=sl_update, value=sizes[0])
		sl_sz_hg = ft.Slider(min=0, max=(global_area[1]), divisions=(global_area[1]), label="{value}", on_change=sl_update, value=sizes[1])
		sl_ss_mod = ft.Slider(min=0, max=(max(global_area)), divisions=(max(global_area)), label="{value}", on_change=sl_update, value=max(sizes))
		sl_tr = ft.Slider(min=0, max=int("FFFFFF", 16), divisions=100, label=f"", on_change=sl_update, value=tr)
		tf_wa_wh = TextIntoSlider(value=worked_area[0])
		tf_wa_hg = TextIntoSlider(value=worked_area[1])
		tf_sz_wh = TextIntoSlider(value=sizes[0])
		tf_sz_hg = TextIntoSlider(value=sizes[1])
		tf_ss_mod = TextIntoSlider(value=max(sizes))
		end_tb = ft.TextField(label=language.endp_config_input)

	def gen_set_page():
		regen_set_page()
		if save_size_mode == "OFF":
			return ft.Column(
					[
						ft.Row(
							[	
								ft.Column(
									[
										ft.Row([ft.Text(language.set_left)], alignment=ft.MainAxisAlignment.CENTER),
										ft.Row([sl_wa_wh, tf_wa_wh], alignment=ft.MainAxisAlignment.CENTER),
										ft.Row([ft.Text(language.set_up)], alignment=ft.MainAxisAlignment.CENTER),
										ft.Row([sl_wa_hg, tf_wa_hg], alignment=ft.MainAxisAlignment.CENTER),
										ft.Row([ft.Text(language.set_wight)], alignment=ft.MainAxisAlignment.CENTER),
										ft.Row([sl_sz_wh, tf_sz_wh], alignment=ft.MainAxisAlignment.CENTER),
										ft.Row([ft.Text(language.set_height)], alignment=ft.MainAxisAlignment.CENTER),
										ft.Row([sl_sz_hg, tf_sz_hg], alignment=ft.MainAxisAlignment.CENTER),
									]
								),
								ft.Column(
									[
										ft.Row([ft.Text(language.set_trans)], alignment=ft.MainAxisAlignment.CENTER),
										ft.Row([sl_tr], alignment=ft.MainAxisAlignment.CENTER),
										ft.Row([cb_rgb], alignment=ft.MainAxisAlignment.CENTER),
										ft.Row([ft.Text(language.set_ssm)], alignment=ft.MainAxisAlignment.CENTER),
										ft.Row([dd_ss], alignment=ft.MainAxisAlignment.CENTER)
									], horizontal_alignment=ft.CrossAxisAlignment.END
								),
								ft.Column(
									[
										image_holder_settings,
										ft.Row([ft.OutlinedButton(text=language.set_button, on_click=open_img_button)], alignment=ft.MainAxisAlignment.CENTER)
									]
								)
							], alignment=ft.MainAxisAlignment.CENTER
						),
						
					],
					alignment=ft.MainAxisAlignment.END
				)
		return ft.Column(
					[
						ft.Row(
							[	
								ft.Column(
									[
										ft.Row([ft.Text(language.set_left)], alignment=ft.MainAxisAlignment.CENTER),
										ft.Row([sl_wa_wh, tf_wa_wh], alignment=ft.MainAxisAlignment.CENTER),
										ft.Row([ft.Text(language.set_up)], alignment=ft.MainAxisAlignment.CENTER),
										ft.Row([sl_wa_hg, tf_wa_hg], alignment=ft.MainAxisAlignment.CENTER),
										ft.Row([ft.Text(language.set_sl_ssmod)], alignment=ft.MainAxisAlignment.CENTER),
										ft.Row([sl_ss_mod, tf_ss_mod], alignment=ft.MainAxisAlignment.CENTER)
									]
								),
								ft.Column(
									[
										ft.Row([ft.Text(language.set_trans)], alignment=ft.MainAxisAlignment.CENTER),
										ft.Row([sl_tr], alignment=ft.MainAxisAlignment.CENTER),
										ft.Row([cb_rgb], alignment=ft.MainAxisAlignment.CENTER),
										ft.Row([ft.Text(language.set_ssm)], alignment=ft.MainAxisAlignment.CENTER),
										ft.Row([dd_ss], alignment=ft.MainAxisAlignment.CENTER)
									], alignment=ft.MainAxisAlignment.END
								),
								ft.Column(
									[
										image_holder_settings,
										ft.Row([ft.OutlinedButton(text=language.set_button, on_click=open_img_button)], alignment=ft.MainAxisAlignment.CENTER)
									]
								)
							], alignment=ft.MainAxisAlignment.CENTER
						),
						
					],
					alignment=ft.MainAxisAlignment.CENTER
				)

	def ref_button(e):
		global printers, rg_pr
		printers = [i for i in win32print.EnumPrinters(3)]
		rg_pr = gen_rg_pr()
		page.update()
		
	def gen_printer_page():
		global rg_pr
		rg_pr = gen_rg_pr()
		return ft.Column(
			[
				ft.Row([rg_pr], alignment=ft.MainAxisAlignment.CENTER),
				ft.Row(
					[
						ft.Text(language.printer),
						ft.IconButton(icon=ft.icons.REFRESH, on_click=ref_button)
					], alignment=ft.MainAxisAlignment.CENTER
			),
				
			],
			alignment=ft.MainAxisAlignment.CENTER
		)

	def save_conf(e=None):
		global global_area, save_size_mode, worked_area, sizes, path_template, rgb_mode, printer, w_path, log_path, tr
		if end_tb.value != None:
			if not os.path.exists(log_path+f"/{end_tb.value}config.json"):
				with open(log_path+f"/{end_tb.value}config.json", "w") as file:
					file.write('{}')
			else:
				with open(log_path+f"/{end_tb.value}config.json", "r") as file:
					if not file.read():
						with open(log_path+f"/{end_tb.value}config.json", "w") as file:
							file.write('{}')
			with open(log_path+f"/{end_tb.value}config.json", "r") as file:
				data: dict = json.load(file)
			if data == {}:
				data = {
					"device": {
						"printer": printer,
						"path": w_path,
						"template": path_template
					}, 
					"image": {
						"mode": {
							"rgb": rgb_mode, 
							"save_size": save_size_mode
						},
						"color": tr,
						"global_area": global_area,
						"worked_area": worked_area, 
						"sizes": sizes
					}
				}
			else:
				data["device"]["path"] = w_path
				data["device"]["printer"] = printer
				data["device"]["template"] = path_template
				data["image"]["mode"]["rgb"] = rgb_mode
				data["image"]["mode"]["save_size"] = save_size_mode
				data["image"]["global_area"] = global_area
				data["image"]["worked_area"] = worked_area
				data["image"]["sizes"] = sizes
			with open(log_path+f"/{end_tb.value}config.json", "w") as file:
				json.dump(data, file, indent=4)
			page.update()

	def gen_start_page():
		if config_name:
			return ft.Row(
				[
					ft.Column(
						[
							ft.Row([ft.Text(f"{language.endp_config}{config_name}")], alignment=ft.MainAxisAlignment.CENTER),
							ft.Row([ft.Text(f"{language.endp_printer}{printer}")], alignment=ft.MainAxisAlignment.CENTER),
							ft.Row([ft.Text(f"{language.endp_path_work}{w_path}")], alignment=ft.MainAxisAlignment.CENTER),
							ft.Row([ft.Text(f"{language.endp_path_template}{path_template}")], alignment=ft.MainAxisAlignment.CENTER),
							ft.Row([ft.Text(f"{language.endp_rgb_mod}{language.py_to_lang(rgb_mode)}")], alignment=ft.MainAxisAlignment.CENTER),
							ft.Row([ft.Text(f"{language.endp_save_size_mod}{save_size_mode}")], alignment=ft.MainAxisAlignment.CENTER),
							ft.Row([ft.Text(f"{language.endp_global_size}{global_area}")], alignment=ft.MainAxisAlignment.CENTER),
							ft.Row([ft.Text(f"{language.endp_left}{worked_area[0]}")], alignment=ft.MainAxisAlignment.CENTER),
							ft.Row([ft.Text(f"{language.endp_up}{worked_area[1]}")], alignment=ft.MainAxisAlignment.CENTER),
							ft.Row([ft.Text(f"{language.endp_size}{sizes}")], alignment=ft.MainAxisAlignment.CENTER)
						]
					),
					ft.Column(
						[
							image_holder_settings, 
							ft.Row([end_tb, ft.OutlinedButton(text=language.endp_button, on_click=save_conf)], alignment=ft.MainAxisAlignment.CENTER)
						]
					),
				], alignment=ft.MainAxisAlignment.CENTER
			)
		return ft.Row(
			[
				ft.Column(
					[
						ft.Row([ft.Text(f"{language.endp_printer}{printer}")], alignment=ft.MainAxisAlignment.CENTER),
						ft.Row([ft.Text(f"{language.endp_path_work}{w_path}")], alignment=ft.MainAxisAlignment.CENTER),
						ft.Row([ft.Text(f"{language.endp_path_template}{path_template}")], alignment=ft.MainAxisAlignment.CENTER),
						ft.Row([ft.Text(f"{language.endp_rgb_mod}{language.py_to_lang(rgb_mode)}")], alignment=ft.MainAxisAlignment.CENTER),
						ft.Row([ft.Text(f"{language.endp_save_size_mod}{save_size_mode}")], alignment=ft.MainAxisAlignment.CENTER),
						ft.Row([ft.Text(f"{language.endp_global_size}{global_area}")], alignment=ft.MainAxisAlignment.CENTER),
						ft.Row([ft.Text(f"{language.endp_left}{worked_area[0]}")], alignment=ft.MainAxisAlignment.CENTER),
						ft.Row([ft.Text(f"{language.endp_up}{worked_area[1]}")], alignment=ft.MainAxisAlignment.CENTER),
						ft.Row([ft.Text(f"{language.endp_size}{sizes}")], alignment=ft.MainAxisAlignment.CENTER)
					]
				),
				ft.Column(
					[
						image_holder_settings, 
						ft.Row([end_tb, ft.OutlinedButton(text=language.endp_button, on_click=save_conf)], alignment=ft.MainAxisAlignment.CENTER)
					]
				),
			], alignment=ft.MainAxisAlignment.CENTER
		)

	page.on_app_lifecycle_state_change = page_close
	start_log_func()

	change_button("NEXT", ft.icons.ARROW_FORWARD, new_progress)
	page.navigation_bar = change_nav()
	page.add(gen_fp_page())

ft.app(main)

# ft.app(target=main, view=ft.AppView.WEB_BROWSER)
