import numpy as np
import datetime
import sys
from netCDF4 import Dataset
from pmap import getmap
import lxml.etree as et
import sys

##########################################################################################
  #get hyflux data
##########################################################################################

def hget(t0,t1,hfpath,plat,plon,dt0,dt1):

  tinit=datetime.datetime(2010,1,1,0,0)


  plat=float(plat)
  plon=float(plon)

  tstart=datetime.datetime.strptime(t0,'%Y%m%d.%H')
  tend=datetime.datetime.strptime(t1,'%Y%m%d.%H')
  dt=(tend-tstart).total_seconds()
  ndt=dt/(3600*12)
  ndt=np.int(ndt)+1

  filename=hfpath+'calc_{}/bathymetry.tif'.format(t0)
  grid = getmap(filename)

  gt=grid.GeoTr

  width=grid.NCOLS
  height=grid.NROWS

  minx = gt[0]
  miny = gt[3] + width*gt[4] + height*gt[5] 
  maxx = gt[0] + width*gt[1] + height*gt[2]
  maxy = gt[3] 

  lon=np.linspace(minx,maxx,width,endpoint=True)
  lat=np.linspace(miny,maxy,height,endpoint=True)

  i=np.abs(lat-plat).argmin()
  j=np.abs(lon-plon).argmin()


  combined=[]
  tw=[]

  for it in range(ndt): 
    idate=tstart+datetime.timedelta(hours=12*it)
    dstamp=datetime.datetime.strftime(idate,'%Y%m%d.%H')

    # track completion
    sys.stdout.write('\r')
    sys.stdout.write(dstamp)
    sys.stdout.flush()

    try:
       tree0=et.ElementTree(file=hfpath+'calc_{}/locations.xml'.format(dstamp))
       for elem in list(tree0.getiterator()):
         if elem.tag == 'pubDate': 
                 tn=datetime.datetime.strptime(elem.text,'%d %b %Y %H:%M')
                 break
    except:
       sys.stdout.write('  > problem with locations.xml file')
       pass  

    if tn != tinit :
         sys.stdout.write( '  > restart date : {}'.format(tn))
         sys.stdout.write('\n')
         tinit=tn

    try:

      filename=hfpath+'calc_{}/NETCDF_H.nc'.format(dstamp)

      d =  Dataset(filename)
      ha=d.variables['HA'][:,i,j]
      t=d.variables['TIME'][:]

      tp=[]
#     print tinit,t[0]
      for ts in t:
        if t[0] == 0 :
          tp.append(idate+datetime.timedelta(seconds=ts))
          tinit=idate
        else:
          tp.append(tinit+datetime.timedelta(seconds=ts))
     
      for iw in range(dt0,dt1):
         tf = idate+datetime.timedelta(hours=iw)
         tw.append(tf)

         if np.argwhere(np.array(tp)==tf).flatten() :
            ii=np.argwhere(np.array(tp)==tf).flatten()[0]
            combined.append(ha[ii])
         else:
            combined.append(np.nan)


    except:
      sys.stdout.write('  > problem with netcdf file, skiping'.format(dstamp))
      sys.stdout.write('\n')

  htcw=np.array(tw).flatten()
  hcw=np.array(combined).flatten()

  return  htcw,hcw

if __name__ == "__main__":
    tstart=sys.argv[1]
    tend=sys.argv[2]
    path=sys.argv[3]
    plat =sys.argv[4]
    plon =sys.argv[5]
    t,ha=hget(tstart,tend,path,plat,plon)

