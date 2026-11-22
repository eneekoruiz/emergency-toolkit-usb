# EmergencyToolKitUSB

Herramientas y scripts reproducibles en PowerShell para la provisión y verificación de dos unidades USB de emergencia:

- **`USB_PRIVACIDAD_TAILS`:** Entorno amnésico con persistencia cifrada basado en Tails OS.
- **`USB_RESCATE_VENTOY`:** Sistema multiboot de diagnóstico, clonación, particionado y rescate.

El repositorio no almacena imágenes ni binarios pesados. El archivo `Arsenal_Digital/00_MANIFIESTOS/tools.json` define versiones, enlaces oficiales de descarga y sumas de verificación SHA-256.

## Uso rápido

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
.\Arsenal_Digital\scripts\Build-Arsenal.ps1
.\Arsenal_Digital\scripts\Verify-Arsenal.ps1
```

Para transferir las cargas verificadas a las unidades montadas:

```powershell
.\Arsenal_Digital\scripts\Export-ToUsb.ps1 -PrivacyDrive E: -RescueDrive F:
```

## Principios operativos

- Tails se instala exclusivamente en su unidad dedicada, sin coexistir con cargadores multiboot.
- Cada descarga se verifica criptográficamente contra su hash SHA-256 oficial antes de ser copiada.
- Los scripts no realizan acciones destructivas sobre discos sin confirmación explícita de letra de unidad.
