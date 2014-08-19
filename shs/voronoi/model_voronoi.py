#!/usr/bin/python 
# __*__ coding: utf8 __*__

#import string
#import copy
#import math
#import random
from model_ngbr import model_ngbr

#--- some functions --------------------------------------------------
# periodic boundary conditions
def bound(x, y):
        if x > y/2.: return x-y
        if x < -y/2. : return x+y
        return x

def bound_v(a, b, c):
        return [((x-y)+0.5*z)%z-0.5*z for x,y,z in zip(a,b,c) ]

#-------------------------------------------------------------
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

#------------------------------------------------------------
def sistema(a,b,c):
    '''solution of linear system by Krammers method '''
    d1=a[1]*b[2]-a[2]*b[1]
    d2=a[2]*b[0]-a[0]*b[2]
    d3=a[0]*b[1]-a[1]*b[0]

    dt1=-a[3]*b[0]+a[0]*b[3]
    dt2= a[3]*b[1]-a[1]*b[3]
    dt3= a[3]*b[2]-a[2]*b[3]

    det=d1*c[0]+d2*c[1]+d3*c[2]
    if (abs(det) < 1e-12): 
#       print 'det=',det
                return

    v=[]
    v.append( (c[3]*d1-c[1]*dt3+c[2]*dt2)/det /2. )
    v.append( (c[0]*dt3-c[3]*(-d2)+c[2]*dt1)/det /2. )
    v.append( (-c[0]*dt2-c[1]*dt1+c[3]*d3)/det /2.)

    return v
#--------------------------------------------------------
def sistema_del(r,a,b,c):
    
    u=[(i*i-dot_prod(ii,ii)-r[0]*r[0])/2. for i,ii in zip(r[1:],[a,b,c])] +[0]
    dr=[ ii-r[0] for ii in r[1:] ] +[0]

    x=[-a[0],-b[0],-c[0]]
    y=[-a[1],-b[1],-c[1]]
    z=[-a[2],-b[2],-c[2]]

    q=[ dot_prod(dr,vec_prod(i,j)) for i,j in [(y,z),(z,x),(x,y)] ]
    w=[ dot_prod(u,vec_prod(i,j)) for i,j in [(y,z),(z,x),(x,y)] ]

    det= dot_prod(x,vec_prod(y,z))
    det2=det*det

    E=(dot_prod(q,q)-det2)
    G=(dot_prod(q,w)-r[0]*det2)
    F=(dot_prod(w,w)-(r[0]*r[0])*det2)

    DIS=G*G-E*F
    if DIS<=0: return []
    DIS=pow(DIS,0.5)
    
    v=[]
    RAD=(-G-DIS)/E
    if RAD >0 :
        v.append( (RAD,[(x*RAD+y)/det for x,y in zip(q,w)] )  )

    RAD=(-G+DIS)/E
    if RAD >0 :
        v.append( (RAD,[(x*RAD+y)/det for x,y in zip(q,w)] )  )
    return v

#---------------------------------------------------
def fnd_del(r,a,b=None,c=None):
    if b==None:
        return [a[3]**0.5-r[0]-r[1],0,[0,0,0]]  
        if c==None:
                c=vec_prod(a,b)
        for rrr,v in sistema_del(r,a,b,c):
                v2=dot_prod(v,v)
                return [v2,rrr,v]
        return [3e20,3e10,[1e10,1e10,1e10]]

def fnd_vor(a,b=None,c=None):
    if b==None:
        return [a[3],0,[0,0,0]]
    if c==None:
        c=vec_prod(a,b)
        c.append( dot_prod(a,c))
    v=sistema(a,b,c)
    if v== None: v=[1e10,1e10,1e10]
    v2=dot_prod(v,v)
    return [v2,v2**0.5,v]

#===================================================================
class model_voronoi(model_ngbr):
# --------------------------------------------------------------------
    def __init__(self,d={}):
        model_ngbr.__init__(self,d)

