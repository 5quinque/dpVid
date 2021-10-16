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
    --post-processor=CLASS          The python class that handles post processing, use multiple seperated by commas [default: dipthid.postprocessing:PostProcessLog]
```

## Installation

### Create and activate virtual environment

```bash
python3.9 -m venv env
source env/bin/activate
```

### Docker

Build the image
```bash
docker build -t dipthid .
```

Example
```
docker run \
    --name dipthid \
    -v test_videos:/app/watch \
    -v output:/app/output \
    --rm dipthid \
    --post-processor=dipthid.postprocessing:PostProcessLog
```

B2 Post Processor
```
docker run \
    --name dipthid \
    -v test_videos:/app/watch \
    -v output:/app/output \
    --rm dipthid \
    --env "B2_BUCKETNAME=REPLACEME" \
    --env "B2_KEY=REPLACEME" \
    --env "B2_SECRET=REPLACEME" \
    --post-processor=dipthid.postprocessing.b2_upload:B2Upload
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
dipthid ./test_videos/sample-avi-file.avi --post-processor=dipthid.postprocessing.b2_sync:B2Process
```
