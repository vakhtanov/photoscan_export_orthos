import PhotoScan
import os
try:
	import gdal
except:
	print("нет gdal модуля!!")
from math import ceil
from math import floor

#___ПРОВЕРКА_ВЕРСИИ____ИМПОРТ ИНТЕРФЕЙСА_____________
PH_version=PhotoScan.app.version
CommandStack=0 #Набор комманд, начальное значение в программе не используется 1- набор комманд 125, 126, 5 - набор комманд 130, 131, 132, 133, 134, 140
if PH_version=="1.2.5" or PH_version=="1.2.6":
	CommandStack=1
elif PH_version=="1.3.0" or PH_version=="1.3.1" or PH_version=="1.3.2" or PH_version=="1.3.3" or PH_version=="1.3.4" or PH_version=="1.4.0":
	CommandStack=5
else:
	pass


if CommandStack==1:
	from PySide.QtGui import QDialog, QApplication,QFileDialog,QVBoxLayout,QHBoxLayout,QPushButton,QCheckBox,QLabel,QComboBox,QLineEdit,QRadioButton
elif CommandStack==5:
	from PySide2.QtWidgets import QDialog, QApplication,QFileDialog,QVBoxLayout,QHBoxLayout,QPushButton,QCheckBox,QLabel,QComboBox,QLineEdit,QRadioButton
	PhotoScan.app.messageBox("В версиях фотоскана старше 1.3.0 \n ортофотоплан при экспорте будет обрезан по границам SHP")
else:
	PhotoScan.app.messageBox("Версия программы "+PH_version+"\nРабота скрипта гарантируется только на версии 1.2.5")

	
	
