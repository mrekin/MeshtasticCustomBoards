## Device info

**PCB_Board**: DIY

**MCU**: ESP32

**MCU_Board**: ESP-WROOM-32 DEVKIT [1.02](https://github.com/NanoVHF/Meshtastic-DIY/tree/main/PCB/ESP-32-devkit_EBYTE-E22/Mesh-v1.02-2LCD-FreePins)

**LORA_Board**: EByte E22/E220-xxxM-22/30S 

**LINK**: [Github](https://github.com/mrekin/MeshtasticCustomBoards/new/main/firmware/variants/diy/v1_rxtx)

## Notes

Current diy_v1 variant uses dio2 as RF switch, but highly available pcbs has rxen/txen traces and doesn't has dio2 circuit. This causes problem when PA in 30s modules doesn't work.
So this variant use rxen/txen pins instead.

**General**: Custom PCB

**Forum**: 

**State**:

**Known issues**: 

**HowTo**:
