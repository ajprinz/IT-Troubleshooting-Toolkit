# Windows IT Troubleshooting Toolkit

A command-line toolkit that gathers basic Windows system and network diagnostics. This project is intended as a learning project and a demonstration of entry-level IT troubleshooting and Python skills.

## Features

- Reports the computer name, Windows version, system-drive capacity, CPU usage, and memory usage.
- Displays network interface addresses and basic host network information.
- Lists listening network ports and associated process IDs when the operating system makes that information available.
- Checks TCP connectivity to `8.8.8.8` on port `53`.
- Measures internet download speed, upload speed, and latency using `speedtest-cli`.
- Queries DNS records using the system's configured resolver and, for one test, Cloudflare DNS (`1.1.1.1`).

## Requirements

- Windows
- Python 3.9 or later
- Internet access for connectivity, speed, and DNS tests

Python packages are listed in [`requirements.txt`](requirements.txt).

## Setup

Open PowerShell in the project folder and run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks virtual-environment activation, you can install dependencies without activating it:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run

With the virtual environment activated:

```powershell
python main.py
```

Or without activating it:

```powershell
.\.venv\Scripts\python.exe main.py
```

The speed test and DNS queries require network access and may take some time. Results are printed to the terminal; the program does not save a report file.

## Privacy and permissions

The output can include the computer name, MAC address, local network addresses, listening ports, and process IDs. Avoid sharing unredacted output publicly.

The toolkit performs DNS lookups and network tests, including a speed test with an external service. Some process or connection details may not be available unless the terminal is run with elevated permissions. The script currently targets the Windows `C:\` system drive.

## Skills demonstrated

- Python standard-library modules for platform, socket, and disk information
- Third-party package usage with `psutil`, `pandas`, `dnspython`, and `speedtest-cli`
- Basic network connectivity and DNS troubleshooting
- Collecting and presenting diagnostic information in the terminal

## Current limitations

- This is a read-only diagnostic script; it does not attempt to change system or network settings.
- It is designed for Windows and assumes the system drive is `C:\`.
- Some system calls can depend on local permissions and network configuration.
- The speed test depends on the external speed-test service and a working internet connection.
