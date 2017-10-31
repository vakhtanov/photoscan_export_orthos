import PhotoScan
import os
from math import ceil
from PySide import QtGui, QtCore


#______________________Создаем интерфейс___________________

#______________________Интерфейс готов_____________________
chunk = PhotoScan.app.document.chunk
# ВЫХОДНАЯ ПРОЕКЦИЯ 
out_crs=PhotoScan.CoordinateSystem('PROJCS["WGS 84 / UTM zone 37N",GEOGCS["WGS 84",DATUM["World Geodetic System 1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9102"]],AUTHORITY["EPSG","4326"]],PROJECTION["Transverse_Mercator",AUTHORITY["EPSG","9807"]],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",39],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AUTHORITY["EPSG","32637"]]')
#out_crs=PhotoScan.CoordinateSystem('PROJCS["WGS 84 / UTM zone 38N",GEOGCS["WGS 84",DATUM["World Geodetic System 1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9102"]],AUTHORITY["EPSG","4326"]],PROJECTION["Transverse_Mercator",AUTHORITY["EPSG","9807"]],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",45],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AUTHORITY["EPSG","32638"]]')

DATA_OK=0



#sizeXM=1000.05
#sizeYM=1000.05
#if sizeXMpix%2: sizeXMpix=sizeXMpix+1
#if sizeYMpix%2: sizeYMpix=sizeYMpix+1


class ExportOrthoWin(QtGui.QDialog):
#_____________Пременные уровня класса___________
	TXT_name=[] #имя файла с разграфкой
	OUT_dir=[] #выходная дирректория
	DifPix=float(0.1) #размер пикселя
	BlockSize=int(8192) #размер блока
	#messa_box=PhotoScan.app.messageBox('Неверный формат')
	
#__________________________________________________
	def __init__(self, parent):
		QtGui.QDialog.__init__(self, parent)
		self.setWindowTitle("Экспорт Орто по разграфке")
		self.resize(500, 250) 
		self.txt_comment = QtGui.QLabel("	Модуль экспортирует ортофото из фотоскана по нарезке. \
Нарезка в текстовом файле: название листа, координаты нижнего левого угла, размеры. Проекция нарезки должна совпадать с проекцией выходного ортофотоплана.\
Листы делятся по нарезке, а внутри нарезки по блокам, размеры задаются")
		self.txt_comment.setWordWrap(True)
		self.now_prj = QtGui.QLabel(str(out_crs))  
		self.select_prj = QtGui.QPushButton("Выберете проекцию")  #(" открыть ")
		self.select_prj.setFixedSize(150, 26)
		
		
		self.TXT_dif_pix = QtGui.QLabel("<B>Размер пикселя: </B>")
		self.TXT_dif_pix.setFixedSize(150, 26)
		self.dif_pix = QtGui.QLineEdit()  
		self.dif_pix.setText('0.1')  
		self.dif_pix.setFixedSize(100, 26)  
		
		items_bloksize = ('5000', '8192', '10000', '15000', '20000', '25000', '29999')
