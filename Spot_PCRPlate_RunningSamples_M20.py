#### Crazy Idea Spotting script
###############################################
### Spotting Multichannel M20 Gen2 protocol ###
###############################################

## Author Jonas Greve Lauritsen
## Protocol for multichannel spotting.

############################

#### Package loading ####
from opentrons import protocol_api, types # type: ignore
from math import *


# #### User Input Parameters ###
def add_parameters(parameters):

    ## Number of samples included.
    parameters.add_int(
        variable_name = "sample_count",
        display_name = "Sample count",
        description = "Number of input DNA samples.",
        default = 128,
        minimum = 1,
        maximum = 128
        )
    
    parameters.add_str(
        variable_name="first_well",
        display_name="First Well of Plate 1",
        choices=[
            {"display_name": "A1", "value": "A1"},
            {"display_name": "A2", "value": "A2"},
            {"display_name": "A3", "value": "A3"},
            {"display_name": "A4", "value": "A4"},
            {"display_name": "A5", "value": "A5"},
            {"display_name": "A6", "value": "A6"},
            {"display_name": "A7", "value": "A7"},
            {"display_name": "A8", "value": "A8"},
            {"display_name": "A9", "value": "A9"},
            {"display_name": "A10", "value": "A10"},
            {"display_name": "A11", "value": "A11"},
            {"display_name": "A12", "value": "A12"}
        ],
        default="A1",
    )




#### Meta Data ####
metadata = {
    'protocolName': 'Multichannel Spotting Script',
    'apiLevel': '2.22',
    'robotType': 'OT-2',    
    'author': 'Jonas Lauritsen <jonas.lauritsen@sund.ku.dk>',
    'description': "Using multichannel to spot ZooMs peptide samples."}


