/**
 * Copyright (c) 2014 - 2017, Nordic Semiconductor ASA
 * 
 * All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without modification,
 * are permitted provided that the following conditions are met:
 * 
 * 1. Redistributions of source code must retain the above copyright notice, this
 *    list of conditions and the following disclaimer.
 * 
 * 2. Redistributions in binary form, except as embedded into a Nordic
 *    Semiconductor ASA integrated circuit in a product or a software update for
 *    such product, must reproduce the above copyright notice, this list of
 *    conditions and the following disclaimer in the documentation and/or other
 *    materials provided with the distribution.
 * 
 * 3. Neither the name of Nordic Semiconductor ASA nor the names of its
 *    contributors may be used to endorse or promote products derived from this
 *    software without specific prior written permission.
 * 
 * 4. This software, with or without modification, must only be used with a
 *    Nordic Semiconductor ASA integrated circuit.
 * 
 * 5. Any software provided in binary form under this license must not be reverse
 *    engineered, decompiled, modified and/or disassembled.
 * 
 * THIS SOFTWARE IS PROVIDED BY NORDIC SEMICONDUCTOR ASA "AS IS" AND ANY EXPRESS
 * OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY, NONINFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL NORDIC SEMICONDUCTOR ASA OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
 * GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 * 
 */

/**
 * @brief BLE Heart Rate and Running speed Relay application main file.
 *
 * @detail This application demonstrates a simple "Relay".
 * Meaning we pass on the values that we receive. By combining a collector part on
 * one end and a sensor part on the other, we show that the s130 can function
 * simultaneously as a central and a peripheral device.
 *
 * In the figure below, the sensor ble_app_hrs connects and interacts with the relay
 * in the same manner it would connect to a heart rate collector. In this case, the Relay
 * application acts as a central.
 *
 * On the other side, a collector (such as Master Control panel or ble_app_hrs_c) connects
 * and interacts with the relay the same manner it would connect to a heart rate sensor peripheral.
 *
 * Led layout:
 * LED 1: Central side is scanning       LED 2: Central side is connected to a peripheral
 * LED 3: Peripheral side is advertising LED 4: Peripheral side is connected to a central
 *
 * @note While testing, be careful that the Sensor and Collector are actually connecting to the Relay,
 *       and not directly to each other!
 *
 *    Peripheral                  Relay                    Central
 *    +--------+        +-----------|----------+        +-----------+
 *    | Heart  |        | Heart     |   Heart  |        |           |
 *    | Rate   | -----> | Rate     -|-> Rate   | -----> | Collector |
 *    | Sensor |        | Collector |   Sensor |        |           |
 *    +--------+        +-----------|   and    |        +-----------+
 *                      | Running   |   Running|
 *    +--------+        | Speed    -|-> Speed  |
 *    | Running|------> | Collector |   Sensor |
 *    | Speed  |        +-----------|----------+
 *    | Sensor |
 *    +--------+
 */

#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "nordic_common.h"
#include "softdevice_handler.h"
#include "peer_manager.h"
#include "app_timer.h"
#include "boards.h"
#include "bsp.h"
#include "bsp_btn_ble.h"
#include "ble.h"
#include "ble_advdata.h"
#include "ble_advertising.h"
#include "ble_conn_params.h"
#include "ble_db_discovery.h"
#include "ble_hrs.h"
#include "ble_rscs.h"
#include "ble_hrs_c.h"
#include "ble_rscs_c.h"
#include "ble_conn_state.h"
#include "fstorage.h"
#include "fds.h"

#define NRF_LOG_MODULE_NAME "APP"
#include "nrf_log.h"
#include "nrf_log_ctrl.h"

#if (NRF_SD_BLE_API_VERSION == 3)
#define NRF_BLE_MAX_MTU_SIZE        GATT_MTU_SIZE_DEFAULT                         /**< MTU size used in the softdevice enabling and to reply to a BLE_GATTS_EVT_EXCHANGE_MTU_REQUEST event. */
#endif

#define APP_FEATURE_NOT_SUPPORTED   BLE_GATT_STATUS_ATTERR_APP_BEGIN + 2          /**< Reply when unsupported features are requested. */

#define CENTRAL_LINK_COUNT          2                                             /**< Number of central links used by the application. When changing this number remember to adjust the RAM settings*/
#define PERIPHERAL_LINK_COUNT       1                                             /**< Number of peripheral links used by the application. When changing this number remember to adjust the RAM settings*/

#define UART_TX_BUF_SIZE            256                                           /**< Size of the UART TX buffer, in bytes. Must be a power of two. */
#define UART_RX_BUF_SIZE            1                                             /**< Size of the UART RX buffer, in bytes. Must be a power of two. */

/* Central related. */

#define CENTRAL_SCANNING_LED        23
#define CENTRAL_CONNECTED_LED       24

#define APP_TIMER_PRESCALER         0                                             /**< Value of the RTC1 PRESCALER register. */
#define APP_TIMER_MAX_TIMERS        (2 + BSP_APP_TIMERS_NUMBER)                   /**< Maximum number of timers used by the application. */
#define APP_TIMER_OP_QUEUE_SIZE     2                                             /**< Size of timer operation queues. */

#define SEC_PARAM_BOND              1                                             /**< Perform bonding. */
#define SEC_PARAM_MITM              0                                             /**< Man In The Middle protection not required. */
#define SEC_PARAM_LESC              0                                             /**< LE Secure Connections not enabled. */
#define SEC_PARAM_KEYPRESS          0                                             /**< Keypress notifications not enabled. */
#define SEC_PARAM_IO_CAPABILITIES   BLE_GAP_IO_CAPS_NONE                          /**< No I/O capabilities. */
#define SEC_PARAM_OOB               0                                             /**< Out Of Band data not available. */
#define SEC_PARAM_MIN_KEY_SIZE      7                                             /**< Minimum encryption key size in octets. */
#define SEC_PARAM_MAX_KEY_SIZE      16                                            /**< Maximum encryption key size in octets. */

#define SCAN_INTERVAL               0x00A0                                        /**< Determines scan interval in units of 0.625 millisecond. */
#define SCAN_WINDOW                 0x0050                                        /**< Determines scan window in units of 0.625 millisecond. */
#define SCAN_TIMEOUT                0

#define MIN_CONNECTION_INTERVAL     (uint16_t) MSEC_TO_UNITS(7.5, UNIT_1_25_MS)   /**< Determines minimum connection interval in milliseconds. */
#define MAX_CONNECTION_INTERVAL     (uint16_t) MSEC_TO_UNITS(30, UNIT_1_25_MS)    /**< Determines maximum connection interval in milliseconds. */
#define SLAVE_LATENCY               0                                             /**< Determines slave latency in terms of connection events. */
#define SUPERVISION_TIMEOUT         (uint16_t) MSEC_TO_UNITS(4000, UNIT_10_MS)    /**< Determines supervision time-out in units of 10 milliseconds. */

#define UUID16_SIZE                 2                                             /**< Size of a UUID, in bytes. */
// #define CUSTOM_SERVICE_UUID_BASE    {0x22,0x22,0x22,0x22,0x22,0x22,0x22,0x22,0x22,0x22,0x22,0x22,0x22,0x22,0x22,0xB2}
#define CUSTOM_SERVICE_UUID         0x1523
#define CUSTOM_CHAR_UUID            0x1524
static ble_uuid128_t const CUSTOM_SERVICE_UUID_BASE = 
    {{0x44,0x44,0x44,0x44,
      0x44,0x44,0x44,0x44,
      0x44,0x44,0x44,0x44,
      0x44,0x44,0x44,0xD4}};

