# StreamDeck

Configuración y scripts para el **Elgato Stream Deck XL** en AdmiraNext.

## Dispositivo

- **Modelo:** Elgato Stream Deck XL (32 botones)
- **Máquina:** MacBookAirBlanco (csilvasantin)

## Botones configurados

### Fila superior — aprobaciones AI

| Posición | Botón | Descripción |
|----------|-------|-------------|
| `3,0` | ✓ Claude | Aprueba el permiso pendiente en Claude Code |
| `4,0` | ✓ Codex | Aprueba el permiso pendiente en Codex |

**Comportamiento:**
1. Enfoca automáticamente la app correspondiente (Claude o Codex)
2. Envía `Enter` para aprobar el permiso
3. Devuelve el foco al app donde estabas trabajando

### Fila inferior — modo reposo

| Posición | Botón | Descripción |
|----------|-------|-------------|
| `3,3` | 🌙 Admira Sleep | Lanza el protector de pantalla Admira inmediatamente |

Al pulsarlo el Stream Deck entra en reposo y muestra la imagen `ADMIRA NEXT` distribuida por los 32 botones. Se activa también automáticamente tras **15 minutos** de inactividad.

## Scripts

### `approve_claude.applescript` / `AprovaClaude.app`

Envía aprobación a Claude Code sin soltar el ratón ni cambiar de ventana manualmente.

### `approve_codex.applescript` / `AprovaCodex.app`

Mismo comportamiento para Codex.

### `generate_screensaver.py`

Genera la imagen del protector de pantalla (`screensaver_admira_full.png`, 768×384 px) con la paleta dorada/azul marino de AdmiraNext. Ejecútalo con `/opt/homebrew/bin/python3 generate_screensaver.py` y carga el PNG resultante en **Preferencias → Dispositivos → Seleccionar protector de pantalla**.

## Instalación

### Requisitos

- macOS con [Elgato Stream Deck](https://www.elgato.com/downloads) instalado
- Stream Deck XL conectado por USB

### Pasos

1. Clona el repositorio:
   ```bash
   git clone https://github.com/csilvasantin/StreamDeck.git ~/StreamDeck
   ```

2. Compila los scripts AppleScript:
   ```bash
   osacompile -o ~/StreamDeck/AprovaClaude.app ~/StreamDeck/approve_claude.applescript
   osacompile -o ~/StreamDeck/AprovaCodex.app ~/StreamDeck/approve_codex.applescript
   ```

3. Concede permisos de **Accesibilidad** en:
   **Ajustes del Sistema → Privacidad y Seguridad → Accesibilidad**
   - Añade `AprovaClaude.app`
   - Añade `AprovaCodex.app`

4. Importa el perfil del Stream Deck o configura los botones manualmente apuntando a los `.app` compilados mediante la acción **Open** de Stream Deck.

## Configuración del perfil Stream Deck

El perfil se almacena en:
```
~/Library/Application Support/com.elgato.StreamDeck/ProfilesV3/
```

Los botones usan la acción `com.elgato.streamdeck.system.open` apuntando a cada `.app`.

## GitHub SSH

Clave SSH configurada para este repositorio:
```
~/.ssh/github_ed25519
```
Añadida a `github.com/settings/keys` como `MacBookAirBlanco`.
