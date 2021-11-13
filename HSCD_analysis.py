import numpy as np
import struct
import matplotlib.pyplot as plt
import pandas as pd
from scipy import interpolate
from matplotlib import lines
from PIL import Image, ImageDraw

def Input_filename():
    print("Please Input Experiment name :")
    filename = input()
    df = open("{}.HSC".format(filename),'rb')
    df2 = pd.read_csv(r'C:\Users\augus\OneDrive\デスクトップ\HSCD_analysis\HSCD_analysis\2d_cmf.csv', header = None)
    df3 = pd.read_csv(r'C:\Users\augus\OneDrive\デスクトップ\HSCD_analysis\HSCD_analysis\cccie64.csv',header = None)

    print("Please Input Compare blue No. :")
    blue_index = input()
    df4 = pd.read_csv(r'C:\Users\augus\OneDrive\デスクトップ\HSCD_analysis\HSCD_analysis\Seric_blue_analysis\{}\spectrumdata.csv'.format(blue_index),header = None) 
    df5 = pd.read_csv(r'C:\Users\augus\OneDrive\デスクトップ\HSCD_analysis\HSCD_analysis\Seric_blue_analysis\LIGHTDATA\Light.csv',header = None)
    return filename, blue_index, df, df2, df3, df4, df5


def ReadHeader(filename, df):
    data = df.read()
    header = struct.unpack_from("L", data,0)
    lenH = struct.unpack_from("L", data,4)
    lenV = struct.unpack_from("L", data,8)
    pixel = lenH[0] * lenV[0]
    return  data, header, lenH, lenV

def Input2(header, lenH, lenV):
    print("spectrum data has \n H: {}pixels \n V: {}lines \n Wavelength: {}samples".format(lenH[0],lenV[0],header[0]))
    print("h(0-{}):  ".format(lenH[0]-1))
    h = int(input())
    print("v(0-{}):  ".format(lenV[0]-1))
    v = int(input())
    print("Wavlength_index(0-255)")
    index = int(input())
    return h, v, index

def ReadData(data, lenH, lenV, h, v):
    offset_header = 12
    offset = offset_header
    Wavelength=[]
    for i in range(256):
        values = struct.unpack_from("f",data, offset)
        Wavelength.append(values[0])
        offset += 4
     

    offset = offset_header + 4 * 256 * lenH[0] * v +  4 * 256 * (h+1)
    Intensity = []
    for i in range(256):
        values = struct.unpack_from("f",data,offset)
        Intensity.append(values[0])
        offset += 4
    return Wavelength, Intensity



def Img(data, lenH, lenV):
    offset_header = 12 + 4*256
    offset = offset_header

    list = []
    for j in range(lenH[0]*lenV[0]): 
        Intensities= []
        for i in range(256):
            intensity = struct.unpack_from("f", data, offset)
            Intensities.append(intensity[0])
            offset += 4 
        list.append(Intensities)
    return list

def MinMax(list, index):
    max = list[0][index] 
    min = list[0][index]
    for i in range(len(list)):
        tmp = list[i][index]
        if max < tmp: max = tmp
        if min > tmp: min = tmp
    return max, min

def NormalizeMinMax(axes, list, max, min, index):
   for i in range(len(list)):
       list[i][index] = ((list[i][index]) - min) / (max - min)

   
def CreateImg(list,lenH, lenV, index, h, v):
    im = Image.new("RGBA", (10*lenH[0], 10*lenV[0]), (255,255,255))
    draw = ImageDraw.Draw(im)
    for x in range(lenH[0]):
        for y in range(lenV[0]):
            draw.rectangle((x*10, 10*lenV[0]-y*10, x*10 +10 , 10* lenV[0] - y*10 -10 ), fill = (int(list[x + lenH[0]*y][index]*255),int(list[x + lenH[0]*y][index]*255),int(list[x + lenH[0]*y][index]*255)), outline =(int(list[x + lenH[0]*y][index]*255),int(list[x + lenH[0]*y][index]*255),int(list[x + lenH[0]*y][index]*255)))
            draw.rectangle((h*10,10*lenV[0]-10*v,h*10 +10, 10*lenV[0]-(10*v +10)), fill = (255,0,0),outline =(255,0,0))
    im.show()
    return 

def CreateFigure1(axes, filename, blue_index, Wavelength, Intensity, df4, df5):
    Intensity = np.array(Intensity)
    RI = Intensity / max(Intensity)

    RI_light = df5.iloc[1,0:256]
    RI_light /= max(RI_light)


    RI_comp = df4.iloc[1,0:256]
    RI_comp /= max(RI_comp)
    axes[0,0].plot(Wavelength, RI, linewidth = 1, color = "blue" ,label ="Experiment data" )
   # axes[0,0].plot(Wavelength, RI_comp, linewidth=1, color = "red", label = "{}".format(blue_index))
    axes[0,0].plot(Wavelength, RI_light, linewidth=1, color = "black", label = "Light")
    axes[0,0].set_title("{} : {}".format(filename,blue_index))
    axes[0,0].set_xlabel("Wavelength λ nm")
    axes[0,0].set_ylabel("Reflectance Intensity")
    axes[0,0].set_xlim(400,730)
    axes[0,0].set_ylim(0,1.0)
    axes[0,0].grid(True)
    axes[0,0].legend(loc = "upper right")

    return RI, RI_comp

