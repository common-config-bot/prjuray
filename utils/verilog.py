#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2020-2022 F4PGA Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

import sys
import random
import re


def top_harness(DIN_N, DOUT_N, f=sys.stdout):
    f.write('''
module top(input clk, stb, di, output do);
    localparam integer DIN_N = %d;
    localparam integer DOUT_N = %d;

    reg [DIN_N-1:0] din;
    wire [DOUT_N-1:0] dout;

    reg [DIN_N-1:0] din_shr;
    reg [DOUT_N-1:0] dout_shr;

    always @(posedge clk) begin
        din_shr <= {din_shr, di};
        dout_shr <= {dout_shr, din_shr[DIN_N-1]};
        if (stb) begin
            din <= din_shr;
            dout_shr <= dout;
        end
    end

    assign do = dout_shr[DOUT_N-1];

    roi roi (
        .clk(clk),
        .din(din),
        .dout(dout)
    );
endmodule
''' % (DIN_N, DOUT_N))


def top_harness_clk(DCLK_N, DIN_N, DOUT_N, f=sys.stdout):
    f.write('''
module top(input [DCLK_N-1:0] clk, stb, di, output do);
    localparam integer DCLK_N = %d;
    localparam integer DIN_N = %d;
    localparam integer DOUT_N = %d;

    reg [DIN_N-1:0] din;
    wire [DOUT_N-1:0] dout;

    reg [DIN_N-1:0] din_shr;
    reg [DOUT_N-1:0] dout_shr;

    always @(posedge clk[0]) begin
        din_shr <= {din_shr, di};
        dout_shr <= {dout_shr, din_shr[DIN_N-1]};
        if (stb) begin
            din <= din_shr;
            dout_shr <= dout;
        end
    end

    assign do = dout_shr[DOUT_N-1];

    roi roi (
        .clk(clk),
        .din(din),
        .dout(dout)
    );
endmodule
''' % (DCLK_N, DIN_N, DOUT_N))


def instance(mod, name, ports, params={}, sort=True, string_buffer=sys.stdout):
    # TODO: make this print nicer
    tosort = sorted if sort else lambda x: x
    print('    %s' % mod, file=string_buffer)
    if len(params):
        print('        #(', file=string_buffer)
        for i, (paramk, paramv) in enumerate(tosort(params.items())):
            comma = '' if i == len(params) - 1 else ','
            print(
                '            .%s(%s)%s' % (paramk, paramv, comma),
                file=string_buffer)
        print('        )', file=string_buffer)
    print('        %s (' % name, file=string_buffer)
    for i, (portk, portv) in enumerate(tosort(ports.items())):
        comma = '' if i == len(ports) - 1 else ','
        print(
            '            .%s(%s)%s' % (portk, portv, comma),
            file=string_buffer)
    print('        );', file=string_buffer)


def quote(s):
    return '"' + s + '"'


def unquote(s):
    assert s[0] == '"' and s[-1] == '"'
    return s[1:-1]


def to_int(s):
    value = 0

    match = re.search(r'^(\d+)\'([sS]*)([bBoOdDhH])(.*)', str(s))

    if match:
        width = int(match.group(1))
        signed = match.group(2)
        radix = match.group(3)
        value = match.group(4)

        # Convert to int type
        if re.match(r'[bB]', radix):
            value = int(value, 2)
        elif re.match(r'[oO]', radix):
            value = int(value, 8)
        elif re.match(r'[dD]', radix):
            value = int(value, 10)
        elif re.match(r'[hH]', radix):
            value = int(value, 16)
        else:
            raise ValueError('Don\'t know how to interpret input %s' % (s))

        # Truncate to `width` bits
        value &= 2**width - 1
    else:
        value = int(s)

    return value


def parsei(s):
    if s == "1'b0":
        return 0
    elif s == "1'b1":
        return 1
    else:
        assert 0, 'FIXME'


def parse_bitstr(s):
    n, postfix = s.split("'")
    n = int(n)
    assert postfix[0] == 'b'
    bitstr = postfix[1:]
    assert len(bitstr) == n
    return [int(x) for x in bitstr]


def vrandbit():
    if random.randint(0, 1):
        return "1'b1"
    else:
        return "1'b0"


def vrandbits(n):
    ret = "%u'b" % n
    for _i in range(n):
        ret += str(random.randint(0, 1))
    return ret
