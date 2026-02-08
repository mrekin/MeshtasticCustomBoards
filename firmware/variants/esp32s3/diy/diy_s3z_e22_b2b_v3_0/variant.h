// I2C LCD
#define I2C_SDA 6          		// I2C pins for LCD                                                                                             
#define I2C_SCL 5				// I2C pins for LCD

// Periphery
#define BUTTON_PIN 0            // If defined, this will be used for user button presses
//#define BUTTON_NEED_PULLUP

// #define LED_POWER 1 // This is a LED_WS2812 not a standard LED
#define HAS_NEOPIXEL            // Enable the use of neopixels
#define NEOPIXEL_COUNT 1        // How many neopixels are connected
#define NEOPIXEL_DATA 21        // gpio pin used to send data to the neopixels
#define NEOPIXEL_TYPE (NEO_GRB + NEO_KHZ800) // type of neopixels in use
#define ENABLE_AMBIENTLIGHTING  // Turn on Ambient Lighting

// LoRa module
#define USE_SX1262
#define USE_SX1268
#define USE_LLCC68

// LORA
#define SX126X_CS 7              // EBYTE module's NSS pin 
#define SX126X_SCK 8             // EBYTE module's SCK pin
#define SX126X_MOSI 9            // EBYTE module's MOSI pin
#define SX126X_MISO 10           // EBYTE module's MISO pin
#define SX126X_RESET 11          // EBYTE module's NRST pin
#define SX126X_BUSY 12           // EBYTE module's BUSY pin
#define SX126X_DIO1 13           // EBYTE module's DIO1/IRQ pin
//#define SX126X_DIO2_AS_RF_SWITCH
#define SX126X_DIO3_TCXO_VOLTAGE 1.8
#define SX126X_TXEN 3 			 // Schematic connects EBYTE module's TXEN pin to MCU
#define SX126X_RXEN 4 			 // Schematic connects EBYTE module's RXEN pin to MCU
#define SX126X_MAX_POWER 22     

// SPI
#define LORA_CS SX126X_CS        // Compatibility with variant file configuration structure
#define LORA_SCK SX126X_SCK      // Compatibility with variant file configuration structure
#define LORA_MOSI SX126X_MOSI    // Compatibility with variant file configuration structure
#define LORA_MISO SX126X_MISO    // Compatibility with variant file configuration structure
#define LORA_DIO1 SX126X_DIO1    // Compatibility with variant file configuration structure
