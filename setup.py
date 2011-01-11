from distutils.core import setup
import py2exe

setup(
    name = 'KaeserSAMConnect',
    description = 'Tool to connect to Kaeser SAM controller',
    version = '0.2',

    windows = [
                  {
                      'script': 'SAMConnectApp.py',
                      'icon_resources': [(1, "SAMConnect.ico")]

                  }
                ],

    options = {
                  'py2exe': {
                      'packages':'encodings',
                      'includes': 'cairo, pango, pangocairo, atk, gobject',
                  }
                },

    data_files=[
                    'SAMView.glade',
                    'com-uit.png', 
                    'com-nullast.png',
                    'com-vollast.png',
                    'com-alarm.png', 
                ]
)
