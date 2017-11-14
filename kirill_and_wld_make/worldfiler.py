# -*- coding:utf-8  -*-
import os
import gdal
import math


def wordfiler(img_path, shapefile_path, filename_field, pix_res):
    ds = gdal.OpenEx(shapefile_path, 0)

    lyr = ds.GetLayer()

    # print (feat_count)
    for root, dirs, files in os.walk(img_path):
        for filename in files:
            name, ext = os.path.splitext(filename)
            # print ('name: ',name, ext)
            if ext == '.jpg':
                for feature in lyr:
                    # alpha = math.radians(feature.GetField('Angle'))
                    out_filename = feature.GetField(filename_field)
                    # print('outname before loop: ', out_filename)
                    if out_filename == name[:-9]:
                        feat_geom = feature.GetGeometryRef()  # feature geometry
                        geom = feat_geom.GetGeometryRef(0)  # geometry of geometry, without this you can't do GetPoint()
                        pt1 = geom.GetPoint(0)
                        pt2 = geom.GetPoint(1)  # always first point needed

                        dx, dy = pt2[0] - pt1[0], pt2[1] - pt1[1]
                        alpha = math.atan2(dx, dy) # rectangle main angle
                        par1, par2 = float(pix_res) * math.cos(alpha), float(pix_res) * math.sin(-alpha)
                        # corner_factor = pix_res * .5 # in order to bind raster to the corner of pixel, not to it's center
                        # print(out_filename, name)
                        out_filename = os.path.join(root, name)
                        with open(out_filename + '.wld', 'w') as out:
                            out.write(str(par1) + '\n')
                            out.write(str(par2) + '\n')
                            out.write(str(par2) + '\n')
                            out.write(str(-par1) + '\n')
                            out.write(str(pt2[0]) + '\n')
                            out.write(str(pt2[1]) + '\n')
                lyr.ResetReading()


if __name__ == '__main__':
    shp = r't:\0000_AirPatrol\NII_STT_Full_data\SAMARA\Razgrafka\Narezka_Samara_full_UTM39_lpu_full.shp'
    #shp = r't:\0000_AirPatrol\NII_STT\KAZAN\razgrafka_full2.shp'
    # shp = r't:\0000_AirPatrol\NII_STT\SAMARA\Narezka_Samara_full_UTM39_lpu_full.shp'
    img_path = r't:\0000_AirPatrol\NII_STT_Full_data\SAMARA\ortho\201708_listy_forMBtiles'
    # img_path = r'm:\AIRPATROL\01_Initial_data\GT_Samara\unpucked'
    shp_path = os.path.abspath(shp)
    field = 'filename'
    pix_res = 0.28
    wordfiler(img_path, shp_path, field, pix_res)
