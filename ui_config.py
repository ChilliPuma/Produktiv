import json
import logging

from loader import saves_dir, load_default

log = logging.getLogger(__name__)

import pygame
pygame.init()

from collections import deque

from visual_config import COLORS, FONTS, std_padding, BASE_DIR

from world_config import format_time

from game import game


def unify(qty: float, unit: str) -> str:
    if unit == "weight":
        if qty < 1:
            qty *= 1000
            unit = "g"
            return f"{qty:.0f}{unit}"
        elif qty > 2000:
            qty /= 1000
            unit = "t"
            return f"{qty:.1f}{unit}"
        else:
            unit = "kg"

    elif unit == "volume":
        if qty < 1:
            qty *= 1000
            unit = "mL"
            return f"{qty:.0f}{unit}"
        elif qty > 2000:
            qty /= 1000
            unit = "m³"
            return f"{qty:.1f}{unit}"
        else:
            unit = "L"

    elif unit == "area":
        if qty < 0.1:
            qty *= 10000
            unit = "cm²"
            return f"{qty:.0f}{unit}"
        elif qty > 2000:
            qty /= 10000
            unit = "ha"
            return f"{qty:.1f}{unit}"
        else:
            unit = "m²"

    elif unit == "power":
        if qty > 2000:
            qty /= 1000
            unit = "kW"
            return f"{qty:.1f}{unit}"
        else:
            return f"{qty:.0f}W"


    return f"{qty:.1f}{unit}"

class Text:
    def __init__(
        self,
        text: str = "",
        font: pygame.font.Font = FONTS["topaz_m"],
        color: tuple[int, int, int, int] = COLORS["white"],
        h_align="center",
        v_align="center",
        pad_x: int = std_padding,
        pad_y: int = std_padding,
        rotate: int = 0
        ):

        self.text = text
        self.font = font
        self.color = color
        self.h_align = h_align
        self.v_align = v_align
        self.pad_x = pad_x
        self.pad_y = pad_y
        self.rotate = rotate

class Image:
    def __init__(
        self,
        png: str = "",
        scale: float | None = None,
        pad_x: int = 0,
        pad_y: int = 0,
        h_align: str = "center",
        v_align: str = "center",
        rotate: float = 0,
        ):

        self.png = png
        self.scale = scale
        self.pad_x = pad_x
        self.pad_y = pad_y
        self.h_align = h_align
        self.v_align = v_align
        self.rotate = rotate

        self._surface = None

    def get_image_surface(self):

        surf = pygame.image.load(BASE_DIR / "pngs" / f"{self.png}.png").convert_alpha()
        if self.scale:
            surf = pygame.transform.scale_by(surf, self.scale)
        if self.rotate:
            surf = pygame.transform.rotate(surf, self.rotate)
        self._surface = surf
        return self._surface

