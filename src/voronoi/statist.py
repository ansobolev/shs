#!/usr/bin/python 
# __*__ coding: utf8 __*__

oneline = "Prepare and write one dimentional statistics"

docstr = """
s = statistics(step)		defined statistics with step

s.clear() 			clear the stat, step is unchanged 
s.add_data(list)		add set data to statistics
s.get_data("1<x<=3","x>10")	resive data "1<x<=3" or "x>10" or ...

s.write_data("file","norm")     write data to "file" and make normalization "norm"
	"norm" could be "no" - no normalization
			"yes"- to the number of data items
			"g_r"- to the density and volume in spherical coordinates

s.write_info("file",*args)	write information to "file"
				if file is not exists write names of columns 
	*arg could be : t  	- any variables
			"min"   - minimal value
			"max"   - maximum value
			"num"   - number of data items
			"mid"   - mean value
			"mid_sq"- mean square value
	     	   	"1<x<5" - conditions (x - is variable), see get data
Variables:
    s.sum 	- summ of data items
    s.sum2 	- summ of squares of data items
    s.number 	- number of data items
    s.min 	- minimal value
    s.max	- maximum value

    s.n0	- number of steps from zero are skipped (left side of diagram) 
    s.dx	- step of hystogram 
    s.main[] 	- list of hystogram data
"""

# Class definition

class statistics:

  # --------------------------------------------------------------------
  def __init__(self,dx):
    self.sum = self.sum2 = self.number = self.min = self.max = self.mean = self.strdev = 0
    self.n0=0
    self.dx=dx
    self.main = []

  # --------------------------------------------------------------------
  def clear(self):
    self.sum = self.sum2 = self.number = self.min = self.max = self.mean = self.strdev = 0
    self.n0=0
    self.main = []

  # --------------------------------------------------------------------
  def add_data(self,x):
    if x==[]: return
    if not hasattr(x,'__iter__'): x=[x]

    if self.number==0: self.n0=int(x[0]/self.dx) 
    for i in x:
	ind=int(i/self.dx)-self.n0
        if ind < 0: 
		for k in range(abs(ind)): self.main.insert(0,0)
		self.n0 += ind
                ind=0    
	elif ind >= len(self.main):
		for k in range(ind+1-len(self.main)): self.main.append(0)

        self.main[ind] += 1
        if self.min > i: self.min=i
	if self.max < i: self.max=i
        self.sum += i
        self.sum2 += i*i
        self.number += 1
    self.mean = self.sum / self.number
    self.strdev = pow(abs(self.sum2/self.number - self.mean*self.mean), 0.5)
#----------------------------------------------------------------
  def add_data2(self,x,y):
    if x==[]: return
 
    if self.number==0: self.n0=int(x[0]/self.dx) 
    for j in range(len(x)):
        i=x[j]
	ind=int(i/self.dx)-self.n0
        if ind < 0: 
		for k in range(abs(ind)): self.main.insert(0,0)
		self.n0 += ind
                ind=0    
	elif ind >= len(self.main):
		for k in range(ind+1-len(self.main)): self.main.append(0)

        self.main[ind] += y[j]
        if self.min > i: self.min=i
	if self.max < i: self.max=i
        self.sum += i
        self.sum2 += i*i
        self.number += 1

  # --------------------------------------------------------------------
  def get_data(self,*arg):
     sum=0
     for i in range(len(self.main)):
     	x=i*self.dx+self.n0
     	if reduce(lambda x,y: x or y, map(eval, arg)):
	    sum += self.main[i]
     return sum
  # --------------------------------------------------------------------
  def get_statistics(self):
     x=[i*self.dx+self.n0 for i in range(len(self.main))]
     return x,self.main
  # --------------------------------------------------------------------
  def write_data(self,file,mode="w",norm="no"):
    if self.main==[]: return
    f = open(file,mode)
    main=self.main[:]
    if norm=="yes": 
	main=map(lambda x: float(x)/self.number, main)

    if norm=="g_r": 
        ind0=0   #(self.n0)
        ind1=(len(self.main)+self.n0)
        cf=(pow(ind1,3)-pow(ind0,3))/3./self.number
	for i in xrange(len(self.main)):
        	ind=(i+self.n0)
                main[i]=float(main[i])*cf/pow(ind,2)

    for i in xrange(len(self.main)):
        ind=(i+self.n0)*self.dx 
	f.write( '%12.6f %12.6f \n' %(ind,main[i]))
    f.write('\n\n')
    f.close()	
 #========== Graphics =========================================
  def show(self,n=1,cl=0,norm='no'):

    main=self.main
    nmb=self.number
    n0=self.n0
    x=[ (i+n0)*self.dx for i in range(len(main))] 

    if norm=="yes": 
	y=[float(x)/nmb for i in main]

    elif norm=="g_r": 
        ind0=0   #(self.n0)
        ind1=(len(self.main)+n0)
        cf=(pow(ind1,3)-pow(ind0,3))/3./nmb
        y=[ cf*i/pow(j,2) for i,j in zip(main,x) ]
    else:
        y=main

    try:
      from pylab import ion,figure,clf,plot,draw #pylab
      ion()
      figure(n)
      if cl<>0:
        clf()
      plot(x,y, 'o',lw=2)
      draw()
    except:
      self.show_nograph()
    return

  # --------------------------------------------------------------------
  def write_info(self,file,*arg):
    min=self.min
    max=self.max
    num=self.number
    mid=mid_sq=0
    if num<>0 :
        mid=float(self.sum)/num
        mid_sq=float(self.sum2)/num
        
    s=s1=''
    list=[]
    for i in arg:
	s1=s1+'%12s '
	s=s+'%12.6f '
        try:
	   list.append(eval(i))
	except:
	   try:
		list.append(self.get_data(i))
	   except:
		list.append(i)
		i=str(i)	
    s1=s1+'\n'
    s=s+'\n'

    try: 
	f = open(file,"r")
	f.close()
	f = open(file,"a")
    except:
	f = open(file,"a")
	f.write(s1 %arg)
    
    f.write( s %tuple(list))
    f.close()	