static uint16_t   m_service_handle;
static ble_gatts_char_handles_t m_rssi_char_handles;
static uint16_t   m_conn_handle = BLE_CONN_HANDLE_INVALID;
static int8_t m_rssi_init_value = 0;
static int8_t m_rssi_value = 0;

// 1. Add these variables at the top with other globals
static bool m_rssi_update_pending = false;
static int8_t m_pending_rssi_value = 0;
static uint32_t m_adv_report_count = 0;
static uint8_t last_target_index = 0;
static uint8_t last_target_indexs = 0;

static uint32_t m_time_tick = 0;
static uint8_t last_b0_index = 0;
static uint16_t major = 0;
static uint16_t minor = 0;

#define B0_SERVICE_UUID         

/**@brief Macro to unpack 16bit unsigned UUID from an octet stream. */
#define UUID16_EXTRACT(DST, SRC) \
    do                           \
    {                            \
        (*(DST))   = (SRC)[1];   \
        (*(DST)) <<= 8;          \
        (*(DST))  |= (SRC)[0];   \
    } while (0)

/**@brief Variable length data encapsulation in terms of length and pointer to data. */
typedef struct
{
    uint8_t     * p_data;    /**< Pointer to data. */
    uint16_t      data_len;  /**< Length of data. */
} data_t;

/**
 * @brief Parameters used when scanning.
 */
static const ble_gap_scan_params_t m_scan_params =
{
    .active   = 1,
    .interval = SCAN_INTERVAL,
    .window   = SCAN_WINDOW,
    .timeout  = SCAN_TIMEOUT,
    #if (NRF_SD_BLE_API_VERSION == 2)
        .selective   = 0,
        .p_whitelist = NULL,
    #endif
    #if (NRF_SD_BLE_API_VERSION == 3)
        .use_whitelist = 0,
    #endif
};

/**@brief Connection parameters requested for connection. */
static const ble_gap_conn_params_t m_connection_param =
{
    (uint16_t)MIN_CONNECTION_INTERVAL,
    (uint16_t)MAX_CONNECTION_INTERVAL,
    0,
    (uint16_t)SUPERVISION_TIMEOUT
};

static ble_hrs_c_t        m_ble_hrs_c;                                                    /**< Main structure used by the Heart rate client module. */
static ble_rscs_c_t       m_ble_rsc_c;                                                    /**< Main structure used by the Running speed and cadence client module. */


static ble_db_discovery_t m_ble_db_discovery[CENTRAL_LINK_COUNT + PERIPHERAL_LINK_COUNT]; /**< list of DB structures used by the database discovery module. */

/* Peripheral related. */

#define PERIPHERAL_ADVERTISING_LED       BSP_BOARD_LED_2
#define PERIPHERAL_CONNECTED_LED         BSP_BOARD_LED_3

#define DEVICE_NAME                      "RelayNordic"                                    /**< Name of device used for advertising. */
#define MANUFACTURER_NAME                "NordicSemiconductor"                      /**< Manufacturer. Will be passed to Device Information Service. */
#define APP_ADV_INTERVAL                 300                                        /**< The advertising interval (in units of 0.625 ms). This value corresponds to 187.5 ms. */
#define APP_ADV_TIMEOUT_IN_SECONDS       0                                        /**< The advertising timeout in units of seconds. */

#define FIRST_CONN_PARAMS_UPDATE_DELAY   APP_TIMER_TICKS(5000, APP_TIMER_PRESCALER) /**< Time from initiating event (connect or start of notification) to first time sd_ble_gap_conn_param_update is called (5 seconds). */
#define NEXT_CONN_PARAMS_UPDATE_DELAY    APP_TIMER_TICKS(30000, APP_TIMER_PRESCALER)/**< Time between each call to sd_ble_gap_conn_param_update after the first call (30 seconds). */
#define MAX_CONN_PARAMS_UPDATE_COUNT     3                                          /**< Number of attempts before giving up the connection parameter negotiation. */

static ble_hrs_t    m_hrs;                                                          /**< Main structure for the Heart rate server module. */
static ble_rscs_t   m_rscs;                                                         /**< Main structure for the Running speed and cadence server module. */


/**@brief names which the central applications will scan for, and which will be advertised by the peripherals.
 *  if these are set to empty strings, the UUIDs defined below will be used
 */
static const char m_target_periph_name[] = "";

/**@brief UUIDs which the central applications will scan for if the name above is set to an empty string,
 * and which will be advertised by the peripherals.
 */
static ble_uuid_t m_adv_uuids[] = {{BLE_UUID_HEART_RATE_SERVICE,         BLE_UUID_TYPE_BLE},
                                   {BLE_UUID_RUNNING_SPEED_AND_CADENCE,  BLE_UUID_TYPE_BLE}};


/**@brief Function to handle asserts in the SoftDevice.
 *
 * @details This function will be called in case of an assert in the SoftDevice.
 *
 * @warning This handler is an example only and does not fit a final product. You need to analyze
 *          how your product is supposed to react in case of Assert.
 * @warning On assert from the SoftDevice, the system can only recover on reset.
 *
 * @param[in] line_num     Line number of the failing ASSERT call.
 * @param[in] p_file_name  File name of the failing ASSERT call.
 */
void assert_nrf_callback(uint16_t line_num, const uint8_t * p_file_name)
{
    app_error_handler(0xDEADBEEF, line_num, p_file_name);
}

/**@brief Function for handling errors from the Connection Parameters module.
 *
 * @param[in] nrf_error  Error code containing information about what went wrong.
 */
static void conn_params_error_handler(uint32_t nrf_error)
{
    APP_ERROR_HANDLER(nrf_error);
}


/**
 * @brief Parses advertisement data, providing length and location of the field in case
 *        matching data is found.
 *
 * @param[in]  Type of data to be looked for in advertisement data.
 * @param[in]  Advertisement report length and pointer to report.
 * @param[out] If data type requested is found in the data report, type data length and
 *             pointer to data will be populated here.
 *
 * @retval NRF_SUCCESS if the data type is found in the report.
 * @retval NRF_ERROR_NOT_FOUND if the data type could not be found.
 */
static uint32_t adv_report_parse(uint8_t type, data_t * p_advdata, data_t * p_typedata)
{
    uint32_t  index = 0;
    uint8_t * p_data;

    p_data = p_advdata->p_data;

    while (index < p_advdata->data_len)
    {
        uint8_t field_length = p_data[index];
        uint8_t field_type   = p_data[index + 1];

        if (field_type == type)
        {
            p_typedata->p_data   = &p_data[index + 2];
            p_typedata->data_len = field_length - 1;
            return NRF_SUCCESS;
        }
        index += field_length + 1;
    }
    return NRF_ERROR_NOT_FOUND;
}


/**@brief Function for initiating scanning.
 */
static void scan_start(void)
{
    ret_code_t err_code;

    (void) sd_ble_gap_scan_stop();

    err_code = sd_ble_gap_scan_start(&m_scan_params);
    // It is okay to ignore this error since we are stopping the scan anyway.
    if (err_code != NRF_ERROR_INVALID_STATE)
    {
        APP_ERROR_CHECK(err_code);
    }
}


/**@brief Function for initiating advertising and scanning.
 */
static void adv_scan_start(void)
{
    ret_code_t err_code;
    uint32_t count;

    //check if there are no flash operations in progress
    err_code = fs_queued_op_count_get(&count);
    APP_ERROR_CHECK(err_code);

    if (count == 0)
    {
        // Start scanning for peripherals and initiate connection to devices which
        // advertise Heart Rate or Running speed and cadence UUIDs.
        scan_start();
        bsp_board_led_on(CENTRAL_CONNECTED_LED);
        // Turn on the LED to signal scanning.
        bsp_board_led_on(CENTRAL_SCANNING_LED);

        // Start advertising.
        err_code = ble_advertising_start(BLE_ADV_MODE_FAST);
        APP_ERROR_CHECK(err_code);
    }
}

