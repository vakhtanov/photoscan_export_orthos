import PhotoScan
import os
try:
	import gdal
except:
	print("нет gdal модуля!!")

from math import ceil
from PySide import QtGui, QtCore

#______________________Создаем интерфейс___________________
class ExportOrthoWin(QtGui.QDialog): #новый класс как приложение с интерфейсом и кодом

	def __init__(self, parent):
		#_____________Пременные уровня класса___________
		self.OUT_dir='' #выходная дирректория
		self.orthoBounds=[]
		# ВЫХОДНАЯ ПРОЕКЦИЯ по умолчанию
		#out_crs='PROJCS["WGS 84 / UTM zone 37N",GEOGCS["WGS 84",DATUM["World Geodetic System 1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9102"]],AUTHORITY["EPSG","4326"]],PROJECTION["Transverse_Mercator",AUTHORITY["EPSG","9807"]],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",39],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AUTHORITY["EPSG","32637"]]'
		self.out_crs=PhotoScan.CoordinateSystem('PROJCS["WGS 84 / UTM zone 37N",GEOGCS["WGS 84",DATUM["World Geodetic System 1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9102"]],AUTHORITY["EPSG","4326"]],PROJECTION["Transverse_Mercator",AUTHORITY["EPSG","9807"]],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",39],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AUTHORITY["EPSG","32637"]]')
		#out_crs=PhotoScan.CoordinateSystem('PROJCS["WGS 84 / UTM zone 38N",GEOGCS["WGS 84",DATUM["World Geodetic System 1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9102"]],AUTHORITY["EPSG","4326"]],PROJECTION["Transverse_Mercator",AUTHORITY["EPSG","9807"]],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",45],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AUTHORITY["EPSG","32638"]]')
		self.DATA_OK=0
		print ('orthoBounds=',len(self.orthoBounds))
		#формат массива:0-имя ортофото, 1-Xmin, 2-Ymin, 3-sizeX, 4-sizeY, 5-ID полигона
		#__________________________________________________

		
		QtGui.QDialog.__init__(self, parent)
		self.setWindowTitle("Экспорт Орто по разграфке") #Заголвок окна
		self.resize(500, 250) #размер окна
		self.txt_comment = QtGui.QLabel("	Модуль экспортирует ортофото из фотоскана по нарезке. \
Нарезка в текстовом файле: название листа, координаты нижнего левого угла, размеры. \n	Проекция нарезки должна совпадать с проекцией выходного ортофотоплана.\
Листы делятся по нарезке, а внутри нарезки по блокам, размеры задаются. ФОРМАТ JPG \n	При импорте SHP должно быть текстовое поле NAME \n \
Адрес сервера: "+ServerIP+" меняем в теле программы \n")
		self.txt_comment.setWordWrap(True)
		self.now_prj = QtGui.QLabel(str(self.out_crs))  
		self.select_prj = QtGui.QPushButton("Выберете проекцию")  #(" открыть ")
		self.select_prj.setFixedSize(170, 26)
		
		self.TXT_dif_pix = QtGui.QLabel("<B>Размер пикселя: </B>")
		self.TXT_dif_pix.setFixedSize(170, 26)
		self.dif_pix = QtGui.QLineEdit()  
		self.dif_pix.setText('0.1')# Задает размер пикселя по умолчанию
		self.dif_pix.setFixedSize(100, 26)  
		
		items_bloksize = ('5000', '8192', '10000', '15000', '20000', '25000', '29999','Full') # список с размерами тайлов
		#items_bloksize = {5000:5000, 8192:8192, 10000:10000, 15000:15000, 20000:20000, 25000:25000, 29999:29999}
		self.TXT_block_size = QtGui.QLabel("<B>Размер блока: </B>",)
		self.TXT_block_size.setFixedSize(170, 26)
		self.block_size = QtGui.QComboBox() 
		self.block_size.setFixedSize(100, 26)
		self.block_size.addItems(items_bloksize)
		self.block_size.setCurrentIndex(1) #Устанавливает по умолчанию второе значение из списка - 8192
		
		self.TXT_SHPname = QtGui.QLabel("Файл разграфки SHP (NAME,poligons)")  
		self.SHPname = QtGui.QPushButton("Выберете файл разграфки SHP")  #(" открыть ")
		self.SHPname.setFixedSize(170, 26)
		
		self.TXT_filename = QtGui.QLabel("Файл разграфки TXT(имя; X0; Y0; sizeX; SizeY)")  
		self.filename = QtGui.QPushButton("Выберете Файл разграфки")  #(" открыть ")
		self.filename.setFixedSize(170, 26)
		
		self.TXT_OUTFOLDER = QtGui.QLabel("Выходная дирректория")  
		self.OUTFOLDER = QtGui.QPushButton("Выберете дирректорию")  #(" открыть ")
		self.OUTFOLDER.setFixedSize(170, 26)
		
		self.GoGo = QtGui.QPushButton("Экспорт локально")  #(" Экспорт локально ")
		self.GoGo.setFixedSize(170, 26)
		self.GoGo.setDisabled(True)
		
		self.GoGoNet = QtGui.QPushButton("Экспорт по сети")  #(" Экспорт по сети ")
		self.GoGoNet.setFixedSize(170, 26)
		self.GoGoNet.setDisabled(True)
		
		hbox0 = QtGui.QHBoxLayout()
		hbox0.addWidget(self.txt_comment,alignment=0)
		
		hbox1 = QtGui.QHBoxLayout()
		hbox1.addWidget(self.select_prj,alignment=0)
		hbox1.addWidget(self.now_prj,alignment=0)
		
		hbox2 = QtGui.QHBoxLayout()
		hbox2.addWidget(self.TXT_block_size,alignment=1)
		hbox2.addWidget(self.block_size,alignment=1)
		
		hbox3 = QtGui.QHBoxLayout()
		hbox3.addWidget(self.TXT_dif_pix,alignment=1)
		hbox3.addWidget(self.dif_pix,alignment=1)
		
		hbox4 = QtGui.QHBoxLayout()
		#hbox4.addStretch(1)
		hbox4.addWidget(self.SHPname,alignment=0)
		hbox4.addWidget(self.TXT_SHPname,alignment=0)
		
		hbox5 = QtGui.QHBoxLayout()
		#hbox5.addStretch(1)
		hbox5.addWidget(self.filename,alignment=0)
		hbox5.addWidget(self.TXT_filename,alignment=0)
		
		hbox6 = QtGui.QHBoxLayout()
		#hbox5.addStretch(1)
		hbox6.addWidget(self.OUTFOLDER,alignment=0)
		hbox6.addWidget(self.TXT_OUTFOLDER,alignment=0)
		
		hbox7 = QtGui.QHBoxLayout()
		hbox7.addWidget(self.GoGo, stretch=0, alignment=0)
		hbox7.addWidget(self.GoGoNet, stretch=0, alignment=0)
		
		vbox = QtGui.QVBoxLayout() #Определяем вбокс и забиваем его Нбоксами
		#vbox.addStretch(1)
		vbox.addLayout(hbox0)
		vbox.addLayout(hbox1)
		vbox.addLayout(hbox2)
		vbox.addLayout(hbox3)
		vbox.addLayout(hbox4)
		vbox.addLayout(hbox5)
		vbox.addLayout(hbox6)
		vbox.addLayout(hbox7)
		
		self.setLayout(vbox)
		
		#QtCore.QObject.connect(self.filename, QtCore.SIGNAL("clicked()"), self.input_razgr_name)
		#QtCore.QObject.connect(self.OUTFOLDER, QtCore.SIGNAL("clicked()"), self.input_out_dir)
		#QtCore.QObject.connect(self.select_prj, QtCore.SIGNAL("clicked()"), self.set_projection)
		#QtCore.QObject.connect(self.GoGo, QtCore.SIGNAL("clicked()"), self.test_path)
		#QtCore.QObject.connect(self.GoGo, QtCore.SIGNAL("clicked()"), self.ortho_local)
		
		self.select_prj.clicked.connect(self.set_projection)
		self.SHPname.clicked.connect(self.input_razgr_SHPname)
		self.filename.clicked.connect(self.input_razgr_name)
		self.OUTFOLDER.clicked.connect(self.input_out_dir)
		self.GoGo.clicked.connect(self.ortho_local)
		self.GoGoNet.clicked.connect(self.ortho_net)
		
		self.exec()
		
	def unlock_export(self,sel):
		#Переменная нужна для разблокирования кнопки Экспорт. Два критических параметра:Файл разграфки и выходная дирректория, каждый добавляет по еденице.
		#Sel=5 блокирует кнопки при запуске сетевой обработки
		'''
		DATA_OK логика работы: Для экспорта нужно задать выходную директорию и файл разграфки, текстовый или векторный
		при запуске сетевой обработки кнопки опять блокируются
		DATA_OK меняет только эта процедура!!!
		
		0-ничего не задано экспорт заблокирован
		1-выбран  файл разграфки проверяем выбран ли путь, да, разблокируем 3
		2-выбран путь проверяем выбран ли файл разграфки, да, разблокируем 3
		'''
		if sel==5 and self.DATA_OK==1: self.DATA_OK=0; self.GoGo.setDisabled(True); self.GoGoNet.setDisabled(True)
		if sel==5 and self.DATA_OK==2: self.DATA_OK=2; self.GoGo.setDisabled(True); self.GoGoNet.setDisabled(True)
		if sel==5 and self.DATA_OK==3: self.DATA_OK=2; self.GoGo.setDisabled(True); self.GoGoNet.setDisabled(True)
		if self.DATA_OK==1 and sel==2: self.DATA_OK=3
		if self.DATA_OK==2 and sel==1: self.DATA_OK=3
		if self.DATA_OK==0 and sel != 5: self.DATA_OK=sel
		if self.DATA_OK==3 and sel != 5: self.GoGo.setDisabled(False); self.GoGoNet.setDisabled(False);print ('unlock')
		print (sel,self.DATA_OK)
