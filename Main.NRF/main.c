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

/** @file
 *
 * @defgroup ble_sdk_app_beacon_main main.c
 * @{
 * @ingroup ble_sdk_app_beacon
 * @brief Beacon Transmitter Sample Application main file.
 *
 * This file contains the source code for an Beacon transmitter sample application.
 */

#include <stdbool.h>
#include <stdint.h>
#include "ble_advdata.h"
#include "nordic_common.h"
#include "softdevice_handler.h"
#include "bsp.h"
#include "bsp_btn_ble.h"
#include "app_timer.h"
#include "nrf_log.h"
#include "nrf_log_ctrl.h"

#define CENTRAL_LINK_COUNT              0
#define PERIPHERAL_LINK_COUNT           0

#define IS_SRVC_CHANGED_CHARACT_PRESENT 0

#define APP_CFG_NON_CONN_ADV_TIMEOUT    0
#define NON_CONNECTABLE_ADV_INTERVAL    MSEC_TO_UNITS(100, UNIT_0_625_MS)

#define APP_BEACON_INFO_LENGTH          0x17                              /**< Total length of information advertised by the Beacon. */
#define APP_ADV_DATA_LENGTH             0x15                              /**< Length of manufacturer specific data in the advertisement. */
#define APP_DEVICE_TYPE                 0x02                              /**< 0x02 refers to Beacon. */
#define APP_MEASURED_RSSI               0xC3                              /**< The Beacon's measured RSSI at 1 meter distance in dBm. */
#define APP_COMPANY_IDENTIFIER          0x0059                            /**< Company identifier for Nordic Semiconductor ASA. as per www.bluetooth.org. */
#define APP_MAJOR_VALUE                 0x00, 0x6F                       /**< Major value used to identify Beacons. */
#define APP_MINOR_VALUE                 0x03, 0x78                        /**< Minor value used to identify Beacons. */
#define APP_BEACON_UUID                 0xB2, 0x22, 0x22, 0x22, \
                                        0x22, 0x22, 0x22, 0x22, \
                                        0x22, 0x22, 0x22, 0x22, \
                                        0x22, 0x22, 0x22, 0x22

#define DEAD_BEEF                       0xDEADBEEF

#define APP_TIMER_PRESCALER             0
#define APP_TIMER_OP_QUEUE_SIZE         4

#if defined(USE_UICR_FOR_MAJ_MIN_VALUES)
#define MAJ_VAL_OFFSET_IN_BEACON_INFO   18
#define UICR_ADDRESS                    0x10001080
#endif

static ble_gap_adv_params_t m_adv_params;
static uint8_t m_beacon_info[APP_BEACON_INFO_LENGTH] =
{
    APP_DEVICE_TYPE,
    APP_ADV_DATA_LENGTH,
    APP_BEACON_UUID,
    APP_MAJOR_VALUE,
    APP_MINOR_VALUE,
    APP_MEASURED_RSSI
};

APP_TIMER_DEF(m_beacon_timer_id);
static bool toggle_flag = false;
static uint32_t time_tick_seconds = 0;
static ble_advdata_t m_advdata;

void assert_nrf_callback(uint16_t line_num, const uint8_t * p_file_name)
{
    app_error_handler(DEAD_BEEF, line_num, p_file_name);
}

static void advertising_init(void)
{
    uint32_t      err_code;
    ble_advdata_t advdata;
    uint8_t       flags = BLE_GAP_ADV_FLAG_BR_EDR_NOT_SUPPORTED;

    ble_advdata_manuf_data_t manuf_specific_data;

    manuf_specific_data.company_identifier = APP_COMPANY_IDENTIFIER;

#if defined(USE_UICR_FOR_MAJ_MIN_VALUES)
    uint16_t major_value = ((*(uint32_t *)UICR_ADDRESS) & 0xFFFF0000) >> 16;
    uint16_t minor_value = ((*(uint32_t *)UICR_ADDRESS) & 0x0000FFFF);

    uint8_t index = MAJ_VAL_OFFSET_IN_BEACON_INFO;

    m_beacon_info[index++] = MSB_16(major_value);
    m_beacon_info[index++] = LSB_16(major_value);
    m_beacon_info[index++] = MSB_16(minor_value);
    m_beacon_info[index++] = LSB_16(minor_value);
#endif

    manuf_specific_data.data.p_data = (uint8_t *) m_beacon_info;
    manuf_specific_data.data.size   = APP_BEACON_INFO_LENGTH;

    memset(&advdata, 0, sizeof(advdata));
    advdata.name_type             = BLE_ADVDATA_NO_NAME;
    advdata.flags                 = flags;
    advdata.p_manuf_specific_data = &manuf_specific_data;

    err_code = ble_advdata_set(&advdata, NULL);
    APP_ERROR_CHECK(err_code);

    memset(&m_adv_params, 0, sizeof(m_adv_params));
    m_adv_params.type        = BLE_GAP_ADV_TYPE_ADV_NONCONN_IND;
    m_adv_params.p_peer_addr = NULL;
    m_adv_params.fp          = BLE_GAP_ADV_FP_ANY;
    m_adv_params.interval    = NON_CONNECTABLE_ADV_INTERVAL;
    m_adv_params.timeout     = APP_CFG_NON_CONN_ADV_TIMEOUT;
}

