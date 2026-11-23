# New_Codicum_Workflows
Updated GitHub repository for Codicum work: Opentrons OT-2 protocols for ZooMs peptide
preparation and MALDI-TOF (Bruker MTP) spotting.

## Repository layout

```
New_Codicum_Workflows/
├── *.py              OT-2 protocols (upload directly to the Opentrons App)
├── CustomLabware/    Custom labware definitions (.json) + technical drawings (.pdf)
├── FrozenVersions/   Archived, validated protocol versions
├── SOPs/             Standard operating procedures
├── Templates/        Input templates (CSV/XLSX) for protocols
└── requirements.txt  Python packages for local simulation only
```

## Protocols

| Protocol | Description | Custom labware needed |
|---|---|---|
| `ZooMs_Full.py` | ZooMs peptide digestion and extraction | none |
| `ZooMs_Extraction.py` | ZooMs peptide extraction | `piercetip_96_tiprack_10ul` |
| `ZipTip_TestProtocol.py` | Test protocol for PierceTip 96 tip rack 10 µL (ZipTips) | `piercetip_96_tiprack_10ul` |
| `Spot_PCRPlate_RunningSamples_M20.py` | Multichannel spotting of ZooMs peptide samples onto a Bruker MTP plate | `bruker_384_wellplate_20ul` |
| `Spot_SkirtedPlate_RunningSamples.py` | MS prep, MTP plate (Protocol Designer, skirted plate) | embedded* |
| `Spot_LVLPlate_RunningSamples*.py` | MS prep, MTP plate (Protocol Designer, LVL plate), three working variants | embedded* |
| `Test.py` | Scratch script for testing spot patterns (not a protocol) | none |

\* Protocol Designer exports embed their custom labware (`CUSTOM_LABWARE` at the bottom of the
file), so they run without importing anything. The definitions in `CustomLabware/` are the
same source definitions.

## Custom labware

Before running a protocol that uses custom labware, import the matching `.json` from
`CustomLabware/` in the Opentrons App (**Labware → Import**). You only need to do this once per
computer/robot.

| Definition file | loadName | Used by |
|---|---|---|
| `BrukerPlate.json` | `bruker_384_wellplate_20ul` | Codicum spotting protocols |
| `piercetip_96_tiprack_10ul.json` | `piercetip_96_tiprack_10ul` | ZooMs_Extraction, ZipTip_TestProtocol |
| `piercetip_96_tiprack_100ul.json` | `piercetip_96_tiprack_100ul` | (available) |
| `96afatubetpxplate_96_wellplate_200ul.json` | `96afatubetpxplate_96_wellplate_200ul` | EHI protocols |
| `LVLXSX200_wellplate_200ul.json` | `LVLXSX200_wellplate_200ul` | EHI protocols |
| `LVLLX1000_wellplate_1000ul.json` | `LVLLX1000_wellplate_1000ul` | (available) |
| `lvl_96_wellplate_200ul.json` | `lvl_96_wellplate_200ul` | (available) |
| `lvl_96_wellplate_1000ul.json` | `lvl_96_wellplate_1000ul` | (available) |
| `deepwellreservoir_12channel_21000ul.json` | `deepwellreservoir_12channel_21000ul` | EHI protocols |
| `opentronsrack_15_tuberack_5000ul.json` | `opentronsrack_15_tuberack_5000ul` | EHI protocols |
| `bioplastics_96_aluminumblock_100ul.json` | `bioplastics_96_aluminumblock_100ul` | EHI protocols |
| `custom_24_well_1.5ml.json` | `custom_24_well_1.5ml` | (available) |

The PDFs next to the definitions are the manufacturer drawings and datasheets used to
build them.

## Local simulation (optional)

```bash
pip install -r requirements.txt
opentrons_simulate ZooMs_Extraction.py -L CustomLabware
```

`-L CustomLabware` points the simulator at the custom labware definitions.

## Author
Jonas Lauritsen, University of Copenhagen
