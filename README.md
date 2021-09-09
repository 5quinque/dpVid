# dpVid

Convert videos into a web compatible format. 

Provide a path to a file/directory containing videos and they will be converted and stored in the `./output` directory.
Alternatively you can watch a directory and newly created files will be automatically converted

```
dpVid / dipthid

Usage:
    dipthid watch <dir> [--consumers=CONSUMERS]
    dipthid <path>

Options:
    --consumers=CONSUMERS           Number of consumers that will convert videos asynchronously [default: 2]
```