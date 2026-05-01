from collections import deque

import pygame

from game import game
from loader import saves_dir
from data.ui_components import UI, unify
from data.visual_design import COLORS, color_map
from world_config import format_time_short, format_time, MessageKind, Comm


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

    viewed_comm = None
    selected_message=None
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

    def perma_ui_color_switch(self, menu: str):
        color=color_map[menu]
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
            self.scroll["facilities_inventory"]=0
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
        elif isinstance(pointer, MessageKind):
            print(f"[ui] pointer item -> {pointer.name}")
            self.send_message(pointer)

    def menu_scroll(self, menu:str, scroll:int):
        self.scroll[menu]=(self.scroll[menu]+scroll)
        print(f"[ui] item contents scroll -> {menu}: {scroll}")
        if menu=="facilities":
            self.facilities_display()
        elif menu=="item":
            self.item_display()
        elif menu=="comms":
            self.comms_display()
        elif menu=="convo" or menu=="convo_text":
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
        self.ui_lookup("time_bar").text[0].text = format_time_short(game.world.time)
        print(f"[ui] game loaded at {format_time_short(game.world.time)}")
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
        if menu=="convo":
            for ui in UI.elements:
                if ui.name.startswith(f"{menu}_r_grid_cell_") and not ui.name.startswith(f"{menu}_r_grid_cell_image_"):
                    gcs+=1
        else:
            for ui in UI.elements:
                if ui.name.startswith(f"{menu}_grid_cell_") and not ui.name.startswith(f"{menu}_grid_cell_image_"):
                    gcs += 1

        view_start=self.scroll[menu]*gcs
        view_end=view_start+gcs

        ui_up=self.ui_lookup(menu+"_up")
        ui_down=self.ui_lookup(menu+"_down")
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
        if menu=="convo":
            return
        for i in range(gcs):
            ui = self.ui_lookup(f"{menu}_grid_cell_{i + 1}")

            for target, content_key in mapping.items():
                if len(viewed_content)<=i:
                    if target[0]=="text":
                        ui.text[target[1]].text=""
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
                    ui.text[target[1]].text=entry[content_key]
                    ui.fill=COLORS[f"{color_map[menu]}_lo"]
                elif target[0]=="image":
                    ui_image=self.ui_lookup(f"{menu}_grid_cell_image_{i + 1}")
                    ui_image.image[target[1]].png=entry[content_key]
                    ui_image.fill=COLORS[f"{color_map[menu]}_dead"]

            if len(viewed_content) > i:
                entry = viewed_content[i]
                if "function" not in entry:
                    ui.function=None
                    continue
                if "pointer" not in entry:
                    print(f"no pointer for gc{i+1} of {menu}")
                    ui.function=entry["function"]
                    continue
                function, pointer=entry["function"], entry["pointer"]
                ui.pointer=pointer
                ui.function=lambda f=function, p=pointer: f(p)

    def facilities_display(self):
        facility=game.world.owned_facilities[self.viewed_facility]

        inventory=[]
        for area_name, area in facility.areas.items():
            for obj in area.inventory:
                inventory.append({
                    "obj_name": obj.name, "obj_area": unify(obj.area, "area"),
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
            "facilities_inventory",
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
                "obj_weight": unify(obj.total_weight(), "weight"),
                "obj_volume": unify(obj.volume, "volume"),
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

    def view_comm(self, comm: Comm):
        self.viewed_comm=comm
        self.conv_scroll = 0
        self.conv_txt_scroll = 0
        print(f"[ui] view comm -> {comm.cid}")
        if not self.menu_history or self.menu_history[-1] != "convo":
            self.menu_switch("convo")
        else:
            self.convo_display()

    def select_message(self, kind):
        message_ui=self.ui_lookup(self.click_history[-1])
        send_ui=self.ui_lookup("convo_text_send")
        if message_ui.name.endswith("1"):
            other_message_ui=self.ui_lookup(message_ui.name.rsplit("_", 1)[0]+"_2")
        else:
            other_message_ui=self.ui_lookup(message_ui.name.rsplit("_", 1)[0]+"_1")
        if other_message_ui.selected:
            other_message_ui.selected=not other_message_ui.selected
            message_ui.selected=not message_ui.selected
        else:
            message_ui.selected=not message_ui.selected
            send_ui.selected=message_ui.selected
        self.selected_message=message_ui if message_ui.selected else None
        self.convo_display()

    def send_message(self, kind: MessageKind):
        text=self.selected_message.text[0]
        game.comm_send(self.viewed_comm, {
            "kind": kind,
            "text": text,
        })


    def comms_display(self):
        if self.click_history[-1] not in ("back_button", "comms_up", "comms_down"):
            self.scroll["comms"]=0

        contacts = [{
            "contact_name": comm.recipient.name,
            "contact_title": comm.recipient.title,
            "contact_image": comm.recipient.pid,
            "comm_last_text": (
                (comm.history[0]["message"]["text"] if comm.history else "")[:91]
            ),
            "comm_last_time": (
                format_time_short(comm.history[0]["timestamp"])
                if comm.history else ""
            ),
            "pointer": comm,
            "function": self.follow_pointer
        } for comm in game.world.comms.values()]

        contacts.sort(
            key=lambda c: (
                c["contact_image"]!="hai",
                -c["pointer"].history[0]["timestamp"] if c["pointer"].history else 0
            )
        )

        self.fill_grid_menu(
            "comms",
            contacts,
            {
                ("text", 0): "contact_name",
                ("text", 1): "contact_title",
                ("text", 2): "comm_last_text",
                ("text", 3): "comm_last_time",
                ("image", 0): "contact_image"
            }
        )

        self.menu_refresh()

    def convo_display(self):
        comm=self.viewed_comm

        self.ui_lookup("convo_header").text[0].text = comm.recipient.name

        gcs=4
        start=gcs*self.conv_scroll
        end=gcs+gcs*self.conv_scroll
        texts=comm.transcript[start:end]
        filled=0

        while filled<gcs:
            gc_l=self.ui_lookup(f"convo_l_grid_cell_{gcs-filled}")
            gc_l_pfp=self.ui_lookup(f"convo_l_grid_cell_image_{gcs-filled}")
            gc_r=self.ui_lookup(f"convo_r_grid_cell_{gcs-filled}")
            gc_r_pfp=self.ui_lookup(f"convo_r_grid_cell_image_{gcs-filled}")

            if filled >= len(texts):
                gc_l.text[0].text, gc_l.text[1].text, gc_l.fill = "", "", COLORS["transparent"]
                gc_l_pfp.image[0].png, gc_l_pfp.fill = "", COLORS["transparent"]
                gc_r.text[0].text, gc_r.text[1].text, gc_r.fill = "", "", COLORS["transparent"]
                gc_r_pfp.image[0].png, gc_r_pfp.fill = "", COLORS["transparent"]
                filled += 1
                continue

            entry=texts[filled]
            text=entry["text"]
            side=entry["side"]
            timestamp=entry["timestamp"]

            if side=="right":
                gc_l.text[0].text, gc_l.text[1].text, gc_l.fill="", "", COLORS["transparent"]
                gc_l_pfp.image[0].png, gc_l_pfp.fill="", COLORS["transparent"]
                gc_r.text[0].text=text
                gc_r.text[1].text=format_time_short(timestamp) if timestamp is not None else ""
                gc_r.fill=COLORS["orange_lo"]
                gc_r_pfp.image[0].png, gc_r_pfp.fill=comm.sender.pid, COLORS["transparent"]
            elif side=="left":
                gc_l.text[0].text=text
                gc_l.text[1].text=format_time_short(timestamp) if timestamp is not None else ""
                gc_l.fill=COLORS["cyan_lo"]
                gc_l_pfp.image[0].png, gc_l_pfp.fill=comm.recipient.pid, COLORS["transparent"]
                gc_r.text[0].text, gc_r.text[1].text, gc_r.fill="", "", COLORS["transparent"]
                gc_r_pfp.image[0].png, gc_r_pfp.fill="", COLORS["transparent"]
            else:
                gc_l.text[0].text, gc_l.text[1].text, gc_l.fill="", "", COLORS["transparent"]
                gc_l_pfp.image[0].png, gc_l_pfp.fill="", COLORS["transparent"]
                gc_r.text[0].text, gc_r.text[1].text, gc_r.fill="", "", COLORS["transparent"]
                gc_r_pfp.image[0].png, gc_r_pfp.fill="", COLORS["transparent"]

            filled += 1

        self.fill_grid_menu(
            "convo",
            comm.transcript,
            {}
        )

        game.comm_responses(comm)
        responses=[{
            "text": response["text"],
            "pointer": response["kind"],
            "function": self.select_message
        } for response in comm.responses]
        self.fill_grid_menu(
            "convo_text",
            responses,
            {
                ("text", 0): "text"
            }
        )
        text_send=self.ui_lookup("convo_text_send")
        color=color_map["convo_text"]
        if self.selected_message:
            self.selected_message.fill=COLORS[f"{color}_mid"]
            text_send.fill, text_send.text[0].color=COLORS[f"{color}_mid"], COLORS["white"]
            text_send.pointer, text_send.function= self.selected_message.pointer, self.follow_pointer
        else:
            text_send.fill, text_send.text[0].color = COLORS[f"{color}_lo"], COLORS["black"]
            text_send.pointer, text_send.function = None, None

        self.menu_refresh()


ui_manager = UIManager()
