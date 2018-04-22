from aircraft import list_aircraft
from kivy.garden.mapview import MapView, MarkerMapLayer, MapMarkerPopup
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.bubble import Bubble
from kivy.clock import Clock
from kivy.base import runTouchApp


class Aircraft:
    pass


class AircraftMarker(MapMarkerPopup):

    def __init__(self):
        self.full_label = False
        super().__init__()

    def on_release(self, *args):
        if self.is_open:
            if self.full_label:
                self.full_label = False
                self.is_open = False
            else:
                self.full_label = True
        else:
            self.is_open = True
            self.full_label = False


class RadarMapView(MapView):

    def __init__(self, lat=51.5, lon=0, zoom=8, url="http://localhost/dump1090/data/aircraft.json", interval=1):
        self.aircraft_layer = MarkerMapLayer()
        self.update_in_progress = False
        self.list_of_tracked_aircraft = []
        self.aircraft_markers = []
        self.url = url
        super().__init__(lat=lat, lon=lon, zoom=zoom)
        self.add_layer(self.aircraft_layer)
        self.update_aircraft(0)
        Clock.schedule_interval(self.update_aircraft, interval)

    def update_aircraft(self, time):
        if self.update_in_progress:
            return
        self.update_in_progress = True
        list_of_aircraft = list_aircraft(self.url)

        # Update tracked aircraft and mark stale ones as inactive
        for a_tracked_aircraft in self.list_of_tracked_aircraft:
            aircraft_active = False
            for an_aircraft in list_of_aircraft:
                if an_aircraft["hex"] == a_tracked_aircraft.hex:
                    a_tracked_aircraft.data = an_aircraft
                    aircraft_active = True
                    break
            a_tracked_aircraft.active = aircraft_active

        # Add newly detected aircraft
        for an_aircraft in list_of_aircraft:
            aircraft_tracked = False
            for a_tracked_aircraft in self.list_of_tracked_aircraft:
                if a_tracked_aircraft.hex == an_aircraft["hex"]:
                    aircraft_tracked = True
                    break
            if not aircraft_tracked:
                a_tracked_aircraft = Aircraft()
                a_tracked_aircraft.hex = an_aircraft["hex"]
                a_tracked_aircraft.active = True
                a_tracked_aircraft.data = an_aircraft
                self.list_of_tracked_aircraft.append(a_tracked_aircraft)
                print("New track:", a_tracked_aircraft.data)

        # Set up markers
        for a_tracked_aircraft in self.list_of_tracked_aircraft:
            active = a_tracked_aircraft.active
            data = a_tracked_aircraft.data
            position_known = "lat" in data and "lon" in data and "track" in data
            has_marker = hasattr(a_tracked_aircraft, "marker")

            if active and position_known:
                if has_marker:
                    marker = a_tracked_aircraft.marker
                else:
                    marker = AircraftMarker()
                    marker.anchor_x = 0.5
                    marker.anchor_y = 0.5
                    a_tracked_aircraft.marker = marker
                    marker.popup_size = (80, 25)
                    a_tracked_aircraft.labelmode = 1
                    label = Label()
                    bubble = Bubble()
                    label.color = (1, 1, 0, 1)
                    label.outline_color = (0, 0, 0, 1)
                    bubble.add_widget(label)
                    marker.add_widget(bubble)
                    a_tracked_aircraft.label = label
                if hasattr(a_tracked_aircraft, "label"):
                    label = a_tracked_aircraft.label
                    if "flight" in data:
                        label.text = data["flight"]
                    else:
                        label.text = "unknown"
                    if marker.full_label:
                        marker.popup_size = (80, 100)
                        if "altitude" in data:
                            label.text = label.text + \
                                "\nALT: {}".format(data["altitude"])
                        if "vert_rate" in data:
                            label.text = label.text + \
                                "\nRoC: {}".format(data["vert_rate"])
                        if "track" in data:
                            label.text = label.text + \
                                "\nTRK: {}".format(data["track"])
                        if "speed" in data:
                            label.text = label.text + \
                                "\nSPD: {}".format(data["speed"])
                    else:
                        marker.popup_size = (80, 25)

                marker.source = "icons/plane{}.png".format(
                    round(a_tracked_aircraft.data["track"]/10)*10)
                marker.lat = a_tracked_aircraft.data["lat"]
                marker.lon = a_tracked_aircraft.data["lon"]
                print("Tracked aircraft data:", a_tracked_aircraft.data)
                if not has_marker:
                    self.add_marker(
                        a_tracked_aircraft.marker, layer=self.aircraft_layer)
            else:
                if has_marker:
                    print("Removing marker:", a_tracked_aircraft.hex)
                    self.remove_marker(a_tracked_aircraft.marker)
                    delattr(a_tracked_aircraft, "marker")
                if not active:
                    print("Lost contact:", a_tracked_aircraft.hex)
                    self.list_of_tracked_aircraft.remove(a_tracked_aircraft)
        self.aircraft_layer.reposition()
        self.update_in_progress = False


if __name__ == "__main__":
    runTouchApp(RadarMapView())
