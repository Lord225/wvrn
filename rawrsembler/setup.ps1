# Check if $PROFILE exists, if not create it
if (!(Test-Path -Path $PROFILE)) {
    New-Item -Type File -Path $PROFILE -Force
}

# Current folder
$root = Split-Path -Parent $MyInvocation.MyCommand.Definition

# Check if # lords-asm-for-mc-begin comment exists in $PROFILE, if so remove everything between # lords-asm-for-mc-begin and # lords-asm-for-mc-end
if (Select-String -Path $PROFILE -Pattern "# rawrsembler-begin") {
    Write-Host "Removing previous installation of 'lords-asm-for-mc' from $PROFILE"
    $content = Get-Content $PROFILE -Raw
    $content = $content -replace "(?ms)(\# rawrsembler-begin)(.*?)(\# rawrsembler-end)\s*", ""
    Set-Content $PROFILE $content
}

# Create a virtual environment
$venv_dir = Join-Path $root "venv"
if (-Not (Test-Path -Path $venv_dir)) {
    Write-Host "Creating virtual environment in $venv_dir"
    python -m venv $venv_dir
}

# Define the path to the Python executable within the virtual environment
$venv_python = Join-Path $venv_dir "Scripts\python.exe"

# Install requirements using the virtual environment's Python
& $venv_python -m pip install -r "$root\requirements.txt"

# Add # lords-asm-for-mc-begin comment to $PROFILE
"# rawrsembler-begin" | Out-File -FilePath $PROFILE -Append -Encoding ASCII
"# do not edit, remove or change these comments, it is used by 'rawrsembler' to install and uninstall itself" | Out-File -FilePath $PROFILE -Append -Encoding ASCII

# Add alias to compile.py
$compile = Join-Path $root "rawr.py"
"function rawr { `$input | & `"$venv_python`" `"$compile`" @args }" | Out-File -FilePath $PROFILE -Append -Encoding ASCII

# Add alias to get-wvrn-bin.py
$compile = Join-Path $root "./tools/get-wvrn-bin.py"
"function to-wve { `$input | & `"$venv_python`" `"$compile`" @args }" | Out-File -FilePath $PROFILE -Append -Encoding ASCII

# # Add alias to send.py
# $send = Join-Path $root "tools/send.py"
# "function rfsend { `$input | & `"$venv_python`" `"$send`" @args }" | Out-File -FilePath $PROFILE -Append -Encoding ASCII

Write-Host "Alias 'rawr' and 'to-wve' created in $PROFILE"

# Add $root to the PATH, if not already there
if ($env:PATH -notcontains $root) {
    "`$env:PATH += `";$root`"" | Out-File -FilePath $PROFILE -Append -Encoding ASCII
}

Write-Host "Added '$root' to the PATH"

"# rawrsembler-end" | Out-File -FilePath $PROFILE -Append -Encoding ASCII

# install vs code extrension if code is installed
# chceck if code is installed
# Check if Visual Studio Code is installed
if (Get-Command code -ErrorAction SilentlyContinue) {
    Write-Host "Visual Studio Code is installed. Installing rawrsembler-lit... (./rawrsembler-lit/rawrsembler-0.2.2.vsix)"
    & code --install-extension ./rawrsembler-lit/rawrsembler-0.2.2.vsix
} else {
    Write-Host "Visual Studio Code is not installed. Skipping extension installation."
}

Write-Host "Done"
Write-Host "You may need to restart your PowerShell session for changes to take effect"
