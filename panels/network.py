import gi
import json
import logging
import netifaces
import os
import re

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib, Pango
from ks_includes.screen_panel import ScreenPanel

def create_panel(*args):
    return NetworkPanel(*args)

class NetworkPanel(ScreenPanel):
    networks = {}
    network_list = []

    def initialize(self, menu):
        _ = self.lang.gettext
        self.show_add = False

        grid = self._gtk.HomogeneousGrid()
        grid.set_hexpand(True)

        # Get Hostname
        stream = os.popen('hostname -A')
        hostname = stream.read()
        # Get IP Address
        gws = netifaces.gateways()
        if "default" in gws and netifaces.AF_INET in gws["default"]:
            self.interface = gws["default"][netifaces.AF_INET][1]
        else:
            ints = netifaces.interfaces()
            if 'lo' in ints:
                ints.pop(ints.index('lo'))
            if (len(ints) > 0):
                self.interface = ints[0]
            else:
                self.interface = 'lo'

        res = netifaces.ifaddresses(self.interface)
        if netifaces.AF_INET in res and len(res[netifaces.AF_INET]) > 0:
            ip = res[netifaces.AF_INET][0]['addr']
        else:
            ip = "0.0.0.0"

        self.labels['networks'] = {}

        self.labels['interface'] = Gtk.Label()
        self.labels['interface'].set_text(" %s: %s" % (_("Interface"), self.interface))
        self.labels['disconnect'] = self._gtk.Button(_("Disconnect"), "color2")

        self.labels['ip'] = Gtk.Label()#flsun add,add ip refresh function 7.28 2022
        self.labels['ip'].set_hexpand(True)#flsun add
        reload_networks = self._gtk.ButtonImage("refresh", None, "color1")#flsun add
        reload_networks.connect("clicked", self.reload_networks)#flsun add
        reload_networks.set_hexpand(False)#flsun add

        sbox = Gtk.Box()
        sbox.set_hexpand(True)
        sbox.set_vexpand(False)
        sbox.add(self.labels['interface'])
        # sbox.add(self.labels['disconnect'])

        if ip is not None: #flsun add，add ip refresh function 7.28 2022
            self.labels['ip'].set_text("IP: %s  " % ip)#flsun add
            sbox.add(self.labels['ip'])#flsun add
        sbox.add(reload_networks)#flsun add

        scroll = Gtk.ScrolledWindow()
        scroll.set_property("overlay-scrolling", False)
        scroll.set_vexpand(True)
        scroll.add_events(Gdk.EventMask.TOUCH_MASK)
        scroll.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box.set_vexpand(True)

        self.labels['networklist'] = Gtk.Grid()
        self.files = {}

        if self._screen.wifi is not None and self._screen.wifi.is_initialized():
            box.pack_start(sbox, False, False, 0)
            box.pack_start(scroll, True, True, 0)

            GLib.idle_add(self.load_networks)
            scroll.add(self.labels['networklist'])

            self._screen.wifi.add_callback("connected", self.connected_callback)
            self._screen.wifi.add_callback("scan_results", self.scan_callback)
            self.timeout = GLib.timeout_add_seconds(5, self.update_all_networks)
        else:
            self.labels['networkinfo'] = Gtk.Label("")
            self.labels['networkinfo'].get_style_context().add_class('temperature_entry')
            box.pack_start(self.labels['networkinfo'], False, False, 0)
            self.update_single_network_info()
            self.timeout = GLib.timeout_add_seconds(5, self.update_single_network_info)

        self.content.add(box)
        self.labels['main_box'] = box

    def load_networks(self):
        networks = self._screen.wifi.get_networks()

        conn_ssid = self._screen.wifi.get_connected_ssid()
        if conn_ssid in networks:
            networks.remove(conn_ssid)
        self.add_network(conn_ssid, False)

        for net in networks:
            self.add_network(net, False)

        self.update_all_networks()
        self.content.show_all()

    def add_network(self, ssid, show=True):
        _ = self.lang.gettext

        if ssid is None:
            return
        ssid = ssid.strip()

        if ssid in list(self.networks):
            logging.info("SSID already listed")
            return

        netinfo = self._screen.wifi.get_network_info(ssid)
        if netinfo is None:
            logging.debug("Couldn't get netinfo")
            return

        configured_networks = self._screen.wifi.get_supplicant_networks()
        network_id = -1
        for net in list(configured_networks):
            if configured_networks[net]['ssid'] == ssid:
                network_id = net

        frame = Gtk.Frame()
        frame.set_property("shadow-type", Gtk.ShadowType.NONE)
        frame.get_style_context().add_class("frame-item")


        name = Gtk.Label()
        name.set_markup("<big><b>%s</b></big>" % (ssid))
        name.set_hexpand(True)
        name.set_halign(Gtk.Align.START)
        name.set_line_wrap(True)
        name.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)

        info = Gtk.Label()
        info.set_halign(Gtk.Align.START)
        # info.set_markup(self.get_file_info_str(ssid))
        labels = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        labels.add(name)
        labels.add(info)
        labels.set_vexpand(True)
        labels.set_valign(Gtk.Align.CENTER)
        labels.set_halign(Gtk.Align.START)

        connect = self._gtk.ButtonImage("load", None, "color3")
        connect.connect("clicked", self.connect_network, ssid)
        connect.set_hexpand(False)
        connect.set_halign(Gtk.Align.END)

        delete = self._gtk.ButtonImage("delete", "", "color3")
        delete.connect("clicked", self.remove_wifi_network, ssid)
        delete.set_size_request(60, 0)
        delete.set_hexpand(False)
        delete.set_halign(Gtk.Align.END)

        network = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        network.set_hexpand(True)
        network.set_vexpand(False)

        network.add(labels)

        buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        if network_id != -1 or netinfo['connected']:
            buttons.pack_end(delete, False, False, 0)
        connected_ssid = self._screen.wifi.get_connected_ssid()
        if ssid != connected_ssid or not netinfo['connected']:
            buttons.pack_end(connect, False, False, 0)

        network.add(buttons)

        self.networks[ssid] = frame
        frame.add(network)

        nets = sorted(list(self.networks), reverse=False)
        if connected_ssid == ssid:
            pos = 0
        elif nets.index(ssid) is not None:
            pos = nets.index(ssid) + 1
        else:
            logging.info("Error: SSID not in nets")
            return

        self.labels['networks'][ssid] = {
            "connect": connect,
            "delete": delete,
            "info": info,
            "name": name,
            "row": network
        }

        self.labels['networklist'].insert_row(pos)
        self.labels['networklist'].attach(self.networks[ssid], 0, pos, 1, 1)
        if show:
            self.labels['networklist'].show()

    def add_new_network(self, widget, ssid, connect=False):
        self._screen.remove_keyboard()
        networks = self._screen.wifi.get_networks()
        psk = self.labels['network_psk'].get_text()
        result = self._screen.wifi.add_network(ssid, psk)

        self.close_add_network()

        if connect:
            if result:
                self.connect_network(widget, ssid, False)
            else:
                self._screen.show_popup_message("Error adding network %s" % ssid)

    def back(self):
        if self.show_add:
            self.close_add_network()
            return True
        return False

    def check_missing_networks(self):
        networks = self._screen.wifi.get_networks()
        for net in list(self.networks):
            if net in networks:
                networks.remove(net)

        for net in networks:
            self.add_network(net, False)
        self.labels['networklist'].show_all()

    def close_add_network(self):
        if not self.show_add:
            return

        for child in self.content.get_children():
            self.content.remove(child)
        self.content.add(self.labels['main_box'])
        self.content.show()
        for i in ['add_network', 'network_psk']:
            if i in self.labels:
                del self.labels[i]
        self.show_add = False

    def close_dialog(self, widget, response_id):
        widget.destroy()

    def connected_callback(self, ssid, prev_ssid):
        logging.info("Now connected to a new network")
        if ssid is not None:
            self.remove_network(ssid)
        if prev_ssid is not None:
            self.remove_network(prev_ssid)

        self.check_missing_networks()

    def connect_network(self, widget, ssid, showadd=True):
        _ = self.lang.gettext

        snets = self._screen.wifi.get_supplicant_networks()
        isdef = False
        for id, net in snets.items():
            if net['ssid'] == ssid:
                isdef = True
                break

        if not isdef:
            if showadd:
                self.show_add_network(widget, ssid)
            return
        self.prev_network = self._screen.wifi.get_connected_ssid()

        buttons = [
            {"name": _("Close"), "response": Gtk.ResponseType.CANCEL}
        ]

        scroll = Gtk.ScrolledWindow()
        scroll.set_property("overlay-scrolling", False)
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)
        scroll.add_events(Gdk.EventMask.TOUCH_MASK)
        scroll.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.labels['connecting_info'] = Gtk.Label(_("Starting WiFi Re-association"))
        self.labels['connecting_info'].set_halign(Gtk.Align.START)
        self.labels['connecting_info'].set_valign(Gtk.Align.START)
        scroll.add(self.labels['connecting_info'])
        dialog = self._gtk.Dialog(self._screen, buttons, scroll, self.close_dialog)
        self._screen.show_all()

        if ssid in self.networks:
            self.remove_network(ssid)
        if self.prev_network in self.networks:
            self.remove_network(self.prev_network)
            # GLib.timeout_add(500, self.add_network, self.prev_network)

        self._screen.wifi.add_callback("connecting_status", self.connecting_status_callback)
        self._screen.wifi.connect(ssid)

    def connecting_status_callback(self, msg):
        self.labels['connecting_info'].set_text(self.labels['connecting_info'].get_text() + "\n" + msg)
        self.labels['connecting_info'].show_all()

    def remove_network(self, ssid, show=True):
        if ssid not in self.networks:
            return

        for i, network in enumerate(self.labels['networklist']):
            if self.networks[ssid] == self.labels['networklist'].get_child_at(0, i):
                self.labels['networklist'].remove_row(i)
                self.labels['networklist'].show()
                del self.networks[ssid]
                del self.labels['networks'][ssid]
                return

    def remove_wifi_network(self, widget, ssid):
        self._screen.wifi.delete_network(ssid)
        self.remove_network(ssid)
        self.check_missing_networks()

    def scan_callback(self, new_networks, old_networks):
        for net in old_networks:
            self.remove_network(net, False)
        for net in new_networks:
            self.add_network(net, False)
        self.content.show_all()

    def show_add_network(self, widget, ssid):
        if self.show_add:
            return

        _ = self.lang.gettext
        for child in self.content.get_children():
            self.content.remove(child)

        if "add_network" in self.labels:
            del self.labels['add_network']

        self.labels['add_network'] = Gtk.VBox()
        self.labels['add_network'].set_valign(Gtk.Align.START)

        box = Gtk.Box(spacing=5)
        box.set_size_request(self._gtk.get_content_width(), self._gtk.get_content_height() -
                             self._screen.keyboard_height - 20)
        box.set_hexpand(True)
        box.set_vexpand(False)
        self.labels['add_network'].add(box)

        label = self._gtk.Label("%s %s:" % (_("PSK for"), ssid))
        label.set_hexpand(False)
        entry = Gtk.Entry()
        entry.set_hexpand(True)

        save = self._gtk.ButtonImage("sd", _("Save"), "color3")
        save.set_hexpand(False)
        save.connect("clicked", self.add_new_network, ssid, True)


        self.labels['network_psk'] = entry
        box.pack_start(label, False, False, 5)
        box.pack_start(entry, True, True, 5)
        box.pack_start(save, False, False, 5)

        self.show_create = True
        self.labels['network_psk'].set_text('')
        self.content.add(self.labels['add_network'])
        self.labels['network_psk'].connect("focus-in-event", self._show_keyboard)#flsun add for wifi keyboard
        self.labels['network_psk'].connect("button-press-event", self._show_keyboard)#flsun add for wifi keyboard
        self._screen.show_keyboard(entry=self.labels['network_psk']) #flsun modify for wifi keyboard 
        self.labels['network_psk'].grab_focus_without_selecting()
        self.content.show_all()
        self.show_add = True

    def _show_keyboard(self, widget=None, event=None): #flsun add for wifi keyboard
        self._screen.show_keyboard(entry=self.labels['network_psk'])

    def update_all_networks(self):
        for network in list(self.networks):
            self.update_network_info(network)
        return True

    def update_network_info(self, ssid):
        _ = self.lang.gettext

        if ssid not in self.networks or ssid not in self.labels['networks']:
            return
        netinfo = self._screen.wifi.get_network_info(ssid)
        if netinfo is None:
            return

        connected = ""
        if netinfo['connected']:
            stream = os.popen('hostname -f')
            hostname = stream.read().strip()
            ifadd = netifaces.ifaddresses(self.interface)
            ipv4 = ""
            ipv6 = ""
            if netifaces.AF_INET in ifadd and len(ifadd[netifaces.AF_INET]) > 0:
                ipv4 = "<b>%s:</b> %s " % (_("IPv4"), ifadd[netifaces.AF_INET][0]['addr'])
            if netifaces.AF_INET6 in ifadd and len(ifadd[netifaces.AF_INET6]) > 0:
                ipv6 = ipv6 = "<b>%s:</b> %s " % (_("IPv6"), ifadd[netifaces.AF_INET6][0]['addr'].split('%')[0])
            connected = "<b>%s</b>\n<b>%s:</b> %s\n%s\n%s\n" % (_("Connected"), _("Hostname"), hostname, ipv4, ipv6)  #flsun modify,split ipv4 and ipv6
        elif "psk" in netinfo:
            connected = "Password saved."
        freq = "2.4 GHz" if netinfo['frequency'][0:1] == "2" else "5 Ghz"

        self.labels['networks'][ssid]['info'].set_markup("%s%s <small>%s %s %s  %s%s</small>" % (
            connected, "" if netinfo['encryption'] == "off" else netinfo['encryption'].upper(),
            freq, _("Channel"), netinfo['channel'], netinfo['signal_level_dBm'], _("dBm")
        ))
        self.labels['networks'][ssid]['info'].show_all()

    def update_single_network_info(self):
        _ = self.lang.gettext

        stream = os.popen('hostname -f')
        hostname = stream.read().strip()
        ifadd = netifaces.ifaddresses(self.interface)
        ipv4 = ""
        ipv6 = ""
        if netifaces.AF_INET in ifadd and len(ifadd[netifaces.AF_INET]) > 0:
            ipv4 = "<b>%s:</b> %s " % (_("IPv4"), ifadd[netifaces.AF_INET][0]['addr'])
        if netifaces.AF_INET6 in ifadd and len(ifadd[netifaces.AF_INET6]) > 0:
            ipv6 = ipv6 = "<b>%s:</b> %s " % (_("IPv6"), ifadd[netifaces.AF_INET6][0]['addr'].split('%')[0])
        connected = "<b>%s</b>\n\n<small><b>%s</b></small>\n<b>%s:</b> %s\n%s\n%s\n" % (
            self.interface, _("Connected"), _("Hostname"), hostname, ipv4, ipv6)

        self.labels['networkinfo'].set_markup(connected)
        self.labels['networkinfo'].show_all()

    def reload_networks(self, widget=None): #flsun add，add ip refresh function 7.28 2022
        self.networks = {}
        #os.system("sudo dhclient -r && sudo dhclient")
        self.labels['networklist'].remove_column(0)
        self._screen.wifi.rescan()#flsun add,_screen.wifi
        res = netifaces.ifaddresses(self.interface)#flsun add ,refresh ip while refresh wifi
        if netifaces.AF_INET in res and len(res[netifaces.AF_INET]) > 0:
            ip = res[netifaces.AF_INET][0]['addr']
        else:
            ip = "0.0.0.0"
        if ip is not None: #flsun add，add ip refresh function 7.28 2022
            self.labels['ip'].set_text("IP: %s  " % ip)#flsun add
        if self._screen.wifi is not None and self._screen.wifi.is_initialized():
            GLib.idle_add(self.load_networks)