import matplotlib.pyplot as plt
import cartopy
import cartopy.feature as cfeature
import cartopy.geodesic as geodesic
import cartopy.crs as ccrs
import cartopy.geodesic
import numpy as np
import shapely.geometry as sgeom
import warnings
import matplotlib

# Set the backend for matplotlib.
matplotlib.use("TkAgg")

class picketMap():

	def  __init__(self,picket_dict,central_station=None):
		self.pickets=picket_dict
		self.__define_extent()
		self.__unpack_central_station_params(central_station)
			
		self.__init_plot_params()	
		self.active_pickets=[] #TODO: Make this useful by adding a live plot
		
	def __unpack_central_station_params(self,central_station):
	
		self.central_station=central_station
		
		if central_station is not None:					
		
			self.central_name=list(self.central_station.keys())[0]
			self.central_lon=self.central_station[self.central_name]["Longitude"]
			self.central_lat=self.central_station[self.central_name]["Latitude"]
			
			if not (self.west < self.central_lon < self.east and self.south < self.central_lat < self.north):
					warnings.warn("Central station is not inside the picket radius")
			
		else:
			self.central_lon=(self.west + self.east)/2
			self.central_lat=(self.north + self.south)/2
			
		distances=[geodesic.Geodesic().inverse([self.central_lon,self.central_lat],[self.pickets[name]["Longitude"],self.pickets[name]["Latitude"]])
			for name in self.pickets]
						
		self.max_distance=np.max(distances)
				
	def __define_extent(self):
	
		#Define the location of the pickets
		self.north=np.max([self.pickets[picket]["Latitude"] for picket in self.pickets])+1
		self.south=np.min([self.pickets[picket]["Latitude"] for picket in self.pickets])-1
		
		self.east=np.max([self.pickets[picket]["Longitude"] for picket in self.pickets])+1
		self.west=np.min([self.pickets[picket]["Longitude"] for picket in self.pickets])-1
				
		self.extent=[self.west, self.east, self.north, self.south]
		
		
	def __init_plot_params(self):
	
		#Add concentric circles to help understand the plot
		self.circles = []
		self.circle_text_info=[] #Longitude and latitude of the text for the circles
		
		dist_step=200 #Size of the concentric circle gaps in kilometers
		circle_num=np.arange(1,np.ceil(self.max_distance/1000/dist_step)+1,1)
		for dist in circle_num*dist_step:
			cp=cartopy.geodesic.Geodesic().circle(lon=self.central_lon, lat=self.central_lat, radius=1000*dist, n_samples=50, endpoint=True)
			self.circles.append(sgeom.LinearRing(cp))
			
			self.circle_text_info.append([cp[np.argmin(cp[:,1]),0]-50/(dist)+dist/2100, #Longitude
											min(cp[:,1])+.1+0*100/(dist+200),			#Latitude
											dist]) #Distance
											#TODO standardize this equation for text location
		return
		
	def generate_plot(self,active_pickets=None):
		if hasattr(self, 'fig'):
			self.fig.show()
		else:
			print("Generating a new Picket Map")
			fig = plt.figure(2,figsize=(8, 8)) #TODO: Hardcoded figure 2, how do we know how many figures are on display? can we not hardcode this somehow?
			ax = fig.add_subplot(1, 1, 1,
								 projection=ccrs.AzimuthalEquidistant(central_longitude=self.central_lon,
																	  central_latitude=self.central_lat))
															  
			# Here we add the transform argument and use the Geodetic projection.
			ax.set_extent(self.extent)
			#ax.stock_img()
			ax.coastlines()
			ax.add_feature(cfeature.OCEAN)
			ax.add_feature(cfeature.LAND,facecolor='white')
			ax.add_feature(cfeature.BORDERS)
			#ax.gridlines()
			offset_lon=-1.6/2
			offset_lat=-1.2/2
	
			for station in self.pickets:
				ax.scatter(self.pickets[station]["Longitude"],self.pickets[station]["Latitude"], s=200,marker='.', color='yellow',edgecolors='black', alpha=0.7, transform=ccrs.Geodetic())
				ax.text(self.pickets[station]["Longitude"]+offset_lon,self.pickets[station]["Latitude"]+offset_lat,
						station,fontsize=10,weight='bold',transform=ccrs.Geodetic())
				
			if self.central_station is not None:
				ax.scatter(self.central_lon,self.central_lat, s=150,marker='*', color='black',edgecolors='black', alpha=0.7, transform=ccrs.Geodetic())
				ax.text(self.central_lon+offset_lon,self.central_lat+offset_lat,self.central_name,fontsize=10,weight='bold',transform=ccrs.Geodetic())

			for lon, lat, dist in self.circle_text_info:
				ax.text(lon,lat,str(dist),fontsize=8,transform=ccrs.Geodetic())
	
			ax.add_geometries(self.circles, crs=ccrs.PlateCarree(), edgecolor='k',facecolor="none", linestyle='--')
			fig.show()
			self.fig=fig
			self.ax=ax
