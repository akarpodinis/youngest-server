import logging
import os
import re
import signal
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from types import FrameType
from typing import Any, override

DATA_DIRECTORY = '/data'
DATE_PATTERN = r'(\d{1,2})-(\d{1,2})-(\d{2,4})'
SERVER_PORT = 8000

logger = logging.getLogger('youngest-server')
logging.basicConfig(
    format='%(levelname)-8s %(message)s',  # Pad logging format for the widest level CRITICAL
    level=os.getenv('LOGGING_LEVEL', 'INFO')
)


class FileHandler(BaseHTTPRequestHandler):
    error_message_format = '%(message)s'

    @override
    def log_message(self, format: str, *args: Any):
        logger.info(format, *args)

    def do_GET(self):
        logger.info('Handling request on %s', self.path)
        if self.path != '/':
            logger.info('Unrecognized path, 404')
            self.send_error(404)
            return

        try:
            files = os.listdir(DATA_DIRECTORY)
            if not files:
                logger.warning('No objects in /data, 404')
                self.send_error(404)
                return

            # Find youngest file based on mm-dd-yyyy date
            youngest = None
            youngest_date = None

            logger.info('Scanning for files')
            for filename in files:
                logger.debug(filename)
                if not os.path.isfile(os.path.join(DATA_DIRECTORY, filename)):
                    continue

                match = re.search(DATE_PATTERN, filename)
                if match:
                    month, day, year = match.groups()
                    try:
                        file_date = datetime(int(year), int(month), int(day))
                        if youngest_date is None or file_date > youngest_date:
                            youngest = filename
                            youngest_date = file_date
                    except ValueError:
                        continue

            if not youngest:
                logger.warning('No files in /data or none having a date in the filename, 404')
                self.send_error(404)
                return

            logger.info('Found youngest %s', youngest)
            logger.debug('Reading')
            # Read and compress file
            file_path = os.path.join(DATA_DIRECTORY, youngest)
            with open(file_path, 'rb') as f:
                file_data = f.read()
            # Send response with caching headers
            self.send_response(200)
            self.send_header('Content-Type', 'application/pdf')
            self.send_header('Content-Length', str(len(file_data)))
            self.send_header('Cache-Control', 'max-age=86400, must-revalidate')
            self.send_header('Content-Disposition', f'attachment; filename={youngest}')
            self.end_headers()
            logger.info('Sending')
            self.wfile.write(file_data)

        except Exception as e:
            logger.error(e)
            self.send_error(500)

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', SERVER_PORT), FileHandler)

    def shutdown_handler(signum: int, frame: FrameType | None):
        logger.warning('Received %s on %s', signal.Signals(signum).name, frame or 'no frame')
        logger.info('Shutting down gracefully')
        server.server_close()

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    logger.info('Starting server')
    server.serve_forever()
