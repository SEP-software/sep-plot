import numba
import numpy as np
import math


class base:
    """Base class doesn't do anything but setup interface"""
    def __init__(self):
        pass;
    def apply(self,inA):
        """Apply clip on array 
        
        array - Numpy input array
        """
        raise Exception("Must override apply function")

class basicClip(base):
    def __init__(self ,clip=None,bclip=None,eclip=None):
        """
            clip - Apply -clip and clip
            bclip - Apply minimum value clip
            eclip - Apply maximum value clip
        """
        if not clip and not bclip and not eclip:
            raise Exception("must specify bclip, eclip or clip")
        
        if eclip:
            self._eclip=eclip
            if bclip:
                self._bclip=bclip
            elif clip:
                self._bclip=-clip
            else:
                self._bclip=None
        else:
            if clip:
                self._eclip=clip
                if bclip:
                    self._bclip=bclip
                else:
                    self._bclip=-clip
            else:
                self.eclip=None
                if bclip:
                    self._bclip=bclip
    def apply(self,array):
        """Apply clip to array
        
            array - Input array
        
        """
        return np.clip(array,a_min=self._bclip,a_max=self._eclip)

class percentileClip(basicClip):
    """Clip data based on percentiles"""
    
    def __init__(self,array,bpclip=1,epclip=99):
        """
            array to base clip on
            bpclip - Low clip
            epclip - High clip
        """
        self._bclip=None
        self._eclip=None
        if bpclip:
            self._bclip=np.percentile(array,bpclip)
        if epclip:
            self._eclip=np.percentile(array,epclip)
        super().__init__(self,bclip=self._bclip,eclip=self._eclip)
            
            
@numba.njit()
def sumE(array,hw):
    tmp=np.zeros(array.shape[0]+hw*2)
    out=array.copy()
    tmp[0:hw]=array[0]
    tmp[hw:hw+array.shape[0]]=array[:]
    tmp[array.shape[0]+hw]=array[array.shape[0]-1]
    out[0]=np.sum(tmp[0:2*hw+1])
    for i in range(1,out.shape[0]):
        out[i]=out[i-1]-tmp[i-1]+tmp[2*hw+i]
    return out


@numba.njit(parallel=True)
def calcL1_1D(array,wind):
    out=array.copy()
    hwind=int(wind[0])
    for i2 in numba.prange(array.shape[0]):
        x=array[i2,:]
        y=sumE(x,hwind)
        out[i2,:]=y
    return out

@numba.njit(parallel=True)
def calcL1_2D(array,wind):
    out=array.copy()
    hw1=int(wind[0])
    hw2=int(wind[1])
    for i3 in numba.prange(array.shape[0]):
        tmp=np.zeros((out.shape[1],out.shape[0]),np.float32)
        for i2 in range(out.shape[1]):
            tmp[i2,:]=sumE(array[i3,i2,:],hw1)
        for i1 in range(out.shape[0]):
            out[i3,:,i1]=sumE(array[i3,:,i1],hw2)
    return out
            
            
     
     
@numba.njit(parallel=True)
def calcL1_3D(array,wind):
    out=array.copy()
    hw1=int(wind[0])
    hw2=int(wind[1])
    hw3=int(wind[2])
    for i4 in numba.prange(array.shape[0]):
        tmp=np.zeros(out.shape[1],out.shape[2],out.shape[3])
        tmp2=tmp.copy()
        for i3 in range(out.shape[1]):
            for i2 in range(out.shape[2]):
                tmp[i3,i2,:]=sumE(array[i4,i3,i2,:],hw1)
        for i3 in range(out.shape[1]):
            for i1 in range(out.shape[2]):
                  tmp2[i3,:,i1]=sumE(tmp[i3,:,i1],hw2)
        for i2 in range(out.shape[2]):
            for i1 in range(out.shape[3]):
                  out[i4,:,i2,i1]=sumE(tmp2[:,i2,i1],hw3)
    return out
                  
@numba.njit(parallel=True)
def applyAGC(inA,wt,sm,nsm):
    out=inA.copy()
    sm=wt.max()/nsm/128
    print(wt.min(),wt.max(),wt[20],sm)
    for i in numba.prange(inA.shape[0]):
        out[i]=inA[i]/(wt[i]/nsm+sm)
    return out
   
        
class agc(base):
    
    def __init__(self,wind:list=[100]):
        if len(wind)>3:
            raise Exception("Expecting wind to be an int array of len<=3")
        self._wind=numba.typed.List()
        self._nsm=1
        for w in wind: 
            self._wind.append(w)
            self._nsm*=w
    def apply(self,array):
        """
        Apply AGC on given dataset
        
        """
        absA=np.absolute(array)
        perc=4
        found=False
        while not found and perc<80:
            val=np.percentile(absA,perc)
            if val==0:
                perc*=2
            else:
                found=True
        if not found:
            raise Exception("Can not find enough non-zero values")
        else:
            if len(array.shape)==1:
                if len(self._wind)>1:
                    raise Exception("Can not have window higher dimension than data")
                oneD=calcL1_1D(np.reshape(absA,(array.shape[0],1),self._wind))
            elif len(array.shape)==2:
                if len(self._wind)==1:
                    oneD=calcL1_1D(absA,self._wind)
                elif len(self._wind)==2:
                    oneD=calcL1_2D(np.reshape(absA,(array.shape[0],array.shape[1],1)),self._wind)
                else:
                    raise Exception("wind must be 1-D or 2-D when array is 2-D")
            elif len(array.shape)==3:
                if len(self._wind)==1:
                    oneD=calcL1_1D(np.reshape(absA,(array.shape[0],array.shape[1]*array.shape[1])),self._wind)
                elif len(self._wind)==2:
                    oneD=calcL1_2D(array,self._wind)
                else:
                    oneD=calcL1_3D(np.reshape(absA,(array.shape[0],array.shape[1],array.shape[2],1)),self._wind)
            else:
                n=list(array.shape)
                if len(self._wind)==1:
                    oneD=calcL1_1D(np.reshape(absA,(n[0],math.product(n[1:]))),self._wind)
                elif len(self._wind)==2:
                    oneD=calcL1_2D(np.reshape(absA,(n[0],n[1],math.product(n[2:]))),self._wind)
                else:
                    oneD=calcL1_3D(np.reshape(absA,(n[0],n[1],n[2],math.product(n[3:]))),self._wind)
        return np.reshape(applyAGC(np.reshape(array,(array.size,)),\
                                   np.reshape(oneD,(oneD.size,)),val,self._nsm),\
                          array.shape)
        

@numba.jit(nopython=True)
def softClipBasic(array,g):
    """Soft clip data (Claerbout-softclip)
      array - array to softclip
      g - softclip parameter
    """
    print(type(array),type(g),g)
    n=array.size
    out=array.copy()
    for i in range(n):
        out[i]=array[i]*g/math.sqrt(1+g*g*array[i]*array[i])
    return out


class softClip(base):
    
    def __init__(self,perc:float=75,fact:float=math.sqrt(1./3.)):
        """SOft clip an array
            perc - Percentile to scale soft clip by
            fact - Factor to apply to the percentil
        """
        self._perc=perc
        self._fact=fact
                 
                 
    def apply(self,array):
        """
        Apply softclip on given dataset
        
        """
        return np.reshape(softClipBasic(np.reshape(array,(array.size,)),self._fact/np.percentile(array,self._perc)),array.shape)