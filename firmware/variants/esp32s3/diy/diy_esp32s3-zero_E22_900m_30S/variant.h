// ESP32 S3 Zero Board
// https://www.waveshare.com/wiki/ESP32-S3-Zero?srsltid=AfmBOorEoHDtz4ypjl8b7OYGCoQ3C6y-UPeDjfZrJKqySkAq9t5QIzKT

// Pins for encoder
// 4 - Right
// 5 - Left
// 6 - Select

// There are two display types available: SSD1306 and SH1107. 
// If the display exhibits artifacts on the left side, change the display type to SH1107.

#define I2C_SDA 11 // I2C pins for this board
#define I2C_SCL 12

#define BUTTON_PIN 0 // If defined, this will be used for user button presses
#define BUTTON_NEED_PULLUP
#define PIN_BUZZER 10

// BATERY
#define BATTERY_PIN 1 // A battery voltage measurement pin, voltage divider connected here to measure battery voltage
#define ADC_CHANNEL ADC1_GPIO1_CHANNEL
#define ADC_ATTENUATION ADC_ATTEN_DB_11 // 683 223
#define ADC_MULTIPLIER 2.08
#define EXT_PWR_DETECT 2

// GNSS
#define HAS_GPS 1 // Don't need to set this to 0 to prevent a crash as it doesn't crash if GPS not found, will probe by default 
#define PIN_GPS_EN 9
#define GPS_EN_ACTIVE 1 
#define GPS_UBLOX
#define GPS_TX_PIN 8 // rx 
#define GPS_RX_PIN 7 // tx 
#define GPS_BAUDRATE 38400 
#define GPS_THREAD_INTERVAL 100
#define IDLE_FRAMERATE 1

// NEOPIXEL
#define HAS_NEOPIXEL 1                         // Enable the use of neopixels
#define NEOPIXEL_COUNT 6                     // How many neopixels are connected
#define NEOPIXEL_DATA 13                     // GPIO pin used to send data to the neopixels
#define NEOPIXEL_TYPE (NEO_GRB + NEO_KHZ800) // Type of neopixels in use
#define ENABLE_AMBIENTLIGHTING               // Turn on Ambient Lighting

// LoRa
#define SX126X_CS 18    // EBYTE module's NSS pin // FIXME: rename to SX126X_SS
#define LORA_SCK 38     // EBYTE module's SCK pin
#define LORA_MOSI 39    // EBYTE module's MOSI pin
#define LORA_MISO 40    // EBYTE module's MISO pin
#define SX126X_RESET 41 // EBYTE module's NRST pin
#define SX126X_BUSY 42  // EBYTE module's BUSY pin
#define SX126X_DIO1 45  // EBYTE module's DIO1 pin

#define SX126X_TXEN 3
#define SX126X_RXEN 17

#define USE_SX1262 // E22-900M30S, E22-900M22S, and E22-900MM22S (not E220!) use SX1262
#define USE_SX1268

// Power
#define SX126X_MAX_POWER 22 // SX126xInterface.cpp defaults to 22 if not defined, but here we define it for good practice
#define SX126X_DIO3_TCXO_VOLTAGE 1.8

#define LORA_CS SX126X_CS // FIXME: for some reason both are used in /src

#define LORA_DIO1                                                                                                                \
    SX126X_DIO1 // The old name is used in
                // https://github.com/meshtastic/firmware/blob/7eff5e7bcb2084499b723c5e3846c15ee089e36d/src/sleep.cpp#L298, so
                // must also define the old name
