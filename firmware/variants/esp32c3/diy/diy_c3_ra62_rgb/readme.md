## Device info

<img alt = "diy_c3_ra62" class = "board-img img-thumbnail img-responsive rounded float-end" src="https://raw.githubusercontent.com/mrekin/MeshtasticCustomBoards/main/firmware/variants/diy/diy_c3_ra62/img1.jpg" width="25%">

**PCB_Board**: DIY

**MCU**: ESP32C3

**MCU_Board**: [ESP32C3 SuperMini v2](https://www.nologo.tech/product/esp32/esp32c3SuperMini/esp32C3SuperMini.html) or similar (a lot of them on Ali). <green>Has RGB on pin 8, SDA moved to D0</green>

**LORA_Board**: HT-RA62/RA-01SH

**LINKS**: [Variant](https://github.com/mrekin/MeshtasticCustomBoards/tree/main/firmware/variants/diy/diy_c3_ra62) [Gerber](https://github.com/mrekin/MeshtasticCustomBoards/tree/main/Gerbers/ra62_c3_smini)

## Notes

**General**: Custom PCB

**Forum**: [Discord](https://discord.com/channels/867578229534359593/871539930852130866)

**State**:

**Known issues**: 

- ***ESP32C3*** is power hungry MCU (with BLE/WiFi enabled), at least with Meshtastic FW - so it is not best choise for battery powered devices (regular esp32 mcu is better).
      Initial variant, can be enreached with gps/spi pins, but not very interesting while ble sleep mode not working (other esp32c3 boards has this problem too).
  
- ***ESP32C3*** currently has non working USB CDC (it is has problems wirh arduino platform <=2.0.14). Starting arduino platform 2.0.15 problem is solved and we need wait platformio release with this version support.

          
