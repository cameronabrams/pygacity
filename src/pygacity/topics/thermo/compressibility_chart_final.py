"""
Generalized Compressibility Factor Chart - With Phase Transitions
==================================================================
Handles vapor-liquid equilibrium region for subcritical isotherms (Tr < 1.0)
where isotherms are discontinuous.
"""

import numpy as np
import json
from scipy.interpolate import Rbf
import warnings

from importlib.resources import files

class CompressibilityChart:
    """
    Compressibility factor chart with proper phase transition handling.
    
    For Tr < 1.0, isotherms go through vapor-liquid equilibrium with
    a discontinuity. The chart provides:
    - Vapor phase Z values (high Z)
    - Liquid phase Z values (low Z)
    - Saturation pressure where transition occurs
    """
    
    resources_path = files('pygacity') / 'resources'
    data_path = resources_path / 'corresponding-states-data'
    data_json = data_path / 'Z_vs_Pr_isotherms.json'
    indicials_json = data_path / 'Z_vs_Pr_indicials.json'
    def __init__(self):
        """Initialize with digitized data and indicials."""
        self.load_data_with_warping(self.data_json, self.indicials_json)
        self._identify_phase_transitions()
        self._create_interpolators()
    
    def load_data_with_warping(self, isotherms_file, indicials_file):
        """Load data and create coordinate transformation using indicials."""
        
        # Step 1: Load indicials from separate file
        print("="*70)
        print("STEP 1: Loading Indicials")
        print("="*70)
        
        with open(indicials_file, 'r') as f:
            indicials_data = json.load(f)
        
        # Extract indicials
        pixel_x = []
        pixel_y = []
        data_Pr = []
        data_Z = []
        
        for point in indicials_data['data']:
            pixel_x.append(point['x'])
            pixel_y.append(point['y'])
            data_Pr.append(point['value'][0])
            data_Z.append(point['value'][1])
        
        self.pixel_x = np.array(pixel_x)
        self.pixel_y = np.array(pixel_y)
        self.data_Pr = np.array(data_Pr)
        self.data_Z = np.array(data_Z)
        
        print(f"Loaded {len(self.pixel_x)} indicials")
        
        # Find critical point
        crit_idx = np.where((np.abs(self.data_Pr - 1.0) < 0.01) & 
                           (np.abs(self.data_Z - 0.27) < 0.01))[0]
        if len(crit_idx) > 0:
            print(f"★ Critical point found at Pr=1.0, Z=0.27")
        
        # Step 2: Create coordinate transformation
        print("\n" + "="*70)
        print("STEP 2: Creating Coordinate Transformation")
        print("="*70)
        
        log_data_Pr = np.log10(self.data_Pr)
        
        self.warp_to_logPr = Rbf(self.pixel_x, self.pixel_y, log_data_Pr, 
                                  function='thin_plate', smooth=0)
        self.warp_to_Z = Rbf(self.pixel_x, self.pixel_y, self.data_Z, 
                            function='thin_plate', smooth=0)
        
        print("Created RBF transformations")
        
        # Step 3: Load and warp isotherms from separate file
        print("\n" + "="*70)
        print("STEP 3: Loading and Warping Isotherms")
        print("="*70)
        
        with open(isotherms_file, 'r') as f:
            isotherms_data = json.load(f)
        
        self.isotherms = {}
        
        for dataset in isotherms_data['datasetColl']:
            name = dataset['name']
            
            # Only process isotherm datasets  
            if not name.startswith('Z_T_'):
                continue
            
            tr_str = name.replace('Z_T_', '').replace('p', '.')
            Tr = float(tr_str)
            
            # Extract raw pixel coordinates
            raw_pixel_x = []
            raw_pixel_y = []
            raw_value_x = []
            raw_value_y = []

            for point in dataset['data']:
                raw_pixel_x.append(point['x'])
                raw_pixel_y.append(point['y'])
                value = point['value']
                raw_value_x.append(value[0])
                raw_value_y.append(value[1])

            raw_pixel_x = np.array(raw_pixel_x)
            raw_pixel_y = np.array(raw_pixel_y)
            raw_value_x = np.array(raw_value_x)
            raw_value_y = np.array(raw_value_y)
            
            sorted_indices = np.argsort(raw_value_x)

            # Apply coordinate transformation
            warped_log_Pr = self.warp_to_logPr(raw_pixel_x, raw_pixel_y)
            warped_Pr = 10**warped_log_Pr
            warped_Z = self.warp_to_Z(raw_pixel_x, raw_pixel_y)
            
            # Sort by Pr
            warped_sorted_indices = np.argsort(warped_Pr)
            warped_Pr = warped_Pr[warped_sorted_indices]
            warped_Z = warped_Z[warped_sorted_indices]
            if not np.all(sorted_indices == warped_sorted_indices):
                print(f'Tr {Tr}: warping changed order')
                for ir, r, rz, iw, w, wz in zip(sorted_indices, raw_value_x[sorted_indices], raw_value_y[sorted_indices], warped_sorted_indices, warped_Pr[warped_sorted_indices], warped_Z[warped_sorted_indices]):
                    print(f'[{ir:>2d}] {r:.3f}, {rz:.3f} -> [{iw:>2d}] {w:.3f}, {wz:.3f}')
                warped_sorted_indices = sorted_indices
                warped_Pr = warped_Pr[warped_sorted_indices]
                warped_Z = warped_Z[warped_sorted_indices]
            
            self.isotherms[Tr] = {
                'Pr': warped_Pr,
                'Z': warped_Z,
                'n_points': len(warped_Pr)
            }
            
            # Add critical point to Tr=1.0 isotherm
            if abs(Tr - 1.0) < 0.001:
                if not np.any(np.abs(warped_Pr - 1.0) < 0.001):
                    warped_Pr = np.append(warped_Pr, 1.0)
                    warped_Z = np.append(warped_Z, 0.27)
                    
                    sorted_indices = np.argsort(warped_Pr)
                    warped_Pr = warped_Pr[sorted_indices]
                    warped_Z = warped_Z[sorted_indices]
                    
                    self.isotherms[Tr] = {
                        'Pr': warped_Pr,
                        'Z': warped_Z,
                        'n_points': len(warped_Pr)
                    }
                    print(f"  → Added critical point to Tr={Tr:.2f}")
        
        self.Tr_values = np.array(sorted(self.isotherms.keys()))
        
        print(f"\nLoaded and warped {len(self.isotherms)} isotherms")
        print(f"Tr range: {self.Tr_values.min():.2f} to {self.Tr_values.max():.2f}")
    
    def _identify_phase_transitions(self):
        """
        Identify phase transitions in subcritical isotherms.
        
        The data may not be sorted by Pr - it follows the curve visually,
        tracing the liquid branch, then jumping to vapor branch.
        We need to identify the discontinuity and split accordingly.
        """
        print("\n" + "="*70)
        print("STEP 4: Identifying Phase Transitions")
        print("="*70)
        
        self.phase_transitions = {}
        
        for Tr in self.Tr_values:
            if Tr >= 1.0:
                # Supercritical - no phase transition
                self.phase_transitions[Tr] = None
                continue
            
            Pr = self.isotherms[Tr]['Pr']
            Z = self.isotherms[Tr]['Z']
            
            search_Z_idx = np.where(Pr < 1.0)
            search_Z = Z[search_Z_idx]

            # Look for large jumps in Z between consecutive points
            # This indicates the discontinuity
            dZ = np.diff(search_Z)
            large_jumps = np.where((np.abs(dZ) > 0.3) & (Pr[:1] < 1.0))[0]
            
            if len(large_jumps) == 0:
                # No clear phase transition found
                print(f'No transitions detected by jumps in Z at Tr {Tr}')
                self.phase_transitions[Tr] = None
                continue
            
            # Find the largest jump
            jump_idx = large_jumps[np.argmax(np.abs(dZ[large_jumps]))]
            
            # The discontinuity is between jump_idx and jump_idx+1
            # Before jump: one phase
            # After jump: other phase
            
            Z_before = Z[jump_idx]
            Z_after = Z[jump_idx + 1]
            
            Pr_before = Pr[jump_idx]
            Pr_after = Pr[jump_idx + 1]

            if np.abs(Pr_after - Pr_before) > 0.1:
                print(f'Tr {Tr}: jump {Z_before}->{Z_after} Pr_before {Pr_before} Pr_after {Pr_after}')
                self.phase_transitions[Tr] = None
                continue

            # Determine which is liquid vs vapor based on Z values
            # Liquid has higher Z in the two-phase region
            if Z_before > Z_after:
                # Before jump is liquid, after is vapor
                liquid_indices = np.arange(0, jump_idx + 1)
                vapor_indices = np.arange(jump_idx + 1, len(Pr))
            else:
                # Before jump is vapor, after is liquid
                vapor_indices = np.arange(0, jump_idx + 1)
                liquid_indices = np.arange(jump_idx + 1, len(Pr))
            
            # Estimate saturation pressure
            # It's approximately where both phases exist
            # Use the Pr value near the discontinuity
            Pr_sat = (Pr[jump_idx] + Pr[jump_idx + 1]) / 2
            
            # Sort each branch by Pr for interpolation
            liq_Pr = Pr[liquid_indices]
            liq_Z = Z[liquid_indices]
            liq_sort = np.argsort(liq_Pr)
            
            vap_Pr = Pr[vapor_indices]
            vap_Z = Z[vapor_indices]
            vap_sort = np.argsort(vap_Pr)
            
            self.phase_transitions[Tr] = {
                'Pr_sat': Pr_sat,
                'liquid': {
                    'Pr': liq_Pr[liq_sort],
                    'Z': liq_Z[liq_sort]
                },
                'vapor': {
                    'Pr': vap_Pr[vap_sort],
                    'Z': vap_Z[vap_sort]
                }
            }
            
            print(f"Tr={Tr:.2f}: Phase transition at Pr_sat≈{Pr_sat:.3f}")
            print(f"  Discontinuity between indices {jump_idx} ({Pr[jump_idx]:.3f}) and {jump_idx+1} ({Pr[jump_idx+1]:.3f})")
            print(f"  Liquid: {len(liquid_indices)} points, Z: [{liq_Z.min():.3f}, {liq_Z.max():.3f}], Pr: [{liq_Pr.min():.3f}, {liq_Pr.max():.3f}]")
            print(f"  Vapor:  {len(vapor_indices)} points, Z: [{vap_Z.min():.3f}, {vap_Z.max():.3f}], Pr: [{vap_Pr.min():.3f}, {vap_Pr.max():.3f}]")
    
    def _create_interpolators(self):
        """Create interpolators for each isotherm, handling phase transitions."""
        print("\n" + "="*70)
        print("STEP 5: Creating Interpolators")
        print("="*70)
        
        from scipy.interpolate import interp1d
        
        self.interpolators = {}
        
        for Tr in self.Tr_values:
            if self.phase_transitions[Tr] is None:
                # Single-phase region - simple interpolator
                Pr = self.isotherms[Tr]['Pr']
                Z = self.isotherms[Tr]['Z']
                if Tr < 1.0:
                    phase = 'liquid'
                else:
                    phase = 'vapor'
                self.interpolators[Tr] = {
                    'type': 'single_phase',
                    'phase': phase,
                    'interp': interp1d(Pr, Z, kind='linear',
                                      bounds_error=False, fill_value='extrapolate')
                }
            else:
                # Two-phase region - separate interpolators
                trans = self.phase_transitions[Tr]
                
                self.interpolators[Tr] = {
                    'type': 'two_phase',
                    'Pr_sat': trans['Pr_sat'],
                    'liquid': interp1d(trans['liquid']['Pr'], trans['liquid']['Z'],
                                      kind='linear', bounds_error=False, fill_value='extrapolate'),
                    'vapor': interp1d(trans['vapor']['Pr'], trans['vapor']['Z'],
                                     kind='linear', bounds_error=False, fill_value='extrapolate')
                }
        
        print(f"Created interpolators for {len(self.interpolators)} isotherms")
        
        # Count two-phase isotherms
        n_two_phase = sum(1 for Tr in self.Tr_values 
                         if self.phase_transitions[Tr] is not None)
        print(f"  Single-phase: {len(self.interpolators) - n_two_phase}")
        print(f"  Two-phase: {n_two_phase}")
    
    def get_Z(self, Pr, Tr, phase='auto'):
        """
        Calculate compressibility factor Z.
        
        Parameters
        ----------
        Pr : float or array-like
            Reduced pressure
        Tr : float or array-like
            Reduced temperature
        phase : {'auto', 'vapor', 'liquid'}, optional
            For two-phase region:
            - 'auto': Return vapor phase for Pr < Pr_sat, liquid for Pr > Pr_sat
            - 'vapor': Force vapor phase
            - 'liquid': Force liquid phase
        
        Returns
        -------
        Z : float or ndarray
            Compressibility factor
        
        Notes
        -----
        For Tr < 1.0 and near saturation, the isotherm is discontinuous.
        This method handles the discontinuity by splitting into vapor/liquid branches.
        """
        Pr_input = np.atleast_1d(Pr)
        Tr_input = np.atleast_1d(Tr)
        scalar_input = (Pr_input.size == 1 and Tr_input.size == 1)
        
        # Check bounds
        if np.any(Pr_input < 0.1) or np.any(Pr_input > 30):
            warnings.warn("Pr values outside typical range [0.1, 30]")
        
        if np.any(Tr_input < self.Tr_values.min()) or np.any(Tr_input > self.Tr_values.max()):
            warnings.warn(f"Tr values outside data range [{self.Tr_values.min():.2f}, {self.Tr_values.max():.2f}]")
        
        Z_result = np.zeros_like(Pr_input, dtype=float)
        
        for i, (pr, tr) in enumerate(zip(Pr_input, Tr_input)):
            # Find bounding Tr values
            idx = np.searchsorted(self.Tr_values, tr)
            
            if idx == 0 or idx >= len(self.Tr_values):
                # Extrapolation - use nearest isotherm
                Tr_nearest = self.Tr_values[0] if idx == 0 else self.Tr_values[-1]
                Z_result[i] = self._interpolate_on_isotherm(pr, Tr_nearest, phase)
                
            elif self.Tr_values[idx-1] == tr:
                # Exactly on an isotherm
                Z_result[i] = self._interpolate_on_isotherm(pr, tr, phase)
                
            else:
                # Between isotherms - linear interpolation
                Tr_low = self.Tr_values[idx-1]
                Tr_high = self.Tr_values[idx]
                
                Z_low = self._interpolate_on_isotherm(pr, Tr_low, phase)
                Z_high = self._interpolate_on_isotherm(pr, Tr_high, phase)
                
                alpha = (tr - Tr_low) / (Tr_high - Tr_low)
                Z_result[i] = Z_low + alpha * (Z_high - Z_low)
        
        if scalar_input:
            return Z_result.item()
        return Z_result
    
    def _interpolate_on_isotherm(self, Pr, Tr, phase='auto'):
        """Interpolate Z on a single isotherm, handling phase transitions."""
        interp_data = self.interpolators[Tr]
        
        if interp_data['type'] == 'single_phase':
            # Simple case
            return interp_data['interp'](Pr)
        
        else:
            # Two-phase region
            Pr_sat = interp_data['Pr_sat']
            
            if phase == 'auto':
                # Determine phase based on pressure
                if Pr < Pr_sat:
                    return interp_data['vapor'](Pr)
                else:
                    return interp_data['liquid'](Pr)
            elif phase == 'vapor':
                return interp_data['vapor'](Pr)
            elif phase == 'liquid':
                return interp_data['liquid'](Pr)
            else:
                raise ValueError(f"Invalid phase: {phase}")
    
    def get_saturation_pressure(self, Tr):
        """
        Get saturation pressure for a given Tr < 1.0.
        
        Returns None if Tr >= 1.0 (supercritical).
        """
        if Tr >= 1.0:
            return None
        
        # Find nearest Tr in data
        idx = np.argmin(np.abs(self.Tr_values - Tr))
        Tr_nearest = self.Tr_values[idx]
        
        if self.phase_transitions[Tr_nearest] is not None:
            return self.phase_transitions[Tr_nearest]['Pr_sat']
        return None
    
    def plot_chart(self, Tr_curves=None, figsize=(12, 8), show_phases=True):
        """Plot the compressibility chart with phase transitions marked."""
        import matplotlib.pyplot as plt
        from matplotlib import colormaps as cm

        cmap = cm['viridis']

        if Tr_curves is None:
            Tr_curves = self.Tr_values
        
        fig, ax = plt.subplots(figsize=figsize)
        
        n_iso = len(Tr_curves)

        for idx, Tr in enumerate(Tr_curves):
            if Tr not in self.isotherms:
                continue
            
            if self.phase_transitions[Tr] is None:
                # Single phase
                data = self.isotherms[Tr]
                shortcode = 'o-'
                if 'phase' in data:
                    if data['phase'] == 'liquid':
                        shortcode = 'o--'

                ax.plot(data['Pr'], data['Z'], shortcode, 
                       markersize=2, linewidth=1.5, alpha=0.7,
                       label=f'Tr = {Tr:.2f}', color=cmap(idx/n_iso))
            else:
                # Two phase
                trans = self.phase_transitions[Tr]
                
                # Plot liquid branch
                liq = trans['liquid']
                ax.plot(liq['Pr'], liq['Z'], 'o-',
                       markersize=2, linewidth=1.5, alpha=0.7, color=cmap(idx/n_iso),
                       label=f'Tr = {Tr:.2f}')
                
                # Plot vapor branch  
                vap = trans['vapor']
                ax.plot(vap['Pr'], vap['Z'], 'o--',
                       markersize=2, linewidth=1.5, alpha=0.7, color=cmap(idx/n_iso))
                
                # Mark transition
                if show_phases:
                    ax.axvline(trans['Pr_sat'], color='red', 
                              linestyle=':', linewidth=1, alpha=0.3)
        
        ax.set_xlabel('Reduced Pressure, Pr', fontsize=12)
        ax.set_ylabel('Compressibility Factor, Z', fontsize=12)
        ax.set_title('Generalized Compressibility Chart (Zc = 0.27)\n' + 
                    'With Phase Transitions',
                    fontsize=14, fontweight='bold')
        ax.set_xscale('log')
        ax.grid(True, which='both', alpha=0.3)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8, ncol=2)
        ax.set_xlim(0.1, 30)
        ax.set_ylim(0, 1.5)
        
        plt.tight_layout()
        return fig, ax


