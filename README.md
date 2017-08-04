# msr
Munich stream ripper (Python 3.6) creates timelapses from 2 streams: wetter.com (Hauptbahnhof) and ludwigbeck.de (Marienplatz)

usage: .py [-h] --source SOURCE [--debug DEBUG]
optional arguments:
  -h, --help       show help message
  --source SOURCE  0 - wetter.com, 1 - ludwigbeck.de
  --debug DEBUG    0 - default, 1 - fade in/out stage, 2 - merge files
                   
TODO:
- "Upload to youtube" feature
- Restart process automatically upon completion