#Начальные установки
#_________Параметры Сервера Сетевого и папка для работы_____________
ServerIP='192.168.254.72' # для версии 1.2.5
#ServerIP='192.168.254.81' #Для версии 1.3.4
RootDir=r'V:\Photoscan_Cluster'
doc = PhotoScan.app.document #Текущий проект
PH_program=PhotoScan.app #сама программа
ProjectPath=doc.path #Полный путь до файла проекта
chunk = doc.chunk #chunk = PhotoScan.app.document.chunk
client = PhotoScan.NetworkClient()
MessBox=PhotoScan.app.messageBox
#______________________Создаем интерфейс___________________
class ExportOrthoWin(QDialog): #новый класс как приложение с интерфейсом и кодом

	def __init__(self, parent):
		#_____________Пременные уровня класса___________
		self.OUT_dir='' #выходная дирректория
		self.orthoBounds=[]
		# ВЫХОДНАЯ ПРОЕКЦИЯ по умолчанию
		#out_crs='PROJCS["WGS 84 / UTM zone 37N",GEOGCS["WGS 84",DATUM["World Geodetic System 1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9102"]],AUTHORITY["EPSG","4326"]],PROJECTION["Transverse_Mercator",AUTHORITY["EPSG","9807"]],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",39],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AUTHORITY["EPSG","32637"]]'
		self.out_crs=PhotoScan.CoordinateSystem('PROJCS["WGS 84 / UTM zone 37N",GEOGCS["WGS 84",DATUM["World Geodetic System 1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9102"]],AUTHORITY["EPSG","4326"]],PROJECTION["Transverse_Mercator",AUTHORITY["EPSG","9807"]],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",39],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AUTHORITY["EPSG","32637"]]')
		#out_crs=PhotoScan.CoordinateSystem('PROJCS["WGS 84 / UTM zone 38N",GEOGCS["WGS 84",DATUM["World Geodetic System 1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9102"]],AUTHORITY["EPSG","4326"]],PROJECTION["Transverse_Mercator",AUTHORITY["EPSG","9807"]],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",45],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AUTHORITY["EPSG","32638"]]')
		self.crsShapes=PhotoScan.CoordinateSystem('PROJCS["WGS 84 / UTM zone 37N",GEOGCS["WGS 84",DATUM["World Geodetic System 1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9102"]],AUTHORITY["EPSG","4326"]],PROJECTION["Transverse_Mercator",AUTHORITY["EPSG","9807"]],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",39],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AUTHORITY["EPSG","32637"]]')
		self.DATA_OK=0
		#print ('orthoBounds=',len(self.orthoBounds))
		#формат массива:0-имя ортофото, 1-Xmin, 2-Ymin, 3-sizeX, 4-sizeY, 5-ID полигона
		#__________________________________________________
		
		QDialog.__init__(self, parent)
		self.setWindowTitle("Экспорт Орто по разграфке") #Заголвок окна
		self.resize(500, 250) #размер окна
		self.txt_comment = QLabel("	Модуль экспортирует ортофото и DEM из фотоскана по нарезке. \
Нарезка в текстовом файле: название листа, координаты нижнего левого угла, размеры. \n	Проекция нарезки должна совпадать с проекцией выходного ортофотоплана.\
Листы делятся по нарезке, а внутри нарезки по блокам, размеры задаются. ФОРМАТ JPG \n	При импорте SHP должно быть текстовое поле NAME \n \
Адрес сервера: "+ServerIP+" меняем в теле программы. Ваша версия фотоскана: "+PH_version+" \n")
		self.txt_comment.setWordWrap(True)
		self.now_prj = QLabel(str(self.out_crs))  
		self.select_prj = QPushButton("Выберете проекцию")  #(" открыть ")
		self.select_prj.setFixedSize(170, 26)
		
		self.TXT_dif_pix = QLabel("<B>Размер пикселя: </B>")
		self.TXT_dif_pix.setFixedSize(170, 26)
		self.dif_pix = QLineEdit()  
		self.dif_pix.setText('0.1')# Задает размер пикселя по умолчанию
		self.dif_pix.setFixedSize(100, 26)  
		
		items_bloksize = ('5000', '8192', '10000', '15000', '20000', '25000', '29999','Full') # список с размерами тайлов
		#items_bloksize = {5000:5000, 8192:8192, 10000:10000, 15000:15000, 20000:20000, 25000:25000, 29999:29999}
		self.TXT_block_size = QLabel("<B>Размер блока: </B>",)
		self.TXT_block_size.setFixedSize(170, 26)
		self.block_size = QComboBox() 
		self.block_size.setFixedSize(100, 26)
		self.block_size.addItems(items_bloksize)
		self.block_size.setCurrentIndex(1) #Устанавливает по умолчанию второе значение из списка - 8192
		
		self.TXT_SHPname = QLabel("Файл разграфки SHP (NAME,poligons)")  
		self.SHPname = QPushButton("Выберете файл разграфки SHP")  #(" открыть ")
		self.SHPname.setFixedSize(170, 26)
		
		self.TXT_filename = QLabel("Файл разграфки TXT(имя; X0; Y0; sizeX; SizeY)")  
		self.filename = QPushButton("Выберете Файл разграфки")  #(" открыть ")
		self.filename.setFixedSize(170, 26)
		
		self.TXT_CheckOrthoDem=QLabel("Вид выходной продукции")
		self.TXT_CheckOrthoDem.setFixedSize(170, 26)
		self.CheckOrtho_Radio=QRadioButton("Ортофото")
		self.CheckOrtho_Radio.setChecked(True)
		self.CheckDem_Radio=QRadioButton("ДЕМ")
		
		self.TXT_OUTFOLDER = QLabel("Выходная дирректория")  
		self.OUTFOLDER = QPushButton("Выберете дирректорию")  #(" открыть ")
		self.OUTFOLDER.setFixedSize(170, 26)
		
		items_format = ('JPG', 'TIF') # список форматов, ПРИ выборе ДЕМ будет выбран второй формат - внимательно при изменении списка!!!
		self.file_format = QComboBox() 
		self.file_format.setFixedSize(50, 26)
		self.file_format.addItems(items_format)
		self.file_format.setCurrentIndex(0) #Устанавливает по умолчанию первое значение
		
		self.TXT_checkExportOrtho = QLabel("Построить ортофото:") # Ортофото
		self.TXT_checkExportOrtho.setFixedSize(170, 26)
		self.checkExportOrtho = QCheckBox()
		self.checkExportOrtho.setChecked(False)
		
		self.GoGo = QPushButton("Экспорт локально")  #(" Экспорт локально ")
		self.GoGo.setFixedSize(170, 26)
		self.GoGo.setDisabled(True)
		
		self.GoGoNet = QPushButton("Экспорт по сети")  #(" Экспорт по сети ")
		self.GoGoNet.setFixedSize(170, 26)
		self.GoGoNet.setDisabled(True)
		
		
		hbox0 = QHBoxLayout()
		hbox0.addWidget(self.txt_comment,alignment=0)
		
		hbox1 = QHBoxLayout()
		hbox1.addWidget(self.select_prj,alignment=0)
		hbox1.addWidget(self.now_prj,alignment=0)
		
		hbox2 = QHBoxLayout()
		hbox2.addWidget(self.TXT_block_size,alignment=1)
		hbox2.addWidget(self.block_size,alignment=1)
		
		hbox3 = QHBoxLayout()
		hbox3.addWidget(self.TXT_dif_pix,alignment=1)
		hbox3.addWidget(self.dif_pix,alignment=1)
		
		hbox4 = QHBoxLayout()
		#hbox4.addStretch(1)
		hbox4.addWidget(self.SHPname,alignment=0)
		hbox4.addWidget(self.TXT_SHPname,alignment=0)
		
		hbox5 = QHBoxLayout()
		#hbox5.addStretch(1)
		hbox5.addWidget(self.filename,alignment=0)
		hbox5.addWidget(self.TXT_filename,alignment=0)
		
		hbox51 = QHBoxLayout()
		hbox51.addWidget(self.TXT_CheckOrthoDem,alignment=0)
		hbox51.addWidget(self.CheckOrtho_Radio,alignment=0)
		hbox51.addWidget(self.CheckDem_Radio,alignment=0)
		
		
		hbox6 = QHBoxLayout()
		#hbox5.addStretch(1)
		hbox6.addWidget(self.OUTFOLDER,alignment=0)
		hbox6.addWidget(self.TXT_OUTFOLDER,alignment=0)
		hbox6.addWidget(self.file_format,alignment=0)
		
		hbox7 = QHBoxLayout() #build ortho
		hbox7.addWidget(self.TXT_checkExportOrtho,alignment=0)
		hbox7.addWidget(self.checkExportOrtho,alignment=0)
		
		hbox8 = QHBoxLayout()
		hbox8.addWidget(self.GoGo, stretch=0, alignment=0)
		hbox8.addWidget(self.GoGoNet, stretch=0, alignment=0)
		
		vbox = QVBoxLayout() #Определяем вбокс и забиваем его Нбоксами
		#vbox.addStretch(1)
		vbox.addLayout(hbox0)
		vbox.addLayout(hbox1)
		vbox.addLayout(hbox2)
		vbox.addLayout(hbox3)
		vbox.addLayout(hbox4)
		vbox.addLayout(hbox5)
		vbox.addLayout(hbox51) #выбор, что строить орто или дем
		vbox.addLayout(hbox6)
		#Функция построения ортофото спрятана, поскольку работает не стабильно и построение ортофото для каждого листа в сумме занимает очень много времени, 
		#гораздо больше, чем один раз построить ортофото для всех
		#vbox.addLayout(hbox7) #build ortho
		vbox.addLayout(hbox8)
		
		self.setLayout(vbox)
		
		
		self.select_prj.clicked.connect(self.set_projection)
		self.SHPname.clicked.connect(self.input_razgr_SHPname)
		self.filename.clicked.connect(self.input_razgr_name)
		self.OUTFOLDER.clicked.connect(self.input_out_dir)
		self.GoGo.clicked.connect(self.ortho_local)
		self.GoGoNet.clicked.connect(self.ortho_net)
		#Организация блокировки интерфейса для радио кнопок
		self.CheckOrtho_Radio.clicked.connect(self.CheckOrtho_Radio_DO)
		self.CheckDem_Radio.clicked.connect(self.CheckDem_Radio_DO)
		#____________
		self.checkExportOrtho.clicked.connect(self.PrintChkStat) #Функция для проверки работы чека
		#self.WindowContextHelpButtonHint.clicked.connect(self.prog_hint)
		#self.WindowTitleHint.clicked.connect(self.prog_hint)
		
		self.exec()
		#____________________________________________________________________________
		
		
		
	def PrintChkStat(self): #Эта функция работает в принте с подстановкой и получение значения чека
		if self.checkExportOrtho.isChecked()==True:
			stat='ДА'
		else:
			stat='НЕТ'
		print ('Строить орто %s здесь'%stat)
		
	def CheckOrtho_Radio_DO(self):#Если выбран Ортоф - формат Джипег и свободен!!!
		print("Орто")
		self.file_format.setCurrentIndex(0)
		self.file_format.setDisabled(False)
	
	def CheckDem_Radio_DO(self):#Если выбран ДЕМ - формат тифф и блокируется!!!
		print("DEM")
		self.file_format.setCurrentIndex(1)
		self.file_format.setDisabled(True)
	
	def ortho_local(self):
		self.export_ortho('local')
	def ortho_net(self):
		self.export_ortho('net')
	def prog_hint(self):
		print("OK")
	
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
		
	def OrthoBoundCalc(self,Xn,Yn,XS,YS): # изменить под сетевую обработку с тайлами
		DifPix=float(self.dif_pix.text())
		''' Округление начала Если надо
		Xnround=floor(Xn/DifPix)*DifPix #
		Ynround=floor(Yn/DifPix)*DifPix
		'''
		'''
		if self.block_size.currentText()=='Full' or CommandStack==5 : #Экспорт целикового фрагмента
			print('границы целиковые')
			Xnround=Xn
			Ynround=Yn-DifPix
			XSround=ceil(XS/DifPix+1)*DifPix #Границы округляем в большую сторону и расширяем на пиксель
			YSround=ceil(YS/DifPix+1)*DifPix
			XSround=Xnround+XSround
			YSround=Ynround+YSround
			
		elif CommandStack==1 and self.block_size.currentText()!='Full': # Экспорт по тайлам
			print("Границы со сдвигом")
			BlockSize=float(self.block_size.currentText())
			Xnround=Xn
			Ynround=Yn #-DifPix
			XSround=ceil(XS/DifPix+1)*DifPix #Границы округляем в большую сторону и расширяем на пиксель
			YSround=ceil(YS/DifPix+1)*DifPix
			YBlockSize=BlockSize*DifPix 
			TileShift=YBlockSize-YSround
			Ynround=Ynround+TileShift
			XSround=Xnround+XSround
			YSround=Ynround+YSround+TileShift
		else:
			Print("Bound version error, OrthoBoundCalc")
			pass
			'''
		Xnround=Xn
		Ynround=Yn-DifPix
		XSround=ceil(XS/DifPix+1)*DifPix #Границы округляем в большую сторону и расширяем на пиксель
		YSround=ceil(YS/DifPix+1)*DifPix
		XSround=Xnround+XSround
		YSround=Ynround+YSround
		point=[] #"Эта конструкция нужна для поиска максимальных координат квадрата при переходе из системы в систему
		print("точки")
		point.append(PhotoScan.Vector((Xnround,Ynround)))
		point.append(PhotoScan.Vector((Xnround,YSround)))
		point.append(PhotoScan.Vector((XSround,YSround)))
		point.append(PhotoScan.Vector((XSround,Ynround)))
		print("точки2")
		point_trans=[]
		point_trans.append(PhotoScan.CoordinateSystem.transform(point[0],self.crsShapes,self.out_crs))
		point_trans.append(PhotoScan.CoordinateSystem.transform(point[1],self.crsShapes,self.out_crs))
		point_trans.append(PhotoScan.CoordinateSystem.transform(point[2],self.crsShapes,self.out_crs))
		point_trans.append(PhotoScan.CoordinateSystem.transform(point[3],self.crsShapes,self.out_crs))
		x=[]
		y=[]
		for i in range(4):
			print(i)
			x.append(point_trans[i][0])
			y.append(point_trans[i][1])
		xMin=min(x); yMin=min(y);xMax=max(x); yMax=max(y)
		#OrthoBound=(Xnround,Ynround,XSround,YSround)
		OrthoBound=(Xnround,Ynround,XSround,YSround)
		print (OrthoBound)
		OrthoBound=(xMin,yMin,xMax,yMax)
		print (OrthoBound)
		return OrthoBound
	def input_razgr_SHPname(self):
		#global listShapes
		SHPname='' #Векторный файл разграфки
		DataDir = os.path.dirname(__file__) # Дирректория по умолчанию - дирректория скрипта!!
		shpfilename= QFileDialog.getOpenFileName(self, 'выберете векторный файл разграфки', DataDir, filter='*.shp') #Координаты в выходной проекции
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
		self.crsShapes=shapes.crs #Проекция шейпа
		print(self.crsShapes)
		PhotoScan.app.messageBox('Импортированы объекты: '+str(shapes)+'\n Старые объекты удалены')
		
		#Получили список векторных объектов, загруженных в проект, теперь проходим по каждому объекту и определяем его минимум и максимум по коориднатам
		
		if len(listShapes) !=0:
			poligon_ID=0
			self.orthoBounds=[]
			for shape in listShapes: # ЗДЕСЬ определяются координаты минимум и максимум в текущей проекции в другой все по другому - Могут быть дыры
			# в OrthoBoundCalc стоит заглушка - имщет максимальные коориднаты углов прямоугольника после перепроецирования - можно но не совсем корректно
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
				self.orthoBounds.append(element) #ЭТО МАССИВ с ГРАНИЦАМИ ОРТОФОТО 
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
		textfilename= QFileDialog.getOpenFileName(self, 'выберете  файл разграфки', DataDir, filter='*.txt') #Координаты в выходной проекции
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
					self.orthoBounds.append(element) #ЭТО МАССИВ с ГРАНИЦАМИ ОРТОФОТО 
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
		outputdir = QFileDialog.getExistingDirectory(self, 'выберете дирректорию', DataDir)
		if not outputdir=='':
			self.OUT_dir=outputdir
			self.TXT_OUTFOLDER.setText(str(self.OUT_dir))
			self.unlock_export(2)  #разблокирует экспорт, если заданы разграфка и дирректория
		else:
			return
		print ('orthoBounds=',len(self.orthoBounds))

	def export_ortho(self,proc_type): # универсальная процедура экспорта для локлаьной и для сетевой обработки
		#global chunk
		
		''' ЭТО ПРОВЕРКА ДЛЯ ПОСТРОЕНИЯ ОРТО ПЕРЕД РАБОТОЙ В ТЕКУЩЕЙ ВЕРСИИ ФУНКЦИЯ ОТКЛЮЧЕНА!!
		if self.checkExportOrtho.isChecked()==True:
			statOrthoBuild=True
		else:
			statOrthoBuild=False
		# 000000 Проверка на наличие ортофото или дем перед работой
		if (doc.chunk.orthomosaic==None and statOrthoBuild==False):
			PhotoScan.app.messageBox('Нет орто!!')
			return
		elif (doc.chunk.elevation==None and statOrthoBuild==True):
			PhotoScan.app.messageBox('Нет ДЕМ!!')
			return
		'''
		#Определение вида экспорта - орто или дем
		if self.CheckOrtho_Radio.isChecked()==True:
			ExportType='ORTHO'
		elif self.CheckDem_Radio.isChecked()==True:
			ExportType='DEM'
		else:
			AssertionError("Какой процесс экспорта?")
		
			
		#ПРОВЕРКИ НАЛИЧИЯ ДЕМ И ОРТО
		if (doc.chunk.orthomosaic==None and ExportType=='ORTHO'):
			PhotoScan.app.messageBox('Нет орто!!')
			return
		elif (doc.chunk.elevation==None and ExportType=='DEM'):
			PhotoScan.app.messageBox('Нет ДЕМ!!')
			return
		
		file_format=self.file_format.currentText()
		print ('orthoBounds=',len(self.orthoBounds))
		task=[] #Это СПИСОК тасков
		DifPix=float(self.dif_pix.text())
		if self.block_size.currentText()=='Full':
			BlockSize=0
		else:
			BlockSize=int(self.block_size.currentText())

		# Цикл для запуска ортофото локально или для забивания стека на сеть из массива
		try:
			for cu_string in self.orthoBounds:
				OName=cu_string[0]
				XMLeft=float(cu_string[1])
				YMDown=float(cu_string[2])
				sizeXM=float(cu_string[3])
				sizeYM=float(cu_string[4])
				shapeNumber=int(cu_string[5])
				cu_Region=self.OrthoBoundCalc(XMLeft,YMDown,sizeXM,sizeYM)#Функция вычисления границ # изменить под сетевую обработку с тайлами
				if file_format=='JPG' and ExportType=='ORTHO':
					fileoutname=self.OUT_dir+"\\ortho_"+OName+".jpg"
				elif file_format=='TIF' and ExportType=='ORTHO':
					fileoutname=self.OUT_dir+"\\ortho_"+OName+".tif"
				elif file_format=='TIF' and ExportType=='DEM':
					fileoutname=self.OUT_dir+"\\dem_"+OName+".tif"
				else:
					print("Формат файла?")

				if proc_type=='local': #КОММАНДЫ для локальной обработки
					print ('Обработка локально')
					''' ПОСТРОЕНИЕ ОРТОФОТО В ЭТОЙ ВЕРСИИ ОТКЛЮЧЕНО
					if statOrthoBuild==True: 
						#chunk.buildOrthomosaic(surface=PhotoScan.ElevationData, blending=PhotoScan.MosaicBlending, color_correction=False, projection=self.out_crs, region=cu_Region,dx=DifPix, dy=DifPix)
						chunk.buildOrthomosaic(surface=PhotoScan.ElevationData, blending=PhotoScan.MosaicBlending, projection=self.out_crs, region=cu_Region,dx=DifPix, dy=DifPix)
					'''
					
					if CommandStack==1 and ExportType=='ORTHO':
						if file_format=='JPG': chunk.exportOrthomosaic(fileoutname, format="jpg", projection=self.out_crs, region=cu_Region, dx=DifPix, dy=DifPix, blockw=BlockSize, blockh=BlockSize, write_kml=False, write_world=True)
						elif file_format=='TIF': chunk.exportOrthomosaic(fileoutname, format="tif", projection=self.out_crs, region=cu_Region, dx=DifPix, dy=DifPix, blockw=BlockSize, blockh=BlockSize, write_kml=False, write_world=True, tiff_compression="jpeg", tiff_big=False)
						#сжатие LZW
						#elif file_format=='TIF': chunk.exportOrthomosaic(fileoutname, format="tif", region=cu_Region, projection=self.out_crs,dx=DifPix, dy=DifPix, blockw=BlockSize, blockh=BlockSize, write_kml=False, write_world=True, tiff_compression="lzw", tiff_big=False)
						else: print("Формат файла?")
					elif CommandStack==5 and ExportType=='ORTHO':
						if file_format=='JPG': chunk.exportOrthomosaic(fileoutname, PhotoScan.RasterFormatTiles, PhotoScan.ImageFormatJPEG, region=cu_Region, projection=self.out_crs,dx=DifPix, dy=DifPix, blockw=BlockSize, blockh=BlockSize, write_kml=False, write_world=True)
						elif file_format=='TIF': chunk.exportOrthomosaic(fileoutname, PhotoScan.RasterFormatTiles, PhotoScan.ImageFormatTIFF, region=cu_Region, projection=self.out_crs,dx=DifPix, dy=DifPix, blockw=BlockSize, blockh=BlockSize, write_kml=False, write_world=True, tiff_compression=PhotoScan.TiffCompressionJPEG, tiff_big=False)
						#сжатие LZW
						#elif file_format=='TIF': chunk.exportOrthomosaic(fileoutname, PhotoScan.RasterFormatTiles,PhotoScan.ImageFormatTIFF, region=cu_Region, projection=self.out_crs,dx=DifPix, dy=DifPix, blockw=BlockSize, blockh=BlockSize, write_kml=False, write_world=True, tiff_compression=PhotoScan.TiffCompressionLZW, tiff_big=False)
						else: print("Формат файла?")
					elif CommandStack==1 and ExportType=='DEM':
						print ("Экспорт ДЕМ локально")
						if file_format=='TIF': chunk.exportDem(fileoutname, format="tif", projection=self.out_crs, region=cu_Region, dx=DifPix, dy=DifPix, blockw=BlockSize, blockh=BlockSize, write_kml=False, write_world=True,  tiff_big=False)
					elif CommandStack==5 and ExportType=='DEM':
						print ("Экспорт ДЕМ локально")
						if file_format=='TIF': chunk.exportDem(fileoutname, PhotoScan.RasterFormatTiles, PhotoScan.ImageFormatTIFF, region=cu_Region, projection=self.out_crs,dx=DifPix, dy=DifPix, blockw=BlockSize, blockh=BlockSize, write_kml=False, write_world=True,  tiff_big=False)
						
				elif proc_type=='net':
					print ('Обработка по сети')
					
					''' ПОСТРОЕНИЕ ОРТОФОТО В ЭТОЙ ВЕРСИИ ОТКЛЮЧЕНО
					#Построить ортофото
					if statOrthoBuild==True:
						workBuild = PhotoScan.NetworkTask() # СОздаем ворк и забиваем его параметрами
						#Версионность
						if CommandStack==1:
							workBuild.params['ortho_surface'] = 0
							workBuild.params['resolution_x'] = DifPix
							workBuild.params['resolution_y'] = DifPix
						elif CommandStack==5:
							workBuild.params['ortho_surface'] = 4
							workBuild.params['resolution'] = DifPix
						else:
							return
						workBuild.name = "BuildOrthomosaic"
						workBuild.frames.append((chunk.key,0))
						workBuild.params['network_distribute'] = True
						
						task.append(workBuild) #Добавляем задачу построения в таск
					'''
					
					#Экспортировать ортофото
					workExport = PhotoScan.NetworkTask() # СОздаем ворк и забиваем его параметрами
					#ВЕРСИОННОСТЬ
					if CommandStack==1 and ExportType=='ORTHO':
						workExport.name = "ExportOrthomosaic"
						workExport.params['resolution_x'] = DifPix
						workExport.params['resolution_y'] = DifPix
						if file_format=='JPG': workExport.params['raster_format'] = 2
						elif file_format=='TIF': workExport.params['raster_format'] = 1
						else: print("Формат файла?")
					elif CommandStack==5 and ExportType=='ORTHO':
						workExport.name = "ExportRaster"
						workExport.params['resolution'] = DifPix
						if file_format=='JPG': workExport.params['image_format'] = 1
						elif file_format=='TIF': workExport.params['image_format'] = 2 #Значение на шару!!! ПРОВЕРИТЬ
						else: print("Формат файла?")
					elif CommandStack==1 and ExportType=='DEM':
						print ("Экспорт ДЕМ по сети")
						workExport.name = "ExportDem"
						workExport.params['resolution_x'] = DifPix
						workExport.params['resolution_y'] = DifPix
					elif CommandStack==5 and ExportType=='DEM': #НЕ ОТЛАЖЕНО ПАРАМЕТРЫ НА ШАРУ
						print ("Экспорт ДЕМ по сети")
						workExport.name = "ExportOrthomosaic"
						workExport.params['resolution'] = DifPix
						pass
					else:
						return
					
					workExport.frames.append((chunk.key,0))
					workExport.params['write_world'] = 1
					if self.block_size.currentText()=='Full':# Условие на запись тайлов
						workExport.params['write_tiles'] = 0
					else:
						workExport.params['write_tiles'] = 1
					workExport.params['tile_width'] = BlockSize
					workExport.params['tile_height'] = BlockSize
					workExport.params['path'] = fileoutname #выходная дирректория с именем файла
					workExport.params['region'] = cu_Region
					# ВНИМАНИЕ! По сети нельзя экспортировать в пользовательской проекции ИЛИ проекция должна быть НА ВСЕХ НОДАХ
					workExport.params['projection'] = self.out_crs.authority #Из объекта проекция берется только ее номер EPSG::32637 
					#ВНИМАНИЕ ЭКСПОРТ ОТКЛЮЧЕН!!!!
					task.append(workExport) #Добавляем задачу в таск
				else:
					print ('Пока не задано')
			PhotoScan.app.messageBox('Обработка закончена')
		except Exception as e:
			print (e)
			PhotoScan.app.messageBox('Что-то пошло не так ((')
			return
				#break
#Запуск сетевого стека, таска в обработку
		if proc_type=='net':
			print(ProjectLocalPath_auto)
			print (ProjectPath)
			client.connect(ServerIP)
			batch_id = client.createBatch(ProjectPath, task) 
			
			if batch_id==None: #Проверка наличия проекта в сети
				PhotoScan.app.messageBox('<B>Этот проект уже запущен в обработку!!!<B>')
				self.unlock_export(5)
			else:
				print ('Проект работает под номером ',batch_id)
				client.resumeBatch(batch_id)
				self.unlock_export(5)
				PhotoScan.app.messageBox('Проект поставлен в очередь сетевой обработки')
			
			client.disconnect()
			pass

#НАЧАЛО_ПРОГРАММЫ______Глобальные переменные_____________

try:
	ProjectLocalPath_auto = os.path.relpath(ProjectPath, RootDir) # путь до проекта относительно сетевой папки
	#ЭТИ КОМАНДЫ СРАЗУ ЗАПУСКАЮТ ОКНО
	parent = QApplication.instance().activeWindow()
	dlg = ExportOrthoWin(parent)
except Exception as e:
	PhotoScan.app.messageBox('Откройте рабочий проект! ')
	print(e)
	pass

print('\n\n ============== STOP ==============')

pass