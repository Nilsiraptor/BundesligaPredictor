$EndYear = (Get-Date).Year

# Bundesliga

$StartYear = 2025

# The base URL for the Bundesliga season data on Transfermarkt.de
$baseUrl = "https://www.transfermarkt.de/bundesliga/gesamtspielplan/wettbewerb/L1?saison_id="

# The name of the folder where the downloaded files will be saved
$downloadFolder = "websites"

# --- Script Logic ---

Write-Host "Starting Bundesliga download process..."

# Create the download folder if it doesn't exist
try {
    if (-not (Test-Path -Path $downloadFolder)) {
        New-Item -Path $downloadFolder -ItemType Directory | Out-Null
        Write-Host "Created download folder: $downloadFolder"
    }
}
catch {
    Write-Host "Error creating folder: $_" -ForegroundColor Red
    return # Exit the script if the folder cannot be created
}

# Loop through each year from the start year to the end year
for ($year = $StartYear; $year -le $EndYear; $year++) {
    $url = "$baseUrl$year"
    $outputFile = Join-Path -Path $downloadFolder -ChildPath "bundesliga_$($year).html"

    Write-Host "Attempting to download data for year $year from $url..."

    try {
        # The 'curl' command is an alias for Invoke-WebRequest in PowerShell
        # Use Invoke-WebRequest for better compatibility and control
        Invoke-WebRequest -Uri $url -OutFile $outputFile -TimeoutSec 60
        Write-Host "Successfully downloaded data for year $year and saved to $outputFile" -ForegroundColor Green
    }
    catch {
        Write-Host "Error downloading data for year ${year}: $_" -ForegroundColor Red
    }

    # Add a delay to avoid overwhelming the server with requests
    Start-Sleep -Seconds 0.1
}

Write-Host "Bundesliga Download process completed."


# 2. Bundesliga

$StartYear = 2025

# The base URL for the Bundesliga season data on Transfermarkt.de
$baseUrl = "https://www.transfermarkt.de/2-bundesliga/gesamtspielplan/wettbewerb/L2?saison_id="

# The name of the folder where the downloaded files will be saved
$downloadFolder = "websites"

# --- Script Logic ---

Write-Host "Starting Bundesliga download process..."

# Loop through each year from the start year to the end year
for ($year = $StartYear; $year -le $EndYear; $year++) {
    $url = "$baseUrl$year"
    $outputFile = Join-Path -Path $downloadFolder -ChildPath "bundesliga2_$($year).html"

    Write-Host "Attempting to download data for year $year from $url..."

    try {
        # The 'curl' command is an alias for Invoke-WebRequest in PowerShell
        # Use Invoke-WebRequest for better compatibility and control
        Invoke-WebRequest -Uri $url -OutFile $outputFile -TimeoutSec 60
        Write-Host "Successfully downloaded data for year $year and saved to $outputFile" -ForegroundColor Green
    }
    catch {
        Write-Host "Error downloading data for year ${year}: $_" -ForegroundColor Red
    }

    # Add a delay to avoid overwhelming the server with requests
    Start-Sleep -Seconds 0.1
}

Write-Host "2. Bundesliga Download process completed."
