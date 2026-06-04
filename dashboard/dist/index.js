(function () {
  "use strict";
  const SDK = window.__HERMES_PLUGIN_SDK__;
  const { React } = SDK;
  const { useEffect, useState } = SDK.hooks;
  const { Badge, Button, Card, CardContent, CardHeader, CardTitle } = SDK.components;
  const h = React.createElement;
  function Field(props) { return h("label", { className: "mimo-field" }, h("span", { className: "mimo-label" }, props.label), props.children, props.hint ? h("span", { className: "mimo-hint" }, props.hint) : null); }
  function MetaItem(props) { return h("div", { className: "mimo-meta-item" }, h("span", { className: "mimo-meta-label" }, props.label), h("strong", { className: "mimo-meta-value" }, props.value)); }
  function StatusPanel({ status, loading, onRefresh }) {
    const configured = status && status.configured;
    return h(Card, { className: "mimo-status-card" },
      h(CardHeader, { className: "mimo-card-header" }, h("div", null, h(CardTitle, null, "运行状态"), h("p", { className: "mimo-subtle" }, "当前 Hermes 进程中的 MiMo TTS 配置")), h(Badge, { variant: configured ? "default" : "destructive" }, configured ? "已连接" : "未配置")),
      h(CardContent, null,
        h("div", { className: "mimo-meta-grid" }, h(MetaItem, { label: "API Key", value: configured ? status.key_preview : "未设置" }), h(MetaItem, { label: "默认模型", value: status ? status.model : "—" }), h(MetaItem, { label: "默认声音", value: status ? status.voice : "—" }), h(MetaItem, { label: "输出格式", value: "WAV" })),
        h("div", { className: "mimo-endpoint" }, h("span", { className: "mimo-meta-label" }, "API 端点"), h("code", null, status ? status.base_url : "—")),
        h("div", { className: "mimo-actions mimo-status-actions" }, h(Button, { variant: "outline", onClick: onRefresh, disabled: loading }, loading ? "刷新中…" : "刷新状态"), h("a", { className: "mimo-link", href: "/env" }, "前往 Keys 设置"))));
  }
  function Studio({ status, onRefresh }) {
    const [text, setText] = useState("你好，我是由小米 MiMo 提供语音能力的 Hermes Agent。");
    const [model, setModel] = useState("mimo-v2.5-tts");
    const [voice, setVoice] = useState("冰糖");
    const [style, setStyle] = useState("");
    const [speed, setSpeed] = useState("1");
    const [busy, setBusy] = useState(false);
    const [error, setError] = useState("");
    const [notice, setNotice] = useState("");
    const [audioUrl, setAudioUrl] = useState("");
    useEffect(function () { if (!status) return; setModel(status.model || "mimo-v2.5-tts"); setVoice(status.voice || "冰糖"); setStyle(status.style_prompt || ""); }, [status]);
    useEffect(function () { return function () { if (audioUrl) URL.revokeObjectURL(audioUrl); }; }, [audioUrl]);
    async function synthesize() {
      setError(""); setNotice(""); setBusy(true);
      try {
        const response = await SDK.authedFetch("/api/plugins/mimo-tts/synthesize", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text, model, voice, style, speed: Number(speed) }) });
        if (!response.ok) { let message = "语音合成失败"; try { const payload = await response.json(); message = payload.detail || message; } catch (_) {} throw new Error(message); }
        const blob = await response.blob(); if (audioUrl) URL.revokeObjectURL(audioUrl); setAudioUrl(URL.createObjectURL(blob));
      } catch (err) { setError(err.message || "语音合成失败"); } finally { setBusy(false); }
    }
    async function saveDefaultVoice() {
      setError(""); setNotice(""); setBusy(true);
      try { await SDK.api.setEnvVar("XIAOMI_TTS_VOICE", voice); await onRefresh(); setNotice("默认音色已保存为 " + voice + "，后续 Hermes TTS 会使用该音色。"); }
      catch (err) { setError(err.message || "保存默认音色失败"); } finally { setBusy(false); }
    }
    const models = status ? status.models : ["mimo-v2.5-tts", "mimo-v2-tts"];
    const voices = status ? status.voices : ["冰糖", "Mia"];
    const disabled = busy || !status || !status.configured || !text.trim();
    return h(Card, { className: "mimo-studio-card" }, h(CardHeader, null, h(CardTitle, null, "语音工作台"), h("p", { className: "mimo-subtle" }, "输入文本并试听当前 MiMo 配置")),
      h(CardContent, { className: "mimo-studio-content" },
        h(Field, { label: "朗读文本", hint: text.length + " / 5000" }, h("textarea", { className: "mimo-textarea", value: text, maxLength: 5000, onChange: function (event) { setText(event.target.value); }, placeholder: "输入需要合成的中文或英文文本" })),
        h("div", { className: "mimo-form-grid" },
          h(Field, { label: "模型" }, h("select", { className: "mimo-select", value: model, onChange: function (event) { setModel(event.target.value); } }, models.map(function (item) { return h("option", { value: item, key: item }, item); }))),
          h(Field, { label: "声音" }, h("select", { className: "mimo-select", value: voice, onChange: function (event) { setVoice(event.target.value); } }, voices.map(function (item) { return h("option", { value: item, key: item }, item); }))),
          h(Field, { label: "语速", hint: Number(speed).toFixed(1) + "×" }, h("input", { className: "mimo-range", type: "range", min: "0.5", max: "2", step: "0.1", value: speed, onChange: function (event) { setSpeed(event.target.value); } })),
          h(Field, { label: "说话风格", hint: "可选" }, h("input", { className: "mimo-input", value: style, maxLength: 1000, onChange: function (event) { setStyle(event.target.value); }, placeholder: "例如：温暖、清晰、自然" }))),
        error ? h("div", { className: "mimo-error", role: "alert" }, error) : null, notice ? h("div", { className: "mimo-notice", role: "status" }, notice) : null,
        h("div", { className: "mimo-output" }, audioUrl ? h(React.Fragment, null, h("audio", { className: "mimo-audio", src: audioUrl, controls: true, autoPlay: true }), h("a", { className: "mimo-download", href: audioUrl, download: "mimo-preview.wav" }, "下载 WAV")) : h("p", { className: "mimo-empty" }, status && status.configured ? "生成后的音频会显示在这里" : "设置 XIAOMI_API_KEY 后即可试听")),
        h("div", { className: "mimo-actions" }, h(Button, { variant: "outline", onClick: saveDefaultVoice, disabled: busy || !status || voice === status.voice }, voice === (status && status.voice) ? "当前默认音色" : "设为默认音色"), h(Button, { onClick: synthesize, disabled: disabled }, busy ? "正在合成…" : "生成并试听"))));
  }
  function MiMoDashboard() {
    const [status, setStatus] = useState(null); const [loading, setLoading] = useState(true); const [error, setError] = useState("");
    async function loadStatus() { setLoading(true); setError(""); try { setStatus(await SDK.fetchJSON("/api/plugins/mimo-tts/status")); } catch (err) { setError(err.message || "无法读取插件状态"); } finally { setLoading(false); } }
    useEffect(function () { loadStatus(); }, []);
    return h("div", { className: "mimo-page" }, h("header", { className: "mimo-page-header" }, h("div", null, h("div", { className: "mimo-eyebrow" }, "XIAOMI MIMO · SPEECH SYNTHESIS"), h("h1", null, "MiMo TTS 控制台"), h("p", null, "检查连接状态，调整声音参数，并在 Hermes Dashboard 中直接试听。")), h("div", { className: "mimo-signal", "aria-label": "MiMo TTS status" }, h("span", { className: status && status.configured ? "is-online" : "" }), status && status.configured ? "Ready" : "Setup required")), error ? h("div", { className: "mimo-error", role: "alert" }, error) : null, h("div", { className: "mimo-layout" }, h(StatusPanel, { status, loading, onRefresh: loadStatus }), h(Studio, { status, onRefresh: loadStatus })));
  }
  window.__HERMES_PLUGINS__.register("mimo-tts", MiMoDashboard);
})();
