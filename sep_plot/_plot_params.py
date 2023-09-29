"""Class for describing plot parameters"""


class Param:
    """Class for plot parameter"""

    def __init__(self, default_value, typ, help_documentation, **kw):
        """Set the default value and type for a parameter

        default_value - Default value
        typ      - Type for parameter
        helpD    _ Help documentation
        Optional parameter:
            valid    - Valid parameters
        """
        self._value = default_value
        self._valid = None
        self._typ = typ
        self._help = help_documentation
        if "valid" in kw:
            self._valid = kw["valid"]

    def set_value(self, value):
        """Set the value for the parameter"""
        if self._valid:
            if not value in self._valid:
                raise Exception("Not valid parameter")
        self._value = value

    def return_help(self):
        """Return the help for a parameter"""
        if self._value:
            return f" [{self._value}] - {self._typ} - {self._help}"
        else:
            return f"  - {self._typ} - {self._value}"

    def get_value(self):
        """Get parameter value"""
        if self._value is None:
            return None
        if self._typ == "int":
            return int(self._value)
        elif self._typ == "float":
            return float(self._value)
        elif self._typ == "floatVec":
            lst = []
            for item in self._value:
                lst.append(float(item))
            return lst
        elif self._typ == "intVec":
            lst = []
            for item in self._value:
                lst.append(int(item))
            return lst
        else:
            return self._value


class Params:
    """Class for plot parameters"""

    def __init__(self, message=None, extra=None):
        """Initialize plot parameters

        message - Additional message to be printed when doing self-doc
        extra -  Additional extension to use when trying to match params
           (e.g. display0 as well as display)

        """
        self._pars = {}
        self._extra = extra
        self._message = message

    def add_param(self, par, def_value, typ, help_documentation, **kw):
        """Add a parameter"""
        self._pars[par] = Param(def_value, typ, help_documentation, **kw)

    def add_params(self, pars):
        """Add multiple parameters"""
        for key, val in pars.items():
            self._pars[key] = val

    def print_help(self):
        """Print the help"""
        print(f"\n{self._message}")
        for key, val in self._pars.items():
            print(f"{key} {val.return_help()}")

    def get_param(self, par):
        """Return parameter"""
        if not par in self._pars:
            raise Exception("Unknown key " + par)
        return self._pars[par].get_value()

    def set_params(self, dct):
        """Set parameters"""
        for key, val in self._pars.items():
            if key in dct:
                val.set_value(dct[key])
            if self._extra:
                tot = key + self._extra
                if tot in dct:
                    val.set_value(dct[tot])

    def set_file_params(self, dct):
        """Update a dictionary with the default params"""
        self.set_params(dct)
        for key, val in self._pars.items():
            dct[key] = val.get_value()
        return dct
