// BuildLab Scout: rotary encoder driver, status LEDs and board defaults for a fresh configuration.

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

// Changes a LED setting in place when the LED Settings menu is open (defined with the status LEDs)
static bool ledMenuHandleSelect();

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

        bool redraw = false;
        if (ev == INPUT_BROKER_SELECT && ledMenuHandleSelect()) {
            ev = INPUT_BROKER_NONE;
            redraw = true; // the menu stays open; an empty event makes the screen redraw it now
        }
        if (ev != INPUT_BROKER_NONE || redraw) {
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

    static void onTurn(void *arg)
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

    static void onPress(void *arg) { wake(static_cast<ScoutEncoder *>(arg)); }

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
// Status LEDs (same behaviour as the BuildLab Scout MeshCore firmware)
//   LED1 green   - packet received (flash) + faint heartbeat every 5 s
//   LED2 red     - transmitting
//   LED3, LED4   - unread messages: slow breathing (can be switched off separately)
//   LED5 blue    - GPS on, searching (blink)
//   LED6 yellow  - GPS fix (short blink)
// Settings (on/off, messages on/off, brightness 1..4) are in the home screen menu
// and stored in /prefs/scout_leds, so a factory reset brings the defaults back.
// ---------------------------------------------------------------------------------------

#if defined(SCOUT_STATUS_LEDS) && HAS_SCREEN

#include "GPSStatus.h"
#include "MeshModule.h"
#include "Observer.h"
#include "graphics/Screen.h"
#include "graphics/SharedUIDisplay.h"
#include "buzz/buzz.h"
#include "graphics/draw/MenuHandler.h"
#include "graphics/draw/NotificationRenderer.h"
#include "sleep.h"
#include <Adafruit_NeoPixel.h>

#define LED_FRAME_MS 20
#define LED_RX_FLASH_MS 120
#define LED_TX_HOLD_MS 80
#define LED_HEARTBEAT_PERIOD_MS 5000
#define LED_HEARTBEAT_MS 60
#define LED_BREATH_PERIOD_MS 3000
#define LED_GPS_SEARCH_PERIOD_MS 1000
#define LED_GPS_FIX_PERIOD_MS 3000
#define LED_GPS_BLINK_MS 80
#define LED_LEVELS 4

// Peak channel value per brightness step (out of 255)
static const uint8_t ledLevels[LED_LEVELS] = {6, 20, 60, 160};
static const char *ledPrefsFile = "/prefs/scout_leds";

// Counts received packets for the green LED; sees every packet the node decodes or relays
class ScoutRxWatch : public MeshModule
{
  public:
    ScoutRxWatch() : MeshModule("ScoutRxWatch") { isPromiscuous = true; }
    volatile uint32_t rxCount = 0;

  protected:
    bool wantPacket(const meshtastic_MeshPacket *p) override { return true; }
    ProcessMessage handleReceived(const meshtastic_MeshPacket &mp) override
    {
        if (!isFromUs(&mp))
            rxCount++;
        return ProcessMessage::CONTINUE;
    }
};

class ScoutLeds : public concurrency::OSThread
{
  public:
    ScoutLeds() : concurrency::OSThread("ScoutLeds") { deepSleepObserver.observe(&notifyDeepSleep); }

    struct Settings {
        uint8_t enabled = 1;
        uint8_t msgEnabled = 1;
        uint8_t level = 1; // 0 = dimmest .. LED_LEVELS - 1 = brightest
    } settings;

    void begin()
    {
        loadSettings();
        strip.begin();
        strip.clear();
        strip.show();
        rxWatch = new ScoutRxWatch();
    }

    void saveSettings()
    {
#ifdef FSCom
        spiLock->lock();
        auto f = FSCom.open(ledPrefsFile, FILE_O_WRITE);
        if (f) {
            f.write((const uint8_t *)&settings, sizeof(settings));
            f.close();
        }
        spiLock->unlock();
#endif
        dirty = true;
        setIntervalFromNow(0); // show the change now, even if the strip was idle
    }

  protected:
    int32_t runOnce() override
    {
        uint32_t now = millis();

        // Track events even while disabled, so re-enabling does not replay a stale flash
        uint32_t rx = rxWatch ? rxWatch->rxCount : 0;
        if (rx != lastRx)
            rxUntil = now + LED_RX_FLASH_MS;
        lastRx = rx;
#ifdef SX126X_TXEN
        if (digitalRead(SX126X_TXEN))
            txUntil = now + LED_TX_HOLD_MS;
#endif

        if (!settings.enabled) {
            for (uint8_t i = 0; i < SCOUT_LED_COUNT; i++)
                put(i, 0, 0, 0, 0);
            if (dirty) {
                strip.show();
                dirty = false;
            }
            return 500; // nothing to animate; saveSettings() wakes the thread when switched back on
        } else {
            // LED1: received packet, otherwise a faint heartbeat
            if ((int32_t)(rxUntil - now) > 0)
                put(0, 0, 255, 0, 256);
            else if (now % LED_HEARTBEAT_PERIOD_MS < LED_HEARTBEAT_MS)
                put(0, 0, 255, 0, 64);
            else
                put(0, 0, 0, 0, 0);

            // LED2: transmit
            put(1, 255, 0, 0, (int32_t)(txUntil - now) > 0 ? 256 : 0);

            // LED3/LED4: unread messages, smooth fade in/out
            if (settings.msgEnabled && graphics::hasUnreadMessage) {
                float ph = (float)(now % LED_BREATH_PERIOD_MS) / LED_BREATH_PERIOD_MS;
                float w = sinf(ph * PI);
                uint16_t scale = 8 + (uint16_t)(w * w * 248); // never fully dark mid-cycle
                put(2, 160, 0, 255, scale);
                put(3, 160, 0, 255, scale);
            } else {
                put(2, 0, 0, 0, 0);
                put(3, 0, 0, 0, 0);
            }

            // LED5/LED6: GPS searching / fix
            bool gpsOn = config.position.gps_mode == meshtastic_Config_PositionConfig_GpsMode_ENABLED && gpsStatus &&
                         gpsStatus->getIsConnected();
            bool gpsFix = gpsOn && gpsStatus->getHasLock();
            put(4, 0, 0, 255, (gpsOn && !gpsFix && now % LED_GPS_SEARCH_PERIOD_MS < LED_GPS_BLINK_MS) ? 256 : 0);
            put(5, 255, 160, 0, (gpsFix && now % LED_GPS_FIX_PERIOD_MS < LED_GPS_BLINK_MS) ? 256 : 0);
        }

        if (dirty) {
            strip.show();
            dirty = false;
        }
        return LED_FRAME_MS;
    }

  private:
    void loadSettings()
    {
#ifdef FSCom
        spiLock->lock();
        auto f = FSCom.open(ledPrefsFile, FILE_O_READ);
        if (f) {
            Settings s;
            if (f.read((uint8_t *)&s, sizeof(s)) == sizeof(s) && s.level < LED_LEVELS)
                settings = s;
            f.close();
        }
        spiLock->unlock();
#endif
    }

    // scale: 0..256, fraction of the current brightness level
    void put(uint8_t idx, uint8_t r, uint8_t g, uint8_t b, uint16_t scale)
    {
        uint32_t peak = (uint32_t)ledLevels[settings.level] * scale / 256;
        uint32_t c = strip.Color(r * peak / 255, g * peak / 255, b * peak / 255);
        if (strip.getPixelColor(idx) != c) {
            strip.setPixelColor(idx, c);
            dirty = true;
        }
    }

    int onDeepSleep(void *)
    {
        strip.clear();
        strip.show();
        return 0;
    }

    Adafruit_NeoPixel strip = Adafruit_NeoPixel(SCOUT_LED_COUNT, SCOUT_LED_PIN, NEO_GRB + NEO_KHZ800);
    ScoutRxWatch *rxWatch = nullptr;
    bool dirty = true;
    uint32_t lastRx = 0;
    uint32_t rxUntil = 0;
    uint32_t txUntil = 0;
    CallbackObserver<ScoutLeds, void *> deepSleepObserver =
        CallbackObserver<ScoutLeds, void *>(this, &ScoutLeds::onDeepSleep);
};

static ScoutLeds *scoutLeds = nullptr;

// "LED Settings" menu, opened from the home screen menu (MenuHandler.cpp is patched by the flasher
// build to add the entry and to call scoutLedMenuShowPending() from handleMenuSwitch()).
// The menu is opened from handleMenuSwitch(), like the stock nested menus. Settings change in place:
// the encoder driver handles the press while this menu is open, so the menu never closes and reopens.

enum ScoutLedMenuItem { LedMenuBack, LedMenuEnabled, LedMenuMsg, LedMenuLevel, LedMenuCount };
static bool ledMenuPending = false;
static bool homeMenuPending = false; // Back returns to the home screen menu
static char ledMenuLabels[LedMenuCount][20];
static const char *ledMenuOptions[LedMenuCount];
static int ledMenuIds[LedMenuCount];

static void ledMenuFillLabels()
{
    const ScoutLeds::Settings &s = scoutLeds->settings;
    snprintf(ledMenuLabels[LedMenuBack], sizeof(ledMenuLabels[0]), "Back");
    snprintf(ledMenuLabels[LedMenuEnabled], sizeof(ledMenuLabels[0]), "LED: %s", s.enabled ? "On" : "Off");
    snprintf(ledMenuLabels[LedMenuMsg], sizeof(ledMenuLabels[0]), "Msg LED: %s", s.msgEnabled ? "On" : "Off");
    snprintf(ledMenuLabels[LedMenuLevel], sizeof(ledMenuLabels[0]), "Brightness: %d/%d", s.level + 1, LED_LEVELS);
}

static void ledMenuApply(int item)
{
    ScoutLeds::Settings &s = scoutLeds->settings;
    if (item == LedMenuEnabled)
        s.enabled = !s.enabled;
    else if (item == LedMenuMsg)
        s.msgEnabled = !s.msgEnabled;
    else if (item == LedMenuLevel)
        s.level = (s.level + 1) % LED_LEVELS;
    else
        return;
    scoutLeds->saveSettings();
    ledMenuFillLabels();
}

static bool ledMenuHandleSelect()
{
    using graphics::NotificationRenderer;
    if (!scoutLeds || !NotificationRenderer::isOverlayBannerShowing() || NotificationRenderer::optionsArrayPtr != ledMenuOptions)
        return false;
    int item = NotificationRenderer::curSelected;
    if (item <= LedMenuBack || item >= LedMenuCount)
        return false; // Back closes the menu as usual
    ledMenuApply(item);
    // Same feedback the stock select gives, which this press no longer reaches
    if (config.device.buzzer_mode != meshtastic_Config_DeviceConfig_BuzzerMode_DISABLED &&
        config.device.buzzer_mode != meshtastic_Config_DeviceConfig_BuzzerMode_NOTIFICATIONS_ONLY &&
        config.device.buzzer_mode != meshtastic_Config_DeviceConfig_BuzzerMode_DIRECT_MSG_ONLY)
        playBeep();
    if (NotificationRenderer::alertBannerUntil != 0)
        NotificationRenderer::alertBannerUntil = millis() + 30000; // keep it open while it is being used
    return true;
}

extern "C" void scoutLedMenuRequest()
{
    ledMenuPending = true;
    if (screen)
        screen->runNow(); // draw the next frame now, as the stock nested menus do
}

extern "C" bool scoutLedMenuShowPending()
{
    if (homeMenuPending) {
        homeMenuPending = false;
        graphics::menuHandler::homeBaseMenu();
        return true;
    }
    if (!ledMenuPending || !scoutLeds || !screen)
        return false;
    ledMenuPending = false;
    ledMenuFillLabels();
    for (int i = 0; i < LedMenuCount; i++) {
        ledMenuOptions[i] = ledMenuLabels[i];
        ledMenuIds[i] = i;
    }

    graphics::BannerOverlayOptions banner;
    banner.message = "LED Settings";
    banner.optionsArrayPtr = ledMenuOptions;
    banner.optionsEnumPtr = ledMenuIds;
    banner.optionsCount = LedMenuCount;
    banner.InitialSelected = LedMenuEnabled;
    // A select from another input source (not the encoder) still works, the menu just closes after it
    banner.bannerCallback = [](int selected) {
        if (selected == LedMenuBack) {
            homeMenuPending = true;
            if (screen)
                screen->runNow();
        } else if (scoutLeds) {
            ledMenuApply(selected);
        }
    };
    screen->showOverlayBanner(banner);
    return true;
}

#else
static bool ledMenuHandleSelect()
{
    return false;
}
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
#if defined(SCOUT_STATUS_LEDS) && HAS_SCREEN
    if (!scoutLeds) {
        scoutLeds = new ScoutLeds();
        scoutLeds->begin();
    }
#endif
#ifdef FSCom
    applyBoardDefaults();
#endif
}