#=========== Make radii =========================================
    def make_radii(self):
        print "RAD go" 

        def f_rad(v2,r):
            if r==0: return pow(v2,0.5)/2.
            return pow(v2,0.5)-r

        rad=[0 for x in self.atoms]
        sos=[-1 for x in self.atoms]

        while not all(tuple(rad)):
            for i in range(len(self.atoms)):
                if rad[i]==0: 
                    rm,jat=min( (f_rad(vec[3],rad[i]),i) for i,vec in self.ngbr_it(i))
                    sos[i]=jat
                    if rad[jat]<>0:
                        rad[i]=rm
                    elif sos[jat]==i:
                        rad[i]=rm
                        rad[jat]=rm
## check
#    sos=[0 for x in self.atoms]
#    for i in range(len(self.atoms)):
#        ng=self.ngbr.index[i]
#        for ke in ng.keys():
#            d=pow(ng[ke][3],0.5)-rad[ke]-rad[i]
#            if abs(d)<1e-7: sos[i] = 1
##            if d<0: print 'bad radii',i,ke,rad[i],rad[ke],ng[ke][3],d
#    x=reduce(lambda x,y: x*y, sos)
#    if x<>1: print 'bad x',x
#
#    print "RAD done",x
        return rad

#------------------------------------------------------------------
    def del123(self,iat):
        ir = self.legend.index('rad')
        r0=[self.atoms[iat][ir]]
        q,rrr,q1,vec0,jat = min(( fnd_del(r0+[self.atoms[i][ir]],vec)+[vec,i] for i,vec in self.ngbr_it(iat) ))
        r0+=[self.atoms[jat][ir]]
        q,rrr,q1,vec1,kat=min(( fnd_del(r0+[self.atoms[i][ir]],vec0,vec)+[vec,i] for i,vec in self.ngbr_it(iat) ))  # second
        r0+=[self.atoms[kat][ir]]
        q,rrr,vec2,mat=min(( fnd_del(r0+[self.atoms[i][ir]],vec0,vec1,vec)+[i] for i,vec in self.ngbr_it(iat) ))  # second
        return [iat,jat,kat,mat],vec2,rrr

    def vor123(self,iat):
        q,rrr,q1,vec0,jat = min(( fnd_vor(vec)+[vec,i] for i,vec in self.ngbr_it(iat) ))
        q,rrr,q1,vec1,kat=min(( fnd_vor(vec0,vec)+[vec,i] for i,vec in self.ngbr_it(iat) ))  # second
        q,rrr,vec2,mat=min(( fnd_vor(vec0,vec1,vec)+[i] for i,vec in self.ngbr_it(iat) ))  # second
        return [iat,jat,kat,mat],vec2,rrr
  
#=========================================================================
    def vor_next(self,at,vert):
    
        vc=self.vc
        ix=self.legend.index('x')
  
        crd_abs=self.atoms[at[0]][ix:ix+3]
# known vertex in relative coordinates
        point= [ ((x-y)+0.5*z)%z-0.5*z for x,y,z in zip(vert[4:7],crd_abs,vc) ]
        ng=self.ngbr.index[at[0]]
        a=ng[at[1]]
        b=ng[at[2]]
#++++
        d1=a[1]*b[2]-a[2]*b[1]
        d2=a[2]*b[0]-a[0]*b[2]
        d3=a[0]*b[1]-a[1]*b[0]

        dt1=-a[3]*b[0]+a[0]*b[3]
        dt2= a[3]*b[1]-a[1]*b[3]
        dt3= a[3]*b[2]-a[2]*b[3]
#+++++

        old=[ i for i in vert[0:4] if i not in at][0]    # old, opposit atom 
        vo=ng[old]

        min=1e9
        for ik,c in self.ngbr.index[at[0]].iteritems():
            if ik in vert[0:4]: continue

