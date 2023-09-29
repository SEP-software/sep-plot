import numpy as np
from sep-python import Hypercube
from _communicate import Object as Communicate
from _plot_params import Params 


class Position:
    """Position object"""

    def __init__(self,initial_hyper):
        """
            Initiaize position object with
            Option 1 - hypercube
        """
        self._hyper = initial_hyper
        self._n = [1] *8
        self._b = [0] *8
        self._e = [1] *8
        self._pos = [0]* 8
        self._nax_max = 0
        if isinstance(initial_hyper, Hypercube.hypercube):
            self.init_from_hyper(initial_hyper)
        else:
            raise Exception("Only support hypercube initialization")

    def init_from_hyper(self, hyp):
        """Initialize from a hypercube"""
        for i in range(len(self._hyper.axes)):
            self._n[i] = self._hyper.axes[i].n
            self._e[i] = self._n[i]
            self._pos[i] = int(self._n[i] / 2)
            if self._n[i] > 1:
                self._nax_max = i

    def advance(self, iax, step):
        """Advance a frame looping around if necessary
            iax - Axis
            step - Step
        """
        if abs(step) >= self._n[iax]:
            step = step / abs(step) * (self._n[iax] - 1)

        self._pos[iax] += step
        if self._pos[iax] >= self._n[iax]:
            self._pos[iax] -= self._n[iax]
        elif self._pos[iax] < 0:
            self._pos[iax] += self._n[iax]

    def set_position(self, iax, ipos):
        """Set the position along one axis"""
        if ipos < 0:
            raise Exception("Illegal set position value < 0")
        if ipos >= self._n[iax]:
            raise Exception("Illegal set position greater >= n")
        if ipos < self._b[iax] or ipos >= self._e[iax]:
            self.reset_axis(iax)
        self._pos[iax] = int(ipos)

    def reset_axis(self, iax):
        """Reset axis to default"""
        self._b[iax] = 0
        self._e[iax] = self._n[iax]
        self._e[iax] / 2

    def reset_all_axis(self):
        """Reset all axes"""
        for i in range(8):
            self.reset_axis(i)

    def get_position(self):
        """Return position"""
        return self._pos
    
    def set_position(self, iax, b, e):
        """ Set the window for the axis
            iax - Axis to change
            b - First sample
            e - Last sample"""
        self._b[iax] = max(0, int(b + .5))
        self._e[iax] = min(int(e + .5), self._n[iax])
        if self._e[iax] == self._b[iax]:
            if self._e[iax] < self._n[iax]:
                self._e[iax] = self._b[iax] + 1
            else:
                self._b[iax] = self._e[iax] - 1

        self._pos[iax] = int((b + e) / 2)


