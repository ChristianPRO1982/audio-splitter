class ApiClient {
  constructor() {
    this.baseUrl = "";
  }

  async createProject(file) {
    const form = new FormData();
    form.append("file", file);

    const res = await fetch(`${this.baseUrl}/api/projects`, {
      method: "POST",
      body: form,
    });

    if (!res.ok) {
      throw new Error(await res.text());
    }
    return res.json();
  }

  getAudioUrl(projectId) {
    return `${this.baseUrl}/api/projects/${projectId}/audio`;
  }

  async export(projectId, payload) {
    const res = await fetch(`${this.baseUrl}/api/projects/${projectId}/export`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      throw new Error(await res.text());
    }
    return res.json();
  }
}

class TimeUtils {
  static toClock(seconds) {
    const s = Math.max(0, Math.floor(seconds));
    const mm = String(Math.floor(s / 60)).padStart(2, "0");
    const ss = String(s % 60).padStart(2, "0");
    return `${mm}:${ss}`;
  }
}

class CutterApp {
  constructor() {
    this.api = new ApiClient();
    this.projectId = null;
    this.markers = [];
    this.wave = null;

    this.fileInput = document.getElementById("fileInput");
    this.uploadBtn = document.getElementById("uploadBtn");
    this.projectInfo = document.getElementById("projectInfo");

    this.playBtn = document.getElementById("playBtn");
    this.addMarkerBtn = document.getElementById("addMarkerBtn");
    this.timeInfo = document.getElementById("timeInfo");

    this.segmentsDiv = document.getElementById("segments");
    this.exportBtn = document.getElementById("exportBtn");
    this.exportLog = document.getElementById("exportLog");
    this.bitrate = document.getElementById("bitrate");

    this._bind();
    this._setUiDisabled(true);
  }

  _bind() {
    this.uploadBtn.addEventListener("click", () => this._onUpload());
    this.playBtn.addEventListener("click", () => this._togglePlay());
    this.addMarkerBtn.addEventListener("click", () => this._addMarker());
    this.exportBtn.addEventListener("click", () => this._export());
  }

  _setUiDisabled(disabled) {
    this.playBtn.disabled = disabled;
    this.addMarkerBtn.disabled = disabled;
    this.exportBtn.disabled = disabled;
  }

  async _onUpload() {
    const file = this.fileInput.files?.[0];
    if (!file) return;

    this._log("Uploading...");
    const data = await this.api.createProject(file);

    this.projectId = data.project_id;
    this.projectInfo.textContent = `Project: ${this.projectId}`;
    await this._loadAudio();
  }

  async _loadAudio() {
    this._setUiDisabled(true);
    this.markers = [];
    this._renderSegments();

    if (this.wave) {
      this.wave.destroy();
    }

    const url = this.api.getAudioUrl(this.projectId);
    this.wave = WaveSurfer.create({
      container: "#waveform",
      height: 120,
      mediaControls: true,
      url: url,
    });

    this.wave.on("timeupdate", (t) => {
      this.timeInfo.textContent = TimeUtils.toClock(t);
    });

    this.wave.on("ready", () => {
      this._setUiDisabled(false);
      this._log("Audio loaded. Add markers, then export.");
    });
  }

  _togglePlay() {
    if (!this.wave) return;
    this.wave.playPause();
  }

  _addMarker() {
    if (!this.wave) return;

    const t = this.wave.getCurrentTime();
    this.markers.push(t);
    this.markers.sort((a, b) => a - b);
    this._renderSegments();
  }

  _segmentsFromMarkers() {
    if (!this.wave) return [];
    const duration = this.wave.getDuration();
    const points = [0, ...this.markers, duration].filter((x) => Number.isFinite(x));
    const segments = [];

    for (let i = 0; i < points.length - 1; i += 1) {
      const start = points[i];
      const end = points[i + 1];
      if (end - start < 0.2) continue;

      segments.push({
        start_s: start,
        end_s: end,
        filename: `segment_${String(i + 1).padStart(2, "0")}.mp3`,
      });
    }
    return segments;
  }

  _renderSegments() {
    const segments = this._segmentsFromMarkers();
    this.segmentsDiv.innerHTML = "";

    segments.forEach((seg, idx) => {
      const div = document.createElement("div");
      div.className = "segment";

      const label = document.createElement("div");
      label.textContent = `${TimeUtils.toClock(seg.start_s)} → ${TimeUtils.toClock(seg.end_s)}`;

      const input = document.createElement("input");
      input.type = "text";
      input.value = seg.filename;
      input.addEventListener("input", (e) => {
        segments[idx].filename = e.target.value;
      });

      const jumpBtn = document.createElement("button");
      jumpBtn.textContent = "Jump";
      jumpBtn.addEventListener("click", () => {
        if (!this.wave) return;
        this.wave.setTime(seg.start_s);
      });

      div.appendChild(label);
      div.appendChild(input);
      div.appendChild(jumpBtn);
      this.segmentsDiv.appendChild(div);
    });

    this._currentSegments = segments;
  }

  async _export() {
    if (!this.projectId) return;
    const segments = this._currentSegments || [];
    if (segments.length === 0) {
      this._log("No segments to export (add markers).");
      return;
    }

    const payload = {
      segments: segments.map((s) => ({
        start_s: s.start_s,
        end_s: s.end_s,
        filename: s.filename,
      })),
      bitrate_kbps: Number(this.bitrate.value),
    };

    this._log("Exporting...");
    const res = await this.api.export(this.projectId, payload);
    this._log(JSON.stringify(res, null, 2));
  }

  _log(text) {
    this.exportLog.textContent = text;
  }
}

window.addEventListener("DOMContentLoaded", () => {
  new CutterApp();
});