#+++++++++ 
            det=d1*c[0]+d2*c[1]+d3*c[2]
            if (abs(det) < 1e-12): 
                continue

            v=[ (c[3]*d1-c[1]*dt3+c[2]*dt2)/det /2. ]
            v.append( (c[0]*dt3-c[3]*(-d2)+c[2]*dt1)/det /2. )
            v.append( (-c[0]*dt2-c[1]*dt1+c[3]*d3)/det /2.)
#+++++++++
#        print v,vo
            if 2*dot_prod(v,vo) > vo[3]: continue    # atom opposit to old one
  
            dv=sum((x-y)*(x-y) for x,y in zip(v,point)) 
            if dv<min:
                min=dv                       # nearest to known vertex
                mat=ik
                vec=v
        rrr=dot_prod(vec,vec)**0.5
        vec_abs= [ (x+y)%z for x,y,z in zip(vec,crd_abs,vc) ]  # vertex in absolute coordinates
        return mat,vec_abs,rrr 

#===================================================================
    def del_next(self,at,vert):
  
        att=self.atoms
        vc=self.vc
  
        ix = self.legend.index('x')
        crd_abs=att[at[0]][ix:ix+3]
  
# known vertex in relative coordinates
        point= [ ((x-y)+0.5*z)%z-0.5*z for x,y,z in zip(vert[4:7],crd_abs,vc) ]
  
        ng=self.ngbr.index[at[0]]
        a=ng[at[1]]
        b=ng[at[2]]
        ng1=self.ngbr.index[at[1]].keys()
        ng2=self.ngbr.index[at[2]].keys()

        old=[ i for i in vert[0:4] if i not in at][0]    # old, opposit atom 
        vo=ng[old]

        ir = self.legend.index('rad')
        r0=[ att[at[0]][ir],att[at[1]][ir],att[at[2]][ir] ]
#  print 'as1'
        min=1e9
        mat=0
        for ik,c in self.ngbr_it(at[0]):
            if ik in vert[0:4]: continue
            if ik not in ng1: continue
            if ik not in ng2: continue

            v1=sistema_del(r0+[att[ik][ir]],a,b,c)
            if v1== None: continue
            for rrr,v in v1:
                if sum((x-y)**2 for x,y in zip(v,vo))**0.5-rrr-att[old][ir] >=0:
                    dv=sum((x-y)*(x-y) for x,y, in zip(v,point) )

                    if dv<min:
                        min=dv                       # nearest to known vertex
                        mat=ik
                        vec=v+[rrr]

        vec_abs= [ (x+y)%z for x,y,z in zip(vec,crd_abs,vc) ]  # vertex in absolute coordinates
        return mat,vec_abs,vec[3]

#======= Make Voronoi =====================================================
# construct Voronoi mesh 
    def make_voronoi(self,iat=1):
        """ constructs Voronoi mesh 
        """
#---------------------------------------------------------
        vc=self.vc
        ngbr=self.ngbr.index
        ix=self.legend.index('x')
  
        print "Voronoi mesh go"
        try:
            self.legend.index('rad')
            fnd123=self.del123
            fnd_next=self.del_next
            print 'Delone triangulation'
        except:
            fnd123=self.vor123
            fnd_next=self.vor_next
            print 'Voronoi polihedra' 
 
        at,vec2,rrr=fnd123(iat)
#        print at
        index_back=at
  
        index = [-1 for x in self.atoms]
        index[at[0]]=0
        index[at[1]]=1
        index[at[2]]=2
        index[at[3]]=3
# convert to real coordinates
        vec_abs= [ (x+y)%v for x,y,v in zip(vec2,self.atoms[iat][ix:ix+3],vc) ] 
        vertexes=[at+vec_abs+[dot_prod(vec2,vec2)]]

        self.edges = [ [0,1,2,0],[0,1,3,0],[0,2,3,0],[1,2,3,0] ]

        ne=0
        while ne <> len(self.edges):
