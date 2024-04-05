## Device info

**PCB_Board**: DIY

**MCU**: ESP32C3

**MCU_Board**: [ESP32C3 SuperMini](https://www.nologo.tech/product/esp32/esp32c3SuperMini/esp32C3SuperMini.html) or similar (a lot of them on Ali)

**LORA_Board**: EByte E22/E220-xxxMM-22S

**LINK**: [Github](https://github.com/mrekin/MeshtasticCustomBoards/tree/main/firmware/variants/diy/diy_nano_c3)

## Notes

**General**: Custom PCB

**Forum**: [Discord](https://discord.com/channels/867578229534359593/1194757507013427250)

**State**:

**Known issues**: ESP32C3 is power hungry MCU (with BLE/WiFi enabled), at least with Meshtastic FW - so it is not best choise for battery powered devices (regular esp32 mcu is better).
      Initial variant, can be enreached with gps/spi pins, but not very interesting while ble sleep mode not working (other esp32c3 boards has this problem too).

          
