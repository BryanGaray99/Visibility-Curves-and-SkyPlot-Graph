# -*- coding: utf-8 -*-
"""
Created on Mon Nov  29 23:25:58 2021

@author: Bryan Garay
"""
import tkinter as tk
import numpy as np
from matplotlib import pyplot as plt
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, Angle, get_sun, get_moon
from datetime import datetime   
import pytz
from timezonefinder import TimezoneFinder
from astroplan.plots import plot_finder_image
from astroplan import FixedTarget, Observer
from astroplan.plots import plot_sky
from astropy.visualization import astropy_mpl_style, quantity_support
plt.style.use(astropy_mpl_style)
quantity_support()

def Plot_h():
    
    #Get entry values
    Lon_0 = Local_coord_lon.get()
    Lat_0 = Local_coord_lat.get()
    Ra_0 = Obj_coord_ra.get()
    Dec_0 = Obj_coord_dec.get()
    Name_0 = Obj_name_ent.get()
    
    Da_time_0 = Local_time_ent.get()

    #Time conversion to UTC
    
    Lat_1 = Angle(Lat_0)
    Lon_1 = Angle(Lon_0)
    Lat_2 = float(Lat_1.to_string(decimal=True))
    Lon_2 = float(Lon_1.to_string(decimal=True))
    
    Tzf = TimezoneFinder() 
    Lat_Lon = Tzf.timezone_at(lng=Lon_2, lat=Lat_2)
    City.configure(text=Lat_Lon)
    
    Time_zone = pytz.timezone(Lat_Lon)
    Naive_Local_time = datetime.strptime(Da_time_0, "%Y-%m-%d %H:%M:%S")
    Tz_Date_Time = Time_zone.localize(Naive_Local_time, is_dst=None)
    UTC_Date_Time = Tz_Date_Time.astimezone(pytz.utc)
    UTC0 = UTC_Date_Time.strftime("%Y-%m-%d %H:%M:%S")
    UTC.configure(text=UTC0)
    
    #Obtain altitude and azimuth of the object
    Ra_Dec = [Ra_0,Dec_0]
    Time_UTC = Time(UTC0)
    Location = EarthLocation.from_geodetic(Lon_0,Lat_0)
    Ra_Dec1 = SkyCoord(Ra_Dec[0],Ra_Dec[1],frame='icrs')
    
    Alt_Az_Frame_1 = AltAz(obstime=Time_UTC,location=Location)
    Alt_Az  = Ra_Dec1.transform_to(Alt_Az_Frame_1)
    Alt_0 = Alt_Az.alt
    Az_0  = Alt_Az.az
    
    Alt0.configure(text=Alt_0)
    Az0.configure(text=Az_0)
    
    #Create The plot h(t)
    #1. Obtain the time axis
    
    #1.1 Convert local time to midnight 
    Data1 = Time(Da_time_0)  # 2021-12-05 22:00:00.000 (Time)
    Data2 = 1*u.d
    Data3 = Data1 + Data2    # 2021-12-06 22:00:00.000 (Time)
    Data4 = Time(Data3, out_subfmt='date').iso #2021-12-06 (String)
    Data5 = Time(Data4, out_subfmt='date_hms') #2021-12-06 00:00:00.000 (Time)
    Data6 = Data5.strftime("%Y-%m-%d %H:%M:%S") #2021-12-06 00:00:00 (String)
    
    #1.2 Mignith conversion to UTC (Полночь)
    Mignight_Local = Data6
    Naive_Mignight_Local = datetime.strptime(Mignight_Local, "%Y-%m-%d %H:%M:%S")
    Tz_Date_Time_M = Time_zone.localize(Naive_Mignight_Local, is_dst=None)
    UTC_Date_Time_M = Tz_Date_Time_M.astimezone(pytz.utc)
    Mignight_UTC_0 = UTC_Date_Time_M.strftime("%Y-%m-%d %H:%M:%S")
    Mignight_UTC = Time(Mignight_UTC_0, out_subfmt='date_hms')
    
    
    #1.3 Obtain the array of times 
    Delta_Mignight_UTC = np.linspace(-12, 12, 1000)*u.hour
    Observation_night = Mignight_UTC + Delta_Mignight_UTC
    
    #2. Obtain the array of altitude
    Alt_Az_Frame_2 = AltAz(obstime=Observation_night,location=Location)
    
    #2.1 For the object h(t): 
      # Ra_Dec = [Ra_0,Dec_0]
      # Ra_Dec1 = SkyCoord(Ra_Dec[0],Ra_Dec[1],frame='icrs')
    Object_AltAz_obs_night = Ra_Dec1.transform_to(Alt_Az_Frame_2)
    
    #2.2 from astropy.coordinates import get_sun (Мы получаем Альт-азимутальные координаты солнца, так как с высотой солнца будут установлены границы сумерек.)
    Sun_AltAz_obs_night = get_sun(Observation_night).transform_to(Alt_Az_Frame_2)

    #2.3 from astropy.coordinates import get_moon
    Moon_AltAz_obs_night = get_moon(Observation_night).transform_to(Alt_Az_Frame_2)

    #3. Plot configuration 
    #3.1 Plot object,sun and moon. 
    plt.scatter(Delta_Mignight_UTC, Object_AltAz_obs_night.alt, c = Object_AltAz_obs_night.az, 
                lw=0, s=10, cmap='winter', label= Name_0)
                            #xcoor(time), ycoord(alt),
                            #c = Скаляр или последовательность из n чисел, 
                            #которые должны быть сопоставлены с цветами с использованием cmap )
                            #cmpa: a colormap, s = размер маркера, lw = (ширина краев маркера)
                            
    plt.plot(Delta_Mignight_UTC, Sun_AltAz_obs_night.alt, color='gold', label='Sun')
    plt.plot(Delta_Mignight_UTC, Moon_AltAz_obs_night.alt, color=[0.50]*3, ls='--', label='Moon')
    
    #3.2 Plot limits of the twilight (заполнение между пределами)
    plt.fill_between(Delta_Mignight_UTC, 0*u.deg, 90*u.deg, 
                     Sun_AltAz_obs_night.alt >= 0*u.deg, color='1', zorder=0)
                     # (x,y1,y2, where)
                     # x = time values, 
                     # y1,y2 Значения оси 'y', под которой будет применяться заполнение м.б крибая
                     # where: Определить, где надо исключить заполнение 
                     #        некоторых горизонтальных областей. 
                     # zorder: субординация, color = 1 white, 0 black 
                     
    plt.fill_between(Delta_Mignight_UTC, 0*u.deg, 90*u.deg,
                 Sun_AltAz_obs_night.alt < -0*u.deg, color='0.75', zorder=0, label='Civil')
    plt.fill_between(Delta_Mignight_UTC, 0*u.deg, 90*u.deg,
                 Sun_AltAz_obs_night.alt < -6*u.deg, color='0.5', zorder=0, label='Nautical')
    plt.fill_between(Delta_Mignight_UTC, 0*u.deg, 90*u.deg,
                 Sun_AltAz_obs_night.alt < -12*u.deg, color='0.25', zorder=0, label='Astronomical')
    plt.fill_between(Delta_Mignight_UTC, 0*u.deg, 90*u.deg,
                 Sun_AltAz_obs_night.alt < -18*u.deg, color='0', zorder=0, label='Nigth')

    #Change format of the x values from (-12,...,-6,...0,...6,...12) to (12,..18,...0,...6,...12)
    midnight_plot1 = np.arange(12, 24, 2)
    midnight_plot2 = np.arange(0, 14, 2)
    midnight_plot = [*midnight_plot1,*midnight_plot2]
    
    plt.xticks((np.arange(13)*2-12)*u.hour,midnight_plot) #First argument values, and second label to show 
   
    #3.3 Other parameters 
    plt.xlim(-12*u.hour, 12*u.hour) #limits of the plot in x in hours
    plt.xlabel('Hours in Local Time for '+Data4+'')
    
    plt.ylim(0*u.deg, 90*u.deg)  #limits of the plot in y in degrees
    plt.ylabel('Altitude [deg]')
    
    plt.legend(loc='upper center', ncol=3)
    plt.colorbar().set_label('Azimuth [deg]')
    plt.show()
    plt.savefig('ploth_t'+Data4+'.png', dpi=600)
    
