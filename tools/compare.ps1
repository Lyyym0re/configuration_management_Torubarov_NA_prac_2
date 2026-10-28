$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$dotnet = Join-Path $root '.tools/dotnet/dotnet.exe'
$env:DOTNET_CLI_HOME = Join-Path $root '.tools/dotnet-home'
$env:DOTNET_CLI_TELEMETRY_OPTOUT = '1'
$env:DOTNET_NOLOGO = '1'
$env:NUGET_PACKAGES = Join-Path $root 'output/native/packages'
$packages = 'DependencyInjection', 'Options', 'Logging'
foreach ($name in $packages) {
    $package = "Microsoft.Extensions.$name"
    $directory = Join-Path $root "output/native/$name"
    New-Item -ItemType Directory -Force -Path $directory | Out-Null
    $project = Join-Path $directory 'Comparison.csproj'
    $xml = '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup>'
    $xml += '<TargetFramework>net10.0</TargetFramework></PropertyGroup><ItemGroup>'
    $xml += "<PackageReference Include=`"$package`" Version=`"[9.0.0]`" />"
    $xml += '</ItemGroup></Project>'
    Set-Content -LiteralPath $project -Value $xml -Encoding utf8
    & $dotnet restore $project --source https://api.nuget.org/v3/index.json
    if ($LASTEXITCODE) { throw 'Restore failed' }
    $listing = & $dotnet package list --project $project --include-transitive --format json --no-restore
    if ($LASTEXITCODE) { throw 'Package list failed' }
    $listing | Set-Content (Join-Path $directory 'packages.json') -Encoding utf8
    $framework = ($listing | ConvertFrom-Json).projects[0].frameworks[0]
    foreach ($item in @($framework.topLevelPackages) + @($framework.transitivePackages)) {
        & $dotnet nuget why $project $item.id --framework net10.0
        if ($LASTEXITCODE) { throw 'Dependency tree failed' }
    }
}
