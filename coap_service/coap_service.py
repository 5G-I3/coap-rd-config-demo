#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright (C) 2019 Freie Universitaet Berlin
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.

import argparse
import asyncio
import json
import logging
import urllib.parse

from aiocoap import *
from aiocoap.numbers import media_types
from aiocoap.util import linkformat

logging.basicConfig(level=logging.INFO)

event_loop = None


def link_to_json(link):
    return json.dumps(
            {k: v for k,v in link.items() if k in ["addr", "path"]}
        ).encode("utf-8")


async def register(protocol, config_node, target_node):
    request = Message(code=POST, mtype=CON) 
    request.set_request_uri(config_node["target"]["href"])
    request.payload = link_to_json(target_node["points"])  
    request.opt.content_format = 50 # json
    pr = protocol.request(request)
    resp = await pr.response
    print("Tried to register {} with {}:".format(
            target_node["points"]["href"],
            config_node["target"]["href"],
        ), resp)


def incoming_observation(protocol, response):
    global event_loop
    links = {}
    nodes = {}

    if response.code.is_successful():
        cf = response.opt.content_format
        mime_type = media_types.get(cf, "type %s" % cf)
        mime_type, *parameters = mime_type.split(";")
        if mime_type == "application/link-format":
            ls = linkformat.parse(response.payload.decode('utf-8'))
            for link in ls.links:
                link = link.as_json_data()
                pr = urllib.parse.urlparse(link["href"])
                link["addr"] = pr.netloc
                link["path"] = pr.path
                links[link["href"]] = link 
    for link in links.values():
        path = link["path"]
        node, sense, *rest = path.strip("/").split("/")
        if node not in nodes:
            nodes[node] = {sense: link}
        else:
            nodes[node][sense] = link
    if "btn" in nodes and "target" in nodes["btn"] and \
       "dsp" in nodes and "points" in nodes["dsp"]:
        asyncio.ensure_future(register(protocol, nodes["btn"],
                                       nodes["dsp"]))
    if "dsp" in nodes and "target" in nodes["dsp"] and \
       "dino" in nodes and "points" in nodes["dino"]:
        asyncio.ensure_future(register(protocol, nodes["dsp"],
                                       nodes["dino"]))



async def main(addr):
    protocol = await Context.create_client_context()

    print('coap://[{addr}]/resource-lookup'.format(addr=addr))
    request = Message(code=GET,
                      uri='coap://[{addr}]/resource-lookup'.format(addr=addr),
                      observe=0)

    try:
        pr = protocol.request(request)
        observation_is_over = asyncio.Future()

        pr.observation.register_errback(observation_is_over.set_result)
        pr.observation.register_callback(lambda data, protocol=protocol:
                incoming_observation(protocol, data)
            )
        print("waiting for response")
        resp = await pr.response
        incoming_observation(protocol, resp)
        exit_reason = await observation_is_over
        print(exit_reason)
    finally:
        if not pr.observation.cancelled:
            pr.observation.cancel()
            await asyncio.sleep(1)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("addr")
    args = p.parse_args()
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(main(args.addr))
