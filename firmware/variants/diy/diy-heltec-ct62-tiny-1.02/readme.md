## Device info

**PCB_Board**: DIY

**MCU**: ESP32C3

**MCU_Board**: [Heltec CT-62](https://heltec.org/project/ht-ct62/) 

**LORA_Board**: [Heltec CT-62](https://heltec.org/project/ht-ct62/) 

**LINK**: [Github](https://github.com/mrekin/MeshtasticCustomBoards/new/main/firmware/variants/diy/diy-heltec-ct62-tiny-1.02)

## Notes

**General**: Custom PCB

**Forum**: [Discord](https://discord.com/channels/867578229534359593/871539930852130866)

**State**:

**Known issues**: ESP32C3 is power hungry MCU (with BLE/WiFi enabled), at least with Meshtastic FW - so it is not best choise for battery powered devices (regular esp32 mcu is better).
      Initial variant, but not very interesting while ble sleep mode not working (other esp32c3 boards has this problem too). CT-62 has only few free pins, can be interesting only by small/compact size.

          
