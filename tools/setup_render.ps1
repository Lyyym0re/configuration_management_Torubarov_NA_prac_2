$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$toolsRoot = Join-Path $projectRoot '.tools'
New-Item -ItemType Directory -Force -Path $toolsRoot | Out-Null
$version = '1.2026.9'
$base = 'https://github.com/plantuml/plantuml/releases/download'
$url = "$base/v$version/plantuml-java8-$version.jar"
Invoke-WebRequest -Uri $url -OutFile (Join-Path $toolsRoot 'plantuml.jar')
Write-Output "PlantUML $version installed locally. Java 8+ is required."
