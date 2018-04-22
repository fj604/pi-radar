from radar import RadarMapView
from kivy.app import runTouchApp

runTouchApp(RadarMapView(zoom=8, lat=51.44, lon=-1.03, url="http://192.168.1.222/dump1090/data/aircraft.json"))
