# simple-file-transfer-system

Implementation of a simple file transfer system for group project

## Troubleshooting

If the server doesn't respond to keyboard interrupts and you want to terminate the process, run:

```Batch
netstat -ano|findstr 5000
```

To terminate the process, copy the PID and run:

```Batch
taskkill /F /PID <PID>
```

## Credits

[Example Secure File Transfer system implementation](https://github.com/FarisHijazi/Secure-FileTransfer/tree/master)

The socket programming portion was created following this [tutorial](https://realpython.com/python-sockets/)
