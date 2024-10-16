import gc  # Import garbage collection for memory management
from machine import Pin, WIZNET_PIO_SPI, SoftI2C
import network
import lwip
import time
import struct
import ssd1306
import re
from fdrawer import FontDrawer
import robotl_m8
import robotl_m10


# Initialize I2C for OLED screen
i2c = SoftI2C(scl=Pin(3), sda=Pin(2))
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

fd = FontDrawer(frame_buffer=oled, font_name='robotl_m10')


def w5x00_init():
    """
    Initialize the WIZnet5K network interface.
    Set up hostname, enable promiscuous mode, and activate the NIC.
    """
    spi = WIZNET_PIO_SPI(baudrate=31_250_000, mosi=Pin(23), miso=Pin(22), sck=Pin(21))  # W55RP20 PIO_SPI
    nic = network.WIZNET5K(spi, Pin(20), Pin(25))  # SPI, CS, reset pin
    nic.active(True)

    hostname = "EtherSnoop"
    print(f"FQN Hostname: {hostname}")
    oled.fill(0)
    fd.print_str(hostname, 0, 0)
    oled.show()

    lwip.set_hostname(hostname)

    # Enable MACRAW mode for capturing all packets
    try:
        nic.enable_macraw(0)
        print('Promiscuous mode enabled')
    except AttributeError:
        print('MACRAW mode not supported in this driver')

    print('NIC init complete')
    return nic


def check_link_status(nic):
    """
    Check if the Ethernet cable is connected.
    Returns True if connected, False if disconnected.
    """
    return nic.status() != 0


def request_dhcp(nic):
    """
    Request an IP address via DHCP.
    Displays progress on the OLED screen.
    Returns a tuple (True, IP address) on success or (False, None) on failure.
    """
    print('Requesting IP via DHCP...')
    oled.fill(0)
    fd.print_str('Requesting IP...', 0, 0)
    oled.show()
    
    timeout = 120  # 2 minutes timeout for DHCP
    start_time = time.ticks_ms()

    while True:
        elapsed = time.ticks_diff(time.ticks_ms(), start_time) / 1000
        if elapsed > timeout:
            print("DHCP request timed out")
            return False, None
        
        try:
            nic.ifconfig('dhcp')  # Request a new IP from DHCP
            if nic.isconnected():
                ip_config = nic.ifconfig()
                ip_address = ip_config[0]
                print(f"Obtained IP: {ip_config[0]}")
                oled.fill(0)
                fd.print_str(f"IP: {ip_address}", 0, 0)
                oled.show()
                return True, ip_address
        except OSError:
            oled.fill(0)
            fd.print_str('Waiting for DHCP...', 0, 0)
            oled.show()
        time.sleep(1)


def clear_dhcp_state(nic):
    """
    Clear the NIC's DHCP state to ensure a fresh IP address request is made.
    This fully resets the NIC's IP configuration, including clearing any IP address.
    """
    print("Clearing DHCP state and IP configuration.")
    try:
        nic.ifconfig(('0.0.0.0', '0.0.0.0', '0.0.0.0', '0.0.0.0'))  # Reset to default "empty" config
        print("DHCP state cleared.")
    except OSError as e:
        print(f"Error clearing DHCP state: {e}")


def shorten_port_name(port_name):
    """
    Shorten the port name from FastEthernet, GigabitEthernet, and TenGigabitEthernet
    to Fa, Gi, and Te respectively for easier display on the OLED.
    """
    if port_name.startswith('FastEthernet'):
        return port_name.replace('FastEthernet', 'Fa')
    elif port_name.startswith('GigabitEthernet'):
        return port_name.replace('GigabitEthernet', 'Gi')
    elif port_name.startswith('TenGigabitEthernet'):
        return port_name.replace('TenGigabitEthernet', 'Te')
    return port_name  # Return the original if no match



def parse_cdp_packet(packet, ip_address):
    """
    Parse a CDP packet and extract switch, port, VLAN, and IOS version information.
    Display the information on the OLED screen along with the IP address.
    """
    cdp_data = packet[14:]  # CDP starts after 14 bytes of Ethernet frame
    switch = port = vlan_id = ios_version = "N/A"

    pos = 0
    while pos < len(cdp_data):
        if pos + 4 > len(cdp_data):
            break

        tlv_type = int.from_bytes(cdp_data[pos:pos + 2], "big")
        tlv_length = int.from_bytes(cdp_data[pos + 2:pos + 4], "big")

        if pos + tlv_length > len(cdp_data):
            pos += 4
            continue

        tlv_value = cdp_data[pos + 4:pos + tlv_length]
        
        # Check for Device-ID (Switch)
        if tlv_type == 0x01:
            switch = tlv_value.decode('utf-8')

        # Check for Port-ID (Port)
        elif tlv_type == 0x03:
            port = tlv_value.decode('utf-8')
            port = shorten_port_name(port)  # Shorten the port name for display

        # Check for Native VLAN (VLAN ID)
        elif tlv_type == 0x0A:
            vlan_id = int.from_bytes(tlv_value, "big")

        # Check for Version String (Extract IOS version number only)
        elif tlv_type == 0x05:
            full_ios_version = tlv_value.decode('utf-8')  # Decode the full IOS version string
            # Extract just the version number (e.g., "12.2(55)EX3")
            version_match = re.search(r"Version ([\d.]+\([^)]+\)\w*)", full_ios_version)
            if version_match:
                ios_version = version_match.group(1)  # Extract only the version part

        pos += tlv_length

    print(f"Switch: {switch}, Port: {port}, VLAN: {vlan_id}, IOS Version: {ios_version}")
    
    # Display CDP information along with the IP address on the OLED
    oled.fill(0)
    fd.print_str(f'SW:{switch}', 0, 0)
    fd.print_str(f'Port:{port}', 0, 10)
    fd.print_str(f'VLAN:{vlan_id}', 0, 20)
    fd.print_str(f'IOS:{ios_version}', 0, 30)  # Add the extracted IOS version number to the display
    fd.print_str(f'IP:{ip_address}', 0, 40)
    oled.show()

