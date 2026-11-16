// BuildLab Frost Node: board defaults on the first boot.

// The ESP-IDF hybrid compile pass (it rebuilds the IDF libs when they are stale) builds a dummy sketch
// with build_src_filter still applied, so this file is compiled there without lib_deps and fails
// on pb.h. Nanopb is always on the include path of the real build, so skip the file only in that pass.
#if __has_include(<pb.h>)

#include "configuration.h"
#include "FSCommon.h"
#include "NodeDB.h"
#include "SPILock.h"
#include "main.h"

// Applied once. The marker lives in /prefs, which a factory reset removes, so the defaults come back
// after one. Values the user has already set are left alone.
// - Battery: the cell is read by the INA3221, which Meshtastic only uses as the battery when
//   power.device_battery_ina_address points to it.
// - Power metrics: the three INA3221 channels (panel, charger, load) are sent as power telemetry.
#ifdef FSCom
static const char *defaultsMarker = "/prefs/board_defaults";

void lateInitVariant()
{
    spiLock->lock();
    bool applied = FSCom.exists(defaultsMarker);
    spiLock->unlock();
    if (applied)
        return;

    int segments = 0;
    if (config.power.device_battery_ina_address == 0) {
        LOG_INFO("Frost Node: battery from INA3221 at 0x%x", INA3221_ADDR);
        config.power.device_battery_ina_address = INA3221_ADDR;
        segments |= SEGMENT_CONFIG;
    }
    if (!moduleConfig.telemetry.power_measurement_enabled) {
        LOG_INFO("Frost Node: enable power metrics");
        moduleConfig.has_telemetry = true;
        moduleConfig.telemetry.power_measurement_enabled = true;
        segments |= SEGMENT_MODULECONFIG;
    }
    if (segments) {
        nodeDB->saveToDisk(segments);
        // The power telemetry module is created at boot only when it is enabled, so restart once
        if (segments & SEGMENT_MODULECONFIG)
            rebootAtMsec = millis() + 2000;
    }

    spiLock->lock();
    auto f = FSCom.open(defaultsMarker, FILE_O_WRITE);
    if (f)
        f.close();
    spiLock->unlock();
}
#endif

#endif // __has_include(<pb.h>)
