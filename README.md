pyfrank - python binding for iOS automation using frank.
==================================================

pyfrank is an API to interact with frank, the iOS automation framework.


#Installation

Option 1:

1. Clone this repo or download the sources

2. `cd pyfrank`

3. `python setup.py build`

4. `sudo python setup.py install`

Option 2:

`sudo pip install pyfrank`



#It's that simple
----------

```python
from pyfrank import *

# We are running a simulator with frank locally on port 32765
device = Device(host='127.0.0.1', port=32765)

# Get the view representing a tab-bar button with the label "Mail"
view = device.getView(UiQuery("tabBarButton", {'marked': "Mail" }))

# Touch the button
response = view.touch()

if isinstance(response, Success):
    logging.info("Test mail button succeeded!");
elif isinstance(response, Failure):
    logging.error("Test mail button failed: %s", response)
```

#The object model
----------

## Device
a device is the first entry point for interacting with frank. Its constructor receives the host and the port of the frank enabled device.


###Example:
```python
from pyfrank import *

device = Device("127.0.0.1", 32765)
    
# Type text into the keyboard
device.typeIntoKeyboard("abc")

# Execute an application on the device
device.appExec("appName", "arg1", "arg2", ...)

# Get the accesibility state
accessibilityEnabled = device.accessibilityCheck()

# Get the device orientation
orientation = device.getOrientation()
if orientation == Orientation.PORTRAIT:
    print "Portrait"
elif orientation == Orientation.LANDSCAPE:
    print "Landscape"

# Get the application layout graph
dump = device.dump()
```

## UiQuery
UiQuery is the view traversal DSL of frank's UiSpec. A view is located with a UiQuery.
pyfrank allows you to choose your preferred way of specifying a ui query.

###Example:
```python
from pyfrank import *

UiQuery({'view': 'UIImageView'}, {'marked': 'ProfilePicture'}) # The recommended way
UiQuery(('view', 'UIImageView'), ('marked', 'ProfilePicture))
UiQuery("view:'UIImageView' marked:'ProfilePicture'")
UiQuery('imageView', { 'marked': 'ProfilePicture' })
```

These represent the same ui query: "view:'UIImageView' marked:'ProfilePicture'". 
* We recommend to use the first two options as they automatically build and escapes the appropriate fields to conform with frank's UiQuery specifications.

    
###For more info on UiQuery - http://code.google.com/p/uispec/wiki/Documentation#UIQuery


## View
represents a view within an iOS application.
View provides a method to perform operations on a view or multiple views.


###Example:
```python
#Get the profile picture view
view = device.getView(UiQuery({'view': 'UIImageView'}, {'marked': 'ProfilePicture'}))

#Flash the profile picture
r = view.flash() 

#Test for success
if isinstance(r, Success):
    print "Flashed the profile picture!"
else:
    print "Failed flashing profile picture"

#Touch the profile picture
r = view.touch()


#Get the title text input view
input = device.getView(UiQuery({'view', 'UITextField'}, {'marked': 'Title'}))
    
r = input.setText("New title text")    

if isinstance(r, Success):
    print "Title input was changed successfully."
else:
    print "Failed changing title input"
```


#More information on frank
----------
http://testingwithfrank.com/

