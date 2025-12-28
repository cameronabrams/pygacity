# Author: Cameron F. Abrams, <cfa22@drexel.edu>
#
# Methods for pure-component cubic equations of state
# vdw and PengRobinson
from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from scipy.constants import R # J/mol-K, aka m3-Pa/mol-K

sqrt_2 = np.sqrt(2)

class GasConstant(float):
    """
    Universal gas constant R in (pressure * volume)/(mol*K).
    """

    # base value: J/(mol*K) = Pa*m^3/(mol*K)
    _R_SI = R

    _pressure_units = {
        "pa":   1.0,
        "kpa":  1e-3,
        "bar":  1e-5,
        "atm":  1.0 / 101325.0,
    }

    _volume_units = {
        "m3":  1.0,
        "l":   1e3,       # 1 m^3 = 1000 L
        "cm3": 1e6,
    }

    def __new__(cls, pressure_unit: str, volume_unit: str):
        p = pressure_unit.lower()
        v = volume_unit.lower()

        if p not in cls._pressure_units:
            raise ValueError(f"Unsupported pressure unit: {pressure_unit}")
        if v not in cls._volume_units:
            raise ValueError(f"Unsupported volume unit: {volume_unit}")

        factor = cls._pressure_units[p] * cls._volume_units[v]
        value = cls._R_SI * factor

        obj = super().__new__(cls, value)
        obj.pressure_unit = p
        obj.volume_unit = v
        obj.factor = factor
        return obj

    def __repr__(self):
        return f"GasConstant({self.pressure_unit!r}, {self.volume_unit!r})"

    def __str__(self):
        return (
            f"{float(self):g} "
            f"({self.pressure_unit}·{self.volume_unit})/(mol·K)"
        )

@dataclass
class CubicEOS:
    pressure_unit: str = 'mpa' # MPa
    volume_unit: str = 'm3'
    temperature_unit: str = 'K'
    thermal_energy_unit: str = 'J'
    P: float = 0.0
    T: float = 298.15
    Pc: float = 0.0 # critical pressure, any pressure unit
    Tc: float = 298.15 # critical temperature, K
    omega: float = 0.0 # acentricity factor, dimensionless

    showiter: bool = False
    maxiter: int = 100
    epsilon: float = 1.e-5
    iter: int = 0
    err: float = 0.0

    def unit_consistency(self, other: CubicEOS):
        return self.pressure_unit == other.pressure_unit and self.volume_unit == other.volume_unit and self.temperature_unit == other.temperature_unit

    @property    
    def volumetric_energy_unit(self):
        return self.pressure_unit + '-' + self.volume_unit
    
    # @property
    # def e_v2t(self): # factor to convert volumetric energy units to thermal energy units
    #     return GasConstant._pressure_units[self.pressure_unit.lower()] * GasConstant._volume_units[self.volume_unit.lower()]

    @property
    def Pv(self): # Pv in volumetric energy units
        return self.P * self.v

    @property
    def R(self):
        return GasConstant(self.pressure_unit, self.volume_unit)

    @property
    def a(self):
        return (27 / 64) * self.R**2 * self.Tc**2 / self.Pc
    
    @property
    def da_dT(self):
        return 0.0

    @property
    def b(self):
        return self.R * self.Tc / (8 * self.Pc)
    
    @property
    def A(self): # dimensionless vdw a parameter
        return self.a * self.P / (self.R * self.T)**2
    
    @property
    def B(self): # dimensionelss vdw b parameter
        return self.b * self.P / (self.R * self.T)
    
    @property
    def cubic_coeff(self): # default for vdw eos
        return np.array([1, -1 - self.B, self.A, -self.A * self.B])
    
    @property
    def Z(self):
        complx_roots = np.roots(self.cubic_coeff)
        real_roots_idx = np.where(complx_roots.imag==0)[0]
        real_roots = complx_roots[real_roots_idx].real
        if len(real_roots) == 1:
            return real_roots[0]
        else:
            return np.array([real_roots[0], real_roots[2]])

    @property
    def v(self):
        return self.Z * self.R * self.T / self. P

    @property
    def h_departure(self): # default for vdw eos
        z = self.Z
        return self.R * self.T * (z - 1 - self.A * np.reciprocal(z))

    @property
    def s_departure(self):
        z = self.Z
        return self.R * (np.log(z - self.B) - np.log(z))
    
    @property
    def logphi(self): # natural log of fugacity coefficient(s)
        z = self.Z
        return np.log(z / (z - self.B)) - self.A / z
    
    @property
    def f(self): # fugacity/fugacities
        logPhi = self.logphi
        return np.exp(logPhi) * self.P

    @property
    def Pvap(self): # vapor pressure at temperature; P is retained
        saveP = self.P
        self.P = self.Pc * (self.T / self.Tc)**8
        keepgoing = True
        self.iter = 0
        while keepgoing:
            self.iter += 1
            try:
                fV, fL = self.f
            except:
                raise ValueError(f'Error computing pvap at {self.T} K')
            self.err = np.abs(fL / fV - 1)
            if self.showiter: print(f'Iter {self.iter}: P {self.P:.6f}, fV {fV:.6f}, fL {fL:.6f}; error {self.err:.4e}')
            self.P *= fL / fV
            if self.err < self.epsilon or self.iter == self.maxiter:
                keepgoing = False
            if self.iter >= self.maxiter:
                print(f'Reached {self.iter} iterations without convergence; error {np.abs(fL/fV-1):.4e}')
        Pvap = self.P
        self.P = saveP
        return Pvap
    
    def DeltaH(self, other: CubicEOS, Cp: dict | float = None):
        if not self.unit_consistency(other):
            raise ValueError('inconsistent units')
        if isinstance(Cp, float):
            a = Cp
            b, d, d = 0.0, 0.0, 0.0
        elif isinstance(Cp, dict):
            a, b, c, d = Cp['a'], Cp['b'], Cp['c'], Cp['d']
        else:
            a, b, c, d = 0.0, 0.0, 0.0, 0.0
        dt1 = other.T - self.T
        dt2 = other.T**2 - self.T**2
        dt3 = other.T**3 - self.T**3
        dt4 = other.T**4 - self.T**4
        dH_ideal = a * dt1 + b / 2 * dt2 + c / 3 * dt3 + d / 4 * dt4
        return other.h_departure + dH_ideal - self.h_departure

    def DeltaS(self, other: CubicEOS, Cp: dict | float = None):
        if not self.unit_consistency(other):
            raise ValueError('inconsistent units')
        if isinstance(Cp, float):
            a = Cp
            b, d, d = 0.0, 0.0, 0.0
        elif isinstance(Cp, dict):
            a, b, c, d = Cp['a'], Cp['b'], Cp['c'], Cp['d']
        else:
            a, b, c, d = 0.0, 0.0, 0.0, 0.0
        lrt = np.log(other.T / self.T)
        dt1 = other.T - self.T
        dt2 = other.T**2 - self.T**2
        dt3 = other.T**3 - self.T**3
        dS_ideal =  a * lrt + b * dt1 + c / 2 * dt2 + d / 3 * dt3 - self.R * self.R.factor * np.log(other.P / self.P)
        return other.s_departure + dS_ideal - self.s_departure
    
    def DeltaPV(self, other: CubicEOS):
        if not self.unit_consistency(other):
            raise ValueError('inconsistent units')
        return other.Pv * other.e_v2t - self.Pv * self.e_v2t
    
    def DeltaU(self, other: CubicEOS):
        return self.DeltaH(other) - self.DeltaPV(other)
    
