/*
  Copyright (c) 2014-2015 Arduino LLC.  All right reserved.
  Copyright (c) 2016 Sandeep Mistry All right reserved.
  Copyright (c) 2018, Adafruit Industries (adafruit.com)

  This library is free software; you can redistribute it and/or
  modify it under the terms of the GNU Lesser General Public
  License as published by the Free Software Foundation; either
  version 2.1 of the License, or (at your option) any later version.
  This library is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
  See the GNU Lesser General Public License for more details.
  You should have received a copy of the GNU Lesser General Public
  License along with this library; if not, write to the Free Software
  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
*/

#ifndef _VARIANT_FEATHER_DIY_
#define _VARIANT_FEATHER_DIY_

/** Master clock frequency */
#define VARIANT_MCK (64000000ul)

//#define USE_LFXO // Board uses 32khz crystal for LF
#define USE_LFRC    // Board uses RC for LF

/*----------------------------------------------------------------------------
 *        Headers
 *----------------------------------------------------------------------------*/

#include "WVariant.h"

#ifdef __cplusplus
extern "C" {
#endif // __cplusplus

// Number of pins defined in PinDescription array
#define PINS_COUNT (48)
#define NUM_DIGITAL_PINS (48)
#define NUM_ANALOG_INPUTS (6)
#define NUM_ANALOG_OUTPUTS (0)

#define WIRE_INTERFACES_COUNT 1

#define PIN_WIRE_SDA (32 + 2) // P0.12 22
#define PIN_WIRE_SCL (32 + 7) // P0.12 23

#define PIN_LED1 (32 +1) // P1.15 3
//#define PIN_LED2 (32 + 10) // P1.10 4

#define LED_BUILTIN PIN_LED1

//#define LED_GREEN PIN_LED2 // Actually red
#define LED_BLUE PIN_LED1

#define LED_STATE_ON 1 // State when LED is litted

//#define BUTTON_PIN (32 + 2) // P1.02 7

/*
 * Serial interfaces
 */
#define PIN_SERIAL1_RX (-1) // P0.24 1
#define PIN_SERIAL1_TX (-1) // P0.25 0

#define PIN_SERIAL2_RX (-1)
#define PIN_SERIAL2_TX (-1)

#define SPI_INTERFACES_COUNT 1

#define PIN_SPI_MISO (32 + 13) // P0.15 24
#define PIN_SPI_MOSI (32 + 11) // P0.13 25
#define PIN_SPI_SCK (0 + 10)  // P0.14 26

//#define SS (32+15)

#define HAS_GPS 0
#undef GPS_RX_PIN
#undef GPS_TX_PIN

#undef LORA_SCK
#undef LORA_MISO
#undef LORA_MOSI
#undef LORA_NSS

#define LORA_DIO0 -1        // a No connect on the SX1262/SX1268 module
#define LORA_RESET (0 + 9) // P1.09 13 // RST for SX1276, and for SX1262/SX1268
#define LORA_DIO1 (0 + 29)   // P0.06 11  // IRQ for SX1262/SX1268
#define LORA_DIO2 (0 + 2)   // P0.08 12  // BUSY for SX1262/SX1268
#define LORA_DIO3           // Not connected on PCB, but internally on the TTGO SX1262/SX1268, if DIO3 is high the TXCO is enabled

#define LORA_SCK PIN_SPI_SCK
#define LORA_MISO PIN_SPI_MISO
#define LORA_MOSI PIN_SPI_MOSI
//#define LORA_NSS 




static const uint8_t SS = (32 + 15); // LORA_CS   P0.31
static const uint8_t MOSI = PIN_SPI_MOSI;
static const uint8_t MISO = PIN_SPI_MISO;
static const uint8_t SCK = PIN_SPI_SCK;

#define LORA_NSS SS

// enables 3.3V periphery like GPS or IO Module
#define PIN_3V3_EN (-1)

#undef USE_EINK

// supported modules list
#define USE_LLCC68
#define USE_SX1262

// common pinouts for SX126X modules
#define SX126X_CS LORA_NSS // NSS for SX126X
#define SX126X_DIO1 LORA_DIO1
#define SX126X_BUSY LORA_DIO2
#define SX126X_RESET LORA_RESET
#define SX126X_RXEN (32 + 6) // P0.27 10
#define SX126X_TXEN (0 + 31) // P0.26 9


#ifdef EBYTE_E22
// Internally the TTGO module hooks the SX126x-DIO2 in to control the TX/RX switch
// (which is the default for the sx1262interface code)
#define SX126X_DIO3_TCXO_VOLTAGE 1.8
#endif

#ifdef __cplusplus
}
#endif

/*----------------------------------------------------------------------------
 *        Arduino objects - C++ only
 *----------------------------------------------------------------------------*/

#endif