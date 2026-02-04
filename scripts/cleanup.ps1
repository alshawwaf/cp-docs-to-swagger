# Cleanup script for removing debug and temporary files
# Run this before committing to GitHub

Write-Host "Cleaning up debug and temporary files..." -ForegroundColor Cyan

# Define files to remove
$filesToRemove = @(
    "debug_gaia_examples.py",
    "debug_log.txt",
    "debug_output.txt",
    "debug_output_2.txt",
    "debug_output_3.txt",
    "debug_output_4.txt",
    "changes_dump.json",
    "content_dump.json",
    "content_dump_utf8.json",
    "api_versions.html",
    "infinity_threat_prevention.html",
    "introduction.html",
    "raw_changelog.html"
)

$removedCount = 0
$notFoundCount = 0

foreach ($file in $filesToRemove) {
    if (Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "  [REMOVED] $file" -ForegroundColor Green
        $removedCount++
    } else {
        Write-Host "  [NOT FOUND] $file" -ForegroundColor Yellow
        $notFoundCount++
    }
}

Write-Host "`nCleanup complete!" -ForegroundColor Cyan
Write-Host "  Removed: $removedCount files" -ForegroundColor Green
Write-Host "  Not found: $notFoundCount files" -ForegroundColor Yellow
