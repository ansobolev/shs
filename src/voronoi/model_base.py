#!/usr/bin/python 
# __*__ coding: utf8 __*__

oneline = "Read, write and operate with models"

import os
from copy import deepcopy
#---------------------------------------------------------------
#def format_data(dl,format='i s f f f f f f'.split()):
#    def intt(x): return int(float(x))
#    d={'i': intt,'f': float,'s': str}
#    for li in dl:
#       ll=[i for i in li.split() if i not in '(){}[]']
#       yield [d[j](i) for i,j in zip(ll,format)] 
 
#--------------------------------------------------------------
def write_pdb_it(at_iter):
   s= 'ATOM  %5i  IS %c     %4i    %8.3f%8.3f%8.3f%6.2f%6.2f \n'
   j=33
   for iat,(id,type,x,y,z,col) in at_iter:
     j += 1
     if j==240: j=33
#     print id,type,x,y,z,col
     yield s%(id,chr(j),int(type),x,y,z,0.0,float(col))
#=============================================================================
class model_base:
  # --------------------------------------------------------------------
  def __init__(self,d={}):
     self.time=d.get('time',0)

     box=d.get('box',[[0],[0],[0]])
     self.box=box
     if len(box[0])==3:   self.vc=[box[0][0],box[1][1],box[2][2]]
     elif len(box[0])==2: self.vc=map(lambda x: x[1]-x[0], box)
     else:                self.vc=[box[0][0],box[1][0],box[2][0]]

     leg_list=d.get('legend',[])
     ft_list=d.get('format',[])
     atoms=d.get('atoms',[])

     if not 'id' in leg_list:       # add 'id' colum
        for i in range(len(atoms)):
           atoms[i] +=[i+1]
        leg_list +=['id']
        ft_list +=['i']
   
     if not 'itype' in leg_list:    # add 'itype' colum
       if 'type' in leg_list:
         tp={}
         it=leg_list.index('type')
         tt=sorted(list(set((at[it] for at in atoms)))) 
         for at in atoms: 
           at += [ tt.index(at[it])+1]
       else:   
         for at in atoms:
           at +=[1]

       leg_list +=['itype']
       ft_list +=['i']

     self.atoms=atoms
     self.legend=leg_list
     self.format=ft_list
     
#====================================================================
  def at_get(self,n,leg_st=''):
    if leg_st=='':
      return tuple(self.atoms[n])                  # all properties
    else:
      a=[self.legend.index(i) for i in leg_st.split()]
      if len(a)<>1: 
        return tuple(self.atoms[n][j] for j in a)  # several properties
      else:
        return self.atoms[n][a[0]]                 # one property
  #-------------------------------------------------------------------
  def at_it(self,leg_st='',atoms=None):
    s_at=self.atoms

    if atoms==None:
      atoms=xrange(len(self.atoms))
#    else:
#      atoms=tuple(list)       

    if leg_st=='':
      for n in atoms: 
        yield n,tuple(s_at[n])                  # all properties
    else:
      a=[self.legend.index(i) for i in leg_st.split()]
      if len(a)<>1: 
        for n in atoms:
          s_at_n=s_at[n]
          yield n,tuple(s_at_n[j] for j in a)  # several properties
      else:
        for n in atoms:
          yield n,s_at[n][a[0]]                 # one property
  
  #-------------------------------------------------------------------
  def at_format_it(self,leg_st='x y z',format='',atoms=None):
     for iat,i in self.at_it(leg_st,atoms):
        if format<>'':
          yield format%i
        else:
          yield ' '.join( (str(j) for j in tuple(i) ))
  #-------------------------------------------------------------------
  def at_func_it(self,func_st='0',cf={},atoms=None):
     func_list=func_st.split()
     for iat,prop in self.at_it(atoms=atoms):
        d=dict( zip(self.legend, prop))
        if len(func_list)==1:
           yield iat,eval(func_st, d,cf)
        else: 
           yield iat,tuple([eval(func, d,cf) for func in func_list])