static void advertising_start(void)
{
    uint32_t err_code;
    err_code = sd_ble_gap_adv_start(&m_adv_params);
    bsp_board_led_on(3);
    APP_ERROR_CHECK(err_code);

    err_code = bsp_indication_set(BSP_INDICATE_ADVERTISING);
    APP_ERROR_CHECK(err_code);
}

static void ble_stack_init(void)
{
    uint32_t err_code;
    nrf_clock_lf_cfg_t clock_lf_cfg = NRF_CLOCK_LFCLKSRC;

    SOFTDEVICE_HANDLER_INIT(&clock_lf_cfg, NULL);

    ble_enable_params_t ble_enable_params;
    err_code = softdevice_enable_get_default_config(CENTRAL_LINK_COUNT,
                                                    PERIPHERAL_LINK_COUNT,
                                                    &ble_enable_params);
    APP_ERROR_CHECK(err_code);

    CHECK_RAM_START_ADDR(CENTRAL_LINK_COUNT,PERIPHERAL_LINK_COUNT);

    err_code = softdevice_enable(&ble_enable_params);
    APP_ERROR_CHECK(err_code);
}

static void power_manage(void)
{
    uint32_t err_code = sd_app_evt_wait();
    APP_ERROR_CHECK(err_code);
}

static uint16_t beacon_minor_get(void)
{
    // อ่านค่า counter ของ RTC1
    uint32_t rtc_count = NRF_RTC1->COUNTER;  // 24-bit counter

    // แปลง tick → millisecond
    uint32_t ms = (rtc_count * 1000UL) / 32768UL;

    // คืนค่า 16-bit (วนได้เอง)
    return (uint16_t)(ms & 0xFFFF);
}

static void beacon_update(void)
{
    uint16_t major, minor;

    if (toggle_flag)
    {
        major = 111;
    }
    else
    {
        major = 888;
    }

    toggle_flag = !toggle_flag;

    minor = beacon_minor_get();

    // อัพเดตลง advertising packet
    m_beacon_info[18] = major >> 8;
    m_beacon_info[19] = major & 0xFF;
    m_beacon_info[20] = minor >> 8;
    m_beacon_info[21] = minor & 0xFF;

    ble_advdata_set(&m_advdata, NULL);

    uint8_t index = 18;
    m_beacon_info[index++] = (major >> 8) & 0xFF;
    m_beacon_info[index++] = (major & 0xFF);
    m_beacon_info[index++] = (minor >> 8) & 0xFF;
    m_beacon_info[index++] = (minor & 0xFF);

    ble_advdata_t advdata;
    ble_advdata_manuf_data_t manuf_specific_data;

    manuf_specific_data.company_identifier = APP_COMPANY_IDENTIFIER;
    manuf_specific_data.data.p_data = (uint8_t *) m_beacon_info;
    manuf_specific_data.data.size   = APP_BEACON_INFO_LENGTH;

    memset(&advdata, 0, sizeof(advdata));
    advdata.name_type             = BLE_ADVDATA_NO_NAME;
    advdata.flags                 = BLE_GAP_ADV_FLAG_BR_EDR_NOT_SUPPORTED;
    advdata.p_manuf_specific_data = &manuf_specific_data;

    uint32_t err_code = ble_advdata_set(&advdata, NULL);
    APP_ERROR_CHECK(err_code);
}

static void beacon_timeout_handler(void * p_context)
{
    UNUSED_PARAMETER(p_context);

    // เพิ่มเวลา (ทุกครั้งที่ timer ยิง)
    time_tick_seconds += 0.1;
    beacon_update();
}

int main(void)
{
    uint32_t err_code;
    err_code = NRF_LOG_INIT(NULL);
    APP_ERROR_CHECK(err_code);

    APP_TIMER_INIT(APP_TIMER_PRESCALER, APP_TIMER_OP_QUEUE_SIZE, false);
    err_code = bsp_init(BSP_INIT_LED, APP_TIMER_TICKS(100, APP_TIMER_PRESCALER), NULL);
    APP_ERROR_CHECK(err_code);

    // เปิด LED1 ให้ค้างตลอดเวลาที่บอร์ดทำงาน

    ble_stack_init();
    advertising_init();

    NRF_LOG_INFO("BLE Beacon started\r\n");
    advertising_start();

    err_code = app_timer_create(&m_beacon_timer_id,
                                APP_TIMER_MODE_REPEATED,
                                beacon_timeout_handler);
    APP_ERROR_CHECK(err_code);

    err_code = app_timer_start(m_beacon_timer_id,
                               APP_TIMER_TICKS(100, APP_TIMER_PRESCALER),
                               NULL);
    APP_ERROR_CHECK(err_code);

    for (;; )
    {
        if (NRF_LOG_PROCESS() == false)
        {
            power_manage();
        }
    }
}

/**
 * @}
 */
