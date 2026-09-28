# Original typographic identity card. No downloaded images or bundled fonts.
. (Join-Path $PSScriptRoot 'BuildCommon.ps1')
Add-Type -AssemblyName System.Drawing
$outputPath = Join-Path (Get-RimroomsRoot) 'Mod/Rimrooms - Async Industries/About/Preview.png'
$bitmap = New-Object Drawing.Bitmap 960, 540
$graphics = [Drawing.Graphics]::FromImage($bitmap)
$graphics.SmoothingMode = [Drawing.Drawing2D.SmoothingMode]::AntiAlias
$graphics.TextRenderingHint = [Drawing.Text.TextRenderingHint]::AntiAliasGridFit
$resources = [Collections.Generic.List[IDisposable]]::new()
function New-CardBrush([string] $Hex) {
    $brush = [Drawing.SolidBrush]::new([Drawing.ColorTranslator]::FromHtml($Hex))
    $resources.Add($brush)
    return $brush
}
function New-CardPen([string] $Hex, [single] $Width) {
    $pen = [Drawing.Pen]::new([Drawing.ColorTranslator]::FromHtml($Hex), $Width)
    $resources.Add($pen)
    return $pen
}
function New-CardFont([single] $Size, [Drawing.FontStyle] $Style = [Drawing.FontStyle]::Regular) {
    $font = [Drawing.Font]::new('Arial', $Size, $Style, [Drawing.GraphicsUnit]::Pixel)
    $resources.Add($font)
    return $font
}
try {
    $graphics.Clear([Drawing.ColorTranslator]::FromHtml('#141A1D'))
    $paper = New-CardBrush '#EEE8D5'
    $muted = New-CardBrush '#A8B0AD'
    $amber = New-CardBrush '#D3B46C'
    $dark = New-CardBrush '#080D10'
    $steel = New-CardBrush '#263135'
    $line = New-CardPen '#415053' 2
    $warmLine = New-CardPen '#D3B46C' 3
    $graphics.FillRectangle($amber, 48, 48, 48, 6)
    $graphics.DrawString('RIMWORLD MOD', (New-CardFont 17), $muted, 112, 42)
    $graphics.DrawString('RIMROOMS', (New-CardFont 74 ([Drawing.FontStyle]::Bold)), $paper, 42, 128)
    $graphics.DrawString('Async Industries', (New-CardFont 34), $amber, 48, 220)
    $graphics.DrawLine($line, 48, 300, 530, 300)
    $graphics.DrawString('COMPANY RESEARCH / UNKNOWN SPACES', (New-CardFont 16), $muted, 48, 326)
    $graphics.DrawString('FOUNDATION BUILD  0.1.0', (New-CardFont 18 ([Drawing.FontStyle]::Bold)), $paper, 48, 426)
    $graphics.DrawString('Operator', (New-CardFont 16), $muted, 48, 460)
    # Nested structural frames are an original identity mark, not a gameplay screenshot.
    $graphics.FillRectangle($steel, 618, 84, 278, 370)
    $graphics.FillRectangle($dark, 640, 106, 234, 348)
    $graphics.DrawRectangle($warmLine, 640, 106, 234, 348)
    $graphics.DrawRectangle($line, 674, 146, 166, 308)
    $graphics.DrawRectangle($line, 704, 184, 106, 270)
    $graphics.DrawLine($line, 588, 492, 732, 426)
    $graphics.DrawLine($line, 934, 492, 782, 426)
    $graphics.FillRectangle($amber, 725, 220, 64, 5)
    $graphics.DrawString('01', (New-CardFont 16), $muted, 866, 470)
    $bitmap.Save($outputPath, [Drawing.Imaging.ImageFormat]::Png)
    Write-Output "Rendered original 960 x 540 identity card: $outputPath"
} finally {
    foreach ($resource in $resources) { $resource.Dispose() }
    $graphics.Dispose()
    $bitmap.Dispose()
}