// 3. อัปเดตค่า RSSI และส่ง Notification
/*static void rssi_update(int8_t rssi)
{
    if (m_conn_handle != BLE_CONN_HANDLE_INVALID)
    {
        uint16_t               len = sizeof(rssi);
        ble_gatts_hvx_params_t params;
        memset(&params, 0, sizeof(params));

        params.type   = BLE_GATT_HVX_NOTIFICATION;
        params.handle = m_rssi_char_handles.value_handle;
        params.p_data = (uint8_t*)&rssi;
        params.p_len  = &len;

        sd_ble_gatts_hvx(m_conn_handle, &params);
    }
}*/

// 3. อีกอันนึง
/*
static void rssi_update(int8_t rssi)
{
    if (m_conn_handle != BLE_CONN_HANDLE_INVALID)
    {
        uint16_t len = sizeof(rssi);
        ble_gatts_value_t value;

        memset(&value, 0, sizeof(value));
        value.len     = len;
        value.offset  = 0;
        value.p_value = (uint8_t*)&rssi;

        sd_ble_gatts_value_set(m_conn_handle,
                               m_rssi_char_handles.value_handle,
                               &value);
    }
}*/
static void update_rssi_characteristic_light(int8_t rssi)
{
    ret_code_t err_code;
    
    // Store value globally for Read operations
    m_rssi_value = rssi;

    // Only update GATT DB, skip notification in interrupt context
    ble_gatts_value_t gatts_value;
    memset(&gatts_value, 0, sizeof(gatts_value));
    gatts_value.len     = sizeof(m_rssi_value);
    gatts_value.offset  = 0;
    gatts_value.p_value = (uint8_t *)&m_rssi_value;

    err_code = sd_ble_gatts_value_set(BLE_CONN_HANDLE_INVALID,
                                      m_rssi_char_handles.value_handle,
                                      &gatts_value);
    
    // Remove all logging from this function to prevent overflow
    // Just store the error for later if needed
    (void)err_code;
}

///////////// RSSI4, H4TT, L4TT, RSSI0, H0TT, L0TT/////////////////////

static uint16_t beacon_minor_get(void)
{
    // อ่านค่า counter ของ RTC1
    uint32_t rtc_count = NRF_RTC1->COUNTER;  // 24-bit counter

    // แปลง tick → millisecond
    uint32_t ms = (rtc_count * 1000UL) / 32768UL;

    // คืนค่า 16-bit (วนได้เอง)
    return (uint16_t)(ms & 0xFFFF);
}

static void beacon_timeout_handler(void * p_context)
{
    UNUSED_PARAMETER(p_context);

    // เพิ่มเวลา (ทุกครั้งที่ timer ยิง)
    time_tick_seconds += 0.1;
    beacon_update();
}

// 4. Add this timer callback function:
APP_TIMER_DEF(m_rssi_update_timer);

static void rssi_update_timeout_handler(void * p_context)
{
    
    if (m_rssi_update_pending)
    {
        //NRF_LOG_INFO("if m_rssi_update_pending alive\r\n");
        update_rssi_characteristic_light(m_pending_rssi_value);
        m_rssi_update_pending = false;

        // Optional: Send notification outside of interrupt context
        if (m_conn_handle != BLE_CONN_HANDLE_INVALID)
        {
            char rssi_str[20];
            const char *name = "??";
             uint8_t notify_data[16];

             // เลือกชื่อ device (D4 หรือ C3) ตาม UUID ที่เจอ
            if (last_target_index == 1) {
                name = "D4";
            } else if (last_target_index == 3) {
                name = "C3";
            } else if (last_target_indexs == 2){
                name = "B0";
            }
            notify_data[0] = (uint8_t)(major >> 8);
            notify_data[1] = (uint8_t)(major & 0xFF);
            notify_data[2] = (uint8_t)(minor >> 8);
            notify_data[3] = (uint8_t)(minor & 0xFF);

            notify_data[4] = (uint8_t)(rssi & 8);
            notify_data[7] = (uint8_t)(minor4 & 8);
            notify_data[8] = (uint8_t)(minor4 & 0xFF);
            
            // สร้าง string เช่น "D4:-55 dBm"
            snprintf(rssi_str, sizeof(rssi_str), "%s:%d dBm", name, m_rssi_value);

            //uint16_t len = sizeof(m_rssi_value);
            //uint16_t len = sizeof(m_time_tick);
            uint16_t len = sizeof(notify_data);
            //uint16_t len = strlen(rssi_str);
            ble_gatts_hvx_params_t hvx_params;
            memset(&hvx_params, 0, sizeof(hvx_params));
            hvx_params.handle = m_rssi_char_handles.value_handle;
            hvx_params.type   = BLE_GATT_HVX_NOTIFICATION;
            //hvx_params.p_data = (uint8_t *)&m_time_tick;
            hvx_params.p_data = notify_data;
            hvx_params.p_len  = &len;

            sd_ble_gatts_hvx(m_conn_handle, &hvx_params);
        }
    }
}
/*
static bool find_adv_uuid128(const ble_gap_evt_adv_report_t * adv, const uint8_t target_uuid[16])
{
    uint8_t index = 0;

    while (index < adv->dlen)
    {
        uint8_t field_len  = adv->data[index];
        uint8_t field_type = adv->data[index + 1];

        // 0x06 = Incomplete List of 128-bit UUIDs
        // 0x07 = Complete List of 128-bit UUIDs
        //NRF_LOG_INFO("Start comparing")
            // เทียบ UUID
            
        if (adv->data[index + 1] == BLE_GAP_AD_TYPE_128BIT_SERVICE_UUID_COMPLETE ||
            adv->data[index + 1] == BLE_GAP_AD_TYPE_128BIT_SERVICE_UUID_MORE_AVAILABLE)
        {
            NRF_LOG_INFO("Found comparing\r\n");
            if (field_len >= 17) // 16-byte UUID + type
            {
                if (memcmp(&adv->data[index + 2], target_uuid, 16) == 0)
                {   
                    NRF_LOG_INFO("YES\r\n");
                    return true;
                }
            }
        }
        NRF_LOG_INFO("field_type=0x%02X len=%d", field_type, field_len);
        index += field_len + 1;
    }
    return false;
}*/

// static bool find_ibeacon_uuid(const ble_gap_evt_adv_report_t * adv, const uint8_t target_uuid[16])
// {
//     uint8_t index = 0;
    
//     while (index < adv->dlen)
//     {
//         uint8_t field_len  = adv->data[index];
//         uint8_t field_type = adv->data[index + 1];
        
//         // หา Manufacturer Specific Data (0xFF)
//         if (field_type == BLE_GAP_AD_TYPE_MANUFACTURER_SPECIFIC_DATA)
//         {
            
//             // ตรวจสอบ iBeacon header: 4C 00 02 15
//             if (field_len >= 25 && 
//                 adv->data[index + 2] == 0x4C &&  // Apple Company ID (low byte)
//                 adv->data[index + 3] == 0x00 &&  // Apple Company ID (high byte)
//                 adv->data[index + 4] == 0x02 &&  // iBeacon type
//                 adv->data[index + 5] == 0x15)    // iBeacon data length (21 bytes)
//             {
//                 // เปรียบเทียบ UUID (16 bytes)
//                 // NRF_LOG_INFO("Start comparing\r\n")
//                 if (memcmp(&adv->data[index + 6], target_uuid, 16) == 0)
//                 {
//                     //NRF_LOG_INFO("Found comparing\r\n")
//                     return true;
//                 }
//             }
//         }
        
