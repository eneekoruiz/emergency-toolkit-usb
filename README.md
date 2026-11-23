# Emergency Toolkit USB · Aprovisionamiento y Rescate del Sistema

Scripts de automatización en PowerShell y especificaciones de configuración para la preparación, particionado y verificación de integridad de unidades USB de rescate y privacidad del sistema.

- **Documentación de arquitectura:** [DeepWiki - emergency-toolkit-usb](https://deepwiki.com/eneekoruiz/emergency-toolkit-usb)

## Propósito y Valor Técnico

Herramienta diseñada para administradores de sistemas y técnicos que necesitan preparar entornos de rescate fiables, reproducibles y completamente aislados de internet (Air-Gapped) para diagnóstico, recuperación de datos y desinfección forense.

- **Aprovisionamiento Automatizado:** Formatea y particiona memorias flash USB aplicando esquemas de particionado híbrido (partición FAT32 activa para arranque universal UEFI/BIOS y partición NTFS para imágenes WIM pesadas y volcados de disco).
- **Verificación Criptográfica de Integridad:** Comprueba los hashes criptográficos (SHA-256) de todas las utilidades portátiles (Sysinternals, herramientas de disco, utilidades de red y navegadores portables) frente a un catálogo de firmas de confianza antes de dar por buena la unidad.
- **Operación Estrictamente Aislada:** Todos los scripts y binarios aprovisionados funcionan de manera autónoma sin requerir conectividad de red ni telemetría externa.

## Stack Técnico

- **Entorno de Scripting:** PowerShell 5.1 / PowerShell 7+
- **Plataformas de Ejecución:** Windows PE, WinRE, utilidades portables de Windows de 64 bits

## Uso y Ejecución

### Prerrequisitos

- Windows 10/11 con consola de PowerShell ejecutada como Administrador
- Unidad flash USB (mínimo 16 GB recomendado)

### Flujo de Preparación

```powershell
# Acceder al directorio de utilidades
cd Arsenal_Digital

# Listar scripts de aprovisionamiento disponibles
Get-ChildItem -Filter *.ps1

# Ejecutar el aprovisionamiento sobre la unidad USB seleccionada
.\prepare-rescue-usb.ps1 -DriveLetter E:
```
