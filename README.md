# dpVid

Convert videos into a web compatible format. 

Provide a path to a file/directory containing videos and they will be converted and stored in the `./output` directory.
Alternatively you can watch a directory and newly created files will be automatically converted

```
dpVid / dipthid

Usage:
    dipthid watch <dir> [--consumers=CONSUMERS] [options]
    dipthid <path> [options]

Options:
    --consumers=CONSUMERS           Number of consumers that will convert videos asynchronously [default: 2]
    --log-level=LEVEL               Set logger level, one of DEBUG, INFO, WARNING, ERROR, CRITICAL [default: INFO]
    --container=FORMAT              Output container format, either webm or mp4 [default: mp4]
    --post-processer=CLASS          The python class that handles post processing [default: dipthid.postprocessing:PostProcess]
```

## Installation

### Create and activate virtual environment

```bash
python3.9 -m venv env
source env/bin/activate
```

### Install as pip package

```bash
pip install -e .
```

Any errors due to missing libraries can probably be fixed with:

```bash
sudo dnf install -y mariadb-devel python-devel
```

or the equivalent for your distro.

## Example usage

Upload to Backblaze B2 bucket on completion

```bash
export B2_BUCKETNAME="REPLACEME"
export B2_KEY="REPLACEME"
export B2_SECRET="REPLACEME"
dipthid ./test_videos/sample-avi-file.avi --post-processer=dipthid.postprocessing.b2_upload:B2Upload
```
