param(
    [switch] $NoBuild,
    [switch] $NoBrowser,
    [switch] $ForcePull
)

$scriptPath = Split-Path $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Set our defaults if not overrides are supplied
if (-not (Test-Path env:ML_IMAGE)) { $env:ML_IMAGE = 'ml-fundamentals' }
if (-not (Test-Path env:RUN_BUILD)) { $env:RUN_BUILD = 'build' }
if (-not (Test-Path env:DOCKER_DS_DIFFS)) { $env:DOCKER_DS_DIFF = 'no_diffs' }

if (Test-Path env:DOCKER_HOST) {
    Write-Host "*** WARNING: The DOCKER_HOST env has been set, if this does not point to your local instance you may run into problems ***" -ForegroundColor Red
}

if ($ForcePull) {
    docker pull rappdw/docker-ds
}

if ($NoBuild) {
    $env:RUN_BUILD = 'no'
}

$image = $env:ML_IMAGE
if ($env:RUN_BUILD -eq 'build') {
    Write-Host "*** Building the docker image ***" -ForegroundColor Green

    if (Test-Path -Path ("${scriptPath}\docker\Dockerfile.custom")) {
        Write-Host "*** docker\Dockerfile.custom exists, using as Dockerfile"
        $dockerFile = "${scriptPath}\docker\Dockerfile.custom"
    } else {
        $dockerFile = "${scriptPath}\docker\Dockerfile"
    }

    Write-Host "docker build -t $image -f $dockerFile $scriptPath" -ForegroundColor Green
    docker build -t $image -f $dockerFile $scriptPath

    if (-not ($?)) {
        Write-Host "Failed to build image" -ForegroundColor Red
        exit 1
    }
}

# We can ignore this now as we added .ipynb_checkpoints directory to git (not the contents)
#if (-not (Test-Path -Path '.ipynb_checkpoints')) {
#   New-Item -ItemType directory -Path '.ipynb_checkpoints'
#}

$dockerEnv = ''
if ($env:DOCKER_DS_DIFF -ne 'no_diffs') {
    $dockerEnv= "-e DOCKER_DS_DIFFS=1"
}

$dateStamp = (Get-Date).ToString('yyyy_MM_dd_HH.MM.ss')
$name = "${env:username}_notebook_${dateStamp}".Trim()

$volumeMounts = "--mount type=bind,source='${scriptPath}',target=/home/jovyan/project"
if (Test-Path -Path ("${env:userprofile}\.aws")) {
    Write-Host "We have a $HOME/.aws directory, mounting" -ForegroundColor Green
    $volumeMounts = "${volumeMounts} --mount type=bind,source='${env:userprofile}\.aws',target=/home/jovyan/.aws".Trim()
}

if (Test-Path -Path ("${scriptPath}\.jupyter")) {
    Write-Host "We have a .jupyter folder, mounting for configuration"
    $volumeMounts = "${volumeMounts} --mount type=bind,source='${scriptPath}\.jupyter',target=/home/jovyan/.jupyter".Trim()
}

$dockerEnv = "${dockerEnv} -e NOTEBOOK_MODE=lab".Trim()
$runCommand = "docker run --rm -it -p 8888:8888 --init --name '${name}' ${dockerEnv} $volumeMounts $image"

if (-not $NoBrowser) {
    Start-Job {
        Start-Sleep 2
        Write-Host "`n*** Opening Browser to http://localhost:8888/lab ***`n" -ForegroundColor Green
        Start-Process http://localhost:8888/lab 
    }
}
else
{
    Write-Host "`n*** Not opening browser for as -NoBrowser was supplied ***`n" -ForegroundColor Green
}

Write-Host "`n*** Starting the docker container ***" -ForegroundColor Green
Write-Host "$runCommand" -ForegroundColor Green
Invoke-Expression $runCommand
