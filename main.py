import platform
import socket
import uuid
import shutil
import psutil
import pandas as pd
import dns.resolver
import time
import speedtest
from datetime import datetime

def get_system_info():
    # Report available space on the Windows system drive.
    drive = "C:\\"
    usage = shutil.disk_usage(drive)
    free_gb = usage.free / (1024 ** 3)
    total_gb = usage.total / (1024 ** 3)
    percent_free = usage.free / usage.total * 100
    percent_used = usage.used / usage.total * 100

    # Return a dictionary with system information, including disk usage details.
    return {
        "Hostname": socket.gethostname(),
        "Current Time": datetime.now(),
        "Platform": platform.system(),
        "Platform Version": platform.version(),
        "Disk Capacity": f"{drive} is {percent_used:.1f}% full. " f"{free_gb:.1f} GB free " f"of {total_gb:.1f} GB",
        "CPU Usage": str(psutil.cpu_percent(interval=1)) + "%",
        "Memory Usage": str(psutil.virtual_memory().percent) + "%"
    }

def get_network_interfaces():
    # Get network interface addresses
    net_addrs = psutil.net_if_addrs()

    # Convert the network interface addresses into a structured format for easier reading and analysis
    # Flatten the nested dictionary structure into a list of rows
    rows = []
    for interface, snic_list in net_addrs.items():
        for snic in snic_list:
            rows.append(
                {
                    "Network Interface": str(interface),
                    "Family": str(
                        snic.family.name
                        if hasattr(snic.family, "name")
                        else snic.family
                    ),
                    "Address": str(snic.address or ""),
                    "Netmask": str(snic.netmask or ""),
                    "Broadcast": str(snic.broadcast or ""),
                    "PTP": str(snic.ptp or ""),
                }
            )

    # Convert the list of rows into a DataFrame for further use
    df = pd.DataFrame(rows)

    # Fix formatting for better readability in the console output
    # Calculate the maximum required width for each column (including the header name)
    col_widths = {}
    for col in df.columns:
        max_data_len = df[col].astype(str).map(len).max()
        col_widths[col] = max(max_data_len, len(col))

    # Left-align the header labels
    left_headers = [col.ljust(col_widths[col]) for col in df.columns]

    # Print the header row (separated by two spaces for clear visual breaks)
    print("  ".join(left_headers))

    # Print each row left-aligned to the exact same column widths
    for _, row in df.iterrows():
        aligned_row = [
            str(row[col]).ljust(col_widths[col]) for col in df.columns
        ]
        print("  ".join(aligned_row))


def get_network_info():
    # Retrieve basic network information such as IP address, hostname, and MAC address
    return {
        "IP Address": socket.gethostbyname(socket.gethostname()),
        "Hostname": socket.gethostname(),
        "MAC Address": ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1]),
    }


def get_listening_ports():
    print("\nListening Ports:")
    print(f"{'Protocol':<10} {'Local Address':<25} {'Port':<10} {'PID':<8} {'Status':<10}")
    print("-" * 65)
    
    # Fetch all system network connections
    connections = psutil.net_connections(kind='inet')
    
    for conn in connections:
        # Filter strictly for connections that are in 'LISTEN' state
        if conn.status == psutil.CONN_LISTEN:
            # Determine if TCP or UDP
            protocol = "TCP" if conn.type == 1 else "UDP" 
            local_ip = conn.laddr.ip
            local_port = conn.laddr.port
            pid = conn.pid if conn.pid else "N/A"
            
            print(f"{protocol:<10} {local_ip:<25} {local_port:<10} {pid:<8} {conn.status:<10}")


