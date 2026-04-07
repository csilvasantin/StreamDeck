-- Guardar app en primer plano (con manejo de error por si Stream Deck no tiene frontmost)
set frontApp to ""
try
    tell application "System Events"
        set frontApp to name of first application process whose frontmost is true
    end tell
end try

-- Activar Claude y enviar Enter (aprobación)
tell application "Claude" to activate
delay 0.3
tell application "System Events"
    key code 36
end tell

-- Devolver foco al app original
delay 0.2
if frontApp is not "" and frontApp is not "Claude" then
    try
        tell application frontApp to activate
    end try
end if
