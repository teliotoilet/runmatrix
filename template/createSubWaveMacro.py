#!/usr/bin/python
import sys

if len(sys.argv) <= 1:
    print 'specify MLER spectrum input file'
    print 'FORMAT: amplitude[=H/2]  phase[rad]  period[s]'
    sys.exit()

with open(sys.argv[1],'r') as f:

    # TODO: Update header as needed (e.g. to change the name of the physics
    #       continuum or the superposition VOF wave
    hdr = """// STAR-CCM+ macro: addSubWave.java
package macro;

import java.util.*;

import star.common.*;
import star.base.neo.*;
import star.vof.*;

public class addSubWaves extends StarMacro {

  public void execute() {
    execute0();
  }

  private void execute0() {

    Simulation simulation_0 = getActiveSimulation();
    PhysicsContinuum physicsContinuum_0 = ((PhysicsContinuum) simulation_0.getContinuumManager().getContinuum("Physics 1"));
    VofWaveModel vofWaveModel_0 = physicsContinuum_0.getModelManager().getModel(VofWaveModel.class);

    SuperpositionVofWave supWave = ((SuperpositionVofWave) vofWaveModel_0.getVofWaveManager().getObject("SuperpositionVofWave 1"));
    
    //*** MLER INPUTS BELOW***"""

    # TODO: Update subwave specification as needed
    wavestr = """
    FirstOrderSuperposingVofWave subwave{waveIdx:d} = 
      supWave.getSuperposingVofWaveManager().createSuperposingVofWave(FirstOrderSuperposingVofWave.class, "FirstOrderSuperposing");
    subwave{waveIdx:d}.getAmplitude().setValue({:f}); // m
    subwave{waveIdx:d}.getPhase().setValue({:f}); // radians
    subwave{waveIdx:d}.getSpecificationOption().setSelected(VofWaveSpecificationOption.WAVE_PERIOD_SPECIFIED);
    ((VofWavePeriodSpecification) subwave1.getVofWaveSpecification()).getWavePeriod().setValue({:f}); // seconds"""

    print hdr

    iwave = 0
    for line in f:
        A, phi, T = [ float(val) for val in line.split() ]
        #print A, phi, T
        print wavestr.format(A, phi, T, waveIdx=iwave)
        iwave += 1

    print """
  }
}"""

