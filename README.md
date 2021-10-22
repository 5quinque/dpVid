# dpVid

Convert videos into a MPEG-DASH videos. 

Provide a path to a file/directory containing videos and they will be converted and stored in the `./output` directory.
Alternatively you can watch a directory and newly created files will be automatically converted.

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


## Docker

Build the image
```bash
docker build -t dipthid .
```

Ensure that the `output` directory has write permission for the docker container user.

i.e.

```
# Docker container user is `app` with the following uid/gid
uid=101(app) gid=101(app) groups=101(app)
```

My `output` directory looks like this:

```
 ls -ld output
drwxrwxr-x. 1 ryan 101 50 Oct 22 15:30 output
```


### Examples of launching the docker containers

Simple example, watches for new videos in the watch directory and converts them
```
docker run \
    --name dipthid \
    -v $(pwd)/watch:/app/watch \
    -v $(pwd)/output:/app/output \
    --rm dipthid \
    --post-processor=dipthid.postprocessing:PostProcessLog
```

Watches for new videos in the watch directory, converts them and utilises post proccesors to sync to a B2 bucket and update a database
```
docker run \
    --name dipthid \
    -v $(pwd)/watch:/app/watch \
    -v $(pwd)/output:/app/output \
    --rm dipthid \
    --env "B2_BUCKETNAME=REPLACEME" \
    --env "B2_KEY=REPLACEME" \
    --env "B2_SECRET=REPLACEME" \
    --env "OBJECT_BASE_URL=https://REPLACEME/" \
    --post-processor=dipthid.postprocessing.b2_sync:B2Process,dipthid.postprocessing.dbupdate:UpdateDB
```
