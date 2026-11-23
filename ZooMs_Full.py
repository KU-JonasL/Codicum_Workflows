#################################
### Nucleic Acids Extraction protocol ###
#################################

## Author Jonas Greve Lauritsen
## Protocol for the combined extraction of DNA and RNA. No nuclease step is active here.

############################

#### Package loading ####
from opentrons import protocol_api, types # type: ignore
from math import *


#### User Input Parameters ###
def add_parameters(parameters):

    ## Extraction, yes or no
    parameters.add_bool(
    variable_name="extraction",
    display_name="Extraction included",
    description = "If true, Extraction is included.",
    default = True
    )

    ## Number of samples included.
    parameters.add_int(
        variable_name = "sample_count",
        display_name = "Sample count",
        description = "Number of input DNA samples.",
        default = 23,
        minimum = 8,
        maximum = 23
    )
    
    ## On deck incubation
    parameters.add_bool(
        variable_name = "on_deck_incubation",
        display_name = "On-Deck Incubation",
        description = "If true, Script performs an On-deck Incubation.",
        default = True
    )

    ## On deck incubation time
    parameters.add_int(
        variable_name = "incubation_time",
        display_name = "Beads Incubation Time (Mins)",
        description = "Time for incubation of sample and bead mix (in minutes).",
        default = 15,
        minimum = 0,
        maximum = 120
    )

    ## Ethanol volume for wash
    parameters.add_float(
        variable_name = "ethanol_volume",
        display_name = "Ethanol Wash Volume (Per wash)",
        description = "Number of input DNA samples.",
        default = 160,
        minimum = 100,
        maximum = 180
    )

    ## Elution volume
    parameters.add_float(
        variable_name = "elution_volume",
        display_name = "Elution Volume (Per sample)",
        description = "Number of input DNA samples.",
        default = 50,
        minimum = 20,
        maximum = 100
    )




#### Meta Data ####
metadata = {
    'protocolName': 'ZooMs Peptide Digestion AND Extraction',
    'apiLevel': '2.22',
    'robotType': 'OT-2',    
    'author': 'Jonas Lauritsen <jonas.lauritsen@sund.ku.dk>',
    'description': "ZooMs peptide sample preparation for MALDI-TOF spotting."}