def Verify():
    
    try: 
        Lon_0 = Local_coord_lon.get()
        Lat_0 = Local_coord_lat.get()
        Ra_0 = Obj_coord_ra.get()
        Dec_0 = Obj_coord_dec.get()
        Da_time_0 = Local_time_ent.get()

        Lat_1 = Angle(Lat_0)
        Lon_1 = Angle(Lon_0)
        Lat_2 = float(Lat_1.to_string(decimal=True))
        Lon_2 = float(Lon_1.to_string(decimal=True))
    
        Tzf = TimezoneFinder() 
        Lat_Lon = Tzf.timezone_at(lng=Lon_2, lat=Lat_2)

        Time_zone = pytz.timezone(Lat_Lon)
        Naive_Local_time = datetime.strptime(Da_time_0, "%Y-%m-%d %H:%M:%S")
        Time_zone.localize(Naive_Local_time, is_dst=None)

        Ra_Dec = [Ra_0,Dec_0]
        EarthLocation.from_geodetic(Lon_0,Lat_0)
        SkyCoord(Ra_Dec[0],Ra_Dec[1],frame='icrs')
        
        Check_2.configure(text='All the entries are correct, you can continue!',bg='green yellow')
        
    except: 
        Check_2.configure(text='Please verify the formats of coordinates and time, one or more entries are not correct!.', bg='yellow') 

