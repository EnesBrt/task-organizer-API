#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# megaparsex                                                                   #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program is a parser and associated utilities.                           #
#                                                                              #
# copyright (C) 2017 William Breaden Madden, name by Liam Moore                #
#                                                                              #
# This software is released under the terms of the GNU General Public License  #
# version 3 (GPLv3).                                                           #
#                                                                              #
# This program is free software: you can redistribute it and/or modify it      #
# under the terms of the GNU General Public License as published by the Free   #
# Software Foundation, either version 3 of the License, or (at your option)    #
# any later version.                                                           #
#                                                                              #
# This program is distributed in the hope that it will be useful, but WITHOUT  #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or        #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for     #
# more details.                                                                #
#                                                                              #
# For a copy of the GNU General Public License, see                            #
# <http://www.gnu.org/licenses/>.                                              #
#                                                                              #
################################################################################
"""

import os
import requests
import subprocess
import sys
if sys.version_info >= (3, 0):
    import builtins as _builtins
else:
    import __builtin__ as _builtins

import AWRS
import psutil

name    = "megaparsex"
version = "2018-02-12T2333Z"

def trigger_keyphrases(
    text                          = None,  # input text to parse
    keyphrases                    = None,  # keyphrases for parsing input text
    response                      = None,  # optional text response on trigger
    function                      = None,  # optional function on trigger
    kwargs                        = None,  # optional function keyword arguments
    confirm                       = False, # optional return of confirmation
    confirmation_prompt           = "Do you want to continue? (y/n)",
    confirmation_feedback_confirm = "confirm",
    confirmation_feedback_deny    = "deny"
    ):
    """
    Parse input text for keyphrases. If any keyphrases are found, respond with
    text or by seeking confirmation or by engaging a function with optional
    keyword arguments. Return text or True if triggered and return False if not
    triggered. If confirmation is required, a confirmation object is returned,
    encapsulating a function and its optional arguments.
    """
    if any(pattern in text for pattern in keyphrases):
        if confirm:
            return confirmation(
                prompt           = confirmation_prompt,
                feedback_confirm = confirmation_feedback_confirm,
                feedback_deny    = confirmation_feedback_deny,
                function         = function,
                kwargs           = kwargs
            )
        if function and not kwargs:
            result = function()
        elif function and kwargs:
            result = function(**kwargs)
        else:
            result = None
        if response:
            return response
        elif not response and result:
            return str(result)
        else:
            return True
    else:
        return False

def parse(
    text   = None,
    humour = 75
    ):
    """
    Parse input text using various triggers, some returning text and some for
    engaging functions. If triggered, a trigger returns text or True if and if
    not triggered, returns False. If no triggers are triggered, return False, if
    one trigger is triggered, return the value returned by that trigger, and if
    multiple triggers are triggered, return a list of the values returned by
    those triggers.

    Options such as humour engage or disengage various triggers.
    """
    triggers = []

    # general

    if humour >= 75:
        triggers.extend([
            trigger_keyphrases(
                text       = text,
                keyphrases = [
                             "image"
                             ],
                response   = "http://i.imgur.com/MiqrlTh.jpg"
            ),
            trigger_keyphrases(
                text       = text,
                keyphrases = [
                             "sup",
                             "hi"
                             ],
                response   = "sup home bean"
            ),
            trigger_keyphrases(
                text       = text,
                keyphrases = [
                             "thanks",
                             "thank you"
                             ],
                response   = "you're welcome, boo ;)"
            )
        ])

    # information

    triggers.extend([
        trigger_keyphrases(
            text       = text,
            keyphrases = [
                         "where are you",
                         "IP",
                         "I.P.",
                         "IP address",
                         "I.P. address",
                         "ip address"
                         ],
            function   = report_IP
        ),
        trigger_keyphrases(
            text       = text,
            keyphrases = [
                         "how are you",
                         "are you well",
                         "status"
                         ],
            function   = report_system_status,
            kwargs     = {"humour": humour}
        ),
        trigger_keyphrases(
            text       = text,
            keyphrases = [
                         "heartbeat"
                         ],
            function   = heartbeat_message
        ),
        trigger_keyphrases(
            text       = text,
            keyphrases = [
                         "METAR"
                         ],
            function   = report_METAR,
            kwargs     = {"text": text}
        ),
        trigger_keyphrases(
            text       = text,
            keyphrases = [
                         "TAF"
                         ],
            response   = report_TAF,
            kwargs     = {"text": text}
        ),
        trigger_keyphrases(
            text       = text,
            keyphrases = [
                         "rain"
                         ],
            response   = report_rain_times,
            kwargs     = {"text": text}
        )
    ])

    # actions

    triggers.extend([
        trigger_keyphrases(
            text       = text,
            keyphrases = [
                         "command",
                         "run command",
                         "engage command",
                         "execute command"
                         ],
            response   = command()
        ),
        trigger_keyphrases(
            text                          = text,
            keyphrases                    = [
                                            "restart"
                                            ],
            function                      = restart,
            confirm                       = True,
            confirmation_prompt           = "Do you want to restart this "
                                            "program? (y/n)",
            confirmation_feedback_confirm = "confirm restart",
            confirmation_feedback_deny    = "deny restart"
        )
    ])

    if any(triggers):
        responses = [response for response in triggers if response]
        if len(responses) > 1:
            return responses
        else:
            return responses[0]
    else:
        return False

def parse_networking(
    text    = None
    ):
    """
    Access address and port parameters via the builtins or __builtin__ module.
    Relish the nonsense.
    """
    try:
        address = _builtins.address
        port    = _builtins.port
    except:
        address = None
        port    = None
    triggers = []
    if address and port:
        triggers.extend([
            trigger_keyphrases(
                text                          = text,
                keyphrases                    = [
                                                "reverse SSH",
                                                "reverse ssh"
                                                ],
                function                      = engage_command,
                kwargs                        = {"command": "ssh -R " + str(port) + ":localhost:22 " + address},
                confirm                       = True,
                confirmation_prompt           = "Do you want to reverse SSH "
                                                "connect? (y/n)",
                confirmation_feedback_confirm = "confirm reverse SSH connect: "
                                                "ssh localhost -p " + str(port),
                confirmation_feedback_deny    = "deny reverse SSH connect"
            )
        ])
    if any(triggers):
        responses = [response for response in triggers if response]
        if len(responses) > 1:
            return responses
        else:
            return responses[0]
    else:
        return False

def multiparse(
    text         = None,
    parsers      = [parse],
    help_message = None
    ):
    """
    Parse input text by looping over a list of multiple parsers. If one trigger
    is triggered, return the value returned by that trigger, if multiple
    triggers are triggered, return a list of the values returned by those
    triggers. If no triggers are triggered, return False or an optional help
    message.
    """
    responses = []
    for _parser in parsers:
        response = _parser(text = text)
        if response is not False:
            responses.extend(response if response is list else [response])
    if not any(responses):
        if help_message:
            return help_message
        else:
            return False
    else:
        if len(responses) > 1:
            return responses
        else:
            return responses[0]

class confirmation(
    object
    ):
    """
    A confirmation object contains the ability to detect a confirmation or a
    denial in input text, and contains a prompt, a function to run, with
    optional keyword arguments, and feedback on confirmation or denial.
    """
    def __init__(
        self,
        prompt           = "Do you want to continue? (y/n)",
        feedback_confirm = "confirm",
        feedback_deny    = "deny",
        function         = None,
        kwargs           = None
        ):
        self._prompt           = prompt
        self._feedback_confirm = feedback_confirm
        self._feedback_deny    = feedback_deny
        self._function         = function
        self._kwargs           = kwargs
        self._feedback         = None
        self._confirmed        = None

    def prompt(
        self
        ):
        return self._prompt

    def feedback(
        self
        ):
        if self._confirmed is True:
            self._feedback = self._feedback_confirm
        if self._confirmed is False:
            self._feedback = self._feedback_deny
        return self._feedback

    def test(
        self,
        text = None
        ):
        """
        Parse input text as a confirmation or denial. If a confirmation is
        detected, return True and set internal confirmed state to True and if a
        denial is detected, return False and set internal confirmed state to
        False if a denial is detected, and if neither a confirmation nor a
        denial is detected, return None and set internal confirmed state to
        None.
        """
        if text is None:
            self._confirmed = None
            return None
        else:
            if text.lower() in ["y"]:
                self._confirmed = True
                return True
            elif text.lower() in ["n"]:
                self._confirmed = False
                return False
            else:
                self._confirmed = None
                return None

    def confirmed(
        self
        ):
        """
        Return internal confirmation state.
        """
        return self._confirmed

    def run(
        self
        ):
        """
        Engage contained function with optional keyword arguments.
        """
        if self._function and not self._kwargs:
            return self._function()
        if self._function and self._kwargs:
            return self._function(**self._kwargs)

    def __str__(
        self
        ):
        if self._kwargs is not None:
            kwargs = self._kwargs
            kwargs = ", ".join(
                [str(key) + "=" + str(kwargs[key]) for key in kwargs]
            )
        else:
            kwargs = ""
        return "confirmation: function: {function}({kwargs})".format(
            function = self._function.__name__,
            kwargs   = kwargs
        )

class command(
    object
    ):
    """
    A command object contains the ability to request an input that is to be run
    as a command, and contains a prompt. When it receives the command, it runs
    the command.
    """
    def __init__(
        self,
        prompt     = "input command:",
        command    = None,
        background = True
        ):
        self._prompt     = prompt
        self._command    = command
        self._background = background

    def prompt(
        self
        ):
        return self._prompt

    def engage_command(
        self,
        command    = None,
        background = None
        ):
        if not command:
            command = self._command,
        if background is None:
            background = self._background
        output = engage_command(
            command    = command,
            background = background
        )
        return output

def get_input(
    prompt = None
    ):
    if sys.version_info >= (3, 0):
        return input(prompt)
    else:
        return raw_input(prompt)

def engage_command(
    command    = None,
    background = True
    ):
    if background:
        subprocess.Popen(
            [command],
            shell      = True,
            executable = "/bin/bash"
        )
        return None
    elif not background:
        process = subprocess.Popen(
            [command],
            shell      = True,
            executable = "/bin/bash",
            stdout     = subprocess.PIPE
        )
        process.wait()
        output, errors = process.communicate()
        return output
    else:
        return None

def report_IP(
    country = True,
    IP_only = False
    ):
    IP = "unknown"
    try:
        data_IP_website = requests.get("http://ipinfo.io/json")
        data_IP         = data_IP_website.json()
        IP              = data_IP["ip"]
        country         = data_IP["country"]
        if IP_only:
            text = IP
        else:
            text = "IP address: " + IP
            if country:
                text = text + " (" + country + ")"
        return text
    except:
        return "IP address: unknown"

def report_METAR(
    text = None
    ):
    if not text:
        return "no station specified"
    words = text.split()
    try:
        identifier = words[words.index("METAR") + 1]
    except:
        identifier = None
    if not identifier:
        try:
            report = AWRS.METAR()
        except:
            report = None
    else:
        try:
            report = AWRS.METAR(identifier = identifier)
        except:
            report = None
    if not report:
        return "METAR: unknown"
    else:
        return "METAR: " + report["METAR"]

def report_TAF(
    text = None
    ):
    if not text:
        return "no station specified"
    words = text.split()
    try:
        identifier = words[words.index("TAF") + 1]
    except:
        identifier = None
    if not identifier:
        try:
            report = AWRS.TAF()
        except:
            report = None
    else:
        try:
            report = AWRS.TAF(identifier = identifier)
        except:
            report = None
    if not report:
        return "TAF: unknown"
    else:
        return "TAF:" + report["TAF"]

def report_rain_times(
    text = None
    ):
    if not text:
        return "no station specified"
    words = text.split()
    try:
        identifier = words[words.index("rain") + 1]
        try:
            response = AWRS.rain_human_readable_datetimes(
                identifier    = identifier,
                return_list   = False,
                return_string = True
            )
        except:
            return "rain forecast: unknown"
    except:
        identifier = None
        try:
            response = AWRS.rain_human_readable_datetimes(
                return_list   = False,
                return_string = True
            )
        except:
            return "rain forecast: unknown"
    if not response:
        return "no rain forcast"
    else:
        return "rain forecast times: " + response

def report_system_status(
    humour = 75
    ):
    try:
        CPU           = psutil.cpu_percent(interval = 1)
        system_memory = psutil.virtual_memory().percent
        drive         = psutil.disk_usage("/").percent
        report = "CPU: {CPU} %\n"\
                 "system memory: {system_memory} %\n"\
                 "drive: {drive} %".format(
            CPU           = str(CPU),
            system_memory = str(system_memory),
            drive         = str(drive)
        )
        if humour >= 75:
            if CPU > 90:
                report = report + "\noot ma nut mate"
            else:
                report = report + "\nnae bad fam"
        return report
    except:
        return "unknown"

def heartbeat_message(
    humour = 75
    ):
    message                                   =\
        "heartbeat\n\n"                       +\
        report_IP()                           +\
        "\n\n"                                +\
        report_system_status(humour = humour)
    return message

def restart():
    import __main__
    os.execv(__main__.__file__, sys.argv)
