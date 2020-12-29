# ipChecker
Checks to see if external IP has changed and alerts user via email

(Currently set up for Windows (cmd), with my own Gmail address - change GMAIL_USER variable and allow less secure apps on your Google account to use with your own email.)

Run windowless with pythonw:

`pythonw ipchecker.pyw`

Or you can use the `start.bat` file to execute this command. The script is then automatically added to startup folder and will run on user login.

You will be asked to input your password which will then be encoded with base64 before being saved.

Checks IP every 6 hours while running and logs to `ipchecker.log`

Check log file if any issues.
