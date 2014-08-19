#!/usr/bin/python 
# __*__ coding: cp1251 __*__
#----------------------------------------------------------------
def cut_string_it(str):
  dat=''
  dd=[]
  for i in str:
    if i==',' and dat<>'':
      dd.append(int(dat))
      dat=''
    elif i==']' and dd<>[]: 
      dd.append(int(dat))
      yield dd
      dd=[]
      dat=''
    elif i<>'[':
      dat +=i

#====================================================================
def atom_it(el,Nst):    #separate long list for portions
  li=[]
  k=0
  for i in el:

     time=i[0]
     ost=i[1:]

     if k+time<Nst:
        li +=[i]
        k +=time
        continue


     while k+time>=Nst:
        t1=Nst-k
        li += [ [t1]+ost ]
        yield li
        time = time-t1
        k=0
        li = []

     li = [ [time]+ost ]
     k=time

# --- get statistics from data shit-------  
def atom_stat_it(list,Nst):
  stab_time={}
  stab_n={}
  mstab_time={}
  mstab_n={}
  strike_n={}

  for list_part in atom_it(list,Nst):
#     print list_part
     for j in list_part:
       if len(j)==5: 
         key=j[3]
         if j[2]==1: # --- strike
           strike_n[key] = strike_n.get(key,0)+1
         else:  # --- metastable 
           mstab_time[key] = mstab_time.get(key,0)+j[0] 
           mstab_n[key] = mstab_n.get(key,0)+1
          
       else:        #--- stable
         key=j[1]
         stab_time[key]= stab_time.get(key,0) + j[0] 
         stab_n[key]= stab_n.get(key,0) + 1

     yield stab_time,stab_n,mstab_time,mstab_n,strike_n

#----------------------------------------------

