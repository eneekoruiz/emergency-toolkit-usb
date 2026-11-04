# T09 — Auditoría integral de EmergencyToolKitUSB

Fecha: 4 de noviembre de 2026. **Auditoría documental y estática completada; aptitud de campo pendiente.** No se ha demostrado que ningún USB arranque ni que una reparación o recuperación funcione en el hardware objetivo.

El kit prepara dos USB: privacidad con Tails dedicado y rescate con Ventoy. Se ha evaluado para un operador que trabaja secuencialmente, con datos potencialmente sensibles y discos que pueden fallar. No se ha considerado un servicio multiusuario.

## Alcance y evidencia

Código revisado: candidato basado en `4dd60b44892b2df0305adbb590f1bf7b74fa6a18`, con cambios locales de verificación/exportación y sus pruebas. Los payloads se inventariaron **en lectura**, en la copia local independiente; no están incorporados al candidato. La primera auditoría examinó otra revisión local (`44f3c2d`): sus cifras no describen necesariamente el candidato remoto.

Evidencia privada, fuera del repositorio: `T09-auditoria-final.json`, `T09-PRIMERA-AUDITORIA.md`, `T09-hashes.json` y resultados del verificador conservados por la sesión coordinadora. El JSON final registra metadatos, versiones declaradas, existencia, parseo y firmas sin incluir claves ni contenido de casos. No publicar esta evidencia privada junto con el informe.

Inventario local: **480 archivos, 57 subdirectorios, 16.207.058.959 bytes (15,09 GiB)**; 167 EXE, 70 DLL, 27 scripts PowerShell, 30 Markdown, 16 sidecars SHA-256, 7 ISO y 5 ZIP. Las dos extensiones IMG incluyen Tails y una imagen interna de arranque de Ventoy. El volumen de archivos no equivale a 167 herramientas independientes: hay arquitecturas y dependencias de paquetes.

## Inventario de herramientas y menús

El manifiesto del candidato contiene 13 entradas, 12 habilitadas. Ocho rutas habilitadas coinciden literalmente con los payloads locales. Las cuatro restantes requieren distinguir cambio de nombre y cambio de versión:

| Componente | Candidato / carga local observada | Tamaño del archivo principal | Resultado |
|---|---|---:|---|
| Tails | 7.9.1 / `tails-amd64-7.12.img` | 1,88 GB | Desfase real; el archivo declarado por el candidato falta |
| Ventoy | 1.1.16 / ZIP y directorio extraído | 16,7 MB ZIP | Presente; instalador, no prueba de instalación en USB |
| SystemRescue | 13.01 | 1,36 GB | Presente |
| GParted Live | 1.8.1-3 | 649 MB | Presente |
| Ubuntu Desktop / Server | 26.04 / 26.04 | 6,52 / 2,92 GB | Ambos presentes; distintos usos, no duplicados idénticos |
| Rescuezilla | 2.6.2 | 1,72 GB | Presente; hash no fijado en el manifiesto |
| Rufus | `latest` / `rufus-4.15.exe` | 1,99 MB | Presente con nombre resuelto; no falta funcionalmente |
| KeePassXC | `latest` / ZIP 2.7.11 y extraído | 35,2 MB ZIP | Presente con nombre resuelto |
| TestDisk / PhotoRec | 7.2 Win64, ZIP y extraído | 27,4 MB ZIP | Presente |
| Memtest86+ | 8.10 ZIP y `grub-memtest.iso` | 6,59 / 20,2 MB | Presente; extraer ISO es necesario para el arranque |
| ShredOS | versión declarada 0.41 / ISO 0.42 | 108 MB | Presente con nombre resuelto y versión diferente |
| Clonezilla | deshabilitado | — | Ausencia deliberada; Rescuezilla cubre el uso habitual |
| Sysinternals Suite | ZIP y extraído; fuera del manifiesto | 202 MB ZIP | Presente; versión por ejecutable no inventariada exhaustivamente |
| Microsoft Safety Scanner | `msert-x64.exe`; fuera del manifiesto | 226 MB | Presente; copia fechada 08/09/2026, caducada para uso actual |

