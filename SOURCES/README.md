# What it is
This is an adjustment to UW-IMAP to use poll() over select(), which has a file descriptor limitation of 1024 FDs. On large multi-sites, for example running under an Apache instance with > 1024 logfiles, this necessary to prevent complications in PHP's imap extension.

This is vanilla to UW-IMAP-2007f with the exception of *imap-2007e-epoll.patch* that contains polling implementation.

## Further information
* [php5-imap file open error >1024](https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=478193)
