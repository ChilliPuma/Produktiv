import json
from collections import deque

import pygame

from game import game
from loader import saves_dir
from data.ui_components import UI, Text, unify
from data.visual_design import COLORS, FONTS
from world_config import format_time


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

    def check_scroll(self, menu: str, color: str, items: int, cells: int, scroll: int):
        ui_up = self.ui_lookup(menu + "_up")
        ui_down = self.ui_lookup(menu + "_down")

        if items > cells + cells * scroll:
            ui_down.fill = COLORS[f"{color}_mid"]
            ui_down.text[0].color = COLORS[f"{color}_hi"]
        else:
            ui_down.fill = COLORS[f"{color}_dead"]
            ui_down.text[0].color = COLORS["black"]

        if scroll != 0:
            ui_up.fill = COLORS[f"{color}_mid"]
            ui_up.text[0].color = COLORS[f"{color}_hi"]
        else:
            ui_up.fill = COLORS[f"{color}_dead"]
            ui_up.text[0].color = COLORS["black"]

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
            self.perma_ui_color_switch("yellow")
            self.menu_history.clear()
            if game.world:
                game.world.time_stop = True

        elif menu_name == "saves":
            self.perma_ui_color_switch("blue")

            saves_list = []
            for path in saves_dir.glob("*.json"):
                try:
                    with path.open("r", encoding="utf-8") as f:
                        data = json.load(f)
                except (json.JSONDecodeError, OSError):
                    continue

                facilities = data.get("facilities", {})
                count = sum(1 for f in facilities.values() if f.get("owner") == "player")
                saves_list.append(
                    {
                        "filename": path.name,
                        "run_time": data.get("time"),
                        "facilities": count,
                    }
                )

            for i in range(1, 6):
                self.ui_update(
                    f"{menu_name}_grid_cell_{i}",
                    text=[
                        Text(
                            text="[empty]",
                            h_align="left",
                            font=FONTS["topaz_m"],
                            color=COLORS["gray_mid"],
                        ),
                        Text(
                            h_align="right",
                            font=FONTS["topaz_s"],
                            color=COLORS["gray_mid"],
                        ),
                    ],
                )

            for i, save in enumerate(saves_list, start=1):
                grid_cell_ui = self.ui_lookup(f"{menu_name}_grid_cell_{i}")
                grid_cell_ui.text[0].text = save["filename"]
                grid_cell_ui.text[0].color = COLORS["white"]
                grid_cell_ui.text[1].text = format_time(save["run_time"])
                grid_cell_ui.text[1].color = COLORS["white"]
                grid_cell_ui.fill = COLORS["blue_mid"]

        elif menu_name == "new_save":
            self.perma_ui_color_switch("cyan")

        elif menu_name == "main":
            self.perma_ui_color_switch("orange")

        elif menu_name == "facilities":
            self.perma_ui_color_switch("orange")
            self.facility_inv_scroll = 0
            self.facilities_display(game.world.owned_facilities[self.viewed_facility])

        elif menu_name == "item":
            self.perma_ui_color_switch("green")
            self.item_display()

        elif menu_name == "comms":
            self.perma_ui_color_switch("cyan")
            self.comms_display()

        elif menu_name == "convo":
            self.perma_ui_color_switch("blue")
            self.convo_display()

        self.menu_history.append(menu_name)
        print(f"[ui] menu -> {menu_name}")

        for ui in UI.elements:
            if ui.layer == 33:
                continue
            if ui.name.startswith(menu_name):
                ui.visible = True
                ui.old = True
            elif ui.visible:
                ui.visible = False
                ui.old = True

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

    def follow_pointer(self, ui_name: str):
        ui = self.ui_lookup(ui_name)
        if ui is None or ui.pointer is None:
            return

        if hasattr(ui.pointer, "oid"):
            print(f"[ui] pointer item -> {ui.pointer.oid}")
            self.view_item(ui.pointer)
        elif hasattr(ui.pointer, "cid"):
            print(f"[ui] pointer comm -> {ui.pointer.cid}")
            self.view_comm(ui.pointer)

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

    def facilities_display(self, facility):
        facility_inventory = []
        for area_name, area in facility.areas.items():
            for obj in area.inventory:
                facility_inventory.append((obj, area_name))

        self.ui_lookup("facilities_header").text[0].text = facility.name
        self.ui_lookup("facilities_image").image[0].png = "facility_" + facility.fid
        self.ui_lookup("facilities_location").text[0].text = facility.location[1]
        self.ui_lookup("facilities_staff").text[0].text = f"/{facility.staff_max()} staff"
        self.ui_lookup("facilities_staff").text[1].text = f"{facility.total_staff()}"
        self.ui_lookup("facilities_area").text[0].text = unify(facility.total_area, "area")
        self.ui_lookup("facilities_area").text[1].text = unify(facility.used_area(), "area")
        self.ui_lookup("facilities_power").text[0].text = f"/{unify(facility.power, 'power')}"
        self.ui_lookup("facilities_power").text[1].text = "x"

        cells = 4
        self.check_scroll(
            "facilities_inventory", "orange", len(facility_inventory), cells, self.facility_inv_scroll
        )

        facility_inventory.sort(key=lambda item: item[0].area, reverse=True)

        for i in range(4):
            img = self.ui_lookup(f"facilities_inventory_grid_cell_image_{i + 1}")
            cell = self.ui_lookup(f"facilities_inventory_grid_cell_{i + 1}")

            if len(facility_inventory) <= i + self.facility_inv_scroll * 4:
                img.image[0].png = ""
                img.fill = COLORS["black"]
                cell.text[0].text = ""
                cell.text[1].text = ""
                cell.text[2].text = ""
                cell.fill = COLORS["black"]
                cell.function = None
                cell.pointer = None
                continue

            item, area_name = facility_inventory[i + self.facility_inv_scroll * 4]
            img.image[0].png = item.oid.rsplit("_", 1)[0]
            img.fill = COLORS["orange_dead"]
            cell.text[0].text = item.name
            cell.text[1].text = area_name
            cell.text[2].text = unify(item.area, "area")
            cell.fill = COLORS["orange_lo"]
            cell.pointer = item
            cell.function = lambda ui_name=cell.name: self.follow_pointer(ui_name)

    def facilities_inventory_scroll(self, scroll: int):
        down = self.ui_lookup("facilities_inventory_down")
        up = self.ui_lookup("facilities_inventory_up")

        if scroll > 0 and down.fill == COLORS["orange_dead"]:
            return
        if scroll < 0 and up.fill == COLORS["orange_dead"]:
            return

        self.facility_inv_scroll += scroll
        print(f"[ui] facilities scroll -> {self.facility_inv_scroll}")
        self.facilities_display(game.world.owned_facilities[self.viewed_facility])
        self.menu_refresh()

    def view_item(self, item):
        self.item_cont_scroll = 0
        self.viewed_item_history.append(item)
        print(f"[ui] view item -> {item.oid}")
        if not self.menu_history or self.menu_history[-1] != "item":
            self.menu_switch("item")
        else:
            self.item_display()

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
        if item.storage:
            item_contents = [(obj, obj.volume) for obj in item.storage["content"] if item.storage]

        cells = 4
        self.check_scroll("item_contents", "green", len(item_contents), cells, self.item_cont_scroll)
        item_contents.sort(key=lambda c: c[1], reverse=True)

        for i in range(4):
            cell = self.ui_lookup(f"item_contents_grid_cell_{i + 1}")
            img = self.ui_lookup(f"item_contents_grid_cell_image_{i + 1}")

            if len(item_contents) <= i + self.item_cont_scroll * 4:
                img.image[0].png = ""
                img.fill = COLORS["black"]
                cell.text[0].text = ""
                cell.text[1].text = ""
                cell.text[2].text = ""
                cell.fill = COLORS["black"]
                cell.function = None
                cell.pointer = None
                continue

            content_item = item_contents[i + self.item_cont_scroll * 4][0]
            img.image[0].png = content_item.oid.rsplit("_", 1)[0]
            img.fill = COLORS["green_dead"]
            cell.text[0].text = content_item.name
            cell.text[1].text = unify(content_item.weight, "weight")
            cell.text[2].text = unify(content_item.volume, "volume")
            cell.fill = COLORS["green_lo"]
            cell.pointer = content_item
            cell.function = lambda ui_name=cell.name: self.follow_pointer(ui_name)

        self.menu_refresh()

    def item_contents_scroll(self, scroll: int):
        down = self.ui_lookup("item_contents_down")
        up = self.ui_lookup("item_contents_up")

        if scroll > 0 and down.fill == COLORS["green_dead"]:
            return
        if scroll < 0 and up.fill == COLORS["green_dead"]:
            return

        self.item_cont_scroll += scroll
        print(f"[ui] item contents scroll -> {self.item_cont_scroll}")
        self.item_display()

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
            self.cmms_scroll = 0

        contacts = [
            (comm, comm.history[-1][2] if comm.history else None) for comm in game.world.comms.values()
        ]
        contacts.sort(key=lambda c: (c[0] != game.world.comms["hai"], -(c[1] or 0)))

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
            last_text = comm.history[-1][0]["text"] if comm.history else ""
            if len(last_text) > 91:
                last_text = last_text[:91] + "..."

            cell.text[0].text = comm.recipient.name
            cell.text[1].text = comm.recipient.title
            cell.text[2].text = last_text
            cell.text[3].text = f"{format_time(comm.history[-1][2])}" if comm.history else ""
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

        while filled < 4:
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