def get_internet_speed():
    # Performs a live download, upload, and ping test using speedtest.net.
    
    # Initialize an empty list to store the speed test metrics
    metrics = []

    # Attempt to perform the speed test and handle any exceptions gracefully
    try:
        # Initialize the speedtest client and find the optimal test server
        st = speedtest.Speedtest()
        st.get_best_server()
        
        # Measure metrics (convert bytes/sec to Megabits per second)
        download_mbs = round(st.download() / 1_000_000, 2)
        upload_mbs = round(st.upload() / 1_000_000, 2)
        ping_ms = round(st.results.ping, 2)
        
        # Populate results
        metrics.extend([
            {"Metric": "Download Speed", "Value": f"{download_mbs} Mbps", "Status": "Success"},
            {"Metric": "Upload Speed",   "Value": f"{upload_mbs} Mbps",   "Status": "Success"},
            {"Metric": "Network Ping",   "Value": f"{ping_ms} ms",       "Status": "Success"}
        ])
        
    except Exception as e:
        metrics = [
            {"Metric": "Download Speed", "Value": "N/A", "Status": f"Failed: {type(e).__name__}"},
            {"Metric": "Upload Speed",   "Value": "N/A", "Status": f"Failed: {type(e).__name__}"},
            {"Metric": "Network Ping",   "Value": "N/A", "Status": f"Failed: {type(e).__name__}"}
        ]
    
    # Create Pandas DataFrame
    df = pd.DataFrame(metrics)
    
    # Enforce Left-Alignment for Terminal Printing
    pd.set_option('display.colheader_justify', 'left')
    for col in df.columns:
        df[col] = df[col].astype(str).str.ljust(df[col].astype(str).str.len().max())

    # Print the speed test results DataFrame to the terminal
    print(df)


def check_internet_connection(host, port, timeout):
    # Checks if there is a stable internet connection by opening a direct socket connection to a reliable IP address
    print("Testing internet connection to host:", host, "on port:", port)
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        print("Internet connection is stable.")
        return True
    except socket.error:
        print("Internet connection is not stable.")
        return False
    

def test_dns_performance(domain, record_types=["A", "AAAA", "MX", "TXT"], custom_dns=None):
    # Tests various DNS records, measures query speeds, and outputs a pandas DataFrame.
    # Resolver setup for DNS queries
    resolver = dns.resolver.Resolver()
    if custom_dns:
        resolver.nameservers = [custom_dns]

    # Initialize results list to store DNS query outcomes
    results = []
    
    # Query each record type and log metrics
    for r_type in record_types:
        status = "Success"
        resolved_data = []
        
        start_time = time.perf_counter()
        try:
            answers = resolver.resolve(domain, r_type)
            for rdata in answers:
                resolved_data.append(rdata.to_text())
        except dns.resolver.NoAnswer:
            status = "No Answer"
        except dns.resolver.NXDOMAIN:
            status = "Domain Does Not Exist"
        except dns.exception.Timeout:
            status = "Timeout"
        except Exception as e:
            status = f"Error: {type(e).__name__}"
            
        end_time = time.perf_counter()
        
        # Calculate latency in milliseconds
        elapsed_ms = round((end_time - start_time) * 1000, 2)
        
        results.append({
            "Domain": domain,
            "Record Type": r_type,
            "Status": status,
            "Speed (ms)": f"{elapsed_ms} ms" if status == "Success" else "N/A",
            "Resolved Data": ", ".join(resolved_data) if resolved_data else "None"
        })
        
    # Create Pandas DataFrame
    df = pd.DataFrame(results)
    
    # Force Left-Alignment formatting for Terminal printing
    pd.set_option('display.colheader_justify', 'left')
    for col in df.columns:
        df[col] = df[col].astype(str).str.ljust(df[col].astype(str).str.len().max())

    # Print the DNS performance results DataFrame to the terminal
    print(df)


def main():
    # Run diagnostics and print the results.
    print("=" * 80)
    print("IT TROUBLESHOOTING TOOLKIT (Windows)")
    print("by Adam Prinz")
    print(f"Run time: {datetime.now():%Y-%m-%d %H:%M:%S}")
    print("=" * 80)

    print("\nSYSTEM INFORMATION")
    system_info = get_system_info()
    for key, value in system_info.items():
        print(f"{key}: {value}")
    print("\n" + "="*80 + "\n")

    print("\nNETWORK INFORMATION")
    network_info = get_network_info()
    for key, value in network_info.items():
        print(f"{key}: {value}")
    get_network_interfaces()
    get_listening_ports()
    print("\n" + "="*80 + "\n")

    print("\nINTERNET CONNECTIVITY")
    check_internet_connection(host="8.8.8.8", port=53, timeout=3)
    get_internet_speed()
    print("\n")

    # Test using your system default DNS
    print("Testing with System Default DNS...")
    test_dns_performance("google.com")
    print("\n")
    
    # Test using Cloudflare's DNS (1.1.1.1)
    print("Testing with Cloudflare DNS (1.1.1.1)...")
    test_dns_performance("microsoft.com", custom_dns="1.1.1.1")
    print("\n" + "="*80 + "\n")

    # Print a final separator before completing diagnostics
    print("\nDiagnostics complete.\n")


if __name__ == "__main__":
    main()