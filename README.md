# ipChecker
Checks to see if external IP has changed and automatically edits forwarding rule at domains.google.com (also notifies user by email that IP has changed).

(Currently set up for Windows, with my own Gmail address - change GMAIL_USER variable and allow less secure apps on your Google account to use with your own email.)

Run windowless with pythonw:

`pythonw ipchecker.pyw`

Or you can use the `start.bat` file to execute this command. A script is then automatically added to startup folder and the program will run on user login.

On first run, you will be asked to input your password which will then be encoded with base64 before being saved.

Checks IP every 6 hours while running and logs to `ipchecker.log`

Check log file if any issues, or for more info.