class history:
   def __init__(self,file=None):
      self.number_ticks=0
      self.dt=0.
      self.time_last=0
      self.time_begin=-1
      self.dat=[]
      self.tau_compress=100
      self.rewrite=1
      self.tp=[]

      if file<>None:
         self.read_history(file)
      return
  
   #---- read history_txt ---------------------------
   def read_history(self,file):
     print 'read history from ',file
     
     def f_it(file):
       for i in open(file,'rb'):
         yield(i)
       try:
         for i in open('tail.his','rb'):
           yield(i)
       except:
         pass  
         
     f=f_it(file)
     m=-1
     a=[]
     for st in f:
       if st[0]=='#': 
          a0,a1,a2,a3=tuple([int(j) for j in st.replace('#','').split()[0:4]])
          self.time_begin=a0
          self.time_last=max(self.time_last,a1)
          self.number_ticks=max(self.number_ticks,a2)
          if self.dt<>a3 and self.dt>0:
             print 'Warning!!! wrong dt!!!'
          self.dt=a3
          continue
       m+=1
       try:
         q=st.split(':')
         i=q[1]
         nn,tp=(int(i) for i in q[0].split())
       except:
         nn=m
         i=st
         tp=0
       
       if nn>len(a)-1:
         a +=['' for s in range(nn-len(a)+1)]
         self.tp +=[0 for s in range(nn-len(self.tp)+1)]
         
       a[nn] += i.strip().replace('\n','').replace('[[','[').replace(']]',']').replace('],',']') 
       self.tp[nn]=tp
       
     self.number_ticks=sum([eval(j+']')[0] for j in a[0].split(']') if j<>''])
     print self.time_begin,self.time_last,self.number_ticks,self.dt,'@@@!'
     
     self.dat=[[i] for i in a]
     return 
   #---------------------------------------------------
   def unpack(self,tail=None):
     print 'unpack -',tail
     if tail==0:return
     for n,b in enumerate(self.dat):
       if type(b[0]) == type('a'):
         if tail==None:
           k=[j+']' for j in b[0].rsplit(']') if j<>'']
           self.dat[n]=[eval(i) for i in k]+b[1:]
         else:
           k=[j+']' for j in b[0].rsplit(']',tail+1) if j<>'']
           k[-tail:]=[eval(i) for i in k[-tail:]]
           self.dat[n]=k+b[1:]
     return 
   #---------------------------------------------------
   def pack(self,tail=0):
     print 'pack -',tail
     for n,b in enumerate(self.dat):
       if tail==0: tail=-len(b)
       if len(b)>tail:
         self.dat[n]=[''.join(str(j).replace(' ','') for j in b[:-tail] if j<>[])]+b[-tail:]
     return
   
   #---- write history_txt ---------------------------
   def write(self,file,tail=0):
     
     if self.rewrite==1:
        f=open(file,'wb')
     else:
        f=open(file,'ab')
     self.rewrite=0      

     print 'write part ',tail, ' to file ',file
     f.write('# %i %i %i %i \n'%(self.time_begin,self.time_last,self.number_ticks,self.dt))
      
     self.pack(tail)

     for n,i in enumerate(self.dat):
       if type(i[0])==type('str'):
         f.write('%i %i: '%(n,self.tp[n]))
         j=i.pop(0)
         f.write(j+'\n')
     f.close()

     f=open('tail.his','wb')
     if tail<>0:
        f.write('# %i %i %i %i \n'%(self.time_begin,self.time_last,self.number_ticks,self.dt))
        for n,i in enumerate(self.dat):
           st=''.join(str(j).replace(' ','') for j in i)
           f.write('%i %i: %s\n'%(n,self.tp[n],st))
     f.close()

     return
   
   #----------------------------------------------
   def update_compress(self,time,cl=[]):

      if time<=self.time_last:
        print 'Old time'
        return

      dt=time-self.time_last
      if dt<>self.dt:
          print 'error: wrong dt'
          self.dt=dt
      if self.time_begin==-1:  self.time_begin=time

      self.time_last=time

      tau=self.tau_compress

      mm=len(cl)-len(self.dat)
      if mm>0:
        self.dat += [[[self.number_ticks,1]]  for i in range(mm)]
      elif mm<0:
        cl+=[1 for i in range(-mm)]
      print self.time_begin,self.time_last,self.number_ticks,self.dt,'##'
            
      clust=self.dat
      for i,el in enumerate(clust):    
        s=el[-1]

        if s[1]==cl[i]:
          s[0] +=1
        else:
          if s[0]==0:
            el.pop(-1)
          elif s[0]<tau:  
            s +=[1,s[1],s[1]]
            try:                 #compress
              el[-2][0] += s[0]
              el[-2][1] += s[1]
              el[-2][2] += 1
              el[-2][3] = max(el[-2][3],s[1])
              el[-2][4] = min(el[-2][4],s[1])
              el.pop(-1)
            except:
              pass
          clust[i].append([1,cl[i]])     # [time,size]
      self.number_ticks +=1
   #----------------------------------------------
   def update(self,time,cl=[],tp=[]):

      if time<=self.time_last:
        print 'Old time'
        return

      dt=time-self.time_last
      if dt<>self.dt:
          print 'error: wrong dt'
          self.dt=dt
      if self.time_begin==-1:  self.time_begin=time

      self.time_last=time

      mm=len(cl)-len(self.dat)
      if mm>0:
        self.dat += [[[self.number_ticks,1]]  for i in range(mm)]
        self.tp += [0  for i in range(mm)]
      elif mm<0:
        cl+=[1 for i in range(-mm)]
        tp+=[0 for i in range(-mm)]
        
