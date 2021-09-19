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

## Installation

### Create and activate virtual environment

```bash
python3.9 -m venv ~/.venv/dpVid
source ~/.venv/dpVid/bin/activate
```

### Install as pip package

```bash
pip install -e .
```

### Install packages

```bash
pip install -r requirements.txt
```