import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class WaveformEnvelope:
    """Hold a downsampled waveform envelope."""

    times_s: np.ndarray
    values: np.ndarray


class WaveformError(RuntimeError):
    """Raised when waveform extraction fails."""


class WaveformService:
    """Build a waveform envelope using ffmpeg."""

    def __init__(self, executable: str = "ffmpeg") -> None:
        """Initialize with an ffmpeg executable name/path."""
        self._executable = executable

    def build_envelope(
        self,
        file_path: Path,
        duration_s: float,
        points: int = 2000,
        sample_rate: int = 8000,
    ) -> WaveformEnvelope:
        """Extract mono PCM and compute a peak envelope."""
        pcm = self._extract_pcm(file_path, sample_rate)
        values = self._peak_envelope(pcm, points)
        times = self._build_times(duration_s, len(values))
        return WaveformEnvelope(times_s=times, values=values)

    def _extract_pcm(self, file_path: Path, sample_rate: int) -> np.ndarray:
        """Return mono float32 PCM samples in [-1, 1]."""
        args = [
            "-v",
            "error",
            "-i",
            str(file_path),
            "-ac",
            "1",
            "-ar",
            str(sample_rate),
            "-f",
            "f32le",
            "pipe:1",
        ]
        output = self._run(args)
        return np.frombuffer(output, dtype=np.float32)

    def _run(self, args: list[str]) -> bytes:
        """Run ffmpeg and return stdout bytes."""
        cmd = [self._executable, *args]
        try:
            completed = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
            )
            return completed.stdout
        except FileNotFoundError as exc:
            raise WaveformError("ffmpeg not found in PATH") from exc
        except subprocess.CalledProcessError as exc:
            stderr = (exc.stderr or b"").decode(errors="ignore").strip()
            raise WaveformError(f"ffmpeg failed: {stderr}") from exc

    def _peak_envelope(self, samples: np.ndarray, points: int) -> np.ndarray:
        """Compute peak envelope (max abs) over fixed windows."""
        if samples.size == 0:
            return np.zeros(points, dtype=np.float32)

        win = max(1, samples.size // points)
        trimmed = samples[: win * (samples.size // win)]
        frames = trimmed.reshape(-1, win)
        peaks = np.max(np.abs(frames), axis=1)

        if peaks.size < points:
            return np.pad(peaks, (0, points - peaks.size))

        return peaks[:points]

    def _build_times(self, duration_s: float, points: int) -> np.ndarray:
        """Build time axis in seconds."""
        if points <= 1:
            return np.array([0.0], dtype=np.float32)
        return np.linspace(0.0, duration_s, num=points, dtype=np.float32)
