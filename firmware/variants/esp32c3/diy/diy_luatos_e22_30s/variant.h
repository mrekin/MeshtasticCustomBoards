// ESP32 C3 LuatOS Board
// https://wiki.luatos.org/chips/esp32c3/board.html

// Please!!! In large networks use Device Role - CLIENT_MUTE 

// Pins for encoder
// Pin A: 4 - Right
// Pin B: 18 - Left
// Pin Press: 9 - Select

#define LOW_MEMORY_MODE 1

// I2C LCD
#define HAS_SCREEN 1
#define I2C_SDA 0            	// I2C pins for LCD                                                                                             
#define I2C_SCL 19				// I2C pins for LCD

#define PIN_BUZZER 12

// BATTERY
// Two Li-Ion cells connected in series are used
// IP2326 can be used for fast charging
#define BATTERY_PIN 1 			// A battery voltage measurement pin, voltage divider connected here to measure battery voltage
#define ADC_CHANNEL ADC1_GPIO1_CHANNEL
#define ADC_ATTENUATION ADC_ATTEN_DB_11 // 683 223 (680k and 220k)
#define ADC_MULTIPLIER 2.09

//LED
#define HAS_NEOPIXEL            // Enable the use of neopixels
#define NEOPIXEL_COUNT 6        // How many neopixels are connected
#define NEOPIXEL_DATA 8         // gpio pin used to send data to the neopixels
#define NEOPIXEL_TYPE (NEO_GRB + NEO_KHZ800) // type of neopixels in use
#define ENABLE_AMBIENTLIGHTING  // Turn on Ambient Lighting

//GPS
#define HAS_GPS 0
#undef GPS_RX_PIN
#undef GPS_TX_PIN

// LoRa module
#define USE_SX1262
#define USE_SX1268
#define USE_LLCC68

// LORA
#define SX126X_CS 5              // EBYTE module's NSS pin 
#define SX126X_SCK 11            // EBYTE module's SCK pin
#define SX126X_MOSI 7            // EBYTE module's MOSI pin
#define SX126X_MISO 6            // EBYTE module's MISO pin
#define SX126X_RESET 10          // EBYTE module's NRST pin
#define SX126X_BUSY 3            // EBYTE module's BUSY pin
#define SX126X_DIO1 2            // EBYTE module's DIO1/IRQ pin
#define SX126X_DIO2_AS_RF_SWITCH
#define SX126X_TXEN RADIOLIB_NC  // Schematic connects EBYTE module's TXEN pin to MCU
#define SX126X_RXEN 13			 // Schematic connects EBYTE module's RXEN pin to MCU
#define SX126X_MAX_POWER 22     
#define SX126X_DIO3_TCXO_VOLTAGE 1.8

// SPI
#define LORA_CS SX126X_CS        // Compatibility with variant file configuration structure
#define LORA_SCK SX126X_SCK      // Compatibility with variant file configuration structure
#define LORA_MOSI SX126X_MOSI    // Compatibility with variant file configuration structure
#define LORA_MISO SX126X_MISO    // Compatibility with variant file configuration structure
#define LORA_DIO1 SX126X_DIO1    // Compatibility with variant file configuration structure
