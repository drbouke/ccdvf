# Environment Setup

The course runs in Visual Studio Code (VS Code), either in the browser through GitHub Codespaces or installed on a laptop. A codespace requires no installation and follows Step 6. A laptop follows Steps 1 to 5.

## Step 1. Python and VS Code

1. Install Python 3.11 or later from https://www.python.org/downloads/. On Windows, select **Add python.exe to PATH**.
2. Install VS Code from https://code.visualstudio.com/.

## Step 2. Course Folder

1. Download **CCDV-F Course Programs** from the course Materials page and unzip it.
2. In VS Code, choose **File > Open Folder** and open the `ccdvf` folder itself.
3. Install the recommended extensions when VS Code offers them. These are Python, Python Debugger, and Claude Code.

## Step 3. Virtual Environment

Open a terminal with **Terminal > New Terminal** and run the commands for your system.

On Windows, in PowerShell:

```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

On macOS or Linux:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If PowerShell blocks `Activate.ps1`, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once and activate again.

The status bar at the bottom of the window must show the `.venv` interpreter. To change it, press **F1**, run **Python: Select Interpreter**, and choose `.venv`.

## Step 4. API Key

The course key appears on the **Class Key** slide and remains valid until the course ends.

1. Create the `.env` file from its template. Use `Copy-Item .env.example .env` in PowerShell or `cp .env.example .env` on macOS and Linux.
2. Open `.env` and replace the empty `ANTHROPIC_API_KEY=` line with the full line from the slide.
3. Save the file.

Verify the environment. The check sends one small request and ends with `Ready.`

```
python check_setup.py --ping
```

To follow the key from the file to the request, run the key program.

```
python part1/00_environment/inject_key.py
```

Run any program from the `ccdvf` folder.

```
python run.py part1/04_tools/agent.py
```

A program can also run with **F5**, through the **Run this program** configuration in `.vscode/launch.json`.

Everyone holding the course key can see files uploaded through the API with it, so real data does not belong there. A personal API key stays private and never appears in code, on a slide, or in Git. Personal keys are created at https://platform.claude.com under **Keys & access**, preferably in a workspace with a monthly spend limit. API usage is billed in the Claude Console and is separate from a Claude subscription.

## Step 5. Claude Code

The Claude Code extension takes the course key from `.env` through the `.claude/settings.json` file, so it requires no sign-in. The same file sets Claude Haiku 5.5 as the default model, the lowest-cost option, and the model menu in the panel can change it.

1. After saving `.env`, press **F1** and run **Developer: Reload Window**.
2. Open Claude Code from its icon.
3. If a sign-in screen appears, select **Disable Login Prompt** in the Claude Code extension settings and reload the window again. Use none of the sign-in options.

In a codespace, the `claude` command is already available in the terminal. Start it from the `ccdvf` folder, because Claude Code reads its project settings from the folder where it starts. On a laptop, this command requires the separate installation described at https://code.claude.com/docs/en/setup.

The Agent SDK program `core_concepts/agent_sdk.py` needs neither the extension nor the command. The SDK package includes its own copy of Claude Code and uses `ANTHROPIC_API_KEY`.

## Step 6. GitHub Codespaces

A codespace is VS Code in the browser, connected to a machine that GitHub runs. Python, the packages, and the extensions are already installed.

1. Create a free account at https://github.com/signup if you have none, send your GitHub username to the instructor, and accept the repository invitation from your GitHub email.
2. Open https://github.com/codespaces/new and choose `drbouke/ccdvf`.
3. Confirm that the page names your own account as the payer, keep the 2-core machine, and click **Create codespace**.
4. Wait about two minutes until the terminal finishes the installation.
5. Click **+** in the terminal panel and complete Step 4, using the `cp` command.
6. Complete Step 5.

Usage counts against the free allowance of your own GitHub account, about 60 hours a month on a 2-core machine. Stop the codespace at the end of each day from https://github.com/codespaces. An idle codespace stops after 30 minutes, and GitHub deletes one left unused for 30 days.

## Troubleshooting

| Message | Cause | Action |
|---|---|---|
| `No ANTHROPIC_API_KEY` | The `.env` file is missing or unsaved | Complete Step 4 |
| A different key in the setup check | A variable set on the machine takes priority over `.env` | Delete the variable from your system or shell profile, then restart VS Code |
| `401 authentication_error` | The key is mistyped, revoked, or expired | Copy the full line from the slide again |
| `Error loading webview` | Security software is injecting scripts into web pages, as Kaspersky does through its **Inject script into web traffic** setting | Turn off the injection setting, then close and reopen the browser |
| `Not logged in` in the terminal | `claude` started from a subfolder | Start it from the `ccdvf` folder |
