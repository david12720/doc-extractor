from pathlib import Path

from pdf_pipeline.abstractions.file_preparator import (
    FileConverter,
    PreparationPipeline,
    PreparationStep,
    PreparedFile,
)


class FakeConverter(FileConverter):
    def convert(self, input_files: list[Path]) -> list[PreparedFile]:
        return [
            PreparedFile(source_path=p, data=b"fake", mime_type="image/png", page_index=0)
            for p in input_files
        ]


class FakeStep(PreparationStep):
    def __init__(self):
        self.called = False

    def process(self, files: list[PreparedFile]) -> list[PreparedFile]:
        self.called = True
        for f in files:
            f.metadata["step_applied"] = True
        return files


def test_pipeline_runs_converter_and_steps():
    converter = FakeConverter()
    step = FakeStep()
    pipeline = PreparationPipeline(converter=converter, steps=[step])

    results = pipeline.prepare([Path("test.pdf")])

    assert len(results) == 1
    assert step.called
    assert results[0].metadata.get("step_applied") is True


def test_pipeline_without_steps():
    converter = FakeConverter()
    pipeline = PreparationPipeline(converter=converter)

    results = pipeline.prepare([Path("a.pdf"), Path("b.png")])
    assert len(results) == 2
