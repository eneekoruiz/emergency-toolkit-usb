# Emergency Toolkit USB

PowerShell scripts and configuration to provision and verify bootable and portable USB rescue drives for system recovery and privacy.

## Tech Stack

- **Scripting:** PowerShell 5.1 / 7+
- **Platform:** Windows PE, WinRE, portable Windows utilities

## Key Decisions

- **Automated Provisioning:** Formats and partitions USB drives with designated partition labels, file systems (FAT32 for UEFI boot, NTFS for large archives), and portable directory layouts.
- **Integrity Verification:** Hashes (SHA-256) all copied diagnostics and repair tools against a known baseline before drive deployment.
- **Air-Gapped Operation:** All provisioned utilities and scripts run standalone without internet access.

## Usage

### Prerequisites

- Windows 10/11 with PowerShell running as Administrator
- USB flash drive (minimum 16 GB recommended)

### Running Provisioning

```powershell
# Open elevated PowerShell prompt
cd Arsenal_Digital

# Review available scripts
Get-ChildItem -Filter *.ps1

# Execute USB preparation workflow
.\prepare-rescue-usb.ps1 -DriveLetter E:
```