#            print ne,len(self.edges)
            ed=self.edges[ne]
            if len(ed) < 5:
                vert=vertexes[ed[3]]

                at=[index_back[ed[x]] for x in range(3)]
                mat,cr_abs,rrr = fnd_next(at,vert) 
#atom, coord[0:3], edge as vector[0:3]

                if index[mat] == -1:          # new atom
                    index[mat]=len(index_back)
                    index_back.append(mat)

# add vertex, add edges
                nver=len(vertexes)
                vertexes += [at+[mat]+cr_abs+[rrr]]

                self.edges[ne] += [nver]  # edge -- 2 vertexes 
                self.add_edge([ed[0],ed[2],index[mat]],nver,ne)
                self.add_edge([ed[1],ed[2],index[mat]],nver,ne)
                self.add_edge([ed[0],ed[1],index[mat]],nver,ne)

            ne += 1

#check fxor n22 and n3
        for i in xrange(len(self.edges)):
            ed=self.edges[i]
            if len(ed)==5: continue
            if len(ed)==7:
                at=[index_back[x] for x in ed[0:3]]
                crd_abs=self.atoms[at[0]][ix:ix+3]
  
                ng=ngbr[at[0]]
                c=vec_prod(ng[at[1]],ng[at[2]])
  
                v = ( vertexes[x][4:7] for x in ed[3:7] )
                v1= ( dot_prod(c,bound_v(x,crd_abs,vc)) for x in v )
                s=sorted([(j,i) for i,j in enumerate(v1)])
  
                ed1=ed[0:3]+[ ed[3+s[0][1]],ed[3+s[1][1]] ]
                ed2=ed[0:3]+[ ed[3+s[2][1]],ed[3+s[3][1]] ]
                self.edges[i]=ed1
                self.edges.insert(i,ed2)
                ne +=1
                continue
            print 'bad delone!!!!'
  
        self.index=index
        self.index_back=index_back
        self.vertexes=vertexes
  
        print 'Voronoi done',ne
        return
  
#<<<<<<<<<<<<<< construction is done, find parameters >>>>>>>>>>>>>>>>>>
# calculate V, S distribution
    def get_voronoi_param(self):
        index=self.index
        index_back=self.index_back
        ix = self.legend.index('x')

        sq=[0. for x in self.atoms]
        vol=[0. for x in self.atoms]
        pl_mv=[{} for x in self.atoms]

        for ed in self.edges:

#      if len(ed) <> 5:  print ed,'bad!!!' 
# make plates for each MV
            at=[ index_back[x] for x in ed[0:3]]
            crd_abs=self.atoms[at[0]][ix:ix+3]

            w= [bound(x-y,z) for x,y,z in zip(self.vertexes[ed[3]][4:7],crd_abs,self.vc) ]
            w1= [bound(x-y,z) for x,y,z in zip(self.vertexes[ed[4]][4:7],crd_abs,self.vc) ]
  
            nv=[x-y for x,y in zip(w1,w)] #ed[5:9]
            nv+=[dot_prod(nv,nv)]
  
            ng=self.ngbr.index[at[0]]
            a=ng[at[1]]       # to 1-st ngbr
            b=ng[at[2]]       # to 2-nd ngbr
            ab=vec_prod(a,b)
  
#       print ab,w,nv
            alf = - dot_prod(ab,w) / dot_prod(ab,nv)
#  center of triangle - alf*nv+w
# r2 - square of radius of external circle
            r2=alf*alf*nv[3]+dot_prod(w,w)+2*alf*dot_prod(nv,w)
# squares of length
            l=[a[3]/4.,b[3]/4.,(a[3] + b[3]-2*dot_prod(a,b))/4.]
# perpendiculars from sides of triangle to the center of circle
            try:
                h=[pow(abs(r2-x),0.5) for x in l]
            except (ValueError,):
                print r2,l
                raise
        # if angle >90, should substract the value
            if l[0]>l[1]+l[2]: h[0] *= -1
            if l[1]>l[0]+l[2]: h[1] *= -1
            if l[2]>l[0]+l[1]: h[2] *= -1
  
