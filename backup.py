from os import system, path, walk
from re import sub
from hashlib import md5

# Инициализация
drive = path.splitdrive(__file__)[0]
#print(drive)
main_backup_dir = path.join(drive, r"\backup")
#print(main_backup_dir)
ignore = ['.git', '.vscode', '__pycache__', 'venv', 'vEnv', 'python_backup']
target_data = []

# Функции
# Чекаем на наличие элемента в бэкапе
def backup_check(element_path :str) : 
	if path.exists(element_path) : # Если путь существует
		if path.isfile(element_path) : # Если указывает на файл
			print(f"[CHECK] File {element_path} existed!")
			return True
		if path.isdir(element_path) : # Если указывает на директорию
			print(f"[CHECK] Directory {element_path} existed!")
			return True
	else : # Иначе 
		return False

#Проверка на игнорируемые элементы
def check_ignore(path :str) -> bool:
	for word in ignore:
		if word in path:
			return True
	return 

#убираем лишнее из пути
def normalize_path(path :str) ->str :
	string = sub(r"\s+", "_", path)
	string = sub(r",+", "_", string)
	return string

#возвращаем бэкап путь файла/директории
def get_backup_path(root :str, element :str, backup :str, el_path :str) ->str:
	path_in = path.join(root, element) #полный путь 
	path_in_base = path.basename(el_path) # делим путь
	path_in_split = path_in.split(path_in_base)[1][1:] # забираем без шелухи
	path_out = path.join(backup, path_in_split) # путь в бэкапе

	#нужна проверка на пробелы, запятые в строке пути, заменять на "_"
	return normalize_path(path_out)


# Копируем пути файлов/папок в бэкап если их нет
def check_elements(backup_dir :str, element_path :str):
	if path.isfile(element_path): #Если путь файл
		file_name = path.basename(element_path) #Имя файла
		backup_full = path.join(backup_dir, file_name) #полный путь

		if not backup_check(backup_full):
			with open(backup_full, 'w') as file:
				file.write("")
			print (f"[SYNC] Created {file_name} in {backup_dir}")

	if path.isdir(element_path): #Если путь директория
		for root, dirs, files in walk(element_path): # Начинаем гулять по директории
			for dir in dirs: # сперва по папкам
				dir_out = get_backup_path(root, dir, backup_dir, element_path)
				if check_ignore(dir_out):
					continue
				else :
					if not backup_check(dir_out) : #есть ли такая папка в бэкапе
						print (f"[CHECK] Create {dir_out}")
						system (f"mkdir {dir_out}")
						
			for file in files :
				file_out = get_backup_path(root, file, backup_dir, element_path)
				file_in = path.join(root, file)
				
				if check_ignore(file_out):
					continue
				else :
					if not backup_check(file_out):
						print (f"[CHECK] Create {file_out}")
						with open(file_out, 'w') as file :
							file.write("")
					# Синхронизируем файл с источником
					#print(f"[SYNC F] in : {file_in}")		
					sync_data(file_in, file_out)

# Получаем мд5 хэш в hex
def get_md5(file :str) -> str :
	with open (file, 'rb') as f:
		data = f.read()
	return md5(data).hexdigest()

# Синхронизируем файлы
def sync_data(file :str, backup :str) :
	#print(f"\n[SYNC] Check file {file}")
	#print(f"xcopy \"{file}\" \"{backup}\" /y")
	#print(f"[SYNC] Check backup {backup}\n")
	if not get_md5(file) == get_md5(backup) :
		system (f"xcopy \"{file}\" \"{backup}\" /y")
		print (f"[SYNC] File {file} synchronized !")
		return True
	print("[SYNC] Synchronized")
	return False

# Главный блок
def main() :
	
	# Читаем файл target_data и пишем в список target_data
	with open('target_data.txt', 'r') as file:
		data = file.readlines()
		for string in data :
			target_data.append(string)

	#Чекаем на существование корневого пути, если нет - создаем
	if not backup_check(main_backup_dir):
		print(f"[CHECK] Created new backup root dir!")
		system(f"mkdir {main_backup_dir}")
		
	# Читаем список target_data, достаем строку и парсим ее
	for i in range(len(target_data)) :
		string = target_data[i].split(":") #парсим путь
		backup_dir  = string[0] #берем название папки в бэкапе
		element_path = string[1]+":"+string[2] #берем путь сканируемого
		element_path = element_path.strip() #убираем лишние символы
		element_in = path.abspath(element_path) #нормализованный путь к сканируемому 
		element_out = path.join(main_backup_dir ,backup_dir)
		# Проверяем наличие директорий в корневой папке
		if not backup_check(element_out) :
			system(f"mkdir {element_out}")
			print(f"[CHECK] Created {element_out} directory in root dir")
		# Создаем пустые файлы/папки для перезаписи
		check_elements(element_out, element_in)
		
	print("\n[CHECK] Check completed!")
	print("[SYNC] Sync completed!")
		

if __name__ == "__main__" :
	main()