`ventoy/ventoy.json` tiene tres alias explícitos, para SystemRescue, GParted y Rescuezilla, con rutas coherentes con esos nombres. El resto depende del descubrimiento automático de imágenes de Ventoy; no existe un lanzador Windows central. Tails permanece separado. `USB_AUDITORIA_KALI`, `THREAT_HUNTING` y `SECRETS` aportan documentación/protocolos; no prueban que haya una imagen Kali, VeraCrypt, una bóveda o un arsenal de análisis adicional instalado.

Los ZIP y sus extracciones facilitan actualización y uso offline: no se propone borrarlos automáticamente. GParted Live solapa herramientas de SystemRescue, pero ofrece acceso visual directo; es opcional reducir ese solapamiento tras pruebas. No añadir Clonezilla, otra distribución de pentesting ni otro gestor de contraseñas sin un caso concreto.

## Inventario de los 27 scripts

| Grupo | Scripts | Comportamiento y límites |
|---|---|---|
| Preparación y mantenimiento | `Build-Arsenal`, `Update-Arsenal`, `Download-EmergencyTools`, `Install-WindowsFieldKit`, `Expand-HardwarePayloads` | Descargan/extraen, escriben logs y sidecars; requieren red para actualizar. `Download-EmergencyTools` delega en el instalador Windows |
| Integridad y despliegue | `Verify-Arsenal`, `Validate-Arsenal`, `Export-ToUsb`, `Install-ArsenalFolder` | Verifican/copian; exportar archivos no instala Ventoy ni graba la imagen Tails |
| Casos y trazabilidad | `Start-ArsenalAudit`, `Initialize-IncidentWorkspace`, `New-RescueCaseLog` | Crean carpetas/transcripciones/notas; una transcripción editable no es evidencia inmutable |
| Diagnóstico | `Test-HardwareHealth`, `Get-DiskSnapshot`, `Network-Triage`, `Collect-TriageData`, `Export-SystemInventory`, `Export-EventLogs` | Consultan estado y exportan datos; acceso parcial sin administrador y funciones específicas de Windows |
| Copias | `Backup-UserProfiles`, `Backup-NetworkConfig`, `Backup-WindowsDrivers` | Copias/exportaciones; perfiles usan `/E`, no `/MIR`; no prueban restaurabilidad |
| Reparación e instalación | `Repair-WindowsSystemFiles`, `Repair-WindowsBoot-Runbook`, `Get-WindowsISO` | SFC/DISM modifica el sistema; el runbook de arranque solo imprime comandos; el helper ISO imprime instrucciones y opcionalmente abre la web |
| Destrucción | `Secure-WipeDisk`, `Secure-WipeFile` | Sobrescriben/eliminan tras confirmaciones; excluidos de ejecución en esta auditoría |
| Reputación | `Query-VirusTotal` | Envía un hash y utiliza una clave local; no sube el archivo, no funciona offline ni acredita ausencia de malware |

Nombres abreviados: todos terminan en `.ps1` y están en `Arsenal_Digital/scripts`. Los playbooks cubren RAW, BitLocker, arranque, registro offline, virtualización de discos, respuesta a ransomware, forense Windows, Linux y redes. Los procedimientos de contraseñas y captura de tráfico requieren autorización del propietario; no se ejecutaron.

## Cobertura funcional