def Sky_Plot():
    
    #Obtain entries
    Lon_0 = Local_coord_lon.get()
    Lat_0 = Local_coord_lat.get()
    Ra_0 = Obj_coord_ra.get()
    Dec_0 = Obj_coord_dec.get()
    Name_0 = Obj_name_ent.get()
    Da_time_0 = Local_time_ent.get()

    #Time zone
    Lat_1 = Angle(Lat_0)
    Lon_1 = Angle(Lon_0)
    Lat_2 = float(Lat_1.to_string(decimal=True))
    Lon_2 = float(Lon_1.to_string(decimal=True))
    Tzf = TimezoneFinder() 
    Lat_Lon = Tzf.timezone_at(lng=Lon_2, lat=Lat_2)
    Time_zone = pytz.timezone(Lat_Lon)
    
    #Coordinates
    Ra_Dec_0 = [Ra_0,Dec_0]
    Ra_Dec = SkyCoord(Ra_Dec_0[0],Ra_Dec_0[1],frame='icrs')
    
    #Time frame
    observe_time = Time(Da_time_0)
    observe_time_1 = observe_time + np.linspace(-12, 13, 12)*u.hour
    
    #Arguments
    Place = EarthLocation.from_geodetic(Lon_0,Lat_0)
    observer = Observer(location=Place,timezone=Time_zone)
    star = FixedTarget(name=Name_0, coord=Ra_Dec)

    plot_sky(star, observer, observe_time_1)
    plt.legend(loc='center left', bbox_to_anchor=(1.25, 0.5))
    plt.show()
     
def Photo():
    Name_0 = Obj_name_ent.get()
    Object = FixedTarget.from_name(Name_0)
    ax, hdu = plot_finder_image(Object)
    plt.show()

    
# Set-up the window
window = tk.Tk()
window.title("Observation tools")
window.geometry("1000x500")
window.configure(bg='Lightblue1')

#Frames 
Frame1 = tk.Frame(master=window,bg='Lightblue1')
Frame1.grid(column=0,row=3,sticky='w',pady=5)
Frame2 = tk.Frame(master=window,bg='Lightblue1')
Frame2.grid(column=0,row=5,pady=10,sticky='w')
Frame3 = tk.Frame(master=window,bg='Lightblue1')
Frame3.grid(column=0,row=6,pady=4,sticky='w')
Frame4 = tk.Frame(master=window,bg='Lightblue1')
Frame4.grid(column=0,row=8,sticky='w',pady=5)
Frame5 = tk.Frame(master=window,bg='Lightblue1')
Frame5.grid(column=0,row=9,sticky='w',pady=5)
Frame6 = tk.Frame(master=window,bg='Lightblue1')
Frame6.grid(column=0,row=10,sticky='w',pady=5)

