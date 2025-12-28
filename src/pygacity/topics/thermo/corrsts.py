
import pandas as pd

from importlib.resources import files
from scipy.interpolate import LinearNDInterpolator

class CorrespondingStates:
    resource_path = files('pygacity') / 'resources'
    data_path = resource_path / 'corresponding-states-data'

    def __init__(self):
        self.edep = pd.read_csv(self.data_path / 'enthalpy-departures.csv', header=0, index_col=None)
        self.sdep = pd.read_csv(self.data_path / 'entropy-departures.csv', header=0, index_col=None)
        self.Hr_limits = dict(
            Tr = [min(self.edep['Tr']), max(self.edep['Tr'])],
            Pr = [min(self.edep['Pr']), max(self.edep['Pr'])])
        self.Sr_limits = dict(
            Tr = [min(self.sdep['Tr']), max(self.sdep['Tr'])],
            Pr = [min(self.sdep['Pr']), max(self.sdep['Pr'])])
        self.Hr = LinearNDInterpolator(list(zip(self.edep['Tr'], self.edep['Pr'])), self.edep['Dr'])
        self.Sr = LinearNDInterpolator(list(zip(self.sdep['Tr'], self.sdep['Pr'])), self.sdep['Dr'])

    def readHdep(self, Tr, Pr):
        if self.Hr_limits['Tr'][0] > Tr or self.Hr_limits['Tr'][1] < Tr:
            print(f'Requested value of Tr {Tr} is outside interpolation bounds [{self.Hr_limits["Tr"][0]}, {self.Hr_limits["Tr"][1]}]')
            return None
        if self.Hr_limits['Pr'][0] > Pr or self.Hr_limits['Pr'][1] < Pr:
            print(f'Requested value of Pr {Pr} is outside interpolation bounds [{self.Hr_limits["Pr"][0]}, {self.Hr_limits["Pr"][1]}]')
            return None
        return self.Hr(Tr, Pr)
    
    def readSdep(self,Tr,Pr):
        if self.Sr_limits['Tr'][0] > Tr or self.Sr_limits['Tr'][1] < Tr:
            print(f'Requested value of Tr {Tr} is outside interpolation bounds [{self.Hr_limits["Tr"][0]}, {self.Hr_limits["Tr"][1]}]')
            return None
        if self.Sr_limits['Pr'][0] > Pr or self.Sr_limits['Pr'][1] < Pr:
            print(f'Requested value of Pr {Pr} is outside interpolation bounds [{self.Hr_limits["Pr"][0]}, {self.Hr_limits["Pr"][1]}]')
            return None
        return self.Sr(Tr, Pr)