//         index += field_len + 1;
//     }
//     return false;
// }

static bool find_b0_uuid(const ble_gap_evt_adv_report_t * adv, const uint8_t target_uuid[16])
{
    uint8_t index = 0;
    last_b0_index = -1;

    while (index < adv->dlen)
    {
        uint8_t field_len  = adv->data[index];
        uint8_t field_type = adv->data[index + 1];

        if (field_type == BLE_GAP_AD_TYPE_MANUFACTURER_SPECIFIC_DATA)
        {
            // ปกติ UUID จะเริ่มหลังจาก Company ID (2 bytes)
            //NRF_LOG_INFO("Manufacturer specific data, len=%d", field_len);
            //NRF_LOG_HEXDUMP_INFO(&adv->data[index + 6], field_len);
            if (field_len >= 25) // 2 + 16 bytes
            {
                // offset = index+2 (ข้าม type + length) + 2 bytes company ID
                //NRF_LOG_INFO("Prepare Comparing");
                char uuid_ascii[17];
                memcpy(uuid_ascii, &adv->data[index + 6], 16);
                uuid_ascii[16] = '\0';
                //NRF_LOG_INFO("UUID as text: %s", nrf_log_push(uuid_ascii));
                if (memcmp(&adv->data[index + 6], target_uuid, 16) == 0)
                {
                    NRF_LOG_INFO("Found Comparing");
                    last_b0_index = index;
                    return true;
                }
            }
        }

        index += field_len + 1;
    }
    return false;
}





/**@brief Function for handling Peer Manager events.
 *
 * @param[in] p_evt  Peer Manager event.
 */
static void pm_evt_handler(pm_evt_t const * p_evt)
{
    ret_code_t err_code;

    switch (p_evt->evt_id)
    {
        case PM_EVT_BONDED_PEER_CONNECTED:
        {
            NRF_LOG_INFO("Connected to a previously bonded device.\r\n");
        } break;

        case PM_EVT_CONN_SEC_SUCCEEDED:
        {
            NRF_LOG_INFO("Link secured. Role: %d. conn_handle: %d, Procedure: %d\r\n",
                         ble_conn_state_role(p_evt->conn_handle),
                         p_evt->conn_handle,
                         p_evt->params.conn_sec_succeeded.procedure);
        } break;

        case PM_EVT_CONN_SEC_FAILED:
        {
            /* Often, when securing fails, it shouldn't be restarted, for security reasons.
             * Other times, it can be restarted directly.
             * Sometimes it can be restarted, but only after changing some Security Parameters.
             * Sometimes, it cannot be restarted until the link is disconnected and reconnected.
             * Sometimes it is impossible, to secure the link, or the peer device does not support it.
             * How to handle this error is highly application dependent. */
        } break;

        case PM_EVT_CONN_SEC_CONFIG_REQ:
        {
            // Reject pairing request from an already bonded peer.
            pm_conn_sec_config_t conn_sec_config = {.allow_repairing = false};
            pm_conn_sec_config_reply(p_evt->conn_handle, &conn_sec_config);
        } break;

        case PM_EVT_STORAGE_FULL:
        {
            // Run garbage collection on the flash.
            err_code = fds_gc();
            if (err_code == FDS_ERR_BUSY || err_code == FDS_ERR_NO_SPACE_IN_QUEUES)
            {
                // Retry.
            }
            else
            {
                APP_ERROR_CHECK(err_code);
            }
        } break;

        case PM_EVT_PEERS_DELETE_SUCCEEDED:
        {
            adv_scan_start();
        } break;

        case PM_EVT_LOCAL_DB_CACHE_APPLY_FAILED:
        {
            // The local database has likely changed, send service changed indications.
            pm_local_database_has_changed();
        } break;

        case PM_EVT_PEER_DATA_UPDATE_FAILED:
        {
            // Assert.
            APP_ERROR_CHECK(p_evt->params.peer_data_update_failed.error);
        } break;

        case PM_EVT_PEER_DELETE_FAILED:
        {
            // Assert.
            APP_ERROR_CHECK(p_evt->params.peer_delete_failed.error);
        } break;

        case PM_EVT_PEERS_DELETE_FAILED:
        {
            // Assert.
            APP_ERROR_CHECK(p_evt->params.peers_delete_failed_evt.error);
        } break;

        case PM_EVT_ERROR_UNEXPECTED:
        {
            // Assert.
            APP_ERROR_CHECK(p_evt->params.error_unexpected.error);
        } break;

        case PM_EVT_CONN_SEC_START:
        case PM_EVT_PEER_DATA_UPDATE_SUCCEEDED:
        case PM_EVT_PEER_DELETE_SUCCEEDED:
        case PM_EVT_LOCAL_DB_CACHE_APPLIED:
        case PM_EVT_SERVICE_CHANGED_IND_SENT:
        case PM_EVT_SERVICE_CHANGED_IND_CONFIRMED:
        default:
            break;
    }
}


/**@brief Handles events coming from the Heart Rate central module.
 */



/**@brief Handles events coming from  Running Speed and Cadence central module.
 */



/**@brief Function for searching a given name in the advertisement packets.
 *
 * @details Use this function to parse received advertising data and to find a given
 * name in them either as 'complete_local_name' or as 'short_local_name'.
 *
 * @param[in]   p_adv_report   advertising data to parse.
 * @param[in]   name_to_find   name to search.
 * @return   true if the given name was found, false otherwise.
 */
static bool find_adv_name(const ble_gap_evt_adv_report_t *p_adv_report, const char * name_to_find)
{
    uint32_t err_code;
    data_t   adv_data;
    data_t   dev_name;

    // Initialize advertisement report for parsing
    adv_data.p_data     = (uint8_t *)p_adv_report->data;
    adv_data.data_len   = p_adv_report->dlen;

    //search for advertising names
    err_code = adv_report_parse(BLE_GAP_AD_TYPE_COMPLETE_LOCAL_NAME,
                                &adv_data,
                                &dev_name);
    if (err_code == NRF_SUCCESS)
    {
        if (memcmp(name_to_find, dev_name.p_data, dev_name.data_len )== 0)
        {
            return true;
        }
    }
    else
    {
        // Look for the short local name if it was not found as complete
        err_code = adv_report_parse(BLE_GAP_AD_TYPE_SHORT_LOCAL_NAME,
                                    &adv_data,
                                    &dev_name);
        if (err_code != NRF_SUCCESS)
        {
            return false;
        }
        if (memcmp(m_target_periph_name, dev_name.p_data, dev_name.data_len )== 0)
        {
            return true;
        }
    }
    return false;
}


/**@brief Function for searching a UUID in the advertisement packets.
 *
 * @details Use this function to parse received advertising data and to find a given
 * UUID in them.
 *
 * @param[in]   p_adv_report   advertising data to parse.
 * @param[in]   uuid_to_find   UUIID to search.
 * @return   true if the given UUID was found, false otherwise.
 */
