<#
.SYNOPSIS
    Downloads Bundesliga season data from Transfermarkt.de for a range of years.

.DESCRIPTION
    This script iterates through a specified range of years, constructs a URL for each
    season's game plan on Transfermarkt.de, and downloads the HTML content. The
    downloaded files are saved in a local folder, with each file named after its
    corresponding season.

.PARAMETER StartYear
    The first year of the season range to download. Defaults to 1963.

.PARAMETER EndYear
    The last year of the season range to download. Defaults to the current year.

.EXAMPLE
    .\download_bundesliga.ps1
    # This will download all Bundesliga seasons from 1963 to the current year.

.EXAMPLE
    .\download_bundesliga.ps1 -StartYear 2000 -EndYear 2010
    # This will download Bundesliga seasons from 2000 to 2010.

#>

[CmdletBinding()]
param (
    [int]$StartYear = 1981,
    [int]$EndYear = (Get-Date).Year
)

# --- Configuration ---
# The base URL for the Bundesliga season data on Transfermarkt.de
$baseUrl = "https://www.transfermarkt.de/2-bundesliga/gesamtspielplan/wettbewerb/L2?saison_id="

# The name of the folder where the downloaded files will be saved
$downloadFolder = "websites"

# --- Script Logic ---

Write-Host "Starting download process..."

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
    Start-Sleep -Seconds 1
}

Write-Host "Download process completed."
