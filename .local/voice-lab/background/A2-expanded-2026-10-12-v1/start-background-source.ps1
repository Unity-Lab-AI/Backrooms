$ErrorActionPreference = 'Stop'
$voiceProject = 'C:\Users\gfour\Desktop\Backrooms'
$voiceJob = Join-Path $voiceProject '.local\voice-lab\background\A2-expanded-2026-10-12-v1'
if (Test-Path -LiteralPath (Join-Path $voiceJob 'launcher.json')) {
    throw 'This launcher was already used. Inspect the existing process and status; do not start a duplicate.'
}
$voicePython = 'C:\Program Files\Python310\python.exe'
$voiceArgv = @(
    '-B', '-u', (Join-Path $voiceProject 'training\voice\run_expanded_preparation.py'),
    '--seed', (Join-Path $voiceProject '.local\voice-lab\dataset\A2-full-1378-draft-v3'),
    '--seed-screen', (Join-Path $voiceProject '.local\voice-lab\dataset\A2-full-1378-screen-v2'),
    '--output', (Join-Path $voiceJob 'pipeline'),
    '--qwen-model', (Join-Path $voiceProject '.local\voice-lab\models\qwen3-tts-base'),
    '--qwen-python', (Join-Path $voiceProject '.local\voice-lab\.venv-qwen\Scripts\python.exe'),
    '--cosy-python', (Join-Path $voiceProject '.local\voice-lab\.venv-cosy\Scripts\python.exe'),
    '--cosy-code', (Join-Path $voiceProject '.local\voice-lab\models\cosyvoice-code'),
    '--cosy-model', (Join-Path $voiceProject '.local\voice-lab\models\cosyvoice3'),
    '--asr-model', 'C:\Users\gfour\.cache\huggingface\hub\models--Systran--faster-whisper-base\snapshots\ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66',
    '--source-digest', '7138ec0643a19b3db60ffa1dc5bd4d2739b93e5ca25a439b7f3490f4dedf7e00',
    '--max-seconds', '172800'
)
if ($voiceArgv | Where-Object { $_.Contains('"') }) { throw 'Unexpected quotation mark in a fixed argument.' }
$voiceQuotedArguments = ($voiceArgv | ForEach-Object { '"' + $_ + '"' }) -join ' '
$voiceProcess = Start-Process -FilePath $voicePython -ArgumentList $voiceQuotedArguments -WorkingDirectory $voiceProject -WindowStyle Hidden -RedirectStandardOutput (Join-Path $voiceJob 'run.stdout.log') -RedirectStandardError (Join-Path $voiceJob 'run.stderr.log') -PassThru
$voiceReceipt = [ordered]@{
    schema = 'unity-local-source-launch-v1'
    recorded_at = [DateTimeOffset]::UtcNow.ToString('o')
    pid = $voiceProcess.Id
    executable = $voicePython
    arguments = $voiceArgv
    source_digest = '7138ec0643a19b3db60ffa1dc5bd4d2739b93e5ca25a439b7f3490f4dedf7e00'
    status_path = (Join-Path $voiceJob 'pipeline\status.json')
    existing_seed_pid_at_launch = 31052
    existing_seed_screen_pid_at_launch = 3800
    max_seconds = 172800
    training_authorized = $false
    rental_authorized = $false
    uploads_authorized = $false
    corpus_accepted = $false
}
$voiceReceipt | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $voiceJob 'launcher.json') -Encoding UTF8
$voiceReceipt | ConvertTo-Json -Depth 6
