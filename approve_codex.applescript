-- Guardar app en primer plano
tell application "System Events"
    set frontApp to name of first application process whose frontmost is true
end tell

-- Activar Codex y enviar Enter (aprobación)
tell application "Codex" to activate
delay 0.3
tell application "System Events"
    key code 36
end tell

-- Devolver foco al app original
delay 0.2
if frontApp is not "Codex" then
    tell application frontApp to activate
end if
