#################################
### ZipRack Test protocol ###
#################################

## Author Jonas Greve Lauritsen
## Protocol for the combined extraction of DNA and RNA. No nuclease step is active here.

############################

#### Package loading ####
from opentrons import protocol_api, types # type: ignore
from math import *

#### User Input Parameters ###
def add_parameters(parameters):

    ## Number of samples included.
    parameters.add_bool(
        variable_name = "liquid_test",
        display_name = "Test Liquid Transfer",
        description = "Include Liquid Transfer testing.",
        default = False
    )



#### Meta Data ####
metadata = {
    'protocolName': 'ZipTip Test Protocol Peptide Extraction',
    'apiLevel': '2.22',
    'robotType': 'OT-2',    
    'author': 'Jonas Lauritsen <jonas.lauritsen@sund.ku.dk>',
    'description': "Test protocol for PierceTip 96 Tip Rack 10 µL (ZipTips)"}


#### Protocol Script ####
def run(protocol: protocol_api.ProtocolContext):

    #### Loading Protocol Runtime Parameters ####
    LiquidTest = protocol.params.liquid_test


    #### LABWARE SETUP ####
    ## Eppendorf Racks for digestionbuffer and sample tubes
    Sample_Plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr',3)

    ## Zip tip rack - PierceTip 96 Tip
    Ziprack = protocol.load_labware('piercetip_96_tiprack_10ul',1)


    #### PIPETTE SETUP ####
    p200 = protocol.load_instrument('p300_single_gen2', mount = 'left', tip_racks = ([Ziprack]))
    #p20 = protocol.load_instrument("p20_single_gen2", mount = "right")
    
    
    #LiquidTest = False
    if LiquidTest == True:
        WaterTube = protocol.load_labware("opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap",2).wells_by_name()["A1"]



    ############################### Lab Work Protocol ###############################
    ## The instructions for the robot to execute.
    protocol.comment("STATUS: Nucleic Acid Extraction Begun")
    protocol.set_rail_lights(True)


    #### Tip Pick-up Position ####  
    protocol.pause("First: Investigate the tip pick up from Zip Tip rack")

    ## Pick up tip A1
    p200.pick_up_tip(Ziprack.well('A1'))
    protocol.pause("Did the pipette pick up the tip in A1 correctly?")

    ## Return tip A1    
    p200.return_tip()


    ## Pick up tip H12
    p200.pick_up_tip(Ziprack.well('H12'))
    protocol.pause("Did the pipette pick up the tip in H12 correctly?")

    ## Return tip H12   
    p200.return_tip()




    #### Test tip movement ####
    protocol.pause("Second: Investigate the tip placement in accordance to plate")

    ## Pick up tip A1
    p200.pick_up_tip(Ziprack.well("A1"))



    ## Move tip to top of PCR plate A1
    protocol.pause("Move tip to top of PCR plate position A1")
    p200.move_to(Sample_Plate['A1'].top())
    protocol.pause("Is the tip accurately above the PCR plate A1.")
    
    ## Move tip to the sides, one at a time
    well = Sample_Plate.well('A1')
    p200.default_speed = 100  ## default moving speed is 400
   
    ## Edge positiions
    all_4_edges = [[well._from_center_cartesian(x=-1, y=0, z=1), 'left'],
                   [well._from_center_cartesian(x=1, y=0, z=1), 'right'],
                    [well._from_center_cartesian(x=0, y=-1, z=1), 'front'],
                    [well._from_center_cartesian(x=0, y=1, z=1), 'back']
        ]

    ## Move well edges 
    for edge_pos, edge_name in all_4_edges:
        #set_speeds(RATE)
        edge_location = types.Location(point = edge_pos, labware = None)
        p200.move_to(edge_location)
        protocol.pause("If the position is accurate click 'resume.'")



    
    ## Move tip to top of PCR plate H12
    protocol.pause("Move tip to top of PCR plate position A1")
    p200.move_to(Sample_Plate['H12'].top())
    protocol.pause("Is the tip accurately above the PCR plate A1.")
    
    ## Move tip to the sides, one at a time
    well = Sample_Plate.well('H12')
    p200.default_speed = 100  ## default moving speed is 400
   
    ## Edge positiions
    all_4_edges = [[well._from_center_cartesian(x=-1, y=0, z=1), 'left'],
                   [well._from_center_cartesian(x=1, y=0, z=1), 'right'],
                    [well._from_center_cartesian(x=0, y=-1, z=1), 'front'],
                    [well._from_center_cartesian(x=0, y=1, z=1), 'back']
        ]

    ## Move well edges 
    for edge_pos, edge_name in all_4_edges:
        #set_speeds(RATE)
        edge_location = types.Location(point = edge_pos, labware = None)
        p200.move_to(edge_location)
        protocol.pause("If the position is accurate click 'resume.'")

    
    #### Reset p200.default_speed to 400
    p200.default_speed = 400


    ## Liquid aspiration and dispension test
    ## Run if true. Tip already on.

    if LiquidTest == True:
        ## Continue with Liquid test
        protocol.pause("Press 'resume' to continue to liquid transfer test")

        ## Transfer
        p200.transfer(volume = 10, source = WaterTube, dest = Sample_Plate.wells(['A1','B1']), new_tip = "Never")
        protocol.pause("Press 'resume' if A1 and B1 volumes equal were transfered accurately")

        ## Distribute from watertube
        p200.distribute(volume = 2, source = WaterTube, dest = Sample_Plate.wells(['D1','D2','D3','D4','D5']))
        protocol.pause("Press 'resume' if D1 to D5 were transfered accurately in equal fashion")

        ## Distribute from B1
        p200.distribute(volume = 2, source = Sample_Plate.well('B1'), dest = Sample_Plate.wells(['C1','C2','C3','C4','C5']))
        protocol.pause("Press 'resume' if C1 to C5 were transfered accurately in equal fashion. Compare to row D as well.")

        ## Consolidate D1 to D5
        p200.consolidate(volume = 10, source = Sample_Plate.wells(['D1','D2','D3','D4','D5']), dest = Sample_Plate.wells('A2'))
        protocol.pause("Press 'resume' if D1 to D5 were accurately consolidated in A2. Compare to well A1.")

        ## Move pipette to 
        p200.move_to(Sample_Plate['A1'].top(z=10))
        protocol.pause("Check the leftover liquid in tip. Press 'resume' to finish run.")


    ## return Tip
    p200.return_tip()


    #### Protocol finished ####
    protocol.set_rail_lights(False)
    protocol.comment("STATUS: Protocol Completed.")
