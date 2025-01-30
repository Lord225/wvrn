# remove alias from $profile
if (Select-String -Path $PROFILE -Pattern "rawrsembler-begin") {
    Write-Host "Removing installation of 'rawrsembler' from $PROFILE."
    $content = Get-Content $PROFILE -Raw
    $content = $content -replace "(?ms)(\# rawrsembler-begin)(.*?)(\# rawrsembler)\s*", ""
    Set-Content $PROFILE $content
}