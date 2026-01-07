from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FfmpegRunner:
    """Run ffmpeg commands safely and consistently."""

    ffmpeg_bin: str = "ffmpeg"

    def run(self, args: list[str]) -> None:
        """Execute ffmpeg with the provided arguments."""
        cmd = [self.ffmpeg_bin, "-y", *args]
        subprocess.run(cmd, check=True, capture_output=True)


@dataclass(frozen=True)
class AudioEncoder:
    """Encode audio segments into MP3."""

    runner: FfmpegRunner

    def cut_to_mp3(self, src: Path, start_s: float, end_s: float, dst: Path,
                   bitrate_kbps: int) -> None:
        """Cut and encode [start_s, end_s] from src into dst."""
        duration_s = max(0.0, end_s - start_s)
        args = [
            "-ss", f"{start_s:.3f}",
            "-t", f"{duration_s:.3f}",
            "-i", str(src),
            "-vn",
            "-acodec", "libmp3lame",
            "-b:a", f"{bitrate_kbps}k",
            str(dst),
        ]
        self.runner.run(args)
