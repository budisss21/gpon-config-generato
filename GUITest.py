from typing import Dict, Optional
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import ttkbootstrap as ttk
from datetime import date
import re
import pyperclip

class OLTConfigGenerator:
    def __init__(self):

        self.root = ttk.Window(themename="darkly")
        self.root.title("OLT Configuration Generator")
        self.root.geometry("1920x1080")
        
        # Constants
        self.SERVICES = {
            '2801': '10', '2802': '10', '2828': '20', '2887': '5',
            '2888': '20', '2889': '50', '2890': '100', '1601': '10',
            '1602': '20', '1603': '30', '1604': '50', '1605': '100',
            '2820': '10', '2830': '20', '2819': '50'
        }
        
        self.VLAN_RANGE = [str(i) for i in range(2900, 3000)] + list(self.SERVICES.keys())
        
        # Variables
        self.registration_type = tk.StringVar(value="new")
        self.connection_type = tk.StringVar(value="pppoe")
        self.olt_brand = tk.StringVar(value="raisecom")
        self.use_today_password = tk.BooleanVar(value=True)
        self.use_nce = tk.BooleanVar(value=False)
        
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the main GUI layout"""
        # Create main container
        main_container = ttk.Frame(self.root, padding=20)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel for inputs
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Right panel for output
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        self.create_input_panel(left_panel)
        self.create_output_panel(right_panel)
        
    def create_input_panel(self, parent):
        """Create the input form panel"""
        # Title
        title_label = ttk.Label(
            parent,
            text="OLT Configuration Generator",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Registration Type
        reg_frame = ttk.LabelFrame(parent, text="Registration Type", padding=10)
        reg_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Radiobutton(
            reg_frame,
            text="New Registration",
            variable=self.registration_type,
            value="new"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            reg_frame,
            text="Replace/Re-register",
            variable=self.registration_type,
            value="replace"
        ).pack(side=tk.LEFT, padx=5)
        
        # Connection Type
        conn_frame = ttk.LabelFrame(parent, text="Connection Type", padding=10)
        conn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Radiobutton(
            conn_frame,
            text="PPPoE",
            variable=self.connection_type,
            value="pppoe",
            command=self.toggle_password_fields
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            conn_frame,
            text="IPoE",
            variable=self.connection_type,
            value="ipoe",
            command=self.toggle_password_fields
        ).pack(side=tk.LEFT, padx=5)
        
        # OLT Brand
        brand_frame = ttk.LabelFrame(parent, text="OLT Brand", padding=10)
        brand_frame.pack(fill=tk.X, pady=(0, 10))
        
        brands = [
            ("Raisecom", "raisecom"),
            ("ZTE C610", "zte_c610"),
            ("ZTE C320", "zte_c320"),
            ("BDCOM", "bdcom"),
            ("Huawei", "huawei")
        ]
        
        for text, value in brands:
            ttk.Radiobutton(
                brand_frame,
                text=text,
                variable=self.olt_brand,
                value=value,
                command=self.update_fsp_format
            ).pack(side=tk.LEFT, padx=5)
        
        # Device Information
        device_frame = ttk.LabelFrame(parent, text="Device Information", padding=10)
        device_frame.pack(fill=tk.X, pady=(0, 10))
        
        # SN Entry
        ttk.Label(device_frame, text="Serial Number:").pack(fill=tk.X)
        self.sn_entry = ttk.Entry(device_frame)
        self.sn_entry.pack(fill=tk.X, pady=(0, 10))
        
        # FSP Entry
        ttk.Label(device_frame, text="FSP:").pack(fill=tk.X)
        self.fsp_label = ttk.Label(device_frame, text="Format: F/S/P/Onu id")
        self.fsp_label.pack(fill=tk.X)
        self.fsp_entry = ttk.Entry(device_frame)
        self.fsp_entry.pack(fill=tk.X, pady=(0, 10))
        
        # VLAN Entry
        ttk.Label(device_frame, text="VLAN:").pack(fill=tk.X)
        self.vlan_entry = ttk.Entry(device_frame)
        self.vlan_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Customer Information
        customer_frame = ttk.LabelFrame(parent, text="Customer Information", padding=10)
        customer_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(customer_frame, text="SID:").pack(fill=tk.X)
        self.sid_entry = ttk.Entry(customer_frame)
        self.sid_entry.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(customer_frame, text="Customer Name:").pack(fill=tk.X)
        self.name_entry = ttk.Entry(customer_frame)
        self.name_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Password Frame
        self.password_frame = ttk.LabelFrame(parent, text="PPPoE Password", padding=10)
        self.password_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Checkbutton(
            self.password_frame,
            text="Use Today's Date",
            variable=self.use_today_password,
            command=self.toggle_password_entry
        ).pack(fill=tk.X)
        
        self.password_entry = ttk.Entry(self.password_frame, state="disabled")
        self.password_entry.pack(fill=tk.X, pady=(5, 0))
        
        # NCE Option for Huawei
        self.nce_frame = ttk.LabelFrame(parent, text="NCE Option", padding=10)
        self.nce_frame.pack(fill=tk.X, pady=(0, 10))
        self.nce_frame.pack_forget()
        
        ttk.Checkbutton(
            self.nce_frame,
            text="Use NCE",
            variable=self.use_nce
        ).pack(fill=tk.X)
        
        # Generate Button
        ttk.Button(
            parent,
            text="Generate Configuration",
            command=self.generate_config,
            style="Accent.TButton"
        ).pack(fill=tk.X, pady=10)
        
    def create_output_panel(self, parent):
        """Create the output display panel"""
        # Output area
        output_frame = ttk.LabelFrame(parent, text="Generated Configuration", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            width=50,
            height=30,
            font=("Courier", 10)
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Copy button
        ttk.Button(
            parent,
            text="Copy to Clipboard",
            command=self.copy_to_clipboard,
            style="Accent.TButton"
        ).pack(fill=tk.X, pady=(10, 0))
        
    def update_fsp_format(self):
        """Update FSP format hint based on selected brand"""
        formats = {
            "raisecom": "Format: S/P/Onu id",
            "zte_c610": "Format: F/S/P/Onu id",
            "zte_c320": "Format: F/S/P/Onu id",
            "bdcom": "Format: P/Onu id",
            "huawei": "Format: F/S/P/Onu id"
        }
        
        self.fsp_label.config(text=formats.get(self.olt_brand.get(), "Format: F/S/P/Onu id"))
        
        # Show/hide NCE frame for Huawei
        if self.olt_brand.get() == "huawei":
            self.nce_frame.pack(fill=tk.X, pady=(0, 10))
        else:
            self.nce_frame.pack_forget()
            
    def toggle_password_fields(self):
        """Show/hide password fields based on connection type"""
        if self.connection_type.get() == "pppoe":
            self.password_frame.pack(fill=tk.X, pady=(0, 10))
        else:
            self.password_frame.pack_forget()
            
    def toggle_password_entry(self):
        """Enable/disable password entry based on use_today_password"""
        if self.use_today_password.get():
            self.password_entry.config(state="disabled")
        else:
            self.password_entry.config(state="normal")
            
    def validate_inputs(self) -> bool:
        """Validate all input fields"""
        if not self.sn_entry.get() or len(self.sn_entry.get()) not in [12, 16]:
            messagebox.showerror("Error", "Invalid Serial Number")
            return False
            
        if not self.fsp_entry.get():
            messagebox.showerror("Error", "FSP is required")
            return False
            
        if not self.vlan_entry.get() or self.vlan_entry.get() not in self.VLAN_RANGE:
            messagebox.showerror("Error", "Invalid VLAN")
            return False
            
        if not self.sid_entry.get() or not self.sid_entry.get().isdigit():
            messagebox.showerror("Error", "Invalid SID")
            return False
            
        if not self.name_entry.get():
            messagebox.showerror("Error", "Customer Name is required")
            return False
            
        return True
        
    def generate_config(self):
        """Generate OLT configuration based on inputs"""
        if not self.validate_inputs():
            return
            
        try:
            # Get values from inputs
            config = self.create_config_string()
            
            # Display configuration
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, config)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate configuration: {str(e)}")
            
    def create_config_string(self) -> str:
        """Create the configuration string based on selected options"""
        # Get all input values
        sn = self.sn_entry.get()
        fsp = self.fsp_entry.get()
        vlan = self.vlan_entry.get()
        sid = self.sid_entry.get()
        name = self.name_entry.get().replace(' ', '.')
        
        # Get configuration parameters
        is_replacement = self.registration_type.get() == "replace"
        is_pppoe = self.connection_type.get() == "pppoe"
        brand = self.olt_brand.get()
        
        # Get password for PPPoE
        password = ""
        if is_pppoe:
            if self.use_today_password.get():
                password = date.today().strftime('%Y%m%d')
            else:
                password = self.password_entry.get()
        
        # Generate configuration based on brand
        config_generators = {
            "raisecom": self.generate_raisecom_config,
            "zte_c610": self.generate_c610_config,
            "zte_c320": self.generate_c320_config,
            "bdcom": self.generate_bdcom_config,
            "huawei": self.generate_huawei_config
        }
        
        return config_generators[brand](
            sn=sn,
            fsp=fsp,
            vlan=vlan,
            sid=sid,
            name=name,
            password=password,
            is_replacement=is_replacement,
            is_pppoe=is_pppoe
        )
    
    def generate_raisecom_config(self, **kwargs) -> str:
        """Generate Raisecom configuration"""
        sn = kwargs['sn']
        fsp = kwargs['fsp']
        vlan = kwargs['vlan']
        sid = kwargs['sid']
        name = kwargs['name']
        password = kwargs.get('password', '')
        is_replacement = kwargs['is_replacement']
        is_pppoe = kwargs['is_pppoe']
        
        split_fsp = re.split(r'\D', fsp)
        config = []
        
        # First part
        config.append("config")
        config.append(f"interface gpon-olt {split_fsp[0]}/{split_fsp[1]}")
        
        if is_replacement:
            config.append(f"no create gpon-onu {split_fsp[2]}")
            
        config.append(f"create gpon-onu {split_fsp[2]} sn {sn} line-profile-id 1 service-profile-id 1")
        config.append("quit")
        config.append(f"interface gpon-onu {fsp}")
        config.append(f"description {sid}-{name}")
        config.append("quit")
        
        # Second part for Raisecom ONUs
        if sn.lower().startswith('rcm'):
            config.append(f"gpon-onu {fsp}")
            config.append(f"iphost 1 mode {'pppoe' if is_pppoe else 'dhcp'}")
            
            if is_pppoe:
                config.append(f"iphost 1 pppoe username {sn} password {password}")
                
            config.append(f"iphost 1 vlan {vlan}")
            config.append("iphost 1 service Internet")
            config.append("iphost 1 service mode route nat enable cos 0 portlist 1,2 ssidlist 1")
            config.append("end")
            
        return '\n'.join(config)
    
    def generate_c610_config(self, **kwargs) -> str:
        """Generate ZTE C610 configuration"""
        sn = kwargs['sn']
        fsp = kwargs['fsp']
        vlan = kwargs['vlan']
        sid = kwargs['sid']
        name = kwargs['name']
        password = kwargs.get('password', '')
        is_replacement = kwargs['is_replacement']
        is_pppoe = kwargs['is_pppoe']
        
        split_fsp = re.split(r'\D', fsp)
        config = []
        
        # First part
        config.append("config t")
        config.append(f"interface gpon_olt-{split_fsp[0]}/{split_fsp[1]}/{split_fsp[2]}")
        
        if is_replacement:
            config.append(f"no onu {split_fsp[3]}")
            
        config.append(f"onu {split_fsp[3]} type ZTEG-F609 sn {sn}")
        config.append("exit")
        
        # Second part
        config.append(f"interface gpon_onu-{split_fsp[0]}/{split_fsp[1]}/{split_fsp[2]}:{split_fsp[3]}")
        config.append(f"description {sid}-{name}")
        config.append(f"tcont 1 name HSI profile {'PPPOE' if is_pppoe else self.SERVICES[vlan]+'Mbps'}")
        config.append("gemport 1 name HSI tcont 1")
        config.append("exit")
        config.append(f"interface vport-{split_fsp[0]}/{split_fsp[1]}/{split_fsp[2]}.{split_fsp[3]}:1")
        config.append(f"service-port 1 user-vlan {vlan} vlan {vlan}")
        config.append("exit")
        
        # Third part
        config.append(f"pon-onu-mng gpon_onu-{split_fsp[0]}/{split_fsp[1]}/{split_fsp[2]}:{split_fsp[3]}")
        config.append(f"service HSI gemport 1 vlan {vlan}")
        
        if sn.lower().startswith('zte'):
            if is_pppoe:
                config.append(f"wan-ip ipv4 mode pppoe username {sn} password {password} vlan-profile vlan{vlan} host 1")
                config.append(f"wan-ip ipv4 mode pppoe username {sn} password {password} vlan-profile wan{vlan} host 1")
            else:
                config.append(f"wan-ip ipv4 mode dhcp vlan-profile vlan{vlan} host 1")
                
        config.extend([
            f"vlan port eth_0/1 mode tag vlan {vlan}",
            f"vlan port eth_0/2 mode tag vlan {vlan}",
            "dhcp-ip ethuni eth_0/1 from-onu",
            "dhcp-ip ethuni eth_0/2 from-onu",
            "end"
        ])
        
        return '\n'.join(config)
    
    def generate_c320_config(self, **kwargs) -> str:
        """Generate ZTE C320 configuration"""
        sn = kwargs['sn']
        fsp = kwargs['fsp']
        vlan = kwargs['vlan']
        sid = kwargs['sid']
        name = kwargs['name']
        password = kwargs.get('password', '')
        is_replacement = kwargs['is_replacement']
        is_pppoe = kwargs['is_pppoe']
        
        split_fsp = re.split(r'\D', fsp)
        config = []
        
        # First part
        config.append("config t")
        config.append(f"interface gpon-olt_{split_fsp[0]}/{split_fsp[1]}/{split_fsp[2]}")
        
        if is_replacement:
            config.append(f"no onu {split_fsp[3]}")
            
        config.append(f"onu {split_fsp[3]} type ZTEG-F609 sn {sn}")
        config.append("exit")
        
        # Second part
        config.append(f"interface gpon-onu_{split_fsp[0]}/{split_fsp[1]}/{split_fsp[2]}:{split_fsp[3]}")
        config.append(f"description {sid}-{name}")
        config.append("sn-bind enable sn")
        config.append(f"tcont 1 name HSI profile {'PPPOE' if is_pppoe else self.SERVICES[vlan]+'Mbps'}")
        config.append("gemport 1 name HSI tcont 1")
        config.append(f"service-port 1 vport 1 user-vlan {vlan} vlan {vlan}")
        config.append("exit")
        
        # Third part
        if sn.lower().startswith('zte'):
            config.append(f"pon-onu-mng gpon-onu_{split_fsp[0]}/{split_fsp[1]}/{split_fsp[2]}:{split_fsp[3]}")
            config.append(f"service HSI gemport 1 vlan {vlan}")
            
            if is_pppoe:
                config.append(f"wan-ip 1 mode pppoe username {sn} password {password} vlan-profile vlan{vlan} host 1")
            else:
                config.append(f"wan-ip 1 mode dhcp vlan-profile vlan{vlan} host 1")
                config.append(f"wan-ip 1 mode dhcp vlan-profile wan{vlan} host 1")
                
            config.extend([
                f"vlan port eth_0/1 mode tag vlan {vlan}",
                "dhcp-ip ethuni eth_0/1 from-onu",
                "end"
            ])
        else:
            config.extend([
                f"pon-onu-mng gpon-onu_{split_fsp[0]}/{split_fsp[1]}/{split_fsp[2]}:{split_fsp[3]}",
                f"service HSI gemport 1 vlan {vlan}",
                f"vlan port eth_0/1 mode tag vlan {vlan}",
                "dhcp-ip ethuni eth_0/1 from-onu",
                "end"
            ])
            
        return '\n'.join(config)
    
    def generate_bdcom_config(self, **kwargs) -> str:
        """Generate BDCOM configuration"""
        sn = kwargs['sn']
        fsp = kwargs['fsp']
        vlan = kwargs['vlan']
        sid = kwargs['sid']
        name = kwargs['name']
        password = kwargs.get('password', '')
        is_pppoe = kwargs['is_pppoe']
        
        split_fsp = re.split(r'\D', fsp)
        config = ["config"]
        
        config.append(f"interface gpoN 0/{split_fsp[0]}:{split_fsp[1]}")
        config.append(f"description {sid}-{name}")
        
        if sn.lower().startswith('5a54'):
            config.append("gpon onu flow-mapping-profile ZTE")
            
        config.extend([
            "gpon onu wan 1 admin-status enable",
            "gpon onu wan 1 nat enable",
            "gpon onu wan 1 service-type internet",
            "gpon onu wan 1 connection-type pppoe"
        ])
        
        if is_pppoe:
            config.append(f"gpon onu wan 1 pppoe username {sn} password {password}")
            
        config.extend([
            f"gpon onu wan 1 tci vlan {vlan}",
            "gpon onu wan 1 bind lan1 lan2 ssid1",
            "gpon onu wan 1 auto-get-dns-address enable",
            "gpon onu wan 1 lan-dhcp enable",
            "quit",
            "write all"
        ])
        
        return '\n'.join(config)
    
    def generate_huawei_config(self, **kwargs) -> str:
        """Generate Huawei configuration"""
        sn = kwargs['sn']
        fsp = kwargs['fsp']
        vlan = kwargs['vlan']
        sid = kwargs['sid']
        name = kwargs['name']
        password = kwargs.get('password', '')
        is_replacement = kwargs['is_replacement']
        is_pppoe = kwargs['is_pppoe']
        use_nce = self.use_nce.get()
        
        split_fsp = re.split(r'\D', fsp)
        config = ["config"]
        
        # First part - replacement logic
        if is_replacement:
            config.extend([
                f"undo service-port {self.serviceport_entry.get()}",
                f"interface gpon {split_fsp[0]}/{split_fsp[1]}",
                f"ont delete {split_fsp[2]} {split_fsp[3]}"
            ])
        else:
            config.append(f"interface gpon {split_fsp[0]}/{split_fsp[1]}")
        
        # Second part - PPPoE configuration
        if is_pppoe:
            if use_nce:
                config.extend([
                    f"ont add {split_fsp[2]} {split_fsp[3]} sn-auth {sn} omci "
                    f"ont-lineprofile-name ICONNET.PPPOE.{vlan} "
                    f"ont-srvprofile-name ICONNET.PPPOE.{vlan} desc {sid}-{name}",
                    "",
                    f"ont ipconfig {split_fsp[2]} {split_fsp[3]} pppoe vlan {vlan} "
                    f"priority 0 user-account username {sn} password {password}",
                    "",
                    f"ont port route {split_fsp[2]} {split_fsp[3]} eth 1 enable",
                    "",
                    f"ont port route {split_fsp[2]} {split_fsp[3]} eth 2 enable",
                    "",
                    "quit",
                    "",
                    f"service-port vlan {vlan} gpon {split_fsp[0]}/{split_fsp[1]}/{split_fsp[2]} "
                    f"ont {split_fsp[3]} gemport 1 multi-service user-vlan {vlan} tag-transform translate",
                    "",
                    "quit"
                ])
            else:
                config.extend([
                    f"ont add {split_fsp[2]} {split_fsp[3]} sn-auth {sn} omci "
                    f"ont-lineprofile-name ICONNET.PPPOE.{vlan} "
                    f"ont-srvprofile-name ICONNET.PPPOE.{vlan} desc {sid}-{name}",
                    "",
                    f"ont ipconfig {split_fsp[2]} {split_fsp[3]} pppoe vlan {vlan} "
                    f"priority 0 user-account username {sn} password {password}",
                    "",
                    f"ont internet-config {split_fsp[2]} {split_fsp[3]} ip-index 0",
                    "",
                    f"ont wan-config {split_fsp[2]} {split_fsp[3]} ip-index 0 profile-name ICONNET.AUTOPROV",
                    "",
                    f"ont policy-route-config {split_fsp[2]} {split_fsp[3]} profile-name ICONNET.AUTOPROV",
                    "",
                    f"ont port route {split_fsp[2]} {split_fsp[3]} eth 1 enable",
                    "",
                    f"ont port route {split_fsp[2]} {split_fsp[3]} eth 2 enable",
                    "",
                    "quit",
                    "",
                    f"service-port vlan {vlan} gpon {split_fsp[0]}/{split_fsp[1]}/{split_fsp[2]} "
                    f"ont {split_fsp[3]} gemport 1 multi-service user-vlan {vlan} tag-transform translate",
                    "",
                    "quit"
                ])
        
        # Third part - IPoE configuration
        else:
            if vlan in ['2828', '2820', '2830', '2819']:
                config.extend([
                    f"ont add {split_fsp[2]} {split_fsp[3]} sn-auth {sn} omci "
                    f"ont-lineprofile-name AUTOPROV.{self.SERVICES[vlan]}-{vlan} "
                    f"ont-srvprofile-name AUTOPROV.{self.SERVICES[vlan]}-{vlan} desc {sid}-{name}",
                    "",
                    f"ont ipconfig {split_fsp[2]} {split_fsp[3]} dhcp vlan {vlan} priority 0",
                    "",
                    f"ont internet-config {split_fsp[2]} {split_fsp[3]} ip-index 0",
                    "",
                    f"ont wan-config {split_fsp[2]} {split_fsp[3]} ip-index 0 profile-name ICONNET.AUTOPROV",
                    "",
                    f"ont policy-route-config {split_fsp[2]} {split_fsp[3]} profile-name ICONNET.AUTOPROV",
                    "",
                    f"ont port route {split_fsp[2]} {split_fsp[3]} eth 1 enable",
                    "",
                    f"ont port route {split_fsp[2]} {split_fsp[3]} eth 2 enable",
                    "",
                    "quit",
                    "",
                    f"service-port vlan {vlan} gpon {split_fsp[0]}/{split_fsp[1]}/{split_fsp[2]} "
                    f"ont {split_fsp[3]} gemport 1 multi-service user-vlan {vlan} tag-transform translate",
                    "",
                    "quit"
                ])
            else:
                config.extend([
                    f"ont add {split_fsp[2]} {split_fsp[3]} sn-auth {sn} omci "
                    f"ont-lineprofile-name AUTOPROV.{self.SERVICES[vlan]} "
                    f"ont-srvprofile-name AUTOPROV.{self.SERVICES[vlan]} desc {sid}-{name}",
                    "",
                    f"ont ipconfig {split_fsp[2]} {split_fsp[3]} dhcp vlan {vlan} priority 0",
                    "",
                    f"ont internet-config {split_fsp[2]} {split_fsp[3]} ip-index 0",
                    "",
                    f"ont wan-config {split_fsp[2]} {split_fsp[3]} ip-index 0 profile-name ICONNET.AUTOPROV",
                    "",
                    f"ont policy-route-config {split_fsp[2]} {split_fsp[3]} profile-name ICONNET.AUTOPROV",
                    "",
                    f"ont port route {split_fsp[2]} {split_fsp[3]} eth 1 enable",
                    "",
                    f"ont port route {split_fsp[2]} {split_fsp[3]} eth 2 enable",
                    "",
                    "quit",
                    "",
                    f"service-port vlan {vlan} gpon {split_fsp[0]}/{split_fsp[1]}/{split_fsp[2]} "
                    f"ont {split_fsp[3]} gemport 1 multi-service user-vlan {vlan} tag-transform translate",
                    "",
                    "quit"
                ])
        
        return '\n'.join(config)

    def validate_serviceport(self) -> bool:
        """Validate serviceport for Huawei OLT"""
        if self.olt_brand.get() == "huawei" and self.registration_type.get() == "replace":
            if not hasattr(self, 'serviceport_entry'):
                self.serviceport_entry = ttk.Entry(self.device_frame)
                ttk.Label(self.device_frame, text="Serviceport:").pack(fill=tk.X)
                self.serviceport_entry.pack(fill=tk.X, pady=(0, 10))
            
            if not self.serviceport_entry.get() or not self.serviceport_entry.get().isdigit():
                messagebox.showerror("Error", "Invalid Serviceport")
                return False
        return True

    def validate_inputs(self) -> bool:
        """Validate all input fields"""
        # Basic validation
        if not self.sn_entry.get() or len(self.sn_entry.get()) not in [12, 16]:
            messagebox.showerror("Error", "Invalid Serial Number")
            return False
        
        # FSP validation
        fsp_patterns = {
            "raisecom": r'^\d/\d+/\d+$',
            "zte_c610": r'^\d/\d/\d+/\d+$',
            "zte_c320": r'^\d/\d/\d+/\d+$',
            "bdcom": r'^\d+/\d+$',
            "huawei": r'^\d/\d/\d+/\d+$'
        }
        
        if not re.match(fsp_patterns[self.olt_brand.get()], self.fsp_entry.get()):
            messagebox.showerror("Error", "Invalid FSP format")
            return False
        
        # VLAN validation
        if not self.vlan_entry.get() or self.vlan_entry.get() not in self.VLAN_RANGE:
            messagebox.showerror("Error", "Invalid VLAN")
            return False
        
        # Customer information validation
        if not self.sid_entry.get() or not self.sid_entry.get().isdigit():
            messagebox.showerror("Error", "Invalid SID")
            return False
        
        if not self.name_entry.get():
            messagebox.showerror("Error", "Customer Name is required")
            return False
        
        # PPPoE password validation
        if (self.connection_type.get() == "pppoe" and 
            not self.use_today_password.get() and 
            not self.password_entry.get()):
            messagebox.showerror("Error", "PPPoE password is required")
            return False
        
        # Huawei-specific validation
        if not self.validate_serviceport():
            return False
        
        return True

    def update_dynamic_fields(self, *args):
        """Update dynamic fields based on OLT brand and registration type"""
        brand = self.olt_brand.get()
        is_replacement = self.registration_type.get() == "replace"
        is_pppoe = self.connection_type.get() == "pppoe"
        
        # Update FSP format hint
        self.update_fsp_format()
        
        # Show/hide password fields
        if is_pppoe:
            self.password_frame.pack(fill=tk.X, pady=(0, 10))
        else:
            self.password_frame.pack_forget()
        
        # Show/hide NCE option for Huawei
        if brand == "huawei":
            self.nce_frame.pack(fill=tk.X, pady=(0, 10))
        else:
            self.nce_frame.pack_forget()
        
        # Show/hide serviceport for Huawei replacement
        if brand == "huawei" and is_replacement:
            if not hasattr(self, 'serviceport_entry'):
                self.serviceport_entry = ttk.Entry(self.device_frame)
                ttk.Label(self.device_frame, text="Serviceport:").pack(fill=tk.X)
                self.serviceport_entry.pack(fill=tk.X, pady=(0, 10))
        elif hasattr(self, 'serviceport_entry'):
            self.serviceport_entry.pack_forget()

    # Add trace to variables to update dynamic fields
    def add_traces(self):
        """Add traces to variables to update dynamic fields"""
        self.olt_brand.trace_add('write', self.update_dynamic_fields)
        self.registration_type.trace_add('write', self.update_dynamic_fields)
        self.connection_type.trace_add('write', self.update_dynamic_fields)
            
            
    def copy_to_clipboard(self):
        """Copy generated configuration to clipboard"""
        config = self.output_text.get(1.0, tk.END).strip()
        if config:
            pyperclip.copy(config)
            messagebox.showinfo("Success", "Configuration copied to clipboard!")
        else:
            messagebox.showwarning("Warning", "No configuration to copy!")

def main():
    app = OLTConfigGenerator()
    app.root.mainloop()

if __name__ == "__main__":
    main()