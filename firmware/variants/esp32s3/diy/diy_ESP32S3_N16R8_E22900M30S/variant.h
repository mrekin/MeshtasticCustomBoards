//#define HELTEC_TRACKER_V1_X

// I2C
#define I2C_SDA SDA // SDA = 8;
#define I2C_SCL SCL // SCL = 18;
#define HAS_SCREEN 1

// UART
#define UART_TX 43
#define UART_RX 44

// Buzzer
#define PIN_BUZZER 5

// Button
#define BUTTON_PIN 0

#define BATTERY_PIN 1 // A battery voltage measurement pin, voltage divider connected here to measure battery voltage
#define ADC_CHANNEL ADC1_GPIO1_CHANNEL
#define ADC_ATTENUATION ADC_ATTEN_DB_2_5 // lower dB for high resistance voltage divider
#define ADC_MULTIPLIER 4.05 
#define EXT_PWR_DETECT 2

// NEOPIXEL
#define HAS_NEOPIXEL 1                         // Enable the use of neopixels
#define NEOPIXEL_COUNT 6                     // How many neopixels are connected
#define NEOPIXEL_DATA 48                     // GPIO pin used to send data to the neopixels
#define NEOPIXEL_TYPE (NEO_GRB + NEO_KHZ800) // Type of neopixels in use
#define ENABLE_AMBIENTLIGHTING               // Turn on Ambient Lighting

// GPS
#define HAS_GPS 1 // Don't need to set this to 0 to prevent a crash as it doesn't crash if GPS not found, will probe by default
#define PIN_GPS_EN 11
#define GPS_EN_ACTIVE 1
#define GPS_TX_PIN 12 // rx
#define GPS_RX_PIN 13 // tx
#define GPS_BAUDRATE 38400
#define GPS_UBLOX10

// LoRa
#define USE_SX1262
#define SX126X_MAX_POWER 22          // SX126xInterface.cpp defaults to 22 if not defined, but here we define it for good practice
#define SX126X_DIO3_TCXO_VOLTAGE 1.8 // E22 series TCXO reference voltage is 1.8V

#define SX126X_CS 14    // EBYTE module's NSS pin // FIXME: rename to SX126X_SS
#define SX126X_SCK 15   // EBYTE module's SCK pin
#define SX126X_MOSI 38 // EBYTE module's MOSI pin
#define SX126X_MISO 39  // EBYTE module's MISO pin
#define SX126X_RESET 40 // EBYTE module's NRST pin
#define SX126X_BUSY 41 // EBYTE module's BUSY pin
#define SX126X_DIO1 42 // EBYTE module's DIO1 pin
#define SX126X_TXEN 16 // Schematic connects EBYTE module's TXEN pin to MCU
#define SX126X_RXEN 17 // Schematic connects EBYTE module's RXEN pin to MCU

#define LORA_CS SX126X_CS     // Compatibility with variant file configuration structure
#define LORA_SCK SX126X_SCK   // Compatibility with variant file configuration structure
#define LORA_MOSI SX126X_MOSI // Compatibility with variant file configuration structure
#define LORA_MISO SX126X_MISO // Compatibility with variant file configuration structure
#define LORA_DIO1 SX126X_DIO1 // Compatibility with variant file configuration structure