#   print 'h',h
  
        # squares of plates
            s= [x*pow(nv[3],0.5)/2. for x in h]
        # volumes
            v= [x*pow(y,0.5)/3. for x,y in zip(s,l)]
  
  
            pl_mv[at[0]][at[1]] = pl_mv[at[0]].get(at[1],[0,0.,0.])
            pl_mv[at[0]][at[2]] = pl_mv[at[0]].get(at[2],[0,0.,0.])
            pl_mv[at[1]][at[2]] = pl_mv[at[1]].get(at[2],[0,0.,0.])
  
            pl_mv[at[0]][at[1]][0] +=1
            pl_mv[at[0]][at[2]][0] +=1
            pl_mv[at[1]][at[2]][0] +=1

            pl_mv[at[0]][at[1]][1] += s[0]
            pl_mv[at[0]][at[2]][1] += s[1]
            pl_mv[at[1]][at[2]][1] += s[2]

            pl_mv[at[0]][at[1]][2] += v[0]
            pl_mv[at[0]][at[2]][2] += v[1]
            pl_mv[at[1]][at[2]][2] += v[2]
  
            pl_mv[at[1]][at[0]] = pl_mv[at[0]][at[1]] 
            pl_mv[at[2]][at[0]] = pl_mv[at[0]][at[2]] 
            pl_mv[at[2]][at[1]] = pl_mv[at[1]][at[2]] 

            sq[at[0]] += s[0]+s[1]
            sq[at[1]] += s[0]+s[2]
            sq[at[2]] += s[1]+s[2]
  
            vol[at[0]] += v[0]+v[1]
            vol[at[1]] += v[0]+v[2]
            vol[at[2]] += v[1]+v[2]
  
        for i in range(len(pl_mv)):
            for j in pl_mv[i]:
                pl_mv[i][j].append(pow(self.ngbr.index[i][j][3], 0.5))

        k_sph = [36.*3.1416*x*x/(y*y*y) for x,y in zip(vol,sq)]
  
        print "Voronoi done"
        return sq,vol,k_sph,pl_mv 
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# calculate T, O, S, N parameters
    def get_delone_param(self):
        index=self.index
        index_back=self.index_back
        vert=self.vertexes

        tet=[]
        oct=[]
        sov=[]
        n_par=[0 for x in vert]
        n_test=[0 for x in vert]

        for ver in self.vert:
            l=[aat[ver[i]][ver[j]][3]**0.5 for i,j in [(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)] ]
            l0=sum(l)/6
            t =  sum((x-y)**2 for x,y in zip(l,l))/15./l0/l0  
            l.sort()
            o =  sum((x-l[6]/pow(2,0.5))**2 for x in l[0:6])/5/l0/l0 
            o1 = sum((l[i]-l[5])**2 for i in l[0:5]) 
            o1 += sum((l[i]-l[4])**2 for i in l[0:4]) 
            o1 += sum((l[i]-l[3])**2 for i in l[0:3]) 
            o1 += sum((l[i]-l[2])**2 for i in l[0:2]) 
            o1 += (l[0]-l[1])**2 
            o = o1/10/l0/l0 +o
            tet +=[t]
            oct +=[o]
            sov += [min(t/0.018,o/0.030)]

        for ed in self.edges:
            v1=ed[3]
            v2=ed[4]
            v=map(to_center, vert[v1][4:7],vert[v2][4:7],self.vc)
            r=pow(dot_prod(v,v),0.5)-vert[v1][7]-vert[v2][7]
            n_test[v1] +=1
            n_test[v2] +=1
            if r <0:
                n_par[v1] +=1
                n_par[v2] +=1

        print "Delone parameter done"
        return n_par,n_test,tet,oct,sov

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


