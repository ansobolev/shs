#!/usr/bin/python 
# __*__ coding: utf8 __*__

oneline = "Read, write and operate with models"

#import os
from model_base import model_base
# --------------------------------------------------------------------
class Free_class:
  pass

def bound(x, y):
	if x > y/2.: return x-y
	if x < -y/2. : return x+y
	return x

#=============================================================================
class model_ngbr(model_base):
  # --------------------------------------------------------------------
  def __init__(self,d={}):
    model_base.__init__(self,d)	
#    vc=self.vc
#    ix=self.legend.index('x')
#    for at in self.atoms:
#       at[ix]=at[ix]%vc[0]
#       at[ix+1]=at[ix+1]%vc[1]
#       at[ix+2]=at[ix+2]%vc[2]
     
  #========= make Verlet ===========================
  def make_verlet(self,r=None):
    """ Make Verlet for the model  """

    if r==None:
	r=((self.vc[0]*self.vc[1]*self.vc[2]/self.natoms)**0.33333333333)
    print "Verlet go. r=",r

    ver =Free_class()
    vc=self.vc

    ver.imax=tuple(( int(x/r)+1  for x in vc ))
    ver.dr=tuple(( x/y for x,y in zip(vc, ver.imax) ))
    
    ver.ind={}
    for iat,vec in self.at_it('x y z'):
	im=tuple( int(x/y)%ii for x,y,ii in zip(vec,ver.dr,ver.imax)  )
        ver.ind[ im ] =ver.ind.get(im,[])+[iat]

    self.verlet=ver
    print "Verlet done"    
  #==============================================================
  def make_ngbr_short(self,r=None):  
    """ makes Short Neighbours table """
    
    if r==None: r=max(self.vc)/3.
    print "Short NGBR go. r=",r 

    if not hasattr(self,'verlet'): self.make_verlet(r/2.5)
   
    ng=Free_class()
    ng.r=r

    def key_it(pt,im,mmm):
      for i in range(pt[0]+1,pt[0]+mmm+1):
        for j in range(pt[1]-mmm,pt[1]+mmm+1):
          for k in range(pt[2]-mmm,pt[2]+mmm+1):
              yield (i%im[0],j%im[1],k%im[2])
      i=pt[0]
      for j in range(pt[1]+1,pt[1]+mmm+1):
        for k in range(pt[2]-mmm,pt[2]+mmm+1):
            yield (i,j%im[1],k%im[2])
      i=pt[0]
      j=pt[1]
      for k in range(pt[2]+1,pt[2]+mmm+1):
            yield (i,j,k%im[2])
  

    ver=self.verlet
    mmm=int(r/min(ver.dr))+1
    print 'mmm = ',mmm
    ng.index=[[] for i in self.atoms]
    for key in ver.ind:
      at_list=ver.ind[key]
      for i in at_list: ng.index[i] +=at_list
      for key1 in key_it(key,ver.imax,mmm):
        try:
          at_list1=ver.ind[key1]
          for i in at_list: ng.index[i] +=at_list1
          for i in at_list1: ng.index[i] +=at_list
        except:
          pass

    self.ngbr_short=ng
    print "Short NGBR done" 

  #==============================================================
  def read_ngbr_short(self,d={}):  
    """ read Short Neighbours table """
    
    self.time=d.get('time',0)

    if self.box<>[[0],[0],[0]]:
      box=d.get('box',[[0],[0],[0]])
      self.box=box
      if len(box[0])==3:   self.vc=[box[0][0],box[1][1],box[2][2]]
      elif len(box[0])==2: self.vc=map(lambda x: x[1]-x[0], box)
      else:                self.vc=[box[0][0],box[1][0],box[2][0]]

    dat=d.get('atoms',[])
    ng=Free_class()
    ind=[]
    for i in dat:
      s=[int(j) for j in i]
      while len(ind)<s[0]:
        ind.append([])
      ind[s[0]-1] += [j-1 for j in s[2:] if j<>-1]

    if self.atoms==[]: self.atoms=[[] for j in ind]
    while len(ind)<len(self.atoms):
        ind.append([])
 
    ng.index=ind
    self.ngbr_short=ng
#    print "Short NGBR is read" 


#==============================================================
  def make_ngbr(self,r=None,part=''):  
    """ makes Neighbours table with distances """
    try:
      self.make_ngbr_numpy(r,part)
      return
    except ImportError:
      print 'Numpy is not installed, falling back to standard procedure'
      
    if r==None: 
       print 'Warning !!! Make full ngbr list. It could take alot of time!!!'
       r=max(self.vc)/3.
    print "NGBR go. r=",r 

    if not hasattr(self,'ngbr_short'): self.make_ngbr_short(r)
   
    ng=Free_class()
    r2=r*r
    ng.r=r

    ix=self.legend.index('x')
    aat=[i[ix:ix+3] for i in self.atoms]
    vc=self.vc
    ngs=self.ngbr_short.index
    ng.index=[{} for i in self.atoms]
    for iat,nng in enumerate(ngs):
      vec0=aat[iat]
      for jat in nng:
        if jat<=iat: continue
        vec1=aat[jat]
        vec= [ ((x-y)+0.5*v)%v-0.5*v for x,y,v in zip(vec1,vec0,vc) ]
        dist2=sum(x*x for x in vec)
        vec +=[dist2]
        if dist2 <= r2: 
           ng.index[iat][jat]=vec
           ng.index[jat][iat]=[-vec[0],-vec[1],-vec[2],vec[3]]
    self.ngbr=ng
    print "NGBR done" 
