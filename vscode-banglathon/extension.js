const vscode = require("vscode");
const { spawn, execFileSync } = require("child_process");
const crypto = require("crypto");
const fs = require("fs");
const os = require("os");
const path = require("path");

let consolePanel = null;
let consoleReady = false;
let pendingMessages = [];
let terminalInstance = null;
let currentProcess = null;
let lastRunFile = null;

function fileExists(p) {
  try {
    return Boolean(p) && fs.existsSync(p);
  } catch {
    return false;
  }
}

function findOnPath(binName) {
  try {
    const checker = process.platform === "win32" ? "where" : "which";
    const out = execFileSync(checker, [binName], {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "ignore"],
    });
    const firstLine = out.split(/\r?\n/).find((l) => l.trim().length > 0);
    return firstLine ? firstLine.trim() : null;
  } catch {
    return null;
  }
}

/**
 * Resolve the BanglaThon CLI or standalone runtime without relying solely on shell PATH.
 */
function resolveRunner() {
  const custom = vscode.workspace
    .getConfiguration("banglathon")
    .get("executablePath", "")
    .trim();
  if (custom && fileExists(custom)) {
    return { cmd: custom, argsPrefix: [] };
  }

  const home = os.homedir();
  const isWin = process.platform === "win32";

  if (isWin) {
    const localAppData = process.env.LOCALAPPDATA || path.join(home, "AppData", "Local");
    const candidates = [
      "C:\\BanglaThon\\bin\\bangla.exe",
      path.join(home, ".bangla", "bin", "bangla.exe"),
      path.join(localAppData, "Microsoft", "WindowsApps", "bangla.exe"),
      "C:\\BanglaThon\\bin\\bangla.cmd",
      path.join(home, ".bangla", "bin", "bangla.cmd"),
    ];
    for (const c of candidates) {
      if (fileExists(c)) {
        return { cmd: c, argsPrefix: [] };
      }
    }

    const runtimes = [
      ["C:\\BanglaThon\\runtime\\python.exe", "C:\\BanglaThon\\runtime\\main.py"],
      [path.join(home, ".bangla", "runtime", "python.exe"), path.join(home, ".bangla", "runtime", "main.py")],
    ];
    for (const [py, script] of runtimes) {
      if (fileExists(py) && fileExists(script)) {
        return { cmd: py, argsPrefix: [script] };
      }
    }
  } else {
    const candidates = [
      path.join(home, ".local", "bin", "bangla"),
      path.join(home, ".bangla", "bin", "bangla"),
      "/opt/homebrew/bin/bangla",
      "/usr/local/bin/bangla",
    ];
    for (const c of candidates) {
      if (fileExists(c)) {
        return { cmd: c, argsPrefix: [] };
      }
    }

    const py = path.join(home, ".bangla", "py", "bin", "python3");
    const mainPy = path.join(home, ".bangla", "runtime", "main.py");
    if (fileExists(py) && fileExists(mainPy)) {
      return { cmd: py, argsPrefix: [mainPy] };
    }
  }

  const fromPath = findOnPath("bangla");
  if (fromPath) {
    return { cmd: fromPath, argsPrefix: [] };
  }

  return null;
}