class Orient(Communicate):
    """Orientation object"""

    def __init__(self,**kw):
        """Initiaize position object with
                        Option 1 -
                            init_from= hyper, iwind=wind
                        Option 2 
                            init_from=position, iwind=iwind
        """
        super().__init__()

        if "help" in kw:
            self._params=plotParams.params("Orientation parameters (specify by window pos0_0=)")
            self.addParams()
            self._params.printHelp()
            return
        if not "init_from" in kw:
            raise Exception("Must supply init_from")
        if not "iwind" in kw:
            raise Exception("Must supply iwind")

        self._iwind=str(kw["iwind"])


        init_from=kw["init_from"]
        if isinstance(init_from, Hypercube):
            self._pos=position(init_from)    
        elif isinstance(init_from, position):
            self._pos=position(init_from._hyper)    
        else:
            raise Exception("Must initialize with a hypercube or position")
        self._params=params("Orientation parameters (specify by window pos0_0=)","_"+self._iwind)
        self.addParams()

        self._order = [0, 1, 2, 3, 4, 5, 6, 7]
        self._reverse = [
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False]

    def switch_axes(self, iax1, iax2):
        """Switch two axes order"""
        if iax1 < 0 or iax1 > self._pos.nAxMax:
            raise Exception(
                "Illegal axis 1 " +
                iax1 +
                " must be between 0 and " +
                self._pos.nAxMax)
        if iax2 < 0 or iax2 > self._pos.nAxMax:
            raise Exception(
                "Illegal axis 2 " +
                iax2 +
                " must be between 0 and " +
                self._pos.nAxMax)
        i = self._order[iax1]
        self._order[iax1] = self._order[iax2]
        self._order[iax2] = i



    def reverse_axis(self, iax):
        """Reverse axis"""
        if iax < 0 or iax > self._pos.nAxMax:
            raise Exception(
                "Illegal axis 1 ",
                iax,
                " must be between 0 and ",
                self._pos.nAxMax)
        if self._reverse[iax]:
            self._reverse[iax] = False
        else:
            self._reverse[iax] = True


    def reset_all(self):
        """Completely reset display"""
        self.reset_all_axes()
        for i in range(8):
            self._order[i] = False
            self._reverse[i] = False

    def return_orrient_axis(self, iax):
        """Return current oriented axis for display
            iax - Axis to return
           Return:
                ax - True axis
                b - first sample
                e - last sample +1
                rev - Whether or not to reverse axis"""
        return self._order[iax], self._pos._b[self._order[iax]], self._pos._e[
            self._order[iax]], self._reverse[self._order[iax]]

    def add_params(self):
        """Add parameters associated with orientation"""
        self._params.add_param("b",None, "intList", "List containing initial positions along each axis to display")
        self._params.add_param("e",None, "intList", "List containing ending positions along each axis to display")
        self._params.add_param("pos",None, "intList", "List containing  position along each axis to display")
        self._params.add_param("order",None, "intList", "List containing order of axes to display")

    def set_params(self, kw):
        """Set parameters"""
        self._params.set_params(kw)
        b= self._params.get_param("b")
        if b:
            for i in range(len(b)):
                if b[i]>=0 and b< self._pos._n[i]:
                    self._pos._b[i]=b[i]
        e= self._params.get_param("e")
        if e:
            for i in range(len(e)):
                if e[i]>=0 and e[i] <=self._pos._n[i]:
                    if e[i] >b[i]:
                        self._pos._e[i]=e[i]
                    else:
                        self._pos._b[i]=e[i]-1
                        self._pos._e[i]=e[i]
        pos= self._params.get_param("pos")
        if pos:
            for i in range(len(pos)):
                if pos[i]>0 and pos[i]< self._pos._n[i]:
                    if pos[i] >=self._pos._b[i] and pos[i] < self._pos._e[i]:
                        self._pos._pos[i]=pos[i]
                    else:
                        if pos[i] < self._pos._b[i]:
                            self._pos._b[i]=pos[i]
                        if pos[i] >= self._pos._e[i]:
                            self._pos._e[i]=pos[i]+1
        order=self._params.get_param("order")
        if order:
            found=[False]*10
            valid=True
            for i in range(len(order)):
                if order[i] <0 or order[i]>=8: 
                    valid=False
                for j in range(i):
                    if order[j]==order[i]:
                        valid=False
            if valid:
                for i in range(len(order)):
                    self._order[i]=order[i]
                    found[order[i]]=True
                for i in range(len(order),8):
                    done=False
                    j=0
                    while not done:
                        if not found[j]:
                            found[j]=True
                            self._order[i]=j
                            done=True

    def advance(self, iax, step):
        """Advance a frame looping around if necessary
            iax - Axis
            step - Step
        """
        self._pos.advance(iax,step)


    def set_position(self, iax, ipos):
        """Set the position along one axis
            iax - Axis
            ipos - Set position
        """
        self._pos.set_position(iax,ipos)
 

    def reset_axis(self, iax):
        """Reset axis to default
            iax - Axis to reset

        """
        self._pos.reset_axis(iax)
 

    def reset_all_axes(self):
        """Reset all axes"""
        for i in range(8):
            self.reset_axis(i)

    def get_position(self):
        """Return position"""
        return self._pos.get_position() 

    def set_window(self, iax, b, e):
        """ Set the window for the axis
            iax - Axis to change
            b - First sample
            e - Last sample"""
        self._pos.set_window(iax,b,e)