#      print self.time_begin,self.time_last,self.number_ticks,self.dt,'##'
            
      clust=self.dat
      for i,el in enumerate(clust):
        if tp[i]<>0: self.tp[i]=tp[i]  
        s=el[-1]

        if s[1]==cl[i]:
          s[0] +=1
        else:
          if s[0]==0: el.pop(-1)
          clust[i].append([1,cl[i]])     # [time,size]
      self.number_ticks +=1
   
   #----------------------------------------------
   def update_all(self,file,nat=0):
     from dump import dump_lmp
     from model_cluster import model_cluster

     dum=dump_lmp(file)
     dum.set_time([self.time_last+1,])
     for i in dum.iter:
       mod=model_cluster()
       mod.read_ngbr_short(i)
       nk=mod.make_cluster_fast()
       self.update(mod.time,nk)
   #----------------------------------------------
   def update_file(self,file,nat=0,n_ar=2):
     from dump import dump_lmp

     dum=dump_lmp(file)
     dum.set_time([self.time_last+1,])
     for dmp in dum.iter:
       dat=dmp.get('atoms',[])
       sz={}
       arr={}
       m=nat+1
       for i in dat:
         sz[i[2]]=sz.get(i[2],0)+1
         if int(i[1])==n_ar:arr[i[2]]=-1
         if int(i[0])>m: m=int(i[0])+1

       nk=[1 for i in range(m)]
       tp=[0 for i in range(m)]
       
       for i in dat:
#         print i[0],i[1],i[2],m
         nk[int(i[0])]=sz[i[2]]*arr.get(i[2],1)
         tp[int(i[0])]=int(i[1])
        
       self.update(dmp['time'],nk,tp)

# ------ find short ----------------------------------------
   def info_total(self,Nst=10000,t_tick=0.004*0.001*5):

      len_time=int(self.number_ticks)+1
      a=[{}]
      ma=[{}]  

      tmax=self.number_ticks

      for b in self.dat:
        if type(b[0]) == type('a'):
           k=[j for j in cut_string_it(b[0])]
           el=k+b[1:]
        else:
           el=b

        if len(el)==1:
          continue

        total_time=sum( j[0] for j in el)
        if total_time<tmax:
           el = [[tmax-total_time,1]]+el
        ti=0
        for stab_time,stab_n,mstab_time,mstab_n,strike_n in atom_stat_it(el,Nst):
    
          if len(a)<ti+1:  a+=[{}]
          for key,val in stab_time.iteritems():
            a[ti][key] = a[ti].get(key,0.)+float(val)/key*t_tick  
    
    
          if len(ma)<ti+1:  ma+=[{}]
          for key,val in mstab_time.iteritems():
            ma[ti][key] = ma[ti].get(key,0.)+float(val)/key*t_tick  
          ti+=1
      return a,ma
#=================================================
if __name__=='__main__':    #run as programm
#  import pylab
#  from function import function

#  from timer import timer
#  tmr=timer()

  cl=history('history_txt')
  cl.write('history_txt')
  import os
  os.remove('tail.his')

  stop
  #print tmr
#  cl.unpack()
#  print tmr

#  cl.update_all('dump_clust.lmp')
#  cl.write('his2',new=1)
  
  #print cl.number_ticks

  t_tick=0.004*0.001*5
  Nst=10000
  a,ma=cl.info_total(Nst,t_tick)
  #print tmr

  x=[Nst*(i+1)*t_tick for i in range(len(a))]
  f=[]
  leg=[]
  for key in range(1,7):
    b=[a[i].get(key,0) for i in range(len(a))]
    f.append(function(x,b))
#  f[-1].write_fx('%i_stab1.dat'%key)
    f[-1] = f[-1].smooth_nlin7().diff5()

    f[-1].show(1)
    leg.append(key)
    f[-1].write_fx('%i_stab.dat'%key)
#pylab.figure(1)
#pylab.legend(tuple(leg))

  f1=[]
  for key in range(1,7):
    b=[ma[i].get(key,0) for i in range(len(ma))]
    f1.append(function(x,b))
#  f1[-1].write_fx('%i_mstab1.dat'%key)
    f1[-1] = f1[-1].smooth_nlin7().diff5()

    f1[-1].show(2)
    f1[-1].write_fx('%i_mstab.dat'%key)
    leg.append(key)

#pylab.figure(2)
#pylab.legend(tuple(leg))

  ff=[]
  for i in range(len(f)):
    ff.append(f[i]+f1[i])
    ff[-1].show(4)

  s=[]
  for i in range(len(a)):
    s.append( sum(a[i].itervalues()) )
    s[-1] +=sum(ma[i].itervalues()) 

  function(x,s).show(3)
    

#pylab.show()