#==============================================================
  def make_ngbr_numpy(self,r=None,part=''):  
    """ makes Neighbours table with distances """

    import n3umpy as np
    
    if r==None: 
       print 'Warning !!! Make full ngbr list. It could takes alot of time!!!'
       r=max(self.vc)/3.
    print "NGBR numpy go. r=",r 

    ng=Free_class()
    r2=r*r
    ng.r=r

    ix=self.legend.index('x')
    crd = np.array(self.atoms, order = 'F')[:,ix:ix+3].astype(np.float32)
    vc = np.array(self.vc, order = 'F').astype(np.float32)

    ng.index=[{} for i in self.atoms]

    for iat in range(crd.shape[0]):
      d = crd[iat:] - crd[iat]
      vn = d - (d/vc).round()*vc
      r2n = np.array([np.dot(x,x) for x in vn])
      idn = np.nonzero((r2n < r2) & (r2n > 0.)) 
      for inn in idn[0]:
        ng.index[iat][iat + inn] = vn[inn].tolist()
	ng.index[iat][iat + inn] += [r2n[inn],]
        ng.index[iat + inn][iat] = (-vn[inn]).tolist()
	ng.index[iat + inn][iat] += [r2n[inn],]
    print ng.index[0]
    self.ngbr=ng
    print "NGBR numpy done" 
#==============================================================
  #---------------------------------------------------------------
  def get_round_it(self,crd,r=None):
    """ returns list of atoms near to to the point 
    """
    def key_it(pt,im,mmm):
      for i in range(pt[0]-mmm,pt[0]+mmm+1):
        for j in range(pt[1]-mmm,pt[1]+mmm+1):
          for k in range(pt[2]-mmm,pt[2]+mmm+1):
            yield (i%im[0],j%im[1],k%im[2])

    if r==None: r=min(self.vc)/3. 
    if not hasattr(self,'verlet'): self.make_verlet(r+0.05)
  
    ver=self.verlet
    mmm=int(r/min(self.verlet.dr))+1
    pt=[int(x/y) for x,y in zip(crd,ver.dr)] 

    it=(ver.ind.get(k,[]) for k in key_it(pt,ver.imax,mmm))
    for val in it:
       for iat in val:
         yield iat   

  #======== NGBR  ===========================================
  def ngbr_it(self,iat,r=None,part=''):  
    
    filt={}
    filt['gt']=lambda x,y: x>y
    filt['ge']=lambda x,y: x>=y
    filt['lt']=lambda x,y: x<y
    filt['le']=lambda x,y: x<=y
    filt['ne']=lambda x,y: x<>y
    filt['']=lambda x,y: 1==1
    ff=filt[part]

    if hasattr(self,'ngbr'):
      for k,vec in self.ngbr.index[iat].iteritems():
         if ff(k,iat):
            yield k,vec
    else:
      if not hasattr(self,'ngbr_short'): self.make_ngbr_short(r)
      for k in self.ngbr_short.index[iat]:
         if ff(k,iat):
            yield k,[None,None,None,None]

  #======== Make NGBR table ===========================================
  def make_ngbr_old(self,r=1e10,part=''):  
    """ makes Neighbours table
    """
    print "NGBR go. r=",r 

    ng=Free_class()
    r2=r*r
    ng.r2=r2

    ng.index = [dict(self.ngbr_it(iat,r,part)) for iat  in xrange(len(self.atoms)) ] 

    self.ngbr=ng

    print "NGBR done" 

  #======== Make GR ===========================================
  def make_gr_it(self,r=1e10):
  
    ind=self.ngbr.index
    for i in ind:
      for j in i:
        rr=i[j][3]**0.5
        if rr<r:
           yield rr
#========================================================================
  def ep_it(self,n=1):
    from random import random
    nn=0
    dr=self.verlet.dr
    ind=self.verlet.ind
    im=self.verlet.imax

    while nn<n:
      key=tuple( int(i*random()) for i in im )
      if ind.has_key(key): continue
      yield( ((i+0.5)*j for i,j in zip(key,dr)) )
      nn +=1

#************************************************************************
if __name__=='__main__':    #run as programm
   from model_i import dump_lmp
#   from timer import timer
#   tm=timer()
   dump=dump_lmp('dump.lmp')

   mod=model_ngbr(dump())
   mod.make_verlet(2)
#   print tm
   mod.make_fast_ngbr(5)
#   print tm
   l=list(mod.make_gr_it(5))
#   print tm
