# Copyright 2012 Do@. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are
# permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice, this list of
#       conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright notice, this list
#       of conditions and the following disclaimer in the documentation and/or other materials
#       provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY Do@ ``AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are those of the
# authors and should not be interpreted as representing official policies, either expressed
# or implied, of Do@.

__author__ = 'Daniel Ben-Zvi'

import sys
import urllib2
import logging
import json
import socket
import time
from exceptions import *
from contextlib import contextmanager
from threading import Event


'''
Python frank bindings
Created on Sep 09, 2012

@author: Daniel Ben-Zvi
'''



class Selector(object):
    """
    Selector interface

    Used for locating UI views.
    Implemented by UiQuery.
    """
    def engine(self):
        pass

    def query(self):
        pass

    def __repr__(self):
        return "%s(%s, %s)" % (self.__class__.__name__, self.engine(), self.query())


class Response(object):
    """
    Represents a response from frank
    The response may or may not conform to the standard response format (http://testingwithfrank.com/frankly.html)

    A standard frankly response contains an outcome property which is either 'SUCCESS' or 'FAILURE'.
    Depending on the value of outcome we will instantiate a Success or a Failure object.

    If the response is not a dictionary (not json) and thus not standard,
    the response data will be available through the outcome() property.
    """
    def __init__(self, data):
        self._data = data if type(data) == dict else { 'outcome': data }


    def get(self, key, default=None):
        """
        Gets a property from the underlying data dict.
        """
        return self._data.get(key, default)

    def raw(self):
        return self._data

    def outcome(self):
        return self.get('outcome')

    def __getattr__(self, item):
        return self.get(item)

    def __getitem__(self, item):
        return self.get(item)

    @staticmethod
    def parse(data):
        """
        Response factory.
        If the data is a standard frankly response (has an 'outcome' property), either a Success() or a Failure() will be generated
        If the data is non standard, a Response() will be generated
        """
        data = json.loads(data)

        if 'outcome' in data:
            if data['outcome'] == 'SUCCESS':
                return Success(data)
            else:
                return Failure(data)
        else:
            return Response(data)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self._data)

class Success(Response):
    """
    Returned by appExec or sendMessage
    """
    def results(self):
        return self.get('results')

class Failure(Response):
    """
    Returned by appExec or sendMessage when frank returns a failure
    """
    def reason(self):
        return self.get('reason')

    def details(self):
        return self.get('details')


class Orientation(Response):
    """
    Represents the device orientation (portrait or landscape)
    """
    PORTRAIT = 'portrait'
    LANDSCAPE = 'landscape'

    def orientation(self):
        return self.get('orientation')

    @staticmethod
    def parse(data):
        return Orientation(json.loads(data))

class Dump(Response):
    """
    Represents the entire application UI graph
    """
    def __str__(self):
        return str(self._data)

    @staticmethod
    def parse(data):
        return Dump(json.loads(data))

class Accessibility(Response):
    """
    Represents the accessibility state of the application
    """

    def enabled(self):
        return bool(self.get('accessibility_enabled'))

    @staticmethod
    def parse(data):
        return Accessibility(json.loads(data))




class Operation(object):
    """
    Represents an operation that can be performed on a View
    Used internally.
    """

    def __init__(self, method, *args):
        self.method_name = method
        self.arguments = args or []

    def __repr__(self):
        return "%s(%s, %s)" % (self.__class__.__name__, self.method_name, self.arguments)



class UiQuery(Selector):
    """
    The UiQuery selector
    The syntax is described here: http://testingwithfrank.com/selector_syntax.html
    """
    def __init__(self, *args):
        """
        Initialize the UiQuery
        @param args - The argument list. Every argument can be a string, dict, set or a tuple. for example:
                      UiQuery({'view': 'UIImageView'}, {'marked': 'ProfilePicture'})
                      UiQuery(('view', 'UIImageView'), ('marked', 'ProfilePicture))
                      UiQuery("view:'UIImageView' marked:'ProfilePicture'")
                      UiQuery('imageView', { 'marked': 'ProfilePicture' })

                      Will all affect the same view set.
        """
        l = list()
        for x in args:
            if type(x) == dict:
                l.extend([ "%s:%s" % (k,json.dumps(v)) for k,v in x.iteritems() ])
            elif type(x) == tuple or type(x) == set and len(x) == 2:
                l.append("%s:%s" % (x[0],json.dumps(x[1])))
            elif type(x) == str:
                l.append(x)
            else:
                raise ArgumentError("Unknown type passed to UiQuery: %s (%s)", type(x), x)

        self._query = ' '.join(l)

    def query(self):
        return self._query

    def engine(self):
        return "uiquery"


@contextmanager
def TimeSampler(actionDescription, callback = None, minTimeFilterMS = 0):
    st = time.time()
    yield
    et = time.time()
    duration =  1000*(et - st)
    if duration < minTimeFilterMS:
        return

    msg = 'Action %s took %.03fms' % (actionDescription, duration)

    if callback:
        callback(msg)
    else:
        logging.debug("%s", msg)