| Área requerida | Cobertura existente | Falta de evidencia / límite |
|---|---|---|
| Hardware, HDD/SSD/USB y SMART | Get-PhysicalDisk; SystemRescue; GParted Live/GSmartControl | El resumen Healthy no equivale a atributos SMART completos; probar SATA/NVMe y puente USB real |
| RAM | Inventario WMI y Memtest86+ | Inventariar RAM no prueba su integridad; faltan pasadas en equipo real |
| Redes | PowerShell, TCPView y herramientas Linux | `Network-Triage` contacta 1.1.1.1 por defecto; no es una operación totalmente offline |
| Sistema, procesos y logs | Exportaciones, Procmon, Process Explorer, Autoruns | Permisos, archivos bloqueados y captura parcial pendientes de prueba |
| Copias e imagen | Robocopy, drivers, Rescuezilla, Disk2vhd | No se ha restaurado una copia sintética ni una imagen |
| Recuperación de archivos | TestDisk/PhotoRec y playbooks | Primero imagen y destino distinto; no probar sobre el original |
| Discos defectuosos | SystemRescue y GNU ddrescue | Verificar disponibilidad y persistencia de mapfile en la ISO concreta |
| Particiones y arranque | GParted, SystemRescue, runbook WinRE/bcdboot | No hay medio Windows de reparación verificado; Ubuntu no sustituye WinRE |
| Seguridad / antimalware | MSERT, Sysinternals y consulta de reputación | MSERT caducado, sin protección continua ni diagnóstico confiable desde un SO comprometido |
| Rescate Linux e instalación | SystemRescue y Ubuntu | Detección real de red, RAID/VMD, almacenamiento y teclado pendiente |
| Privacidad y credenciales | Tails dedicado, KeePassXC y protocolo de bóveda | Ninguna prueba de persistencia cifrada, separación de identidades o desbloqueo BitLocker |
| Borrado | ShredOS y dos scripts | No se acredita sanitización de SSD/NVMe ni borrado forense de archivos |

