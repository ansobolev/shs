#!/usr/bin/python 
# __*__ coding: utf8 __*__

oneline = "Prepare and write one dimentional statistics"

docstr = """
s = statistics2(step)		defined statistics with step

s.clear() 			clear the stat, step is unchanged 
s.add_data(list,list1)		add set data to statistics

s.write_data("file")     write data to "file" and make normalization "norm"

Variables:
    s.n0	- number of steps from zero are skipped (left side of diagram) 
    s.dx	- step of hystogram 
    s.main[] 	- list of hystogram data
"""

# Class definition

class statistics2:

  # --------------------------------------------------------------------
  def __init__(self,dx):
    self.n0=0
    self.dx=dx
    self.main = []
    self.main2 = [] 
    self.count = []

  # --------------------------------------------------------------------
  def clear(self):
    self.n0=0
    self.main = []
    self.main2 = []
    self.count= [] 


  # --------------------------------------------------------------------
  def add_data(self,x,y):
    print len(x), len(y)
    if x==[]: return
 
    if self.main==[]: self.n0=int(x[0]/self.dx) 
    for j in range(len(x)):
        i=x[j]
	ind=int(i/self.dx)-self.n0
        if ind < 0: 
		for k in range(abs(ind)):
                    self.main.insert(0,0)
                    self.main2.insert(0,0)
                    self.count.insert(0,0)
		self.n0 += ind
                ind=0    
	elif ind >= len(self.main):
		for k in range(ind+1-len(self.main)):
                    self.main.append(0)
		    self.main2.append(0)
                    self.count.append(0)

        self.main[ind] += y[j]
        self.main2[ind] += y[j]*y[j]
        self.count[ind]+= 1

  # --------------------------------------------------------------------
  def write_data(self,file):
    f = open(file,"w")
    
    for i in xrange(len(self.main)):
        a= a2 = dis = 0
        if self.count[i]<>0:
	   a=float(self.main[i])/self.count[i]
           a2=float(self.main2[i])/self.count[i]
           dis=a*a-a2
           ind=(i+self.n0)*self.dx 
	   f.write( '%12.6f %12.6f %12.6f \n' %(ind,a,dis))
    f.close()	