@dataclass
class IdealGasEOS(CubicEOS):
    
    @property
    def a(self):
        return 0.0
    
    @property
    def b(self):
        return 0.0
    
    @property
    def Z(self):
        return 1.0

@dataclass
class PengRobinsonEOS(CubicEOS):

    @property
    def kappa(self):
        return 0.37464 + 1.54226 * self.omega - 0.26992 * self.omega**2
    
    @property
    def alpha(self):
        return (1 + self.kappa * (1 - np.sqrt(self.T / self.Tc)))**2

    @property
    def a(self):
        return 0.45724 * self.R**2 * self.Tc**2 / self.Pc * self.alpha
    
    @property
    def b(self):
        return 0.07780 * self.R * self.Tc / self.Pc

    @property
    def da_dT(self):
        return -self.a * self.kappa / np.sqrt(self.alpha * self.T * self.Tc)
    
    @property
    def cubic_coeff(self):  # coefficients for cubic form of PR eos
        return np.array([1, -1 + self.B, self.A - 3 * self.B**2 - 2*self.B, -self.A * self.B + self.B**2 + self.B**3])

    @property
    def lrfrac(self):
        z = self.Z
        num_arg = z + (1 + sqrt_2) * self.B
        den_arg = z + (1 - sqrt_2) * self.B
        return np.log(num_arg / den_arg)
    
    @property
    def h_departure(self):
        z = self.Z
        return self.R * self.T * (z - 1) + (self.T * self.da_dT - self.a) / (2 * sqrt_2 * self.b) * self.lrfrac

    @property
    def s_departure(self):
        z = self.Z
        return self.R * np.log(z - self.B) + self.da_dT/(2 * sqrt_2 * self.b) * self.lrfrac
    
    @property
    def logphi(self): # natural log of fugacity coefficient
        z = self.Z
        return z - 1 - np.log(z - self.B) - self.A / (2 * np.sqrt(2) * self.B) * self.lrfrac

