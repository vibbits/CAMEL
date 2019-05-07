import sys
import os
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))

from Camel import app as application

if __name__ == '__main__':
    application.run(debug=True)


