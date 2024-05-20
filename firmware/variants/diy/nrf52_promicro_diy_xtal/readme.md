## Device info

**PCB_Board**: DIY

**MCU**: NRF52840

**MCU_Board**: ProMicro

**LORA_Board**: EByte E22/E220-xxxMM-22S/RA-01SH

**LINK**: [Github](https://github.com/meshtastic/firmware/tree/master/variants/diy/nrf52_promicro_diy_xtal)

## Notes

The same but official contributed as `promicro_diy_mm`

**General**: Custom PCB, using low freq pins for SPI

**Forum**: [Discord](https://discord.com/channels/867578229534359593/1194757507013427250)

**State**:

**Known issues**: 
      - PCB v1.01 has trace errors near Lora Ant wire. Used incorrect footprint for ipex connector.
      - MM modules working unstable on some meshtastic presets (LongFast, LongSlow)
