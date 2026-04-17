Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SetOutputToWaveFile("c:\finhack\fin-hack\sample_voice.wav")
$synth.Speak("Transfer two hundred and fifty ringgit to Mr. Loy.")
$synth.Dispose()
