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

#ifndef _VARIANT_PROMICRO_DIY_
#define _VARIANT_PROMICRO_DIY_

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

/*
 * Analog pins
 */
#define PIN_A4 (0 + 4) // P0.04 Battery ADC
#define BATTERY_PIN PIN_A4
static const uint8_t A4 = PIN_A4;
#define ADC_RESOLUTION 14
#define BATTERY_SENSE_RESOLUTION_BITS 12
#define BATTERY_SENSE_RESOLUTION 4096.0
// Definition of milliVolt per LSB => 3.0V ADC range and 12-bit ADC resolution = 3000mV/4096
#define VBAT_MV_PER_LSB (0.73242188F)
// Voltage divider value => 1.5M + 1M voltage divider on VBAT = (1.5M / (1M + 1.5M))
#define VBAT_DIVIDER (0.4F)
// Compensation factor for the VBAT divider
#define VBAT_DIVIDER_COMP (1.73)
// Fixed calculation of milliVolt from compensation value
#define REAL_VBAT_MV_PER_LSB (VBAT_DIVIDER_COMP * VBAT_MV_PER_LSB)
#undef AREF_VOLTAGE
#define AREF_VOLTAGE 3.0
#define VBAT_AR_INTERNAL AR_INTERNAL_3_0
#define ADC_MULTIPLIER VBAT_DIVIDER_COMP // REAL_VBAT_MV_PER_LSB
#define VBAT_RAW_TO_SCALED(x) (REAL_VBAT_MV_PER_LSB * x)

//WIRE IC
#define WIRE_INTERFACES_COUNT 1

//IIC
#define PIN_WIRE_SDA (32 + 4) // P1.04
#define PIN_WIRE_SCL (0 + 11) // P0.11

//LED
#define PIN_LED1 (0 +15) // P0.15
#define LED_BUILTIN PIN_LED1
// Actually red
#define LED_BLUE PIN_LED1
#define LED_STATE_ON 1 // State when LED is litted

//Button
#define BUTTON_PIN (32 + 0) // P1.00

/*
 * Serial interfaces
 */
#define PIN_SERIAL1_RX (0 + 6) // P0.06
#define PIN_SERIAL1_TX (0 + 8) // P0.08

#define PIN_SERIAL2_RX (-1)
#define PIN_SERIAL2_TX (-1)

#define SPI_INTERFACES_COUNT 1

#define PIN_SPI_MISO (0 + 2) // P0.02
#define PIN_SPI_MOSI (32 + 15) // P1.15
#define PIN_SPI_SCK (32 + 11)  // P1.11

//#define SS (32+15)

#define HAS_GPS 0
#undef GPS_RX_PIN
#undef GPS_TX_PIN


//LORA MODULES
#define USE_LLCC68
#define USE_SX1262

//LORA CONFIG
#define SX126X_CS (32 + 13) // P1.13 FIXME - we really should define LORA_CS instead
#define SX126X_DIO1 (0 + 10) // P0.10 IRQ
// Note DIO2 is attached internally to the module to an analog switch for TX/RX switching
// #define SX1262_DIO3 (0 + 21)
// This is used as an *output* from the sx1262 and connected internally to power the tcxo, do not drive from the main CPU?
#define SX126X_BUSY (0 + 29) //P0.29
#define SX126X_RESET (0 + 9) //P0.09
#define SX126X_RXEN (0 + 31) // P0.31
#define SX126X_TXEN (32 + 6) // P1.06

//  DIO2 controlls an antenna switch and the TCXO voltage is controlled by DIO3
//#define SX126X_DIO2_AS_RF_SWITCH
//#define SX126X_DIO3_TCXO_VOLTAGE 1.8


//#define LORA_DIO0 -1        // a No connect on the SX1262/SX1268 module
//#define LORA_RESET (0 + 9) // P1.09 13 // RST for SX1276, and for SX1262/SX1268
//#define LORA_DIO1 (0 + 29)   // P0.06 11  // IRQ for SX1262/SX1268
//#define LORA_DIO2 (0 + 2)   // P0.08 12  // BUSY for SX1262/SX1268
//#define LORA_DIO3           // Not connected on PCB, but internally on the TTGO SX1262/SX1268, if DIO3 is high the TXCO is enabled

//#define LORA_SCK PIN_SPI_SCK
//#define LORA_MISO PIN_SPI_MISO
//#define LORA_MOSI PIN_SPI_MOSI
//#define LORA_NSS 




//static const uint8_t SS = (32 + 15); // LORA_CS   P0.31
//static const uint8_t MOSI = PIN_SPI_MOSI;
//static const uint8_t MISO = PIN_SPI_MISO;
//static const uint8_t SCK = PIN_SPI_SCK;

//#define LORA_NSS SS

// enables 3.3V periphery like GPS or IO Module
#define PIN_3V3_EN (0 + 13) //P0.13

//#undef USE_EINK

// supported modules list


// common pinouts for SX126X modules
//#define SX126X_CS LORA_NSS // NSS for SX126X
//#define SX126X_DIO1 LORA_DIO1
//#define SX126X_BUSY LORA_DIO2
//#define SX126X_RESET LORA_RESET
//#define SX126X_RXEN (32 + 6) // P0.27 10
//#define SX126X_TXEN (0 + 31) // P0.26 9


//#ifdef EBYTE_E22
// Internally the TTGO module hooks the SX126x-DIO2 in to control the TX/RX switch
// (which is the default for the sx1262interface code)
//#define SX126X_DIO3_TCXO_VOLTAGE 1.8
//#endif

#ifdef __cplusplus
}
#endif

/*----------------------------------------------------------------------------
 *        Arduino objects - C++ only
 *----------------------------------------------------------------------------*/

#endif