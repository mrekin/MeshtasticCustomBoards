#ifndef Pins_Arduino_h
#define Pins_Arduino_h

#include <stdint.h>
#include <variant.h>

#define USB_VID 0x303a
#define USB_PID 0x1001

// Serial
//static const uint8_t TX = UART_TX;
//static const uint8_t RX = UART_RX;

// Default SPI will be mapped to Radio
static const uint8_t SS = LORA_CS;
static const uint8_t SCK = LORA_SCK;
static const uint8_t MOSI = LORA_MOSI;
static const uint8_t MISO = LORA_MISO;

// The default Wire will be mapped to PMU and RTC
static const uint8_t SCL = I2C_SCL;
static const uint8_t SDA = I2C_SDA;

static const uint8_t A0 = 1;
static const uint8_t A1 = 2;

#endif /* Pins_Arduino_h */
