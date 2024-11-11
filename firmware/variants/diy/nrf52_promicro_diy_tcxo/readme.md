## Device info

**PCB_Board**: DIY

**MCU**: NRF52840

**MCU_Board**: [ProMicro/SuperMini](https://github.com/joric/nrfmicro/wiki/Alternatives#supermini-nrf52840)

**LORA_Board**: EByte E22/E220-xxxM-22S or other with tcxo ( *>= 2.5.0 also support xtal modules*)

**LINK**: [Github](https://github.com/meshtastic/firmware/tree/master/variants/diy/nrf52_promicro_diy_tcxo)

## Notes

The same but official contributed as `promicro_diy_m`

**General**: Custom PCB, using low freq pins for SPI

**Forum**: [Discord](https://discord.com/channels/867578229534359593/1194757507013427250)

**State**:

**Known issues**: There are lot of DIY PCBs with their props/cons. Some links and additional info [in Nestpebble repo](https://github.com/Nestpebble/NiceRa)

**HowTo**:

        1. Check if bootloader has actual version (read version from files on UF2 mass storage) (version > 0.8)
          - Update bootloader if needed [Bootloader for NiceNano](https://github.com/adafruit/Adafruit_nRF52_Bootloader/releases)
        2. Download selected meshtastic firmware and flash using UF2 mass storage
        3. Use ota.zip and nRF DFU app/nRF Connect app for ota update. "Number of packets" = 8, "request high MTU" =Y , "Keep bond" = Y  settings works for me.