def demo():
    """Demonstrate phase transition handling."""
    import matplotlib.pyplot as plt
    
    print("\n" + "="*70)
    print("COMPRESSIBILITY CHART WITH PHASE TRANSITIONS")
    print("="*70)
    
    chart = CompressibilityChart()
    
    # Validation
    print("\n" + "="*70)
    print("VALIDATION TESTS")
    print("="*70)
    
    tests = [
        (1.0, 1.0, 0.27, "auto", "Critical point"),
        (1.0, 1.5, 0.92, "auto", "Reference point"),
        (1.0, 0.90, None, "vapor", "Tr=0.90 vapor (above Pr_sat)"),
        (0.3, 0.90, None, "liquid", "Tr=0.90 liquid (below Pr_sat)"),
        (5.0, 2.0, None, "auto", "Supercritical"),
    ]
    
    print(f"\n{'Pr':>6} {'Tr':>6} {'Phase':>10} {'Z':>8} {'Expected':>10} {'Description':<30}")
    print("-"*85)
    
    for pr, tr, expected, phase, desc in tests:
        z = chart.get_Z(pr, tr, phase=phase)
        if np.isnan(z):
            print(f"{pr:>6.1f} {tr:>6.2f} {phase:>10} {'NaN':>8} {'--':>10} {desc:<30}")
        elif expected:
            error = abs(z - expected) / expected * 100
            print(f"{pr:>6.1f} {tr:>6.2f} {phase:>10} {z:>8.4f} {expected:>10.2f} ({error:>4.1f}%) {desc:<30}")
        else:
            print(f"{pr:>6.1f} {tr:>6.2f} {phase:>10} {z:>8.4f} {'--':>10} {desc:<30}")
    
    # Plot
    print("\n" + "="*70)
    print("GENERATING PLOTS")
    print("="*70)
    
    fig, ax = chart.plot_chart()
    plt.savefig('chart_with_phases.png', dpi=150, bbox_inches='tight')
    print("Saved: chart_with_phases.png")
    plt.close()
    
    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)


if __name__ == "__main__":
    demo()