static bool find_adv_uuid(const ble_gap_evt_adv_report_t *p_adv_report, const uint16_t uuid_to_find)
{
    uint32_t err_code;
    data_t   adv_data;
    data_t   type_data;

    // Initialize advertisement report for parsing.
    adv_data.p_data     = (uint8_t *)p_adv_report->data;
    adv_data.data_len   = p_adv_report->dlen;

    err_code = adv_report_parse(BLE_GAP_AD_TYPE_16BIT_SERVICE_UUID_MORE_AVAILABLE,
                                &adv_data,
                                &type_data);

    if (err_code != NRF_SUCCESS)
    {
        // Look for the services in 'complete' if it was not found in 'more available'.
        err_code = adv_report_parse(BLE_GAP_AD_TYPE_16BIT_SERVICE_UUID_COMPLETE,
                                    &adv_data,
                                    &type_data);

        if (err_code != NRF_SUCCESS)
        {
            // If we can't parse the data, then exit.
            return false;
        }
    }

    // Verify if any UUID match the given UUID.
    for (uint32_t u_index = 0; u_index < (type_data.data_len / UUID16_SIZE); u_index++)
    {
        uint16_t    extracted_uuid;

        UUID16_EXTRACT(&extracted_uuid, &type_data.p_data[u_index * UUID16_SIZE]);

        if (extracted_uuid == uuid_to_find)
        {
            return true;
        }
    }
    return false;
}


/**@brief Function for handling BLE Stack events concerning central applications.
 *
 * @details This function keeps the connection handles of central applications up-to-date. It
 * parses scanning reports, initiating a connection attempt to peripherals when a target UUID
 * is found, and manages connection parameter update requests. Additionally, it updates the status
 * of LEDs used to report central applications activity.
 *
 * @note        Since this function updates connection handles, @ref BLE_GAP_EVT_DISCONNECTED events
 *              should be dispatched to the target application before invoking this function.
 *
 * @param[in]   p_ble_evt   Bluetooth stack event.
 */
static void on_ble_central_evt(const ble_evt_t * const p_ble_evt)
{
    const ble_gap_evt_t   * const p_gap_evt = &p_ble_evt->evt.gap_evt;
    ret_code_t                    err_code;

    switch (p_ble_evt->header.evt_id)
    {
        /** Upon connection, check which peripheral has connected (HR or RSC), initiate DB
         *  discovery, update LEDs status and resume scanning if necessary. */
        case BLE_GAP_EVT_CONNECTED:
        {
            NRF_LOG_INFO("Central Connected \r\n");
            /** If no Heart Rate sensor or RSC sensor is currently connected, try to find them on this peripheral*/


            /** Update LEDs status, and check if we should be looking for more
             *  peripherals to connect to. */
            bsp_board_led_on(CENTRAL_CONNECTED_LED);
            if (ble_conn_state_n_centrals() == CENTRAL_LINK_COUNT)
            {
                bsp_board_led_off(CENTRAL_SCANNING_LED);
            }
            else
            {
                // Resume scanning.
                bsp_board_led_on(CENTRAL_SCANNING_LED);
                scan_start();
            }
        } break; // BLE_GAP_EVT_CONNECTED

        /** Upon disconnection, reset the connection handle of the peer which disconnected, update
         * the LEDs status and start scanning again. */
        case BLE_GAP_EVT_DISCONNECTED:
        {
            uint8_t n_centrals;

            if ((m_conn_handle == BLE_CONN_HANDLE_INVALID))
            {
                // Start scanning
                scan_start();

                // Update LEDs status.
                bsp_board_led_on(CENTRAL_SCANNING_LED);
            }
            n_centrals = ble_conn_state_n_centrals();

            if (n_centrals == 0)
            {
                bsp_board_led_off(CENTRAL_CONNECTED_LED);
            }
        } break; // BLE_GAP_EVT_DISCONNECTED

        case BLE_GAP_EVT_ADV_REPORT:
        {
            const ble_gap_evt_adv_report_t *adv = &p_gap_evt->params.adv_report;
            
            // Limit processing frequency to avoid overwhelming the system
            m_adv_report_count++;
            if (m_adv_report_count % 10 != 0) {
                break; // Process only every 10th advertisement
            }
            
            if (strlen(m_target_periph_name) != 0)
            {
                if (find_adv_name(adv, m_target_periph_name))
                {
                    // Initiate connection.
                    err_code = sd_ble_gap_connect(&adv->peer_addr,
                                                &m_scan_params,
                                                &m_connection_param);
                    if (err_code != NRF_SUCCESS)
                    {
                        NRF_LOG_INFO("Connection Request Failed, reason %d\r\n", err_code);
                    }
                }
            }
            else
            {
            /** We do not want to connect to two peripherals offering the same service, so when
                *  a UUID is matched, we check that we are not already connected to a peer which
                *  offers the same service. */
                if ((find_adv_uuid(adv, BLE_UUID_HEART_RATE_SERVICE)&&
                    (m_conn_handle== BLE_CONN_HANDLE_INVALID)))
                {
                    // Initiate connection.
                    err_code = sd_ble_gap_connect(&adv->peer_addr,
                                                &m_scan_params,
                                                &m_connection_param);
                    if (err_code != NRF_SUCCESS)
                    {
                        NRF_LOG_INFO("Connection Request Failed, reason %d\r\n", err_code);
                    }
                }
                
            }
            static const uint8_t b0_target_uuid[16] = {
                 0xB0,0x00,0x00,0x00,
                 0x00,0x00,0x00,0x00,
                 0x00,0x00,0x00,0x00,
                 0x00,0x00,0x00,0x00
             };


            //bool found = find_ibeacon_uuid(adv, target_uuid);

            // if (find_ibeacon_uuid(adv, target_uuid))
            // {
            //     // Instead of immediate processing, just flag for later update
            //     m_rssi_update_pending = true;
            //     m_pending_rssi_value = adv->rssi;
                
            //     // Minimal logging - remove the hexdump completely
            //     NRF_LOG_INFO("Target found, RSSI=%d", adv->rssi);
            // }
            // for (int i = 0; i < 2; i++)
            // {
            //     if (find_ibeacon_uuid(adv, target_uuid[i]))
            //     {
            //         m_rssi_update_pending = true;
            //         m_pending_rssi_value = adv->rssi;
            //         last_target_index = i;
            //         //NRF_LOG_INFO("Target %d found, RSSI=%d", i, adv->rssi);
            //     }

            // }

            if (find_b0_uuid(adv, b0_target_uuid))
            {
                m_rssi_update_pending = true;
                m_pending_rssi_value  = adv->rssi;
                last_target_indexs    = 2; // B0
                

                if (last_b0_index >= 0)
                {
                    major = (adv->data[last_b0_index + 22] << 8) |
                                    (adv->data[last_b0_index + 23]);
                    minor = (adv->data[last_b0_index + 24] << 8) |
                                    (adv->data[last_b0_index + 25]);

                    m_time_tick = ((uint32_t)major << 16) | minor;

                    NRF_LOG_INFO("Target found, RSSI=%d, Major=%u, Minor=%u, time_tick=%u",
                                adv->rssi, major, minor, m_time_tick);
                }
            }
            
    

            

        } break; // BLE_GAP_ADV_REPORT

        case BLE_GAP_EVT_TIMEOUT:
        {
            // We have not specified a timeout for scanning, so only connection attemps can timeout.
            if (p_gap_evt->params.timeout.src == BLE_GAP_TIMEOUT_SRC_CONN)
            {
                NRF_LOG_INFO("Connection Request timed out.\r\n");
            }
        } break; // BLE_GAP_EVT_TIMEOUT

        case BLE_GAP_EVT_CONN_PARAM_UPDATE_REQUEST:
        {
            // Accept parameters requested by peer.
            err_code = sd_ble_gap_conn_param_update(p_gap_evt->conn_handle,
                                        &p_gap_evt->params.conn_param_update_request.conn_params);
            APP_ERROR_CHECK(err_code);
        } break; // BLE_GAP_EVT_CONN_PARAM_UPDATE_REQUEST

        case BLE_GATTC_EVT_TIMEOUT:
            // Disconnect on GATT Client timeout event.
            NRF_LOG_DEBUG("GATT Client Timeout.\r\n");
            err_code = sd_ble_gap_disconnect(p_ble_evt->evt.gattc_evt.conn_handle,
                                             BLE_HCI_REMOTE_USER_TERMINATED_CONNECTION);
            APP_ERROR_CHECK(err_code);
            break; // BLE_GATTC_EVT_TIMEOUT

        case BLE_GATTS_EVT_TIMEOUT:
            // Disconnect on GATT Server timeout event.
            NRF_LOG_DEBUG("GATT Server Timeout.\r\n");
            err_code = sd_ble_gap_disconnect(p_ble_evt->evt.gatts_evt.conn_handle,
                                             BLE_HCI_REMOTE_USER_TERMINATED_CONNECTION);
            APP_ERROR_CHECK(err_code);
            break; // BLE_GATTS_EVT_TIMEOUT

#if (NRF_SD_BLE_API_VERSION == 3)
        case BLE_GATTS_EVT_EXCHANGE_MTU_REQUEST:
            err_code = sd_ble_gatts_exchange_mtu_reply(p_ble_evt->evt.gatts_evt.conn_handle,
                                                       NRF_BLE_MAX_MTU_SIZE);
            APP_ERROR_CHECK(err_code);
            break; // BLE_GATTS_EVT_EXCHANGE_MTU_REQUEST
#endif

        default:
            // No implementation needed.
            break;
    }
}


