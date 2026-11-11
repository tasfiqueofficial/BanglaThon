const vscode = require("vscode");
const { spawn, execFileSync } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

let outputChannel;
let terminalInstance;
let currentProcess = null;

function getOutputChannel() {
  if (!outputChannel) {
    outputChannel = vscode.window.createOutputChannel("BanglaThon");
  }
  return outputChannel;
}

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
    return { cmd: custom, argsPrefix: [], shellCmd: `"${custom}"` };
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
        return { cmd: c, argsPrefix: [], shellCmd: c.includes(" ") ? `& "${c}"` : c };
      }
    }

    const runtimes = [
      ["C:\\BanglaThon\\runtime\\python.exe", "C:\\BanglaThon\\runtime\\main.py"],
      [path.join(home, ".bangla", "runtime", "python.exe"), path.join(home, ".bangla", "runtime", "main.py")],
    ];
    for (const [py, script] of runtimes) {
      if (fileExists(py) && fileExists(script)) {
        return {
          cmd: py,
          argsPrefix: [script],
          shellCmd: `& "${py}" "${script}"`,
        };
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
        return { cmd: c, argsPrefix: [], shellCmd: `"${c}"` };
      }
    }

    const py = path.join(home, ".bangla", "py", "bin", "python3");
    const mainPy = path.join(home, ".bangla", "runtime", "main.py");
    if (fileExists(py) && fileExists(mainPy)) {
      return {
        cmd: py,
        argsPrefix: [mainPy],
        shellCmd: `"${py}" "${mainPy}"`,
      };
    }
  }

  const fromPath = findOnPath("bangla");
  if (fromPath) {
    return { cmd: fromPath, argsPrefix: [], shellCmd: "bangla" };
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

function getOrCreateTerminal(cwd) {
  if (!terminalInstance || terminalInstance.exitStatus !== undefined) {
    terminalInstance = vscode.window.createTerminal({
      name: "BanglaThon",
      cwd,
      env: {
        PYTHONUTF8: "1",
        PYTHONIOENCODING: "utf-8",
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
  const term = getOrCreateTerminal(dir);
  term.show(true);
  term.sendText(`${formatShellInvoke(runner)} run "${filePath}"`);
}

function runInOutputChannel(runner, filePath) {
  const channel = getOutputChannel();
  channel.clear();
  channel.show(true);

  if (currentProcess) {
    try {
      currentProcess.kill();
    } catch {
      // ignore if already exited
    }
    currentProcess = null;
  }

  const fileName = path.basename(filePath);
  channel.appendLine(`[Running] bangla run "${fileName}"`);
  channel.appendLine("--------------------------------------------------");

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
      LANG: process.env.LANG || "en_US.UTF-8",
    },
  });
  currentProcess = proc;

  proc.stdout.setEncoding("utf8");
  proc.stderr.setEncoding("utf8");

  proc.stdout.on("data", (chunk) => channel.append(chunk));
  proc.stderr.on("data", (chunk) => channel.append(chunk));

  proc.on("error", async (err) => {
    if (currentProcess === proc) currentProcess = null;
    channel.appendLine(`\n[Error] ${err.message}`);
    await promptMissingRuntime();
  });

  proc.on("close", (code) => {
    if (currentProcess === proc) currentProcess = null;
    const elapsed = ((Date.now() - start) / 1000).toFixed(2);
    channel.appendLine("--------------------------------------------------");
    channel.appendLine(`[Done] এক্সিট কোড ${code ?? 0} (${elapsed}s)`);
  });
}

async function handleRunFile(forceTerminal) {
  const doc = await prepareActiveFile();
  if (!doc) return;

  const runner = resolveRunner();
  if (!runner) {
    await promptMissingRuntime();
    return;
  }

  if (forceTerminal || usesUserInput(doc.getText())) {
    runInTerminalWindow(runner, doc.fileName);
  } else {
    runInOutputChannel(runner, doc.fileName);
  }
}

async function handleOpenRepl() {
  const runner = resolveRunner();
  if (!runner) {
    await promptMissingRuntime();
    return;
  }
  const term = getOrCreateTerminal(vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || os.homedir());
  term.show(true);
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
  if (currentProcess) {
    try {
      currentProcess.kill();
    } catch {
      // ignore cleanup error
    }
  }
}

module.exports = { activate, deactivate };
