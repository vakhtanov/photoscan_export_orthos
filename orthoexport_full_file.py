import PhotoScan
import os
from math import ceil
chunk = PhotoScan.app.document.chunk
# ВЫХОДНАЯ ПРОЕКЦИЯ - Краснодарская первый варинат, без номера зоны
out_crs=PhotoScan.CoordinateSystem('PROJCS["SK-42/GK_ZONE7_noZone (var1)",GEOGCS["Pulkovo 1942",DATUM["Pulkovo 1942",SPHEROID["Krassowsky 1940",6378245,298.3,AUTHORITY["EPSG","7024"]],TOWGS84[82.28,-123.01,-138.08,1.07,-2.371,1.15,1.867],AUTHORITY["EPSG","----"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9102"]],AUTHORITY["EPSG","----"]],PROJECTION["Transverse_Mercator",AUTHORITY["EPSG","9807"]],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",39],PARAMETER["scale_factor",1],PARAMETER["false_easting",7500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]]]')
# предварительные настройки
difX=0.15
difY=0.15
sizeXM=1000.05
sizeYM=1000.05
sizeXMpix=ceil(sizeXM/difX)
sizeYMpix=ceil(sizeYM/difY)
#if sizeXMpix%2: sizeXMpix=sizeXMpix+1
#if sizeYMpix%2: sizeYMpix=sizeYMpix+1
sizeXMround=sizeXMpix*difX
sizeYMround=sizeYMpix*difY
# КООРДИАНТЫ ДОЛЖНЫ БЫТЬ В ВЫХОДНОЙ ПРОЕКЦИИ!!!!!
FileRazgr=os.path.dirname(__file__)+"/orthoexport_full_file_razgrafka.txt"



#ЗДЕСЬ ПОМЕНЯТЬ ПУТИ!!!
OFolder="v:\\Photoscan_Cluster\\test_test\\Ortho\\"




with open(FileRazgr) as file_razgr:
	for line in file_razgr:
		cu_string=line.split(";")
		print(cu_string)
		OName=cu_string[0]
		XMLeft=float(cu_string[1])
		YMDown=float(cu_string[2])
		cu_Region=(XMLeft,YMDown,XMLeft+sizeXMround+difX,YMDown+sizeYMround+difY)
		print (OName," ",sizeXMpix," ",sizeYMpix," ",XMLeft," ",YMDown," ",sizeXMround," ",sizeYMround)
		#экспорт в ЮТМ
		#chunk.exportOrthomosaic(OFolder+OName+"_UTM"+".tif", format="tif", region=cu_Region, dx=difX, dy=difY, write_kml=False, write_world=True, tiff_compression="lzw", tiff_big=False)
		#экспорт в ГК
		chunk.exportOrthomosaic(OFolder+OName+"_GK"+".tif", format="tif", region=cu_Region, projection=out_crs,dx=difX, dy=difY, write_kml=False, write_world=True, tiff_compression="lzw", tiff_big=False)