/**@brief Function for handling BLE Stack events involving peripheral applications. Manages the
 * LEDs used to report the status of the peripheral applications.
 *
 * @param[in] p_ble_evt  Bluetooth stack event.
 */
static void on_ble_peripheral_evt(ble_evt_t * p_ble_evt)
{
    ret_code_t err_code;
    switch (p_ble_evt->header.evt_id)
    {
        case BLE_GAP_EVT_CONNECTED:
            NRF_LOG_INFO("Peripheral connected\r\n");
            bsp_board_led_off(PERIPHERAL_ADVERTISING_LED);
            bsp_board_led_on(PERIPHERAL_CONNECTED_LED);
            // แก้ไข
            m_conn_handle = p_ble_evt->evt.gap_evt.conn_handle;
            NRF_LOG_INFO("m_conn_handle set = %d", m_conn_handle);

                    // --- ดึงที่อยู่ (MAC) ของ Central ---
            const ble_gap_evt_connected_t * p_connected =
                &p_ble_evt->evt.gap_evt.params.connected;

            ble_gap_addr_t peer_addr = p_connected->peer_addr;

            // แสดงเป็นรูปแบบ XX:XX:XX:XX:XX:XX
            NRF_LOG_INFO("Connected to: %02X:%02X:%02X:%02X:%02X:%02X",
                        peer_addr.addr[5],
                        peer_addr.addr[4],
                        peer_addr.addr[3],
                        peer_addr.addr[2],
                        peer_addr.addr[1],
                        peer_addr.addr[0]);
            //
            break; //BLE_GAP_EVT_CONNECTED

        case BLE_GAP_EVT_DISCONNECTED:
            NRF_LOG_INFO("Peripheral disconnected\r\n");
            bsp_board_led_off(PERIPHERAL_CONNECTED_LED);
            //แก้ไข
            m_conn_handle = BLE_CONN_HANDLE_INVALID;
            //
            break;//BLE_GAP_EVT_DISCONNECTED

        case BLE_GATTC_EVT_TIMEOUT:
            // Disconnect on GATT Client timeout event.
            NRF_LOG_DEBUG("GATT Client Timeout.\r\n");
            err_code = sd_ble_gap_disconnect(p_ble_evt->evt.gattc_evt.conn_handle,
                                             BLE_HCI_REMOTE_USER_TERMINATED_CONNECTION);
            APP_ERROR_CHECK(err_code);
            break; // BLE_GATTC_EVT_TIMEOUT

        case BLE_GATTS_EVT_TIMEOUT:
            // Disconnect on GATT Server timeout event.
            NRF_LOG_DEBUG("GATT Server Timeout.\r\n");
            err_code = sd_ble_gap_disconnect(p_ble_evt->evt.gatts_evt.conn_handle,
                                             BLE_HCI_REMOTE_USER_TERMINATED_CONNECTION);
            APP_ERROR_CHECK(err_code);
            break; // BLE_GATTS_EVT_TIMEOUT

        case BLE_EVT_USER_MEM_REQUEST:
            err_code = sd_ble_user_mem_reply(p_ble_evt->evt.gap_evt.conn_handle, NULL);
            APP_ERROR_CHECK(err_code);
            break;//BLE_EVT_USER_MEM_REQUEST

        case BLE_GATTS_EVT_RW_AUTHORIZE_REQUEST:
        {
            ble_gatts_evt_rw_authorize_request_t  req;
            ble_gatts_rw_authorize_reply_params_t auth_reply;

            req = p_ble_evt->evt.gatts_evt.params.authorize_request;

            if (req.type != BLE_GATTS_AUTHORIZE_TYPE_INVALID)
            {
                if ((req.request.write.op == BLE_GATTS_OP_PREP_WRITE_REQ)     ||
                    (req.request.write.op == BLE_GATTS_OP_EXEC_WRITE_REQ_NOW) ||
                    (req.request.write.op == BLE_GATTS_OP_EXEC_WRITE_REQ_CANCEL))
                {
                    if (req.type == BLE_GATTS_AUTHORIZE_TYPE_WRITE)
                    {
                        auth_reply.type = BLE_GATTS_AUTHORIZE_TYPE_WRITE;
                    }
                    else
                    {
                        auth_reply.type = BLE_GATTS_AUTHORIZE_TYPE_READ;
                    }
                    auth_reply.params.write.gatt_status = APP_FEATURE_NOT_SUPPORTED;
                    err_code = sd_ble_gatts_rw_authorize_reply(p_ble_evt->evt.gatts_evt.conn_handle,
                                                               &auth_reply);
                    APP_ERROR_CHECK(err_code);
                }
            }
        } break; // BLE_GATTS_EVT_RW_AUTHORIZE_REQUEST

#if (NRF_SD_BLE_API_VERSION == 3)
        case BLE_GATTS_EVT_EXCHANGE_MTU_REQUEST:
            err_code = sd_ble_gatts_exchange_mtu_reply(p_ble_evt->evt.gatts_evt.conn_handle,
                                                       NRF_BLE_MAX_MTU_SIZE);
            APP_ERROR_CHECK(err_code);
            break; // BLE_GATTS_EVT_EXCHANGE_MTU_REQUEST
#endif

        default:
            // No implementation needed.
            break;
    }
}


/**@brief Function for handling advertising events.
 *
 * @param[in] ble_adv_evt  Advertising event.
 */
static void on_adv_evt(ble_adv_evt_t ble_adv_evt)
{
    switch (ble_adv_evt)
    {
        case BLE_ADV_EVT_FAST:
            NRF_LOG_INFO("Fast Advertising\r\n");
            bsp_board_led_on(PERIPHERAL_ADVERTISING_LED);
            break;//BLE_ADV_EVT_FAST

        case BLE_ADV_EVT_IDLE:
        {
            ret_code_t err_code;
            NRF_LOG_INFO("Advertising idle, restarting...");
            err_code = ble_advertising_start(BLE_ADV_MODE_FAST);
            APP_ERROR_CHECK(err_code);
        } break;//BLE_ADV_EVT_IDLE

        default:
            // No implementation needed.
            break;
    }
}


/**@brief Function for dispatching a BLE stack event to all modules with a BLE stack event handler.
 *
 * @details This function is called from the scheduler in the main loop after a BLE stack event has
 * been received.
 *
 * @param[in]   p_ble_evt   Bluetooth stack event.
 */