def CreateFigure2(axes, filename,blue_index, Wavelength, RI, data, df2, df3, df4):
    #計測値
    eye_w = []
    f1 = []
    f2 = []
    f3 = []

    for i in range(len(df2.index)):
        eye_w.append(df2.iloc[i][0])
        f1.append(df2.iloc[i][1])
        f2.append(df2.iloc[i][2])
        f3.append(df2.iloc[i][3])

    f1_n = interpolate.interp1d(eye_w, f1, kind="linear")
    f2_n = interpolate.interp1d(eye_w, f2, kind="linear")
    f3_n = interpolate.interp1d(eye_w, f3, kind="linear")
    Xlist = []
    Ylist = []
    Zlist = []
    for i in range(33,256):
        Xlist.append( RI[i]*f1_n(Wavelength[i]))
        Ylist.append( RI[i]*f2_n(Wavelength[i]))
        Zlist.append( RI[i]*f3_n(Wavelength[i]))
    X = sum(Xlist)
    Y = sum(Ylist)
    Z = sum(Zlist)
    x = round(X / (X + Y + Z),3)
    y = round(Y / (X + Y + Z),3)
    print(x,y)

    #理論範囲
    xy = []
    for i in range(len(df3.index)):
        X_t = df3.iloc[i][1]
        Y_t = df3.iloc[i][2]
        Z_t = df3.iloc[i][3]
        if((X_t + Y_t + Z_t) == 0):
            continue
        x_t = X_t / (X_t + Y_t + Z_t)
        y_t = Y_t / (X_t + Y_t + Z_t)
        xy.append([x_t, y_t])

    xy_df = pd.DataFrame(xy, columns=["x", "y"])
    x0 = xy_df.iloc[0][0]
    y0 = xy_df.iloc[0][1]
    xe = xy_df.iloc[len(xy_df.index)-1][0]
    ye = xy_df.iloc[len(xy_df.index)-1][1]
    line = lines.Line2D([x0, xe], [y0, ye])

    # xy色度図のスペクトル軌跡描画
    axes[0,1].add_line(line)
    axes[0,1].plot(xy_df["x"], xy_df["y"],'-')
    axes[0,1].plot(x, y,"o", color = "blue", label = "Experiment data")
    #axes[0,1].plot(df4.iloc[4,0],df4.iloc[5,0],"o", color="red", label = "{}".format(blue_index))
    axes[0,1].set_title("xy choromaticity diagram({} : {})".format(filename, blue_index))
    axes[0,1].set_xlabel("Wavelength λ nm")
    axes[0,1].set_ylabel("Reflectance Intensity")
    axes[0,1].set_xlim(0,0.8)
    axes[0,1].set_ylim(0,0.9)
    axes[0,1].grid(True)
    axes[0,1].legend(loc = "upper right")
   

def CreateFigure3(axes, filename,blue_index, Wavelength,RI,RI_comp, df4, df5):
    RI_light = df5.iloc[1,37:205]
    RI_light /= max(RI_light)

    beta = RI[37:205]/RI_light
    beta_comp = RI_comp[37:205] / RI_light

    beta /= max(beta)
    beta_comp /= max(beta_comp)

    axes[1,0].plot(Wavelength[37:205], beta, linewidth = 1, color = "blue", label = "Experiment Data")
   # axes[1,0].plot(Wavelength[37:205], beta_comp, linewidth = 1, color = "red", label = "{}".format(blue_index))
    axes[1,0].set_title("{} : {}".format(filename, blue_index))
    axes[1,0].set_xlabel("Wavelength")
    axes[1,0].set_ylabel("Reflectance Intensity")
    axes[1,0].set_xlim(400,730)
    axes[1,0].set_ylim(0,1.0)
    axes[1,0].grid(True)
    axes[1,0].legend(loc = "lower right")

def Run():

    filename, blue_index, df, df2, df3 ,df4, df5= Input_filename()
    
    data, header, lenH, lenV = ReadHeader(filename, df)
    
    h, v, index= Input2(header, lenH, lenV)

    Wavelength, Intensity = ReadData(data, lenH, lenV, h, v)
    
    fig,axes = plt.subplots(nrows = 2, ncols = 2, figsize =(16, 12), sharex = False, squeeze = False)
    RI, RI_comp = CreateFigure1(axes, filename, blue_index, Wavelength, Intensity, df4, df5)
    CreateFigure2(axes, filename,blue_index ,Wavelength, RI, data, df2, df3, df4)
    CreateFigure3(axes, filename,blue_index ,Wavelength, RI,RI_comp, df4, df5)
    
    
    list = Img(data, lenH, lenV)
    max, min = MinMax(list, index)
    NormalizeMinMax(axes, list, max, min, index)
    CreateImg(list,lenH, lenV, index, h, v)
    plt.show()

    df.close()
    print("end")

Run()