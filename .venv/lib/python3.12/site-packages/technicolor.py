################################################################################
#                                                                              #
# technicolor                                                                  #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program provides color logging in Python.                               #
#                                                                              #
# copyright (C) 2014 William Breaden Madden                                    #
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

name    = "technicolor"
version = "2017-01-16T1544Z"

import ctypes
import logging
import os
import inspect
import functools
 
class ColorisingStreamHandler(logging.StreamHandler):

    # color names to indices
    color_map = {
        "black":   0,
        "red":     1,
        "green":   2,
        "yellow":  3,
        "blue":    4,
        "magenta": 5,
        "cyan":    6,
        "white":   7,
    }

    # level colour specifications
    # syntax: logging.level: (background color, foreground color, bold)
    level_map = {
        logging.DEBUG:    (None,   "blue",    False),
        logging.INFO:     (None,   "white",   False),
        logging.WARNING:  (None,   "yellow",  False),
        logging.ERROR:    (None,   "red",     False),
        logging.CRITICAL: ("red",  "white",   True),
    }

    # control sequence introducer
    CSI = "\x1b["

    # normal colours
    reset = "\x1b[0m"
 
    def istty(self):
        isatty = getattr(self.stream, "isatty", None)
        return isatty and isatty()
 
    def emit(self, record):
        try:
            message = self.format(record)
            stream  = self.stream
            if not self.istty:
                stream.write(message)
            else:
                self.output_colorized(message)
            stream.write(getattr(self, "terminator", "\n"))
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
 
    def output_colorized(self, message):
        self.stream.write(message)
 
    def colorize(self, message, record):
        if record.levelno in self.level_map:
            background_color, \
            foreground_color, \
            bold = self.level_map[record.levelno]
            parameters = []
            if background_color in self.color_map:
                parameters.append(str(self.color_map[background_color] + 40))
            if foreground_color in self.color_map:
                parameters.append(str(self.color_map[foreground_color] + 30))
            if bold:
                parameters.append("1")
            if parameters:
                message = "".join((
                    self.CSI,
                    ";".join(parameters),
                    "m",
                    message,
                    self.reset
                ))
        return message
 
    def format(self, record):
        message = logging.StreamHandler.format(self, record)
        if self.istty:
            # Do not colorize traceback.
            parts    = message.split("\n", 1)
            parts[0] = self.colorize(parts[0], record)
            message  = "\n".join(parts)
        return(message)

def log(function):

    @functools.wraps(function)
    def decoration(
        *args,
        **kwargs
        ):
        # Get the names of all of the function arguments.
        arguments = inspect.getcallargs(function, *args, **kwargs)
        logging.debug(
            "function '{function_name}' called by '{caller_name}' with arguments:"
            "\n{arguments}".format(
                function_name = function.__name__,
                caller_name   = inspect.stack()[1][3],
                arguments     = arguments
            ))
        result = function(*args, **kwargs)
        logging.debug("function '{function_name}' result: {result}\n".format(
            function_name = function.__name__,
            result        = result
        ))

    return(decoration)