def is_cdp_packet(packet):
    """
    Check if the packet is a CDP packet.
    Returns True if it is, otherwise False.
    """
    return packet[:6] == b'\x01\x00\x0c\xcc\xcc\xcc'


def capture_packets(nic, ip_address, cdp_processed):
    """
    Capture packets and process only the first valid CDP packet.
    Once a CDP packet is captured and parsed, no more packets will be processed
    until the Ethernet cable is unplugged and re-plugged.
    """
    print("Listening for CDP packets...")
    oled.fill(0)
    fd.print_str('Waiting for CDP', 0, 10)
    oled.show()

    last_packet_data = None  # Store the first CDP packet

    while True:
        # Check if the Ethernet cable is still connected
        if not check_link_status(nic):
            print("Ethernet cable unplugged. Stopping packet capture.")
            oled.fill(0)
            fd.print_str('Please Connect', 0, 0)
            fd.print_str('Ethernet...', 0, 10)
            oled.show()

            # Clear previous CDP data and IP address
            last_packet_data = None
            ip_address = None
            cdp_processed = False  # Reset CDP processing state

            # Clear the OLED screen
            oled.fill(0)
            fd.print_str('No IP Address', 0, 0)
            oled.show()
            return cdp_processed  # Exit packet capture and indicate reset

        if cdp_processed:  # If a CDP packet has already been processed, ignore further packets
            print("CDP packet already processed, ignoring further packets.")
            time.sleep(1)  # Wait a second to avoid overloading the loop
            continue

        try:
            # Receive packet from NIC
            packet = nic.recv_ethernet()

            # Process only the first CDP packet
            if packet and is_cdp_packet(packet):
                if not last_packet_data:  # Process only the first CDP packet
                    last_packet_data = packet
                    parse_cdp_packet(packet, ip_address)  # Display CDP data
                    print("CDP packet processed, no further packets will be captured.")
                    cdp_processed = True  # Mark CDP as processed
                    return cdp_processed  # Exit after processing the first CDP packet

            else:
                continue  # Drop non-CDP packets
        except OSError as e:
            print(f"Error receiving packet: {e}")
            continue  # Handle errors gracefully

        # Run garbage collection to free memory
        gc.collect()


def wait_for_reconnection(nic):
    """
    Wait for the Ethernet cable to be reconnected.
    Once reconnected, the system will restart DHCP and resume packet capture.
    """
    while not check_link_status(nic):
        print("Cable is disconnected. Waiting for reconnection...")
        oled.fill(0)
        fd.print_str('Please Connect', 0, 0)
        fd.print_str('Ethernet...', 0, 10)
        oled.show()
        time.sleep(1)  # Check connection every second

    print("Ethernet cable reconnected. Restarting DHCP...")
    return request_dhcp(nic)


def main():
    """Main loop controlling the Ethernet monitoring and packet capture flow."""
    nic = w5x00_init()
    cdp_processed = False  # To track whether a CDP packet has been processed

    while True:
        # Check if Ethernet cable is connected
        if not check_link_status(nic):
            print("Ethernet not connected. Waiting for reconnection...")
            oled.fill(0)
            fd.print_str('Please Connect', 0, 0)
            fd.print_str('Ethernet...', 0, 10)
            oled.show()
            clear_dhcp_state(nic)  # Clear DHCP details on disconnection
            wait_for_reconnection(nic)
            cdp_processed = False  # Reset CDP processed state after reconnection
            continue  # Wait for reconnection before proceeding

        # Request IP via DHCP after connection
        if not cdp_processed:  # Ensure DHCP is only requested if CDP hasn't been processed
            success, ip_address = request_dhcp(nic)
            if success:
                print(f"IP obtained: {ip_address}, starting packet capture.")
                cdp_processed = capture_packets(nic, ip_address, cdp_processed)  # Capture CDP packets after DHCP
            else:
                print("DHCP failed. Waiting for reconnection...")
                wait_for_reconnection(nic)
        else:
            print("CDP packet already processed. No further actions until cable disconnects.")
            time.sleep(1)  # Wait and check again


if __name__ == "__main__":
    main()

