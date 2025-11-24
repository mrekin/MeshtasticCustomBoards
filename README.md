# MeshtasticCustomBoards

This repo contains custom device (boards) profiles for meshtastic builds (mainly for development purposes)

Builds can be found here(esp32/nrf52/rp2040 variants)

- https://mrekin.duckdns.org/flasher/

Please open issue/PR if you want add board variant to firmware builds.

## Content
* ```/Gerbers``` - Gerber for my boards,  may contain some bugs and not perfect. Just DIY )
* ```/firmware``` - variants for custom builds which not exist in official repo
* ``` build_list* ``` - yaml files with configs for build jobs. Each yaml file related to different firmware source
* ``` /additional_files ``` - some code, used by Jenkins jobs for firmware build

# How to
## Build variants
1. Clone repo
2. Clone meshtastic firmware source (official or fork)
3. Copy *firmware* folder content to source folder (merge)
4. Build as usual (using VSCode or cli)



# Read more:

- https://meshtastic.org
- https://github.com/NanoVHF/Meshtastic-DIY
- https://github.com/Nestpebble/NiceRa
- https://github.com/gargomoma/fakeTec_pcb

| Name            | MCU      | Board                         | Lora Modules            | Link                                                                                            | FW variant                   |
| --------------- | -------- | ----------------------------- | ----------------------- | ----------------------------------------------------------------------------------------------- | ---------------------------- |
| NanoVHF (1.02)  | ESP32    | ESP32 WROOM-32 DevKit 38 pins | E22-XXXM22S,E22-XXXM30S | https://github.com/NanoVHF/Meshtastic-DIY/tree/main/PCB/ESP-32-devkit_EBYTE-E22/Mesh-v1.02-2LCD | meshtastic-diy-v1-rxtx-ru    |
| C3-RA62         | ESP32C3  | ESP32C3-SuperMini             | HT-RA62,RA-01SH         | https://github.com/mrekin/MeshtasticCustomBoards/tree/main/firmware/variants/diy/diy_c3_ra62    | diy-c3-ra62                  |
| CT62 tiny       | ESP32C3  | HT-CT62                       | HT-CT62                 | https://github.com/mrekin/MeshtasticCustomBoards/tree/main/Gerbers/ct62_tiny                    | diy-heltec-ct62-c3-tiny-1_02 |
| E80 promicro    | NRF52840 | ProMicro (NiceNano)           | E80-XXXM2213S           | https://github.com/mrekin/MeshtasticCustomBoards/tree/main/Gerbers/e80_promicro                 | nrf52_promicro_diy_tcxo      |
| FakeTec         | NRF52840 | ProMicro (NiceNano)           | HT-RA62,RA-01SH         | https://github.com/gargomoma/fakeTec_pcb/                                                       | nrf52_promicro_diy_tcxo      |
| MichTastic_Node | NRF52840 | ProMicro (NiceNano)           | E22-XXXM30S             | https://github.com/Hamspiced/MichTastic_Node                                                    | nrf52_promicro_diy_tcxo      |
| NiceRA          | NRF52840 | ProMicro (NiceNano)           | HT-RA62,RA-01SH         | https://github.com/NomDeTom/NiceRa                                                              | nrf52_promicro_diy_tcxo      |
| SlotRa_PCB      | NRF52840 | ProMicro (NiceNano)           | HT-RA62,RA-01SH         | https://github.com/MagnusKos/SlotRa_PCB                                                         | nrf52_promicro_diy_tcxo      |
| WashTastic      | NRF52840 | ProMicro (NiceNano)           | E22-XXXM30S             | https://github.com/valzzu/meshtastic-pcbs/tree/main/WashTastic                                  | WashTastic      |
