#ifndef Pins_Arduino_h
#define Pins_Arduino_h

#include <stdint.h>

#define USB_VID 0x303a
#define USB_PID 0x1001

//#define EXTERNAL_NUM_INTERRUPTS 22
//#define NUM_DIGITAL_PINS 22
//#define NUM_ANALOG_INPUTS 6

//#define analogInputToDigitalPin(p) (((p) < NUM_ANALOG_INPUTS) ? (esp32_adc2gpio[(p)]) : -1)
//#define digitalPinToInterrupt(p) (((p) < NUM_DIGITAL_PINS) ? (p) : -1)
//#define digitalPinHasPWM(p) (p < EXTERNAL_NUM_INTERRUPTS)

static const uint8_t TX = -1;
static const uint8_t RX = -1;

static const uint8_t SDA = 20;
static const uint8_t SCL = 21;

static const uint8_t SS = 8;
static const uint8_t MOSI = 7;
static const uint8_t MISO = 6;
static const uint8_t SCK = 10;

static const uint8_t A0 = 0;
static const uint8_t A1 = 1;
static const uint8_t A2 = 2;
static const uint8_t A3 = 3;
static const uint8_t A4 = 4;
static const uint8_t A5 = 5;

#endif /* Pins_Arduino_h */