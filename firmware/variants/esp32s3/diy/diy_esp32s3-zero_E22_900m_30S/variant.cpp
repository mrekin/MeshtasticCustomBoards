// BuildLab Scout: board defaults for a fresh configuration.
//
// Applied once, on the first boot after flashing a clean device or after a factory reset
// (the region is still unset). A device that was already configured is left alone.
// The marker file lives in /prefs, which a factory reset removes, so defaults come back then.

#include "configuration.h"
#include "FSCommon.h"
#include "NodeDB.h"
#include "SPILock.h"
#include "main.h"

#ifdef FSCom

static const char *defaultsMarker = "/prefs/board_defaults";

void lateInitVariant()
{
    spiLock->lock();
    bool applied = FSCom.exists(defaultsMarker);
    spiLock->unlock();
    if (applied)
        return;

    if (config.lora.region == meshtastic_Config_LoRaConfig_RegionCode_UNSET) {
        LOG_INFO("Scout: apply board defaults");

        config.lora.tx_power = SCOUT_DEFAULT_TX_POWER;

        moduleConfig.canned_message.rotary1_enabled = true;
        moduleConfig.canned_message.inputbroker_pin_a = SCOUT_ENCODER_PIN_A;
        moduleConfig.canned_message.inputbroker_pin_b = SCOUT_ENCODER_PIN_B;
        moduleConfig.canned_message.inputbroker_pin_press = SCOUT_ENCODER_PIN_PRESS;
        moduleConfig.canned_message.inputbroker_event_cw = meshtastic_ModuleConfig_CannedMessageConfig_InputEventChar_RIGHT;
        moduleConfig.canned_message.inputbroker_event_ccw = meshtastic_ModuleConfig_CannedMessageConfig_InputEventChar_LEFT;
        moduleConfig.canned_message.inputbroker_event_press = meshtastic_ModuleConfig_CannedMessageConfig_InputEventChar_SELECT;

        moduleConfig.store_forward.enabled = true;
        moduleConfig.store_forward.is_server = true;
        moduleConfig.store_forward.heartbeat = false;
        moduleConfig.store_forward.history_return_window = SCOUT_SF_WINDOW_MIN;

        nodeDB->saveToDisk(SEGMENT_CONFIG | SEGMENT_MODULECONFIG);
        // Encoder, Store & Forward and radio power are set up before this hook runs
        rebootAtMsec = millis() + 2000;
    }

    spiLock->lock();
    auto f = FSCom.open(defaultsMarker, FILE_O_WRITE);
    if (f)
        f.close();
    spiLock->unlock();
}

#endif
