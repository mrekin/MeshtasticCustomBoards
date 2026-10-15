// BuildLab Scout: board defaults for a fresh configuration, and the rotary encoder driver.

#include "configuration.h"
#include "FSCommon.h"
#include "NodeDB.h"
#include "SPILock.h"
#include "concurrency/OSThread.h"
#include "input/InputBroker.h"
#include "main.h"

// ---------------------------------------------------------------------------------------
// Rotary encoder
//
// The stock canned-message encoder only reschedules its thread from the pin interrupt and does
// not wake the main loop, so on an idle screen turns wait up to ~1 s and several detents merge
// into one event. This driver decodes the encoder in the interrupt, wakes the main loop and hands
// out one event per detent. At most SCOUT_ENCODER_QUEUE detents are kept: menus redraw on every
// step, and a longer queue keeps them scrolling after the knob has stopped. Turning the other way
// drops the queue, so the UI follows the new direction at once.
// ---------------------------------------------------------------------------------------

#if !MESHTASTIC_EXCLUDE_INPUTBROKER

#define SCOUT_ENCODER_STEPS_PER_DETENT 4
#define SCOUT_ENCODER_QUEUE 2
#define SCOUT_LONG_PRESS_MS 300
#define SCOUT_PRESS_DEBOUNCE_MS 200

// Index = (previous AB << 2) | current AB; value = step direction, 0 = no change or bounce
static const int8_t quadTable[16] = {0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0};

class ScoutEncoder : public Observable<const InputEvent *>, public concurrency::OSThread
{
  public:
    ScoutEncoder() : concurrency::OSThread("ScoutEncoder") {}

    void begin()
    {
        // Pin A/B are swapped against the defines so that turning right is CW
        pinMode(SCOUT_ENCODER_PIN_A, INPUT_PULLUP);
        pinMode(SCOUT_ENCODER_PIN_B, INPUT_PULLUP);
        pinMode(SCOUT_ENCODER_PIN_PRESS, INPUT_PULLUP);
        prevAB = readAB();
        // Replaces the stock rotary handlers on these pins if the canned-message encoder is enabled
        attachInterruptArg(SCOUT_ENCODER_PIN_A, onTurn, this, CHANGE);
        attachInterruptArg(SCOUT_ENCODER_PIN_B, onTurn, this, CHANGE);
        attachInterruptArg(SCOUT_ENCODER_PIN_PRESS, onPress, this, CHANGE);
        inputBroker->registerSource(this);
        LOG_INFO("Scout encoder initialized (%d, %d, %d)", SCOUT_ENCODER_PIN_A, SCOUT_ENCODER_PIN_B, SCOUT_ENCODER_PIN_PRESS);
    }

  protected:
    int32_t runOnce() override
    {
        uint32_t now = millis();
        input_broker_event ev = INPUT_BROKER_NONE;

        portENTER_CRITICAL(&mux);
        if (pending > 0) {
            pending--;
            ev = INPUT_BROKER_RIGHT;
        } else if (pending < 0) {
            pending++;
            ev = INPUT_BROKER_LEFT;
        }
        bool more = pending != 0;
        portEXIT_CRITICAL(&mux);

        bool pressed = digitalRead(SCOUT_ENCODER_PIN_PRESS) == LOW;
        if (ev == INPUT_BROKER_NONE) {
            if (pressed && !pressActive) {
                pressActive = true;
                longSent = false;
                pressStartMs = now;
            } else if (pressed && pressActive && !longSent && now - pressStartMs >= SCOUT_LONG_PRESS_MS) {
                longSent = true;
                ev = INPUT_BROKER_SELECT_LONG;
            } else if (!pressed && pressActive) {
                pressActive = false;
                if (!longSent && now - lastPressMs >= SCOUT_PRESS_DEBOUNCE_MS) {
                    lastPressMs = now;
                    ev = INPUT_BROKER_SELECT;
                }
            }
        }

        if (ev != INPUT_BROKER_NONE) {
            InputEvent e = {};
            e.source = "ScoutEncoder";
            e.inputEvent = ev;
            notifyObservers(&e);
        }

        if (more)
            return 5;
        if (pressActive)
            return 20; // keep watching for long press and release
        // The ISR reschedules us; a periodic check covers an edge that lands while we are running
        return 1000;
    }