#<<<<<<<<<<<<<<  >>>>>>>>>>>>>>>>>>
    def get_voronoi_ngbr(self):
        index=self.index
        index_back=self.index_back
        ix = self.legend.index('x')

        pl_mv=[[] for x in self.atoms]
        for ed in self.edges:
            at=[ index_back[x] for x in ed[0:3]]
            if pl_mv[at[0]].count(at[1])==0:
                pl_mv[at[0]].append(at[1])
                pl_mv[at[1]].append(at[0])
            if pl_mv[at[0]].count(at[2])==0:
                pl_mv[at[0]].append(at[2])
                pl_mv[at[2]].append(at[0])
            if pl_mv[at[1]].count(at[2])==0:
                pl_mv[at[1]].append(at[2])
                pl_mv[at[2]].append(at[1])

        return pl_mv 
#<<<<<<<<<<<<<<  >>>>>>>>>>>>>>>>>>
    def get_voronoi_ngbr1(self,iat=1):
        index=self.index
        index_back=self.index_back
        ix = self.legend.index('x')

        jat=self.index[iat]
#        print jat,iat
        ind0=[]
        ed0=[]
        for ed in self.edges:
            if not jat in ed[0:3]: continue
            v1=ed[3]
            v2=ed[4]
            if not v1 in ind0: ind0.append(v1)
            n1=ind0.index(v1)
            if not v2 in ind0: ind0.append(v2)
            n2=ind0.index(v2)
            ed0.append([n1,n2])
        vec0=zip(*[self.vertexes[i][4:7] for i in ind0])

        ind1=[iat]
        ed1=[]
        for ed in self.edges:
            if not jat in ed[0:3]: continue
            a=[index_back[i] for i in ed[0:3]]
            for i in a:
                if not i in ind1: ind1.append(i)

            nn=sorted(ind1.index(i) for i in a)
#            print nn
            if not [nn[0],nn[1]] in ed1:
                ed1.append([nn[0],nn[1]])
            if not [nn[0],nn[2]] in ed1:
                ed1.append([nn[0],nn[2]])
            if not [nn[1],nn[2]] in ed1:
                ed1.append([nn[1],nn[2]])

        vec1=zip(*[self.atoms[i][ix:ix+3] for i in ind1])

        return ind0,ed0,vec0 
  
# --------------------------------------------------------------------
# Fast insert, ne elements have sorted
    def add_edge(self,ed,ver,ne):
#----------------------
        def bigger(a,b):
            if a[0] <> b[0]:
                return a[0] - b[0]
            if a[1] <> b[1]:
                return a[1] - b[1]
            if a[2] <> b[2]:
                return a[2] - b[2]
            return 0
      #---------------------
        ed.sort()
        nmin=ne                      # already  sorted, don't touch
        nmax=len(self.edges)-1
     
        if bigger(self.edges[nmax],ed) <0 :     # insert at left side
            self.edges.insert(nmax+1,ed+[ver])
            return 

        while nmax-nmin > 1:                    # bisection method
            ind=(nmax+nmin)/2
            b=bigger(self.edges[ind],ed)
            if b ==0:
                self.edges[ind].append(ver)       # known edge, add 2-nd vertex
                return
            if b > 0:
                nmax=ind
            else:
                nmin=ind
     
        if bigger(self.edges[nmax],ed) ==0 :    # known edge, add 2-nd vertex
            self.edges[nmax].append(ver)
            return 
  
        if bigger(self.edges[nmin],ed) ==0 :    # known edge, add 2-nd vertex
            self.edges[nmin].append(ver)
            return 
      
   # insert in nmin+1
        self.edges.insert(nmax,ed+[ver])        # add new edge

#************************************************************************
if __name__=='__main__':    #run as programm
    from model_io import mod_lammps_dump

    print 'go'
    mod=model_voronoi(mod_lammps_dump('dump.lmp'))
    mod.make_verlet(5)
    mod.make_ngbr(5,'ne')
#   rad=mod.make_radii()
#   mod.add_prop(rad,leg_st='rad',for_st='f')
    mod.make_voronoi()
    mod.get_voronoi_param()