function usesUserInput(source) {
  const withoutComments = source
    .split(/\r?\n/)
    .map((line) => line.replace(/#.*$/, ""))
    .join("\n");
  return /(?:^|[^A-Za-z0-9_\u0980-\u09FF])(?:nao|নাও)\s*\(/m.test(withoutComments);
}

async function promptMissingRuntime() {
  const isWin = process.platform === "win32";
  const installCmd = isWin
    ? "irm https://raw.githubusercontent.com/tasfiqueofficial/BanglaThon/main/install.ps1 | iex"
    : "curl -fsSL https://raw.githubusercontent.com/tasfiqueofficial/BanglaThon/main/install.sh | sh";

  const choice = await vscode.window.showErrorMessage(
    "BanglaThon ইঞ্জিন পাওয়া যায়নি। এক কমান্ডে ইনস্টল করতে নিচের বাটনে ক্লিক করুন:",
    "Copy Install Command"
  );
  if (choice === "Copy Install Command") {
    await vscode.env.clipboard.writeText(installCmd);
    vscode.window.showInformationMessage(
      isWin
        ? "ইনস্টল কমান্ড কপি হয়েছে! PowerShell-এ পেস্ট করে এন্টার দিন।"
        : "ইনস্টল কমান্ড কপি হয়েছে! Terminal-এ পেস্ট করে এন্টার দিন।"
    );
  }
}

async function prepareActiveFile() {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    vscode.window.showWarningMessage("অনুগ্রহ করে প্রথমে একটি .bl বা .bng ফাইল খুলুন।");
    return null;
  }
  if (editor.document.isUntitled) {
    vscode.window.showWarningMessage("চালানোর আগে ফাইলটি .bl বা .bng নামে সেভ করুন।");
    return null;
  }
  if (editor.document.isDirty) {
    await editor.document.save();
  }
  return editor.document;
}

function killCurrentProcess() {
  if (currentProcess) {
    try {
      currentProcess.kill();
    } catch {
      // ignore if already exited
    }
    currentProcess = null;
  }
}

function getConsoleHtml() {
  const nonce = crypto.randomBytes(16).toString("hex");
  return `<!DOCTYPE html>
<html lang="bn">
<head>
  <meta charset="UTF-8" />
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'nonce-${nonce}';" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <style>
    :root {
      --bg: #071913;
      --surface: #0b241c;
      --border: #164435;
      --green: #10b981;
      --green-dark: #006a4e;
      --red: #f42a41;
      --text: #ecfdf5;
      --muted: #86a89c;
      --warn: #fbbf24;
      --stdin: #38bdf8;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: 'Kohinoor Bangla', 'Noto Sans Bengali', 'Hind Siliguri', 'Bangla Sangam MN', system-ui, -apple-system, sans-serif;
      display: flex;
      flex-direction: column;
      height: 100vh;
      overflow: hidden;
    }
    .header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 10px 14px;
      background: var(--surface);
      border-bottom: 2px solid var(--green-dark);
      gap: 10px;
      flex-wrap: wrap;
    }
    .title-group {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .badge {
      width: 26px;
      height: 26px;
      border-radius: 7px;
      background: var(--green-dark);
      display: inline-flex;
      align-items: center;
      justify-content: center;
      position: relative;
      font-weight: 700;
      font-size: 15px;
      color: #fff;
    }
    .badge::before {
      content: "";
      position: absolute;
      width: 17px;
      height: 17px;
      border-radius: 50%;
      background: var(--red);
    }
    .badge span { position: relative; z-index: 1; }
    .file-pill {
      font-family: 'JetBrains Mono', 'Menlo', monospace;
      font-size: 12.5px;
      color: #a7f3d0;
      background: rgba(16, 185, 129, 0.12);
      padding: 3px 9px;
      border-radius: 6px;
      border: 1px solid rgba(16, 185, 129, 0.25);
    }
    .status {
      font-size: 12px;
      font-weight: 600;
      padding: 3px 10px;
      border-radius: 999px;
      background: rgba(251, 191, 36, 0.15);
      color: var(--warn);
    }
    .status.done { background: rgba(16, 185, 129, 0.16); color: #6ee7b7; }
    .status.err { background: rgba(244, 42, 65, 0.2); color: #fda4af; }
    .actions {
      display: flex;
      gap: 6px;
    }
    button.btn {
      border: 1px solid var(--border);
      background: rgba(255, 255, 255, 0.06);
      color: var(--text);
      padding: 5px 11px;
      border-radius: 7px;
      font-family: inherit;
      font-size: 12.5px;
      font-weight: 600;
      cursor: pointer;
    }
    button.btn:hover { background: rgba(255, 255, 255, 0.13); }
    button.btn.run { background: var(--green-dark); border-color: var(--green); }
    button.btn.stop { background: rgba(244, 42, 65, 0.22); border-color: var(--red); color: #fecdd3; }

    #log {
      flex: 1;
      padding: 16px 18px;
      overflow-y: auto;
      white-space: pre-wrap;
      word-break: break-word;
      font-size: 15px;
      line-height: 1.75;
    }
    .meta { color: var(--muted); font-size: 13px; }
    .stderr { color: #fda4af; }
    .stdin-echo { color: var(--stdin); font-weight: 600; }

    .input-bar {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 10px 14px;
      background: var(--surface);
      border-top: 1px solid var(--border);
    }
    .input-bar.hidden { display: none; }
    .prompt-arrow {
      color: var(--green);
      font-weight: 700;
      font-size: 16px;
    }
    #stdinInput {
      flex: 1;
      background: #04110c;
      color: #ffffff;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 8px 12px;
      font-family: inherit;
      font-size: 14.5px;
      outline: none;
    }
    #stdinInput:focus {
      border-color: var(--green);
      box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.22);
    }
    button.send-btn {
      background: var(--red);
      color: #fff;
      border: none;
      border-radius: 8px;
      padding: 8px 14px;
      font-family: inherit;
      font-weight: 700;
      font-size: 13.5px;
      cursor: pointer;
    }
    button.send-btn:hover { background: #be123c; }
  </style>
</head>
<body>
  <div class="header">
    <div class="title-group">
      <div class="badge"><span>ব</span></div>
      <strong>বাংলাথন কনসোল</strong>
      <span class="file-pill" id="fileLabel">—</span>
      <span class="status" id="statusBadge">প্রস্তুত</span>
    </div>
    <div class="actions">
      <button type="button" class="btn run" id="btnRerun">▶ আবার চালান</button>
      <button type="button" class="btn stop" id="btnStop">■ থামান</button>
      <button type="button" class="btn" id="btnClear">পরিষ্কার</button>
    </div>
  </div>

  <div id="log"></div>

  <form class="input-bar hidden" id="inputForm">
    <span class="prompt-arrow">›</span>
    <input id="stdinInput" type="text" placeholder="এখানে ইনপুট লিখুন (যেমন নাম বা সংখ্যা) এবং Enter চাপুন..." autocomplete="off" />
    <button type="submit" class="send-btn">পাঠান ↵</button>
  </form>

  <script nonce="${nonce}">
    const vscode = acquireVsCodeApi();
    const logEl = document.getElementById('log');
    const fileLabel = document.getElementById('fileLabel');
    const statusBadge = document.getElementById('statusBadge');
    const inputForm = document.getElementById('inputForm');
    const stdinInput = document.getElementById('stdinInput');

    function appendChunk(text, cls) {
      const span = document.createElement('span');
      if (cls) span.className = cls;
      span.appendChild(document.createTextNode(text));
      logEl.appendChild(span);
      logEl.scrollTop = logEl.scrollHeight;
    }

    inputForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const val = stdinInput.value;
      stdinInput.value = '';
      appendChunk(val + '\\n', 'stdin-echo');
      vscode.postMessage({ type: 'stdin', value: val });
    });

    document.getElementById('btnRerun').addEventListener('click', () => {
      vscode.postMessage({ type: 'rerun' });
    });
    document.getElementById('btnStop').addEventListener('click', () => {
      vscode.postMessage({ type: 'stop' });
    });
    document.getElementById('btnClear').addEventListener('click', () => {
      logEl.textContent = '';
    });

    window.addEventListener('message', (event) => {
      const msg = event.data;
      if (msg.type === 'start') {
        logEl.textContent = '';
        fileLabel.textContent = msg.fileName;
        statusBadge.textContent = 'চলছে...';
        statusBadge.className = 'status';
        inputForm.classList.remove('hidden');
        if (msg.focusInput) {
          setTimeout(() => stdinInput.focus(), 60);
        }
        appendChunk('▶ ' + msg.fileName + ' চালু হয়েছে...\\n\\n', 'meta');
      } else if (msg.type === 'stdout') {
        appendChunk(msg.text, '');
      } else if (msg.type === 'stderr') {
        appendChunk(msg.text, 'stderr');
      } else if (msg.type === 'done') {
        inputForm.classList.add('hidden');
        const ok = msg.code === 0;
        statusBadge.textContent = ok
          ? 'সমাপ্ত (' + msg.elapsed + 's)'
          : 'ত্রুটি (কোড ' + msg.code + ')';
        statusBadge.className = 'status ' + (ok ? 'done' : 'err');
        appendChunk('\\n[সমাপ্ত — ' + msg.elapsed + 's]\\n', 'meta');
      }
    });

    vscode.postMessage({ type: 'ready' });
  </script>
</body>
</html>`;
}

function postToConsole(msg) {
  if (!consolePanel) return;
  if (consoleReady) {
    consolePanel.webview.postMessage(msg);
  } else {
    pendingMessages.push(msg);
  }
}

function ensureConsolePanel(preserveFocus) {
  if (!consolePanel) {
    consoleReady = false;
    pendingMessages = [];
    consolePanel = vscode.window.createWebviewPanel(
      "banglathonConsole",
      "বাংলাথন কনসোল",
      { viewColumn: vscode.ViewColumn.Beside, preserveFocus },
      { enableScripts: true, retainContextWhenHidden: true }
    );
    consolePanel.webview.html = getConsoleHtml();

    consolePanel.webview.onDidReceiveMessage((msg) => {
      if (msg.type === "ready") {
        consoleReady = true;
        while (pendingMessages.length > 0) {
          consolePanel.webview.postMessage(pendingMessages.shift());
        }
      } else if (msg.type === "stdin" && currentProcess && currentProcess.stdin && !currentProcess.stdin.destroyed) {
        currentProcess.stdin.write(msg.value + "\n", "utf8");
      } else if (msg.type === "stop") {
        killCurrentProcess();
      } else if (msg.type === "rerun" && lastRunFile) {
        runInBanglaConsole(lastRunFile);
      }
    });

    consolePanel.onDidDispose(() => {
      consolePanel = null;
      consoleReady = false;
      pendingMessages = [];
      killCurrentProcess();
    });
  } else {
    consolePanel.reveal(vscode.ViewColumn.Beside, preserveFocus);
  }
  return consolePanel;
}

function runInBanglaConsole(docOrPath) {
  const runner = resolveRunner();
  if (!runner) {
    promptMissingRuntime();
    return;
  }

  const filePath = typeof docOrPath === "string" ? docOrPath : docOrPath.fileName;
  const sourceText =
    typeof docOrPath === "string" ? fs.readFileSync(filePath, "utf8") : docOrPath.getText();
  lastRunFile = filePath;

  const hasInput = usesUserInput(sourceText);
  ensureConsolePanel(!hasInput);

  killCurrentProcess();

  postToConsole({
    type: "start",
    fileName: path.basename(filePath),
    focusInput: hasInput,
  });

  const start = Date.now();
  const useShell =
    process.platform === "win32" && /\.(cmd|bat)$/i.test(runner.cmd);

  const proc = spawn(runner.cmd, [...runner.argsPrefix, "run", filePath], {
    cwd: path.dirname(filePath),
    shell: useShell,
    env: {
      ...process.env,
      PYTHONUTF8: "1",
      PYTHONIOENCODING: "utf-8",
      PYTHONUNBUFFERED: "1",
      LANG: process.env.LANG || "en_US.UTF-8",
    },
  });
  currentProcess = proc;

  proc.stdout.setEncoding("utf8");
  proc.stderr.setEncoding("utf8");

  proc.stdout.on("data", (chunk) => {
    postToConsole({ type: "stdout", text: chunk });
  });
  proc.stderr.on("data", (chunk) => {
    postToConsole({ type: "stderr", text: chunk });
  });

  proc.on("error", async (err) => {
    if (currentProcess === proc) currentProcess = null;
    postToConsole({ type: "stderr", text: `\n[Error] ${err.message}\n` });
    postToConsole({
      type: "done",
      code: 1,
      elapsed: ((Date.now() - start) / 1000).toFixed(2),
    });
    await promptMissingRuntime();
  });

  proc.on("close", (code) => {
    if (currentProcess === proc) currentProcess = null;
    postToConsole({
      type: "done",
      code: code ?? 0,
      elapsed: ((Date.now() - start) / 1000).toFixed(2),
    });
  });
}

function getOrCreateTerminal(cwd) {
  if (!terminalInstance || terminalInstance.exitStatus !== undefined) {
    terminalInstance = vscode.window.createTerminal({
      name: "BanglaThon",
      cwd,
      env: {
        PYTHONUTF8: "1",
        PYTHONIOENCODING: "utf-8",
        PYTHONUNBUFFERED: "1",
        LANG: "en_US.UTF-8",
      },
    });
  }
  return terminalInstance;
}

function formatShellInvoke(runner) {
  const isWin = process.platform === "win32";
  const shellName = (vscode.env.shell || "").toLowerCase();
  const isPwsh = isWin && (shellName.includes("powershell") || shellName.includes("pwsh"));

  const quoteBin = (p) => {
    if (!/\s/.test(p)) return p;
    return isPwsh ? `& "${p}"` : `"${p}"`;
  };

  if (runner.argsPrefix.length > 0) {
    const quotedArgs = runner.argsPrefix.map((a) => `"${a}"`).join(" ");
    return `${quoteBin(runner.cmd)} ${quotedArgs}`;
  }
  return quoteBin(runner.cmd);
}

function runInTerminalWindow(runner, filePath) {
  const dir = path.dirname(filePath);
  if (terminalInstance) {
    terminalInstance.dispose();
    terminalInstance = null;
  }
  const term = getOrCreateTerminal(dir);
  term.show(false);
  term.sendText(`${formatShellInvoke(runner)} run "${filePath}"`);
}

async function handleRunFile(forceTerminal) {
  const doc = await prepareActiveFile();
  if (!doc) return;

  if (forceTerminal) {
    const runner = resolveRunner();
    if (!runner) {
      await promptMissingRuntime();
      return;
    }
    runInTerminalWindow(runner, doc.fileName);
    return;
  }

  runInBanglaConsole(doc);
}

async function handleOpenRepl() {
  const runner = resolveRunner();
  if (!runner) {
    await promptMissingRuntime();
    return;
  }
  const term = getOrCreateTerminal(vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || os.homedir());
  term.show(false);
  term.sendText(formatShellInvoke(runner));
}

function activate(context) {
  context.subscriptions.push(
    vscode.commands.registerCommand("banglathon.runFile", () => handleRunFile(false)),
    vscode.commands.registerCommand("banglathon.runInTerminal", () => handleRunFile(true)),
    vscode.commands.registerCommand("banglathon.openRepl", () => handleOpenRepl()),
    vscode.window.onDidCloseTerminal((closed) => {
      if (closed === terminalInstance) terminalInstance = null;
    })
  );
}

function deactivate() {
  killCurrentProcess();
}

module.exports = { activate, deactivate };
