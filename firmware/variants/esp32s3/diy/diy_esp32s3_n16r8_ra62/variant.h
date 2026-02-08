// I2C OLED
#define USE_SSD1306
#define I2C_SDA 8 							 // I2C pins for LCD
#define I2C_SCL 9 							 // I2C pins for LCD

// Periphery

//LED AMBIENTLIGHTING
// #define LED_POWER 38     					 // This is a RGB LED not a standard LED
#define HAS_NEOPIXEL                		 // Enable the use of neopixels
#define NEOPIXEL_COUNT 1                     // How many neopixels are connected
#define NEOPIXEL_DATA 48                     // gpio pin used to send data to the neopixels
#define NEOPIXEL_TYPE (NEO_GRB + NEO_KHZ800) // type of neopixels in use
#define ENABLE_AMBIENTLIGHTING  

// Battary voltmeter
#define BATTERY_PIN 1 						 // A battery voltage measurement pin, voltage divider connected here to measure battery voltage
#define ADC_CHANNEL ADC1_GPIO1_CHANNEL
#define ADC_ATTENUATION ADC_ATTEN_DB_2_5 	 // lower dB for high resistance voltage divider
#define ADC_MULTIPLIER 4.9 * 1.045

// "FUNK" button
#define BUTTON_PIN 0 						 // This is the BOOT button and FUNC button
#define BUTTON_NEED_PULLUP

// LoRa module
#define USE_SX1262
#define USE_SX1268

// LORA
#define SX126X_CS 10              			 // EBYTE module's NSS pin 
#define SX126X_MOSI 11            			 // EBYTE module's MOSI pin
#define SX126X_MISO 13           			 // EBYTE module's MISO pin
#define SX126X_SCK 12            			 // EBYTE module's SCK pin
#define SX126X_BUSY 14            			 // EBYTE module's BUSY pin
#define SX126X_RESET 21           			 // EBYTE module's NRST pin
#define SX126X_DIO1 20			             // EBYTE module's DIO1/IRQ pin
#define SX126X_DIO2_AS_RF_SWITCH			 // Switch RX/TX for RA-62
#define SX126X_TXEN RADIOLIB_NC  			 // Schematic connects EBYTE module's TXEN pin to MCU, no for RA-62
#define SX126X_RXEN RADIOLIB_NC  			 // Schematic connects EBYTE module's RXEN pin to MCU, no for RA-62
#define SX126X_MAX_POWER 22     
#define SX126X_DIO3_TCXO_VOLTAGE 1.8

// SPI
#define LORA_CS SX126X_CS                    // Compatibility with variant file configuration structure
#define LORA_SCK SX126X_SCK                  // Compatibility with variant file configuration structure
#define LORA_MOSI SX126X_MOSI                // Compatibility with variant file configuration structure
#define LORA_MISO SX126X_MISO                // Compatibility with variant file configuration structure
#define LORA_DIO1 SX126X_DIO1                // Compatibility with variant file configuration structure