class UI:
    elements = []
    def __init__(self,
        name: str,
        pos: tuple,
        size: tuple,
        layer: int = 1,
        visible: bool = False,
        fill: tuple[int, int, int, int] = (0, 0, 0, 0),
        border: tuple[int, int, int, int, int] = (0, 0, 0, 0, 0),
        text: list[Text] = None,
        image: list[Image] = None,
        function = None):

        self.name = name
        self.pos = pos
        self.size = size
        self.layer = layer
        self.visible = visible
        self.fill = fill
        self.border = border
        self.text = text or []
        self.image = image or []
        self.function = function

        self.surf = pygame.Surface(size, pygame.SRCALPHA)
        self.old = True

        UI.elements.append(self)
        log.debug("Registering UI element: %s", self.name)

    def render_text_lines(self, text: str, font: pygame.font.Font, pad_x: int, pad_y: int):
        words = text.split(" ")
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if font.size(test_line)[0] <= self.size[0] - 2 * pad_x:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    def renew(self):
        self.surf.fill(self.fill)

        r, g, b, a, t = self.border
        if t > 0:
            pygame.draw.rect(self.surf, (r, g, b, a), self.surf.get_rect(), t)

        if self.text:
            for element in self.text:
                lines = self.render_text_lines(
                    element.text, element.font, element.pad_x, element.pad_y)
                line_height = element.font.get_height()
                total_height = len(lines) * line_height

                # Vertical alignment
                if element.v_align == "top":
                    y = element.pad_y
                elif element.v_align == "center":
                    y = (self.size[1] - total_height) // 2
                elif element.v_align == "bottom":
                    y = max(element.pad_y, self.size[1] - total_height - element.pad_y)
                else:
                    y = element.pad_y

                # Draw each line with horizontal alignment
                for line in lines:
                    text_surf = element.font.render(line, True, element.color[:3]).convert_alpha()
                    text_surf.set_alpha(element.color[3])

                    if element.h_align == "left":
                        x = element.pad_x
                    elif element.h_align == "center":
                        x = (self.size[0] - text_surf.get_width()) // 2
                    elif element.h_align == "right":
                        x = self.size[0] - text_surf.get_width() - element.pad_x
                    else:
                        x = element.pad_x

                    text_surf = pygame.transform.rotate(text_surf, element.rotate)

                    self.surf.blit(text_surf, (x, y))
                    y += line_height

            self.old = False

        if self.image:

            for element in self.image:
                if element.png == "":
                    break
                img_surf = element.get_image_surface()
                iw, ih = img_surf.get_size()

                # Vertical alignment
                if element.v_align == "top":
                    y = element.pad_y
                elif element.v_align == "center":
                    y = (self.size[1] - ih) // 2
                elif element.v_align == "bottom":
                    y = self.size[1] - ih - element.pad_y
                else:
                    y = element.pad_y

                # Horizontal alignment
                if element.h_align == "left":
                    x = element.pad_x
                elif element.h_align == "center":
                    x = (self.size[0] - iw) // 2
                elif element.h_align == "right":
                    x = self.size[0] - iw - element.pad_x
                else:
                    x = element.pad_x

                self.surf.blit(img_surf, (x, y))

    def open(self, ui):
        pass

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

    cmms_scroll = 0

    viewed_comm = ""
    conv_scroll = 0
    conv_txt_scroll = 0

    def draw(self, surface):

        for ui in sorted(UI.elements, key=lambda e: e.layer):
            if not ui.visible:
                continue
            if ui.old:
                ui.renew()
            surface.blit(ui.surf, ui.pos)

    def click(self, pos):
        log.debug("Click at %s", pos)
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
                    log.debug("Clicked UI: %s", ui.name)
                    break

    def menu_back(self):
        if len(self.menu_history) > 1:

            if self.menu_history[-1] == "item":
                if len(self.viewed_item_history) > 1:
                    self.viewed_item_history.pop()
                    self.item_display()
                    return
                elif len(self.viewed_item_history) == 1:
                    self.viewed_item_history.pop()

            self.menu_history.pop()
            previous_menu = self.menu_history.pop()
            self.menu_switch(previous_menu)

    def perma_ui_color_switch(self, color: str):
        self.ui_update("permanent_borders",
            border = COLORS[f"{color}_border"])
        self.ui_update("back_button",
            fill = COLORS[f"{color}_lo"])
        self.ui_update("save_button",
            fill = COLORS[f"{color}_lo"])

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
                    continue  # skip broken saves

                facilities = data.get("facilities", {})
                count = sum(
                    1
                    for f in facilities.values()
                    if f.get("owner") == "player"
                )

                saves_list.append(
                    {
                    "filename": path.name,
                    "run_time": data.get("time"),
                    "facilities": count
                }
                )

            for i in range(1, 6):
                grid_cell_ui_name = f"{menu_name}_grid_cell_{i}"
                self.ui_update(grid_cell_ui_name,
                    text = [
                        Text(
                            text = "[empty]",
                            h_align = "left",
                            font = FONTS["topaz_m"],
                            color = COLORS["gray_mid"]
                        ),
                        Text(
                            h_align = "right",
                            font = FONTS["topaz_s"],
                            color = COLORS["gray_mid"]
                        )
                    ]
                )

            for i, save in enumerate(saves_list, start = 1):
                    filename = save["filename"]
                    game_time = format_time(save["run_time"])
                    grid_cell_ui = self.ui_lookup(f"{menu_name}_grid_cell_{i}")

                    grid_cell_ui.text[0].text = filename
                    grid_cell_ui.text[0].color = COLORS["white"]

                    grid_cell_ui.text[1].text = f"{game_time}"
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
        log.info("Switching menu to: %s", menu_name)
        log.debug("Menu history: %s", self.menu_history)

        for ui in UI.elements:
            if ui.layer == 33:
                continue
            if ui.name.startswith(menu_name):
                ui.visible = True
                ui.old = True
            elif ui.visible:
                ui.visible = False
                ui.old = True

    def check_scroll(self, menu: str, color: str, items: int, cells: int, scroll: int):
        ui_up = self.ui_lookup(menu + "_up")
        ui_down = self.ui_lookup(menu + "_down")

        if items > cells + cells * scroll:
            ui_down.fill = COLORS[f"{color}_mid"]
            ui_down.text[0].color = COLORS[f"{color}_hi"]
        else:
            ui_down.fill = COLORS[f"{color}_dead"]
            ui_down.text[0].color = COLORS[f"black"]

        if scroll != 0:
            ui_up.fill = COLORS[f"{color}_mid"]
            ui_up.text[0].color = COLORS[f"{color}_hi"]
        else:
            ui_up.fill = COLORS[f"{color}_dead"]
            ui_up.text[0].color = COLORS[f"black"]

    def facilities_display(self, f):
        v_facility_inventory = []
        for area_name, area in f.areas.items():
            for obj in area.inventory:
                v_facility_inventory.append((obj, area_name))

        inv_items_no = len(v_facility_inventory)

        f_header = self.ui_lookup("facilities_header")
        f_header.text[0].text = f.name

        f_image = self.ui_lookup("facilities_image")
        f_image.image[0].png = "facility_" + f.fid

        f_location = self.ui_lookup("facilities_location")
        f_location.text[0].text = f.location[1]

        f_staff = self.ui_lookup("facilities_staff")
        f_staff.text[0].text = f"/{f.staff_max()} staff"
        f_staff.text[1].text = f"{f.total_staff()}"

        f_area = self.ui_lookup("facilities_area")
        f_area.text[0].text = unify(f.total_area, "area")
        f_area.text[1].text = unify(f.used_area(), "area")

        f_power = self.ui_lookup("facilities_power")
        f_power.text[0].text = f"/{unify(f.power, "power")}"
        f_power.text[1].text = f"x"

        cells = 4

        self.check_scroll(
            "facilities_inventory", "orange", inv_items_no, cells, self.facility_inv_scroll)

        v_facility_inventory.sort(key=lambda item: item[0].area, reverse=True)

        for i in range(4):

            if len(v_facility_inventory) <= i + self.facility_inv_scroll * 4:
                f_inv_item_img = self.ui_lookup(f"facilities_inventory_grid_cell_image_{i + 1}")
                f_inv_item_img.image[0].png = ""
                f_inv_item_img.fill = COLORS["black"]

                f_inv_item_cell = self.ui_lookup(f"facilities_inventory_grid_cell_{i + 1}")
                f_inv_item_cell.text[0].text, f_inv_item_cell.text[1].text, = "", ""
                f_inv_item_cell.text[1].text = ""
                f_inv_item_cell.text[2].text = ""
                f_inv_item_cell.text[3].text = ""
                f_inv_item_cell.fill = COLORS["black"]
                f_inv_item_cell.function = None

            else:
                f_inv_item_img = self.ui_lookup(f"facilities_inventory_grid_cell_image_{i + 1}")
                f_inv_item_img.image[0].png = v_facility_inventory[
                    i + self.facility_inv_scroll * 4][0].oid.rsplit("_", 1)[0]
                f_inv_item_img.fill = COLORS["orange_dead"]

                f_inv_item_cell = self.ui_lookup(f"facilities_inventory_grid_cell_{i + 1}")
                f_inv_item = v_facility_inventory[i + self.facility_inv_scroll * 4][0]
                f_inv_item_cell.text[0].text = f_inv_item.name
                f_inv_item_cell.text[1].text = v_facility_inventory[
                    i + self.facility_inv_scroll * 4][1]
                f_inv_item_cell.text[2].text = unify(f_inv_item.area, "area")
                f_inv_item_cell.fill = COLORS["orange_lo"]
                f_inv_item_cell.text[3].text = f_inv_item.oid
                f_inv_item_cell.function = lambda: self.menu_switch("item")

    def item_display(self):

        if self.click_history[-1] in (
        "back_button", "item_contents_up", "item_contents_down"):
            item = self.viewed_item_history[-1]
        else:
            item = game.world.objects[self.ui_lookup(self.click_history[-1]).text[3].text]
            self.item_cont_scroll = 0
            self.viewed_item_history.append(item)

        self.ui_lookup("item_header").text[0].text = item.name
        self.ui_lookup("item_description").text[0].text = item.description
        self.ui_lookup("item_image").image[0].png = item.oid.rsplit("_", 1)[0]
        self.ui_lookup("item_weight").text[1].text = unify(item.total_weight(), "weight")
        self.ui_lookup("item_volume").text[1].text = unify(item.volume, "volume")

        item_contents = []
        for content in item.storage:
            item_contents.append((content, content.volume))

        cells = 4

        self.check_scroll(
            "item_contents", "green", len(item_contents), cells, self.item_cont_scroll)

        item_contents.sort(key=lambda c: c[1], reverse=True)

        for i in range(4):

            i_cont_cell = self.ui_lookup(f"item_contents_grid_cell_{i + 1}")
            i_cont_img = self.ui_lookup(f"item_contents_grid_cell_image_{i + 1}")

            if len(item_contents) <= i + self.item_cont_scroll * 4:
                i_cont_img.image[0].png = ""
                i_cont_img.fill = COLORS["black"]

                i_cont_cell.text[0].text, i_cont_cell.text[1].text, = "", ""
                i_cont_cell.text[1].text = ""
                i_cont_cell.text[2].text = ""
                i_cont_cell.text[3].text = ""
                i_cont_cell.fill, i_cont_cell.function = COLORS["black"], None

            else:
                i_cont_img.image[0].png = item_contents[
                    i + self.item_cont_scroll * 4][0].oid.rsplit("_", 1)[0]
                i_cont_img.fill = COLORS["green_dead"]

                i_cont_item = item_contents[i + self.item_cont_scroll * 4][0]

                i_cont_cell.text[0].text = i_cont_item.name
                i_cont_cell.text[1].text = unify(i_cont_item.weight, "weight")
                i_cont_cell.text[2].text = unify(i_cont_item.volume, "volume")
                i_cont_cell.fill, i_cont_cell.function = COLORS["green_lo"], lambda: self.item_display()
                i_cont_cell.text[3].text = i_cont_item.oid

        self.menu_refresh()

    def comms_display(self):

        if not self.click_history[-1] in (
        "back_button", "comms_up", "comms_down"):
            self.cmms_scroll = 0

        contacts = [
            (comm, comm.history[-1].timestamp if comm.history else None) for comm in game.world.comms.values()
        ]
        contacts.sort(key = lambda c: (c[0] != game.world.comms["hai"], -(c[1] or 0)))

        gcs = 3

        self.check_scroll("comms", "cyan", len(contacts), gcs, self.cmms_scroll)

        for i in range (gcs):
            gc = self.ui_lookup(f"comms_grid_cell_{i + 1}")
            gc_image = self.ui_lookup(f"comms_grid_cell_image_{i + 1}")

            if i >= len(contacts) - gcs * self.cmms_scroll:
                gc.text[0].text, gc.text[1].text, gc.text[2].text, gc.text[3].text, gc.text[4].text = (
                    "", "", "", "", "")
                gc.fill, gc.function = COLORS["transparent"], None
                gc_image.fill, gc_image.image[0].png = COLORS["transparent"], ""


            else:
                comm = contacts[i + gcs * self.cmms_scroll][0]

                last_text = comm.history[-1].text if comm.history else ""
                if len(last_text) > 91:
                    last_text = last_text[:91] + "..."

                if comm.cid == "hai":
                    gc.text[0].text, gc.text[1].text, gc.text[2].text, gc.text[3].text, gc.text[4].text = (
                        "hAI",
                        "Your helper AI",
                        last_text,
                        comm.cid,
                        f"{format_time(comm.history[-1].timestamp)}" if comm.history else "",
                    )
                    gc.fill, gc.function = COLORS["gray_mid"], lambda: self.menu_switch("convo")
                    gc_image.image[0].png, gc_image.fill = "hai", COLORS["gray_lo"]

                else:
                    gc.text[0].text, gc.text[1].text, gc.text[2].text, gc.text[3].text, gc.text[4].text = (
                        game.world.people[comm.recipient].name,
                        game.world.people[comm.recipient].title,
                        last_text,
                        comm.cid,
                        f"{format_time(comm.history[-1].timestamp)}" if comm.history else "",
                    )
                    gc.fill = COLORS["cyan_lo"]
                    gc_image.image[0].png, gc_image.fill = game.world.people[comm.recipient].pid, COLORS["cyan_dead"]

        self.menu_refresh()

    def convo_display(self):

        if not self.click_history[-1] in (
        "back_button", "convo_up", "convo_down", "convo_text_down", "convo_text_up", "convo_send"):
            self.conv_scroll = 0
            self.conv_txt_scroll = 0
            self.viewed_comm = self.ui_lookup(self.click_history[-1]).text[3].text

        comm = game.world.comms[self.viewed_comm]

        self.ui_lookup("convo_header").text[0].text = game.world.people[comm.recipient].name if (
                self.viewed_comm != "hai") else "hAI"
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

            else:
                text = texts[-1 - filled]
                if text[2] == "right":
                    gc_l.text[0].text, gc_l.text[1].text, gc_l.fill = "", "", COLORS["transparent"]
                    gc_l_pfp.image[0].png, gc_l_pfp.fill = "", COLORS["transparent"]
                    gc_r.text[0].text, gc_r.text[1].text = text[0], text[1]
                    gc_r.fill = COLORS["orange_lo"]
                    gc_r_pfp.image[0].png, gc_r_pfp.fill = comm.sender, COLORS["transparent"]
                    filled += 1
                    continue
                elif text[2] == "left":
                    gc_l.text[0].text, gc_l.text[1].text = text[0], (text[1] if text[1] else "")
                    gc_l.fill = COLORS["cyan_lo"]
                    gc_l_pfp.image[0].png, gc_l_pfp.fill = comm.recipient, COLORS["transparent"]
                    gc_r.text[0].text, gc_r.text[1].text, gc_r.fill = "", "", COLORS["transparent"]
                    gc_r_pfp.image[0].png, gc_r_pfp.fill = "", COLORS["transparent"]
                    filled += 1
                    continue

        self.check_scroll("convo", "cyan", len(comm.transcript), gcs, self.conv_scroll)
        self.menu_refresh()



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

    def new_save_button(self, save_file_name: str):

        self.menu_switch("saves")

    def game_load(self):

        if not self.game_loaded:

            self.ui_lookup("start_continue").text[0].color = COLORS["white"]
            self.ui_update("start_continue",
                fill=COLORS["yellow_mid"])

        self.game_loaded = True
        game.world.time_stop = False

        self.menu_switch("main")

        self.ui_update("time_bar", visible = True)


    def new_game(self):

        game.new_game()
        self.game_load()

    def continue_game(self):
        if self.game_loaded:
            self.game_load()

    def facilities_inventory_scroll(self, scroll:int):
        f_inv_down = self.ui_lookup("facilities_inventory_down")
        f_inv_up = self.ui_lookup("facilities_inventory_up")

        if scroll > 0:
            if f_inv_down.fill == COLORS["orange_dead"]:
                return
        elif scroll < 0:
            if f_inv_up.fill == COLORS["orange_dead"]:
                return

        self.facility_inv_scroll += scroll
        self.facilities_display(game.world.owned_facilities[self.viewed_facility])
        self.menu_refresh()

    def item_contents_scroll(self, scroll:int):
        i_cont_down = self.ui_lookup("item_contents_down")
        i_cont_up = self.ui_lookup("item_contents_up")

        if scroll > 0:
            if i_cont_down.fill == COLORS["green_dead"]:
                return
        elif scroll < 0:
            if i_cont_up.fill == COLORS["green_dead"]:
                return

        self.item_cont_scroll += scroll
        self.item_display()

    def comms_scroll(self, scroll:int):

        c_up = self.ui_lookup("comms_up")
        c_down = self.ui_lookup("comms_down")

        if scroll > 0:
            if c_up.fill == COLORS["cyan_dead"]:
                return

        elif scroll < 0:
            if c_down.fill == COLORS["cyan_dead"]:
                return

        self.cmms_scroll += scroll
        self.comms_display()

    def convo_scroll(self, scroll):

        up = self.ui_lookup("convo_up")
        down = self.ui_lookup("convo_down")

        if scroll > 0:
            if up.fill == COLORS["cyan_dead"]:
                return
        if scroll < 0:
            if down.fill == COLORS["cyan_dead"]:
                return

        self.conv_scroll += scroll
        self.convo_display()


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



ui_manager = UIManager()
