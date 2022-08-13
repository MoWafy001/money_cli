from src import app
import sys

command = sys.argv[1:]

try:
  app.handel_command(command)
except KeyboardInterrupt:
  pass
