# Get all installed programs by looking for apps that registered an uninstall script.
# This is adapted from:
# https://devblogs.microsoft.com/scripting/use-powershell-to-quickly-find-installed-software/
# TODO: make this work remotely.
function Get-InstalledPrograms {
    param (
        $computerName
    )


    $uninstallkey = "SOFTWARE\\Microsoft\Windows\\CurrentVersion\\Uninstall"
    $reg = [microsoft.win32.registrykey]::OpenRemoteBaseKey('localMachine', $computername)

    $installed_programs = @()
    $regkey = $reg.OpenSubKey($UninstallKey)
    $subkeys = $regkey.GetSubKeyNames()
    foreach ($key in $subkeys) {
        $thiskey = $UninstallKey + "\\" + $key
        $thisSubKey = $reg.OpenSubKey($thiskey)
        # these are the three actually relevent properties
        $DisplayName = $thisSubKey.GetValue("DisplayName")
        $Version = $thisSubKey.GetValue("DisplayVersion")
        $Publisher = $thisSubKey.GetValue("Publisher")
        # there's lots of all-null entries, not sure why
        if ($null -eq $DisplayName ) {
            continue
        }
        $program = [PSCustomObject]@{
            name      = $DisplayName
            version   = $Version
            publisher = $Publisher
        }
        $installed_programs += $program

    }

    return $installed_programs
}

# Get the computer hardware specs, plus information Windows and the User.
# Saving the important ones separatly
function Get-Specs {

    # Get all properties
    $full = Get-ComputerInfo

    # clock speed isn't reported by Get-Computer info
    $clock_speed = Get-WmiObject -Class Win32_Processor -ComputerName. `
    | Select-Object -Property MaxClockSpeed
    $full | Add-Member -membertype NoteProperty -name ClockSpeed `
        -value $clock_speed.MaxClockSpeed

    return $full
}

function Get-IPAddresses {
    $ips = Get-NetIPAddress

    $formatted = @()

    foreach ($ip in $ips) {
        # ignore IPV6 and loopback
        if (($ip.AddressFamily -eq 23) -or ($ip.IPAddress -eq "127.0.0.1") ) {
            continue
        }
        $network = [PSCustomObject]@{
            Alias = $ip.InterfaceAlias
            IP    = $ip.IPAddress
        }
        $formatted += $network
    }

    return $formatted

}

$full = Get-Specs

# where the files will be created
$output_dir = "computer_information/"
# use -force flag to allow for already existing directory
mkdir -f $output_dir
Set-Location $output_dir

# this should be unique and descriptive enough
$timestamp = get-date -DisplayHint time
$filename = $full.OsRegisteredUser + "_" + $full.CsName + "_" + $timestamp
# sanitize it for use as a path -- replace invalid characters with an underscore
$filename = $filename -replace '[<>:"/\\|?*]', '_'



# I decided to output everything as JSON, then later we can pull out
# whatever's relevant.
$json_output = [PSCustomObject]@{
    specs              = $full
    networking         = Get-IPAddresses
    installed_software = Get-InstalledPrograms  $env:COMPUTERNAME
}

$json = ConvertTo-Json $json_output
Write-Output $json > ($filename + ".json")
