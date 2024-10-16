# 🕵️‍♂️ **EtherSnoop** – The Ultimate Network Detective! 🔍

![EtherSnoop Logo](https://dummyimage.com/600x200/000/fff&text=EtherSnoop)

Welcome to **EtherSnoop** – the only detective you'll ever need to monitor where your office ports are connected like a hawk (or maybe a really tech-savvy owl 🦉). Say goodbye to network mysteries and hello to **real-time Ethernet snooping**!

## 🚀 What is EtherSnoop?
EtherSnoop is a small but mighty device that captures, parses, and displays Cisco Discovery Protocol (CDP) packets over Ethernet. You know those mysterious network switches? Now, you can see exactly what they're up to!

💡 **Built on the W55RP20-EVB-PICO** (WIZnet Ethernet + Raspberry Pi RP2040-based board), EtherSnoop monitors Ethernet connections in real-time, providing live CDP data like:
- 📡 **Switch Name** (because who doesn’t want to name-drop their network switch at parties?)
- 🔌 **Port Number** (Fa0/1, Gi0/2 – you name it, we parse it)
- 🎛️ **VLAN ID** (Yes, even your VLANs have secrets, and EtherSnoop knows them!)
- 📜 **IOS Version** (Straight from the switch firmware, like `12.2(55)EX3`)

Oh, and did we mention it’s all displayed beautifully on an OLED screen? It’s like having a tiny window into the network world 🌍.

## 😎 Why Use EtherSnoop?
Whether you’re a network admin, an ethical hacker (🕶️), or just someone who wants to know where things are patched in and get the basic config on that port, **EtherSnoop is your gadget**. Forget expensive packet sniffers – this one’s cute, portable, and packs the perfect amount of nerdiness.

Here’s what EtherSnoop can do:
- Detect when **Ethernet cables are plugged in or unplugged** (because cables seem to disappear like magic).
- Dynamically **request an IP via DHCP** and flaunt that IP on its OLED screen like it's the coolest thing ever.
- **Capture and display CDP data** – see info like "Office Switch1" on port "Fa0/5" with VLAN ID "10." (You could even put that on a t-shirt.)
- **Display the Cisco IOS version** to know exactly what software your switch is running.
- Uses **custom fonts** because, why not? Roboto Light never looked so good on an OLED screen.

## ⚙️ How It Works
1. **Plug in an Ethernet cable.** EtherSnoop will request an IP via DHCP.
2. **Sit back, relax**, and let EtherSnoop capture the CDP packets.
3. **Watch the magic** on the OLED screen as EtherSnoop parses and shows you detailed info about your network switch, port, VLAN, and IOS version. (Remember, Cisco switches by default only send CDP packets every 60 seconds!)
4. **Unplug the Ethernet cable** to make it sad – just kidding, it'll patiently wait for reconnection, request a new IP, and start snooping again. It never quits. Ever. 😎

## 🛠️ Getting Started
Ready to snoop? Let’s get you up and running in no time!

### Hardware Requirements
- **W55RP20-EVB-PICO Board** (Ethernet + RP2040 board)
- **SSD1306 OLED Screen** (128x64 pixels)
- **An Ethernet cable** (obviously!)
- **Power source**: Currently USB-powered, but you can go wireless with a battery!

### OLED Pin Connections
To hook up your OLED display (SSD1306), connect the following pins:
- **SDA (I2C Data)** to Pin **2**
- **SCL (I2C Clock)** to Pin **3**
- **VCC** to **3.3V** or **5V**
- **GND** to **Ground**

### Software Requirements
- **MicroPython** installed on your W55RP20-EVB-PICO.
- The following libraries:
  - `ssd1306.py` (OLED library) from [RandomNerdTutorials](https://randomnerdtutorials.com/raspberry-pi-pico-ssd1306-oled-micropython/), though we’ve modded it to work with `fdrawer`.
  - `fdrawer.py` for drawing fonts from the awesome [freetype-generator](https://github.com/mchobby/freetype-generator).
  - **Custom font files**: `robotl_m10.py` and its corresponding `.bin` file (Roboto Light, medium size).

### Installation
1. **Clone this repo** (you know the drill):
   ```bash
   git clone https://github.com/YourGitHub/EtherSnoop.git
   cd EtherSnoop
   ```

2. **Flash MicroPython** onto your W55RP20-EVB-PICO:
   Use the `firmware.uf2` provided in the `firmware` folder. This is a special adaptation of the **WIZnet-ioNIC-micropython** firmware, with some tweaks for our needs (because, frankly, they left out some essential features). Flash it like you mean it!

3. **Upload all the files**:
   Copy everything from root (via Thonny, rshell, or whatever you like). Your device is now ready to snoop!

4. **Plug in your Ethernet cable**, connect power, and watch EtherSnoop do its thing! ⚡

### 🧰 Folder Structure
```
EtherSnoop/
│
├── main.py           # The brains of the operation
├── ssd1306.py        # Manages the OLED display (modded for FontDrawer)
├── fdrawer.py        # Custom font drawer library
├── robotl_m10.py     # Larger font for OLED
├── robotl_m10.bin    # Binary data for larger font
└── firmware/         # Contains the custom MicroPython firmware
    └── firmware.uf2
```

## 🏆 Features
- **Real-time CDP Packet Parsing**: Get live details about the switch, port, VLAN, and **IOS version** – directly from your network traffic.
- **Cable Detection**: Instantly detects cable disconnection and reconnection like a pro.
- **IP Address via DHCP**: Watch your device request and show off its IP address every time it reconnects.
- **OLED Display**: Small but mighty, with custom fonts for that extra bit of flair.

## 🚀 Future Plans
- 🔋 **Battery Integration**: Soon, EtherSnoop will be untethered and completely portable!
- 📦 **Case Design**: It’s time to give this gadget a proper home – a 3D-printed case is coming.

## 🐛 Bugs & Issues
Got bugs? We hope not, but if you do (or you’re bored and want to chat), head over to the [issues section](https://github.com/YourGitHub/EtherSnoop/issues) and let us know. EtherSnoop doesn’t like being bugged. 😉

## 💡 Contributing
We love contributions like a network loves packets! Feel free to submit pull requests, open issues, or even just star the repo – EtherSnoop will thank you. 🎉

## ⚠️ Disclaimer
**EtherSnoop is not responsible for any network drama it uncovers. Use it ethically, and remember – with great power comes great responsibility.** 🕸️

---

Thanks for checking out EtherSnoop! We hope it makes your network monitoring fun, informative, and maybe just a little bit sassy. 😎

Happy Snoopin’! 🕵️‍♂️🎉

P.S. – Shoutout to ChatGPT for helping write most of this, because, let’s face it, I'm more into coding than writing whimsical README files!