Las funciones Linux se apoyan en documentación oficial, **sin montar ni inspeccionar los paquetes internos de cada ISO**: [herramientas de SystemRescue](https://www.system-rescue.org/System-tools/) y [contenido de GParted Live](https://gparted.org/livecd.php). Deben confirmarse al arrancar la versión local.

## Hallazgos priorizados

### Imprescindibles antes de usar en campo

**1. P1 — La versión declarada y la instalada divergen.** `tools.json` del candidato fija Tails 7.9.1 y Validate repite esa ruta; el payload local es 7.12. ShredOS está versionado de forma distinta en manifiesto, nombre resuelto y lista crítica. Rufus/KeePassXC usan `latest`, por lo que no encontrar sus alias literales no demuestra ausencia. Corrección mínima pendiente: reconciliar versiones/nombres y conservar URL, digest y fecha resueltos; derivar validación del inventario en vez de mantener listas paralelas. Sin ello el constructor puede traer una versión anterior y la validación produce falsos faltantes.

**2. P1 — MSERT caducado solo genera advertencia.** `Validate-Arsenal.ps1` permite terminar OK aunque la fecha del archivo tenga más de diez días. La copia local tiene unos 57 días; una firma válida no renueva definiciones. Exigir actualización o marcar antimalware no disponible antes de campo; no interpretar OK como aptitud antimalware. Microsoft establece caducidad a los diez días y recomienda descargar de nuevo antes de cada análisis: [Safety Scanner](https://learn.microsoft.com/en-us/defender-endpoint/safety-scanner-download).

**3. P1 — Borrado de disco informa éxito sin comprobar el resultado nativo.** `Secure-WipeDisk.ps1` ejecuta `diskpart` y escribe `wipe_completed` sin validar código de salida ni resultado. Un error del programa puede producir un registro engañoso. Además acepta el marcador `SIN_SERIAL` y selecciona por número de disco después de la confirmación; hay riesgo si cambia la enumeración. Antes de habilitarlo: abortar sin identificador inequívoco, volver a comprobar identidad/estado y registrar éxito solo tras verificar el resultado. No se ha ejecutado ni simulado DiskPart.

**4. P1 — Reparación del SO sin confirmación y sin comprobar errores.** `Repair-WindowsSystemFiles.ps1`, iniciado con administrador y sin parámetros, ejecuta SFC/DISM inmediatamente. Contradice el principio del README de exigir parámetros/confirmación para operaciones modificadoras. El mensaje final no comprueba sus códigos de retorno. Añadir confirmación explícita y resultados por fase antes de recomendar su uso; offline necesita una fuente DISM adecuada, que el script actual no configura.

**5. P1 — La exclusión Git no protege secretos ni todos los artefactos.** `.gitignore` excluye ISO/IMG/ZIP/EXE/MSI y parte de logs/herramientas, pero no `.env*`, `SECRETS/VT_API_KEY.txt`, bóvedas/claves, CASOS, DLL de extracciones, cachés Python ni los patrones globales de modelos pesados. Una futura clave o caso puede entrar accidentalmente en Git. Completar exclusiones y verificar el índice antes de publicar; no se inspeccionaron valores de secretos. No hay autorización de publicación de payloads ni evidencias privadas.

### Recomendables

**6. P2 — Integridad local no equivale a autenticidad ni cobertura total.** Verify comprueba los sidecars existentes: no conoce automáticamente qué archivo debería tener sidecar. Un paquete y su hash reemplazados juntos siguen coincidiendo. `Install-WindowsFieldKit` genera hashes de archivos ya presentes y solo exige firma en una selección de EXE; si falta un EXE de esa selección, lo registra sin fallar. Conservar hashes oficiales/firmas y verificar presencia de la selección; no generar de nuevo el hash de una carga dudosa como si fuera verificación de origen. No se atribuye autenticidad completa a las ISO por sus sidecars.

**7. P2 — Copias parciales terminan con mensaje de completado.** `Backup-UserProfiles.ps1` advierte errores Robocopy >7 en carpetas generales y solo registra los de navegador. El resumen final puede parecer exitoso aunque falten archivos. Propagar estado incompleto y probar restauración; rutas de usuarios fijas en `C:\Users` y carpetas redirigidas/OneDrive quedan fuera del caso simple. La confirmación textual de destino cifrado no verifica cifrado real.

**8. P2 — Windows PowerShell 5.1 y PowerShell 7 no son intercambiables.** `Test-HardwareHealth` usa `Get-WmiObject`; en PowerShell 7 no existe y la consulta RAM no está protegida por try/catch. WMIC sugerido como alternativa puede no estar instalado. Documentar 5.1 para ese script o cambiar a CIM con prueba pequeña; no declarar compatibilidad Linux porque el parser/CI funcione allí.

**9. P2 — Trazabilidad con garantías excesivas y salida sensible.** `Start-ArsenalAudit` describe Start-Transcript como inmutable y garante de cadena de custodia, pero usa un TXT editable con Append. Los informes incluyen usuarios, IP, rutas y datos de procesos; perfiles pueden contener cookies/tokens. Corregir la afirmación, proteger destino y registrar hashes/custodia fuera del equipo investigado. `Query-VirusTotal` etiqueta `undetected` como limpio: debe expresar ausencia de detección, no seguridad.

**10. P2 — Actualizar no prueba la nueva carga.** Build verifica SHA cuando hay valor fijado o digest GitHub y rechaza descargas sin él, lo cual es correcto. Sin embargo `latest` y el primer asset que coincide con `rufus-*.exe` no fijan versión/arquitectura, y Update no actualiza los pins del manifiesto ni realiza pruebas de arranque. Seleccionar exactamente versión/arquitectura, conservar anterior y repetir matriz tras actualización. No se ha medido que las fuentes sigan ofreciendo cada versión histórica.

### Mejora verificada en este candidato

**11. P1 resuelto en fixtures — Exportación con rutas incompatibles.** Antes, los scripts se copiaban a `tools/arsenal_scripts`, calculaban Root como `tools`, y buscaban manifiestos/payloads inexistentes; los playbooks y protocolos superiores no viajaban. Ahora scripts, manifiesto, playbooks y documentos de aceptación quedan en sus rutas de raíz. Solo se copia `SECRETS/PROTOCOLO_BOVEDA.md`, nunca toda la carpeta de secretos. Los consumidores de payloads detectan el layout Ventoy con `ISO/` y mantienen el layout fuente. Build desplegado filtra el perfil de rescate, sin descargar Tails al USB de rescate. Se conservan las guardas de volúmenes y `/E` sin `/MIR`.

La corrección previa de Verify rechaza ausencia de sidecars, hashes incorrectos/formato inválido y referencias fuera del directorio, y admite rutas literales y sidecars válidos. **Estas mejoras no validan una copia física en USB ni crean un dispositivo arrancable.**

## Compatibilidad, portabilidad y procedencia

| Aspecto | Evaluación |
|---|---|
| Offline | ISO y herramientas ya extraídas son utilizables sin descarga según su diseño; actualización, VirusTotal y DISM actual necesitan red. No se ejecutaron |
| Windows y privilegios | Storage/NetTCPIP/DISM/exportación de logs requieren Windows y a menudo administrador; no elevar todo el kit por defecto. Versiones Windows soportadas por cada binario pendientes de validar en objetivos |
| Arquitecturas | La carga seleccionada es principalmente amd64/Win64. Algunos EXE de paquetes tienen otras arquitecturas; no acredita rescate integral en x86 de 32 bits, ARM64 o Apple Silicon |
| Sistema de archivos / espacio | Ubuntu Desktop mide 6,52 GB: no cabe como archivo único en FAT32. El conjunto supera 15 GiB; dimensionar ambos USB por separado, con margen para logs/persistencia. No se midió capacidad, salud ni formato de ningún pendrive |
| BIOS / UEFI / Secure Boot | Todas las filas de la matriz siguen pendientes. Ventoy documenta condiciones de firmware y posible confianza en CA de terceros; Memtest no hereda automáticamente esa compatibilidad. No se cambió firmware ni se enrolaron claves: [Ventoy Secure Boot](https://www.ventoy.net/en/doc_secure.html), [Memtest86+](https://www.memtest.org/) |
| Exportación | Copia archivos a volúmenes montados; no instala cargador, no graba Tails ni comprueba identidad física USB/capacidad. Las guardas rechazan volumen Windows, carpeta, targets iguales y fuente alojada en destino; no prueban que el resto sea un USB |
| Datos del caso | Las carpetas de notas existentes dentro del perfil de rescate pueden copiarse con él; revisar contenido/destino cifrado antes de exportar. Un USB de privacidad no debe recibir datos de rescate por conveniencia |

Las páginas oficiales consultadas muestran versiones posteriores para parte de la selección: Tails 7.16 frente al 7.12 local, SystemRescue 13.02 frente a 13.01, GParted Live 1.8.1-6 frente a -3 y Memtest86+ 9.00 frente a 8.10. Es evidencia de mantenimiento pendiente, **no de una vulnerabilidad concreta ni autorización para actualizar**. Fuentes: [Tails](https://tails.net/install/download/), [SystemRescue](https://www.system-rescue.org/Download/), [GParted](https://gparted.org/), [Memtest86+](https://www.memtest.org/). No se hizo un análisis CVE exhaustivo ni se determinó la última versión de cada programa.

## Licencias y redistribución

Este apartado identifica obligaciones documentales; no autoriza distribuir el kit. En un sistema live hay componentes con licencias distintas: la licencia del programa principal no sustituye a las de toda la imagen.

| Componente / fuente primaria | Licencia o restricción comprobada | Acción antes de redistribuir |
|---|---|---|
| [Ventoy](https://www.ventoy.net/en/doc_license.html) | Código propio GPLv3+; componentes con licencias propias | Conservar avisos y cumplir obligaciones de fuentes por componente |
| [GParted](https://gparted.org/) | Aplicación GPLv2+ | Incluir avisos; revisar además componentes de GParted Live |
| [TestDisk/PhotoRec](https://www.cgsecurity.org/wiki/TestDisk) | TestDisk GPLv2+; paquete portable | Conservar licencia/fuentes aplicables y avisos del paquete |
| [Rescuezilla](https://github.com/rescuezilla/rescuezilla) | Proyecto GPLv3; live con otros paquetes | Revisar licencias de la imagen además del proyecto |
| [Rufus](https://github.com/pbatard/rufus) | GPLv3; sin instalación | Conservar licencia/avisos y condiciones de fuentes |
| [Memtest86+](https://www.memtest.org/) | GPLv2 | Conservar licencia y vía de fuentes correspondiente |
| [KeePassXC](https://github.com/keepassxreboot/keepassxc) | Repositorio con COPYING y varias licencias GPL/LGPL/BSD/MIT y otras | Revisar COPYING y dependencias del ZIP concreto; no reducirlo a una licencia única |
| [ShredOS](https://github.com/PartialVolume/shredos.x86_64) | Sistema construido con múltiples componentes; licencia enlazada por el proyecto | Revisar licencia y avisos de la release concreta; pendiente de cierre por componente |
| [Ubuntu](https://canonical.com/legal/intellectual-property-policy) | Política de Canonical y licencias de cada paquete | Preservar avisos y revisar condiciones de marcas/distribución y componentes |
| [Sysinternals](https://learn.microsoft.com/en-us/sysinternals/license-terms) | EULA permite uso en dispositivos propios y restringe publicación, préstamo y transferencia | Mantener descarga oficial por operador; no publicar el ZIP ni un USB redistribuible con la suite |
| [MSERT](https://learn.microsoft.com/en-us/defender-endpoint/safety-scanner-download) | Software Microsoft; la página de descarga no concede aquí autorización general de redistribución | Conservar términos del paquete, obtener copia oficial reciente; no tratarlo como software libre |
| [Tails](https://tails.net/install/download/) y [SystemRescue](https://www.system-rescue.org/Download/) | Distribuciones con múltiples paquetes | Pendiente inventario de avisos/fuentes de la imagen exacta; no se verificaron todas sus licencias |
| Scripts y documentos propios | No se ha identificado licencia general raíz en el listado revisado | Definir términos propios antes de reutilización pública |

Las fuentes oficiales están identificadas en `tools.json` para las cargas principales; Sysinternals/MSERT se descargan desde Microsoft en su instalador separado. Nueve firmas locales consultadas fueron **Valid**: MSERT y Autoruns64, procexp64, Procmon64, sigcheck64, tcpview64, Disk2vhd64 y sdelete64 firmados por Microsoft; Rufus 4.15 por Akeo Consulting. No se ejecutaron estos archivos. No se validó Authenticode de los otros 158 EXE ni se comparó individualmente cada ISO con una firma/hash oficial independiente.

## Carencias: qué incorporar y qué omitir

| Prioridad / necesidad | Solución mínima, fuente y licencia | Compatibilidad / portabilidad / dependencias / espacio / riesgo |
|---|---|---|
| Imprescindible: restaurar Windows que no arranca | Preparar medio WinRE/instalación de [Microsoft](https://www.microsoft.com/software-download/windows11), mediante el helper existente; licencia Microsoft, sin redistribución presumida | Windows objetivo y arquitectura adecuados, creación inicial con red, uso posterior offline. Tamaño de ISO y drivers por determinar antes de descarga; varios GB previsibles. No instalar ni reparar sin imagen previa y disco de laboratorio |
| Imprescindible: rescatar sin escribir en origen | Probar SystemRescue/ddrescue ya existente y disponer de destino externo cifrado y suficientemente grande | Sin nueva ISO; almacenamiento externo al menos suficiente para imagen y mapfile. Bloqueador físico de escritura cuando se exige preservar evidencia; no se ha inventariado ni adquirido hardware |
| Recomendable: SMART detallado | Reutilizar smartmontools/GSmartControl del live si la versión concreta los incluye; fuentes oficiales enlazadas en SystemRescue/GParted | No requiere paquete Windows adicional inicialmente. Puentes USB/RAID pueden no exponer SMART; probar adaptador real. Sin espacio adicional si se confirma paquete incorporado |
| Recomendable: antimalware útil | Refrescar MSERT y demostrar disponibilidad; usar Defender del sistema o recuperación oficial según caso | No añadir otro antivirus por defecto. MSERT local ocupa 226 MB; fecha/capacidad futura a comprobar. No confiar en resultado desde un SO comprometido |
| Opcional: especialización adicional | Clonezilla solo si Rescuezilla falla en un caso probado; Kali/VeraCrypt u otras suites solo ante necesidad concreta | Sin descarga propuesta ahora. Licencia, versión, espacio y dependencias deberán cerrarse antes de incorporar cualquier paquete; la documentación existente no demuestra instalación |

No hay necesidad demostrada de añadir herramientas para RAM, red, particionado o recuperación básica. Las carencias prioritarias son pruebas, coherencia de versiones, medio Windows, manejo de errores y protección de datos.

## Pruebas, mejoras y límites

| Comprobación | Resultado / alcance |
|---|---|
| Parseo PowerShell de 27 scripts | Sin errores de sintaxis en el candidato; no valida semántica ni disponibilidad de cmdlets |
| JSON de manifiesto/menú e inventario | Leídos sin errores; identificados desfases y alias de versión |
| 16 sidecars de la carga real | Sesión coordinadora: 16/16 coincidentes con el verificador corregido; resultado heredado, sin repetir lectura de 16 GB aquí. No prueba procedencia |
| Firmas Authenticode de nueve EXE | Todas Valid; nombres y sujetos conservados en evidencia privada |
| Regresión del verificador/guardas | Cuatro tests existentes, con casos de hash inválido, archivo ausente, formato/ruta inválidos, sidecars válidos y rechazo de destinos peligrosos |
| Integración de exportación | Fixture temporal con PSDrives de sesión y Robocopy simulado: copia documentos, conserva separación, excluye clave ficticia, Build usa carga sintética existente sin red, extrae ISO sintética, valida layout y verifica sidecars |
| Consistencia de diff | `git diff --check`; no se alteró el repositorio original con payloads |
| CI remoto | No ejecutado ni publicado en esta auditoría; el éxito local no es una comprobación de GitHub Actions |

La suite en PowerShell 7 aprobó **cinco tests en 90,724 segundos** mediante `python -m unittest discover -s tests -p 'test_*.py'`. Una primera repetición había terminado con once expiraciones del límite de 20 segundos al iniciar procesos del runtime. Una repetición adicional de integración también expiró; se descartó el único ajuste posterior a la suite aprobada y se conserva el código que esta verificó. La alternativa Windows PowerShell heredó módulos incompatibles (`Get-FileHash` no disponible) y su fixture de PSDrive también falló; no se modificó la configuración del sistema para corregirlo. Esos fallos del entorno quedan registrados; no se acredita compatibilidad de ejecución completa con Windows PowerShell 5.1.

Para cerrar la aceptación de campo, completar la matriz existente en VM y hardware objetivo: UEFI/Secure Boot y BIOS si se necesita, Tails dedicado, RAM con varias pasadas, discos SATA/NVMe/USB, red y teclado. Después probar copia/restauración y recuperación sobre imágenes sintéticas con resultados verificables. Borrado, sanitización y reparación solo con dispositivos de laboratorio inequívocos y autorización correspondiente; no usar discos de producción para demostrar funcionamiento.

Se omitieron descargas, instalación, cambios de sistema/firmware, escaneo antimalware, acceso a cuentas, envío de notificaciones, commits y publicación. No se comprobó arranque, capacidad/salud del USB físico, cifrado real, restauración, sanitización, todas las licencias transitivas ni todas las vulnerabilidades. **Riesgo pendiente: el kit conserva operaciones modificadoras con resultados insuficientemente verificados; no declararlo listo para campo.**
