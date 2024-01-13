#define I2C_SDA 8
#define I2C_SCL 9

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
#define LORA_RESET 3 // RST for SX1276, and for SX1262/SX1268
#define LORA_DIO1 0  // IRQ for SX1262/SX1268
#define LORA_DIO2 10  // BUSY for SX1262/SX1268
#define LORA_DIO3 RADIOLIB_NC    // Not connected on PCB, but internally on the TTGO SX1262/SX1268, if DIO3 is high the TXCO is enabled

#define LORA_SCK 4
#define LORA_MISO 5
#define LORA_MOSI 6
#define LORA_NSS 7

// supported modules list
//#define USE_RF95 // RFM95/SX127x
#define USE_SX1262
//#define USE_SX1268
#define USE_LLCC68

// common pinouts for SX126X modules
#define SX126X_CS 7 // NSS for SX126X
#define SX126X_DIO1 LORA_DIO1
#define SX126X_BUSY LORA_DIO2
#define SX126X_RESET LORA_RESET
//#define SX126X_RXEN RADIOLIB_NC // Defining the RXEN ruins RFSwitching for the E22 900M30S in RadioLib
#define SX126X_RXEN 2 // Defining the RXEN ruins RFSwitching for the E22 900M30S in RadioLib
#define SX126X_TXEN 1

//#define SX126X_DIO3_TCXO_VOLTAGE 1.8