#		items_bloksize = {5000:5000, 8192:8192, 10000:10000, 15000:15000, 20000:20000, 25000:25000, 29999:29999}
		self.TXT_block_size = QtGui.QLabel("<B>Размер блока: </B>",)
		self.TXT_block_size.setFixedSize(150, 26)
		self.block_size = QtGui.QComboBox() 
		self.block_size.setFixedSize(100, 26)
		self.block_size.addItems(items_bloksize)
		self.block_size.setCurrentIndex(1)
		#self.block_size.currentIndex(1)
		
		self.TXT_filename = QtGui.QLabel("Файл разграфки(имя; X0; Y0; sizeX; SizeY)")  
		self.filename = QtGui.QPushButton("Выберете Файл разграфки")  #(" открыть ")
		self.filename.setFixedSize(150, 26)
		
		self.TXT_OUTFOLDER = QtGui.QLabel("Выходная дирректория")  
		self.OUTFOLDER = QtGui.QPushButton("Выберете дирректорию")  #(" открыть ")
		self.OUTFOLDER.setFixedSize(150, 26)
		
		self.GoGo = QtGui.QPushButton("Экспорт")  #(" сохранить файл ")
		self.GoGo.setFixedSize(150, 26)
		self.GoGo.setDisabled(True)
		
		vbox = QtGui.QVBoxLayout()
		
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
		hbox4.addWidget(self.filename,alignment=0)
		hbox4.addWidget(self.TXT_filename,alignment=0)
		
		hbox5 = QtGui.QHBoxLayout()
		#hbox5.addStretch(1)
		hbox5.addWidget(self.OUTFOLDER,alignment=0)
		hbox5.addWidget(self.TXT_OUTFOLDER,alignment=0)
		
		#vbox.addStretch(1)
		vbox.addLayout(hbox0)
		vbox.addLayout(hbox1)
		vbox.addLayout(hbox2)
		vbox.addLayout(hbox3)
		vbox.addLayout(hbox4)
		vbox.addLayout(hbox5)
		vbox.addWidget(self.GoGo, stretch=0, alignment=0)
		
		self.setLayout(vbox)
		
		def unlock_export(sel):
			global DATA_OK #Переменная нужна для разблокирования кнопки Экспорт. Два критических параметра:Файл разграфки и выходная дирректория, каждый добавляет по еденице.
			if sel==5 and DATA_OK==1: DATA_OK=0; self.GoGo.setDisabled(True)
			if sel==5 and DATA_OK==2: DATA_OK=2; self.GoGo.setDisabled(True)
			if sel==5 and DATA_OK==3: DATA_OK=2; self.GoGo.setDisabled(True)
			if DATA_OK==1 and sel==2: DATA_OK=3
			if DATA_OK==2 and sel==1: DATA_OK=3
			if DATA_OK==0 and sel != 5: DATA_OK=sel
			if DATA_OK==3 and sel != 5: self.GoGo.setDisabled(False);print ('unlock')
			#print (DATA_OK)
		def input_razgr_name():
			# КООРДИАНТЫ ДОЛЖНЫ БЫТЬ В ВЫХОДНОЙ ПРОЕКЦИИ!!!!!
			global TXT_name
			global DATA_OK
			DataDir = os.path.dirname(__file__)
			textfilename= QtGui.QFileDialog.getOpenFileName(self, 'выберете файл разграфки', DataDir, filter='*.txt')
			if not textfilename[0]=='': TXT_name=textfilename 
			self.TXT_filename.setText(str(TXT_name[0]))
			with open(TXT_name[0]) as f:
				for line in f:
					znach=line.split(";")
					try:
						if not (isinstance(znach[0],str)):  PhotoScan.app.messageBox('Неверный форматS'); unlock_export(5); return
						if not (isinstance(float(znach[1]),(float,int))):  PhotoScan.app.messageBox('Неверный формат1i'); unlock_export(5);return
						if not (isinstance(float(znach[2]),(float,int))):  PhotoScan.app.messageBox('Неверный формат2i'); unlock_export(5);return
						if not (isinstance(float(znach[3]),(float,int))):  PhotoScan.app.messageBox('Неверный формат3i'); unlock_export(5);return
						if not (isinstance(float(znach[4]),(float,int))):  PhotoScan.app.messageBox('Неверный формат4i'); unlock_export(5);return
					except:
						pass
						PhotoScan.app.messageBox('Неверный формат_;'); unlock_export(5);return
			if not (TXT_name[0]==''):unlock_export(1) #разблокирует экспорт, если заданы разграфка и дирректория

			
		def set_projection():
			global out_crs
			out_crs=PhotoScan.app.getCoordinateSystem('Система координат', out_crs)
			self.now_prj.setText(str(out_crs))
			
			
		def input_out_dir():
			global DATA_OK
			global OUT_dir
			DataDir = os.path.dirname(__file__)
			outputdir= QtGui.QFileDialog.getExistingDirectory(self, 'выберете файл разграфки', DataDir)
			if not outputdir=='':OUT_dir=outputdir
			self.TXT_OUTFOLDER.setText(str(OUT_dir))
			if not (OUT_dir==''):unlock_export(2)  #разблокирует экспорт, если заданы разграфка и дирректория
		
		def export_ortho(): # не опред.
			pass
			global TXT_name
			global DifPix
			global BlockSize
			global OUT_dir
			DifPix=float(self.dif_pix.text())
			BlockSize=int(self.block_size.currentText())
			#ПРвоерка исходных данных
			try:
				if not (isinstance(TXT_name[0],str)): PhotoScan.app.messageBox('Неверный формат txt')
				if not (isinstance(OUT_dir,str)): PhotoScan.app.messageBox('Неверный формат out')
				if not (isinstance(float(DifPix),(float,int))): PhotoScan.app.messageBox('Неверный формат pix')
				if not (isinstance(float(BlockSize),(float,int))): PhotoScan.app.messageBox('Неверный формат block')
			except:
				pass
				PhotoScan.app.messageBox('Неверный формат in')
			with open(TXT_name[0]) as file_razgr:
				for line in file_razgr:
					cu_string=line.split(";")
					OName=cu_string[0]
					XMLeft=float(cu_string[1])
					YMDown=float(cu_string[2])
					sizeXM=float(cu_string[3])
					sizeYM=float(cu_string[4])
					
					cu_Region=(XMLeft,YMDown,XMLeft+sizeXM,YMDown+sizeYM)
					fileoutname=OUT_dir+"\\"+OName+".jpg"
					print (fileoutname," ",XMLeft," ",YMDown," ",sizeXM," ",sizeYM)
					chunk.exportOrthomosaic(fileoutname, format="jpg", region=cu_Region, projection=out_crs,dx=DifPix, dy=DifPix, blockw=BlockSize, blockh=BlockSize, write_kml=False, write_world=True, tiff_compression="lzw")
					# для тифа chunk.exportOrthomosaic(fileoutname, format="tif", region=cu_Region, projection=out_crs,dx=DifPix, dy=DifPix, blockw=BlockSize, blockh=BlockSize, write_kml=False, write_world=True, tiff_compression="lzw", tiff_big=False)
		def test_path():
			global TXT_name
			global DifPix #размер пикселя
			global BlockSize #размер блока
			global OUT_dir
			DifPix=float(self.dif_pix.text())
			BlockSize=float(self.block_size.currentText())
			print('Разграфка = '+ TXT_name[0])
			print('Дирректория = '+ OUT_dir)
			print('Размер блока: '+BlockSize+' Размер пикселя: '+DifPix)
			try:
				if not (isinstance(TXT_name[0],str)): PhotoScan.app.messageBox('Неверный формат txt'); return
				if not (isinstance(OUT_dir,str)): PhotoScan.app.messageBox('Неверный формат out'); return
				if not (isinstance(float(DifPix),(float,int))): PhotoScan.app.messageBox('Неверный формат pix'); return
				if not (isinstance(float(BlockSize),(float,int))): PhotoScan.app.messageBox('Неверный формат block'); return
			except:
				pass
				PhotoScan.app.messageBox('Неверный формат in'); return
			print ('Все готово, запускаем орто')
			with open(TXT_name[0]) as file_razgr:
				for line in file_razgr:
					cu_string=line.split(";")
					print (cu_string)
			#print (out_crs.name())
		QtCore.QObject.connect(self.filename, QtCore.SIGNAL("clicked()"), input_razgr_name)
		QtCore.QObject.connect(self.OUTFOLDER, QtCore.SIGNAL("clicked()"), input_out_dir)
		QtCore.QObject.connect(self.select_prj, QtCore.SIGNAL("clicked()"), set_projection)
		#QtCore.QObject.connect(self.GoGo, QtCore.SIGNAL("clicked()"), test_path)
		QtCore.QObject.connect(self.GoGo, QtCore.SIGNAL("clicked()"), export_ortho)
		self.exec()
'''
ДОБАВЛЕНИЕ ПУНКТА МЕНЮ ДЛЯ ВЫЗОВА ОКНА И ЗАПУСКА СКРИПТА
def main():
	parent = QtGui.QApplication.instance().activeWindow()
	dlg = TestWin(parent)
#Menu_Item_Name = "Дополнительно/Экспорт орто"
#PhotoScan.app.addMenuItem(Menu_Item_Name, main) #"main" - вызываемая из меню функция.
'''

#ЭТИ КОМАНДЫ СРАЗУ ЗАПУСКАЮТ ОКНО
parent = QtGui.QApplication.instance().activeWindow()
dlg = ExportOrthoWin(parent)


print('\n\n ============== STOP ==============')
