# FFMPEG Installation Script for Windows
# This script downloads and installs FFMPEG

Write-Host "Downloading FFMPEG for Windows..." -ForegroundColor Green

# Create tools directory
$toolsDir = "e:\New folder\Monitor Agent\tools"
New-Item -ItemType Directory -Force -Path $toolsDir | Out-Null

# Download FFMPEG (using a direct link to ffmpeg.org essentials build)
$ffmpegUrl = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
$ffmpegZip = Join-Path $toolsDir "ffmpeg.zip"
$ffmpegDir = Join-Path $toolsDir "ffmpeg"

Write-Host "Downloading from $ffmpegUrl..." -ForegroundColor Yellow

try {
    # Download
    Invoke-WebRequest -Uri $ffmpegUrl -OutFile $ffmpegZip -UseBasicParsing
    Write-Host "Download complete!" -ForegroundColor Green

    # Extract
    Write-Host "Extracting FFMPEG..." -ForegroundColor Yellow
    Expand-Archive -Path $ffmpegZip -DestinationPath $toolsDir -Force

    # Find the extracted folder (it has a version number)
    $extractedFolder = Get-ChildItem -Path $toolsDir -Directory | Where-Object { $_.Name -like "ffmpeg-*" } | Select-Object -First 1
    
    if ($extractedFolder) {
        $ffmpegBinPath = Join-Path $extractedFolder.FullName "bin"
        
        Write-Host "`nFFMPEG extracted to: $ffmpegBinPath" -ForegroundColor Green
        Write-Host "`nTo use FFMPEG, either:" -ForegroundColor Cyan
        Write-Host "1. Add to PATH permanently (recommended):" -ForegroundColor White
        Write-Host "   - Search 'Environment Variables' in Windows" -ForegroundColor Gray
        Write-Host "   - Edit 'Path' variable" -ForegroundColor Gray
        Write-Host "   - Add: $ffmpegBinPath" -ForegroundColor Gray
        Write-Host "`n2. Or add to current session:" -ForegroundColor White
        Write-Host "   `$env:PATH += ';$ffmpegBinPath'" -ForegroundColor Yellow
        
        # Add to current session
        $env:PATH += ";$ffmpegBinPath"
        
        Write-Host "`nFFMPEG added to current session PATH!" -ForegroundColor Green
        Write-Host "Testing FFMPEG..." -ForegroundColor Yellow
        
        & "$ffmpegBinPath\ffmpeg.exe" -version | Select-Object -First 1
        
        Write-Host "`nFFMPEG is ready to use!" -ForegroundColor Green
    }
    
    # Cleanup
    Remove-Item $ffmpegZip -Force
    
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host "`nPlease install FFMPEG manually from: https://ffmpeg.org/download.html" -ForegroundColor Yellow
}