#_____________________________________________________________________________
	def input_razgr_SHPname(self):
		#global listShapes
		
		SHPname='' #Векторный файл разграфки
		DataDir = os.path.dirname(__file__) # Дирректория по умолчанию - дирректория скрипта!!
		shpfilename= QtGui.QFileDialog.getOpenFileName(self, 'выберете векторный файл разграфки', DataDir, filter='*.shp') #Координаты в выходной проекции
		#проверка  на пустоту
		if not shpfilename[0]=='':
			SHP_name=shpfilename[0]
		else:
			return
		sname=os.path.basename(SHP_name)
		file_sname=os.path.splitext(sname)[0]
		
		print('Путь до шейпа: ',SHP_name)
		print('Имя шейпа: ',file_sname)
		chunk.importShapes(SHP_name,True) # Импорт шейпфайла с заменой
		shapes=chunk.shapes
		#Сделать проверку на ИМЯ ПОЛИГОНА
		#shapes=PhotoScan.app.document.chunk.shapes
		listShapes=shapes.items() #Массив (список) шейпов в проекте
		PhotoScan.app.messageBox('Импортированы объекты: '+str(shapes)+'\n Старые объекты удалены')
		
		#Поличили список векторных объектов, загруженных в проект, теперь проходим по каждому объекту и определяем его минимум и максимум по коориднатам
		
		if len(listShapes) !=0:
			poligon_ID=0
			self.orthoBounds=[]
			for shape in listShapes:
				x=[]
				y=[]
				vertices=shape.vertices
				for vertex in vertices:
					x.append(vertex[0])
					y.append(vertex[1])
				
				# Если есть NAME - это будет имя, если нет - имя шейпа и номер фичи
				if str(shape.label)=='':
					poligonName=str(file_sname)+'_'+str(poligon_ID)
				else:
					poligonName=str(shape.label)
				xMin=min(x); yMin=min(y); xSize=max(x)-min(x); ySize=max(y)-min(y)
				element=[poligonName,xMin,yMin,xSize,ySize,poligon_ID]
				self.orthoBounds.append(element)
				#формат массива:0-имя ортофото, 1-Xmin, 2-Ymin, 3-sizeX, 4-sizeY
				poligon_ID+=1 #Увеличение на единицу
			print (len(self.orthoBounds),poligon_ID)
			if len(self.orthoBounds) != 0: self.unlock_export(1)
			self.TXT_SHPname.setText(str(sname))
			self.TXT_filename.setText("Файл разграфки TXT(имя; X0; Y0; sizeX; SizeY)")
		else:
			PhotoScan.app.messageBox('Пустой SHP файл')
			self.unlock_export(5)
		print ('orthoBounds=',len(self.orthoBounds))
		# Шейп засосали,  минимум максимум нашли, с обрезкой дальше разберемся
		#_____________________________________________________________________________
		
	def input_razgr_name(self):
		TXT_name='' #имя файла с разграфкой
		# КООРДИАНТЫ ДОЛЖНЫ БЫТЬ В ВЫХОДНОЙ ПРОЕКЦИИ!!!!!
		DataDir = os.path.dirname(__file__) # Дирректория по умолчанию - дирректория скрипта!!
		textfilename= QtGui.QFileDialog.getOpenFileName(self, 'выберете  файл разграфки', DataDir, filter='*.txt') #Координаты в выходной проекции
		#проверка текстфайлнайм на пустоту
		if not textfilename[0]=='': 
			with open(textfilename[0]) as f:
				for line in f:
					znach=line.split(";")
					try:
						if not (isinstance(znach[0],str)):  PhotoScan.app.messageBox('Неверный форматS'); self.unlock_export(5); return
						if not (isinstance(float(znach[1]),(float,int))):  PhotoScan.app.messageBox('Неверный формат1i'); self.unlock_export(5);return
						if not (isinstance(float(znach[2]),(float,int))):  PhotoScan.app.messageBox('Неверный формат2i'); self.unlock_export(5);return
						if not (isinstance(float(znach[3]),(float,int))):  PhotoScan.app.messageBox('Неверный формат3i'); self.unlock_export(5);return
						if not (isinstance(float(znach[4]),(float,int))):  PhotoScan.app.messageBox('Неверный формат4i'); self.unlock_export(5);return
					except:
						PhotoScan.app.messageBox('Неверный формат_;') 
						self.unlock_export(5)
						return
		else:
			return
		if not (textfilename[0]==''): #Если все нормально заполняем orthoBounds
			TXT_name=textfilename
			self.orthoBounds=[]
			with open(TXT_name[0]) as f:
				count=0
				for line in f:
					znach=line.split(";")
					element=[znach[0],znach[1],znach[2],znach[3],znach[4],count]
					self.orthoBounds.append(element)
					count+=1
			print ('orthoBounds=',len(self.orthoBounds))
			self.unlock_export(1) #разблокирует экспорт, если заданы разграфка и дирректория
			self.TXT_filename.setText(str(TXT_name[0]))
			self.TXT_SHPname.setText("Файл разграфки SHP (NAME,poligons)")
		
	def set_projection(self):
			self.out_crs=PhotoScan.app.getCoordinateSystem('Система координат', self.out_crs) #Специальная форма для задания системы координат
			self.now_prj.setText(str(self.out_crs))
			
	def input_out_dir(self):
		DataDir = os.path.dirname(__file__)
		outputdir = QtGui.QFileDialog.getExistingDirectory(self, 'выберете дирректорию', DataDir)
		if not outputdir=='':
			self.OUT_dir=outputdir
			self.TXT_OUTFOLDER.setText(str(self.OUT_dir))
			self.unlock_export(2)  #разблокирует экспорт, если заданы разграфка и дирректория
		else:
			return
		print ('orthoBounds=',len(self.orthoBounds))

	def export_ortho(self,proc_type): # универсальная процедура экспорта для локлаьной и для сетевой обработки
		#global chunk
		print ('orthoBounds=',len(self.orthoBounds))
		task=[] #Это СПИСОК тасков
		DifPix=float(self.dif_pix.text())
		if self.block_size.currentText()=='Full':
			BlockSize=0
		else:
			BlockSize=int(self.block_size.currentText())