class Request(object):
    """
    Represents a request that is sent to frank
    """

    # Represents the uri of a specific operation and the response parser
    MAP =           ("/map",                 Response.parse)
    APP_EXEC=       ("/app_exec",            Response.parse)
    TYPE_KEYBOARD = ("/type_into_keyboard",  None)
    ACCESSIBILITY = ("/accessibility_check", Accessibility.parse)
    DUMP =          ("/dump",                Dump.parse)
    ORIENTATION =   ("/orientation",         Orientation.parse)

    def __init__(self, device):
        self._device = device
        self._complete = Event()
        self._error = None

    def _execute(self, query, data=None, timeout=15):
        """
        Execute a query to frank

        @param query - One of the query tuples as described in the class definition. ('/path', response_parser)
        @param data - A string or anything else. Anything else is serialized using JSON.
        @param timeout - Timeout for the request
        """
        try:
            self._complete.clear()

            queryPath, decoder = query

            url = "%s%s" % (self._device.uri(), queryPath)
            serialized = json.dumps(data) if data and type(data) != str else data

            logging.debug("Executing request to %s (data: <%s> %s)", url, type(data), serialized)

            with TimeSampler("query(%s)" % data.get('query', url) if data and type(data) == dict else url):
                fp = urllib2.urlopen(url, data=serialized, timeout=timeout)

            if fp:
                try:
                    if decoder:
                        rawResponse = fp.read()
                        return decoder(rawResponse)

                finally:
                    fp.close()
            else:
                raise FrankError("Unable to open %s - received an empty file descriptor", url)

        except socket.timeout, e:
            raise TimeoutError(e)
        except urllib2.HTTPError, e:
            raise HttpError(e)
        except urllib2.URLError, e:
            raise ConnectionError(e)


        finally:
            self._complete.set()


    def wait(self, timeout=None):
        """
        Wait for the completion of this operation
        Can be used for async
        """
        self._complete.wait(timeout)

    def map(self, selector, operation):
        obj = {
            'query': selector.query(),
            'operation': operation.__dict__,
            'selector_engine': selector.engine()
        }

        return self._execute(Request.MAP, obj)


    def typeIntoKeyboard(self, text):
        return self._execute(Request.TYPE_KEYBOARD, {'text_to_type': text })

    def accessibilityCheck(self):
        return self._execute(Request.ACCESSIBILITY)

    def getOrientation(self):
        return self._execute(Request.ORIENTATION)

    def dump(self):
        return self._execute(Request.DUMP)

    def appExec(self, name, *args):
        return self._execute(Request.APP_EXEC, str(Operation(name, *args)))








class View(object):
    """
    Represents a view control

    Example usage for flashing all the tabBarButton controls:

    view = device.getView(UiQuery("tabBarButton"))
    view.flash()
    """
    def __init__(self, selector, device):
        """
        @param selector - The view selector. Used to find the view. see Selector.
        @param device - The device context
        """
        self._selector = selector
        self._device = device

    def __getattr__(self, item):
        """
        Returns a method proxy lambda for easy of use and code readability.

        Example usage:
        View.touch("a", "b") will transform to View.sendMessage("touch", "a", "b")
        """
        if item[0] != '_':
            return lambda *k: self.sendMessage(item, *k)

    def sendMessage(self, method, *args):
        """
        Send a message to this view
        @param method - The method name
        @param args - Arguments to pass to the method.
        """

        return Request(self._device).map(self._selector, Operation(method, *args))

    def __repr__(self):
        return "%s(%s, %s)" % (self.__class__.__name__, self._selector, self._device)


class Device(object):
    """
    Represents a device with an embedded frank running

    Example usage for decision making according to the device orientation:

    device = Device('127.0.0.1', 32768)
    if device.getOrientation() == Orientation.PORTRAIT:
        view = device.getView(UiQuery("tabBarButton", { 'marked': 'Home' }))
        view.touch()
    """
    def __init__(self, host, port, name='iPhone'):
        """
        @param host - The hostname or IP address of the device
        @param port - The port frank listens to
        @param name - The name of the device - for cosmetic purposes
        """
        self._host = host
        self._port = port
        self._name = name

    def uri(self):
        return "http://%s:%s" % (self._host, self._port)

    def getView(self, selector):
        """
        Returns a view based on the selector query

        @param selector - A UiQuery describing the view path

        Returns a View
        """
        return View(selector, self)

    def dump(self):
        """
        Returns the application layout graph

        Returns dict
        """
        return Request(self).dump().raw()


    def typeIntoKeyboard(self, text):
        """
        Injects text into an open keyboard

        @param text - A string

        Does not return
        """

        Request(self).typeIntoKeyboard(text)

    def accessibilityCheck(self):
        """
        Checks if accessibility mode is enabled

        Returns bool
        """

        return Request(self).accessibilityCheck().enabled()

    def appExec(self, name, *args):
        """
        Executes an application on the device

        @param name - The name of the application
        @param args - Arguments that are passed to the application invocation.

        Returns either Success or Failure
        """

        return Request(self).appExec(name, *args)

    def getOrientation(self):
        """
        Returns the device orientation

        Returns either Orientation.PORTRAIT or Orientation.LANDSCAPE
        """

        return Request(self).getOrientation().orientation()

    def __repr__(self):
        return "%s('%s',%s,'%s')" % (self.__class__.__name__, self._host, self._port, self._name)


