# Youngest Server

A very simple python web service that scans a configured directory and returns the youngest file of all files present.

I wrote this originally to manage serving my resume over the internet as a convenience, and it quickly dawned on me that I would have multiple versions and managing this while also maintaining a historical record was going to be a lot.

So, a simple service to the rescue.

# Configuration

## Docker Compose

1. Mount a directory that the service will be able to read from.
1. The server listens on the exposed port `80`, map this to your desired port
1. Optionally, set `LOGGING_LEVEL`, defaulting to `INFO`

# Caching

The service will send `Cache-Control: max-age=86400, must-revalidate` to be friendly to frequent downloaders, but in practice folks reading from this URL should only really be getting one file at a time and very rarely.