# Цикл для запуска ортофото локально или для забивания стека на сеть из массива
		try:
			#for line in file_razgr:
			for cu_string in self.orthoBounds:
				OName=cu_string[0]
				XMLeft=float(cu_string[1])
				YMDown=float(cu_string[2])
				sizeXM=float(cu_string[3])
				sizeYM=float(cu_string[4])
				shapeNumber=int(cu_string[5])
				cu_Region=(XMLeft,YMDown,XMLeft+sizeXM,YMDown+sizeYM)
				fileoutname=self.OUT_dir+"\\"+OName+".jpg"
				#print (fileoutname," ",XMLeft," ",YMDown," ",sizeXM," ",sizeYM)
				print(fileoutname, cu_Region,DifPix, DifPix, BlockSize, BlockSize)
				if proc_type=='local':
					print ('Обработка локально')
					#для тифа chunk.exportOrthomosaic(fileoutname, format="tif", region=cu_Region, projection=self.out_crs,dx=DifPix, dy=DifPix, blockw=BlockSize, blockh=BlockSize, write_kml=False, write_world=True, tiff_compression="lzw", tiff_big=False)
					chunk.exportOrthomosaic(fileoutname, format="jpg", region=cu_Region, projection=self.out_crs,dx=DifPix, dy=DifPix, blockw=BlockSize, blockh=BlockSize, write_kml=False, write_world=True, tiff_compression="lzw")
				elif proc_type=='net':
					print ('Обработка по сети')
					
					work = PhotoScan.NetworkTask() # СОздаем ворк и забиваем его параметрами
					work.name = "ExportOrthomosaic" #экспорт орто
					work.frames.append((chunk.key,0))
					work.params['write_world'] = 1
					work.params['write_tiles'] = 1
					work.params['tile_width'] = BlockSize
					work.params['tile_height'] = BlockSize
					work.params['path'] = fileoutname #выходная дирректория с именем файла
					work.params['resolution_x'] = DifPix
					work.params['resolution_y'] = DifPix
					work.params['raster_format'] = 2
					work.params['region'] = cu_Region
					# ВНИМАНИЕ! По сети нельзя экспортировать в пользовательской проекции
					work.params['projection'] = self.out_crs.authority #Из объекта проекция берется только ее номер EPSG::32637 
					task.append(work) #Добавляем задачу в таск
				else:
					print ('Пока не задано')
			PhotoScan.app.messageBox('Обработка закончена')
		except:
			PhotoScan.app.messageBox('Что-то пошло не так ((')
			return
				#break
