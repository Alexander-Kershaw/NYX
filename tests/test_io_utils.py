from pathlib import Path

from simulator.io_utils import output_directory, generate_output_filepath


def test_ensure_output_directory_creates_directory(tmp_path: Path) -> None:
    output_dir = tmp_path / "telemetry_output"

    result = output_directory(output_dir)

    assert result.exists()
    assert result.is_dir()


def test_generate_output_filepath_returns_jsonl_path(tmp_path: Path) -> None:
    output_path = generate_output_filepath(tmp_path, prefix="nyx_test")

    assert output_path.parent == tmp_path
    assert output_path.name.startswith("nyx_test_")
    assert output_path.suffix == ".jsonl"