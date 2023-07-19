#!/bin/bash
###############################################################################
# @author Dave Spriet (spriet@ca.ibm.com)
# @file ib-api.sh
# @description Interactive Brokers Shell Script
#
#

#
###############################################################################
# shellcheck disable=SC2164,SC1091,SC2129,SC2120
# [REQUIRED]

# [SOURCE]

#--------------------------- Environment Variables ---------------------------#
# [REQUIRED]
if [[ -z "${IB_API_HOME}" ]] ; then export IB_API_HOME="/dev-cli/cli/modules/tradingview/interactivebrokers"; fi

#[DEFAULTS]


# [CONSTANTS]


#-------------------------------- Alias Values -------------------------------#

#--------------------------------- Sourcing ----------------------------------#
# [SOURCE]

#[ALL_VARIABLES_ARRAY]

#------------------------------ Environment Path -----------------------------#

#------------------------------ Helper Functions -----------------------------#


#============================= Script Functions ==============================#



#--------------------------- Environment Variables ---------------------------#
# [REQUIRED]


#[DEFAULTS]


# [CONSTANTS]

#-------------------------------- Alias Values -------------------------------#

#--------------------------------- Sourcing ----------------------------------#
# [SOURCE]

#============================= Script Functions ==============================#

###############################################################################
#
backupIBAPI(){
    export DATESTAMP=$(/usr/bin/date '+%Y%m%d_%H%M') #By-Pass wrapper
    cp -f "${IB_API_HOME}/ib-api.py" "${IB_API_HOME}/ib-api-${DATESTAMP}.py"
}

###############################################################################
#
buySPY(){

    cd "${IB_API_HOME}"

    #buyPutOptions "QQQ" "20220902" "300" "3" "300" "302" "0" "True"; buyPutOptions "ABNB" "20220902" "111" "1" "111" "113.12" "0" "True"
    #buyCallOptions "QQQ" "20220902" "300" "3" "" "300" "0" "True"; buyPutOptions "SPY" "20220909" "400" "1" "0" "404.10" "0" "True"

    #buyCallOptions "SPY" "20220909" "400" "1" "0" "396" "0" "True"; buyPutOptions "SPY" "20220909" "400" "1" "0" "404.10" "0" "True"
    #buyCallOptions "SPY" "20220909" "400" "1" "0" "396" "0" "True"
    #buyPutOptions "SPY" "20220909" "400" "1" "0" "404.10" "0" "True"

    # buyCallOptions "SPY" "20220831" "403" "1" "404" "403" "406" "False"
    # buyPutOptions "SPY" "20220829" "403" "1" "404" "405" "400" "True"

}

###############################################################################
#
getHistoricalData(){

    #Parameter is missing
    if [[ -z "${1}" ]] ; then
        echo "getHistoricalData <symbol>"
        return
    fi

    local symbol="${1}"

    #'1 secs', '5 secs', '10 secs' 15 secs', '30 secs', '1 min', '2 mins', '3 mins', '5 mins', '10 mins', '15 mins', '20 mins', '30 mins', '1 hour', '2 hours', '3 hours', '4 hours', '8 hours', '1 day', '1 week', '1 month'.
    cd "${IB_API_HOME}"
    python "${IB_API_HOME}/ib-api.py" -type 'STOCK' -symbol "${symbol}" -preMarket "False"
}

###############################################################################
#python /dev-cli/cli/modules/tradingview/ib/ib-options.py -type 'CALL' -symbol 'SPY' -contractDate '20220829' -strike '403' -quantity '1' -priceCondition '404' -stopPriceCondition '403' -profitPriceCondition '406' -transmit 'True'
#python /dev-cli/cli/modules/tradingview/ib/ib-options.py -type 'PUT' -symbol 'SPY' -contractDate '20220829' -strike '403' -quantity '1' -priceCondition '403' -stopPriceCondition '402' -profitPriceCondition '400' -transmit 'True'
#
buyCallOptions(){

    #Parameter is missing
    if [[ -z "${1}" || -z "${2}" || -z "${3}" || -z "${4}" || -z "${5}" || -z "${6}" || -z "${7}" || -z "${8}" ]] ; then
        echo "buyCallOptions <symbol> <contractDate> <strike> <quantity> <priceCondition> <stopPriceCondition> <profitPriceCondition> <transmit>"
        return
    fi

    local symbol="${1}"
    local contractDate="${2}"
    local strike="${3}"
    local quantity="${4}"
    local priceCondition="${5}"
    local stopPriceCondition="${6}"
    local profitPriceCondition="${7}"
    local transmit="${8}"

    cd "${IB_API_HOME}"
    python "${IB_API_HOME}/ib-api.py" -type 'CALL' -symbol "${symbol}" -contractDate "${contractDate}" -strike "${strike}" -quantity "${quantity}" -priceCondition "${priceCondition}" -stopPriceCondition "${stopPriceCondition}" -profitPriceCondition "${profitPriceCondition}" -transmit "${transmit}"
}

###############################################################################
#python /dev-cli/cli/modules/tradingview/ib/ib-options.py -type 'CALL' -symbol 'SPY' -contractDate '20220829' -strike '403' -quantity '1' -priceCondition '404' -stopPriceCondition '403' -profitPriceCondition '406' -transmit 'True'
#python /dev-cli/cli/modules/tradingview/ib/ib-options.py -type 'PUT' -symbol 'SPY' -contractDate '20220829' -strike '403' -quantity '1' -priceCondition '403' -stopPriceCondition '402' -profitPriceCondition '400' -transmit 'True'
#
buyPutOptions(){

    #Parameter is missing
    if [[ -z "${1}" || -z "${2}" || -z "${3}" || -z "${4}" || -z "${5}" || -z "${6}" || -z "${7}" || -z "${8}" ]] ; then
        echo "buyCallOptions <symbol> <contractDate> <strike> <quantity> <priceCondition> <stopPriceCondition> <profitPriceCondition> <transmit>"
        return
    fi

    local symbol="${1}"
    local contractDate="${2}"
    local strike="${3}"
    local quantity="${4}"
    local priceCondition="${5}"
    local stopPriceCondition="${6}"
    local profitPriceCondition="${7}"
    local transmit="${8}"

    cd "${IB_API_HOME}"
    python "${IB_API_HOME}/ib-api.py" -type 'PUT' -symbol "${symbol}" -contractDate "${contractDate}" -strike "${strike}" -quantity "${quantity}" -priceCondition "${priceCondition}" -stopPriceCondition "${stopPriceCondition}" -profitPriceCondition "${profitPriceCondition}" -transmit "${transmit}"
}
