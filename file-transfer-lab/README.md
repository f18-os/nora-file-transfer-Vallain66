## FTP with threads

UPDATED: 10/14/18

## fileThreadServer.py
## fileThreadClient.py


* TO RUN: 
`./fileServer.py`
then
`./fileClient.py <file name>`

## PRINCIPLE OF OPERATION:
fileServer.py:
	
* sets up a thread and a socket to listen to each new request accepted
* a mutex is acquired to prevent filename overlap
* receives the name of the file
* process file name through `getfilename()`
  * `getfilename()` will check if file already exists on the server, if it does a integer is iterated and appended  to make a unique name
* file is copied to server
* mutex is released 

fileClient.py:

* sets up a thread and a socket to handle each file transfer request
* a connection is created to the server
* a mutex is acquired to prevent file transfer overlap
* `put()` handles the file transfer
  * filename is sent to be used as the default name when transfered
* mutex is released 
