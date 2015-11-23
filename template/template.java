package macro;

import java.util.*;

import star.cadmodeler.*;
import star.common.*;
import star.base.neo.*;

import star.meshing.*;

import star.vis.*;

public class setupSim extends StarMacro {

  double H = <<H>>;	        // wave height
  double T = <<T>>;	        // wave period
  double L = <<L>>;	        // wave length
  double U = <<U>>;	        // mean horizontal fluid speed
  double d = <<d>>;         // water depth
  double halfL = <<halfL>>; // domain half length normalized by wavelength
  double dampL = <<dampL>>; // length of numerical beach, normalized by wavelength
  double extL  = <<extL>>;  // how far to extend the domain past x=+halfL, to accomodate the numerical beach
  double width = <<width>>; // domain width
  int nL = <<nL>>;	        // cells per wave length
  int nH = <<nH>>;	        // cells per wave height
  double cfl = <<cfl>>;     // target CFL number
  double ds0 = <<ds0>>;     // max cell size
  int nInner = <<inner>>;   // max inner iterations
  String workingDir = "<<curDir>>";

  public void execute() {

    Simulation mysim = getActiveSimulation();

    Units meters = ((Units) mysim.getUnitsManager().getObject("m"));

    // 
    // setup Tools >> Field Functions
    //

    UserFieldFunction heightFunction = ((UserFieldFunction) mysim.getFieldFunctionManager().getFunction("waveH"));
    heightFunction.setDefinition( String.valueOf(H) );

    UserFieldFunction wavelengthFunction = ((UserFieldFunction) mysim.getFieldFunctionManager().getFunction("waveL"));
    wavelengthFunction.setDefinition( String.valueOf(L) );

    UserFieldFunction waveperiodFunction = ((UserFieldFunction) mysim.getFieldFunctionManager().getFunction("waveT"));
    waveperiodFunction.setDefinition( String.valueOf(T) );

    UserFieldFunction wavespeedFunction = ((UserFieldFunction) mysim.getFieldFunctionManager().getFunction("waveU"));
    wavespeedFunction.setDefinition( String.valueOf(U) );

    UserFieldFunction cellsLengthFunction = ((UserFieldFunction) mysim.getFieldFunctionManager().getFunction("cellsPerL"));
    cellsLengthFunction.setDefinition( String.valueOf(nL) );

    UserFieldFunction cellsHeightFunction = ((UserFieldFunction) mysim.getFieldFunctionManager().getFunction("cellsPerH"));
    cellsHeightFunction.setDefinition( String.valueOf(nH) );

    UserFieldFunction depthFunction = ((UserFieldFunction) mysim.getFieldFunctionManager().getFunction("waterDepth"));
    depthFunction.setDefinition( String.valueOf(d) );

    UserFieldFunction dsmaxFunction = ((UserFieldFunction) mysim.getFieldFunctionManager().getFunction("dsMax"));
    dsmaxFunction.setDefinition( String.valueOf(ds0) );

    UserFieldFunction cflFunction = ((UserFieldFunction) mysim.getFieldFunctionManager().getFunction("targetCFL"));
    cflFunction.setDefinition( String.valueOf(cfl) );

    UserFieldFunction halfLFunction = ((UserFieldFunction) mysim.getFieldFunctionManager().getFunction("domainHalfL"));
    halfLFunction.setDefinition( String.valueOf(halfL) );

    UserFieldFunction dampLFunction = ((UserFieldFunction) mysim.getFieldFunctionManager().getFunction("beachL"));
    dampLFunction.setDefinition( String.valueOf(dampL) );

    UserFieldFunction extLFunction = ((UserFieldFunction) mysim.getFieldFunctionManager().getFunction("extendL"));
    extLFunction.setDefinition( String.valueOf(extL) );

    // 
    // setup Geometry >> 3D-CAD Models >> Tank >> Design Parameters
    //
    double halfLength = halfL*L;
    double halfHeight = d;
    double extLength  = extL*L;

    CadModel mycad = ((CadModel) mysim.get(SolidModelManager.class).getObject("Tank CAD"));

    UserDesignParameter userDesignParameter_1 = ((UserDesignParameter) mycad.getDesignParameterManager().getObject("halfLength"));
    userDesignParameter_1.getQuantity().setValue(halfLength);

    UserDesignParameter userDesignParameter_2 = ((UserDesignParameter) mycad.getDesignParameterManager().getObject("halfHeight"));
    userDesignParameter_2.getQuantity().setValue(halfHeight);

    UserDesignParameter userDesignParameter_3 = ((UserDesignParameter) mycad.getDesignParameterManager().getObject("extendLength"));
    userDesignParameter_3.getQuantity().setValue(extLength);

    mycad.update();

    // 
    // setup Tools >> Volume Shapes
    //

    BrickVolumeShape brickVolumeShape_0 = 
      ((BrickVolumeShape) mysim.get(VolumeShapeManager.class).getObject("free surface refinement zone"));

    brickVolumeShape_0.getCorner1().setCoordinate(meters, meters, meters, new DoubleVector(new double[] {-halfLength          ,   0.0, -1.5*H}));
    brickVolumeShape_0.getCorner2().setCoordinate(meters, meters, meters, new DoubleVector(new double[] { halfLength+extLength, width,  1.5*H}));

    BrickVolumeShape brickVolumeShape_1 = 
      ((BrickVolumeShape) mysim.get(VolumeShapeManager.class).getObject("underwater refinement zone"));

    brickVolumeShape_1.getCorner1().setCoordinate(meters, meters, meters, new DoubleVector(new double[] {-halfLength          ,   0.0, -0.25*L}));
    brickVolumeShape_1.getCorner2().setCoordinate(meters, meters, meters, new DoubleVector(new double[] { halfLength+extLength, width,  -1.5*H}));

    // 
    // set plot axes
    //
    XYPlot surfPlot = ((XYPlot) mysim.getPlotManager().getPlot("Water surface"));
    Axes surfAxes = surfPlot.getAxes();

    Axis axis_0 = surfAxes.getXAxis();
    axis_0.setMinimum(-halfLength);
    axis_0.setMaximum( halfLength+extLength);

    Axis axis_1 = surfAxes.getYAxis();
    axis_1.setMinimum(-0.75*H);
    axis_1.setMaximum( 1.25*H);

    // 
    // generate mesh and initialize solution
    //

    MeshPipelineController meshPipelineController_0 = mysim.get(MeshPipelineController.class);
    meshPipelineController_0.generateVolumeMesh();

    Solution soln = mysim.getSolution();
    soln.initializeSolution();
    soln.initializeSolution(); // do it one more time just to be sure the VoF was properly initialized (is this necessary?)

    // 
    // update representations
    //

    FvRepresentation fv = ((FvRepresentation) mysim.getRepresentationManager().getObject("Volume Mesh"));

    Scene meshScene = mysim.getSceneManager().getScene("Mesh Scene 1");
    PartDisplayer meshDisplayer = ((PartDisplayer) meshScene.getDisplayerManager().getDisplayer("Mesh 1"));
    meshDisplayer.setRepresentation(fv);

    Scene uScene = mysim.getSceneManager().getScene("u");
    PartDisplayer uPartDisplayer = ((PartDisplayer) uScene.getDisplayerManager().getDisplayer("Outline 1"));
    uPartDisplayer.setRepresentation(fv);
    ScalarDisplayer uScalarDisplayer = ((ScalarDisplayer) uScene.getDisplayerManager().getDisplayer("Scalar 1"));
    uScalarDisplayer.setRepresentation(fv);

    Scene wScene = mysim.getSceneManager().getScene("w");
    PartDisplayer wPartDisplayer = ((PartDisplayer) wScene.getDisplayerManager().getDisplayer("Outline 1"));
    wPartDisplayer.setRepresentation(fv);
    ScalarDisplayer wScalarDisplayer = ((ScalarDisplayer) wScene.getDisplayerManager().getDisplayer("Scalar 1"));
    uScalarDisplayer.setRepresentation(fv);

    Scene alphaScene = mysim.getSceneManager().getScene("alpha");
    PartDisplayer alphaPartDisplayer = ((PartDisplayer) alphaScene.getDisplayerManager().getDisplayer("Outline 1"));
    alphaPartDisplayer.setRepresentation(fv);
    ScalarDisplayer alphaScalarDisplayer = ((ScalarDisplayer) alphaScene.getDisplayerManager().getDisplayer("Scalar 1"));
    alphaScalarDisplayer.setRepresentation(fv);

    XYPlot waterPlot = ((XYPlot) mysim.getPlotManager().getPlot("Water surface"));
    waterPlot.setRepresentation(fv);

    XyzInternalTable alphaTable = ((XyzInternalTable) mysim.getTableManager().getTable("XYZ Internal Table"));
    alphaTable.setRepresentation(fv);

    // 
    // setup views
    //
    // setInput(DoubleVector fp, DoubleVector pos, DoubleVector vu, double ps, int pm) 
    // fp:  focal point, the point you're looking at
    // pos: position of the observer
    // vu:  view up
    // ps:  ???
    // pm:  projection mode (0=perspective, 1=parallel)
    DoubleVector fp  = new DoubleVector(new double[] {extLength/2, width/2, 0.0});
    DoubleVector pos = new DoubleVector(new double[] {extLength/2, -1.2*(2*halfLength+extLength), 0.0}); // step back an extra 20% of the domain length
    DoubleVector vu  = new DoubleVector(new double[] {0.0, 0.0, 1.0});

    CurrentView currentView_0 = meshScene.getCurrentView();
    //currentView_0.setInput(fp, pos, vu, ps, 0);
    Coordinate meshScene_coordinate_2 = currentView_0.getViewUpCoordinate();
    meshScene_coordinate_2.setCoordinate(meters, meters, meters, vu);
    Coordinate meshScene_coordinate_1 = currentView_0.getPositionCoordinate();
    meshScene_coordinate_1.setCoordinate(meters, meters, meters, pos);
    Coordinate meshScene_coordinate_0 = currentView_0.getFocalPointCoordinate();
    meshScene_coordinate_0.setCoordinate(meters, meters, meters, fp);

    CurrentView currentView_1 = alphaScene.getCurrentView();
    //currentView_1.setInput(fp, pos, vu, ps, 0);
    Coordinate alphaScene_coordinate_2 = currentView_1.getViewUpCoordinate();
    alphaScene_coordinate_2.setCoordinate(meters, meters, meters, vu);
    Coordinate alphaScene_coordinate_1 = currentView_1.getPositionCoordinate();
    alphaScene_coordinate_1.setCoordinate(meters, meters, meters, pos);
    Coordinate alphaScene_coordinate_0 = currentView_1.getFocalPointCoordinate();
    alphaScene_coordinate_0.setCoordinate(meters, meters, meters, fp);

    CurrentView currentView_2 = uScene.getCurrentView();
    //currentView_2.setInput(fp, pos, vu, ps, 0);
    Coordinate uScene_coordinate_2 = currentView_2.getViewUpCoordinate();
    uScene_coordinate_2.setCoordinate(meters, meters, meters, vu);
    Coordinate uScene_coordinate_1 = currentView_2.getPositionCoordinate();
    uScene_coordinate_1.setCoordinate(meters, meters, meters, pos);
    Coordinate uScene_coordinate_0 = currentView_2.getFocalPointCoordinate();
    uScene_coordinate_0.setCoordinate(meters, meters, meters, fp);

    CurrentView currentView_3 = wScene.getCurrentView();
    //currentView_3.setInput(fp, pos, vu, ps, 0);
    Coordinate wScene_coordinate_2 = currentView_3.getViewUpCoordinate();
    wScene_coordinate_2.setCoordinate(meters, meters, meters, vu);
    Coordinate wScene_coordinate_1 = currentView_3.getPositionCoordinate();
    wScene_coordinate_1.setCoordinate(meters, meters, meters, pos);
    Coordinate wScene_coordinate_0 = currentView_3.getFocalPointCoordinate();
    wScene_coordinate_0.setCoordinate(meters, meters, meters, fp);

    // 
    // save some snapshots of the mesh and init solution
    //
    meshScene.printAndWait(resolvePath(workingDir+"/mesh.png"), 1, 1280,1080);

    alphaScene.printAndWait(resolvePath(workingDir+"/init_alpha.png"), 1, 1280,1080);

    //surfPlot.encode(resolvePath(workingDir+"/init_surf.png"), "png", 800, 600);
    Scene surfPlotScene = mysim.getSceneManager().getScene("Water surface plot");
    surfPlotScene.printAndWait(resolvePath(workingDir+"/init_surfPlot.png"), 1, 800,600);

    // note: the waterSurface MUST exist, otherwise macro quits!!!
    alphaTable.extract();
    alphaTable.export(resolvePath(workingDir+"/waterSurface/XYZ_Internal_Table_table_0.csv"), ",");   

    // 
    // update solver settings
    //
    InnerIterationStoppingCriterion innerIters = 
              ((InnerIterationStoppingCriterion) mysim.getSolverStoppingCriterionManager().getSolverStoppingCriterion("Maximum Inner Iterations"));

    innerIters.setMaximumNumberInnerIterations(nInner);

    // 
    // save and start running
    //

    mysim.saveState(resolvePath(workingDir+"/<<caseName>>.sim"));

    mysim.getSimulationIterator().run();

  }
}
