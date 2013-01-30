#!/usr/bin/python 
# __*__ coding: utf8 __*__
#!/usr/bin/python 
#==============================================================================

def bound_v(a, b, c):
        return [((x-y)+0.5*z)%z-0.5*z for x,y,z in zip(a,b,c) ]
#----------------------------------------------------------------
# vector product of two vectors
def vec_prod(a,b):
    v=[]
    v.append(a[1]*b[2]-a[2]*b[1])
    v.append(a[2]*b[0]-a[0]*b[2])
    v.append(a[0]*b[1]-a[1]*b[0])
    return v
#------------------------------------------------------------
# dot product of two vectors (3)
def dot_prod(a,b):
    return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]
##########################################################################
from model_ngbr import model_ngbr

#=========== MODEL CLUSTER =========================================

class model_cluster(model_ngbr):
  # --------------------------------------------------------------------
  def __init__(self,d={}):
    model_ngbr.__init__(self,d)	

#-----------------------------------------------
  def make_cluster(self,r=100):  ## old function!!!!!
#    print 'cluster go'

    r2=r*r
    if r2 > self.ngbr.r2:
      print 'Warning!!! Cut radius to ngbr radius'
      r2=self.ngbr.r2

    data =[]
    ind=self.ngbr.index
    for i in range(len(self.atoms)):
       if ind[i]=={}:
          data.append(set())
          continue
       data.append(set([j for j in ind[i] if ind[i][j][3] <r2]))

    i=0
    for dat in data:
      i +=1
      if dat==[]: continue
      s=dat.copy()
      id1=id(dat)
      for j in s:
        if id(data[j])<>id1:
          dat.update(data[j])
          data[j]=dat

    s=set()
    clust=[]
    for dat in data:
      idd=id(dat)
      if idd in s: continue
      s.add(idd)
      clust.append(list(dat) )

    self.clust=clust
    return data

#-----------------------------------------------
  def make_cluster_fast_fast(self,ind_cl='c_clu'):
    print 'cluster go'
    atoms=self.atoms
    clust = self.legend.index(ind_cl)
    cl=[[] for i in atoms]+[[]]
    for i in range(len(atoms)):
       color=int(atoms[i][clust])
       cl[color].append(i)

    nkl=[len(cl[int(i[clust])])  for i in atoms]
    self.clust=[]
    for i in cl:
      if len(i)>1: self.clust.append(i)
    return nkl

#-----------------------------------------------
  def make_cluster_fast(self):
    print 'cluster go'

    atoms=self.atoms

    max_color=0
    color=[-1 for i in atoms]
    clust=[]
    for i in range(len(atoms)):
       at=atoms[i]
       if color[i]==-1: 
          c=max_color
          color[i] = c
          max_color +=1
          clust.append([i])
       else:
          c=color[i]

       for ng,vvv in self.ngbr_it(i,2.7): 
         b=color[ng]
         if b==-1:
           clust[c].append(ng)
           color[ng]=c
         else:
           if b<c:
             for ii in clust[c]:
               color[ii]=b
             clust[b] +=clust[c]
             clust[c]=[]
           if c<b:
             for ii in clust[b]:
               color[ii]=c
             clust[c] +=clust[b]
             clust[b]=[]
  
    nkl=[len(clust[color[i]])  for i in range(len(atoms))]
    self.clust=[]
    for i in clust:
      if len(i)>1: self.clust.append(i)
    return nkl
  #==============================================================

  #====================================================
  # sort cluster in order of decreasing size
  def sort_cluster(self):
    
    print 'sort cluster'
    clust=self.clust 
    ss=sorted(((len(i),i)  for i in clust))
    self.clust=[i[1] for i in ss]
    return

  #=========== cluster velocity =========================================
  # Calculate cluster velocity 
  def cluster_info(self,ncl=0):
    ix = self.legend.index('x')
    iv = self.legend.index('vx')
    atoms=self.atoms
    vc=self.vc

    icl=self.clust[ncl]
    ll=len(icl)
    v0=atoms[icl[0]][ix:ix+3]

    crd_summ=[0,0,0]
    vel_summ=[0,0,0]
    for iat in icl:
        at=atoms[iat]
        v1 = bound_v(at[ix:ix+3],v0,vc)
        crd_summ= [i+j for i,j in zip(crd_summ,v1)]
        vel_summ=[i+j for i,j in zip(vel_summ,at[iv:iv+3])]

    c_mass=[(x/ll+y)%z for x,y,z in zip(crd_summ,v0,vc)]
    v_mass=[x/ll for x in vel_summ]
    e_forward=sum(x*x for x in v_mass)*ll/2.

    l_summ=[0,0,0]
    for iat in icl:
        at=atoms[iat]
        r = bound_v(at[ix:ix+3],c_mass,vc)
        vel=[i-j for i,j in zip(at[iv:iv+3],v_mass)] 
        l_summ=[i+j for i,j in zip(l_summ,vec_prod(r,vel))]
    l2=sum(i*i for i in l_summ)

    j_cl=0.
    for iat in icl:
        at=atoms[iat]
        r = bound_v(at[ix:ix+3],c_mass,vc)
        r2_par=dot_prod(l_summ,r)**2/l2
        r2 = sum(i*i for i in r)
        j_cl += r2 - r2_par
    w_mass=[x/j_cl for x in l_summ]
    e_rot1=l2/2./j_cl

    s=0.
    e=0.
    ee=0.
    for iat in icl:
        at=atoms[iat]
        r = bound_v(at[ix:ix+3],c_mass,vc)
        v_rot=vec_prod(w_mass,r)
        e+=sum(i*i for i in v_rot)
        v_intr=[i-j-k for i,j,k in zip(at[iv:iv+3],v_mass,v_rot)] 
        s+=sum(i*i for i in v_intr)
        ee+=sum(i*i for i in at[iv:iv+3])

    e_rot=e/2.
    e_at=s/2./ll
    e_tot=ee/ll/2.

    return c_mass, v_mass, w_mass, e_forward, e_rot, e_at, e_tot

#==================================================================
if __name__=='__main__':    #run as programm
      from dump import dump_lmp

      mod=model_cluster(dump_lmp('e:/temp/long/dump/44400000.lmp')())
      mod.make_ngbr(2.7)
      mod.make_cluster_fast()
 
      col=[]
      _tp=mod.legend.index('type')
      for iat in mod.atoms:
        c=1
        if iat[_tp]=='2': c=0
        col.append(c)

      for n,cl in enumerate(mod.clust):
        for j in cl: col[j]=2
        a, b, c, e1, e2, e3, e22 = mod.cluster_info(n)

      mod.add_prop(col,'color','i')


      a, b, c, e1, e2, e3, e22 = mod.cluster_info()
      print 'e rotation',e2, e22,e1,e3