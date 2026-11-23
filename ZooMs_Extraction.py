#################################
### Protein Extraction protocol ###
#################################

## Author Jonas Greve Lauritsen
## Protocol for the ZooMS extraction/purification of peptides.

############################

#### Package loading ####
from opentrons import protocol_api, types # type: ignore
from math import *


#### User Input Parameters ###
def add_parameters(parameters):

    ## Number of samples included.
    parameters.add_int(
        variable_name = "sample_count",
        display_name = "Sample count",
        description = "Number of input DNA samples.",
        default = 48,
        minimum = 1,
        maximum = 96
    )
    


#### Meta Data ####
metadata = {
    'protocolName': 'ZooMs Peptide Extraction',
    'apiLevel': '2.22',
    'robotType': 'OT-2',    
    'author': 'Jonas Lauritsen <jonas.lauritsen@sund.ku.dk>',
    'description': "ZooMs peptide extraction."}


#### Protocol Script ####
def run(protocol: protocol_api.ProtocolContext):
    
    #### Loading Protocol Runtime Parameters ####
    Sample_Number = protocol.params.sample_count



    #### LABWARE SETUP ####
    ## Eppendorf Racks for digestionbuffer and sample tubes
    Sample_Plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr',4)
    Elution_plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr', 3)

    ## Buffers ## 
    ConditionSolution = protocol.load_labware('nest_96_wellplate_2ml_deep',1)
    WashSolution = protocol.load_labware('nest_96_wellplate_2ml_deep',2)
    
    ## Waste ##
    WasteRack = protocol.load_labware("opentrons_6_tuberack_falcon_50ml_conical",9) ###
    Waste = WasteRack['A1']
    if Sample_Number > 64 :
        Waste2 = WasteRack['A2']



    #### Load Liquid/ Well Labeling ####
    SampleLiquid = protocol.define_liquid(name = "DigestionBuffer", description = "Trypsin Digestion Buffer", display_color = "#FF0000")
    ConditionSolutionLiquid = protocol.define_liquid(name = "ConditionSolution", description = "Conditioning Solution", display_color = "#33FF00")
    WashSolutionLiquid = protocol.define_liquid(name = "WashSolution", description = "Washing Solution Digestion Buffer", display_color = "#0004FF")
    WasteLiquid = protocol.define_liquid(name = "Waste", description = "Waste", display_color = "#E5FF00")

    Sample_Plate.load_liquid(wells = Sample_Plate.wells()[0:Sample_Number], volume = (75), liquid = SampleLiquid)
    ConditionSolution.load_liquid(wells = ConditionSolution.wells()[0:Sample_Number], volume = (230*1.1), liquid = ConditionSolutionLiquid) #10 % Overage
    WashSolution.load_liquid(wells = WashSolution.wells()[0:Sample_Number], volume = (400*1.1), liquid = WashSolutionLiquid) #10 % Overage
    WasteRack.load_liquid(wells = ['A1'], volume = 1, liquid = WasteLiquid)
    if Sample_Number > 64 :
        WasteRack.load_liquid(wells = ['A2'], volume = 1, liquid = WasteLiquid)



    #### Tip racks ####
    tiprack_200_1 = protocol.load_labware('opentrons_96_filtertiprack_200ul',6) 

    #Ziprack = protocol.load_labware('opentrons_96_filtertiprack_200ul',5) ## Temporary
    Ziprack = protocol.load_labware('piercetip_96_tiprack_10ul',5)

    #### PIPETTE SETUP ####
    p200 = protocol.load_instrument('p300_single_gen2', mount = 'left', tip_racks = ([Ziprack]))
    #p20 = protocol.load_instrument("p20_single_gen2", mount = "right")

    ############################### Lab Work Protocol ###############################
    ## The instructions for the robot to execute.
    protocol.comment("STATUS: Nucleic Acid Extraction Begun")
    protocol.set_rail_lights(True)
    
    
    
    ## Extraction
    for i in range(Sample_Number):
        
        if i > 64 :
            Waste = Waste2
        
        #### ZipTip preparation ####
        ## Pickup Ziptip
        p200.pick_up_tip(Ziprack.wells()[i])

        ## Step 1 - Tip rinse conditioning solution
        for k in range(2):
            p200.aspirate(volume = 100, location = ConditionSolution.wells()[i], rate = 0.7)
            p200.dispense(volume = 100, location = Waste, rate = 0.5)

        ## Step 2 - Tip rinse washing solution
        for k in range(2):
            p200.aspirate(volume = 100, location = WashSolution.wells()[i], rate = 0.7)
            p200.dispense(volume = 100, location = Waste, rate = 0.5)



        #### Sample resuspention ####
        ## Step 3 - Note I presume you pick up the volume of the sample
        p200.mix(repetitions = 10, volume = 73, location = Sample_Plate.wells()[i], rate = 0.5)
        p200.aspirate(volume = 73, location = Sample_Plate.wells()[i], rate = 0.5)
        p200.dispense(volume = 73, location = Waste, rate = 0.5)



        #### Sample washing ####
        ## Step 4 - Tip rinse conditioning solution
        for k in range(2):
            p200.aspirate(volume = 100, location = WashSolution.wells()[i], rate = 0.7)
            p200.dispense(volume = 100, location = Waste, rate = 0.5)


        #### Step 5 - Elution in conditioning solution #### !!! We do not have enough conditioning solution !!!
        p200.aspirate(volume = 5, location = ConditionSolution.wells()[i], rate = 0.7) 
        p200.mix(repetitions = 15, volume = 40, location = ConditionSolution.wells()[i], rate = 0.6)
        p200.aspirate(volume = 45, location = ConditionSolution.wells()[i], rate = 0.7)


        ## Step 6 - Dispense eluant into skirted well plate
        p200.dispense(volume = 45, location = Elution_plate.wells()[i], rate = 0.5)


        #### Discard ZipTip ####
        p200.drop_tip()



    #### Protocol finished ####
    protocol.set_rail_lights(False)
    protocol.comment("STATUS: Protocol Completed.")