static void ble_evt_dispatch(ble_evt_t * p_ble_evt)
{
    uint16_t conn_handle;
    uint16_t role;

    ble_conn_state_on_ble_evt(p_ble_evt);
    pm_on_ble_evt(p_ble_evt);

    // The connection handle should really be retrievable for any event type.
    conn_handle = p_ble_evt->evt.gap_evt.conn_handle;
    role        = ble_conn_state_role(conn_handle);

    // Based on the role this device plays in the connection, dispatch to the right applications.
    if (role == BLE_GAP_ROLE_PERIPH)
    {
        // Manages peripheral LEDs.
        on_ble_peripheral_evt(p_ble_evt);

        ble_advertising_on_ble_evt(p_ble_evt);
        ble_conn_params_on_ble_evt(p_ble_evt);

        // Dispatch to peripheral applications.
        ble_hrs_on_ble_evt (&m_hrs, p_ble_evt);
        ble_rscs_on_ble_evt(&m_rscs, p_ble_evt);
    }
    else if ((role == BLE_GAP_ROLE_CENTRAL) || (p_ble_evt->header.evt_id == BLE_GAP_EVT_ADV_REPORT))
    {
        /** on_ble_central_evt will update the connection handles, so we want to execute it
         * after dispatching to the central applications upon disconnection. */
        if (p_ble_evt->header.evt_id != BLE_GAP_EVT_DISCONNECTED)
        {
            on_ble_central_evt(p_ble_evt);
        }

        if (conn_handle < CENTRAL_LINK_COUNT + PERIPHERAL_LINK_COUNT)
        {
            ble_db_discovery_on_ble_evt(&m_ble_db_discovery[conn_handle], p_ble_evt);
        }
        ble_hrs_c_on_ble_evt(&m_ble_hrs_c, p_ble_evt);
        ble_rscs_c_on_ble_evt(&m_ble_rsc_c, p_ble_evt);

        // If the peer disconnected, we update the connection handles last.
        if (p_ble_evt->header.evt_id == BLE_GAP_EVT_DISCONNECTED)
        {
            on_ble_central_evt(p_ble_evt);
        }
    }
}


/**@brief Function for dispatching a system event to interested modules.
 *
 * @details This function is called from the System event interrupt handler after a system
 *          event has been received.
 *
 * @param[in]   sys_evt   System stack event.
 */
static void sys_evt_dispatch(uint32_t sys_evt)
{
    fs_sys_event_handler(sys_evt);
    ble_advertising_on_sys_evt(sys_evt);
}


/**@brief Heart rate collector initialization.
 */
// static void hrs_c_init(void)
// {
//     uint32_t         err_code;
//     ble_hrs_c_init_t hrs_c_init_obj;

//     hrs_c_init_obj.evt_handler = hrs_c_evt_handler;

//     err_code = ble_hrs_c_init(&m_ble_hrs_c, &hrs_c_init_obj);
//     APP_ERROR_CHECK(err_code);
// }


// /**@brief RSC collector initialization.
//  */
// static void rscs_c_init(void)
// {
//     uint32_t            err_code;
//     ble_rscs_c_init_t   rscs_c_init_obj;

//     rscs_c_init_obj.evt_handler = rscs_c_evt_handler;

//     err_code = ble_rscs_c_init(&m_ble_rsc_c, &rscs_c_init_obj);
//     APP_ERROR_CHECK(err_code);
// }


/**@brief Function for initializing the BLE stack.
 *
 * @details Initializes the SoftDevice and the BLE event interrupts.
 */
static void ble_stack_init(void)
{
    ret_code_t err_code;

    // Initialize the SoftDevice handler module.
    nrf_clock_lf_cfg_t clock_lf_cfg = NRF_CLOCK_LFCLKSRC;
    SOFTDEVICE_HANDLER_INIT(&clock_lf_cfg, NULL);

    ble_enable_params_t ble_enable_params;
    err_code = softdevice_enable_get_default_config(CENTRAL_LINK_COUNT,
                                                    PERIPHERAL_LINK_COUNT,
                                                    &ble_enable_params);
    APP_ERROR_CHECK(err_code);

    //Check the ram settings against the used number of links
    CHECK_RAM_START_ADDR(CENTRAL_LINK_COUNT,PERIPHERAL_LINK_COUNT);

    // Enable BLE stack.
#if (NRF_SD_BLE_API_VERSION == 3)
    ble_enable_params.gatt_enable_params.att_mtu = NRF_BLE_MAX_MTU_SIZE;
#endif
    err_code = softdevice_enable(&ble_enable_params);
    APP_ERROR_CHECK(err_code);

    // Register with the SoftDevice handler module for BLE events.
    err_code = softdevice_ble_evt_handler_set(ble_evt_dispatch);
    APP_ERROR_CHECK(err_code);

    // Register with the SoftDevice handler module for System events.
    err_code = softdevice_sys_evt_handler_set(sys_evt_dispatch);
    APP_ERROR_CHECK(err_code);
}


/**@brief Function for the Peer Manager initialization.
 *
 * @param[in] erase_bonds  Indicates whether bonding information should be cleared from
 *                         persistent storage during initialization of the Peer Manager.
 */
static void peer_manager_init(bool erase_bonds)
{
    ble_gap_sec_params_t sec_param;
    ret_code_t err_code;

    err_code = pm_init();
    APP_ERROR_CHECK(err_code);

    if (erase_bonds)
    {
        err_code = pm_peers_delete();
        APP_ERROR_CHECK(err_code);
    }

    memset(&sec_param, 0, sizeof(ble_gap_sec_params_t));

    // Security parameters to be used for all security procedures.
    sec_param.bond              = SEC_PARAM_BOND;
    sec_param.mitm              = SEC_PARAM_MITM;
    sec_param.lesc              = SEC_PARAM_LESC;
    sec_param.keypress          = SEC_PARAM_KEYPRESS;
    sec_param.io_caps           = SEC_PARAM_IO_CAPABILITIES;
    sec_param.oob               = SEC_PARAM_OOB;
    sec_param.min_key_size      = SEC_PARAM_MIN_KEY_SIZE;
    sec_param.max_key_size      = SEC_PARAM_MAX_KEY_SIZE;
    sec_param.kdist_own.enc     = 1;
    sec_param.kdist_own.id      = 1;
    sec_param.kdist_peer.enc    = 1;
    sec_param.kdist_peer.id     = 1;

    err_code = pm_sec_params_set(&sec_param);
    APP_ERROR_CHECK(err_code);

    err_code = pm_register(pm_evt_handler);
    APP_ERROR_CHECK(err_code);
}


/**@brief Function for initializing buttons and leds.
 *
 * @param[out] p_erase_bonds  Will be true if the clear bonding button was pressed to
 *                            wake the application up.
 */
static void buttons_leds_init(bool * p_erase_bonds)
{
    bsp_event_t startup_event;

    ret_code_t err_code = bsp_init(BSP_INIT_LED | BSP_INIT_BUTTONS,
                                 APP_TIMER_TICKS(100, APP_TIMER_PRESCALER),
                                 NULL);
    APP_ERROR_CHECK(err_code);

    err_code = bsp_btn_ble_init(NULL, &startup_event);
    APP_ERROR_CHECK(err_code);

    *p_erase_bonds = (startup_event == BSP_EVENT_CLEAR_BONDING_DATA);
}


/**@brief Function for the GAP initialization.
 *
 * @details This function sets up all the necessary GAP (Generic Access Profile) parameters of the
 *          device including the device name, appearance, and the preferred connection parameters.
 */
