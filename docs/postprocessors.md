# Post Processors

You can pass a post processing class as an argument for example:

`dipthid ./test_videos/sample-mp4-file.mp4 --post-processer=dipthid.postprocessing:PostProcessLog`

The class is a string containing the importable module and the name of the class inside that module, seperated by a colon.

The easiest way to create a post processor is to implement the `PostProcess` class:

```python
class PostProcess(metaclass=ABCMeta):
    def __init__(self, filename, mime_type=None, old_filename=None):
        self.filename = filename
        self.mime_type = mime_type
        self.old_filename = old_filename

    @abstractmethod
    def processed(self):
        pass
```

For example, this `PostProcessLog` class looks like this:

```python
class PostProcessLog(PostProcess):
    def processed(self):
        logger.info(
            f"Processing complete, <{self.filename=}> with the <{self.mime_type=}>"
        )
```