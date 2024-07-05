## Device info

<img alt = "e73_slim pcb v1" class = "board-img img-thumbnail img-responsive rounded float-end" src="https://raw.githubusercontent.com/mrekin/MeshtasticCustomBoards/main/firmware/variants/diy/e73_slim/e73_slim_v1.png" width="20%">

**PCB_Board**: DIY

**MCU**: NRF52840

**MCU_Board**: [E73-2G4M08S1C](https://www.cdebyte.com/products/E73-2G4M08S1C)

**LORA_Board**: HT-RA62/RA-01SH

**LINK**: [Github](https://github.com/mrekin/MeshtasticCustomBoards/tree/main/firmware/variants/diy/e73_slim)

## Notes

**General**: Custom PCB, current - v1

**Forum**: [Discord](https://discord.com/channels/867578229534359593/1194757507013427250)

**State**:

**Known issues**:
- PCB v1 has trace errors (VBS pin not connected). Also PCB doesn't contain status led, battery switch. Battery connect can't be used - incorrect positioning.
- ~~LongFast preset works with troubles, i don't know reason right now..~~ PCB antenna is piece of.. With external antenna no problems with LongFast. The same problem with tiny board: promicro + e22-900mm22s
- BLE range not very big (~ 3 meters), possible reason is e73 position on pcb.

**HowTo**: 

        1. Check if bootloader has actual version (read version from files on UF2 mass storage) (version > 0.8)
          - Flash bootloader if needed [how to flash bootloader](https://github.com/joric/nrfmicro/wiki/Bootloader). I use bluepill for flashing.
          - Update bootloader if needed [Bootloader for NiceNano](https://github.com/adafruit/Adafruit_nRF52_Bootloader/releases)
        2. Download selected meshtastic firmware and flash using UF2 mass storage
          