#======================================================================
  def add_at(self,a):
     d={'i': int,'f': float,'s': str}
     at=[d[ft](a.get(leg,'0')) for leg,ft in zip(self.legend,self.format)]
     id =self.legend.index('id')
     if at[id]<=0: at[id]=len(self.atoms)+1
     self.atoms +=[at]

  #--------------------------------------------------------------------
  def del_at(self,cond_st=''):
     at=list(( iat for iat,f in self.at_func_it(cond_st) if all(f) ))
     at.sort().reverse()
     for iat in at: del self.atoms[iat]
  #--------------------------------------------------------------------
  def replace_at(self,cond_st='',**a):
     d={'i': int,'f': float,'s': str}
     at=[d[ft](a.get(leg,'0')) for leg,ft in zip(self.legend,self.format)]
     b=( iat for iat,f in self.at_func_it(cond_st) if all(f) )
     for iat in b:
       self.atoms[iat]= at

#=======================================================================
  def add_prop(self,prop=[],leg_st='',for_st=''):
    
    self.format +=for_st.split()
    self.legend +=leg_st.split()

    for j,p in zip(self.atoms,prop):
      j += [p]

  #------------------------------------------------------------------
  def del_prop(self,col_st=''):
    
    s=[self.legend.index(i) for i in col_st.split()].sort().revers()

    for j in self.atoms:
      for i in s:
        del j[i]
    
    for i in s:
      del self.legend[i]
      del self.ft[i]

  #-------------------------------------------------------------------
  def replace_prop(self,col_st='',func_st='',**cf):
  
    print col_st,func_st,cf
    it=((self.atoms[iat],f) for iat,f in  self.at_func_it(func_st,cf))
    s=[self.legend.index(i) for i in col_st.split()]

    for at,f in it:
       for i,ff in zip(s,f):
         at[i]=ff

#======================================================================
  def copy(self):
     from copy import deepcopy
     d={'time':self.time}
     d['box']=deepcopy(self.box)
     d['atoms']=deepcopy(self.atoms)
     d['legend']=self.legend
     d['format']=self.format
     return model_io(d)
  #--------------------------------------------------------------
  def sort_by(self,col='id'):
     iii=self.legend.index(col)
     sr=sorted( (iat[iii],i) for i,iat in enumerate(self.atoms) )
     self.atoms=[self.atoms[i[1]] for i in sr]
  #------------------------------------------------------------------------
  def scale_crd(self, cf=1.):
     ix=self.legend.index('x')
     for i in self.atoms:
       i[ix:ix+3]=[x*cf for x in i[ix:ix+3]]
  #------------------------------------------------------------------------
  def scale(self, cf=1.):
     ix=self.legend.index('x')
     for i in self.atoms:
       i[ix:ix+3]=[x*cf for x in i[ix:ix+3]]
     self.vc=[x*cf for x in self.vc]
  #------------------------------------------------------------------------
  def to_box_crd(self):
     ix=self.legend.index('x')
     vc=self.vc
     for i in self.atoms:
       i[ix:ix+3]=[x%y for x,y in zip(i[ix:ix+3],vc)]
 #------------------------------------------------------------------------
  def shift_to_center(self, point=[0,0,0]):
     ix=self.legend.index('x')
     vc=self.vc
     for i in self.atoms:
       i[ix:ix+3]=[((x-y)+0.5*z)%z for x,y,z in zip(i[ix:ix+3],point,vc)]

#=================== Write different formats =================================
  def write_property(self,file,prop_st,atoms=None):

    f = open(file,"w")
    for i in self.at_format_it(prop_st,atoms=None):
       f.write(i+'\n')
    f.close()
  #----------------------------------------------------------
  def write_pdb(self,file,color='itype',atoms=None):

      f=open(file,"w")
      f.write('REMARK  atoms as in \n')
      f.write('REMARK \n')
      f.write('REMARK< i5><  > X     <  >    <x f8.3><y f8.3><z f8.3><f6.2><f6.2> \n')

      iter = self.at_it('id itype x y z '+color,atoms)

      for i in write_pdb_it(iter):
	f.write(i)
      f.close()
#----------------------------------------------------------
  # write list in Raster3D format
  # x[] - numbers of atoms
  def write_r3d_rot(self,file,phy=0,atoms=[],color='itype',zoom=1.0,scale=10):
      from math import sin,cos,pi
      if atoms==[]: atoms=range(len(self.atoms))

      f=open(file,"w")
      f.write('balls - Raster3D V2.6c \n')
      f.write('80  80    tiles in x,y \n')
      f.write('8   8     pixels (x,y) per tile \n')
      f.write('4         anti-aliasing 3x3 -> 2x2 pixels \n')
      f.write('0 0 0     black background \n')
      f.write('F         yes, I LIKE shadows! \n')
      f.write('25        Phong power \n')
      f.write('0.15      secondary light contribution \n')
      f.write('0.05      ambient light contribution \n')
      f.write('0.25      specular reflection component \n')
      f.write('0       eye position \n')
      f.write('1 1 1     main light source position \n')
      phy=pi*phy/180
      f.write('%f 0 %f 0   input co-ordinate+radius transformation \n'%(cos(phy),sin(phy)))
      f.write('0 1 0 0 \n' )
      f.write('%f 0 %f 0 \n' %(-sin(phy),cos(phy)))
      a=self.vc[0]
      f.write('0 0 0 %f \n'%(a*1.15*zoom))
      f.write('3         mixed object types \n')
      f.write('* \n')
      f.write('* \n')
      f.write('* \n')

      s= '2\n  %8.3f %8.3f %8.3f %6.2f %6.2f %6.2f %6.2f \n'

      vc=self.vc
      for iat,(col,x,y,z) in self.at_it(color+' x y z',atoms):
	if col==0: f.write(s%(x-vc[0]/2,y-vc[1]/2,z-vc[2]/2,2,0,0,1))
	if col==1: f.write(s%(x-vc[0]/2,y-vc[1]/2,z-vc[2]/2,2,1,1,0))
	if col==2: f.write(s%(x-vc[0]/2,y-vc[1]/2,z-vc[2]/2,3,0,1,0))

      s1='3\n  %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f %6.2f %6.2f %6.2f \n'	
      f.write(s1%(-280,280,vc[2]/2,2,scale-280,+280,vc[2]/2,1,1,0,0))


      f.close()


  # --------------------------------------------------------------------
  # write a single dump file from current selection

  def write_lammps_crd(self,file,atoms=None):
    
    a=len(self.atoms)
    if atoms: a=len(atoms)

    f = open(file,"w")
    f.write( 'LAMMPS Description. time=%i \n \n' %self.time )
    f.write( '%11i  atoms \n' %a)
    f.write( '%11i  atom types \n \n' % max(( t for iat,t in self.at_it('itype') )))
    f.write( '%15.5f %15.5f xlo xhi \n' %(0, self.vc[0]) )
    f.write( '%15.5f %15.5f ylo yhi \n' %(0, self.vc[1]) )
    f.write( '%15.5f %15.5f zlo zhi \n \n' %(0, self.vc[2]) )

    f.write('Atoms \n \n')
    for i in self.at_format_it('id itype x y z','%6i %5i %15.5f %15.5f %15.5f \n',atoms):
        f.write(i)

    f.write('\n Velocities \n \n')
    for i in self.at_format_it('id vx vy vz','%6i %15.5f %15.5f %15.5f \n',atoms):
        f.write(i)
    f.close()
  # --------------------------------------------------------------------
  # write a single dump file from current selection
  def write_lammps_dump(self,file,atoms=None,leg_st=''):

    a=len(self.atoms)
    if atoms: a=len(atoms)

    data= 'ITEM: TIMESTEP \n %10i \n' %self.time 
    data+='ITEM: NUMBER OF ATOMS \n %11i \n' %a
    data+='ITEM: BOX BOUNDS \n 0. %f \n 0. %f \n 0. %f \n'\
                    %(self.vc[0],self.vc[1],self.vc[2])
    data+='ITEM: ATOMS %s \n' %leg_st
    
    f = open(file,"w")
    f.write(data)
    for i in self.at_format_iter(leg_st,atoms):
      f.write( i+'\n' )
    f.close()
#======================================================================

if __name__=='__main__':    #run as programm
   from model_input import dump_lmp 
   print 'go'
   dump=dump_lmp('dump.lmp')
#   dump.set_time(43000)
   for ddd in dump.iter():
      print 'time ',ddd['time']
      mod=model_base(ddd)
      mod.write_pdb('1.pdb')
      mod.write_lammps_crd('1.crd')