#Запуск сетевого стека, таска в обработку
		if proc_type=='net':
			print(ProjectLocalPath_auto)
			print (ProjectPath)
			#print (task[0].params)
			client.connect(ServerIP)
			batch_id = client.createBatch(ProjectPath, task) #Научиться определять есть ли на сети такой проект!!!.
			
			if batch_id==None:
				PhotoScan.app.messageBox('<B>Этот проект уже запущен в обработку!!!<B>')
				self.unlock_export(5)
			else:
				print ('Проект работает под номером ',batch_id)
				client.resumeBatch(batch_id)
				self.unlock_export(5)
				PhotoScan.app.messageBox('Проект поставлен в очередь сетевой обработки')
			
			client.disconnect()
			pass

	def ortho_local(self):
		self.export_ortho('local')
	def ortho_net(self):
		self.export_ortho('net')
#______________________Интерфейс готов_____________________

#______Глобальные переменные_____________
#_________Параметры Сервера Сетевого и папка для работы_____________
ServerIP='192.168.254.72'
RootDir=r'V:\Photoscan_Cluster'

doc = PhotoScan.app.document #Текущий проект
PH_program=PhotoScan.app #сама программа
ProjectPath=doc.path #Полный путь до файла проекта
chunk = doc.chunk
#chunk = PhotoScan.app.document.chunk
client = PhotoScan.NetworkClient()
#sizeXM=1000.05
#sizeYM=1000.05
#if sizeXMpix%2: sizeXMpix=sizeXMpix+1
#if sizeYMpix%2: sizeYMpix=sizeYMpix+1


