# http-byte-range-tester

A small script for analyzing the response of a web server to HTTP Range requests. I was writing a handler for Range headers for another project and used this to analyze the behavior of my own implementation as well as other popular web servers. The results require some interpretation and spec knowledge (pass/fail is not really descriptive enough) but I found them useful for validation.
