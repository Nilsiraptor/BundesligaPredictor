Write-Host "Run Download Script..." -ForegroundColor Yellow
& ".\download_websites.ps1"

Write-Host "Run Scrape Script..." -ForegroundColor Yellow
py ".\scrape_websites.py"

Write-Host "Run Combining Script..."  -ForegroundColor Yellow
py ".\combine_datasets.py"

Write-Host "Run Training Script..."  -ForegroundColor Yellow
py ".\train_model.py"

Write-Host "Finished Updating the Model with the newest Data"  -ForegroundColor Green
