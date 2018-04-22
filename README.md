# pi-radar
Touchscreen user interface for dump1090-mutability.
Tested on Raspberry Pi 3 with the official touchscreen.

Dependencies:
- access to aircraft.json file generated by [dump1090-mutability](https://github.com/mutability/dump1090)
- Python 3
- [kivy](https://kivy.org)
- [mapview](https://github.com/kivy-garden/garden.mapview/) from [kivy-garden](https://kivy.org/docs/api-kivy.garden.html)

Usage:

````
from radar import RadarMapView
from kivy.app import runTouchApp

runTouchApp(RadarMapView(zoom=8, lat=51.44, lon=-1.03, url="http://192.168.1.222/dump1090/data/aircraft.json"))
````

Tap on any aircraft icon once to show the callsign and again to show altitude, rate of climb, speed and track.
