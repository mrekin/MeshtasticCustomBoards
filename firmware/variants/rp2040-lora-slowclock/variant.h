// #define RADIOLIB_CUSTOM_ARDUINO 1
// #define RADIOLIB_TONE_UNSUPPORTED 1
// #define RADIOLIB_SOFTWARE_SERIAL_UNSUPPORTED 1

#define ARDUINO_ARCH_AVR

#define RP2040_SLOW_CLOCK

#ifdef RP2040_SLOW_CLOCK
// Redefine UART1/Serial2 serial log output to avoid collision with UART0.
#define SERIAL2_TX 4
#define SERIAL2_RX 5

// Reroute log output in SensorLib when USB is not available
#define log_e(...) Serial2.printf(__VA_ARGS__)
#define log_i(...) Serial2.printf(__VA_ARGS__)
#define log_d(...) Serial2.printf(__VA_ARGS__)
#endif

// #define USE_SH1106 1

// Recommended I2C0 pins:
// SDA = 8
// SCL = 9

#define EXT_NOTIFY_OUT 22
#undef BUTTON_PIN // Pin 17 used for antenna switching via DIO4

#define LED_PIN PIN_LED

// #define BATTERY_PIN 26
//  ratio of voltage divider = 3.0 (R17=200k, R18=100k)
// #define ADC_MULTIPLIER 3.1 // 3.0 + a bit for being optimistic

#define USE_SX1262

#undef LORA_SCK
#undef LORA_MISO
#undef LORA_MOSI
#undef LORA_CS

// https://www.waveshare.com/rp2040-lora.htm
// https://www.waveshare.com/img/devkit/RP2040-LoRa-HF/RP2040-LoRa-HF-details-11.jpg
#define LORA_SCK 14  // 10
#define LORA_MISO 24 // 12
#define LORA_MOSI 15 // 11
#define LORA_CS 13   // 3

#define LORA_DIO0 RADIOLIB_NC // No GPIO connection
#define LORA_RESET 23         // GPIO23
#define LORA_BUSY 18          // GPIO18
#define LORA_DIO1 16          // GPIO16
#define LORA_DIO2 RADIOLIB_NC // Antenna switching, no GPIO connection
#define LORA_DIO3 RADIOLIB_NC // No GPIO connection
#define LORA_DIO4 17          // GPIO17

// On rp2040-lora board the antenna switch is wired and works with complementary-pin control logic.
// See PE4259 datasheet page 4

#ifdef USE_SX1262
#define SX126X_CS LORA_CS
#define SX126X_DIO1 LORA_DIO1
#define SX126X_BUSY LORA_BUSY
#define SX126X_RESET LORA_RESET
#define SX126X_DIO2_AS_RF_SWITCH // Antenna switch CTRL
#define SX126X_RXEN LORA_DIO4    // Antenna switch !CTRL via GPIO17
// #define SX126X_DIO3_TCXO_VOLTAGE 1.8
#endif