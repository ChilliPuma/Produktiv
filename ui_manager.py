import json
from collections import deque

import pygame

from game import game
from loader import saves_dir
from data.ui_components import UI, Text, unify
from data.visual_design import COLORS, FONTS, color_map
from world_config import format_time, format_time_short


class UIManager:
    menu_history = []
    click_history = deque(maxlen=70)

    game_loaded = False

    input_state = False
    input_text = ""
    input_ui = None

    viewed_facility = 0
    facility_inv_scroll = 0

    viewed_item_history = []
    item_cont_scroll = 0

    viewed_comm = ""
    cmms_scroll = 0
    conv_scroll = 0
    conv_txt_scroll = 0
    scroll={
        "facilities_inventory": 0,
        "item_contents": 0,
        "comms": 0,
        "convo": 0,
        "convo_text": 0,
    }

    def ui_lookup(self, ui_name: str) -> UI | None:
        for ui in UI.elements:
            if ui.name == ui_name:
                return ui
        return None

    def ui_update(self, ui_name: str, **kwargs):
        ui = self.ui_lookup(ui_name)
        if ui is None:
            return

        for key, value in kwargs.items():
            if hasattr(ui, key):
                setattr(ui, key, value)
        ui.old = True

    def tick(self, dt):
        if game.world and not game.world.time_stop:
            time_bar = self.ui_lookup("time_bar")
            time_bar.text[0].text, time_bar.old = format_time(game.world.time), True

            if self.menu_history[-1].startswith("comms"):
                for comm in game.world.comms.values():
                    if comm.new_message:
                        comm.new_message = False
                        self.comms_display()
                        break
            elif self.menu_history[-1].startswith("convo"):
                for comm in game.world.comms.values():
                    if comm.new_message:
                        comm.new_message = False
                        self.convo_display()
                        break

    def draw(self, surface):
        for ui in sorted(UI.elements, key=lambda e: e.layer):
            if not ui.visible:
                continue
            if ui.old:
                ui.renew()
            surface.blit(ui.surf, ui.pos)

    def click(self, pos):
        for ui in sorted(UI.elements, key=lambda e: e.layer, reverse=True):
            if not ui.visible:
                continue
            elif ui.function or ui.name.endswith("input_box"):
                x, y = ui.pos
                w, h = ui.size
                if x <= pos[0] <= x + w and y <= pos[1] <= y + h:
                    self.click_history.append(ui.name)
                    if ui.name.endswith("input_box"):
                        self.input_state = True
                        self.input_ui = ui
                        self.input_text = ""
                        pygame.key.start_text_input()
                        break

                    elif self.input_state:
                        self.input_ui = None
                        self.input_state = False
                        pygame.key.stop_text_input()

                    ui.function()
                    print(f"[ui] clicked {ui.name}")
                    break

    def menu_refresh(self):
        for ui in UI.elements:
            if ui.layer == 33:
                continue
            if ui.name.startswith(self.menu_history[-1]):
                ui.visible = True
                ui.old = True
            elif ui.visible:
                ui.visible = False
                ui.old = True

    def perma_ui_color_switch(self, color: str):
        self.ui_update("permanent_borders", border=COLORS[f"{color}_border"])
        self.ui_update("back_button", fill=COLORS[f"{color}_lo"])
        self.ui_update("save_button", fill=COLORS[f"{color}_lo"])

    def menu_switch(self, menu_name: str):
        if menu_name == "start":
            self.menu_history.clear()
            if game.world:
                game.world.time_stop = True
        elif menu_name == "saves":
            pass
        elif menu_name == "new_save":
            pass
        elif menu_name == "main":
            pass
        elif menu_name == "facilities":
            self.facility_inv_scroll = 0
            self.facilities_display()
        elif menu_name == "item":
            self.item_display()
        elif menu_name == "comms":
            self.comms_display()
        elif menu_name == "convo":
            self.convo_display()

        self.menu_history.append(menu_name)
        print(f"[ui] menu -> {menu_name}")
        self.perma_ui_color_switch(menu_name)
        self.menu_refresh()

    def menu_back(self):
        if len(self.menu_history) <= 1:
            return

        if self.menu_history[-1] == "item":
            if len(self.viewed_item_history) > 1:
                self.viewed_item_history.pop()
                self.item_display()
                return
            elif len(self.viewed_item_history) == 1:
                self.viewed_item_history.pop()

        self.menu_history.pop()
        previous_menu = self.menu_history.pop()
        print(f"[ui] back -> {previous_menu}")
        self.menu_switch(previous_menu)

    def follow_pointer(self, pointer):
        if pointer is None:
            return

        if hasattr(pointer, "oid"):
            print(f"[ui] pointer item -> {pointer.oid}")
            self.view_item(pointer)
        elif hasattr(pointer, "cid"):
            print(f"[ui] pointer comm -> {pointer.cid}")
            self.view_comm(pointer)

    def menu_scroll(self, menu:str, scroll:int):
        self.scroll[menu]=(self.scroll[menu]+scroll)
        print(f"[ui] item contents scroll -> {menu}: {scroll}")
        if menu=="facilities":
            self.facilities_display()
        elif menu=="item":
            self.item_display()
        elif menu=="comms":
            self.comms_display()
        elif menu=="convo":
            self.convo_display()

    def new_save_button(self, save_file_name: str):
        print(f"[ui] new save requested: {save_file_name or '[auto]'}")
        self.menu_switch("saves")

    def game_load(self):
        if not self.game_loaded:
            self.ui_lookup("start_continue").text[0].color = COLORS["white"]
            self.ui_update("start_continue", fill=COLORS["yellow_mid"])

        self.game_loaded = True
        game.world.time_stop = False
        self.ui_lookup("time_bar").text[0].text = format_time(game.world.time)
        print(f"[ui] game loaded at {format_time(game.world.time)}")
        self.menu_switch("main")
        self.ui_update("time_bar", visible=True)

    def new_game(self):
        print("[ui] new game")
        game.new_game()
        self.game_load()

    def continue_game(self):
        if self.game_loaded:
            print("[ui] continue game")
            self.game_load()

    def fill_grid_menu(
            self,
            menu: str,
            content: list[dict],
            mapping: dict[tuple[str, int], str]
    ):
        gcs=0
        for ui in UI.elements:
            if ui.name.startswith(f"{menu}_grid_cell"):
                gcs+=1

        view_start=self.scroll[menu]*gcs
        view_end=view_start+gcs

        ui_up = self.ui_lookup(menu + "_up")
        ui_down = self.ui_lookup(menu + "_down")
        if len(content) > view_end:
            ui_down.fill=COLORS[f"{color_map[menu]}_mid"]
            ui_down.text[0].color=COLORS[f"{color_map[menu]}_hi"]
            ui_down.function=lambda: self.menu_scroll(menu, 1)
        else:
            ui_down.fill=COLORS[f"{color_map[menu]}_dead"]
            ui_down.text[0].color=COLORS["black"]
            ui_down.function=None
        if self.scroll[menu]!=0:
            ui_up.fill = COLORS[f"{color_map[menu]}_mid"]
            ui_up.text[0].color = COLORS[f"{color_map[menu]}_hi"]
            ui_up.function=lambda: self.menu_scroll(menu, -1)
        else:
            ui_up.fill = COLORS[f"{color_map[menu]}_dead"]
            ui_up.text[0].color = COLORS["black"]
            ui_up.function=None

        viewed_content = content[view_start:view_end]
        for i in range(gcs):
            ui = self.ui_lookup(f"{menu}_grid_cell_{i + 1}")

            for target, content_key in mapping.items():
                if len(viewed_content)<=i:
                    if target[0]=="text":
                        ui.text[target[1]]=""
                        ui.fill=COLORS["transparent"]
                    elif target[0]=="image":
                        ui_image=self.ui_lookup(f"{menu}_grid_cell_image_{i + 1}")
                        ui_image.image[target[1]].png = ""
                        ui_image.fill=COLORS["transparent"]
                    elif target[0]=="function":
                        ui.function=None
                        ui.pointer=None
                    continue

                entry=viewed_content[i]
                if target[0]=="text":
                    ui.text[target[1]]=entry[content_key]
                    ui.fill=COLORS[f"{color_map[menu]}_lo"]
                elif target[0]=="image":
                    ui_image=self.ui_lookup(f"{menu}_grid_cell_image_{i + 1}")
                    ui_image.image[target[1]].png=entry[content_key]
                    ui_image.fill=COLORS[f"{color_map[menu]}_dead"]
                if "function" not in entry:
                    ui.function=None
                    continue
                if "pointer" not in entry:
                    raise ValueError(f"Function defined without pointer for {ui.name}")
                function, pointer=entry["function"], entry["pointer"]
                ui.pointer=pointer
                ui.function=lambda f=function, p=pointer: f(p)

    def facilities_display(self):
        facility=game.world.owned_facilities[self.viewed_facility]

        inventory=[]
        for area_name, area in facility.areas.items():
            for obj in area.inventory:
                inventory.append({
                    "obj_name": obj.name, "obj_area": obj.area,
                    "obj_image": obj.oid.rsplit("_", 1)[0], "area_name": area_name,
                    "pointer": obj, "function": self.follow_pointer
                })
        inventory.sort(key=lambda o: o["obj_area"], reverse=True)

        self.ui_lookup("facilities_header").text[0].text = facility.name
        self.ui_lookup("facilities_image").image[0].png = facility.fid
        self.ui_lookup("facilities_location").text[0].text = facility.location[1]
        self.ui_lookup("facilities_staff").text[0].text = f"/{facility.staff_max()} staff"
        self.ui_lookup("facilities_staff").text[1].text = f"{facility.total_staff()}"
        self.ui_lookup("facilities_area").text[0].text = unify(facility.total_area, "area")
        self.ui_lookup("facilities_area").text[1].text = unify(facility.used_area(), "area")
        self.ui_lookup("facilities_power").text[0].text = f"/{unify(facility.power, 'power')}"
        self.ui_lookup("facilities_power").text[1].text = "x"

        self.fill_grid_menu(
            "facilities",
            inventory,
            {
                ("text", 0): "obj_name",
                ("text", 1): "area_name",
                ("text", 2): "obj_area",
                ("image", 0): "obj_image"
            }
        )
        self.menu_refresh()

    def view_item(self, item):
        self.scroll["item_contents"]=0
        self.viewed_item_history.append(item)
        print(f"[ui] view item -> {item.oid}")
        if self.menu_history[-1]=="item":
            self.item_display()
        else:
            self.menu_switch("item")

    def item_display(self):
        if not self.viewed_item_history:
            return
        item = self.viewed_item_history[-1]

        self.ui_lookup("item_header").text[0].text = item.name
        self.ui_lookup("item_description").text[0].text = item.description
        self.ui_lookup("item_image").image[0].png = item.oid.rsplit("_", 1)[0]
        self.ui_lookup("item_weight").text[1].text = unify(item.total_weight(), "weight")
        self.ui_lookup("item_volume").text[1].text = unify(item.volume, "volume")

        item_contents = []
        if item.storage and item.storage["kind"]=="OBJECT":
            item_contents = [{
                "obj_name": obj.name,
                "obj_weight": obj.total_weight(),
                "obj_volume": obj.volume,
                "obj_image": obj.oid.rsplit("_", 1)[0],
                "pointer": obj,
                "function": self.follow_pointer
            } for obj in item.storage["content"]]
        item_contents.sort(key=lambda c: c["obj_volume"], reverse=True)
        self.fill_grid_menu(
            "item_contents",
            item_contents,
            {
                ("text", 0): "obj_name",
                ("text", 1): "obj_weight",
                ("text", 2): "obj_volume",
                ("image", 0): "obj_image",
            }
        )

        self.menu_refresh()

    def view_comm(self, comm):
        self.viewed_comm = comm.cid
        self.conv_scroll = 0
        self.conv_txt_scroll = 0
        print(f"[ui] view comm -> {comm.cid}")
        if not self.menu_history or self.menu_history[-1] != "convo":
            self.menu_switch("convo")
        else:
            self.convo_display()

    def comms_display(self):
        if self.click_history[-1] not in ("back_button", "comms_up", "comms_down"):
            self.scroll["comms"]=0

        contacts=[{
            "contact_name": comm.recipient.name,
            "contact_title": comm.recipient.title,
            "contact_image": comm.recipient.pid,
            "comm_last_text": comm.transcript[0]["text"],
            "comm_last_time": format_time_short(comm.transcript[0][2]),
            "pointer": comm,
            "function": self.follow_pointer
            } for comm in game.world.comms.values()
        ]
        contacts.sort(key=lambda c: (c["pointer"]!="hai", -(c[1] or 0)))

        gcs = 3
        self.check_scroll("comms", "cyan", len(contacts), gcs, self.cmms_scroll)

        for i in range(gcs):
            cell = self.ui_lookup(f"comms_grid_cell_{i + 1}")
            img = self.ui_lookup(f"comms_grid_cell_image_{i + 1}")

            if i >= len(contacts) - gcs * self.cmms_scroll:
                cell.text[0].text = ""
                cell.text[1].text = ""
                cell.text[2].text = ""
                cell.text[3].text = ""
                cell.fill = COLORS["transparent"]
                cell.function = None
                cell.pointer = None
                img.fill = COLORS["transparent"]
                img.image[0].png = ""
                continue

            comm = contacts[i + gcs * self.cmms_scroll][0]
            last_text = comm.history[0][0]["text"] if comm.history else ""
            if len(last_text) > 91:
                last_text = last_text[:91] + "..."

            cell.text[0].text = comm.recipient.name
            cell.text[1].text = comm.recipient.title
            cell.text[2].text = last_text
            cell.text[3].text = f"{format_time(comm.history[0][2])}" if comm.history else ""
            cell.fill = COLORS["gray_mid"] if comm.cid == "hai" else COLORS["cyan_lo"]
            cell.pointer = comm
            cell.function = lambda ui_name=cell.name: self.follow_pointer(ui_name)
            img.image[0].png = comm.recipient.pid
            img.fill = COLORS["gray_lo"] if comm.cid == "hai" else COLORS["cyan_dead"]

        self.menu_refresh()

    def comms_scroll(self, scroll: int):
        up = self.ui_lookup("comms_up")
        down = self.ui_lookup("comms_down")

        if scroll > 0 and up.fill == COLORS["cyan_dead"]:
            return
        if scroll < 0 and down.fill == COLORS["cyan_dead"]:
            return

        self.cmms_scroll += scroll
        print(f"[ui] comms scroll -> {self.cmms_scroll}")
        self.comms_display()

    def convo_display(self):
        if self.viewed_comm not in game.world.comms:
            return

        comm = game.world.comms[self.viewed_comm]
        self.ui_lookup("convo_header").text[0].text = comm.recipient.name

        gcs = 4
        start = -gcs * (self.conv_scroll + 1)
        end = -gcs * self.conv_scroll if self.conv_scroll != 0 else None
        texts = comm.transcript[start:end]
        filled = 0

        while filled < gcs:
            gc_l = self.ui_lookup(f"convo_grid_cell_l_{4 - filled}")
            gc_l_pfp = self.ui_lookup(f"convo_grid_cell_l_pfp_{4 - filled}")
            gc_r = self.ui_lookup(f"convo_grid_cell_r_{4 - filled}")
            gc_r_pfp = self.ui_lookup(f"convo_grid_cell_r_pfp_{4 - filled}")

            if filled >= len(texts):
                gc_l.text[0].text, gc_l.text[1].text, gc_l.fill = "", "", COLORS["transparent"]
                gc_l_pfp.image[0].png, gc_l_pfp.fill = "", COLORS["transparent"]
                gc_r.text[0].text, gc_r.text[1].text, gc_r.fill = "", "", COLORS["transparent"]
                gc_r_pfp.image[0].png, gc_r_pfp.fill = "", COLORS["transparent"]
                filled += 1
                continue

            text = texts[-1 - filled]
            side = text[1] if len(text) > 1 else None
            timestamp = text[2] if len(text) > 2 else None

            if side == "right":
                gc_l.text[0].text, gc_l.text[1].text, gc_l.fill = "", "", COLORS["transparent"]
                gc_l_pfp.image[0].png, gc_l_pfp.fill = "", COLORS["transparent"]
                gc_r.text[0].text = text[0]
                gc_r.text[1].text = format_time(timestamp) if timestamp is not None else ""
                gc_r.fill = COLORS["orange_lo"]
                gc_r_pfp.image[0].png, gc_r_pfp.fill = comm.sender.pid, COLORS["transparent"]
            elif side == "left":
                gc_l.text[0].text = text[0]
                gc_l.text[1].text = format_time(timestamp) if timestamp is not None else ""
                gc_l.fill = COLORS["cyan_lo"]
                gc_l_pfp.image[0].png, gc_l_pfp.fill = comm.recipient.pid, COLORS["transparent"]
                gc_r.text[0].text, gc_r.text[1].text, gc_r.fill = "", "", COLORS["transparent"]
                gc_r_pfp.image[0].png, gc_r_pfp.fill = "", COLORS["transparent"]
            else:
                gc_l.text[0].text, gc_l.text[1].text, gc_l.fill = "", "", COLORS["transparent"]
                gc_l_pfp.image[0].png, gc_l_pfp.fill = "", COLORS["transparent"]
                gc_r.text[0].text, gc_r.text[1].text, gc_r.fill = "", "", COLORS["transparent"]
                gc_r_pfp.image[0].png, gc_r_pfp.fill = "", COLORS["transparent"]

            filled += 1

        self.check_scroll("convo", "cyan", len(comm.transcript), gcs, self.conv_scroll)

        txt_gcs = 2
        txt_start = -txt_gcs * (self.conv_txt_scroll + 1)
        txt_end = -txt_gcs * self.conv_txt_scroll if self.conv_txt_scroll != 0 else None
        txt_texts = comm.responses[start:end]
        txt_filled = gcs

        self.check_scroll(
            "convo_text", "blue", len(comm.responses),
            txt_gcs, self.conv_txt_scroll
        )

        self.fill_grid_menu(
            {
                "menu": "convo_text",

            }
        )

        self.menu_refresh()

    def convo_scroll(self, scroll):
        up = self.ui_lookup("convo_up")
        down = self.ui_lookup("convo_down")

        if scroll > 0 and up.fill == COLORS["cyan_dead"]:
            return
        if scroll < 0 and down.fill == COLORS["cyan_dead"]:
            return

        self.conv_scroll += scroll
        print(f"[ui] convo scroll -> {self.conv_scroll}")
        self.convo_display()


ui_manager = UIManager()