try:
	ProjectLocalPath_auto = os.path.relpath(ProjectPath, RootDir) # путь до проекта относительно сетевой папки
	#ЭТИ КОМАНДЫ СРАЗУ ЗАПУСКАЮТ ОКНО
	parent = QtGui.QApplication.instance().activeWindow()
	dlg = ExportOrthoWin(parent)
except:
	PhotoScan.app.messageBox('Откройте рабочий проект!')
	pass

print('\n\n ============== STOP ==============')



'''
ДОБАВЛЕНИЕ ПУНКТА МЕНЮ ДЛЯ ВЫЗОВА ОКНА И ЗАПУСКА СКРИПТА
def main():
	parent = QtGui.QApplication.instance().activeWindow()
	dlg = TestWin(parent)
#Menu_Item_Name = "Дополнительно/Экспорт орто"
#PhotoScan.app.addMenuItem(Menu_Item_Name, main) #"main" - вызываемая из меню функция.
'''

''''
2017-11-02 16:55:14 {'error_node_id': -1, 'path': 'test_vah/Photoscan_project/snimki23.psx', 
'tasks': [{'workitems_failed': 0, 'workitems_waiting': 1, 
'name': 'ExportOrthomosaic', 'workitems_working': 0, 
'time_elapsed': 0.0, 'items_done': 0, 'items_total': 1, 
'time_left': 0.0, 
'params': {'region': [302423.017, 6061410.717, 303907.617, 6064366.317], 
'tile_height': 12000, 'path': 'Scripts/SCRIPT_ph_export/ortho/fght.jpg', 
'projection': 'PROJCS["WGS 84 / UTM zone 37N",GEOGCS["WGS 84",DATUM["World Geodetic System 1984",
SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6326"]],
PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9102"]],
AUTHORITY["EPSG","4326"]],PROJECTION["Transverse_Mercator",AUTHORITY["EPSG","9807"]],PARAMETER["latitude_of_origin",0],
PARAMETER["central_meridian",39],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],
UNIT["metre",1,AUTHORITY["EPSG","9001"]],AUTHORITY["EPSG","32637"]]', 'resolution_x': 0.2, 'resolution_y': 0.2, 'raster_format': 2, 
'write_world': 1, 'tile_width': 13000}, 'progress': 0.0, 'status': 'pending'}], 'error_time': 0, 'error_message': '', 'status': 'paused', 'priority': 0}
'''
pass