static void gap_params_init(void)
{
    uint32_t                err_code;
    ble_gap_conn_params_t   gap_conn_params;
    ble_gap_conn_sec_mode_t sec_mode;

    BLE_GAP_CONN_SEC_MODE_SET_OPEN(&sec_mode);

    err_code = sd_ble_gap_device_name_set(&sec_mode,
                                          (const uint8_t *)DEVICE_NAME,
                                          strlen(DEVICE_NAME));
    APP_ERROR_CHECK(err_code);

    memset(&gap_conn_params, 0, sizeof(gap_conn_params));

    gap_conn_params.min_conn_interval = MIN_CONNECTION_INTERVAL;
    gap_conn_params.max_conn_interval = MAX_CONNECTION_INTERVAL;
    gap_conn_params.slave_latency     = SLAVE_LATENCY;
    gap_conn_params.conn_sup_timeout  = SUPERVISION_TIMEOUT;

    err_code = sd_ble_gap_ppcp_set(&gap_conn_params);
    APP_ERROR_CHECK(err_code);
}


/**@brief Function for initializing the Connection Parameters module.
 */
static void conn_params_init(void)
{
    uint32_t               err_code;
    ble_conn_params_init_t cp_init;

    memset(&cp_init, 0, sizeof(cp_init));

    cp_init.p_conn_params                  = NULL;
    cp_init.first_conn_params_update_delay = FIRST_CONN_PARAMS_UPDATE_DELAY;
    cp_init.next_conn_params_update_delay  = NEXT_CONN_PARAMS_UPDATE_DELAY;
    cp_init.max_conn_params_update_count   = MAX_CONN_PARAMS_UPDATE_COUNT;
    cp_init.start_on_notify_cccd_handle    = BLE_CONN_HANDLE_INVALID; // Start upon connection.
    cp_init.disconnect_on_fail             = true;
    cp_init.evt_handler                    = NULL;  // Ignore events.
    cp_init.error_handler                  = conn_params_error_handler;

    err_code = ble_conn_params_init(&cp_init);
    APP_ERROR_CHECK(err_code);
}


/**@brief Function for handling database discovery events.
 *
 * @details This function is callback function to handle events from the database discovery module.
 *          Depending on the UUIDs that are discovered, this function should forward the events
 *          to their respective services.
 *
 * @param[in] p_event  Pointer to the database discovery event.
 */
static void db_disc_handler(ble_db_discovery_evt_t * p_evt)
{
    ble_rscs_on_db_disc_evt(&m_ble_rsc_c, p_evt);
    ble_hrs_on_db_disc_evt(&m_ble_hrs_c, p_evt);
}


/**
 * @brief Database discovery initialization.
 */
static void db_discovery_init(void)
{
    ret_code_t err_code = ble_db_discovery_init(db_disc_handler);
    APP_ERROR_CHECK(err_code);
}


/**@brief Function for initializing services that will be used by the application.
 *
 * @details Initialize the Heart Rate, Battery and Device Information services.
 */
static void services_init(void)
{
    ret_code_t          err_code;
    ble_uuid_t          service_uuid;
    ble_uuid128_t       base_uuid = CUSTOM_SERVICE_UUID_BASE;
    ble_add_char_params_t add_char_params;

    // Add custom base UUID
    err_code = sd_ble_uuid_vs_add(&base_uuid, &service_uuid.type);
    APP_ERROR_CHECK(err_code);

    service_uuid.uuid = CUSTOM_SERVICE_UUID;

    // Add service
    err_code = sd_ble_gatts_service_add(BLE_GATTS_SRVC_TYPE_PRIMARY,
                                        &service_uuid,
                                        &m_service_handle);
    APP_ERROR_CHECK(err_code);

    // Add characteristic for RSSI
    memset(&add_char_params, 0, sizeof(add_char_params));
    add_char_params.uuid              = CUSTOM_CHAR_UUID;
    add_char_params.uuid_type         = service_uuid.type;
    //add_char_params.max_len           = sizeof(int8_t); // RSSI เป็น signed 8-bit
    //add_char_params.init_len          = sizeof(int8_t);
    //add_char_params.p_init_value      = 0;
    add_char_params.init_len    = sizeof(m_rssi_init_value);
    add_char_params.max_len     = 20;
    add_char_params.p_init_value = (uint8_t*)&m_rssi_init_value;
    add_char_params.char_props.read   = 1;
    add_char_params.char_props.notify = 1;
    add_char_params.cccd_write_access = SEC_OPEN;
    add_char_params.read_access       = SEC_OPEN;
    


    err_code = characteristic_add(m_service_handle,
                                  &add_char_params,
                                  &m_rssi_char_handles);
    APP_ERROR_CHECK(err_code);
}


/**@brief Function for initializing the Advertising functionality.
 */
static void advertising_init(void)
{
    uint32_t               err_code;
    ble_advdata_t          advdata;
    ble_adv_modes_config_t options;

    // Build advertising data struct to pass into @ref ble_advertising_init.
    memset(&advdata, 0, sizeof(advdata));

    advdata.name_type               = BLE_ADVDATA_FULL_NAME;
    advdata.include_appearance      = true;
    advdata.flags                   = BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE;
    advdata.uuids_complete.uuid_cnt = sizeof(m_adv_uuids) / sizeof(m_adv_uuids[0]);
    advdata.uuids_complete.p_uuids  = m_adv_uuids;

    memset(&options, 0, sizeof(options));
    options.ble_adv_fast_enabled  = true;
    options.ble_adv_fast_interval = APP_ADV_INTERVAL;
    options.ble_adv_fast_timeout  = APP_ADV_TIMEOUT_IN_SECONDS;

    err_code = ble_advertising_init(&advdata, NULL, &options, on_adv_evt, NULL);
    APP_ERROR_CHECK(err_code);
}


/** @brief Function to sleep until a BLE event is received by the application.
 */
static void power_manage(void)
{
    ret_code_t err_code = sd_app_evt_wait();
    APP_ERROR_CHECK(err_code);
}
////////////////////////////////////////////////////////////////////////////////////
void app_error_fault_handler(uint32_t id, uint32_t pc, uint32_t info)
{
    NRF_LOG_ERROR("Fatal error: ID=0x%08x, PC=0x%08x, INFO=0x%08x", id, pc, info);
    // แสดงข้อมูลเพิ่มเติมผ่าน RTT
    while(1) {
        // Stop execution
    }
}



int main(void)
{
    bool       erase_bonds;

    APP_ERROR_CHECK( NRF_LOG_INIT(NULL));

    NRF_LOG_INFO("Relay Example\r\n");
    
    APP_TIMER_INIT(APP_TIMER_PRESCALER, APP_TIMER_OP_QUEUE_SIZE, NULL);

    ret_code_t err_code = app_timer_create(&m_rssi_update_timer,
                                      APP_TIMER_MODE_REPEATED,
                                      rssi_update_timeout_handler);
    APP_ERROR_CHECK(err_code);

    // Start the timer (100ms interval)
    err_code = app_timer_start(m_rssi_update_timer, 
                            APP_TIMER_TICKS(100, APP_TIMER_PRESCALER), 
                            NULL);
    APP_ERROR_CHECK(err_code);


    buttons_leds_init(&erase_bonds);

    if (erase_bonds)
    {
        NRF_LOG_INFO("Bonds erased!\r\n");
    }

    ble_stack_init();

    peer_manager_init(erase_bonds);

    db_discovery_init();
    //hrs_c_init();
    //rscs_c_init();
    
    gap_params_init();
    conn_params_init();
    services_init();
    advertising_init();

    adv_scan_start();
    //update_rssi_characteristic((int8_t)-51); // -55 dBm -> ค่าที่จะเห็นเป็น 0xC9
    for (;;)
    {
        if (NRF_LOG_PROCESS() == false)
        {
            // Wait for BLE events.
            power_manage();
        }
    }
}
