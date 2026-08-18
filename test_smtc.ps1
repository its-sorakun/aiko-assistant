using namespace Windows.Media.Control;
Add-Type -AssemblyName System.Runtime.WindowsRuntime;

$manager = [GlobalSystemMediaTransportControlsSessionManager]::RequestAsync().GetResults()
$session = $manager.GetCurrentSession()

if ($null -eq $session) {
    Write-Output "No active media session."
    exit
}

$mediaProperties = $session.TryGetMediaPropertiesAsync().GetResults()

$title = $mediaProperties.Title
$artist = $mediaProperties.Artist

Write-Output "$title - $artist"