#### Protocol Script ####
def run(protocol: protocol_api.ProtocolContext):
    
    #### Loading Protocol Runtime Parameters ####
    Sample_Number = protocol.params.sample_count
    Sample_Col = ceil(Sample_Number/8)
    First_Well = protocol.params.first_well
    
    ## Select the number of the first well
    First_Well_Number = {
        "A1": 0,
        "A2": 8,
        "A3": 16,
        "A4": 24,
        "A5": 32,
        "A6": 40, 
        "A7": 48, 
        "A8": 56, 
        "A9": 64, 
        "A10": 72, 
        "A11": 80,
        "A12": 88
    }
    First_Well_Number = First_Well_Number[First_Well]
    FirstPlate_Columns = 12-ceil(First_Well_Number/8)


    ## Pattern to spot sapmle onto Bruker plate (triplicates, every fourth well)
    ## OT-2 API scripting does not allow B-row calling for multichannel pipettes. An adjustment of wells is done by moving the y-coordinate
    Spot_Pattern = [
        ['A1','A5','A9'],['A2','A6','A10'],['A3','A7','A11'],['A4','A8','A12'],['A13','A17','A21'],['A14','A18','A22'],['A15','A19','A23'],['A16','A20','A24'],
        ['A1','A5','A9'],['A2','A6','A10'],['A3','A7','A11'],['A4','A8','A12'],['A13','A17','A21'],['A14','A18','A22'],['A15','A19','A23'],['A16','A20','A24']
        ]


    #### LABWARE SETUP ####
    ## Plates
    Sample_Plate1 = protocol.load_labware('biorad_96_wellplate_200ul_pcr', 1)
    Sample_Plate2 = protocol.load_labware('biorad_96_wellplate_200ul_pcr', 2)
    Bruker_Plate = protocol.load_labware('bruker_384_wellplate_20ul', 3)

    ## Matrix solution - PCR setup
    MatrixRack = protocol.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul',4) 
    
    #### Load Liquid/ Well Labeling ####
    ## Sample Liquid load
    SampleLiquid = protocol.define_liquid(name = "Sample", description = "Sample matriale for Spotting", display_color = "#FF00F2")
    if Sample_Col <= FirstPlate_Columns:
        Sample_Plate1.load_liquid(wells = Sample_Plate1.wells()[First_Well_Number:(First_Well_Number+Sample_Number)], volume = (10), liquid = SampleLiquid)
    
    elif Sample_Col > FirstPlate_Columns:
        Sample_Plate1.load_liquid(wells = Sample_Plate1.columns()[First_Well_Number:FirstPlate_Columns], volume = (10), liquid = SampleLiquid)
        Sample_Plate2.load_liquid(wells = Sample_Plate2.wells()[0:(Sample_Number-FirstPlate_Columns)], volume = (10), liquid = SampleLiquid)
    
    ## Matrix liquid load
    MatrixLiquid = protocol.define_liquid(name = "Matrix Solution", description = "Matrix Solution for spotting", display_color = "#33FF00")
    MatrixRack.load_liquid(wells = MatrixRack.wells()[0:8], volume = (Sample_Col*1*3*1.25), liquid = MatrixLiquid) #10 % Overage
    


    #### Tip racks ####
    tiprack_20_1 = protocol.load_labware('opentrons_96_filtertiprack_20ul',6)
    tiprack_20_2 = protocol.load_labware('opentrons_96_filtertiprack_20ul',5)
    tiprack_20_3 = protocol.load_labware('opentrons_96_filtertiprack_20ul',8)
    tiprack_20_4 = protocol.load_labware('opentrons_96_filtertiprack_20ul',7)
    tiprack_20_5 = protocol.load_labware('opentrons_96_filtertiprack_20ul',10)
    tiprack_20_6 = protocol.load_labware('opentrons_96_filtertiprack_20ul',11)
    

    #### PIPETTE SETUP ####
    m20 = protocol.load_instrument('p20_multi_gen2', mount = 'left', tip_racks = ([tiprack_20_1,tiprack_20_2,tiprack_20_3,tiprack_20_4,tiprack_20_5,tiprack_20_6]))
    #p20 = protocol.load_instrument("p20_single_gen2", mount = "right")

    ############################### Lab Work Protocol ###############################
    ## The instructions for the robot to execute.
    protocol.comment("STATUS: Spotting begun Begun")
    protocol.set_rail_lights(False)
    

    ## Set flowrate for aspiration & dispension.
    m20.flow_rate.aspirate = 3 ## µL/s - is default 7.6 ## µL/s
    m20.flow_rate.dispense = 3 ## µL/s - is default 7.6 ## µL/s
    
    ## Set movement speed for gantry
    #protocol_api.head_speed(4500)


    ## Spotting
    for i in range(Sample_Col):
        
        ## Select working sample plate, and set the well position ('A' well number)
        if i <= 11:
            Sample_Plate = Sample_Plate1
            Column = i*8
        elif i > 11:
            Sample_Plate = Sample_Plate2 
            Column = (i-12)*8  

        ## Adjust the y-axis pipetting to align from row A to row B. The calling of "B" is currently not possibly for a 384-plate. 4.5 mm is the difference between well centers.
        if i <= 7:
            Position = 0
        if i > 7:
            Position = -4.5 
        
        ## Distribute positions for Sample to Bruker plate
        SpotPosSample = [
            Bruker_Plate.wells_by_name()[Spot_Pattern[i][0]].bottom().move(types.Point(x = 0, y = Position, z = 1.0)), 
            Bruker_Plate.wells_by_name()[Spot_Pattern[i][1]].bottom().move(types.Point(x = 0, y = Position, z = 1.0)), 
            Bruker_Plate.wells_by_name()[Spot_Pattern[i][2]].bottom().move(types.Point(x = 0, y = Position, z = 1.0))
            ]
	
        SpotPosMatrix = [
            Bruker_Plate.wells_by_name()[Spot_Pattern[i][0]].bottom().move(types.Point(x = 0, y = Position, z = 1.2)), 
            Bruker_Plate.wells_by_name()[Spot_Pattern[i][1]].bottom().move(types.Point(x = 0, y = Position, z = 1.2)), 
            Bruker_Plate.wells_by_name()[Spot_Pattern[i][2]].bottom().move(types.Point(x = 0, y = Position, z = 1.2))
            ]

        ## Distribute sample in triplicates
        m20.distribute(volume = 1, source = Sample_Plate.wells()[Column], dest = SpotPosSample, disposal_vol = 1, new_tip = 'once', trash = True )

        ## Add matrix to samples on Bruker plate
        for k in range(3):
            m20.transfer(volume = 1, source = MatrixRack.wells_by_name()['A1'], dest = SpotPosMatrix[k], new_tip = 'always', trash = True)
        
	    ## Shake or empty trash bin to avoid tips stacking too high.             
        if i == 9:
            protocol.pause("Shake trash bin. Press RESUME when ready")	


    ## Spotting completed
    protocol.comment("STATUS: Spotting completed")


    #### Protocol finished ####
    protocol.set_rail_lights(False)
    protocol.comment("STATUS: Protocol Completed.")
