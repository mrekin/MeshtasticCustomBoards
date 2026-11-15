// BuildLab Frost Node: ESP32-S3 N16R8 + EByte E22-900M30S (or E22P-868M30S), LTO cell, INA3221 power monitor.
// The builds differ in the INA3221 shunt on CH3 and the LoRa module (see platformio.ini).

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

// Power: GPIO1 and GPIO2 are not connected, so there is no BATTERY_PIN and no EXT_PWR_DETECT.
// The LTO cell is measured by the INA3221 (0x42): CH1 solar panel, CH2 charger output to the cell
// and load, CH3 load from the cell. variant.cpp sets power.device_battery_ina_address once.
#define INA3221_SHUNT_R_CH1 0.01f
#define INA3221_SHUNT_R_CH2 0.01f // CH3 is set per build in platformio.ini
#define INA3221_BAT_CH INA3221_CH2
// CH2 current is positive while the cell charges and negative while it discharges.
#define INA_CHARGING_DETECTION_INVERT

// One LTO cell. Resting voltage over a full discharge of a Frost Node: 2.50 V about 9 h after a full
// charge, 1.90 V where the cell protection cuts off.
#define OCV_ARRAY 2500, 2400, 2320, 2240, 2200, 2170, 2150, 2130, 2110, 2070, 1900

// NEOPIXEL
#define HAS_NEOPIXEL 1                         // Enable the use of neopixels
#define NEOPIXEL_COUNT 6                       // How many neopixels are connected
#define NEOPIXEL_DATA 48                       // GPIO pin used to send data to the neopixels
#define NEOPIXEL_TYPE (NEO_GRB + NEO_KHZ800)   // Type of neopixels in use
#define ENABLE_AMBIENTLIGHTING                 // Turn on Ambient Lighting

// GPS: no GNSS module on this board
#define HAS_GPS 0
#undef GPS_RX_PIN
#undef GPS_TX_PIN

// LoRa
#define USE_SX1262
#define USE_SX1268
#define SX126X_MAX_POWER 22          // SX126xInterface.cpp defaults to 22 if not defined, but here we define it for good practice
#define SX126X_DIO3_TCXO_VOLTAGE 1.8 // E22 series TCXO reference voltage is 1.8V

#define SX126X_CS 14    // EBYTE module's NSS pin
#define SX126X_SCK 15   // EBYTE module's SCK pin
#define SX126X_MOSI 38  // EBYTE module's MOSI pin
#define SX126X_MISO 39  // EBYTE module's MISO pin
#define SX126X_RESET 40 // EBYTE module's NRST pin
#define SX126X_BUSY 41  // EBYTE module's BUSY pin
#define SX126X_DIO1 42  // EBYTE module's DIO1 pin
#ifdef BUILDLAB_FROST_E22P
// E22P-868M30S: module pin 6 (GPIO17) is EN for the RF front end and must stay HIGH in RX and TX;
// pin 7 (GPIO16) is T/R CTRL, HIGH = TX. With no RXEN, RadioLib drives it HIGH in TX and LOW in RX.
#define SX126X_ANT_SW 17
#define SX126X_TXEN 16
#else
#define SX126X_TXEN 16  // Schematic connects EBYTE module's TXEN pin to MCU
#define SX126X_RXEN 17  // Schematic connects EBYTE module's RXEN pin to MCU
#endif

#define LORA_CS SX126X_CS     // Compatibility with variant file configuration structure
#define LORA_SCK SX126X_SCK   // Compatibility with variant file configuration structure
#define LORA_MOSI SX126X_MOSI // Compatibility with variant file configuration structure
#define LORA_MISO SX126X_MISO // Compatibility with variant file configuration structure
#define LORA_DIO1 SX126X_DIO1 // Compatibility with variant file configuration structure
