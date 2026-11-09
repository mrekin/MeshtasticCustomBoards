## Device info

<img alt="BuildLab Scout" class="board-img img-thumbnail img-responsive rounded float-end" src="https://raw.githubusercontent.com/mrekin/MeshtasticCustomBoards/main/firmware/variants/esp32s3/diy/diy_esp32s3-zero_E22_900m_30S/img1.png" width="25%">

**PCB_Board**: BuildLab Scout, носимая нода в корпусе

**MCU**: ESP32-S3FH4R2 (4 МБ flash, 2 МБ PSRAM)

**MCU_Board**: [ESP32-S3-Zero](https://www.waveshare.com/wiki/ESP32-S3-Zero)

**LORA_Board**: EByte E22-900M30S или E22-400M30S

**GNSS**: u-blox M10 (M10050)

**Power**: 2 × 21700 последовательно (2S), зарядка через отдельный USB-C

**LINKS**: [Variant](https://github.com/mrekin/MeshtasticCustomBoards/tree/main/firmware/variants/esp32s3/diy/diy_esp32s3-zero_E22_900m_30S)

## Notes

**Настройки при первом включении** (чистая память, регион не выбран): мощность 12 дБм (начальное значение), Store & Forward сервер с окном 2 часа. Регион не задаётся: модуль бывает 868 и 433, выбирает пользователь.

**Энкодер**: A=4, B=5, кнопка=6, свой драйвер: каждый щелчок отрабатывается сразу.

**Светодиоды** (6 шт., GPIO13): зелёный: принят пакет и мигание раз в 5 с (слушает эфир), красный: передача, два фиолетовых: есть непрочитанные, синий: GPS ищет, жёлтый: есть фикс. Настройка: меню главного экрана, пункт «LED Settings» (вкл/выкл, индикация сообщений, яркость 1–4). Пункт добавляется патчем SCOUT_HOME_MENU_LEDS.yml.

**Прошивка**: кнопка BOOT не нужна (USB-Serial-JTAG).

**Contacts**: Telegram [@BuildLabDIY](https://t.me/BuildLabDIY)
