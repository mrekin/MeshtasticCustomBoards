#define I2C_SDA 20
#define I2C_SCL 21

#define BUTTON_PIN 0  // button

#define BATTERY_PIN 2 // A battery voltage measurement pin, voltage divider connected here to measure battery voltage
#define ADC_CHANNEL ADC1_GPIO2_CHANNEL
#define ADC_MULTIPLIER 1.85 
#define EXT_PWR_DETECT 1    // Pin to detect connected external power source for LILYGO® TTGO T-Energy T18 and other DIY boards


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