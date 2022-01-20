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

from utils import xjson


def load_tiles(tiles_fn):
    '''
    "$type $tile $grid_x $grid_y $typed_sites"
    typed_sites: foreach t $site_types s $sites
    '''
    tiles = list()

    with open(tiles_fn) as f:
        for line in f:
            # CLBLM_L CLBLM_L_X10Y98 30 106 SLICEL SLICE_X13Y98 SLICEM SLICE_X12Y98
            record = line.split()
            tile_type, tile_name, grid_x, grid_y, skip_tile = record[0:5]
            grid_x, grid_y = int(grid_x), int(grid_y)
            skip_tile = int(skip_tile) != 0
            sites = {}
            clock_region = None
            if len(record) >= 6:
                clock_region = record[5]
                if clock_region == "NA":
                    clock_region = None
                for i in range(6, len(record), 2):
                    site_type, site_name = record[i:i + 2]
                    sites[site_name] = site_type

            if not skip_tile:
                tile = {
                    'type': tile_type,
                    'name': tile_name,
                    'grid_x': grid_x,
                    'grid_y': grid_y,
                    'sites': sites,
                    'clock_region': clock_region,
                }
            else:
                # Replace tiles within the exclude_roi with NULL tiles to
                # ensure no gaps in the tilegrid.
                #
                # The name will reflect the original tile.
                tile = {
                    'type': 'NULL',
                    'name': tile_name,
                    'grid_x': grid_x,
                    'grid_y': grid_y,
                    'sites': {},
                    'clock_region': clock_region,
                }

            tiles.append(tile)

    return tiles


def load_pin_functions(pin_func_fn):
    pin_functions = {}

    with open(pin_func_fn) as f:
        for line in f:
            site, pin, pin_func = line.split()
            if site not in pin_functions:
                pin_functions[site] = {}

            pin_functions[site][pin] = pin_func

    return pin_functions


def make_database(tiles, pin_func):
    # tile database with X, Y, and list of sites
    # tile name as keys
    database = dict()

    for tile in tiles:
        database[tile["name"]] = {
            "type": tile["type"],
            "sites": tile["sites"],
            "grid_x": tile["grid_x"],
            "grid_y": tile["grid_y"],
            "bits": {},
            "pin_functions": {},
        }

        if tile["clock_region"]:
            database[tile["name"]]["clock_region"] = tile["clock_region"]

        for site in database[tile["name"]]["sites"]:
            if site in pin_func:
                database[tile["name"]]["pin_functions"][site] = pin_func[site]

    return database


def run(tiles_fn, pin_func_fn, json_fn, verbose=False):
    # Load input files
    tiles = load_tiles(tiles_fn)

    # Read site map
    pin_func = load_pin_functions(pin_func_fn)

    # Index input
    database = make_database(tiles, pin_func)

    # Save
    xjson.pprint(open(json_fn, 'w'), database)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate tilegrid.json from bitstream deltas')

    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument('--out', default='/dev/stdout', help='Output JSON')
    parser.add_argument(
        '--tiles',
        default='tiles.txt',
        help='Input tiles.txt tcl output',
        required=True)
    parser.add_argument(
        '--pin_func', help='List of sites with pin functions', required=True)
    args = parser.parse_args()

    run(args.tiles, args.pin_func, args.out, verbose=args.verbose)


if __name__ == '__main__':
    main()
