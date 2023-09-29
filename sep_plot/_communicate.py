import re


class Object:
    """Objects that need to communicate with each other"""

    def __init__(self):
        pass

    def refresh(self):
        raise BaseException("Must override refresh")

    def update(self, k):
        raise BaseException("Must override update")

    def setCommunicate(self, com):
        self._com = com


class Communicate:
    """A Class that handles updates"""

    def __init__(self, **kw):
        """List of all the objects to update"""
        self._up = kw
        for k, v in self._up.items():
            v.setCommunicate(self)

    def add(self, **kw):
        """Add another communication object"""
        for k, v in kw.items():
            self._up[k] = v
            v.setCommunicate(self)

    def refresh(self, *args):
        """Refresh  objects"""
        for a in args:
            if a == "plots":
                for k in self._plots:
                    k.refresh()
            elif a in self._up:
                self._up[a].refresh()
            else:
                raise Exception("Internal error ", a)

    def finalize(self):
        """Finalize"""
        self._plots = []
        for k, v in self._up.items():
            if k.find("plot") == 0:
                self._plots.append(v)

    def update(self, **kw):
        """Update objects
           object, What to update """
        for k, v in kw.items():
            if k == "plots":
                for i in self._plots:
                    i.update(v)
            elif k in self._up:
                self._up[k].update(v)
            else:
                raise Exception("Internal error", k)