#Title 1 
Title1 = tk.Label(master=window,text='Tools for your obsrvation night',font=('Times',12))
Title1.grid(column=0,row=0)
Title2 = tk.Label(master=window,text='Please enter your data according to the format examples',font=('Times',12))
Title2.grid(column=0,row=1,pady=5)

#Location coordinates
Local_coord = tk.Label(master=Frame1, text="Location coordinates:",bg='Lightblue1',font=('Times',12))
Local_coord.grid(column=0,row=3,sticky='w')

Local_coord_lon = tk.Entry(master=Frame1, width=15,font=('Times',12))
Local_coord_lon.grid(column=1,row=3,sticky='w')
Local_coord1 = tk.Label(master=Frame1, text="Format of the coordinates:",bg='Lightblue1',font=('Times',12))
Local_coord1.grid(column=0,row=4,sticky='w')
Local_coord2 = tk.Label(master=Frame1, text="Longitude",bg='Lightblue1',font=('Times',12))
Local_coord2.grid(column=1,row=5)
Local_coord3 = tk.Label(master=Frame1, text="+150d50m50s",bg='Lightblue1',font=('Times',12))
Local_coord3.grid(column=1,row=4,sticky='NS')

Local_coord_lat = tk.Entry(master=Frame1, width=15,font=('Times',12))
Local_coord_lat.grid(column=2,row=3,sticky='w')
Local_coord4 = tk.Label(master=Frame1, text="Latitude",bg='Lightblue1',font=('Times',12))
Local_coord4.grid(column=2,row=5)
Local_coord5 = tk.Label(master=Frame1, text="-30d30m30s",bg='Lightblue1',font=('Times',12))
Local_coord5.grid(column=2,row=4,sticky='NS')

#Date and time 
Local_time = tk.Label(master=Frame1, text="Local date and time:",bg='Lightblue1',font=('Times',12))
Local_time.grid(column=3,row=3,padx=20,sticky='w')
Local_time1 = tk.Label(master=Frame1, text="Format:",bg='Lightblue1',font=('Times',12))
Local_time1.grid(column=3,row=4,padx=20,sticky='w')
Local_time3 = tk.Label(master=Frame1, text=" 2021-12-23 01:04:00 ",bg='Lightblue1',font=('Times',12))
Local_time3.grid(column=4,row=4,sticky='NS')
Local_time4 = tk.Label(master=Frame1, text="  yyyy-mm-dd hh:mm:ss ",bg='Lightblue1',font=('Times',12))
Local_time4.grid(column=4,row=5,sticky='NS')
Local_time_ent = tk.Entry(master=Frame1, width=30,font=('Times',12))
Local_time_ent.grid(column=4,row=3,sticky='w')

#Objects coordinates
Title3 = tk.Label(master=window,text='Enter the equatorial coordinates of the object and its name',font=('Times',12))
Title3.grid(column=0,row=4)

Obj_coord = tk.Label(master=Frame2, text="Object coordinates:",bg='Lightblue1',font=('Times',12))
Obj_coord.grid(column=0,row=7,sticky='w')

Obj_coord_ra = tk.Entry(master=Frame2, width=15,font=('Times',12))
Obj_coord_ra.grid(column=1,row=7,sticky='w')
Obj_coord1 = tk.Label(master=Frame2, text="Format of the coordinates:",bg='Lightblue1',font=('Times',12))
Obj_coord1.grid(column=0,row=8,sticky='w')
Obj_coord2 = tk.Label(master=Frame2, text="12h47m43.32s",bg='Lightblue1',font=('Times',12))
Obj_coord2.grid(column=1,row=8,sticky='NS')
Obj_coord3 = tk.Label(master=Frame2, text="Right ascension",bg='Lightblue1',font=('Times',12))
Obj_coord3.grid(column=1,row=9)

Obj_coord_dec = tk.Entry(master=Frame2, width=15,font=('Times',12))
Obj_coord_dec.grid(column=2,row=7,sticky='w')
Obj_coord2 = tk.Label(master=Frame2, text="−59d41m19.4s",bg='Lightblue1',font=('Times',12))
Obj_coord2.grid(column=2,row=8,sticky='NS')
Obj_coord3 = tk.Label(master=Frame2, text="Declination",bg='Lightblue1',font=('Times',12))
Obj_coord3.grid(column=2,row=9)

