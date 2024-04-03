## Device info

**PCB_Board**: DIY

**MCU**: NRF52840

**MCU_Board**: [ProMicro/SuperMini](https://github.com/joric/nrfmicro/wiki/Alternatives#supermini-nrf52840)

**LORA_Board**: EByte E22/E220-xxxM-22S

**LINK**: [Github](https://github.com/mrekin/MeshtasticCustomBoards/tree/main/firmware/variants/diy/promicro_diy_m)

## Notes

**General**: Custom PCB, using low freq pins for SPI

**Forum**: [Discord](https://discord.com/channels/867578229534359593/1194757507013427250)

**State**:

**Known issues**: PCB v1.01 has trace errors near Lora Ant wire. Used incorrect footprint for ipex connector.

**HowTo**: 

        1. Check if bootloader has actual version (read version from files on UF2 mass storage) (version > 0.8)
          - Update bootloader if needed [Bootloader for NiceNano](https://github.com/adafruit/Adafruit_nRF52_Bootloader/releases)
        2. Download selected meshtastic firmware and flash using UF2 mass storage
          
