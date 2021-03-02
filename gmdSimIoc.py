#!/usr/bin/env python3
import enum
import os
import sys
import itertools
import csv

from caproto import ChannelType
from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run
from caproto.server import template_arg_parser

from algorithms import *

att_strings = ['0db', '-3db', '-6db', '-9db',
               '-12db', '-15db', '-18db',
               '-21db', '-24db', '-27db',
               '-30db', '-33db', '-36db',
               '-39db', '-42db', '-45db']    

bi_strings = ['No', 'Yes']

peak_check_strings = ['Threshold Detec.']

att_calc_strings = ['Up/Down by one']

att_control_strings = ['Even Distribution']

#def ThreshDetect(high_val, low_val, signal):
#    if max(signal) > high_val:
#        return -1
#    elif max(signal) < low_val:
#        return 1
#    else:
#        return 0

#def UpDownByOne(peak_status, current_att):
#    if peak_status == -1: # Too high
#        if current_att == 15:
#            return 15
#        else:
#            return current_att + 1
#    elif peak_status == 1: # Too low
#        if current_att == 0:
#            return 0
#        else:
#            return current_att - 1
#    else: # Juuuusssst right (or something bad happened)
#        return current_att 
#
#def EvenAttenuation(att_val):
#    preatt = int(att_val%2 + att_val/2)
#    posatt = int(att_val/2)
#    return preatt, posatt

class GmdSimIoc(PVGroup):
    """
    IOC for simulating the GMD ion/electron currents. Reads in arrays of 
    previously taken data and loops through them. 
    """
    def __init__(self, *args, datafile, **kwargs):
        #self.datafile = datafile
        with open(datafile) as csvfile:
            reader = csv.reader(csvfile,delimiter=',')
            waveforms = []
            for line in reader:
                waveforms.append(line)
        self.data_iterator = itertools.cycle(waveforms)
        super().__init__(*args, **kwargs)

    def current_att(self):
        preatt = att_strings.index(self.AMP_PREATTN1.value) 
        posatt = att_strings.index(self.AMP_POSATTN1.value) 

        return preatt + posatt

    async def write_att(self, preatt_val, posatt_val):
        await self.AMP_PREATTN1.write(att_strings[preatt_val])
        await self.AMP_POSATTN1.write(att_strings[posatt_val])
        
    DATA_GAIN = pvproperty(value=1.0, record='ai')

    HIGH_VAL = pvproperty(value=30000, record='longin')

    LOW_VAL = pvproperty(value=10000, record='longin')

    AMP_PREATTN1 = pvproperty(value=att_strings[0],
                              enum_strings=att_strings,
                              record='mbbi',
                              dtype=ChannelType.ENUM)

    AMP_POSATTN1 = pvproperty(value=att_strings[0],
                              enum_strings=att_strings,
                              record='mbbi',
                              dtype=ChannelType.ENUM)

    ATT_CALC_METHOD = pvproperty(value=att_calc_strings[0],
                                 enum_strings=att_calc_strings,
                                 record='mbbi',
                                 dtype=ChannelType.ENUM) 

    ENABLE_ATT_CONTROL = pvproperty(value=bi_strings[0],
                                    enum_strings=bi_strings,
                                    record='bi',
                                    dtype=ChannelType.ENUM)

    PEAK_CHECK_METHOD = pvproperty(value=peak_check_strings[0],
                                   enum_strings=peak_check_strings,
                                   record='mbbi',
                                   dtype=ChannelType.ENUM) 

    ENABLE_PEAK_SHARPEN = pvproperty(value=bi_strings[0],
                                     enum_strings=bi_strings,
                                     record='bi',
                                     dtype=ChannelType.ENUM)

    SHARPEN_K2 = pvproperty(value=5.0, record='ai')

    SHARPEN_K4 = pvproperty(value=434, record='ai')

    RAW_STREAM = pvproperty(value=[0.0]*4096, record='waveform')

    @RAW_STREAM.scan(period=.2, use_scan_field=True)
    async def RAW_STREAM(self, instance, async_lib):
        raw = next(self.data_iterator)
        ret = [int(val)*self.DATA_GAIN.value for val in raw]
        await instance.write(ret)
    
    STREAM = pvproperty(value=[0.0]*4096, record='waveform')

    @STREAM.scan(period=.2, use_scan_field=True)
    async def STREAM(self, instance, async_lib):
        raw = self.RAW_STREAM.value
        # In reality the signal will be attenuated prior to hitting the ADC,
        # so get our fake attenuated signal before applying signal processing
        # algorithms
        att1 = att_strings.index(self.AMP_PREATTN1.value)
        att2 = att_strings.index(self.AMP_POSATTN1.value)
        sig = calc_attn_signal(raw, att1, att2)
        ### Peak Sharpening
        if bi_strings.index(self.ENABLE_PEAK_SHARPEN.value):
            sig = PeakSharpen(sig, self.SHARPEN_K2.value)
#                               self.SHARPEN_K4.value)
        ### Automated attenuation control
        if bi_strings.index(self.ENABLE_ATT_CONTROL.value):
            if self.PEAK_CHECK_METHOD.value == peak_check_strings[0]:
                peak_status = ThreshDetect(self.HIGH_VAL.value,
                                           self.LOW_VAL.value,
                                           sig)
            else: # no other methods supported right now
                peak_status = 0
            # Calculate new attenuator state using selected method
            if self.ATT_CALC_METHOD.value == att_calc_strings[0]:
                curr_att = self.current_att()
                new_att = UpDownByOne(peak_status, curr_att)
            else: # No other calculation methods supported right now
                new_att = self.current_att()
            preatt, posatt = EvenAttenuation(new_att)
            await self.write_att(preatt, posatt)
        ret = sig
        await instance.write(ret)


if __name__ == '__main__':
    parser, split_args = template_arg_parser(
        default_prefix='EM1K0:GMD:',
        desc='Simulate the data stream of the GMD.',
        supported_async_libs=('asyncio',)
    )
    parser.add_argument('--datafile',
                        help='The .csv file the data is stored in',
                        required=True, type=str)
    args = parser.parse_args()
    ioc_options, run_options = split_args(args)
    ioc = GmdSimIoc(datafile=args.datafile, **ioc_options)
    ioc = GmdSimIoc(datafile=args.datafile, **ioc_options)
    run(ioc.pvdb, **run_options)
