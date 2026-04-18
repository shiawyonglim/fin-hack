Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SetOutputToWaveFile("c:\finhack\fin-hack\ai_engine\scripts\sample_voice.wav")
$synth.Speak("Transfer two hundred and fifty ringgit to Mr. Loy.")
$synth.Dispose()