#### Protocol Script ####
def run(protocol: protocol_api.ProtocolContext):
    
    #### Loading Protocol Runtime Parameters ####
    Sample_Number = protocol.params.sample_count
    Incubation_Time = protocol.params.incubation_time
    Extraction = protocol.params.extraction
    OnDeck_Incubation = protocol.params.on_deck_incubation
    
    #### LABWARE SETUP ####
    ## Smart labware



    ## Eppendorf Racks for digestionbuffer and sample tubes
    BufferRack = protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap',4)
    Sample_Rack1 = protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap',1)
    Sample_Rack2 = protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap',2)
    ConditionSolutionRack = protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap',5)
    WashSolutionRack = protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap',6)



    ## Samples in use on sample rack
    Sample_Plate = Sample_Rack1
    Clean_Plate = Sample_Rack2

    
    ## Selecting output format - default is a PCR wellplate
    Elution_plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr', 3) ## Output plate; selected via 
   

    ## Liquid labeling not added.
    DigestionBufferRack = BufferRack.wells_by_name["A1"]
    TerminationSolutionRack = BufferRack.wells_by_name["A2"]
    ConditionSolutionRack = BufferRack.wells_by_name["A3"]
    WashSolutionRack = BufferRack.wells_by_name["A4"]


    ## Waste ##
    Waste = protocol.load_labware("opentrons_6_tuberack_falcon_50ml_conical",8) ###


    ## Load Liquid/ Well Labeling
    ## Beads
    DigestionBuffer = protocol.define_liquid(name = "DigestionBuffer", description = "Trypsin Digestion Buffer",display_color = "#FF0000")
    TerminationSolution = protocol.define_liquid(name = "TerminationSolution", description = "Termination Solution",display_color = "#D9FF00")
    ConditionSolution = protocol.define_liquid(name = "ConditionSolution", description = "Conditioning Solution",display_color = "#33FF00")
    WashSolution = protocol.define_liquid(name = "WashSolution", description = "Washing Solution Digestion Buffer",display_color = "#0004FF")

    BufferRack.load_liquid(wells = ['A1'], volume = (Sample_Number*76*1.1) , liquid = DigestionBuffer) #10 % Overage
    BufferRack.load_liquid(wells = ['A2'], volume = (Sample_Number*1.5*1.1) , liquid = TerminationSolution) #10 % Overage
    BufferRack.load_liquid(wells = ['A3'], volume = (Sample_Number*100*2*1.1) , liquid = ConditionSolution) #10 % Overage
    BufferRack.load_liquid(wells = ['A4'], volume = (Sample_Number*100*4*1.1) , liquid = WashSolution) #10 % Overage


    #### Tip racks ####
    tiprack_200_1 = protocol.load_labware('opentrons_96_filtertiprack_200ul',9) ## 
    #tiprack_200_2 = protocol.load_labware('opentrons_96_filtertiprack_200ul',8) ## 

    tiprack_20_1 = protocol.load_labware('opentrons_96_filtertiprack_200ul',10) ##
    #tiprack_20_2 = protocol.load_labware('opentrons_96_filtertiprack_200ul',10) ##

    Ziprack = protocol.load_labware('opentrons_96_filtertiprack_200ul',11) ##
    #Ziprack = protocol.loadlabware('ziptip_96rack_200µL')

    #### PIPETTE SETUP ####
    p200 = protocol.load_instrument('p300_single_gen2', mount='left', tip_racks=([tiprack_200_1]))
    p20 = protocol.load_instrument('p10_single', mount = 'right', tip_racks=([tiprack_20_1]))


    ############################### Lab Work Protocol ###############################
    ## The instructions for the robot to execute.
    protocol.comment("STATUS: Nucleic Acid Extraction Begun")
    protocol.set_rail_lights(True)
    
    
    #### Sample material resuspenssion ####
    ## Transfer Trypsin Digestion buffer to samples
    p200.transfer(volume = 76, source = DigestionBufferRack, dest = Sample_Plate, rate = 0.8, new_tip = 'always', mix_after = (5,40))



    #### Incubation settings
    if OnDeck_Incubation == True:
        ## Incubation on deck- 4 hours
        protocol.delay(14400)        
        

    if OnDeck_Incubation == False:
        ## Incubation off deck - 4 hours
        protocol.pause("ACTION: Remove tubes to do off deck incubation") 



    #### Termination Reaction ####
    ## If no extraction
    if Extraction == False:

        ## Spin down tubes
        protocol.pause("ACTION: Spin down samples and re-place them in ")

        ## Add termination solution
        p20.transfer(volume = 1, source = TerminationSolutionRack, dest = Sample_Plate, rate = 0.8, new_tip = 'always', mix_after = (5,40))

        ## Protocol ended
        protocol.comment("Samples Digesition Terminated")



    #### Peptide Extraction ####
    elif Extraction == True:
        
        ## Extraction
        for i in range(Sample_Number):
            
            #### ZipTip preparation
            p200.pick_up_tip()[Ziprack]
            
            ## Tip rinse conditioning solution
            for k in 2:
                p200.aspirate(volume = 100, location = ConditionSolutionRack.wells()[i], rate = 0.7)
                p200.dispense(volume = 100, location = Waste, rate = 0.5)

            ## Tip rinse washing solution
            for k in 2:
                p200.aspirate(volume = 100, location = WashSolutionRack.wells()[i], rate = 0.7)
                p200.dispense(volume = 100, location = Waste, rate = 0.5)



            #### Sample resuspention ####
            ## Note I presume you pick up the volume of the sample????????????????????
            p200.mix(repetitions = 10, volume = 60, location = Sample_Plate.wells()[i], rate = 0.6)
            p200.aspirate(volume = 63, location = Sample_Plate.wells()[i], rate = 0.7)
            p200.dispense(volume = 73, location = Waste, rate = 0.5)



            #### Sample washing ####
            ## Tip rinse conditioning solution
            for k in 2:
                p200.aspirate(volume = 100, location = WashSolutionRack.wells()[i], rate = 0.7)
                p200.dispense(volume = 100, location = Waste, rate = 0.5)


            #### Elution in conditioning solution #### !!! We do not have enough conditioning solution !!!
            p200.aspirate(volume = 5, location = ConditionSolutionRack.wells()[i], rate = 0.7) 
            p200.mix(repetitions = 15, volume = 40, location = ConditionSolutionRack.wells()[i], rate = 0.6)
            p200.aspirate(volume = 45, location = ConditionSolutionRack.wells()[i], rate = 0.7)


            ## Dispense into LVL tube
            p200.dispense(volume = 45, location = Elution_plate, rate = 0.5)


            #### Discard ZipTip ####
            p200.drop_tip()



    #### Protocol finished ####
    protocol.set_rail_lights(False)
    protocol.comment("STATUS: Protocol Completed.")
