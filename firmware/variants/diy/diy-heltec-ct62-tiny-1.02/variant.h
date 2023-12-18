#define I2C_SDA 20
#define I2C_SCL 21

//#define BUTTON_PIN  // button
//#define BUTTON_NEED_PULLUP

//#define HAS_SCREEN 0
#define HAS_GPS 0
#undef GPS_RX_PIN
#undef GPS_TX_PIN

#undef LORA_SCK
#undef LORA_MISO
#undef LORA_MOSI
#undef LORA_NSS


#define LORA_DIO0 RADIOLIB_NC   // a No connect on the SX1262/SX1268 module
#define LORA_RESET 5 // RST for SX1276, and for SX1262/SX1268
#define LORA_DIO1 3  // IRQ for SX1262/SX1268
#define LORA_DIO2 4  // BUSY for SX1262/SX1268
#define LORA_DIO3 RADIOLIB_NC    // Not connected on PCB, but internally on the TTGO SX1262/SX1268, if DIO3 is high the TXCO is enabled

#define LORA_SCK 10
#define LORA_MISO 6
#define LORA_MOSI 7
#define LORA_NSS 8

// supported modules list
//#define USE_RF95 // RFM95/SX127x
#define USE_SX1262
//#define USE_SX1268
//#define USE_LLCC68

// common pinouts for SX126X modules
#define SX126X_CS 8 // NSS for SX126X
#define SX126X_DIO1 LORA_DIO1
#define SX126X_BUSY LORA_DIO2
#define SX126X_RESET LORA_RESET
//#define SX126X_RXEN RADIOLIB_NC // Defining the RXEN ruins RFSwitching for the E22 900M30S in RadioLib
#define SX126X_RXEN RADIOLIB_NC // Defining the RXEN ruins RFSwitching for the E22 900M30S in RadioLib
#define SX126X_TXEN RADIOLIB_NC

#define SX126X_DIO3_TCXO_VOLTAGE 1.8

#define SX126X_DIO2_AS_RF_SWITCH
// Adafruit RFM95W OK
// https://www.adafruit.com/product/3072
//#define USE_RF95
//#define LORA_SCK 4
//#define LORA_MISO 5
//#define LORA_MOSI 6
//#define LORA_NSS 7
//#define LORA_DIO0 10
//#define LORA_RESET 8
//#define LORA_DIO1 RADIOLIB_NC
//#define LORA_DIO2 RADIOLIB_NC

// WaveShare Core1262-868M OK
// https://www.waveshare.com/wiki/Core1262-868M
//#define USE_SX1262
//#define LORA_SCK 4
//#define LORA_MISO 5
//#define LORA_MOSI 6
//#define LORA_NSS 7
//#define LORA_DIO0 RADIOLIB_NC
//#define LORA_RESET 8
//#define LORA_DIO1 10
//#define LORA_DIO2 RADIOLIB_NC
//#define LORA_BUSY 18
//#define SX126X_CS LORA_NSS
//#define SX126X_DIO1 LORA_DIO1
//#define SX126X_BUSY LORA_BUSY
//#define SX126X_RESET LORA_RESET
//#define SX126X_E22

// SX128X 2.4 Ghz LoRa module Not OK - RadioLib issue ? still to confirm
//#define USE_SX1280
//#define LORA_SCK 4
//#define LORA_MISO 5
//#define LORA_MOSI 6
//#define LORA_NSS 7
//#define LORA_DIO0 -1
//#define LORA_DIO1 10
//#define LORA_DIO2 21
//#define LORA_RESET 8
//#define LORA_BUSY 1
//#define SX128X_CS LORA_NSS
//#define SX128X_DIO1 LORA_DIO1
//#define SX128X_BUSY LORA_BUSY
//#define SX128X_RESET LORA_RESET
//#define SX128X_MAX_POWER 10

// Not yet tested
//#define USE_EINK
//#define PIN_EINK_EN   -1  // N/C
//#define PIN_EINK_CS   9   // EPD_CS
//#define PIN_EINK_BUSY 18  // EPD_BUSY
//#define PIN_EINK_DC   19  // EPD_D/C
//#define PIN_EINK_RES  -1  // Connected but not needed
//#define PIN_EINK_SCLK 4   // EPD_SCLK
//#define PIN_EINK_MOSI 6   // EPD_MOSI