  private:
    static uint8_t readAB() { return (digitalRead(SCOUT_ENCODER_PIN_B) << 1) | digitalRead(SCOUT_ENCODER_PIN_A); }

    static void wake(ScoutEncoder *self)
    {
        self->setIntervalFromNow(0);
        runASAP = true;
        BaseType_t higherWake = 0;
        concurrency::mainDelay.interruptFromISR(&higherWake);
    }

    static void IRAM_ATTR onTurn(void *arg)
    {
        auto *self = static_cast<ScoutEncoder *>(arg);
        uint8_t cur = readAB();
        bool detent = false;
        portENTER_CRITICAL_ISR(&self->mux);
        self->raw += quadTable[(self->prevAB << 2) | cur];
        self->prevAB = cur;
        int8_t dir = 0;
        if (self->raw >= SCOUT_ENCODER_STEPS_PER_DETENT) {
            self->raw -= SCOUT_ENCODER_STEPS_PER_DETENT;
            dir = 1;
        } else if (self->raw <= -SCOUT_ENCODER_STEPS_PER_DETENT) {
            self->raw += SCOUT_ENCODER_STEPS_PER_DETENT;
            dir = -1;
        }
        if (dir > 0) {
            self->pending = self->pending <= 0 ? 1 : (self->pending < SCOUT_ENCODER_QUEUE ? self->pending + 1 : SCOUT_ENCODER_QUEUE);
            detent = true;
        } else if (dir < 0) {
            self->pending = self->pending >= 0 ? -1 : (self->pending > -SCOUT_ENCODER_QUEUE ? self->pending - 1 : -SCOUT_ENCODER_QUEUE);
            detent = true;
        }
        portEXIT_CRITICAL_ISR(&self->mux);
        if (detent)
            wake(self);
    }

    static void IRAM_ATTR onPress(void *arg) { wake(static_cast<ScoutEncoder *>(arg)); }

    portMUX_TYPE mux = portMUX_INITIALIZER_UNLOCKED;
    volatile uint8_t prevAB = 0;
    volatile int8_t raw = 0;
    volatile int8_t pending = 0;

    bool pressActive = false;
    bool longSent = false;
    uint32_t pressStartMs = 0;
    uint32_t lastPressMs = 0;
};

static ScoutEncoder *scoutEncoder = nullptr;

#endif

// ---------------------------------------------------------------------------------------
// Board defaults
//
// Applied once, on the first boot after flashing a clean device or after a factory reset
// (the region is still unset). A device that was already configured is left alone.
// The marker file lives in /prefs, which a factory reset removes, so defaults come back then.
// ---------------------------------------------------------------------------------------

#ifdef FSCom
static const char *defaultsMarker = "/prefs/board_defaults";

static void applyBoardDefaults()
{
    spiLock->lock();
    bool applied = FSCom.exists(defaultsMarker);
    spiLock->unlock();
    if (applied)
        return;

    if (config.lora.region == meshtastic_Config_LoRaConfig_RegionCode_UNSET) {
        LOG_INFO("Scout: apply board defaults");

        config.lora.tx_power = SCOUT_DEFAULT_TX_POWER;

        moduleConfig.store_forward.enabled = true;
        moduleConfig.store_forward.is_server = true;
        moduleConfig.store_forward.heartbeat = false;
        moduleConfig.store_forward.history_return_window = SCOUT_SF_WINDOW_MIN;

        nodeDB->saveToDisk(SEGMENT_CONFIG | SEGMENT_MODULECONFIG);
        // Store & Forward and radio power are set up before this hook runs
        rebootAtMsec = millis() + 2000;
    }

    spiLock->lock();
    auto f = FSCom.open(defaultsMarker, FILE_O_WRITE);
    if (f)
        f.close();
    spiLock->unlock();
}
#endif

extern bool osk_found;

void earlyInitVariant()
{
#ifndef HAS_PHYSICAL_KEYBOARD
    // The encoder can drive the on-screen keyboard; the canned message module reads this at setup
    osk_found = true;
#endif
}

void lateInitVariant()
{
#if !MESHTASTIC_EXCLUDE_INPUTBROKER
    if (inputBroker && !scoutEncoder) {
        scoutEncoder = new ScoutEncoder();
        scoutEncoder->begin();
    }
#endif
#ifdef FSCom
    applyBoardDefaults();
#endif
}
