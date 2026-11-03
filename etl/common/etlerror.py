class Etlerror(Exception):
    def __init__(self, location, track, error):
        self.location = location
        self.track = track
        self.error = error
