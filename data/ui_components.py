import pygame

from data.visual_design import BASE_DIR, COLORS, FONTS, std_padding

pygame.init()


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
        rotate: int = 0,
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
        try:
            surf = pygame.image.load(BASE_DIR / "pngs" / f"{self.png}.png").convert_alpha()
        except FileNotFoundError:
            surf = pygame.image.load(BASE_DIR / "pngs" / "unknown.png").convert_alpha()

        if self.scale:
            surf = pygame.transform.scale_by(surf, self.scale)
        if self.rotate:
            surf = pygame.transform.rotate(surf, self.rotate)
        self._surface = surf
        return self._surface


class UI:
    elements = []

    def __init__(
        self,
        name: str,
        pos: tuple,
        size: tuple,
        layer: int = 1,
        visible: bool = False,
        fill: tuple[int, int, int, int] = (0, 0, 0, 0),
        border: tuple[int, int, int, int, int] = (0, 0, 0, 0, 0),
        text: list[Text] = None,
        image: list[Image] = None,
        function=None,
        pointer=None,
    ):
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
        self.pointer = pointer

        self.surf = pygame.Surface(size, pygame.SRCALPHA)
        self.old = True

        UI.elements.append(self)

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
                lines = self.render_text_lines(element.text, element.font, element.pad_x, element.pad_y)
                line_height = element.font.get_height()
                total_height = len(lines) * line_height

                if element.v_align == "top":
                    y = element.pad_y
                elif element.v_align == "center":
                    y = (self.size[1] - total_height) // 2
                elif element.v_align == "bottom":
                    y = max(element.pad_y, self.size[1] - total_height - element.pad_y)
                else:
                    y = element.pad_y

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

                if element.v_align == "top":
                    y = element.pad_y
                elif element.v_align == "center":
                    y = (self.size[1] - ih) // 2
                elif element.v_align == "bottom":
                    y = self.size[1] - ih - element.pad_y
                else:
                    y = element.pad_y

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