#Object name
Obj_name = tk.Label(master=Frame2, text="Object name:",bg='Lightblue1',font=('Times',12))
Obj_name.grid(column=3,row=7,sticky='w',padx=20)
Obj_name_ent = tk.Entry(master=Frame2, width=30,font=('Times',12))
Obj_name_ent.grid(column=4,row=7,sticky='w')
Obj_name2 = tk.Label(master=Frame2, text="Examples:",bg='Lightblue1',font=('Times',12))
Obj_name2.grid(column=3,row=8,sticky='w',padx=20)
Obj_name3 = tk.Label(master=Frame2, text="vega, M1, M104",bg='Lightblue1',font=('Times',12))
Obj_name3.grid(column=4,row=8,padx=20)

#Optional to check the validity of the entries
Check_1 = tk.Button(master=Frame3, text="Press to check the validity of the entries",font=('Times',12), relief='raised', command=Verify)
Check_1.grid(column=0,row=0)

Check_2 = tk.Label(master=Frame3,font=('Times',12))
Check_2.grid(column=1,row=0,padx=10)

#Tools
Title4 = tk.Label(master=window,text='Observation Tools',font=('Times',12))
Title4.grid(column=0,row=7,sticky='w',pady=5)

#Button1
Plot_h_t1 = tk.Label(master=Frame4,text='Press to plot a visility curve for your object during the closest nigth',bg='Lightblue1',font=('Times',12))
Plot_h_t1.grid(column=0,row=0,sticky='w')
Plot_h_t = tk.Button(master=Frame4,text='Plot h(t)',command=Plot_h,font=('Times',12),relief='raised')
Plot_h_t.grid(column=1,row=0,sticky='w',padx=10)

City0 = tk.Label(master=Frame4,text='Time zone:',bg='Lightblue1',font=('Times',12))
City0.grid(column=2,row=0,sticky='w',padx=10)
City = tk.Label(master=Frame4,bg='Lightblue1',font=('Times',12))
City.grid(column=3,row=0,sticky='w')

UTC0 = tk.Label(master=Frame4,text='UTC:',bg='Lightblue1',font=('Times',12))
UTC0.grid(column=4,row=0,sticky='w',padx=10)
UTC = tk.Label(master=Frame4,bg='Lightblue1',font=('Times',12))
UTC.grid(column=5,row=0,sticky='w')

Alt = tk.Label(master=Frame4,text='Altitude:',bg='Lightblue1',font=('Times',12))
Alt.grid(column=2,row=2,sticky='w',padx=10)
Alt0 = tk.Label(master=Frame4,bg='Lightblue1',font=('Times',12))
Alt0.grid(column=3,row=2,sticky='w')

Az = tk.Label(master=Frame4,text='Azimuth:',bg='Lightblue1',font=('Times',12))
Az.grid(column=4,row=2,sticky='w')
Az0 = tk.Label(master=Frame4,bg='Lightblue1',font=('Times',12))
Az0.grid(column=5,row=2,sticky='w',padx=10)

#Button2
Sky_plot = tk.Label(master=Frame5, text='Press to plot Alt-azimutal coordinates in the sky',bg='Lightblue1',font=('Times',12))
Sky_plot.grid(column=0,row=0,sticky='w')

Sky_plot_1 = tk.Button(master=Frame5,text='Sky Plot',command=Sky_Plot,font=('Times',12),relief='raised')
Sky_plot_1.grid(column=1,row=0,sticky='w',padx=10)

#Button3
Photo_0 = tk.Label(master=Frame6, text='Press to display a photo of the object',bg='Lightblue1',font=('Times',12))
Photo_0.grid(column=0,row=0,sticky='w')

Photo_1 = tk.Button(master=Frame6,text='Display photo',command=Photo,font=('Times',12),relief='raised')
Photo_1.grid(column=1,row=0,sticky='w',padx=10)

#Run
window.mainloop()