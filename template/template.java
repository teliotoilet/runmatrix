package macro;

import java.util.*;

import star.cadmodeler.*;
import star.common.*;
import star.base.neo.*;

import star.meshing.*;

import star.vis.*;

public class setupSim extends StarMacro {

  double H = <<H>>;	// wave height
  double T = <<T>>;	// wave period
  double L = <<L>>;	// wave length
  double U = <<U>>;	// mean horizontal fluid speed
  double d = <<d>>; 	// water depth
  int nL = <<nL>>;	// cells per wave length
  int nH = <<nH>>;	// cells per wave height
  double cfl = <<cfl>>; // target CFL number
  double ds0 = <<ds0>>; // max cell size
  String workingDir = "<<curDir>>";

  public void execute() {

    Simulation mysim = getActiveSimulation();

    Units meters = ((Units) mysim.getUnitsManager().getObject("m"));

    // 
    // setup Tools >> Field Functions
    //

    UserFieldFunction userFieldFunction_0 = ((UserFieldFunction) mysim.getFieldFunctionManager().getFunction("waveH"));
    userFieldFunction_0.setDefinition( String.valueOf(H) );

    UserFieldFunction userFieldFunction_1 = ((UserFieldFunction) mysim.getFieldFunctionManager().getFunction("waveL"));
    userFieldFunction_1.setDefinition( String.valueOf(L) );

    UserFieldFunction userFieldFunction_2 = ((UserFieldFunction) mysim.getFieldFunctionManager().getFunction("waveT"));
    userFieldFunction_2.setDefinition( String.valueOf(T) );

    UserFieldFunction userFieldFunction_3 = ((UserFieldFunction) mysim.getFieldFunctionManager().getFunction("waveU"));
    userFieldFunction_3.setDefinition( String.valueOf(U) );

    UserFieldFunction userFieldFunction_4 = ((UserFieldFunction) mysim.getFieldFunctionManager().getFunction("cellsPerL"));
    userFieldFunction_4.setDefinition( String.valueOf(nL) );

    UserFieldFunction userFieldFunction_5 = ((UserFieldFunction) mysim.getFieldFunctionManager().getFunction("cellsPerH"));
    userFieldFunction_5.setDefinition( String.valueOf(nH) );

    UserFieldFunction userFieldFunction_6 = ((UserFieldFunction) mysim.getFieldFunctionManager().getFunction("waterDepth"));
    userFieldFunction_6.setDefinition( String.valueOf(d) );

    UserFieldFunction userFieldFunction_7 = ((UserFieldFunction) mysim.getFieldFunctionManager().getFunction("dsMax"));
    userFieldFunction_7.setDefinition( String.valueOf(ds0) );

    UserFieldFunction userFieldFunction_8 = ((UserFieldFunction) mysim.getFieldFunctionManager().getFunction("targetCFL"));
    userFieldFunction_7.setDefinition( String.valueOf(cfl) );

    // 
    // setup Tools >> Volume Shapes
    //

    BrickVolumeShape brickVolumeShape_0 = 
      ((BrickVolumeShape) mysim.get(VolumeShapeManager.class).getObject("free surface refinement zone"));

    brickVolumeShape_0.getCorner1().setCoordinate(meters, meters, meters, new DoubleVector(new double[] {-3*L, 0.0, -1.5*H}));
    brickVolumeShape_0.getCorner2().setCoordinate(meters, meters, meters, new DoubleVector(new double[] { 3*L, 1.0,  1.5*H}));

    BrickVolumeShape brickVolumeShape_1 = 
      ((BrickVolumeShape) mysim.get(VolumeShapeManager.class).getObject("underwater refinement zone"));

    brickVolumeShape_1.getCorner1().setCoordinate(meters, meters, meters, new DoubleVector(new double[] {-3*L, 0.0, -0.25*L}));
    brickVolumeShape_1.getCorner2().setCoordinate(meters, meters, meters, new DoubleVector(new double[] { 3*L, 1.0, -1.5*H}));

    // 
    // setup Geometry >> 3D-CAD Models >> Tank >> Design Parameters
    //

    CadModel mycad = ((CadModel) mysim.get(SolidModelManager.class).getObject("Tank CAD"));

    UserDesignParameter userDesignParameter_1 = ((UserDesignParameter) mycad.getDesignParameterManager().getObject("halfLength"));
    userDesignParameter_1.getQuantity().setValue(3*L);

    UserDesignParameter userDesignParameter_2 = ((UserDesignParameter) mycad.getDesignParameterManager().getObject("halfHeight"));
    userDesignParameter_2.getQuantity().setValue(d);

    mycad.update();

    // 
    // generate mesh and initialize solution
    //

    MeshPipelineController meshPipelineController_0 = mysim.get(MeshPipelineController.class);
    meshPipelineController_0.generateVolumeMesh();

    Solution soln = mysim.getSolution();
    soln.initializeSolution();
    soln.initializeSolution(); // do it one more time just to be sure the VoF was properly initialized

    // 
    // update representations
    //

    FvRepresentation fv = ((FvRepresentation) mysim.getRepresentationManager().getObject("Volume Mesh"));

    Scene meshScene = mysim.getSceneManager().getScene("Mesh Scene 1");
    PartDisplayer partDisplayer_0 = ((PartDisplayer) meshScene.getDisplayerManager().getDisplayer("Mesh 1"));
    partDisplayer_0.setRepresentation(fv);

    Scene scalarScene = mysim.getSceneManager().getScene("Scalar Scene 1");
    PartDisplayer partDisplayer_1 = ((PartDisplayer) scalarScene.getDisplayerManager().getDisplayer("Outline 1"));
    partDisplayer_1.setRepresentation(fv);
    ScalarDisplayer scalarDisplayer_0 = ((ScalarDisplayer) scalarScene.getDisplayerManager().getDisplayer("Scalar 1"));
    scalarDisplayer_0.setRepresentation(fv);

    XYPlot waterPlot = ((XYPlot) mysim.getPlotManager().getPlot("Water surface"));
    waterPlot.setRepresentation(fv);

    XyzInternalTable xyzInternalTable_0 = 
      ((XyzInternalTable) mysim.getTableManager().getTable("XYZ Internal Table"));

    xyzInternalTable_0.setRepresentation(fv);

    // 
    // save some snapshots of the mesh and init solution
    //
    CurrentView currentView_0 = meshScene.getCurrentView();
    currentView_0.setInput(new DoubleVector(new double[] {0.0, 0.05000000074505806, 0.0}), new DoubleVector(new double[] {0.0, -64.5590286092214, 0.0}), new DoubleVector(new double[] {0.0, 0.0, 1.0}), 16.866340974990585, 0);
    meshScene.printAndWait(resolvePath(workingDir+"/mesh.png"), 1, 1011, 853);

    CurrentView currentView_1 = scalarScene.getCurrentView();
    currentView_1.setInput(new DoubleVector(new double[] {0.0, 0.05000000074505806, 0.0}), new DoubleVector(new double[] {0.0, -64.55873979051132, 0.0}), new DoubleVector(new double[] {0.0, 0.0, 1.0}), 16.86626557817765, 0);
    scalarScene.printAndWait(resolvePath(workingDir+"/init_alpha.png"), 1, 1011, 853);

    // 
    // save and start running
    //

    mysim.saveState(resolvePath(workingDir+"/<<caseName>>.sim"));

    mysim.getSimulationIterator().run();

  }
}
